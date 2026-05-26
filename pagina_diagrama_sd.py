"""
pagina_diagrama_sd.py
═══════════════════════════════════════════════════════════════════
MÓDULO: Página "🔬 Diagrama SD" para app_v2.py
Biorefinería Integral Urabá — Grupo ALIADO — UdeA 2025

INSTRUCCIONES DE INTEGRACIÓN:
1. Copiar este bloque completo en app_v2.py
2. Agregar la opción al radio del sidebar:
   pagina = st.radio("", [
       "🏠  Dashboard Ejecutivo",
       "⚙️  Optimizador MILP",
       "📊  Explorador Pareto",
       "🌱  Dinámica SD",
       "🔬  Diagrama SD",   ← AGREGAR ESTA LÍNEA
   ], ...)
3. El elif al final del archivo queda:
   elif '🔬' in pagina:
       [pegar aquí el contenido de esta página]

DEPENDENCIAS:
   - plotly (ya instalado)
   - datos_vensim.csv en data/ (ya existe)
   - Imagen PNG del diagrama Vensim en assets/diagrama_vensim.png
     (exportar desde Vensim: File → Print → Save as Image)
═══════════════════════════════════════════════════════════════════
"""

# ══════════════════════════════════════════════════════════════════════
# DATOS DEL DIAGRAMA CAUSAL SD
# Variables, conexiones y bucles extraídos de
# Diagrama_Hibrido_Uraba_v6.mdl (confirmado con pysd 3.14.3)
# ══════════════════════════════════════════════════════════════════════

# Posiciones (x, y) de cada nodo en el diagrama — layout tipo Vensim
# Coordenadas en [0,1] para escalar al viewport
NODOS_SD = {
    # ── Capa agrícola (arriba) ────────────────────────────────────────
    'Superficie\nCultivada':         (0.10, 0.85),
    'Tasa de\nExpansión':            (0.22, 0.92),
    'Generacion de\nBiomasa':        (0.35, 0.85),
    'Biomasa\nHojas':                (0.50, 0.92),
    'Biomasa\nCormo':                (0.60, 0.92),
    'Biomasa\nRaquis':               (0.70, 0.92),
    'Biomasa\nCampo Total':          (0.55, 0.78),
    # ── Capa logística (medio) ────────────────────────────────────────
    'eta cadena':                    (0.35, 0.62),
    'Tasa de Recoleccion\nEfectiva': (0.50, 0.62),
    'Tasa de\nRecoleccion':          (0.38, 0.70),
    'Perdida\nRed':                  (0.28, 0.55),
    'Costo\nLogistico Red':          (0.20, 0.62),
    # ── Capa biorefinería (centro) ────────────────────────────────────
    'Biomasa\nBiorefineria':         (0.65, 0.62),
    'Utilidad\nNeta':                (0.80, 0.70),
    'Ingreso\nBruto':                (0.85, 0.80),
    'Costo\nOperativo':              (0.85, 0.60),
    # ── Capa ambiental (abajo-derecha) ───────────────────────────────
    'Emisiones\nTotales GEI':        (0.72, 0.45),
    'Biochar\nProducido':            (0.82, 0.38),
    'GEI\nSecuestrado':              (0.72, 0.30),
    'GEI\nNeto':                     (0.60, 0.38),
    # ── Capa suelo (abajo-izquierda) ─────────────────────────────────
    'Fertilidad\ndel Suelo':         (0.22, 0.38),
    'Residuos\nen Campo':            (0.12, 0.50),
    'Rendimiento\nAgricola':         (0.10, 0.70),
    # ── Retroalimentación (inversión) ────────────────────────────────
    'Inversion\nExpansion':          (0.80, 0.52),
}

