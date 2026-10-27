# =====================================================================
# DOCKERFILE - PROYECTO 2: AI BUSINESS INTELLIGENCE & SQL ANALYST AGENT
# =====================================================================
# Empaqueta el motor Text-to-SQL de LangGraph, el Guardrail de Seguridad,
# la API REST en FastAPI y el Centro de Comando Cyber-Tech en Streamlit.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt psycopg2-binary

COPY . .

# Expone el puerto 8001 (FastAPI BI) y el puerto 8502 (Dashboard Cyber-Tech Streamlit)
EXPOSE 8001 8502

CMD ["streamlit", "run", "src/dashboard/bi_app.py", "--server.port=8502", "--server.address=0.0.0.0", "--server.headless=true"]
