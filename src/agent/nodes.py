"""
NODOS DEL GRAFO TEXT-TO-SQL Y SÍNTESIS DE INTELIGENCIA DE NEGOCIOS
==================================================================
Contiene las 4 etapas del agente analista:
1. `inspect_schema_node`: Lee las tablas y columnas reales de la base de datos.
2. `generate_sql_node`: Traduce la pregunta en español a una consulta SQL SELECT optimizada.
3. `validate_and_execute_sql_node`: Pasa el SQL por el Guardrail Read-Only y lo ejecuta.
4. `synthesize_bi_insight_node`: Calcula totales, identifica al líder del segmento y redacta la recomendación ejecutiva.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
from src.agent.state import BIAnalystState
from src.agent.prompts import SQLPlanOutput, BI_SYSTEM_INSTRUCTION
from src.database.connection import (
    get_schema_ddl_summary,
    execute_readonly_query,
    FORBIDDEN_SQL_KEYWORDS,
)

load_dotenv()


def _is_gemini_configured() -> bool:
    """Verifica si existe una llave API válida de Google Gemini en el archivo .env."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    return bool(api_key and api_key != "your_gemini_api_key_here")


# =====================================================================
# NODO 1: Inspector Dinámico de Esquema Relacional
# =====================================================================
def inspect_schema_node(state: BIAnalystState) -> Dict[str, Any]:
    """Obtiene la estructura actual de la tabla `commercial_sales` antes de planificar el SQL."""
    ddl = get_schema_ddl_summary()
    reasoning = list(state.get("reasoning_steps", []))
    reasoning.append(f"1. [Inspector de Esquema] Esquema relacional cargado: {ddl}")
    return {"schema_ddl": ddl, "reasoning_steps": reasoning}


