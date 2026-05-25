"""
app.py — Biorefinería Integral Urabá
Aplicación Streamlit — Modelo Híbrido SD-MILP
Universidad de Antioquia · Grupo ALIADO · 2025
"""

import warnings; warnings.filterwarnings('ignore')
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import os

# ── Configuración de página ───────────────────────────────────────────
st.set_page_config(
    page_title="Biorefinería Urabá — SD-MILP",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paleta corporativa ────────────────────────────────────────────────
V_OSC  = '#1B4D2E'; V_MED  = '#2E7D32'; V_CL   = '#66BB6A'
AMAR   = '#F9A825'; NARAN  = '#E65100'; AZUL   = '#0D47A1'
AZ_CL  = '#1976D2'; GRIS   = '#37474F'; ROJO   = '#C62828'
PURP   = '#4A148C'; TEAL   = '#006064'

# ── CSS personalizado ─────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1B4D2E 0%, #2E7D32 100%);
        padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;
        color: white; text-align: center;
    }
    .metric-card {
        background: white; border-radius: 10px; padding: 1rem;
        border-left: 5px solid; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 0.5rem;
    }
    .status-ok  { color: #2E7D32; font-weight: bold; }
    .status-err { color: #C62828; font-weight: bold; }
    [data-testid="stSidebar"] { background-color: #F1F8F1; }
</style>
""", unsafe_allow_html=True)

# ── Importar motor MILP ───────────────────────────────────────────────
try:
    from milp_core import resolver_milp, SD_DEFAULT, TECNOLOGIAS, TEC_ELEG, PRODUCTOS
    MILP_OK = True
except Exception as e:
    st.error(f"Error cargando milp_core: {e}")
    MILP_OK = False

# ── Cargar datos pre-calculados ───────────────────────────────────────
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
        except FileNotFoundError:
            dfs[nombre] = None
    return dfs

datos = cargar_datos()

# ════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Universidad_de_Antioquia_escudo.svg/200px-Universidad_de_Antioquia_escudo.svg.png",
             width=80)
    st.markdown("### 🌿 Biorefinería Urabá")
    st.markdown("**Modelo Híbrido SD-MILP**")
    st.markdown("*Grupo ALIADO — UdeA 2025*")
    st.divider()

    pagina = st.radio("📋 Navegación", [
        "🏠 Dashboard Ejecutivo",
        "⚙️ Optimizador Interactivo",
        "📊 Explorador Pareto",
        "🌱 Dinámica SD",
    ])
    st.divider()

    # Parámetros globales SD
    st.markdown("### 🔧 Parámetros SD")
    eta_slider = st.slider(
        "η cadena logística", 0.20, 0.90, 0.42, 0.01,
        help="Fracción de biomasa de campo que llega a la biorefinería"
    )
    superficie = st.number_input("Superficie cultivada (Ha)",
                                  min_value=10000, max_value=60000,
                                  value=36932, step=1000)
    q_gen = superficie * 3.4375 * 12
    q_total = q_gen * eta_slider

    st.markdown(f"""
    **Biomasa generada:** {q_gen/1e6:.2f}M Ton/año
    **Biomasa recolectada:** {q_total/1e6:.3f}M Ton/año
    """)
    st.divider()
    st.caption("Juan Carlos Gaviria Chaverra\njcarlos.gaviria@udea.edu.co")


# ════════════════════════════════════════════════════════════════════════
# PÁGINA 1 — DASHBOARD EJECUTIVO
# ════════════════════════════════════════════════════════════════════════
if pagina == "🏠 Dashboard Ejecutivo":

    st.markdown("""
    <div class='main-header'>
        <h2>🌿 BIOREFINERÍA INTEGRAL — CADENA BANANERA URABÁ</h2>
        <p>Universidad de Antioquia · Grupo ALIADO · Modelo Híbrido SD-MILP · 2025</p>
    </div>
    """, unsafe_allow_html=True)

    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌱 Biomasa generada", f"{q_gen/1e6:.2f}M Ton/año",
                  f"36,932 Ha × 3.44 Ton/Ha/mes")
    with col2:
        st.metric("🏭 Biomasa recolectada", f"{q_total/1e6:.3f}M Ton/año",
                  f"η = {eta_slider:.0%}")
    with col3:
        st.metric("📍 Región", "Urabá, Colombia",
                  "AUGURA 2024")
    with col4:
        st.metric("⚙️ Tecnologías", "10 disponibles",
                  "TRL ≥ 4, máx. 6 activas")

    st.divider()

    # Resultados óptimos por FO
    st.subheader("🎯 Resultados Óptimos por Función Objetivo")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class='metric-card' style='border-color:{V_MED}'>
        <b style='color:{V_MED}'>FO1 — UTILIDAD NETA</b><br>
        <span style='font-size:1.6rem;font-weight:bold;color:{V_MED}'>USD 356.5M/año</span><br>
        <small>Ingreso bruto: USD 436.3M/año<br>
        Tec: molienda · secado · compostaje<br>
        extraccion · hidrolisis</small>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='metric-card' style='border-color:{AZUL}'>
        <b style='color:{AZUL}'>FO2 — GEI NETO</b><br>
        <span style='font-size:1.6rem;font-weight:bold;color:{AZUL}'>-18,861 tCO₂/año</span><br>
        <small>Carbono negativo ✅<br>
        Secuestro biochar: 74,828 tCO₂<br>
        Biochar: 45,350 Ton/año</small>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class='metric-card' style='border-color:{AMAR}'>
        <b style='color:{AMAR}'>FO3 — EMPLEO</b><br>
        <span style='font-size:1.6rem;font-weight:bold;color:{AMAR}'>74,901 emp/año</span><br>
        <small>Directo: 21,400 emp/año<br>
        Indirecto (×2.5): 53,500 emp/año<br>
        Tec: molienda · fermentacion · ext</small>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class='metric-card' style='border-color:{NARAN}'>
        <b style='color:{NARAN}'>FO4 — APROVECHAMIENTO</b><br>
        <span style='font-size:1.6rem;font-weight:bold;color:{NARAN}'>42% → 100% α_BR</span><br>
        <small>α_red (campo→acopio): 42%<br>
        α_BR  (acopio→BR): 100%<br>
        Pérdida en red: 1,283,860 Ton</small>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # Solución de compromiso
    st.subheader("🏆 Solución de Compromiso Recomendada (L2)")
    col_comp, col_tec = st.columns([3, 2])

    with col_comp:
        categorias = ['FO1\nUtilidad', 'FO2\nGEI neto', 'FO3\nEmpleo', 'FO4\nAprovech.']
        valores_comp  = [0.64, 1 - 0.607, 0.69, 1.0]   # normalizados 0=peor 1=mejor
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=valores_comp + [valores_comp[0]],
            theta=categorias + [categorias[0]],
            fill='toself', fillcolor=f'rgba(46,125,50,0.2)',
            line=dict(color=V_MED, width=2),
            name='Compromiso L2'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,1])),
            showlegend=False, height=300,
            title="Perfil de la solución compromiso<br>(normalizado: 1=utópico)"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_tec:
        st.markdown(f"""
        | Métrica | Valor |
        |---------|-------|
        | **FO1 Utilidad** | USD 229.3M/año |
        | **FO2 GEI neto** | +9,948 tCO₂/año |
        | **FO3 Empleo** | 13,462 emp/año |
        | **FO4 Aprovech.** | 100% α_BR |
        | **Dist. utópico** | 0.6593 |
        | **Soluciones Pareto** | 50 |

        **Tecnologías activas:**
        molienda · secado · compostaje ·
        extraccion_solventes · pirolisis · carbonizacion
        """)

    # Flujo Sankey simplificado con Plotly
    st.divider()
    st.subheader("🔄 Flujo de Biomasa — Cadena Bananera")
    per = q_gen - q_total
    fig_sankey = go.Figure(go.Sankey(
        node=dict(
            pad=15, thickness=20,
            label=["Campo (36,932 Ha)", "Biomasa Campo", "Packing Plant",
                   "Red Logística", "Pérdida", "Biorefinería",
                   "Biochar", "Compost", "Bioenergía", "Extractos", "Fibras"],
            color=[V_MED, V_CL, AMAR, NARAN, ROJO, AZUL,
                   PURP, V_OSC, AZ_CL, TEAL, NARAN],
        ),
        link=dict(
            source=[0,0,1,2,3,3,5,5,5,5,5],
            target=[1,2,3,3,4,5,6,7,8,9,10],
            value=[q_gen*0.873/1e6, q_gen*0.127/1e6,
                   q_gen*0.873/1e6, q_gen*0.127/1e6,
                   per/1e6, q_total/1e6,
                   q_total*0.12/1e6, q_total*0.35/1e6,
                   q_total*0.30/1e6, q_total*0.08/1e6, q_total*0.15/1e6],
            color=['rgba(102,187,106,0.4)']*11,
            label=["87.3%","12.7%","","","58%","42%",
                   "12%","35%","30%","8%","15%"],
        )
    ))
    fig_sankey.update_layout(height=350, font_size=11)
    st.plotly_chart(fig_sankey, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════
# PÁGINA 2 — OPTIMIZADOR INTERACTIVO
# ════════════════════════════════════════════════════════════════════════
elif pagina == "⚙️ Optimizador Interactivo":

    st.markdown("""
    <div class='main-header'>
        <h2>⚙️ OPTIMIZADOR INTERACTIVO — MILP EN TIEMPO REAL</h2>
        <p>Ajusta los parámetros y ejecuta el modelo MILP</p>
    </div>
    """, unsafe_allow_html=True)

    col_params, col_res = st.columns([1, 2])

    with col_params:
        st.subheader("🎛️ Parámetros del modelo")

        objetivo = st.selectbox("Función objetivo a optimizar", [
            "FO1 — Maximizar Utilidad",
            "FO2 — Minimizar GEI",
            "FO3 — Maximizar Empleo",
            "FO4 — Maximizar Aprovechamiento",
            "Compromiso — Suma Ponderada",
        ])
        obj_map = {
            "FO1 — Maximizar Utilidad":      "FO1",
            "FO2 — Minimizar GEI":           "FO2",
            "FO3 — Maximizar Empleo":        "FO3",
            "FO4 — Maximizar Aprovechamiento":"FO4",
            "Compromiso — Suma Ponderada":   "compromiso",
        }
        obj_key = obj_map[objetivo]

        st.markdown("**Parámetros de mercado**")
        precio_factor = st.slider("Factor de precios de productos",
                                   0.5, 2.0, 1.0, 0.05,
                                   help="1.0 = precios base 2025")
        gei_factor = st.slider("Factor de emisiones GEI",
                                0.5, 2.0, 1.0, 0.05,
                                help="1.0 = factores literatura base")
        phi = st.slider("φ — Secuestro biochar (tCO₂/ton)",
                         0.5, 3.5, 1.65, 0.05)
        mu  = st.slider("μ — Multiplicador empleo indirecto",
                         1.0, 5.0, 2.5, 0.1)

        if obj_key == 'compromiso':
            st.markdown("**Pesos de la función compromiso**")
            w1 = st.slider("w₁ Utilidad",    0.0, 1.0, 0.25, 0.05)
            w2 = st.slider("w₂ GEI",         0.0, 1.0, 0.25, 0.05)
            w3 = st.slider("w₃ Empleo",      0.0, 1.0, 0.25, 0.05)
            w4 = st.slider("w₄ Aprovechamiento", 0.0, 1.0, 0.25, 0.05)
            w_sum = w1+w2+w3+w4
            if abs(w_sum - 1.0) > 0.05:
                st.warning(f"⚠️ Suma de pesos = {w_sum:.2f} (debe ser ~1.0)")
            w_list = [w1, w2, w3, w4]
        else:
            w_list = None

        sd_params_custom = {**SD_DEFAULT,
                            'Q_total_anual': q_total,
                            'Q_gen_anual':   q_gen,
                            'eta_cadena':    eta_slider}

        correr = st.button("🚀 Ejecutar Optimización", type="primary",
                           use_container_width=True)

    with col_res:
        if correr:
            if not MILP_OK:
                st.error("Motor MILP no disponible")
            else:
                with st.spinner(f"⏳ Resolviendo {objetivo}... (~10-25 segundos)"):
                    t0  = time.time()
                    res = resolver_milp(
                        objetivo=obj_key,
                        sd_params=sd_params_custom,
                        eta=eta_slider,
                        precio_factor=precio_factor,
                        gei_factor=gei_factor,
                        phi=phi, mu=mu,
                        w=w_list,
                    )
                    dt = time.time() - t0

                if res.get('error'):
                    st.error(f"❌ Modelo infactible con estos parámetros. "
                             f"Intenta reducir el precio mínimo o aumentar η.")
                else:
                    st.success(f"✅ Solución óptima encontrada en {dt:.1f}s")

                    # KPIs resultado
                    k1, k2, k3, k4 = st.columns(4)
                    k1.metric("💰 Utilidad neta",
                               f"USD {res['FO1']/1e6:.1f}M/año",
                               f"Ingreso: USD {res['ingreso_bruto']/1e6:.1f}M")
                    k2.metric("🌿 GEI neto",
                               f"{res['FO2']:,.0f} tCO₂/año",
                               f"Secuestro: {res['GEI_secuestro']:,.0f} tCO₂")
                    k3.metric("👷 Empleo total",
                               f"{res['emp_total']:,.0f} emp/año",
                               f"Directo: {res['emp_directo']:,.0f}")
                    k4.metric("📦 Aprovechamiento",
                               f"{res['alpha_BR']*100:.1f}% α_BR",
                               f"α_real: {res['alpha_real']*100:.1f}%")

                    # Tecnologías activas
                    st.markdown(f"""
                    **Tecnologías activas ({len(res['tec_activas'])}/{6} máx.):**
                    {' · '.join(f'`{t}`' for t in res['tec_activas'])}
                    """)

                    # Gráfico de producción por producto
                    prod_df = pd.DataFrame([
                        {'Producto': p.replace('_',' ').title(),
                         'Ton/año': v,
                         'Ingreso kUSD': v * {'extractos_bioactivos':45,'pigmentos_antocianinas':30,
                             'nanocelulosa':7.1,'bioplasticos':3.5,'biopeliculas':3.0,
                             'fibras_compuestas':2.5,'bioadhesivos':4.0,'fibras_tecnicas':0.8,
                             'bioetanol':0.65,'biogas_ch4':0.05,'biochar':0.35,
                             'compost_biofertilizante':0.15,'almidon_modificado':0.45,
                             'papel_kraft':0.55,'forraje_animal':0.30,'biocombustible':2.11,
                         }.get(p,0) * 1000 / 1e3}
                        for p, v in res['produccion'].items() if v > 0.1
                    ]).sort_values('Ingreso kUSD', ascending=False)

                    if not prod_df.empty:
                        fig_prod = px.bar(prod_df.head(10), x='Producto',
                                          y='Ingreso kUSD', color='Ingreso kUSD',
                                          color_continuous_scale='Greens',
                                          title='Top productos por ingreso (kUSD/año)')
                        fig_prod.update_layout(height=320, showlegend=False)
                        st.plotly_chart(fig_prod, use_container_width=True)

                    # Desglose empleo
                    emp_df = pd.DataFrame({
                        'Componente': ['Biorrefinería', 'Campo', 'Centros acopio'],
                        'Empleo directo': [res['emp_biorref'], res['emp_campo'], res['emp_acopio']],
                    })
                    fig_emp = px.pie(emp_df, values='Empleo directo', names='Componente',
                                     color_discrete_sequence=[V_MED, AZ_CL, AMAR],
                                     title='Distribución empleo directo')
                    fig_emp.update_layout(height=280)
                    st.plotly_chart(fig_emp, use_container_width=True)

        else:
            st.info("👈 Ajusta los parámetros y haz clic en **Ejecutar Optimización**")
            st.markdown("""
            **¿Qué puedes explorar?**
            - Cambiar η para simular mejoras logísticas
            - Aumentar precios de productos de mayor valor
            - Reducir factores GEI con tecnologías más limpias
            - Ajustar pesos del compromiso según prioridades
            - Combinar parámetros SD dinámicos con MILP
            """)


# ════════════════════════════════════════════════════════════════════════
# PÁGINA 3 — EXPLORADOR PARETO
# ════════════════════════════════════════════════════════════════════════
elif pagina == "📊 Explorador Pareto":

    st.markdown("""
    <div class='main-header'>
        <h2>📊 EXPLORADOR DE FRENTE PARETO</h2>
        <p>50 soluciones no dominadas — 3 métodos de generación</p>
    </div>
    """, unsafe_allow_html=True)

    df_p = datos.get('pareto')
    if df_p is None:
        st.warning("⚠️ Archivo `data/frente_pareto.csv` no encontrado. "
                   "Sube el CSV generado por Colab.")
        st.code("# En Colab:\nfrom google.colab import files\n"
                "files.download('/content/frente_pareto_uraba.csv')")
    else:
        # Filtros
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            fo1_range = st.slider("FO1 Utilidad (kUSD/año)",
                float(df_p['FO1_kUSD'].min()), float(df_p['FO1_kUSD'].max()),
                (float(df_p['FO1_kUSD'].min()), float(df_p['FO1_kUSD'].max())))
        with col_f2:
            fo2_range = st.slider("FO2 GEI (tCO₂/año)",
                float(df_p['FO2_tCO2'].min()), float(df_p['FO2_tCO2'].max()),
                (float(df_p['FO2_tCO2'].min()), float(df_p['FO2_tCO2'].max())))
        with col_f3:
            fo3_range = st.slider("FO3 Empleo (emp/año)",
                float(df_p['FO3_emp'].min()), float(df_p['FO3_emp'].max()),
                (float(df_p['FO3_emp'].min()), float(df_p['FO3_emp'].max())))

        mask = (
            df_p['FO1_kUSD'].between(*fo1_range) &
            df_p['FO2_tCO2'].between(*fo2_range) &
            df_p['FO3_emp'].between(*fo3_range)
        )
        df_filt = df_p[mask]
        st.caption(f"Mostrando {len(df_filt)} de {len(df_p)} soluciones")

        # Scatter FO1 vs FO2
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_p = px.scatter(df_filt, x='FO1_kUSD', y='FO2_tCO2',
                               color='FO4_pct', size='FO3_emp',
                               color_continuous_scale='RdYlGn',
                               hover_data=['metodo','tec_list','dist_utopico'],
                               title='FO1 vs FO2 — tamaño=empleo, color=aprovechamiento',
                               labels={'FO1_kUSD':'Utilidad (kUSD/año)',
                                       'FO2_tCO2':'GEI neto (tCO₂/año)'})
            fig_p.add_hline(y=0, line_dash='dash', line_color='gray',
                            annotation_text='carbono neutro')
            fig_p.update_layout(height=400)
            st.plotly_chart(fig_p, use_container_width=True)

        with col_g2:
            # Coordenadas paralelas
            cols_norm = ['FO1_norm','FO2_norm','FO3_norm','FO4_norm']
            if all(c in df_filt.columns for c in cols_norm):
                df_cp = df_filt.copy()
                for c in ['FO1_norm','FO3_norm','FO4_norm']:
                    df_cp[c] = 1 - df_cp[c]
                df_cp['FO2_norm'] = 1 - df_cp['FO2_norm']

                fig_cp = go.Figure(go.Parcoords(
                    line=dict(color=df_cp['dist_utopico'],
                              colorscale='Viridis_r', showscale=True,
                              cmin=df_cp['dist_utopico'].min(),
                              cmax=df_cp['dist_utopico'].max()),
                    dimensions=[
                        dict(label='FO1\nUtilidad', values=df_cp['FO1_norm'],
                             range=[0,1]),
                        dict(label='FO2\nGEI', values=df_cp['FO2_norm'],
                             range=[0,1]),
                        dict(label='FO3\nEmpleo', values=df_cp['FO3_norm'],
                             range=[0,1]),
                        dict(label='FO4\nAprovech.', values=df_cp['FO4_norm'],
                             range=[0,1]),
                    ]
                ))
                fig_cp.update_layout(height=400,
                    title='Coordenadas paralelas (arriba=mejor)')
                st.plotly_chart(fig_cp, use_container_width=True)

        # Tabla de soluciones
        st.subheader("📋 Soluciones filtradas")
        cols_show = ['FO1_kUSD','FO2_tCO2','FO3_emp','FO4_pct',
                     'dist_utopico','metodo','tec_list']
        cols_show = [c for c in cols_show if c in df_filt.columns]
        st.dataframe(df_filt[cols_show].round(2).reset_index(drop=True),
                     use_container_width=True)

        # Descargar CSV filtrado
        csv = df_filt.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Descargar soluciones filtradas",
                           csv, "pareto_filtrado.csv", "text/csv")


# ════════════════════════════════════════════════════════════════════════
# PÁGINA 4 — DINÁMICA SD
# ════════════════════════════════════════════════════════════════════════
elif pagina == "🌱 Dinámica SD":

    st.markdown("""
    <div class='main-header'>
        <h2>🌱 DINÁMICA DEL SISTEMA — MODELO VENSIM</h2>
        <p>Simulación SD — Diagrama_Hibrido_Uraba_v6.mdl · pysd 3.14.3</p>
    </div>
    """, unsafe_allow_html=True)

    df_sd = datos.get('sd')
    df_res = datos.get('resumen')

    if df_sd is not None:
        st.success(f"✅ Datos SD cargados: {df_sd.shape[0]} meses × "
                   f"{df_sd.shape[1]} variables")

        # Variables disponibles
        vars_num = df_sd.select_dtypes(include=[np.number]).columns.tolist()
        if 'mes' in vars_num: vars_num.remove('mes')

        col_sel, col_info = st.columns([2,1])
        with col_sel:
            vars_sel = st.multiselect("Variables a graficar",
                vars_num, default=vars_num[:3] if len(vars_num)>=3 else vars_num)
        with col_info:
            if df_res is not None:
                params = df_res.iloc[0]
                st.metric("Q_gen anual",
                          f"{params.get('Q_gen_anual_sd',0)/1e6:.2f}M Ton/año")
                st.metric("eta_cadena",
                          f"{params.get('eta_cadena_sd',0.42):.4f}")

        if vars_sel:
            meses = df_sd['mes'] if 'mes' in df_sd.columns else range(len(df_sd))
            fig_sd = go.Figure()
            colores = [V_MED, AZUL, NARAN, AMAR, ROJO, PURP, TEAL, AZ_CL]
            for i, var in enumerate(vars_sel):
                if var in df_sd.columns:
                    fig_sd.add_trace(go.Scatter(
                        x=meses, y=df_sd[var],
                        mode='lines', name=var.replace('_',' '),
                        line=dict(color=colores[i % len(colores)], width=2),
                    ))
            fig_sd.update_layout(
                title='Dinámica SD — Variables del modelo Vensim',
                xaxis_title='Tiempo (meses)',
                height=450,
                legend=dict(orientation='h', yanchor='bottom', y=1.02),
                hovermode='x unified',
            )
            st.plotly_chart(fig_sd, use_container_width=True)

        # Tabla resumen SD
        if df_res is not None:
            st.subheader("📋 Parámetros SD → MILP")
            params_show = {k:v for k,v in df_res.iloc[0].items()
                          if any(k.endswith(s) for s in ['_mean','_last','_sd'])}
            df_params = pd.DataFrame(params_show.items(),
                                     columns=['Parámetro','Valor'])
            st.dataframe(df_params.round(4), use_container_width=True)
    else:
        st.warning("⚠️ Archivo `data/datos_vensim.csv` no encontrado.")
        st.markdown("""
        **Para subir los datos SD:**
        ```python
        # En Colab, después de correr el conector:
        from google.colab import files
        files.download('/content/drive/MyDrive/Biorefineria_Uraba/datos_sd/datos_vensim.csv')
        files.download('/content/drive/MyDrive/Biorefineria_Uraba/datos_sd/resumen_sd.csv')
        ```
        Luego sube los archivos a la carpeta `data/` del repositorio GitHub.
        """)

    # Simulación SD aproximada (siempre disponible)
    st.divider()
    st.subheader("📈 Simulación SD aproximada — escenario interactivo")
    m = np.arange(0, 101)
    sup_sim = superficie * (1 + 0.0019 * m/100 * (1 - m/200))
    bio_sim = sup_sim * (q_gen/12/superficie) / 1000
    rec_sim = bio_sim * eta_slider * (1 - np.exp(-m/5))
    gei_sim = (6800 + 1700*m/100) / 1000

    fig_sim = make_subplots(specs=[[{"secondary_y": True}]])
    fig_sim.add_trace(go.Scatter(x=m, y=bio_sim, name='Generación biomasa (kTon/mes)',
                                  line=dict(color=V_MED, width=2)), secondary_y=False)
    fig_sim.add_trace(go.Scatter(x=m, y=rec_sim, name='Recolección efectiva (kTon/mes)',
                                  line=dict(color=AZUL, width=2, dash='dash')),
                      secondary_y=False)
    fig_sim.add_trace(go.Scatter(x=m, y=gei_sim, name='Emisiones GEI (kTonCO₂/mes)',
                                  line=dict(color=NARAN, width=1.5, dash='dot')),
                      secondary_y=True)
    fig_sim.update_xaxes(title_text="Tiempo (meses)")
    fig_sim.update_yaxes(title_text="Biomasa (kTon/mes)", secondary_y=False)
    fig_sim.update_yaxes(title_text="GEI (kTonCO₂/mes)", secondary_y=True)
    fig_sim.update_layout(height=380, hovermode='x unified',
                          title=f'Dinámica SD — η={eta_slider:.0%}, sup={superficie:,} Ha')
    st.plotly_chart(fig_sim, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────
st.divider()
st.markdown(f"""
<div style='text-align:center;color:{GRIS};font-size:0.8rem;'>
Datos: AUGURA 2024 · 36,932 Ha · 1.265M Ton biomasa/año · η=0.42 ·
50 soluciones Pareto · 3 métodos: suma ponderada + ε-restricción + Chebyshev<br>
<b>Universidad de Antioquia · Grupo ALIADO · 2025</b>
</div>
""", unsafe_allow_html=True)
