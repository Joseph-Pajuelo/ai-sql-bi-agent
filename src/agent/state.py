"""
ESTADO DEL AGENTE ANALISTA DE INTELIGENCIA DE NEGOCIOS (LANGGRAPH STATE)
========================================================================
Define los campos que viajan entre los nodos del flujo Text-to-SQL:
pregunta, esquema DDL, consulta SQL generada, reintentos de auto-corrección,
resultados tabulares, recomendación de gráfico y hallazgo ejecutivo.
"""

from typing import TypedDict, List, Dict, Any, Optional


class BIAnalystState(TypedDict):
    """Diccionario tipado que mantiene la memoria de ejecución del grafo BI."""

    question: str
    schema_ddl: str
    reasoning_steps: List[str]
    generated_sql: str
    sql_error: Optional[str]
    retries: int
    columns: List[str]
    rows: List[Dict[str, Any]]
    chart_type: str  # Valores posibles: 'bar', 'pie', 'line', 'table'
    executive_insight: str
    status: str  # Valores posibles: 'SUCCESS', 'BLOCKED_UNSAFE', 'ERROR'
    latency_ms: float