# Conexiones: (origen, destino, signo, bucle)
# signo: '+' = refuerzo, '-' = balance
# bucle: 'R1','R2','B1','B2','N' (ninguno específico)
CONEXIONES_SD = [
    # ── Bucle R1: Expansión agrícola (refuerzo) ───────────────────────
    ('Superficie\nCultivada',         'Generacion de\nBiomasa',        '+', 'R1'),
    ('Generacion de\nBiomasa',        'Biomasa\nCampo Total',           '+', 'R1'),
    ('Biomasa\nCampo Total',          'Tasa de Recoleccion\nEfectiva',  '+', 'R1'),
    ('Tasa de Recoleccion\nEfectiva', 'Biomasa\nBiorefineria',          '+', 'R1'),
    ('Biomasa\nBiorefineria',         'Utilidad\nNeta',                 '+', 'R1'),
    ('Utilidad\nNeta',                'Inversion\nExpansion',           '+', 'R1'),
    ('Inversion\nExpansion',          'Superficie\nCultivada',          '+', 'R1'),
    ('Superficie\nCultivada',         'Tasa de\nExpansión',             '+', 'R1'),
    ('Tasa de\nExpansión',            'Superficie\nCultivada',          '+', 'R1'),

    # ── Bucle R2: Biochar-Fertilidad (refuerzo) ───────────────────────
    ('Biomasa\nBiorefineria',         'Biochar\nProducido',             '+', 'R2'),
    ('Biochar\nProducido',            'GEI\nSecuestrado',               '+', 'R2'),
    ('Biochar\nProducido',            'Fertilidad\ndel Suelo',          '+', 'R2'),
    ('Fertilidad\ndel Suelo',         'Rendimiento\nAgricola',          '+', 'R2'),
    ('Rendimiento\nAgricola',         'Generacion de\nBiomasa',         '+', 'R2'),

    # ── Bucle B1: Restricción GEI (balance) ───────────────────────────
    ('Biomasa\nBiorefineria',         'Emisiones\nTotales GEI',         '+', 'B1'),
    ('GEI\nSecuestrado',              'GEI\nNeto',                      '-', 'B1'),
    ('Emisiones\nTotales GEI',        'GEI\nNeto',                      '+', 'B1'),
    ('GEI\nNeto',                     'Inversion\nExpansion',           '-', 'B1'),

    # ── Bucle B2: Pérdidas logísticas (balance) ───────────────────────
    ('eta cadena',                    'Tasa de Recoleccion\nEfectiva',  '+', 'B2'),
    ('Tasa de Recoleccion\nEfectiva', 'Perdida\nRed',                   '-', 'B2'),
    ('Perdida\nRed',                  'Costo\nLogistico Red',            '+', 'B2'),
    ('Costo\nLogistico Red',          'Utilidad\nNeta',                  '-', 'B2'),
    ('Tasa de\nRecoleccion',          'Tasa de Recoleccion\nEfectiva',  '+', 'B2'),

    # ── Conexiones auxiliares (sin bucle específico) ──────────────────
    ('Generacion de\nBiomasa',        'Biomasa\nHojas',                 '+', 'N'),
    ('Generacion de\nBiomasa',        'Biomasa\nCormo',                 '+', 'N'),
    ('Generacion de\nBiomasa',        'Biomasa\nRaquis',                '+', 'N'),
    ('Biomasa\nHojas',                'Biomasa\nCampo Total',            '+', 'N'),
    ('Biomasa\nCormo',                'Biomasa\nCampo Total',            '+', 'N'),
    ('Biomasa\nRaquis',               'Biomasa\nCampo Total',            '+', 'N'),
    ('Residuos\nen Campo',            'Fertilidad\ndel Suelo',           '+', 'N'),
    ('Biomasa\nCampo Total',          'Residuos\nen Campo',              '+', 'N'),
    ('Biomasa\nBiorefineria',         'Ingreso\nBruto',                  '+', 'N'),
    ('Ingreso\nBruto',                'Utilidad\nNeta',                  '+', 'N'),
    ('Costo\nOperativo',              'Utilidad\nNeta',                  '-', 'N'),
]

# Colores por bucle
COLORES_BUCLE = {
    'R1': '#4CAF50',   # verde — refuerzo expansión
    'R2': '#FFD700',   # dorado — refuerzo biochar
    'B1': '#FF5252',   # rojo — balance GEI
    'B2': '#00BCD4',   # azul — balance logística
    'N':  '#546E7A',   # gris — auxiliar
}