# =====================================================================
# NODO 2: Generador Text-to-SQL y Auto-Corrector (Self-Healing)
# =====================================================================
def generate_sql_node(state: BIAnalystState) -> Dict[str, Any]:
    """
    Convierte la pregunta del usuario en una consulta SQL SELECT.
    Si hubo un error de sintaxis en el intento previo (`sql_error`), corrige la consulta.
    """
    question = state["question"]
    q_lower = question.lower()
    prev_error = state.get("sql_error")
    retries = state.get("retries", 0)
    reasoning = list(state.get("reasoning_steps", []))
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    # Si el usuario escribió un comando destructivo (ej. DROP TABLE), lo envía al Guardrail para su bloqueo y auditoría
    if FORBIDDEN_SQL_KEYWORDS.search(question):
        reasoning.append(
            "2. [Chain-of-Thought] Detectada instrucción potencialmente destructiva; enviando al Guardrail de Seguridad."
        )
        return {
            "generated_sql": question,
            "chart_type": "table",
            "reasoning_steps": reasoning,
        }

    # Si viene rebotado por un error SQL previo, incrementa el contador de Auto-Healing
    if prev_error:
        retries += 1
        reasoning.append(
            f"🔄 [Auto-Corrección SQL - Intento #{retries}] Corrigiendo error previo: {prev_error}"
        )

    # BLOQUE A: Generación con Google Gemini 3.8 Flash usando Structured Outputs (JSON Schema)
    if _is_gemini_configured():
        try:
            from google import genai

            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            prompt_input = (
                f"Pregunta de negocio: {question}\nEsquema: {state['schema_ddl']}"
            )
            if prev_error:
                prompt_input += f"\nLa consulta anterior `{state.get('generated_sql')}` falló con el error: {prev_error}. Corrige los nombres de columna o sintaxis."

            interaction = client.interactions.create(
                model=model_name,
                system_instruction=BI_SYSTEM_INSTRUCTION,
                input=prompt_input,
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": SQLPlanOutput.model_json_schema(),
                },
                store=False,
            )
            plan = SQLPlanOutput.model_validate_json(interaction.output_text)
            reasoning.append(f"2. [Razonamiento Gemini CoT] {plan.thought_process}")
            return {
                "generated_sql": plan.sql_query.strip().rstrip(";"),
                "chart_type": plan.chart_type,
                "retries": retries,
                "reasoning_steps": reasoning,
            }
        except Exception as exc:
            reasoning.append(
                f"[Aviso] Motor analítico determinista activado ({type(exc).__name__})."
            )

    # BLOQUE B: Compilador Text-to-SQL determinista para ejecución inmediata sin API Key
    if any(
        k in q_lower
        for k in [
            "región",
            "region",
            "ciudad",
            "lima",
            "arequipa",
            "cusco",
            "trujillo",
            "piura",
        ]
    ):
        sql = (
            "SELECT region, SUM(revenue_pen) AS total_ingresos, "
            "SUM(profit_pen) AS ganancia_neta, ROUND(AVG(margin_pct), 2) AS margen_promedio, "
            "SUM(units_sold) AS unidades_vendidas "
            "FROM commercial_sales GROUP BY region ORDER BY total_ingresos DESC"
        )
        chart = "bar"
        cot = "Agrupando ingresos, ganancia neta y margen promedio por dimensión `region` ordenado de mayor a menor."
    elif any(
        k in q_lower
        for k in ["categoría", "categoria", "línea", "linea", "margen", "rentabilidad"]
    ):
        sql = (
            "SELECT category, SUM(revenue_pen) AS ingresos_totales, "
            "SUM(profit_pen) AS utilidad_neta, ROUND(AVG(margin_pct), 2) AS margen_pct "
            "FROM commercial_sales GROUP BY category ORDER BY utilidad_neta DESC"
        )
        chart = "pie"
        cot = "Analizando rentabilidad y participación de mercado agrupado por `category`."
    elif any(
        k in q_lower
        for k in [
            "vendedor",
            "ejecutivo",
            "representante",
            "ranking",
            "sales_rep",
            "valeria",
            "diego",
        ]
    ):
        sql = (
            "SELECT sales_rep, SUM(revenue_pen) AS facturacion_pen, "
            "SUM(profit_pen) AS utilidad_generada, COUNT(id) AS operaciones_cerradas, "
            "ROUND(AVG(margin_pct), 2) AS margen_promedio "
            "FROM commercial_sales GROUP BY sales_rep ORDER BY facturacion_pen DESC"
        )
        chart = "bar"
        cot = "Evaluando KPI de desempeño comercial por ejecutivo de ventas (`sales_rep`)."
    elif any(
        k in q_lower
        for k in ["canal", "b2b", "e-commerce", "ecommerce", "retail", "channel"]
    ):
        sql = (
            "SELECT channel, SUM(revenue_pen) AS ingresos_canal, "
            "SUM(profit_pen) AS utilidad_canal, SUM(units_sold) AS unidades "
            "FROM commercial_sales GROUP BY channel ORDER BY ingresos_canal DESC"
        )
        chart = "pie"
        cot = "Segmentando facturación y volumen de unidades por canal de venta (`channel`)."
    elif any(
        k in q_lower
        for k in ["mes", "fecha", "tendencia", "evolución", "evolucion", "tiempo"]
    ):
        sql = (
            "SELECT sale_date, SUM(revenue_pen) AS ingresos_diarios, "
            "SUM(profit_pen) AS utilidad_diaria "
            "FROM commercial_sales GROUP BY sale_date ORDER BY sale_date ASC"
        )
        chart = "line"
        cot = "Construyendo serie temporal de ingresos y utilidad ordenada cronológicamente por `sale_date`."
    else:
        sql = (
            "SELECT product_name, SUM(revenue_pen) AS ingresos_pen, "
            "SUM(profit_pen) AS utilidad_pen, SUM(units_sold) AS unidades, "
            "ROUND(AVG(margin_pct), 2) AS margen_pct "
            "FROM commercial_sales GROUP BY product_name ORDER BY ingresos_pen DESC LIMIT 8"
        )
        chart = "bar"
        cot = "Consultando el Top de productos y soluciones tecnológicas por facturación acumulada (`product_name`)."

    reasoning.append(f"2. [Chain-of-Thought] {cot}")
    reasoning.append(f"3. [Compilador SQL] Consulta generada: `{sql}`")
    return {
        "generated_sql": sql,
        "chart_type": chart,
        "retries": retries,
        "reasoning_steps": reasoning,
    }


