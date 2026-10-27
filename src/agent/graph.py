"""
ORQUESTADOR DEL GRAFO DE INTELIGENCIA DE NEGOCIOS (LANGGRAPH STATEGRAPH)
========================================================================
Conecta los 4 nodos analíticos e implementa el bucle de Auto-Corrección SQL:
si una consulta falla por un error de sintaxis, regresa al nodo generador (`generate_sql`)
hasta un máximo de 2 reintentos antes de finalizar.
"""

import time
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from src.agent.state import BIAnalystState
from src.agent.nodes import (
    inspect_schema_node,
    generate_sql_node,
    validate_and_execute_sql_node,
    synthesize_bi_insight_node,
)
from src.database.connection import get_db_context
from src.database.models import SQLQueryAudit


def _route_after_execution(state: BIAnalystState) -> str:
    """
    Arista condicional de Auto-Corrección (Self-Healing SQL):
    - Si hubo un error de sintaxis (`status == 'ERROR'`) y lleva menos de 2 reintentos,
      regresa al nodo `generate_sql` para corregirlo.
    - Si tuvo éxito o fue bloqueado por seguridad, avanza a `synthesize_bi_insight`.
    """
    if (
        state.get("status") == "ERROR"
        and state.get("sql_error")
        and state.get("retries", 0) < 2
    ):
        return "generate_sql"
    return "synthesize_bi_insight"


def build_bi_analyst_graph():
    """Construye y compila el grafo de estados Text-to-SQL en LangGraph."""
    workflow = StateGraph(BIAnalystState)

    workflow.add_node("inspect_schema", inspect_schema_node)
    workflow.add_node("generate_sql", generate_sql_node)
    workflow.add_node("validate_and_execute_sql", validate_and_execute_sql_node)
    workflow.add_node("synthesize_bi_insight", synthesize_bi_insight_node)

    workflow.add_edge(START, "inspect_schema")
    workflow.add_edge("inspect_schema", "generate_sql")
    workflow.add_edge("generate_sql", "validate_and_execute_sql")
    workflow.add_conditional_edges(
        "validate_and_execute_sql",
        _route_after_execution,
        {
            "generate_sql": "generate_sql",
            "synthesize_bi_insight": "synthesize_bi_insight",
        },
    )
    workflow.add_edge("synthesize_bi_insight", END)

    return workflow.compile()


compiled_bi_graph = build_bi_analyst_graph()


def run_bi_analyst_agent(question: str) -> Dict[str, Any]:
    """Ejecuta el grafo BI completo, mide la latencia en milisegundos y guarda la auditoría SQL."""
    start_ts = time.perf_counter()

    initial_state: BIAnalystState = {
        "question": question,
        "schema_ddl": "",
        "reasoning_steps": [],
        "generated_sql": "",
        "sql_error": None,
        "retries": 0,
        "columns": [],
        "rows": [],
        "chart_type": "bar",
        "executive_insight": "",
        "status": "SUCCESS",
        "latency_ms": 0.0,
    }

    final_state = compiled_bi_graph.invoke(initial_state)
    elapsed_ms = round((time.perf_counter() - start_ts) * 1000.0, 2)
    final_state["latency_ms"] = elapsed_ms

    # Registra la consulta en la tabla de auditoría `sql_query_audit`
    with get_db_context() as db:
        audit = SQLQueryAudit(
            question=question,
            generated_sql=final_state.get("generated_sql", ""),
            retries=final_state.get("retries", 0),
            rows_returned=len(final_state.get("rows", [])),
            latency_ms=elapsed_ms,
            status=final_state.get("status", "SUCCESS"),
            executive_insight=final_state.get("executive_insight", ""),
        )
        db.add(audit)
        db.commit()

    return final_state