# Color de nodos por categoría
COLORES_NODO = {
    'Superficie\nCultivada':         '#2E7D32',
    'Tasa de\nExpansión':            '#388E3C',
    'Generacion de\nBiomasa':        '#43A047',
    'Biomasa\nHojas':                '#1B5E20',
    'Biomasa\nCormo':                '#1B5E20',
    'Biomasa\nRaquis':               '#1B5E20',
    'Biomasa\nCampo Total':          '#2E7D32',
    'eta cadena':                    '#00838F',
    'Tasa de Recoleccion\nEfectiva': '#00ACC1',
    'Tasa de\nRecoleccion':          '#00ACC1',
    'Perdida\nRed':                  '#C62828',
    'Costo\nLogistico Red':          '#E53935',
    'Biomasa\nBiorefineria':         '#0277BD',
    'Utilidad\nNeta':                '#1565C0',
    'Ingreso\nBruto':                '#1976D2',
    'Costo\nOperativo':              '#C62828',
    'Emisiones\nTotales GEI':        '#BF360C',
    'Biochar\nProducido':            '#6A1B9A',
    'GEI\nSecuestrado':              '#7B1FA2',
    'GEI\nNeto':                     '#E53935',
    'Fertilidad\ndel Suelo':         '#558B2F',
    'Residuos\nen Campo':            '#827717',
    'Rendimiento\nAgricola':         '#33691E',
    'Inversion\nExpansion':          '#E65100',
}