# =====================================================================
# NODO 3: Validador de Seguridad Read-Only y Ejecutor SQL
# =====================================================================
def validate_and_execute_sql_node(state: BIAnalystState) -> Dict[str, Any]:
    """Verifica que el SQL no tenga comandos peligrosos y lo ejecuta sobre la base de datos."""
    sql = state.get("generated_sql", "")
    reasoning = list(state.get("reasoning_steps", []))

    res = execute_readonly_query(sql)
    if not res["success"]:
        err_msg = res["error"] or "Error SQL desconocido"
        if "Bloqueado por seguridad" in err_msg or "Solo se permiten" in err_msg:
            reasoning.append(f"🛑 [Guardrail de Seguridad] {err_msg}")
            return {
                "sql_error": err_msg,
                "status": "BLOCKED_UNSAFE",
                "columns": [],
                "rows": [],
                "reasoning_steps": reasoning,
            }
        reasoning.append(f"⚠️ [Error de Ejecución SQL] {err_msg}")
        return {
            "sql_error": err_msg,
            "status": "ERROR",
            "columns": [],
            "rows": [],
            "reasoning_steps": reasoning,
        }

    reasoning.append(
        f"4. [Ejecución SQL] Consulta ejecutada con éxito ({res['row_count']} filas recuperadas)."
    )
    return {
        "sql_error": None,
        "status": "SUCCESS",
        "columns": res["columns"],
        "rows": res["rows"],
        "reasoning_steps": reasoning,
    }


# =====================================================================
# NODO 4: Sintetizador de Hallazgos de Inteligencia de Negocios (BI)
# =====================================================================
def synthesize_bi_insight_node(state: BIAnalystState) -> Dict[str, Any]:
    """Analiza las filas devueltas por el SQL y redacta un resumen ejecutivo para toma de decisiones."""
    status = state.get("status", "SUCCESS")
    reasoning = list(state.get("reasoning_steps", []))

    if status == "BLOCKED_UNSAFE":
        insight = (
            f"🛑 **Operación Bloqueada por Guardrail de Seguridad SQL**\n\n"
            f"- **Detalle:** {state.get('sql_error')}\n"
            f"- **Política:** El agente analítico opera exclusivamente con permisos `READ-ONLY` (`SELECT`) "
            "para proteger la integridad transaccional de la base de datos."
        )
        return {"executive_insight": insight, "reasoning_steps": reasoning}

    if status == "ERROR" or not state.get("rows"):
        insight = f"⚠️ No se pudieron obtener registros para la consulta: `{state.get('sql_error') or '0 filas'}`."
        return {"executive_insight": insight, "reasoning_steps": reasoning}

    rows = state["rows"]
    cols = state["columns"]
    top_row = rows[0]

    metric_highlights = []
    for k, v in top_row.items():
        if isinstance(v, float):
            metric_highlights.append(f"**{k}:** `{v:,.2f}`")
        else:
            metric_highlights.append(f"**{k}:** `{v}`")

    # Busca la primera columna numérica para calcular la sumatoria acumulada real
    numeric_col = cols[1] if len(cols) > 1 else cols[0]
    for c in cols:
        if isinstance(top_row.get(c), (int, float)):
            numeric_col = c
            break

    total_numeric_sum = sum(
        float(r.get(numeric_col, 0))
        for r in rows
        if isinstance(r.get(numeric_col), (int, float))
    )

    insight = (
        f"📈 **Hallazgo Ejecutivo de Inteligencia de Negocios**\n\n"
        f"- **Líder del Segmento (#1):** {' | '.join(metric_highlights)}\n"
        f"- **Total Acumulado (`{numeric_col}`):** `S/ {total_numeric_sum:,.2f}` en `{len(rows)}` segmentos analizados.\n"
        f"- **Recomendación Estratégica:** Priorizar asignación comercial en el segmento líder y replicar soluciones de alto margen (Consultoría IA y Cloud B2B) en regiones en expansión."
    )
    reasoning.append(
        "5. [Síntesis BI] Reporte ejecutivo generado con indicadores clave."
    )
    return {"executive_insight": insight, "reasoning_steps": reasoning}
