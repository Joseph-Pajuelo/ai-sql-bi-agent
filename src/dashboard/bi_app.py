"""
CENTRO DE COMANDO CYBER-TECH DE INTELIGENCIA DE NEGOCIOS Y ANALISTA SQL (STREAMLIT)
===================================================================================
Este archivo construye la interfaz visual futurista del Proyecto 2:
1. Inyecta un fondo interactivo HTML5 Canvas de Red Neuronal en pantalla completa
   que reacciona en tiempo real al movimiento y clic del mouse (`mousemove` / `click`).
2. Aplica estilos CSS avanzados (Glassmorphism, bordes de neón, animaciones `@keyframes`
   y efectos 3D al pasar el cursor sobre las tarjetas KPI y botones).
3. Conecta la interfaz con el grafo Text-to-SQL de LangGraph (`run_bi_analyst_agent`)
   y renderiza gráficos interactivos de Plotly con paleta Cyber-Neon.
"""

import os
import sys
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

# Agrega la raíz del proyecto al path de Python para importar los módulos de `src/`
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.database.connection import init_bi_db, get_db_context
from src.database.models import CommercialSale, SQLQueryAudit
from src.agent.graph import run_bi_analyst_agent
from src.api.main import get_global_kpis

# =====================================================================
# BLOQUE 1: Configuración de la Página e Inicialización de Base de Datos
# =====================================================================
st.set_page_config(
    page_title="NEURAL BI // Autonomous SQL Analyst",
    page_icon="⚡",
    layout="wide",
)

# Crea las tablas y datos comerciales si aún no están cargados
init_bi_db()

# =====================================================================
# BLOQUE 2: Inyección de CSS Futurista (Glassmorphism + Animaciones Neón)
# =====================================================================
CYBER_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600&display=swap');

/* Hace transparente el contenedor principal de Streamlit para que se vea el Canvas interactivo detrás */
.stApp {
    background: radial-gradient(circle at 50% 10%, rgba(12, 20, 44, 0.72) 0%, rgba(4, 7, 17, 0.90) 100%) !important;
    color: #e2f1ff;
    font-family: 'Inter', sans-serif;
}

/* Asegura que el contenido de Streamlit quede por encima del lienzo de partículas */
.main .block-container {
    position: relative;
    z-index: 2;
    padding-top: 1.8rem;
}

header[data-testid="stHeader"] {
    background: rgba(4, 7, 17, 0.45) !important;
    backdrop-filter: blur(8px);
}

/* Animación de brillo pulsante para el título y bordes */
@keyframes neonPulse {
    0%, 100% {
        text-shadow: 0 0 12px rgba(0, 245, 212, 0.75), 0 0 28px rgba(0, 187, 249, 0.45);
    }
    50% {
        text-shadow: 0 0 22px rgba(155, 93, 229, 0.95), 0 0 42px rgba(0, 245, 212, 0.75);
    }
}

@keyframes borderFlow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes floatCard {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-4px); }
}

/* Encabezado Tecnológico HUD */
.cyber-hero {
    position: relative;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(10, 19, 41, 0.80) 0%, rgba(20, 14, 48, 0.72) 100%);
    border: 1px solid rgba(0, 245, 212, 0.35);
    box-shadow: 0 0 32px rgba(0, 245, 212, 0.12), inset 0 0 20px rgba(155, 93, 229, 0.10);
    backdrop-filter: blur(14px);
    margin-bottom: 1.5rem;
    overflow: hidden;
    transition: all 0.35s ease;
}

.cyber-hero:hover {
    border-color: rgba(0, 245, 212, 0.75);
    box-shadow: 0 0 42px rgba(0, 245, 212, 0.25), inset 0 0 25px rgba(0, 187, 249, 0.15);
}

.cyber-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 4px 14px;
    border-radius: 999px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #00f5d4;
    background: rgba(0, 245, 212, 0.12);
    border: 1px solid rgba(0, 245, 212, 0.45);
    margin-bottom: 0.6rem;
}

.pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #00f5d4;
    box-shadow: 0 0 10px #00f5d4;
    animation: neonPulse 1.6s infinite;
}

