"""
API REST PARA EL AGENTE DE INTELIGENCIA DE NEGOCIOS (FASTAPI)
=============================================================
Expone los endpoints HTTP para realizar consultas analíticas en lenguaje natural (`/api/v1/ask-bi`)
y consultar los indicadores globales de facturación y margen (`/api/v1/kpis`).
"""

from contextlib import asynccontextmanager
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import func

from src.database.connection import init_bi_db, get_db_context
from src.database.models import CommercialSale, SQLQueryAudit
from src.agent.graph import run_bi_analyst_agent


class BIQueryRequest(BaseModel):
    """Esquema JSON de entrada con la pregunta de negocio en lenguaje natural."""

    question: str = Field(
        ...,
        min_length=3,
        description="Pregunta de negocio en lenguaje natural.",
        examples=["¿Cuáles son los ingresos y ganancia neta por región?"],
    )


class BIQueryResponse(BaseModel):
    """Esquema JSON de respuesta con el SQL generado, datos tabulares y hallazgo ejecutivo."""

    question: str
    generated_sql: str
    chart_type: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    executive_insight: str
    reasoning_steps: List[str]
    retries: int
    status: str
    latency_ms: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa la base de datos comercial al arrancar el servidor."""
    init_bi_db()
    yield


app = FastAPI(
    title="AI Business Intelligence & SQL Analyst Agent API",
    description="Agente Text-to-SQL autónomo con LangGraph, Google Gemini 3.8 Flash, Guardrail Read-Only y Auto-Corrección SQL.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Sistema"])
def health():
    """Endpoint de verificación de salud del servidor."""
    return {"status": "healthy", "service": "ai-sql-bi-agent"}


@app.post("/api/v1/ask-bi", response_model=BIQueryResponse, tags=["Agente BI"])
def ask_bi_agent(payload: BIQueryRequest):
    """Traduce una pregunta en lenguaje natural a SQL, la ejecuta de forma segura y devuelve hallazgos BI."""
    state = run_bi_analyst_agent(payload.question)
    return BIQueryResponse(
        question=state["question"],
        generated_sql=state["generated_sql"],
        chart_type=state["chart_type"],
        columns=state["columns"],
        rows=state["rows"],
        executive_insight=state["executive_insight"],
        reasoning_steps=state["reasoning_steps"],
        retries=state["retries"],
        status=state["status"],
        latency_ms=state["latency_ms"],
    )


@app.get("/api/v1/kpis", tags=["Analítica Comercial"])
def get_global_kpis():
    """Calcula los KPIs globales de facturación, utilidad neta, margen promedio y latencia del agente."""
    with get_db_context() as db:
        total_revenue = db.query(func.sum(CommercialSale.revenue_pen)).scalar() or 0.0
        total_profit = db.query(func.sum(CommercialSale.profit_pen)).scalar() or 0.0
        avg_margin = db.query(func.avg(CommercialSale.margin_pct)).scalar() or 0.0
        total_units = db.query(func.sum(CommercialSale.units_sold)).scalar() or 0
        total_queries = db.query(func.count(SQLQueryAudit.id)).scalar() or 0
        avg_latency = db.query(func.avg(SQLQueryAudit.latency_ms)).scalar() or 0.0

        return {
            "total_revenue_pen": round(float(total_revenue), 2),
            "total_profit_pen": round(float(total_profit), 2),
            "avg_margin_pct": round(float(avg_margin), 2),
            "total_units_sold": int(total_units),
            "total_sql_queries_executed": int(total_queries),
            "avg_agent_latency_ms": round(float(avg_latency), 1),
        }