def construir_diagrama_causal(bucles_visibles=None, datos_sd=None):
    """
    Construye el diagrama causal interactivo del modelo SD.

    Parámetros
    ----------
    bucles_visibles : list — subset de ['R1','R2','B1','B2','N'] a mostrar
    datos_sd        : dict — valores actuales de variables (para hover)
    """
    import plotly.graph_objects as go
    import numpy as np

    if bucles_visibles is None:
        bucles_visibles = ['R1', 'R2', 'B1', 'B2', 'N']

    # ── Valores de variables para hover (desde SD real si disponible)
    valores_sd = {
        'Superficie\nCultivada':         '36,932 Ha',
        'Generacion de\nBiomasa':        '104,635 Ton/mes',
        'Biomasa\nCampo Total':          '97,800 Ton/mes',
        'eta cadena':                    '0.4200',
        'Tasa de Recoleccion\nEfectiva': '80,782 Ton/mes',
        'Perdida\nRed':                  '28,978 Ton/mes',
        'Biomasa\nBiorefineria':         '929,692 Ton/año',
        'Utilidad\nNeta':                'USD 229.3M/año (L2)',
        'Emisiones\nTotales GEI':        '7,797 tCO₂/mes',
        'Biochar\nProducido':            '45,350 Ton/año',
        'GEI\nSecuestrado':              '74,828 tCO₂/año',
        'GEI\nNeto':                     '-18,861 tCO₂/año',
        'Fertilidad\ndel Suelo':         '0.449',
        'Biomasa\nHojas':                '11,743 Ton/mes',
        'Biomasa\nCormo':                '5,872 Ton/mes',
        'Biomasa\nRaquis':               '2,642 Ton/mes',
    }
    if datos_sd:
        valores_sd.update(datos_sd)

    fig = go.Figure()

    # ── 1. Dibujar flechas de conexión ────────────────────────────────
    for origen, destino, signo, bucle in CONEXIONES_SD:
        if bucle not in bucles_visibles:
            continue
        if origen not in NODOS_SD or destino not in NODOS_SD:
            continue

        x0, y0 = NODOS_SD[origen]
        x1, y1 = NODOS_SD[destino]
        color   = COLORES_BUCLE[bucle]
        ancho   = 2.5 if bucle != 'N' else 1.2
        opac    = 0.85 if bucle != 'N' else 0.35

        # Calcular punto de control para curva suave
        dx = x1 - x0
        dy = y1 - y0
        # Offset perpendicular ligero para evitar superposición
        perp_x = -dy * 0.08
        perp_y =  dx * 0.08
        xm = (x0 + x1)/2 + perp_x
        ym = (y0 + y1)/2 + perp_y

        # Curva bezier cuadrática con 20 puntos
        t   = np.linspace(0, 1, 20)
        cx  = (1-t)**2 * x0 + 2*(1-t)*t * xm + t**2 * x1
        cy  = (1-t)**2 * y0 + 2*(1-t)*t * ym + t**2 * y1

        fig.add_trace(go.Scatter(
            x=cx, y=cy,
            mode='lines',
            line=dict(color=f'rgba({int(color[1:3],16)},'
                              f'{int(color[3:5],16)},'
                              f'{int(color[5:7],16)},{opac})',
                      width=ancho),
            hoverinfo='skip',
            showlegend=False,
        ))

        # Punta de flecha (triángulo pequeño en el destino)
        dx_tip = cx[-1] - cx[-3]
        dy_tip = cy[-1] - cy[-3]
        norm   = max((dx_tip**2 + dy_tip**2)**0.5, 1e-9)
        ax     = x1 - dx_tip/norm * 0.025
        ay     = y1 - dy_tip/norm * 0.025

        fig.add_annotation(
            x=x1, y=y1,
            ax=ax, ay=ay,
            xref='x', yref='y', axref='x', ayref='y',
            showarrow=True,
            arrowhead=2, arrowsize=1.2, arrowwidth=ancho,
            arrowcolor=color,
            opacity=opac,
        )

        # Signo +/- en el punto medio de la flecha
        if bucle != 'N':
            color_signo = '#4CAF50' if signo == '+' else '#FF5252'
            fig.add_annotation(
                x=xm, y=ym,
                text=f'<b>{signo}</b>',
                showarrow=False,
                font=dict(size=11, color=color_signo, family='Space Mono'),
                bgcolor='rgba(6,14,8,0.7)',
                bordercolor=color_signo,
                borderwidth=1,
                borderpad=2,
            )

    # ── 2. Dibujar nodos ─────────────────────────────────────────────
    nodos_x, nodos_y, nodos_txt, nodos_color, nodos_hover = [], [], [], [], []
    for nombre, (x, y) in NODOS_SD.items():
        nodos_x.append(x)
        nodos_y.append(y)
        nodos_txt.append(nombre.replace('\n', '<br>'))
        nodos_color.append(COLORES_NODO.get(nombre, '#37474F'))
        val = valores_sd.get(nombre, 'N/D')
        nodos_hover.append(
            f'<b>{nombre.replace(chr(10)," ")}</b><br>'
            f'<span style="color:#FFD700">Valor SD: {val}</span>'
        )

    fig.add_trace(go.Scatter(
        x=nodos_x, y=nodos_y,
        mode='markers+text',
        marker=dict(
            size=38,
            color=nodos_color,
            line=dict(color='rgba(255,215,0,0.6)', width=1.5),
            symbol='circle',
        ),
        text=nodos_txt,
        textposition='middle center',
        textfont=dict(size=8, color='white', family='DM Sans'),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=nodos_hover,
        showlegend=False,
    ))

    # ── 3. Etiquetas de bucles (leyenda visual en el diagrama) ────────
    bucles_info = [
        (0.02, 0.15, 'R1', '⟳ Expansión agrícola', '#4CAF50'),
        (0.02, 0.10, 'R2', '⟳ Biochar-Fertilidad', '#FFD700'),
        (0.02, 0.05, 'B1', '⟲ Restricción GEI',    '#FF5252'),
        (0.35, 0.05, 'B2', '⟲ Pérdidas logísticas','#00BCD4'),
    ]
    for xb, yb, clave, lbl, col in bucles_info:
        if clave in bucles_visibles:
            fig.add_annotation(
                x=xb, y=yb, xref='paper', yref='paper',
                text=f'<b style="color:{col}">{lbl}</b>',
                showarrow=False,
                font=dict(size=10, color=col, family='Space Mono'),
                bgcolor='rgba(6,14,8,0.8)',
                bordercolor=col, borderwidth=1, borderpad=4,
                align='left',
            )

    # ── Layout ────────────────────────────────────────────────────────
    fig.update_layout(
        paper_bgcolor='rgba(6,14,8,0.0)',
        plot_bgcolor='rgba(10,31,14,0.5)',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   range=[-0.05, 1.05]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   range=[-0.05, 1.08]),
        height=620,
        margin=dict(l=10, r=10, t=50, b=80),
        title=dict(
            text='Diagrama Causal — Modelo SD Biorefinería Urabá<br>'
                 '<sup style="color:#B0BEC5">Diagrama_Hibrido_Uraba_v6.mdl · '
                 'Variables confirmadas con pysd 3.14.3</sup>',
            x=0.5, font=dict(family='Syne', size=16, color='#F8FFF8'),
        ),
        hoverlabel=dict(
            bgcolor='#0A1F0E', bordercolor='#4CAF50',
            font=dict(family='DM Sans', size=12, color='#F8FFF8'),
        ),
        hovermode='closest',
    )

    return fig


# ══════════════════════════════════════════════════════════════════════
# CONTENIDO DE LA PÁGINA — pegar en app_v2.py dentro del elif '🔬'
# ══════════════════════════════════════════════════════════════════════

