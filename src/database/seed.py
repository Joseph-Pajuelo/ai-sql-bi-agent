"""
DATOS SEMILLA DE INTELIGENCIA COMERCIAL (SEEDING BI)
====================================================
Carga un conjunto de datos multidimensional de ventas tecnológicas en Perú
(Lima, Arequipa, Trujillo, Cusco y Piura) a través de canales B2B, E-Commerce y Retail.
"""

from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session
from src.database.models import CommercialSale, SQLQueryAudit


def seed_commercial_data(db: Session) -> None:
    """Inserta los registros comerciales e historial de auditoría si la base de datos está vacía."""
    if db.query(CommercialSale).first() is not None:
        return

    # Tuplas con: (fecha, región, canal, categoría, solución/producto, ejecutivo, unidades, ingresos, costo)
    records = [
        # Región Lima
        ("2026-08-05", "Lima", "B2B Corporativo", "Consultoría IA", "Implementación Agente LangGraph Enterprise", "Valeria Soto", 3, 28500.0, 11400.0),
        ("2026-08-12", "Lima", "B2B Corporativo", "Cloud & Licencias", "Suscripción Anual Cloud Data Warehouse", "Diego Paredes", 5, 42000.0, 18900.0),
        ("2026-08-19", "Lima", "E-Commerce", "Hardware", "Workstation Pro 32GB NVMe", "Camila Ríos", 12, 54000.0, 37800.0),
        ("2026-09-03", "Lima", "B2B Corporativo", "Ciberseguridad", "Auditoría Zero-Trust & Pentesting", "Valeria Soto", 4, 32000.0, 12800.0),
        ("2026-09-14", "Lima", "Retail Tienda", "Hardware", "Monitor UltraHD 4K 27 IPS", "Jorge Salazar", 25, 33750.0, 22500.0),
        ("2026-09-25", "Lima", "B2B Corporativo", "Consultoría IA", "Automatización RPA + LLM Facturación", "Valeria Soto", 2, 19800.0, 7500.0),
        ("2026-10-04", "Lima", "E-Commerce", "Cloud & Licencias", "Licencia Power BI Embedded Pro Pack", "Diego Paredes", 15, 22500.0, 9000.0),
        ("2026-10-15", "Lima", "B2B Corporativo", "Consultoría IA", "Agente SDR Omnicanal WhatsApp + CRM", "Valeria Soto", 4, 36000.0, 12600.0),
        # Región Arequipa
        ("2026-08-08", "Arequipa", "B2B Corporativo", "Cloud & Licencias", "Suscripción Anual Cloud Data Warehouse", "Diego Paredes", 2, 16800.0, 7560.0),
        ("2026-09-10", "Arequipa", "E-Commerce", "Hardware", "Workstation Pro 32GB NVMe", "Camila Ríos", 6, 27000.0, 18900.0),
        ("2026-10-02", "Arequipa", "B2B Corporativo", "Consultoría IA", "Dashboard Predictivo Minería & Logística", "Valeria Soto", 2, 24000.0, 9600.0),
        ("2026-10-18", "Arequipa", "Retail Tienda", "Hardware", "Monitor UltraHD 4K 27 IPS", "Jorge Salazar", 14, 18900.0, 12600.0),
        # Región Trujillo
        ("2026-08-22", "Trujillo", "E-Commerce", "Hardware", "Teclado Mecánico & Kit Productividad", "Camila Ríos", 30, 11400.0, 6840.0),
        ("2026-09-17", "Trujillo", "B2B Corporativo", "Consultoría IA", "Agente SDR Omnicanal WhatsApp + CRM", "Valeria Soto", 2, 18000.0, 6300.0),
        ("2026-10-09", "Trujillo", "B2B Corporativo", "Ciberseguridad", "Protección Endpoint Corporativo", "Diego Paredes", 8, 19200.0, 8640.0),
        # Región Cusco
        ("2026-08-28", "Cusco", "B2B Corporativo", "Consultoría IA", "Motor de Reservas Inteligente & Pricing", "Valeria Soto", 3, 25500.0, 9690.0),
        ("2026-09-21", "Cusco", "E-Commerce", "Hardware", "Monitor UltraHD 4K 27 IPS", "Camila Ríos", 10, 13500.0, 9000.0),
        ("2026-10-12", "Cusco", "Retail Tienda", "Cloud & Licencias", "Licencia Power BI Embedded Pro Pack", "Jorge Salazar", 6, 9000.0, 3600.0),
        # Región Piura
        ("2026-09-05", "Piura", "B2B Corporativo", "Cloud & Licencias", "Migración Base de Datos PostgreSQL Cloud", "Diego Paredes", 3, 21000.0, 8820.0),
        ("2026-10-20", "Piura", "E-Commerce", "Hardware", "Workstation Pro 32GB NVMe", "Camila Ríos", 5, 22500.0, 15750.0),
    ]

    # Calcula automáticamente la ganancia neta (profit_pen) y el margen porcentual (margin_pct)
    sales_objs = []
    for s_date, region, channel, category, prod, rep, units, rev, cost in records:
        profit = round(rev - cost, 2)
        margin = round((profit / rev) * 100.0, 2) if rev > 0 else 0.0
        sales_objs.append(
            CommercialSale(
                sale_date=date.fromisoformat(s_date),
                region=region,
                channel=channel,
                category=category,
                product_name=prod,
                sales_rep=rep,
                units_sold=units,
                revenue_pen=rev,
                cost_pen=cost,
                profit_pen=profit,
                margin_pct=margin,
            )
        )

    db.add_all(sales_objs)

    # Inserta consultas de ejemplo en el historial de auditoría SQL
    now = datetime.now(timezone.utc)
    sample_audits = [
        SQLQueryAudit(
            timestamp=now - timedelta(hours=3),
            question="¿Cuáles son los ingresos y ganancia neta por región ordenados de mayor a menor?",
            generated_sql="SELECT region, SUM(revenue_pen) AS total_ingresos, SUM(profit_pen) AS ganancia_neta, ROUND(AVG(margin_pct), 2) AS margen_promedio FROM commercial_sales GROUP BY region ORDER BY total_ingresos DESC",
            retries=0,
            rows_returned=5,
            latency_ms=310.4,
            status="SUCCESS",
            executive_insight="Lima lidera la facturación acumulada, seguida por Arequipa y Cusco con márgenes superiores al 50% en servicios B2B.",
        ),
        SQLQueryAudit(
            timestamp=now - timedelta(hours=1),
            question="¿Qué categoría de negocio tiene la mayor rentabilidad y margen porcentual?",
            generated_sql="SELECT category, SUM(revenue_pen) AS ingresos, SUM(profit_pen) AS utilidad, ROUND(AVG(margin_pct), 2) AS margen_pct FROM commercial_sales GROUP BY category ORDER BY utilidad DESC",
            retries=0,
            rows_returned=4,
            latency_ms=285.0,
            status="SUCCESS",
            executive_insight="Consultoría IA presenta el mayor margen porcentual (>60%), mientras que Hardware aporta volumen bruto alto pero menor margen relativo.",
        ),
    ]
    db.add_all(sample_audits)
    db.commit()
