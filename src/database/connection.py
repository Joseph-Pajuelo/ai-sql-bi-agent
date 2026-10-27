"""
CONEXIÓN DE BASE DE DATOS, INSPECTOR DE ESQUEMA Y GUARDRAIL DE SEGURIDAD SQL
============================================================================
Este archivo cumple 3 funciones críticas:
1. Conecta el sistema a SQLite local (o PostgreSQL en producción).
2. Inspecciona dinámicamente las columnas de las tablas (`get_schema_ddl_summary`) para que el agente conozca la base de datos.
3. Implementa el Candado de Seguridad Read-Only (`validate_readonly_sql`) que bloquea cualquier intento de borrar o modificar tablas.
"""

import os
import re
from contextlib import contextmanager
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from src.database.models import Base

load_dotenv()

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "commercial_bi.db",
)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# Expresión regular que detecta comandos destructivos o de modificación de datos
FORBIDDEN_SQL_KEYWORDS = re.compile(
    r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|CREATE|REPLACE|GRANT|REVOKE|ATTACH|DETACH)\b",
    re.IGNORECASE,
)


def init_bi_db() -> None:
    """Crea las tablas del modelo comercial e inserta los datos iniciales si está vacío."""
    Base.metadata.create_all(bind=engine)
    from src.database.seed import seed_commercial_data

    with get_db_context() as db:
        seed_commercial_data(db)


@contextmanager
def get_db_context():
    """Administrador de sesión de base de datos con confirmación (commit) y reversión (rollback) automática."""
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_schema_ddl_summary() -> str:
    """
    Lee en tiempo real los nombres de tablas y columnas de la base de datos
    para enviárselos como contexto al modelo de IA antes de generar el SQL.
    """
    inspector = inspect(engine)
    lines: List[str] = []
    for table_name in inspector.get_table_names():
        if table_name == "sql_query_audit":
            continue
        cols = inspector.get_columns(table_name)
        col_defs = ", ".join(f"{c['name']} ({c['type']})" for c in cols)
        lines.append(f"Table `{table_name}`: {col_defs}")
    return "\n".join(lines)


def validate_readonly_sql(sql_query: str) -> Tuple[bool, str]:
    """
    GUARDRAIL DE SEGURIDAD SQL (MODO SOLO LECTURA):
    Verifica que la consulta generada sea únicamente de lectura (`SELECT` o `WITH`)
    y que no contenga comandos destructivos ni inyección de múltiples sentencias.
    """
    cleaned = sql_query.strip().rstrip(";")
    if not cleaned:
        return False, "La consulta SQL está vacía."

    if ";" in cleaned:
        return (
            False,
            "Bloqueado por seguridad: No se permiten múltiples sentencias SQL separadas por punto y coma.",
        )

    match = FORBIDDEN_SQL_KEYWORDS.search(cleaned)
    if match:
        return (
            False,
            f"Bloqueado por seguridad (Guardrail Read-Only): Operación '{match.group(1).upper()}' no permitida.",
        )

    if not (
        cleaned.upper().startswith("SELECT") or cleaned.upper().startswith("WITH")
    ):
        return (
            False,
            "Solo se permiten consultas analíticas que inicien con SELECT o WITH.",
        )

    return True, "OK"


def execute_readonly_query(sql_query: str) -> Dict[str, Any]:
    """
    Primero pasa la consulta por el Guardrail de Seguridad (`validate_readonly_sql`).
    Si es segura, la ejecuta en la base de datos y devuelve las columnas y filas resultantes.
    """
    is_valid, reason = validate_readonly_sql(sql_query)
    if not is_valid:
        return {"success": False, "error": reason, "columns": [], "rows": []}

    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return {
                "success": True,
                "error": None,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
            }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "columns": [],
            "rows": [],
            "row_count": 0,
        }
