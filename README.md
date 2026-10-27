# 📊 AI Business Intelligence & SQL Analyst Agent

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Text--to--SQL-orange.svg)
![Gemini](https://img.shields.io/badge/Google%20GenAI-Gemini%203.8%20Flash-4285F4.svg)
![SQL](https://img.shields.io/badge/SQL-PostgreSQL%20%7C%20SQLite-336791.svg)
![BI](https://img.shields.io/badge/Business%20Intelligence-Plotly%20%26%20KPIs-success.svg)

Agente autónomo de **Inteligencia de Negocios (BI) y Text-to-SQL** construido con **Python, LangGraph y Google Gemini 3.8 Flash**. Permite a gerentes y analistas consultar métricas comerciales complejas en lenguaje natural, generando consultas SQL optimizadas con validación de seguridad **Read-Only**, bucle de **Auto-Corrección (Self-Healing SQL)**, síntesis ejecutiva de KPIs y visualización interactiva.

---

## 🏗️ Flujo del Agente con Chain-of-Thought y Auto-Corrección (LangGraph)

```mermaid
flowchart TD
    Start([Pregunta de Negocio en Lenguaje Natural]) --> Inspect[Nodo 1: inspect_schema<br/>Inspección Dinámica de Tablas DDL]
    Inspect --> Generate[Nodo 2: generate_sql<br/>Chain-of-Thought + Structured Output JSON]
    Generate --> Execute[Nodo 3: validate_and_execute_sql<br/>Guardrail Read-Only + Ejecución SQL]
    
    Execute -->|Error de Sintaxis y retries < 2| Generate
    Execute -->|Operación Peligrosa Bloqueada| Synthesize[Nodo 4: synthesize_bi_insight<br/>Síntesis Ejecutiva + Recomendación]
    Execute -->|Ejecución Exitosa| Synthesize
    
    Synthesize --> Audit[(Registro de Auditoría<br/>sql_query_audit)]
    Audit --> EndNode([Tabla + Gráfico Plotly + Hallazgo BI])
```

---

## ✨ Características Técnicas Destacadas

1. **Inspección Dinámica de Esquema y Text-to-SQL con Structured Outputs**:
   - Extrae automáticamente metadatos de las tablas relacionales (`commercial_sales`) y planifica agregaciones (`SUM`, `AVG`, `COUNT`, `GROUP BY`) usando esquemas Pydantic y `gemini-3.8-flash`.
2. **Guardrail de Seguridad SQL (`Read-Only`)**:
   - Bloquea de forma preventiva cualquier intento de ejecución de comandos destructivos (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`) o inyección de múltiples sentencias.
3. **Bucle de Auto-Corrección (Self-Healing SQL)**:
   - Si una consulta SQL falla por un nombre de columna o sintaxis, la arista condicional de **LangGraph** re-enruta el mensaje de error al nodo generador para corregir la consulta automáticamente.
4. **Síntesis Ejecutiva y Visualización Automática**:
   - Selecciona dinámicamente el tipo de visualización (`bar`, `pie`, `line`) y redacta conclusiones estratégicas orientadas a la toma de decisiones comerciales.

---

## 🚀 Cómo Ejecutar el Proyecto

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Lanzar el Dashboard Analítico en Streamlit
```bash
streamlit run src/dashboard/bi_app.py
```

### 3. Lanzar la API REST (FastAPI)
```bash
uvicorn src.api.main:app --reload --port 8001
```

### 4. Ejecutar pruebas automatizadas (Pytest)
```bash
pytest -v
```

---

## 👤 Autor
**Joseph Pajuelo Cárdenas**  
Ingeniería de Sistemas e Informática (UTP) | Business Intelligence & AI Agents  
[LinkedIn](https://linkedin.com/in/josephpajuelo) • [GitHub](https://github.com/Joseph-Pajuelo)