PAGE_DIAGRAMA_SD = '''
# ═════════════════════════════════════════════════════════════════════
# PÁGINA 5 — DIAGRAMA SD
# ═════════════════════════════════════════════════════════════════════
elif "🔬" in pagina:

    st.markdown("""
    <div class="hero-header">
      <div class="hero-title">DIAGRAMA CAUSAL<br>MODELO VENSIM SD</div>
      <div class="hero-subtitle">
        Diagrama_Hibrido_Uraba_v6.mdl · 62 variables · 4 bucles de retroalimentación
      </div>
      <div style="margin-top:0.8rem;">
        <span class="hero-badge" style="border-color:#4CAF50;color:#4CAF50;">
          ⟳ R1 Expansión agrícola</span>
        <span class="hero-badge" style="border-color:#FFD700;color:#FFD700;">
          ⟳ R2 Biochar-Fertilidad</span>
        <span class="hero-badge" style="border-color:#FF5252;color:#FF5252;">
          ⟲ B1 Restricción GEI</span>
        <span class="hero-badge" style="border-color:#00BCD4;color:#00BCD4;">
          ⟲ B2 Pérdidas logísticas</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    from pagina_diagrama_sd import construir_diagrama_causal, COLORES_BUCLE

    tab1, tab2 = st.tabs(["📐 Diagrama Causal Interactivo", "🖼️ Diagrama Original Vensim"])

    # ── TAB 1: Diagrama causal interactivo ────────────────────────────
    with tab1:

        # Controles de filtro
        col_ctrl1, col_ctrl2 = st.columns([2, 3])
        with col_ctrl1:
            st.markdown(
                \'\'\'<div class="section-title">Filtrar bucles</div>\'\'\',
                unsafe_allow_html=True)
            mostrar_r1 = st.checkbox("⟳ R1 — Expansión agrícola",  True)
            mostrar_r2 = st.checkbox("⟳ R2 — Biochar-Fertilidad",  True)
            mostrar_b1 = st.checkbox("⟲ B1 — Restricción GEI",     True)
            mostrar_b2 = st.checkbox("⟲ B2 — Pérdidas logísticas", True)
            mostrar_n  = st.checkbox("◦ Conexiones auxiliares",     True)

        with col_ctrl2:
            st.markdown("""
            <div style="background:rgba(10,31,14,0.6);border:1px solid rgba(76,175,80,0.3);
                        border-radius:10px;padding:1rem;">
              <div style="font-family:Space Mono;font-size:0.6rem;color:#FFD700;
                          letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.6rem;">
                Guía de lectura del diagrama
              </div>
              <div style="font-family:DM Sans;font-size:0.8rem;color:#B0BEC5;line-height:1.7;">
                <b style="color:#4CAF50;">+</b> Relación positiva: al aumentar A, aumenta B<br>
                <b style="color:#FF5252;">−</b> Relación negativa: al aumentar A, disminuye B<br>
                <b style="color:#4CAF50;">⟳ Bucle R</b> (refuerzo): amplifica cambios — crecimiento o colapso<br>
                <b style="color:#00BCD4;">⟲ Bucle B</b> (balance): estabiliza — busca equilibrio<br>
                <b style="color:#B0BEC5;">Hover</b> sobre un nodo para ver su valor real del SD
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Construir lista de bucles visibles
        bucles_vis = []
        if mostrar_r1: bucles_vis.append(\'R1\')
        if mostrar_r2: bucles_vis.append(\'R2\')
        if mostrar_b1: bucles_vis.append(\'B1\')
        if mostrar_b2: bucles_vis.append(\'B2\')
        if mostrar_n:  bucles_vis.append(\'N\')

        # Cargar valores reales del SD si hay CSV
        datos_sd_hover = None
        df_res = datos.get(\'resumen\')
        if df_res is not None:
            row = df_res.iloc[0]
            datos_sd_hover = {
                \'Superficie\\nCultivada\':
                    f"{row.get(\'superficie_sd\', 36932):,.0f} Ha",
                \'Generacion de\\nBiomasa\':
                    f"{row.get(\'Q_gen_mean\', 104635):,.0f} Ton/mes",
                \'eta cadena\':
                    f"{row.get(\'eta_cadena_sd\', 0.42):.4f}",
                \'Fertilidad\\ndel Suelo\':
                    f"{row.get(\'fertilidad_sd\', 0.449):.3f}",
            }

        fig_causal = construir_diagrama_causal(
            bucles_visibles=bucles_vis,
            datos_sd=datos_sd_hover,
        )
        st.plotly_chart(fig_causal, use_container_width=True)

        # Tabla de bucles explicada
        st.markdown(
            \'\'\'<div class="section-title">Descripción de los bucles de retroalimentación</div>\'\'\',
            unsafe_allow_html=True)
        b1c, b2c, b3c, b4c = st.columns(4)
        bucles_desc = [
            (b1c, \'R1\', \'#4CAF50\', \'Expansión agrícola\',
             \'Superficie → Biomasa → Utilidad → Inversión → Superficie\',
             \'Bucle virtuoso: mayor área cultivada genera más biomasa, más ingresos '
             \'y más inversión para expandir. Motor del crecimiento del sistema.\'),
            (b2c, \'R2\', \'#FFD700\', \'Biochar-Fertilidad\',
             \'Biochar → Fertilidad → Rendimiento → Biomasa\',
             \'El biochar producido en pirólisis mejora la fertilidad del suelo, '
             \'aumentando el rendimiento agrícola y la generación de biomasa.\'),
            (b3c, \'B1\', \'#FF5252\', \'Restricción GEI\',
             \'GEI → Restricción ambiental → ↓ Inversión\',
             \'Las emisiones de GEI activan restricciones ambientales que '
             \'limitan la inversión y la expansión del sistema. Bucle regulador.\'),
            (b4c, \'B2\', \'#00BCD4\', \'Pérdidas logísticas\',
             \'Pérdidas red → ↑ Costos → ↓ Utilidad\',
             \'Las pérdidas en la red logística (1-η) generan costos adicionales '
             \'que reducen la utilidad neta disponible para reinversión.\'),
        ]
        for col, clave, color, titulo, mecanismo, desc in bucles_desc:
            with col:
                st.markdown(f"""
                <div style="background:rgba(10,31,14,0.6);
                            border:1px solid {color}40;
                            border-top:3px solid {color};
                            border-radius:10px;padding:1rem;">
                  <div style="font-family:Space Mono;font-size:0.7rem;
                              font-weight:700;color:{color};margin-bottom:0.4rem;">
                    {clave} · {titulo}
                  </div>
                  <div style="font-family:DM Sans;font-size:0.75rem;
                              color:#F8FFF8;margin-bottom:0.5rem;">
                    {mecanismo}
                  </div>
                  <div style="font-family:DM Sans;font-size:0.72rem;
                              color:#B0BEC5;line-height:1.5;">
                    {desc}
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 2: Imagen original Vensim ─────────────────────────────────
    with tab2:
        import os
        ruta_img = \'assets/diagrama_vensim.png\'

        if os.path.exists(ruta_img):
            st.image(ruta_img,
                     caption=\'Diagrama Causal SD — Diagrama_Hibrido_Uraba_v6.mdl \' +
                             \'| Vensim PLE | Exportado como PNG\',
                     use_column_width=True)
        else:
            st.markdown("""
            <div style="background:rgba(255,109,0,0.1);
                        border:1px solid #FF6D00;border-radius:10px;
                        padding:2rem;text-align:center;">
              <div style="font-family:Syne;font-size:1.2rem;
                          font-weight:700;color:#FF6D00;margin-bottom:1rem;">
                📁 Imagen no encontrada
              </div>
              <div style="font-family:DM Sans;font-size:0.9rem;color:#B0BEC5;">
                Para mostrar el diagrama original de Vensim:
              </div>
              <div style="font-family:Space Mono;font-size:0.8rem;
                          color:#4CAF50;margin-top:1rem;text-align:left;
                          background:rgba(10,31,14,0.6);padding:1rem;
                          border-radius:8px;border-left:3px solid #4CAF50;">
                1. Abre Vensim PLE<br>
                2. Carga Diagrama_Hibrido_Uraba_v6.mdl<br>
                3. File → Print → Save as Image → PNG<br>
                4. Guarda como: assets/diagrama_vensim.png<br>
                5. Sube la carpeta assets/ a GitHub junto con app.py
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Mientras tanto mostrar el diagrama interactivo como fallback
            st.markdown("""
            <div style="font-family:Space Mono;font-size:0.65rem;color:#4CAF50;
                        letter-spacing:0.1em;margin:1rem 0;">
              ↩ Usa el tab "Diagrama Causal Interactivo" como alternativa
            </div>
            """, unsafe_allow_html=True)
'''

if __name__ == '__main__':
    print("Módulo pagina_diagrama_sd.py cargado correctamente.")
    print(f"Nodos SD: {len(NODOS_SD)}")
    print(f"Conexiones SD: {len(CONEXIONES_SD)}")
    print("Para usar: from pagina_diagrama_sd import construir_diagrama_causal")
