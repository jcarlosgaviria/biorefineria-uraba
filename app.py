"""
app_v2.py — Biorefinería Integral Urabá
Dashboard Rediseñado — Alto Impacto para Presentaciones
Universidad de Antioquia · Grupo ALIADO · 2025
Estilo: Dark Mode · Verde Selva · Dorado · Alto Contraste
"""

import warnings; warnings.filterwarnings('ignore')
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time, os

# ── Configuración ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Biorefinería Urabá · SD-MILP",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Global — Dark Mode + Alto Contraste ───────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Variables de color ── */
:root {
  --verde-oscuro:  #0A1F0E;
  --verde-base:    #1B4D2E;
  --verde-med:     #2E7D32;
  --verde-vivo:    #4CAF50;
  --verde-cl:      #A5D6A7;
  --dorado:        #FFD700;
  --dorado-cl:     #FFF176;
  --dorado-osc:    #F57F17;
  --blanco:        #F8FFF8;
  --gris-cl:       #B0BEC5;
  --gris-med:      #546E7A;
  --negro:         #060E08;
  --azul-acento:   #00BCD4;
  --rojo-acento:   #FF5252;
  --naran-acento:  #FF6D00;
}

/* ── Reset global ── */
.stApp {
  background: linear-gradient(135deg, var(--negro) 0%, var(--verde-oscuro) 50%, #0D1F10 100%) !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #060E08 0%, #0A1F0E 100%) !important;
  border-right: 1px solid var(--verde-med) !important;
}
[data-testid="stSidebar"] * { color: var(--blanco) !important; }
[data-testid="stSidebar"] .stSlider > div > div {
  background: var(--verde-med) !important;
}

/* ── Header principal ── */
.hero-header {
  background: linear-gradient(135deg, var(--verde-base) 0%, var(--negro) 100%);
  border: 1px solid var(--verde-med);
  border-left: 5px solid var(--dorado);
  border-radius: 12px;
  padding: 2rem 2.5rem;
  margin-bottom: 1.5rem;
  position: relative;
  overflow: hidden;
}
.hero-header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(255,215,0,0.08) 0%, transparent 70%);
  border-radius: 50%;
}
.hero-title {
  font-family: 'Syne', sans-serif !important;
  font-size: 2rem !important;
  font-weight: 800 !important;
  color: var(--blanco) !important;
  letter-spacing: -0.02em;
  line-height: 1.1;
  margin: 0;
}
.hero-subtitle {
  font-family: 'Space Mono', monospace !important;
  font-size: 0.75rem !important;
  color: var(--dorado) !important;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-top: 0.5rem;
}
.hero-badge {
  display: inline-block;
  background: rgba(255,215,0,0.15);
  border: 1px solid var(--dorado);
  color: var(--dorado);
  padding: 0.2rem 0.8rem;
  border-radius: 20px;
  font-family: 'Space Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 0.1em;
  margin-right: 0.5rem;
  margin-top: 0.8rem;
}

/* ── Tarjetas KPI ── */
.kpi-card {
  background: linear-gradient(135deg, rgba(27,77,46,0.4) 0%, rgba(6,14,8,0.8) 100%);
  border: 1px solid rgba(76,175,80,0.3);
  border-top: 3px solid;
  border-radius: 12px;
  padding: 1.4rem 1.2rem;
  margin-bottom: 0.5rem;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}
.kpi-card::after {
  content: '';
  position: absolute;
  bottom: 0; right: 0;
  width: 60px; height: 60px;
  border-radius: 50% 0 0 0;
  opacity: 0.06;
}
.kpi-label {
  font-family: 'Space Mono', monospace;
  font-size: 0.6rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--gris-cl);
  margin-bottom: 0.5rem;
}
.kpi-value {
  font-family: 'Syne', sans-serif;
  font-size: 1.8rem;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 0.3rem;
}
.kpi-delta {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.75rem;
  color: var(--gris-cl);
}

/* ── Sección título ── */
.section-title {
  font-family: 'Syne', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--blanco);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  border-left: 3px solid var(--dorado);
  padding-left: 0.8rem;
  margin: 1.5rem 0 1rem 0;
}

/* ── Tabla de resultados ── */
.result-table {
  background: rgba(27,77,46,0.2);
  border: 1px solid rgba(76,175,80,0.2);
  border-radius: 10px;
  padding: 1rem;
}

/* ── Texto general ── */
h1, h2, h3, h4, p, span, div {
  color: var(--blanco);
}
.stMarkdown p { color: var(--blanco) !important; }

/* ── Botones ── */
.stButton > button {
  background: linear-gradient(135deg, var(--verde-med), var(--verde-vivo)) !important;
  color: white !important;
  border: none !important;
  border-radius: 8px !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
  letter-spacing: 0.05em !important;
  padding: 0.6rem 1.5rem !important;
  transition: all 0.3s !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, var(--dorado-osc), var(--dorado)) !important;
  color: var(--negro) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(255,215,0,0.3) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
  background: rgba(27,77,46,0.4) !important;
  border: 1px solid var(--verde-med) !important;
  color: var(--blanco) !important;
  border-radius: 8px !important;
}

/* ── Slider ── */
.stSlider [data-baseweb="slider"] {
  padding: 0.5rem 0 !important;
}

/* ── Radio ── */
.stRadio > div { gap: 0.5rem !important; }
.stRadio label {
  background: rgba(27,77,46,0.3) !important;
  border: 1px solid rgba(76,175,80,0.3) !important;
  border-radius: 8px !important;
  padding: 0.4rem 0.8rem !important;
  color: var(--blanco) !important;
  transition: all 0.2s !important;
}
.stRadio label:hover {
  border-color: var(--dorado) !important;
  background: rgba(255,215,0,0.1) !important;
}

