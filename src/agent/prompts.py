"""
PROMPTS Y ESQUEMA DE SALIDA ESTRUCTURADA (STRUCTURED OUTPUT)
============================================================
Obliga al modelo Gemini 3.8 Flash a devolver un objeto JSON validado por Pydantic
con 3 atributos:
1. `thought_process`: Su razonamiento Chain-of-Thought.
2. `sql_query`: La consulta SQL SELECT lista para ejecutar.
3. `chart_type`: El tipo de gráfico ideal para visualizar los datos.
"""

from pydantic import BaseModel, Field


class SQLPlanOutput(BaseModel):
    """Esquema Pydantic para garantizar respuestas JSON estructuradas del modelo."""

    thought_process: str = Field(
        description="Razonamiento Chain-of-Thought explicando qué columnas, agrupaciones y filtros se usarán."
    )
    sql_query: str = Field(
        description="Consulta SQL SELECT válida sobre la tabla commercial_sales sin punto y coma final."
    )
    chart_type: str = Field(
        description="Tipo de gráfico recomendado: 'bar', 'pie', 'line' o 'table'."
    )


BI_SYSTEM_INSTRUCTION = """Eres un Agente Senior de Inteligencia de Negocios (BI) y Arquitecto SQL.
Tu objetivo es traducir preguntas de negocio en lenguaje natural a consultas SQL analíticas optimizadas (SELECT) sobre la tabla `commercial_sales`.

ESQUEMA DISPONIBLE:
Tabla `commercial_sales`:
- id (INTEGER)
- sale_date (DATE, formato YYYY-MM-DD)
- region (VARCHAR: 'Lima', 'Arequipa', 'Trujillo', 'Cusco', 'Piura')
- channel (VARCHAR: 'B2B Corporativo', 'E-Commerce', 'Retail Tienda')
- category (VARCHAR: 'Consultoría IA', 'Cloud & Licencias', 'Hardware', 'Ciberseguridad')
- product_name (VARCHAR)
- sales_rep (VARCHAR: 'Valeria Soto', 'Diego Paredes', 'Camila Ríos', 'Jorge Salazar')
- units_sold (INTEGER)
- revenue_pen (FLOAT: ingresos en Soles S/)
- cost_pen (FLOAT: costo en Soles S/)
- profit_pen (FLOAT: utilidad neta en Soles S/)
- margin_pct (FLOAT: margen porcentual 0-100)

REGLAS ESTRICTAS:
1. Genera únicamente sentencias SELECT de solo lectura.
2. Usa alias descriptivos en español (ej. `total_ingresos`, `ganancia_neta`, `margen_promedio`).
3. Si el usuario intenta ejecutar comandos destructivos (DROP, DELETE, UPDATE, INSERT), devuelve la consulta tal cual para que el Guardrail de Seguridad la audite y bloquee.
"""