.cyber-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.15rem;
    font-weight: 900;
    letter-spacing: 1px;
    margin: 0;
    background: linear-gradient(90deg, #00f5d4, #00bbf9, #c77dff, #00f5d4);
    background-size: 250% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: borderFlow 6s linear infinite;
}

.cyber-subtitle {
    color: #9ec5fe;
    font-size: 0.95rem;
    margin-top: 0.4rem;
    margin-bottom: 0;
}

/* Tarjetas de Métricas Holográficas (KPIs) */
div[data-testid="stMetric"] {
    background: rgba(11, 22, 44, 0.72) !important;
    border: 1px solid rgba(0, 245, 212, 0.30) !important;
    border-radius: 14px !important;
    padding: 16px 18px !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45), 0 0 15px rgba(0, 245, 212, 0.08) !important;
    transition: transform 0.28s cubic-bezier(0.22, 1, 0.36, 1), border-color 0.28s ease, box-shadow 0.28s ease !important;
    animation: floatCard 5s ease-in-out infinite;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-7px) scale(1.025) !important;
    border-color: #00f5d4 !important;
    box-shadow: 0 12px 32px rgba(0, 245, 212, 0.28), inset 0 0 16px rgba(0, 245, 212, 0.12) !important;
}

div[data-testid="stMetricLabel"] p {
    font-family: 'JetBrains Mono', monospace !important;
    color: #8ecae6 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.5px;
}

div[data-testid="stMetricValue"] {
    font-family: 'Orbitron', sans-serif !important;
    color: #00f5d4 !important;
    text-shadow: 0 0 14px rgba(0, 245, 212, 0.45);
}

/* Botón Principal con Efecto de Energía Cibernética */
div.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #00f5d4 0%, #00bbf9 50%, #9b5de5 100%) !important;
    background-size: 200% auto !important;
    color: #040814 !important;
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: 1px !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.72rem 1.4rem !important;
    box-shadow: 0 0 22px rgba(0, 245, 212, 0.45) !important;
    transition: all 0.3s ease !important;
}

div.stButton > button[kind="primary"]:hover {
    background-position: right center !important;
    transform: translateY(-3px) scale(1.01) !important;
    box-shadow: 0 0 36px rgba(0, 245, 212, 0.85), 0 0 18px rgba(155, 93, 229, 0.75) !important;
}

/* Campos de texto y selectores con borde luminoso */
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {
    background-color: rgba(8, 15, 32, 0.82) !important;
    border: 1px solid rgba(0, 187, 249, 0.38) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(10px);
    transition: all 0.25s ease;
}

div[data-baseweb="select"] > div:hover,
div[data-baseweb="textarea"] > div:hover,
div[data-baseweb="textarea"] > div:focus-within {
    border-color: #00f5d4 !important;
    box-shadow: 0 0 18px rgba(0, 245, 212, 0.32) !important;
}

/* Bloques de código SQL y trazas Chain-of-Thought */
div[data-testid="stCodeBlock"] pre {
    background: rgba(6, 12, 28, 0.88) !important;
    border: 1px solid rgba(155, 93, 229, 0.42) !important;
    border-left: 4px solid #00f5d4 !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.4);
}