/* ── Métricas nativas ── */
[data-testid="stMetric"] {
  background: rgba(27,77,46,0.3) !important;
  border: 1px solid rgba(76,175,80,0.2) !important;
  border-radius: 10px !important;
  padding: 1rem !important;
}
[data-testid="stMetricLabel"] { color: var(--gris-cl) !important; }
[data-testid="stMetricValue"] {
  color: var(--dorado) !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 800 !important;
}
[data-testid="stMetricDelta"] { color: var(--verde-cl) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(6,14,8,0.8) !important;
  border-radius: 10px !important;
  padding: 0.3rem !important;
  gap: 0.3rem !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--gris-cl) !important;
  border-radius: 8px !important;
  font-family: 'Space Mono', monospace !important;
  font-size: 0.7rem !important;
  letter-spacing: 0.08em !important;
}
.stTabs [aria-selected="true"] {
  background: var(--verde-med) !important;
  color: white !important;
}

/* ── Divider ── */
hr { border-color: rgba(76,175,80,0.2) !important; }

/* ── Success/Warning/Error ── */
.stSuccess {
  background: rgba(46,125,50,0.2) !important;
  border: 1px solid var(--verde-med) !important;
  border-radius: 8px !important;
}
.stWarning {
  background: rgba(245,127,23,0.15) !important;
  border: 1px solid var(--dorado-osc) !important;
}
.stError {
  background: rgba(255,82,82,0.15) !important;
  border: 1px solid var(--rojo-acento) !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--dorado) !important; }

/* ── Dataframe ── */
.stDataFrame {
  background: rgba(27,77,46,0.2) !important;
  border: 1px solid rgba(76,175,80,0.2) !important;
  border-radius: 10px !important;
}

