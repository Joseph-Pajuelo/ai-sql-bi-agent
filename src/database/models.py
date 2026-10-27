"""
MODELOS DE DATOS PARA INTELIGENCIA DE NEGOCIOS Y AUDITORÍA SQL
==============================================================
Define dos tablas clave:
1. `CommercialSale`: Tabla de hechos comercial normalizada con ventas por región,
   canal, categoría, ejecutivo, ingresos, costos, utilidad neta y margen porcentual.
2. `SQLQueryAudit`: Tabla de auditoría que registra cada consulta generada por el agente,
   su latencia, si requirió auto-corrección y si fue bloqueada por seguridad.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def utc_now() -> datetime:
    """Retorna la fecha y hora actual en UTC para los registros de auditoría."""
    return datetime.now(timezone.utc)


# =====================================================================
# 1. TABLA DE HECHOS COMERCIAL (commercial_sales)
# Almacena las operaciones de venta para análisis de KPIs y rentabilidad
# =====================================================================
class CommercialSale(Base):
    __tablename__ = "commercial_sales"

    id = Column(Integer, primary_key=True, index=True)
    sale_date = Column(Date, nullable=False, index=True)
    region = Column(String(60), nullable=False, index=True)  # Lima, Arequipa, Trujillo, Cusco, Piura
    channel = Column(String(40), nullable=False, index=True)  # B2B Corporativo, E-Commerce, Retail Tienda
    category = Column(String(60), nullable=False, index=True)  # Consultoría IA, Cloud & Licencias, Hardware, Ciberseguridad
    product_name = Column(String(120), nullable=False)
    sales_rep = Column(String(80), nullable=False)
    units_sold = Column(Integer, nullable=False)
    revenue_pen = Column(Float, nullable=False)  # Ingresos brutos en Soles (S/)
    cost_pen = Column(Float, nullable=False)  # Costo operativo en Soles (S/)
    profit_pen = Column(Float, nullable=False)  # Ganancia neta (revenue - cost)
    margin_pct = Column(Float, nullable=False)  # Margen porcentual ((profit / revenue) * 100)


# =====================================================================
# 2. TABLA DE AUDITORÍA DE CONSULTAS SQL (sql_query_audit)
# Registra cada pregunta en lenguaje natural y el SQL exacto ejecutado
# =====================================================================
class SQLQueryAudit(Base):
    __tablename__ = "sql_query_audit"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    question = Column(Text, nullable=False)
    generated_sql = Column(Text, nullable=False)
    retries = Column(Integer, default=0)  # Número de reintentos de Auto-Corrección (Self-Healing)
    rows_returned = Column(Integer, default=0)
    latency_ms = Column(Float, nullable=False)
    status = Column(String(30), nullable=False)  # SUCCESS, BLOCKED_UNSAFE, ERROR
    executive_insight = Column(Text, nullable=True)