/* Pestañas (Tabs) con estilo futurista */
button[data-baseweb="tab"] {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.6px;
}
</style>
"""

st.markdown(CYBER_CSS, unsafe_allow_html=True)

# =====================================================================
# BLOQUE 3: Motor de Fondo Interactivo (HTML5 Canvas Reactivo al Mouse)
# =====================================================================
# Este script inyecta un lienzo `<canvas>` detrás de toda la aplicación
# que detecta la posición del mouse (`mousemove`) y dibuja nodos neuronales,
# líneas láser cian/violeta y ondas de energía al hacer clic.
INTERACTIVE_CANVAS_JS = """
<script>
(function() {
    const parentDoc = window.parent.document;
    const existingCanvas = parentDoc.getElementById('cyber-neural-canvas');
    if (existingCanvas) {
        return; // Ya está activo en la ventana principal
    }

    const canvas = parentDoc.createElement('canvas');
    canvas.id = 'cyber-neural-canvas';
    Object.assign(canvas.style, {
        position: 'fixed',
        top: '0',
        left: '0',
        width: '100vw',
        height: '100vh',
        zIndex: '0',
        pointerEvents: 'none',
        background: 'radial-gradient(circle at 50% 20%, #0b132b 0%, #050814 70%, #02040a 100%)'
    });
    parentDoc.body.prepend(canvas);

    const ctx = canvas.getContext('2d');
    let width = canvas.width = window.parent.innerWidth;
    let height = canvas.height = window.parent.innerHeight;

    window.parent.addEventListener('resize', () => {
        width = canvas.width = window.parent.innerWidth;
        height = canvas.height = window.parent.innerHeight;
    });

    // Estado en tiempo real del cursor del usuario y ondas expansivas al hacer clic
    const mouse = { x: width / 2, y: height / 3, active: false };
    const ripples = [];

    window.parent.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
        mouse.active = true;
    });

    window.parent.addEventListener('click', (e) => {
        ripples.push({ x: e.clientX, y: e.clientY, radius: 5, alpha: 1.0 });
    });

    const colors = ['#00f5d4', '#00bbf9', '#9b5de5', '#f15bb5'];
    const PARTICLE_COUNT = 85;
    const particles = [];

    for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * 1.15,
            vy: (Math.random() - 0.5) * 1.15,
            radius: Math.random() * 2.2 + 1.2,
            color: colors[i % colors.length]
        });
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        // Dibuja un halo holográfico alrededor del puntero del mouse
        if (mouse.active) {
            const grad = ctx.createRadialGradient(mouse.x, mouse.y, 2, mouse.x, mouse.y, 190);
            grad.addColorStop(0, 'rgba(0, 245, 212, 0.16)');
            grad.addColorStop(0.5, 'rgba(0, 187, 249, 0.06)');
            grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.arc(mouse.x, mouse.y, 190, 0, Math.PI * 2);
            ctx.fill();
        }

        // Dibuja ondas de choque al hacer clic
        for (let r = ripples.length - 1; r >= 0; r--) {
            const rip = ripples[r];
            rip.radius += 5.5;
            rip.alpha -= 0.022;
            if (rip.alpha <= 0) {
                ripples.splice(r, 1);
                continue;
            }
            ctx.beginPath();
            ctx.arc(rip.x, rip.y, rip.radius, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(0, 245, 212, ${rip.alpha})`;
            ctx.lineWidth = 2;
            ctx.stroke();
        }

        // Actualiza y conecta los nodos neuronales
        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0 || p.x > width) p.vx *= -1;
            if (p.y < 0 || p.y > height) p.vy *= -1;

            // Interacción magnética con el mouse del usuario
            if (mouse.active) {
                const dxm = mouse.x - p.x;
                const dym = mouse.y - p.y;
                const distMouse = Math.sqrt(dxm * dxm + dym * dym);

                if (distMouse < 200) {
                    // Conecta el cursor con las partículas cercanas mediante rayos láser cian
                    const alpha = (1 - distMouse / 200) * 0.75;
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.strokeStyle = `rgba(0, 245, 212, ${alpha})`;
                    ctx.lineWidth = 1.25;
                    ctx.stroke();

                    // Ligera atracción orbital hacia el mouse
                    if (distMouse > 45) {
                        p.x += (dxm / distMouse) * 0.45;
                        p.y += (dym / distMouse) * 0.45;
                    }
                }
            }

            // Dibuja el nodo brillante
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.shadowBlur = 10;
            ctx.shadowColor = p.color;
            ctx.fill();
            ctx.shadowBlur = 0;

            // Conecta nodos cercanos entre sí formando una constelación neuronal
            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 130) {
                    const lineAlpha = (1 - dist / 130) * 0.28;
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = `rgba(0, 187, 249, ${lineAlpha})`;
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }
        }

        requestAnimationFrame(animate);
    }

    animate();
})();
</script>
"""

components.html(INTERACTIVE_CANVAS_JS, height=0, width=0)

# =====================================================================
# BLOQUE 4: Encabezado HUD Futurista y Tarjetas KPI Holográficas
# =====================================================================
st.markdown(
    """
    <div class="cyber-hero">
        <div class="cyber-badge">
            <span class="pulse-dot"></span>
            NEURAL SQL ENGINE ONLINE // LANGGRAPH + GEMINI 3.8 FLASH // READ-ONLY GUARDRAIL
        </div>
        <h1 class="cyber-title">⚡ AI BUSINESS INTELLIGENCE & SQL COMMAND CENTER</h1>
        <p class="cyber-subtitle">
            Arquitectura Autónoma Text-to-SQL con Auto-Corrección (Self-Healing), Auditoría en Tiempo Real y Visualización Holográfica | <b>Joseph Pajuelo</b>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Obtiene los KPIs globales calculados en tiempo real sobre la base de datos comercial
kpis = get_global_kpis()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💰 FACTURACIÓN TOTAL", f"S/ {kpis['total_revenue_pen']:,.2f}")
c2.metric("📈 UTILIDAD NETA", f"S/ {kpis['total_profit_pen']:,.2f}")
c3.metric("🎯 MARGEN PROMEDIO", f"{kpis['avg_margin_pct']}%")
c4.metric("📦 UNIDADES VENDIDAS", f"{kpis['total_units_sold']:,}")
c5.metric("⚡ LATENCIA NEURAL SQL", f"{kpis['avg_agent_latency_ms']} ms")

st.write("")

# =====================================================================
# BLOQUE 5: Pestañas Interactivas del Centro de Comando BI
# =====================================================================
tab_analyst, tab_audit, tab_dataset = st.tabs(
    [
        "🧠 ANALISTA SQL NEURONAL (LANGGRAPH)",
        "🛡️ AUDITORÍA DE SEGURIDAD & TELEMETRÍA SQL",
        "🗄️ MATRIZ DE DATOS COMERCIAL (FACT TABLE)",
    ]
)

# PESTAÑA 1: Generador Text-to-SQL, Gráficos Cyber-Neon y Trazabilidad del Grafo
with tab_analyst:
    col_q, col_trace = st.columns([1.35, 1])

    with col_q:
        st.subheader("⚡ Terminal de Consulta Analítica en Lenguaje Natural")
        preset_q = st.selectbox(
            "Selecciona un vector de análisis ejecutivo o escribe el tuyo:",
            [
                "¿Cuáles son los ingresos, ganancia neta y margen promedio por región?",
                "¿Qué categoría de negocio genera mayor rentabilidad y margen porcentual?",
                "Muéstrame el ranking de desempeño comercial por ejecutivo de ventas (sales_rep)",
                "¿Cómo se distribuyen los ingresos y unidades por canal de venta (B2B, E-Commerce, Retail)?",
                "¿Cuál es la tendencia y evolución de ingresos por fecha?",
                "Prueba de Seguridad (Guardrail): DROP TABLE commercial_sales",
            ],
        )

        question_input = st.text_area(
            "Instrucción en lenguaje natural para el Agente BI:",
            value=preset_q,
            height=85,
        )

        if st.button(
            "⚡ COMPILAR SQL, VALIDAR GUARDRAIL Y GRAFICAR",
            type="primary",
            use_container_width=True,
        ):
            if question_input.strip():
                with st.spinner(
                    "Inspeccionando esquema DDL, compilando SQL y sintetizando KPIs..."
                ):
                    bi_state = run_bi_analyst_agent(question_input.strip())
                    st.session_state["last_bi_state"] = bi_state
                    st.rerun()

        # Renderiza el resultado de la consulta si ya se ejecutó el agente
        if "last_bi_state" in st.session_state:
            bs = st.session_state["last_bi_state"]
            st.markdown("#### 💻 Sentencia SQL Compilada y Auditada:")
            st.code(bs["generated_sql"], language="sql", wrap_lines=True)

            st.info(bs["executive_insight"])

            if bs["rows"]:
                df_res = pd.DataFrame(bs["rows"])
                cols = bs["columns"]
                # Identifica automáticamente la primera columna numérica para el eje Y del gráfico
                numeric_cols = [
                    c for c in cols if pd.api.types.is_numeric_dtype(df_res[c])
                ]
                if len(cols) >= 2 and numeric_cols:
                    x_col = cols[0]
                    y_col = numeric_cols[0]
                    neon_palette = [
                        "#00f5d4",
                        "#00bbf9",
                        "#9b5de5",
                        "#f15bb5",
                        "#fee440",
                    ]

                    if bs["chart_type"] == "pie":
                        fig = px.pie(
                            df_res,
                            names=x_col,
                            values=y_col,
                            hole=0.48,
                            color_discrete_sequence=neon_palette,
                            title=f"DISTRIBUCIÓN HOLOGRÁFICA: {y_col.upper()} POR {x_col.upper()}",
                        )
                    elif bs["chart_type"] == "line":
                        fig = px.line(
                            df_res,
                            x=x_col,
                            y=y_col,
                            markers=True,
                            color_discrete_sequence=["#00f5d4"],
                            title=f"SERIE TEMPORAL: {y_col.upper()}",
                        )
                        fig.update_traces(line=dict(width=3.5))
                    else:
                        fig = px.bar(
                            df_res,
                            x=x_col,
                            y=y_col,
                            color=x_col,
                            color_discrete_sequence=neon_palette,
                            title=f"ANÁLISIS COMPARATIVO: {y_col.upper()} POR {x_col.upper()}",
                        )

                    # Estiliza el gráfico de Plotly con fondo transparente y tipografía Cyber-Tech
                    fig.update_layout(
                        paper_bgcolor="rgba(8, 15, 32, 0.72)",
                        plot_bgcolor="rgba(8, 15, 32, 0.45)",
                        font=dict(family="Inter, sans-serif", color="#e2f1ff"),
                        title_font=dict(
                            family="Orbitron, sans-serif", size=15, color="#00f5d4"
                        ),
                        margin=dict(l=25, r=25, t=50, b=25),
                    )
                    st.plotly_chart(fig, use_container_width=True)

                st.dataframe(df_res, use_container_width=True, hide_index=True)

    with col_trace:
        st.subheader("🔍 Telemetría del Grafo Text-to-SQL")
        if "last_bi_state" in st.session_state:
            bs = st.session_state["last_bi_state"]
            st.markdown(
                f"**Estado:** `{bs['status']}` | **Auto-Healing:** `{bs['retries']} reintentos` | **Latencia:** `{bs['latency_ms']} ms`"
            )
            for step in bs.get("reasoning_steps", []):
                st.code(step, language="text", wrap_lines=True)
        else:
            st.caption(
                "Ejecuta una consulta analítica a la izquierda para observar el razonamiento paso a paso (Chain-of-Thought) del grafo."
            )

# PESTAÑA 2: Historial de Auditoría SQL y Telemetría de Seguridad
with tab_audit:
    with get_db_context() as db:
        audits = (
            db.query(SQLQueryAudit)
            .order_by(SQLQueryAudit.timestamp.desc())
            .limit(30)
            .all()
        )
        audit_rows = [
            {
                "ID": a.id,
                "Fecha UTC": a.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                if a.timestamp
                else "",
                "Estado": a.status,
                "Filas": a.rows_returned,
                "Reintentos": a.retries,
                "Latencia (ms)": a.latency_ms,
                "Pregunta": a.question,
                "SQL Ejecutado": a.generated_sql,
            }
            for a in audits
        ]
    st.subheader("🛡️ Registro de Auditoría de Consultas SQL (`sql_query_audit`)")
    st.dataframe(pd.DataFrame(audit_rows), use_container_width=True, hide_index=True)

# PESTAÑA 3: Explorador de la Tabla de Hechos Comercial
with tab_dataset:
    with get_db_context() as db:
        sales = db.query(CommercialSale).all()
        sales_rows = [
            {
                "Fecha": str(s.sale_date),
                "Región": s.region,
                "Canal": s.channel,
                "Categoría": s.category,
                "Producto / Solución": s.product_name,
                "Ejecutivo": s.sales_rep,
                "Unidades": s.units_sold,
                "Ingresos (S/)": s.revenue_pen,
                "Costo (S/)": s.cost_pen,
                "Utilidad (S/)": s.profit_pen,
                "Margen (%)": s.margin_pct,
            }
            for s in sales
        ]
    st.subheader("🗄️ Tabla de Hechos Comercial (`commercial_sales`)")
    st.dataframe(pd.DataFrame(sales_rows), use_container_width=True, hide_index=True)