/* ── Sidebar logo área ── */
.sidebar-logo {
  text-align: center;
  padding: 1rem 0 0.5rem 0;
  border-bottom: 1px solid rgba(76,175,80,0.3);
  margin-bottom: 1rem;
}
.sidebar-logo-text {
  font-family: 'Syne', sans-serif;
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--dorado) !important;
  letter-spacing: 0.05em;
}
.sidebar-sub {
  font-family: 'Space Mono', monospace;
  font-size: 0.6rem;
  color: var(--verde-cl) !important;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

/* ── Tag de estado ── */
.tag {
  display: inline-block;
  padding: 0.15rem 0.6rem;
  border-radius: 20px;
  font-family: 'Space Mono', monospace;
  font-size: 0.6rem;
  letter-spacing: 0.08em;
  font-weight: 700;
}
.tag-green { background: rgba(76,175,80,0.2); color: #81C784; border: 1px solid #4CAF50; }
.tag-gold  { background: rgba(255,215,0,0.15); color: #FFD700; border: 1px solid #FFD700; }
.tag-blue  { background: rgba(0,188,212,0.15); color: #00BCD4; border: 1px solid #00BCD4; }
.tag-red   { background: rgba(255,82,82,0.15); color: #FF5252; border: 1px solid #FF5252; }
</style>
""", unsafe_allow_html=True)

# ── Plotly template dark personalizado ───────────────────────────────
PLOT_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor='rgba(6,14,8,0.0)',
        plot_bgcolor='rgba(10,31,14,0.4)',
        font=dict(family='DM Sans', color='#F8FFF8', size=12),
        title=dict(font=dict(family='Syne', size=16, color='#F8FFF8')),
        xaxis=dict(gridcolor='rgba(76,175,80,0.12)', linecolor='rgba(76,175,80,0.3)',
                   tickfont=dict(color='#B0BEC5')),
        yaxis=dict(gridcolor='rgba(76,175,80,0.12)', linecolor='rgba(76,175,80,0.3)',
                   tickfont=dict(color='#B0BEC5')),
        legend=dict(bgcolor='rgba(6,14,8,0.7)', bordercolor='rgba(76,175,80,0.3)',
                    borderwidth=1, font=dict(color='#F8FFF8')),
        colorway=['#4CAF50','#00BCD4','#FFD700','#FF6D00','#FF5252','#CE93D8'],
        margin=dict(l=40, r=20, t=50, b=40),
    )
)

# ── Paleta ────────────────────────────────────────────────────────────
C = {
    'verde':   '#1B4D2E', 'vmed':  '#2E7D32', 'vvivo': '#4CAF50',
    'vcl':     '#A5D6A7', 'dorado':'#FFD700', 'dosc':  '#F57F17',
    'azul':    '#00BCD4', 'rojo':  '#FF5252', 'naran': '#FF6D00',
    'purp':    '#CE93D8', 'blanco':'#F8FFF8', 'gris':  '#B0BEC5',
    'negro':   '#060E08', 'oscuro':'#0A1F0E',
}

# ── Motor MILP ────────────────────────────────────────────────────────
try:
    from milp_core import resolver_milp, SD_DEFAULT, TEC_ELEG, PRODUCTOS
    MILP_OK = True
except Exception:
    MILP_OK = False

# ── Datos pre-calculados ──────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    dfs = {}
    for nombre, ruta in [
        ('pareto',  'data/frente_pareto.csv'),
        ('sd',      'data/datos_vensim.csv'),
        ('resumen', 'data/resumen_sd.csv'),
    ]:
        try:
            dfs[nombre] = pd.read_csv(ruta)
        except Exception:
            dfs[nombre] = None
    return dfs

datos = cargar_datos()

# ── SIDEBAR ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
      <div class="sidebar-logo-text">🌿 BIOREFINERÍA</div>
      <div class="sidebar-logo-text" style="color:#4CAF50!important">URABÁ</div>
      <div class="sidebar-sub">SD-MILP · Grupo ALIADO</div>
      <div class="sidebar-sub">Universidad de Antioquia · 2025</div>
    </div>
    """, unsafe_allow_html=True)

    pagina = st.radio("", [
        "🏠  Dashboard Ejecutivo",
        "⚙️  Optimizador MILP",
        "📊  Explorador Pareto",
        "🌱  Dinámica SD",
    ], label_visibility='collapsed')

    st.markdown("---")
    st.markdown('<p style="font-family:Space Mono;font-size:0.65rem;color:#FFD700;letter-spacing:0.12em;text-transform:uppercase;">Parámetros SD</p>', unsafe_allow_html=True)

    eta = st.slider("η cadena logística", 0.20, 0.90, 0.42, 0.01,
                    help="Fracción campo→biorefinería")
    sup = st.number_input("Superficie (Ha)", 10000, 60000, 36932, 1000)

    q_gen   = sup * 3.4375 * 12
    q_total = q_gen * eta

    st.markdown(f"""
    <div style="background:rgba(27,77,46,0.3);border:1px solid rgba(76,175,80,0.3);
                border-radius:8px;padding:0.8rem;margin-top:0.5rem;">
      <div style="font-family:Space Mono;font-size:0.6rem;color:#B0BEC5;letter-spacing:0.1em;
                  text-transform:uppercase;margin-bottom:0.4rem;">Biomasa del sistema</div>
      <div style="font-family:Syne;font-size:1rem;font-weight:800;color:#FFD700;">
        {q_gen/1e6:.2f}M Ton/año</div>
      <div style="font-family:DM Sans;font-size:0.75rem;color:#A5D6A7;">
        Recolectada: {q_total/1e6:.3f}M  ·  η={eta:.0%}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p style="font-family:Space Mono;font-size:0.55rem;color:#546E7A;text-align:center;">Juan Carlos Gaviria Chaverra<br>jcarlos.gaviria@udea.edu.co</p>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# PÁGINA 1 — DASHBOARD EJECUTIVO
# ═════════════════════════════════════════════════════════════════════
if '🏠' in pagina:

    # Hero header
    st.markdown(f"""
    <div class="hero-header">
      <div class="hero-title">BIOREFINERÍA INTEGRAL<br>CADENA BANANERA URABÁ</div>
      <div class="hero-subtitle">Modelo Híbrido SD-MILP · Optimización Multiobjetivo 4D</div>
      <div style="margin-top:0.8rem;">
        <span class="hero-badge">🌿 AUGURA 2024</span>
        <span class="hero-badge">📊 50 Soluciones Pareto</span>
        <span class="hero-badge">⚙️ 10 Tecnologías TRL≥4</span>
        <span class="hero-badge">🏭 16 Productos</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs principales ──────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)

    kpis = [
        (k1, '#4CAF50', 'FO1 · UTILIDAD NETA', 'USD 356.5M', '/año', 'Ingreso bruto: USD 436.3M'),
        (k2, '#00BCD4', 'FO2 · GEI NETO', '-18,861', 'tCO₂/año', '🌿 Sistema carbono negativo'),
        (k3, '#FFD700', 'FO3 · EMPLEO TOTAL', '74,991', 'emp/año', 'Directo: 21,400 · Indirecto: 53,591'),
        (k4, '#FF6D00', 'FO4 · APROVECHAMIENTO', '42% → 100%', 'α_BR', 'η campo→BR: 0.42'),
    ]

    for col, color, label, val, unit, sub in kpis:
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-top-color:{color};">
              <div class="kpi-label">{label}</div>
              <div class="kpi-value" style="color:{color};">{val}</div>
              <div class="kpi-delta">{unit}</div>
              <div style="font-size:0.7rem;color:#546E7A;margin-top:0.4rem;">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Solución de Compromiso Recomendada — Distancia L2 al Utópico</div>',
                unsafe_allow_html=True)

    # ── Panel compromiso ──────────────────────────────────────────────
    c_left, c_right = st.columns([3, 2])

    with c_left:
        cats  = ['FO1 Utilidad', 'FO2 GEI', 'FO3 Empleo', 'FO4 Aprovech.']
        vals  = [0.64, 0.393, 0.69, 1.0]
        colors= ['#4CAF50','#00BCD4','#FFD700','#FF6D00']

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=cats + [cats[0]],
            fill='toself',
            fillcolor='rgba(76,175,80,0.15)',
            line=dict(color='#FFD700', width=3),
            marker=dict(size=8, color='#FFD700',
                        line=dict(color='#060E08', width=2)),
            name='Compromiso L2'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[1,1,1,1,1], theta=cats + [cats[0]],
            line=dict(color='rgba(76,175,80,0.3)', width=1, dash='dot'),
            fill='none', name='Utópico', showlegend=True,
        ))
        fig_radar.update_layout(
            **PLOT_TEMPLATE['layout'],
            polar=dict(
                bgcolor='rgba(10,31,14,0.6)',
                radialaxis=dict(visible=True, range=[0,1],
                                gridcolor='rgba(76,175,80,0.2)',
                                tickfont=dict(color='#546E7A', size=9)),
                angularaxis=dict(tickfont=dict(color='#F8FFF8', size=11,
                                               family='Space Mono')),
            ),
            height=320,
            title=dict(text='Perfil de Solución Compromiso', x=0.5,
                       font=dict(family='Syne', size=13, color='#F8FFF8')),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with c_right:
        st.markdown("""
        <div style="background:rgba(10,31,14,0.8);border:1px solid rgba(76,175,80,0.3);
                    border-left:4px solid #FFD700;border-radius:10px;padding:1.2rem;">
          <div style="font-family:Space Mono;font-size:0.6rem;color:#FFD700;
                      letter-spacing:0.12em;text-transform:uppercase;margin-bottom:1rem;">
            Métricas de la solución L2
          </div>
          <table style="width:100%;border-collapse:collapse;">
            <tr>
              <td style="font-family:DM Sans;font-size:0.8rem;color:#B0BEC5;padding:0.4rem 0;">FO1 Utilidad</td>
              <td style="font-family:Syne;font-size:0.9rem;font-weight:700;color:#4CAF50;
                         text-align:right;">USD 229.3M/año</td>
            </tr>
            <tr style="border-top:1px solid rgba(76,175,80,0.15);">
              <td style="font-family:DM Sans;font-size:0.8rem;color:#B0BEC5;padding:0.4rem 0;">FO2 GEI neto</td>
              <td style="font-family:Syne;font-size:0.9rem;font-weight:700;color:#00BCD4;
                         text-align:right;">+9,948 tCO₂/año</td>
            </tr>
            <tr style="border-top:1px solid rgba(76,175,80,0.15);">
              <td style="font-family:DM Sans;font-size:0.8rem;color:#B0BEC5;padding:0.4rem 0;">FO3 Empleo</td>
              <td style="font-family:Syne;font-size:0.9rem;font-weight:700;color:#FFD700;
                         text-align:right;">13,462 emp/año</td>
            </tr>
            <tr style="border-top:1px solid rgba(76,175,80,0.15);">
              <td style="font-family:DM Sans;font-size:0.8rem;color:#B0BEC5;padding:0.4rem 0;">FO4 Aprovech.</td>
              <td style="font-family:Syne;font-size:0.9rem;font-weight:700;color:#FF6D00;
                         text-align:right;">100% α_BR</td>
            </tr>
            <tr style="border-top:1px solid rgba(255,215,0,0.3);">
              <td style="font-family:DM Sans;font-size:0.8rem;color:#B0BEC5;padding:0.4rem 0;">Dist. utópico</td>
              <td style="font-family:Syne;font-size:0.9rem;font-weight:700;color:#FFD700;
                         text-align:right;">0.6593</td>
            </tr>
          </table>
          <div style="margin-top:1rem;padding-top:0.8rem;border-top:1px solid rgba(76,175,80,0.2);">
            <div style="font-family:Space Mono;font-size:0.6rem;color:#546E7A;
                        text-transform:uppercase;letter-spacing:0.1em;">Tecnologías activas</div>
            <div style="font-family:DM Sans;font-size:0.75rem;color:#A5D6A7;margin-top:0.3rem;
                        line-height:1.6;">
              molienda · secado · compostaje<br>extraccion_solventes · pirolisis · carbonizacion
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Sankey mejorado ───────────────────────────────────────────────
    st.markdown('<div class="section-title">Flujo de Biomasa — Cadena Bananera Urabá</div>',
                unsafe_allow_html=True)

    per = q_gen - q_total
    fig_sankey = go.Figure(go.Sankey(
        arrangement='snap',
        node=dict(
            pad=20, thickness=25,
            label=["Campo\n36,932 Ha", "Biomasa\nCampo", "Packing\nPlant",
                   "Red\nLogística", "Pérdida\nRed", "Biorefinería",
                   "Biochar", "Compost", "Bioenergía", "Extractos", "Fibras"],
            color=[C['vmed'], C['vvivo'], C['dosc'],
                   C['naran'], C['rojo'], C['azul'],
                   C['purp'], C['verde'], C['azul'], '#00897B', C['naran']],
            line=dict(color='rgba(6,14,8,0.8)', width=1),
        ),
        link=dict(
            source=[0,0,1,2,3,3,5,5,5,5,5],
            target=[1,2,3,3,4,5,6,7,8,9,10],
            value=[q_gen*0.873/1e6, q_gen*0.127/1e6,
                   q_gen*0.873/1e6, q_gen*0.127/1e6,
                   per/1e6, q_total/1e6,
                   q_total*0.12/1e6, q_total*0.35/1e6,
                   q_total*0.30/1e6, q_total*0.08/1e6, q_total*0.15/1e6],
            color=['rgba(76,175,80,0.35)']*5 +
                  ['rgba(0,188,212,0.35)'] +
                  ['rgba(206,147,216,0.4)','rgba(27,77,46,0.4)',
                   'rgba(0,188,212,0.4)','rgba(0,137,123,0.4)','rgba(255,109,0,0.4)'],
        )
    ))
    fig_sankey.update_layout(
        **PLOT_TEMPLATE['layout'],
        height=380,
        title=dict(text=f'Flujo biomasa · η={eta:.0%} · {q_gen/1e6:.2f}M Ton/año generada',
                   x=0.5, font=dict(family='Syne', size=14)),
    )
    st.plotly_chart(fig_sankey, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════
# PÁGINA 2 — OPTIMIZADOR MILP
# ═════════════════════════════════════════════════════════════════════
elif '⚙️' in pagina:

    st.markdown("""
    <div class="hero-header">
      <div class="hero-title">OPTIMIZADOR MILP<br>EN TIEMPO REAL</div>
      <div class="hero-subtitle">Ajusta parámetros · Ejecuta el solver · Visualiza resultados</div>
    </div>
    """, unsafe_allow_html=True)

    col_params, col_res = st.columns([1, 2], gap='large')

    with col_params:
        st.markdown('<div class="section-title">Configuración</div>', unsafe_allow_html=True)

        objetivo = st.selectbox("Función objetivo", [
            "FO1 — Maximizar Utilidad",
            "FO2 — Minimizar GEI",
            "FO3 — Maximizar Empleo",
            "FO4 — Maximizar Aprovechamiento",
            "Compromiso — Suma Ponderada",
        ])
        obj_map = {
            "FO1 — Maximizar Utilidad":       "FO1",
            "FO2 — Minimizar GEI":            "FO2",
            "FO3 — Maximizar Empleo":         "FO3",
            "FO4 — Maximizar Aprovechamiento":"FO4",
            "Compromiso — Suma Ponderada":    "compromiso",
        }
        obj_key = obj_map[objetivo]

        st.markdown('<div class="section-title">Parámetros de mercado</div>', unsafe_allow_html=True)
        precio_factor = st.slider("Factor de precios", 0.5, 2.0, 1.0, 0.05)
        gei_factor    = st.slider("Factor emisiones GEI", 0.5, 2.0, 1.0, 0.05)
        phi = st.slider("φ biochar (tCO₂/ton)", 0.5, 3.5, 1.65, 0.05)
        mu  = st.slider("μ empleo indirecto", 1.0, 5.0, 2.5, 0.1)

        w_list = None
        if obj_key == 'compromiso':
            st.markdown('<div class="section-title">Pesos compromiso</div>', unsafe_allow_html=True)
            w1 = st.slider("w₁ Utilidad",    0.0, 1.0, 0.25, 0.05)
            w2 = st.slider("w₂ GEI",         0.0, 1.0, 0.25, 0.05)
            w3 = st.slider("w₃ Empleo",      0.0, 1.0, 0.25, 0.05)
            w4 = st.slider("w₄ Aprovech.",   0.0, 1.0, 0.25, 0.05)
            w_sum = w1+w2+w3+w4
            if abs(w_sum-1.0) > 0.05:
                st.warning(f"Suma pesos = {w_sum:.2f} (ideal: 1.0)")
            w_list = [w1,w2,w3,w4]

        sd_custom = {'Q_total_anual': q_total, 'Q_gen_anual': q_gen, 'eta_cadena': eta,
                     'GEI_base': 7796.6, 'fertilidad': 0.449, 'superficie': sup}

        correr = st.button("🚀 EJECUTAR OPTIMIZACIÓN", use_container_width=True, type='primary')

    with col_res:
        if correr:
            if not MILP_OK:
                st.error("Motor MILP no disponible. Verifica milp_core.py")
            else:
                with st.spinner("⚡ Resolviendo modelo MILP..."):
                    t0  = time.time()
                    res = resolver_milp(
                        objetivo=obj_key, sd_params=sd_custom, eta=eta,
                        precio_factor=precio_factor, gei_factor=gei_factor,
                        phi=phi, mu=mu, w=w_list,
                    )
                    dt = time.time() - t0

                if res.get('error'):
                    st.error("❌ Modelo infactible. Reduce I_min o aumenta η.")
                else:
                    st.markdown(f"""
                    <div style="background:rgba(46,125,50,0.2);border:1px solid #4CAF50;
                                border-radius:8px;padding:0.6rem 1rem;margin-bottom:1rem;
                                font-family:Space Mono;font-size:0.7rem;color:#A5D6A7;">
                      ✅ Solución óptima encontrada en {dt:.1f}s
                    </div>
                    """, unsafe_allow_html=True)

                    k1,k2,k3,k4 = st.columns(4)
                    metricas = [
                        (k1,'#4CAF50','Utilidad',f"USD {res['FO1']/1e6:.1f}M/año"),
                        (k2,'#00BCD4','GEI neto',f"{res['FO2']:,.0f} tCO₂/año"),
                        (k3,'#FFD700','Empleo',f"{res['emp_total']:,.0f} emp/año"),
                        (k4,'#FF6D00','Aprovech.',f"{res['alpha_BR']*100:.1f}% α_BR"),
                    ]
                    for col,color,lbl,val in metricas:
                        with col:
                            st.markdown(f"""
                            <div class="kpi-card" style="border-top-color:{color};">
                              <div class="kpi-label">{lbl}</div>
                              <div class="kpi-value" style="color:{color};font-size:1.3rem;">{val}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    # Tecnologías activas
                    tec = res.get('tec_activas', [])
                    st.markdown(f"""
                    <div style="background:rgba(10,31,14,0.8);border:1px solid rgba(76,175,80,0.3);
                                border-radius:8px;padding:0.8rem 1rem;margin:0.5rem 0;">
                      <span style="font-family:Space Mono;font-size:0.6rem;color:#FFD700;
                                   text-transform:uppercase;letter-spacing:0.1em;">
                        Tecnologías activas ({len(tec)}/6)
                      </span><br>
                      <span style="font-family:DM Sans;font-size:0.85rem;color:#A5D6A7;">
                        {' · '.join(f'<code style="background:rgba(76,175,80,0.15);padding:0.1rem 0.4rem;border-radius:4px;color:#4CAF50">{t}</code>' for t in tec)}
                      </span>
                    </div>
                    """, unsafe_allow_html=True)

                    # Gráfico de producción
                    prod_df = pd.DataFrame([
                        {'Producto': p.replace('_',' ').title(), 'Ton/año': v}
                        for p, v in res['produccion'].items() if v > 0.1
                    ]).sort_values('Ton/año', ascending=True).tail(10)

                    if not prod_df.empty:
                        fig_prod = go.Figure(go.Bar(
                            x=prod_df['Ton/año'], y=prod_df['Producto'],
                            orientation='h',
                            marker=dict(
                                color=prod_df['Ton/año'],
                                colorscale=[[0,'#1B4D2E'],[0.5,'#4CAF50'],[1,'#FFD700']],
                                line=dict(color='rgba(6,14,8,0.5)', width=0.5)
                            ),
                            text=[f"{v:,.0f}" for v in prod_df['Ton/año']],
                            textposition='outside',
                            textfont=dict(color='#B0BEC5', size=10, family='Space Mono'),
                        ))
                        fig_prod.update_layout(
                            **PLOT_TEMPLATE['layout'],
                            height=320,
                            title=dict(text='Producción por producto (Ton/año)', x=0,
                                       font=dict(family='Syne', size=13)),
                            xaxis=dict(title='', showgrid=True),
                        )
                        st.plotly_chart(fig_prod, use_container_width=True)

                    # Empleo breakdown
                    emp_data = {
                        'Biorefinería': res.get('emp_biorref', 0),
                        'Campo': res.get('emp_campo', 0),
                        'Acopio': res.get('emp_acopio', 0),
                    }
                    fig_emp = go.Figure(go.Pie(
                        labels=list(emp_data.keys()),
                        values=list(emp_data.values()),
                        hole=0.55,
                        marker=dict(colors=['#4CAF50','#00BCD4','#FFD700'],
                                    line=dict(color='#060E08', width=2)),
                        textfont=dict(family='Space Mono', size=10, color='#F8FFF8'),
                    ))
                    fig_emp.add_annotation(
                        text=f"<b>{res['emp_total']:,.0f}</b><br>emp/año",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(family='Syne', size=13, color='#FFD700'),
                    )
                    fig_emp.update_layout(
                        **PLOT_TEMPLATE['layout'],
                        height=280,
                        title=dict(text='Distribución de empleo directo', x=0.5,
                                   font=dict(family='Syne', size=13)),
                    )
                    st.plotly_chart(fig_emp, use_container_width=True)
        else:
            st.markdown("""
            <div style="height:400px;display:flex;align-items:center;justify-content:center;
                        background:rgba(10,31,14,0.4);border:1px dashed rgba(76,175,80,0.3);
                        border-radius:12px;">
              <div style="text-align:center;">
                <div style="font-size:3rem;">⚙️</div>
                <div style="font-family:Syne;font-size:1.2rem;font-weight:700;
                            color:#4CAF50;margin:0.5rem 0;">Configura y ejecuta</div>
                <div style="font-family:DM Sans;font-size:0.85rem;color:#546E7A;">
                  Ajusta los parámetros en el panel izquierdo<br>
                  y presiona <strong style="color:#FFD700">EJECUTAR OPTIMIZACIÓN</strong>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# PÁGINA 3 — EXPLORADOR PARETO
# ═════════════════════════════════════════════════════════════════════
elif '📊' in pagina:

    st.markdown("""
    <div class="hero-header">
      <div class="hero-title">EXPLORADOR<br>FRENTE DE PARETO</div>
      <div class="hero-subtitle">50 soluciones no dominadas · 3 métodos · Espacio 4D</div>
    </div>
    """, unsafe_allow_html=True)

    df_p = datos.get('pareto')

    if df_p is None:
        st.markdown("""
        <div style="background:rgba(255,109,0,0.1);border:1px solid #FF6D00;
                    border-radius:10px;padding:1.5rem;text-align:center;">
          <div style="font-family:Syne;font-size:1rem;font-weight:700;color:#FF6D00;">
            ⚠️ Datos no encontrados
          </div>
          <div style="font-family:DM Sans;font-size:0.85rem;color:#B0BEC5;margin-top:0.5rem;">
            Sube <code>data/frente_pareto.csv</code> al repositorio GitHub
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Filtros
        st.markdown('<div class="section-title">Filtros del frente</div>', unsafe_allow_html=True)
        cf1, cf2, cf3 = st.columns(3)
        with cf1:
            r1 = st.slider("FO1 Utilidad (kUSD)",
                float(df_p['FO1_kUSD'].min()), float(df_p['FO1_kUSD'].max()),
                (float(df_p['FO1_kUSD'].min()), float(df_p['FO1_kUSD'].max())))
        with cf2:
            r2 = st.slider("FO2 GEI (tCO₂/año)",
                float(df_p['FO2_tCO2'].min()), float(df_p['FO2_tCO2'].max()),
                (float(df_p['FO2_tCO2'].min()), float(df_p['FO2_tCO2'].max())))
        with cf3:
            r3 = st.slider("FO3 Empleo (emp/año)",
                float(df_p['FO3_emp'].min()), float(df_p['FO3_emp'].max()),
                (float(df_p['FO3_emp'].min()), float(df_p['FO3_emp'].max())))

        mask  = (df_p['FO1_kUSD'].between(*r1) &
                 df_p['FO2_tCO2'].between(*r2) &
                 df_p['FO3_emp'].between(*r3))
        df_f  = df_p[mask]

        st.markdown(f"""
        <div style="font-family:Space Mono;font-size:0.65rem;color:#B0BEC5;
                    letter-spacing:0.1em;margin-bottom:1rem;">
          Mostrando <span style="color:#FFD700;font-weight:700;">{len(df_f)}</span>
          de {len(df_p)} soluciones no dominadas
        </div>
        """, unsafe_allow_html=True)

        g1, g2 = st.columns(2)

        with g1:
            # Scatter FO1 vs FO2 mejorado
            fig_sc = go.Figure()

            # Línea carbono neutro
            fig_sc.add_hline(y=0, line_dash='dash',
                             line_color='rgba(255,82,82,0.4)',
                             annotation_text='Carbono neutro',
                             annotation_font=dict(color='#FF5252', size=9))

            if 'metodo' in df_f.columns:
                for met, col_met, sym in [
                    ('suma_ponderada', '#4CAF50', 'circle'),
                    ('chebyshev',      '#00BCD4', 'square'),
                    ('eps_FO1',        '#FFD700', 'triangle-up'),
                    ('eps_FO2',        '#FF6D00', 'triangle-down'),
                    ('eps_FO3',        '#CE93D8', 'diamond'),
                ]:
                    sub = df_f[df_f['metodo']==met]
                    if len(sub):
                        fig_sc.add_trace(go.Scatter(
                            x=sub['FO1_kUSD'], y=sub['FO2_tCO2'],
                            mode='markers',
                            marker=dict(size=10, color=col_met, symbol=sym,
                                        line=dict(color='#060E08', width=1),
                                        opacity=0.85),
                            name=met.replace('_',' '),
                            hovertemplate=
                                '<b>FO1:</b> %{x:,.0f} kUSD<br>'
                                '<b>FO2:</b> %{y:,.0f} tCO₂<extra></extra>'
                        ))
            else:
                fig_sc.add_trace(go.Scatter(
                    x=df_f['FO1_kUSD'], y=df_f['FO2_tCO2'],
                    mode='markers',
                    marker=dict(size=10, color='#4CAF50',
                                colorscale='Viridis', showscale=False,
                                line=dict(color='#060E08', width=1)),
                ))

            fig_sc.update_layout(
                **PLOT_TEMPLATE['layout'],
                height=380,
                title=dict(text='FO1 vs FO2 — Frente de Pareto', x=0.5,
                           font=dict(family='Syne', size=14)),
                xaxis=dict(title='Utilidad Neta (kUSD/año)'),
                yaxis=dict(title='GEI neto (tCO₂/año)'),
            )
            st.plotly_chart(fig_sc, use_container_width=True)

        with g2:
            # Coordenadas paralelas mejoradas
            cols_norm = ['FO1_norm','FO2_norm','FO3_norm','FO4_norm']
            if all(c in df_f.columns for c in cols_norm):
                df_cp = df_f.copy()
                for c in ['FO1_norm','FO3_norm','FO4_norm']:
                    df_cp[c] = 1 - df_cp[c]
                df_cp['FO2_norm'] = 1 - df_cp['FO2_norm']

                dist_col = df_f['dist_utopico'] if 'dist_utopico' in df_f.columns \
                           else pd.Series([0.5]*len(df_f))

                fig_cp = go.Figure(go.Parcoords(
                    line=dict(
                        color=dist_col,
                        colorscale=[[0,'#FFD700'],[0.5,'#4CAF50'],[1,'#1B4D2E']],
                        showscale=True,
                        cmin=float(dist_col.min()),
                        cmax=float(dist_col.max()),
                        colorbar=dict(
                            title=dict(text='Dist.\n utópico', font=dict(color='#B0BEC5', size=9)),
                            tickfont=dict(color='#B0BEC5', size=8),
                            thickness=10, len=0.7,
                        )
                    ),
                    dimensions=[
                        dict(label='FO1\nUtilidad', values=df_cp['FO1_norm'], range=[0,1]),
                        dict(label='FO2\nGEI', values=df_cp['FO2_norm'], range=[0,1]),
                        dict(label='FO3\nEmpleo', values=df_cp['FO3_norm'], range=[0,1]),
                        dict(label='FO4\nAprovech.', values=df_cp['FO4_norm'], range=[0,1]),
                    ],
                    labelangle=0,
                    labelside='top',
                    labelfont=dict(color='#F8FFF8', size=11, family='Space Mono'),
                    tickfont=dict(color='#546E7A', size=8),
                    rangefont=dict(color='#546E7A', size=8),
                ))
                fig_cp.update_layout(
                    **PLOT_TEMPLATE['layout'],
                    height=380,
                    title=dict(text='Coordenadas Paralelas (arriba=mejor)', x=0.5,
                               font=dict(family='Syne', size=14)),
                )
                st.plotly_chart(fig_cp, use_container_width=True)

        # Tabla
        st.markdown('<div class="section-title">Tabla de soluciones filtradas</div>',
                    unsafe_allow_html=True)
        cols_show = [c for c in ['FO1_kUSD','FO2_tCO2','FO3_emp','FO4_pct',
                                  'dist_utopico','metodo'] if c in df_f.columns]
        st.dataframe(
            df_f[cols_show].round(2).reset_index(drop=True),
            use_container_width=True, height=220
        )

        csv = df_f.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Descargar CSV filtrado", csv,
                          "pareto_filtrado.csv", "text/csv")


# ═════════════════════════════════════════════════════════════════════
# PÁGINA 4 — DINÁMICA SD
# ═════════════════════════════════════════════════════════════════════
elif '🌱' in pagina:

    st.markdown("""
    <div class="hero-header">
      <div class="hero-title">DINÁMICA DEL SISTEMA<br>MODELO VENSIM</div>
      <div class="hero-subtitle">Diagrama_Hibrido_Uraba_v6.mdl · pysd 3.14.3 · 62 variables · 100 meses</div>
    </div>
    """, unsafe_allow_html=True)

    df_sd  = datos.get('sd')
    df_res = datos.get('resumen')

    if df_sd is not None:
        st.markdown(f"""
        <div style="font-family:Space Mono;font-size:0.65rem;color:#4CAF50;
                    letter-spacing:0.1em;margin-bottom:1rem;">
          ✅ Datos SD cargados · {df_sd.shape[0]} meses × {df_sd.shape[1]} variables
        </div>
        """, unsafe_allow_html=True)

        vars_num = [c for c in df_sd.select_dtypes(include=[np.number]).columns if c != 'mes']
        vars_sel = st.multiselect("Variables a graficar", vars_num,
                                  default=vars_num[:3] if len(vars_num) >= 3 else vars_num)

        if vars_sel:
            meses  = df_sd['mes'] if 'mes' in df_sd.columns else range(len(df_sd))
            colors = ['#4CAF50','#00BCD4','#FFD700','#FF6D00','#FF5252','#CE93D8','#80CBC4']
            fig_sd = go.Figure()
            for i, var in enumerate(vars_sel):
                if var in df_sd.columns:
                    fig_sd.add_trace(go.Scatter(
                        x=meses, y=df_sd[var],
                        mode='lines',
                        name=var.replace('_',' '),
                        line=dict(color=colors[i % len(colors)], width=2.5),
                        fill='tozeroy' if i == 0 else 'none',
                        fillcolor='rgba(76,175,80,0.05)' if i == 0 else None,
                    ))
            fig_sd.update_layout(
                **PLOT_TEMPLATE['layout'],
                height=420,
                title=dict(text='Variables del modelo SD (Vensim)', x=0.5,
                           font=dict(family='Syne', size=15)),
                xaxis=dict(title='Tiempo (meses)'),
                hovermode='x unified',
            )
            st.plotly_chart(fig_sd, use_container_width=True)

    # ── Simulación aproximada interactiva ─────────────────────────────
    st.markdown('<div class="section-title">Simulación SD Interactiva — Escenario Actual</div>',
                unsafe_allow_html=True)

    m      = np.arange(0, 101)
    sup_d  = sup * (1 + 0.0019 * m/100 * (1 - m/200))
    bio_d  = sup_d * (q_gen/12/sup) / 1000
    rec_d  = bio_d * eta * (1 - np.exp(-m/5))
    gei_d  = (6800 + 1700*m/100) / 1000
    fert_d = 0.449 - 0.04*(1 - np.exp(-m/40))

    fig_sim = make_subplots(specs=[[{"secondary_y": True}]])
    fig_sim.add_trace(go.Scatter(
        x=m, y=bio_d, name='Generación biomasa (kTon/mes)',
        line=dict(color='#4CAF50', width=3),
        fill='tozeroy', fillcolor='rgba(76,175,80,0.08)',
    ), secondary_y=False)
    fig_sim.add_trace(go.Scatter(
        x=m, y=rec_d, name='Recolección efectiva (kTon/mes)',
        line=dict(color='#00BCD4', width=2.5, dash='dash'),
    ), secondary_y=False)
    fig_sim.add_trace(go.Scatter(
        x=m, y=gei_d, name='Emisiones GEI (kTonCO₂/mes)',
        line=dict(color='#FF5252', width=2, dash='dot'),
    ), secondary_y=True)
    fig_sim.add_trace(go.Scatter(
        x=m, y=fert_d*100, name='Fertilidad (%) × 100',
        line=dict(color='#FFD700', width=2, dash='dashdot'),
    ), secondary_y=True)

    # Área de biomasa no valorizada
    fig_sim.add_trace(go.Scatter(
        x=np.concatenate([m, m[::-1]]),
        y=np.concatenate([bio_d, rec_d[::-1]]),
        fill='toself', fillcolor='rgba(255,82,82,0.06)',
        line=dict(color='rgba(0,0,0,0)', width=0),
        name='Biomasa no valorizada', showlegend=True,
    ), secondary_y=False)

    fig_sim.update_layout(
        **PLOT_TEMPLATE['layout'],
        height=420,
        title=dict(text=f'Dinámica SD — η={eta:.0%} · Superficie={sup:,} Ha',
                   x=0.5, font=dict(family='Syne', size=15)),
        hovermode='x unified',
    )
    fig_sim.update_xaxes(title_text="Tiempo (meses)")
    fig_sim.update_yaxes(title_text="Biomasa (kTon/mes)", secondary_y=False)
    fig_sim.update_yaxes(title_text="GEI + Fertilidad", secondary_y=True)
    st.plotly_chart(fig_sim, use_container_width=True)

    # Parámetros SD del resumen
    if df_res is not None:
        st.markdown('<div class="section-title">Parámetros SD → MILP</div>',
                    unsafe_allow_html=True)
        params = df_res.iloc[0]
        p1, p2, p3, p4 = st.columns(4)
        for col, key, lbl, color in [
            (p1, 'Q_gen_anual_sd',    'Q_gen anual',  '#4CAF50'),
            (p2, 'Q_total_anual_sd',  'Q_total anual','#00BCD4'),
            (p3, 'eta_cadena_sd',     'eta cadena',   '#FFD700'),
            (p4, 'GEI_base_sd',       'GEI base/mes', '#FF5252'),
        ]:
            val = params.get(key, 0)
            fmt = f"{val/1e6:.2f}M" if val > 100000 else f"{val:,.4f}" if val < 10 else f"{val:,.1f}"
            with col:
                st.markdown(f"""
                <div class="kpi-card" style="border-top-color:{color};">
                  <div class="kpi-label">{lbl}</div>
                  <div class="kpi-value" style="color:{color};font-size:1.2rem;">{fmt}</div>
                </div>
                """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding:1rem;
            border-top:1px solid rgba(76,175,80,0.2);
            text-align:center;">
  <span style="font-family:Space Mono;font-size:0.6rem;color:#546E7A;letter-spacing:0.1em;">
    BIOREFINERÍA INTEGRAL URABÁ · SD-MILP · GRUPO ALIADO · UNIVERSIDAD DE ANTIOQUIA · 2025
    · <span style="color:#4CAF50;">36,932 Ha</span>
    · <span style="color:#FFD700;">1.265M Ton/año</span>
    · <span style="color:#00BCD4;">50 soluciones Pareto</span>
  </span>
</div>
""", unsafe_allow_html=True)
