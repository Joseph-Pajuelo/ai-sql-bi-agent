"""
SUITE DE PRUEBAS AUTOMATIZADAS DEL AGENTE BI & SQL (PYTEST)
===========================================================
Valida la generación de consultas SQL por región y categoría,
el bloqueo de seguridad ante comandos destructivos (`DROP TABLE`) y los endpoints REST.
"""

from fastapi.testclient import TestClient
from src.database.connection import init_bi_db, validate_readonly_sql
from src.agent.graph import run_bi_analyst_agent
from src.api.main import app


def setup_module():
    """Inicializa la base de datos de Inteligencia Comercial antes de correr los tests."""
    init_bi_db()


def test_regional_revenue_analysis():
    """Prueba 1: Análisis de ingresos y ganancia neta agrupado por región."""
    state = run_bi_analyst_agent("¿Cuáles son los ingresos y ganancia neta por región?")
    assert state["status"] == "SUCCESS"
    assert len(state["rows"]) == 5
    assert "region" in state["columns"]


def test_category_margin_analysis():
    """Prueba 2: Análisis de rentabilidad y margen porcentual por categoría."""
    state = run_bi_analyst_agent("¿Qué categoría tiene mayor margen y rentabilidad?")
    assert state["status"] == "SUCCESS"
    assert len(state["rows"]) >= 3
    assert state["chart_type"] == "pie"


def test_readonly_sql_security_guardrail():
    """Prueba 3: Verifica que SELECT sea permitido y que DROP TABLE sea bloqueado."""
    valid, _ = validate_readonly_sql(
        "SELECT region, SUM(revenue_pen) FROM commercial_sales GROUP BY region"
    )
    assert valid is True

    invalid_drop, msg = validate_readonly_sql("DROP TABLE commercial_sales")
    assert invalid_drop is False
    assert "DROP" in msg

    state_blocked = run_bi_analyst_agent("DROP TABLE commercial_sales")
    assert state_blocked["status"] == "BLOCKED_UNSAFE"


def test_bi_fastapi_endpoints():
    """Prueba 4: Verifica los endpoints HTTP (/api/v1/kpis y /api/v1/ask-bi)."""
    with TestClient(app) as client:
        res_kpis = client.get("/api/v1/kpis")
        assert res_kpis.status_code == 200
        assert res_kpis.json()["total_revenue_pen"] > 0

        res_ask = client.post(
            "/api/v1/ask-bi",
            json={"question": "Muéstrame el ranking por ejecutivo de ventas"},
        )
        assert res_ask.status_code == 200
        assert res_ask.json()["status"] == "SUCCESS"
