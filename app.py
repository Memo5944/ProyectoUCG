import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import libreria_funciones as lf

# Configuración premium de la página
st.set_page_config(
    page_title="Analizador Salarial", 
    page_icon="💼", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado para un look "Premium" (Glassmorphism & Neon Shadows)
st.markdown("""
    <style>
    /* El fondo y colores generales ahora son manejados por .streamlit/config.toml */
    /* Pero añadimos acentos estéticos premium corporativos */
    
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
    }
    
    /* Acentos corporativos en títulos (Cuerpo principal) */
    h1, h2, h3, h4 {
        color: #0b2659 !important;
    }
    
    h1 {
        font-weight: 800;
        margin-bottom: 5px;
        border-bottom: 3px solid #f2c72e;
        display: inline-block;
        padding-bottom: 5px;
    }
    
    /* Borde amarillo en sidebar y textos visibles */
    [data-testid="stSidebar"] {
        border-right: 4px solid #f2c72e !important;
    }
    
    /* Hacer que los títulos de la barra lateral sean dorados para contraste */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4 {
        color: #f2c72e !important;
        border-bottom: none;
    }
    
    /* Textos comunes en la barra lateral en blanco puro */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Documento cargado: fondo amarillo oro, letras/cursores blancos */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] [data-testid="stUploadedFile"] {
        background-color: #f2c72e !important;
        border: none !important;
        border-radius: 6px !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stFileUploader"] [data-testid="stUploadedFile"] * {
        color: #ffffff !important;
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }
    
    /* Botón Browse Files / Subir archivo en amarillo igual que los tags */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] button {
        background-color: #f2c72e !important;
        color: #0b2659 !important; /* Azul marino para legibilidad del botón o bien blanco */
        border: none !important;
        font-weight: bold !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] button:hover {
        background-color: #ffffff !important;
        color: #0b2659 !important;
    }
    
    /* Estilos Premium para Tarjetas de KPI (Light Mode) */
    .kpi-container {
        display: flex;
        gap: 20px;
        margin-bottom: 25px;
    }
    .kpi-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(11, 38, 89, 0.1);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        width: 100%;
        height: 140px; 
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
        margin-bottom: 20px;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        border-color: rgba(242, 199, 46, 0.8);
        box-shadow: 0 20px 30px -10px rgba(11, 38, 89, 0.15);
    }
    .kpi-title {
        font-size: 0.85rem;
        color: #475569 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #0b2659 !important;
        margin-top: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .kpi-delta {
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        align-self: flex-start;
    }
    .delta-pos {
        color: #0b2659 !important;
        background: #f2c72e;
    }
    .delta-neg {
        color: #ffffff !important;
        background: #ef4444;
    }
    
    /* Elegante caja de descripción corporativa - Modo Claro */
    .chart-description {
        font-size: 0.85rem;
        color: #334155 !important;
        margin-top: 15px;
        margin-bottom: 30px;
        line-height: 1.6;
        background: #ffffff;
        padding: 15px 20px;
        border-radius: 8px;
        border-left: 4px solid #f2c72e;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* Fix global margins for columns */
    div[data-testid="column"] {
        padding: 0 10px;
    }
    </style>
""", unsafe_allow_html=True)

def render_kpi_card(title, value, delta=None, delta_type="positive", border_color="#f2c72e"):
    delta_html = ""
    if delta:
        d_class = "delta-pos" if delta_type == "positive" else "delta-neg"
        delta_html = f'<div class="kpi-delta {d_class}">{delta}</div>'
    else:
        # Espaciador invisible para altura perfecta
        delta_html = '<div style="visibility: hidden;" class="kpi-delta">&nbsp;</div>'
    
    return f"""
    <div class="kpi-card" style="border-left: 5px solid {border_color};">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """

st.title("💼 Análisis Salarial")
st.markdown("Evalúa incrementos salariales basándote en datos reales, equidad interna y posicionamiento corporativo.")

# Sidebar - Carga de Datos
st.sidebar.header("📂 1. Cargar Base de Datos")
archivo_cargado = st.sidebar.file_uploader("Sube tu archivo (Excel o CSV)", type=['csv', 'xlsx'])

if archivo_cargado is not None:
    try:
        if archivo_cargado.name.endswith('.csv'):
            df_raw = pd.read_csv(archivo_cargado)
        else:
            df_raw = pd.read_excel(archivo_cargado)
            
        df = lf.preparar_datos(df_raw.copy())
        
        if 'trabajador' not in df.columns or 'cargo' not in df.columns:
            st.error("El archivo debe contener al menos las columnas 'Trabajador' y 'Cargo'.")
            st.stop()

        # Sidebar - Selección de Trabajadores
        st.sidebar.header("👤 2. Seleccionar Trabajador")
        nombres_trabajadores = df['trabajador'].dropna().unique().tolist()
        trabajador_seleccionado = st.sidebar.selectbox(
            "Buscar empleado solicitante:", 
            nombres_trabajadores
        )
        
        if not trabajador_seleccionado:
            st.warning("👈 Por favor, selecciona un empleado en el panel izquierdo.")
            st.stop()
            
        # Determinar cargos de los seleccionados para default
        cargos_default = df[df['trabajador'] == trabajador_seleccionado]['cargo'].unique().tolist()
        
        # Sidebar - Selección de Cargos a comparar
        st.sidebar.header("🔍 3. Filtro de Cargos Similares")
        todos_los_cargos = df['cargo'].dropna().unique().tolist()
        cargos_comparativa = st.sidebar.multiselect(
            "Selecciona cargos para la comparativa de equidad:", 
            todos_los_cargos, 
            default=cargos_default
        )
        
        if not cargos_comparativa:
            st.warning("👈 Por favor, selecciona al menos un cargo para realizar la comparativa.")
            st.stop()

        metricas_comparativa_global = lf.obtener_metricas_cargos_multiples(df, cargos_comparativa)
        mediana_global = metricas_comparativa_global['mediana'] if metricas_comparativa_global else 0

        # Sidebar - Parámetros de Simulación
        st.sidebar.header("📈 4. Parámetros de Simulación")
        inflacion = st.sidebar.number_input("Inflación Anual Esperada (%)", min_value=0.0, max_value=100.0, value=3.0, step=0.1)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("💡 **Ajustes Sugeridos a la Mediana**")
        st.sidebar.caption("Se preestablece el % para alcanzar la mediana comparativa, pero puedes editarlo libremente.")
        
        datos_empleado = df[df['trabajador'] == trabajador_seleccionado].iloc[0]
        salario_actual = datos_empleado.get('salario_total', 0)
        
        # Calcular ajuste a la mediana
        if mediana_global > salario_actual and salario_actual > 0:
            porcentaje_sugerido = ((mediana_global / salario_actual) - 1) * 100
        else:
            porcentaje_sugerido = 0.0
            
        aumento_solicitado = st.sidebar.number_input(
            f"Incremento a Simular (%)", 
            min_value=0.0, max_value=500.0, 
            value=float(round(porcentaje_sugerido, 1)), 
            step=0.5
        )
        
        

        
        cargo_para_busqueda = str(datos_empleado.get('cargo', '')).strip()
        datos_mercado = lf.estimar_mercado_externo(cargo_para_busqueda, mediana_global)
        salario_mercado_estimado = datos_mercado['salario_estimado']


        st.markdown("<br>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["📊 1. Análisis Interno y Simulación", "🌍 2. Mercado Externo (Ecuador)"])
        
        df_pares_global = df[df['cargo'].str.lower().isin([c.lower() for c in cargos_comparativa])]

        with tab1:

            for trabajador_seleccionado in [trabajador_seleccionado]:
                cargo_empleado = datos_empleado['cargo']

                st.markdown(f"### Simulador de Incremento para: **{trabajador_seleccionado.title()}**")
                antiguedad_val = datos_empleado.get('antigüedad', 'N/D')
                antiguedad_str = f"{antiguedad_val:.2f}" if isinstance(antiguedad_val, (int, float)) else antiguedad_val
                st.markdown(f"**Cargo:** {cargo_empleado.title()} | **Antigüedad:** {antiguedad_str} años")
                st.markdown("<br>", unsafe_allow_html=True)
                
                analisis = lf.evaluar_incremento_detallado(datos_empleado, aumento_solicitado, inflacion)
                
                mediana_cargo = metricas_comparativa_global['mediana'] if metricas_comparativa_global else 0
                compa_ratio_actual = lf.calcular_compa_ratio(salario_actual, mediana_cargo) if hasattr(lf, 'calcular_compa_ratio') else (salario_actual / mediana_cargo if mediana_cargo > 0 else 0)
                compa_ratio_propuesto = lf.calcular_compa_ratio(analisis['salario_propuesto'], mediana_cargo) if hasattr(lf, 'calcular_compa_ratio') else (analisis['salario_propuesto'] / mediana_cargo if mediana_cargo > 0 else 0)
                
                # Fila de KPIs
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(render_kpi_card("Salario Actual", f"USD {salario_actual:,.2f}", border_color="#f2c72e"), unsafe_allow_html=True)
                with c2:
                    st.markdown(render_kpi_card("Salario Propuesto", f"USD {analisis['salario_propuesto']:,.2f}", f"+{aumento_solicitado}% (+USD {analisis['aumento_real_monto']:,.2f})", delta_type="positive", border_color="#48BB78"), unsafe_allow_html=True)
                with c3:
                    st.markdown(render_kpi_card("Pérdida por Inflación", f"-USD {analisis['perdida_inflacion']:,.2f}", f"-{inflacion}%", delta_type="negative", border_color="#F56565"), unsafe_allow_html=True)
                with c4:
                    val_mediana = f"USD {mediana_cargo:,.2f}" if mediana_cargo > 0 else "N/D"
                    st.markdown(render_kpi_card("Mediana Comparativa", val_mediana, border_color="#F59E0B"), unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                
                if 'df_desglose' in analisis:
                    st.markdown("#### 🧩 Estructura Salarial Propuesta (Desglose)")
                    st.caption("Muestra cómo el incremento en el Salario Base impacta proporcionalmente el valor de las Horas Extras (HE).")
                    
                    df_desglose = analisis['df_desglose']
                    
                    def highlight_total(row):
                        if row['Rubro'] == 'TOTAL':
                            return ['background-color: rgba(242, 199, 46, 0.3); font-weight: bold; color: #0b2659'] * len(row)
                        return [''] * len(row)
                        
                    formato_desglose = {
                        'Actual': '${:,.2f}',
                        'Propuesto': '${:,.2f}',
                        'Diferencia': '+${:,.2f}'
                    }
                    
                    st.dataframe(df_desglose.style.apply(highlight_total, axis=1).format(formato_desglose), use_container_width=True)

                st.markdown("---")
                
                col_antiguedad = next((c for c in df.columns if 'antig' in c or 'año' in c or 'year' in c), None)
                
            # --- FILA 1 ---
            row1_col1, row1_col2 = st.columns(2)
            
            with row1_col1:
                st.markdown("#### 📊 Equidad Interna y Compa-Ratio")
                # Velocímetro
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = compa_ratio_actual,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Compa-Ratio Actual", 'font': {'size': 14, 'color': "#0b2659"}},
                    number = {'valueformat': ".2f", 'font': {'color': "#0b2659", 'size': 32}},
                    gauge = {
                        'axis': {'range': [0.5, 1.5], 'tickwidth': 1, 'tickcolor': "#0b2659"},
                        'bar': {'color': "#f2c72e"},
                        'bgcolor': "rgba(255,255,255,0.05)",
                        'borderwidth': 0,
                        'steps': [
                            {'range': [0.5, 0.8], 'color': 'rgba(239, 68, 68, 0.3)'},
                            {'range': [0.8, 1.2], 'color': 'rgba(16, 185, 129, 0.3)'},
                            {'range': [1.2, 1.5], 'color': 'rgba(245, 158, 11, 0.3)'}
                        ],
                        'threshold': {
                            'line': {'color': "#FF4B4B", 'width': 4},
                            'thickness': 0.75,
                            'value': compa_ratio_propuesto
                        }
                    }
                ))
                fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#0b2659", height=240, margin=dict(t=30, b=10, l=20, r=20))
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                # Explicación del Compa-Ratio
                texto_explicacion_compa = """
                <div class="chart-description" style="margin-top: -10px; margin-bottom: 20px;">
                    <b>¿Cómo interpretar el Compa-Ratio?</b> Mide la competitividad del salario frente a la Mediana Comparativa (1.0).<br>
                    • 🔴 <b>< 0.8:</b> Riesgo de fuga de talento (Subpagado).<br>
                    • 🟢 <b>0.8 - 1.2:</b> Zona de equidad y competitividad.<br>
                    • 🟠 <b>> 1.2:</b> Alto costo / Tope salarial (Sobrepagado).<br>
                    <i>* La barra de color indica la posición actual, y la <b>línea roja</b> marca dónde quedará el empleado tras simular el incremento.</i>
                </div>
                """
                st.markdown(texto_explicacion_compa, unsafe_allow_html=True)

            with row1_col2:
                if col_antiguedad:
                    st.markdown("#### 📈 Antigüedad vs Salario")
                    # Scatter simplificado
                    fig_scatter = px.scatter(df_pares_global, x=col_antiguedad, y="salario_total", text="trabajador",
                                             size="salario_total", color="cargo",
                                             labels={col_antiguedad: "Antigüedad (Años)", "salario_total": "Salario Total (USD)", "cargo": "Cargo"})
                    fig_scatter.update_traces(textposition='top center')
                    
                    x_vals = df_pares_global[col_antiguedad].fillna(0).values
                    y_vals = df_pares_global['salario_total'].fillna(0).values
                    
                    # Solo intentar hacer la línea de tendencia si hay al menos 2 puntos con X (antigüedad) distinto
                    if len(x_vals) > 1 and len(set(x_vals)) > 1:
                        try:
                            m, c = np.polyfit(x_vals, y_vals, 1)
                            x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
                            y_line = m * x_line + c
                            
                            fig_scatter.add_trace(go.Scatter(
                                x=x_line, y=y_line, mode='lines',
                                line=dict(color='rgba(11, 38, 89, 0.6)', dash='dash'),
                                name='Tendencia Esperada'
                            ))
                            
                            fig_scatter.add_trace(go.Scatter(
                                x=np.concatenate([x_line, x_line[::-1]]),
                                y=np.concatenate([y_line * 1.15, (y_line * 0.85)[::-1]]),
                                fill='toself',
                                fillcolor='rgba(0, 210, 211, 0.1)',
                                line=dict(color='rgba(255,255,255,0)'),
                                hoverinfo="skip",
                                name="Tolerancia (±15%)"
                            ))
                        except Exception:
                            pass # Ignorar si la matemática de la tendencia falla
                    
                    # Resaltar evaluado
                    fig_scatter.add_trace(go.Scatter(
                        x=[datos_empleado.get(col_antiguedad, 0)], y=[salario_actual], mode='markers+text',
                        marker=dict(color='#EF4444', size=22, symbol='star', line=dict(color='#0b2659', width=2)),
                        text=[f"Eval: {trabajador_seleccionado}"], textposition="bottom center", name="Evaluado",
                        textfont=dict(color="#EF4444", size=12, weight="bold")
                    ))
                    
                    fig_scatter.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)", 
                        paper_bgcolor="rgba(0,0,0,0)", 
                        font_color="#0b2659", 
                        height=240, 
                        margin=dict(t=20, b=20, l=20, r=20),
                        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.7)")
                    )
                    fig_scatter.update_xaxes(gridcolor="rgba(11,38,89,0.1)")
                    fig_scatter.update_yaxes(gridcolor="rgba(11,38,89,0.1)")
                    st.plotly_chart(fig_scatter, use_container_width=True)
                    
                    texto_analisis_scatter = f"<b>Interpretación:</b> Con {datos_empleado.get(col_antiguedad, 0):.1f} años de antigüedad, el sueldo busca respetar la curva de experiencia del equipo. Puntos muy por debajo de la zona sombreada alertan sobre un alto riesgo de rotación por falta de equidad."
                    st.markdown(f'<div class="chart-description" style="margin-top: -10px; margin-bottom: 20px;">{texto_analisis_scatter}</div>', unsafe_allow_html=True)
                else:
                    st.warning("No se encontró columna de antigüedad para la tendencia.")

            # --- FILA 2 ---
            st.markdown("<br>", unsafe_allow_html=True)
            row2_col1, row2_col2 = st.columns(2)
            
            with row2_col1:
                st.markdown("#### ⚖️ Comparativa Directa de Pares")
                # Gráfico de Barras Comparativo
                df_pares_local = df_pares_global.sort_values('salario_total', ascending=False).copy()
                
                # Resaltar al evaluado con otro color
                df_pares_local['Color'] = ['#FF4B4B' if t == trabajador_seleccionado else '#0b2659' for t in df_pares_local['trabajador']]
                
                fig_bar = px.bar(df_pares_local, x="trabajador", y="salario_total", 
                                 text="salario_total",
                                 color="Color", color_discrete_map="identity",
                                 labels={"trabajador": "Empleado", "salario_total": "Salario (USD)"})
                
                fig_bar.update_traces(texttemplate='USD %{text:,.0f}', textposition='outside')
                fig_bar.add_hline(y=analisis['salario_propuesto'], line_dash="dash", line_color="#FF4B4B", annotation_text="Propuesto")
                fig_bar.add_hline(y=mediana_cargo, line_dash="solid", line_color="#F59E0B", annotation_text="Mediana")
                
                fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#0b2659", height=260, margin=dict(t=20, b=20, l=10, r=10))
                fig_bar.update_yaxes(gridcolor="rgba(11,38,89,0.1)", range=[0, max(df_pares_local['salario_total'].max(), analisis['salario_propuesto']) * 1.25])
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Análisis de texto dinámico
                pos_actual = (salario_actual/mediana_cargo)*100 if mediana_cargo > 0 else 100
                pos_nueva = (analisis['salario_propuesto']/mediana_cargo)*100 if mediana_cargo > 0 else 100
                texto_analisis_bar = f"<b>Interpretación:</b> {trabajador_seleccionado} gana USD {salario_actual:,.0f} ({pos_actual:.1f}% de la mediana comparativa). El nuevo sueldo (USD {analisis['salario_propuesto']:,.0f}) ajustará su posición al {pos_nueva:.1f}% frente a sus colegas directos."
                st.markdown(f'<div class="chart-description">{texto_analisis_bar}</div>', unsafe_allow_html=True)
                
            with row2_col2:
                st.markdown("#### 📦 Distribución Salarial (Cajas)")
                # Gráfico de Caja y Bigotes
                fig_box = px.box(df_pares_global, x="cargo", y="salario_total", points="all",
                                 color="cargo",
                                 labels={"cargo": "Cargo", "salario_total": "Salario Total (USD)"})
                
                # Líneas de referencia
                fig_box.add_hline(y=salario_actual, line_dash="solid", line_color="#f2c72e", annotation_text="Actual")
                fig_box.add_hline(y=analisis['salario_propuesto'], line_dash="dash", line_color="#FF4B4B", annotation_text="Propuesto")
                
                fig_box.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    font_color="#0b2659", 
                    height=260, 
                    margin=dict(t=20, b=20, l=10, r=10),
                    showlegend=False
                )
                fig_box.update_yaxes(gridcolor="rgba(11,38,89,0.1)")
                st.plotly_chart(fig_box, use_container_width=True)
                
                texto_analisis_box = f"<b>Interpretación:</b> La 'caja' azul muestra dónde se concentra el 50% de los sueldos del mercado analizado. Los 'bigotes' marcan los extremos, y los puntos son colegas individuales. La <b>línea roja</b> te muestra cómo quedará la propuesta frente a la distribución general."
                st.markdown(f'<div class="chart-description">{texto_analisis_box}</div>', unsafe_allow_html=True)
                
            # Moviendo el cuadro comparativo a ancho completo
            st.markdown("---")
            st.markdown("#### 📋 Cuadro Comparativo Detallado de Pares (Ranking y Simulación)")
            
            cols_to_select = ['trabajador', 'cargo']
            if col_antiguedad: cols_to_select.append(col_antiguedad)
            
            # Agregamos base y horas extras para mostrar que se consideran
            has_base = 'salario_base_limpio' in df_pares_global.columns
            if has_base: cols_to_select.extend(['salario_base_limpio', 'total_horas_extras'])
            
            cols_to_select.append('salario_total')
            
            df_comparativo = df_pares_global[cols_to_select].copy()
            df_comparativo['Salario Nuevo'] = df_comparativo['salario_total'].astype(float)
            df_comparativo.loc[df_comparativo['trabajador'] == trabajador_seleccionado, 'Salario Nuevo'] = float(analisis['salario_propuesto'])
            
            # Nuevas métricas
            df_comparativo['Diferencia ($)'] = df_comparativo['Salario Nuevo'] - df_comparativo['salario_total']
            df_comparativo['Crecimiento (%)'] = np.where(df_comparativo['salario_total'] > 0, (df_comparativo['Diferencia ($)'] / df_comparativo['salario_total']) * 100, 0)
            
            columnas_finales = ['Empleado', 'Cargo']
            if col_antiguedad: columnas_finales.append('Años')
            if has_base: columnas_finales.extend(['Salario Base', 'Horas Extras Fijas'])
            columnas_finales.extend(['Salario Actual', 'Salario Nuevo', 'Diferencia ($)', 'Crecimiento (%)'])
            
            df_comparativo.columns = columnas_finales
            
            # Formateamos Años a 2 decimales si existe
            if 'Años' in df_comparativo.columns:
                df_comparativo['Años'] = df_comparativo['Años'].round(2)
                
            df_comparativo = df_comparativo.sort_values('Salario Nuevo', ascending=False).reset_index(drop=True)
            
            def highlight_selected(row):
                if row['Empleado'] == trabajador_seleccionado:
                    return ['background-color: rgba(239, 68, 68, 0.2); color: #0b2659; font-weight: bold'] * len(row)
                return [''] * len(row)
                
            formato_columnas = {
                'Salario Actual': '${:,.2f}',
                'Salario Nuevo': '${:,.2f}',
                'Diferencia ($)': '${:,.2f}',
                'Crecimiento (%)': '{:,.2f}%',
                'Años': '{:.2f}'
            }
            if has_base:
                formato_columnas['Salario Base'] = '${:,.2f}'
                formato_columnas['Horas Extras Fijas'] = '${:,.2f}'
                
            st.dataframe(df_comparativo.style.apply(highlight_selected, axis=1).format(formato_columnas), use_container_width=True)
            
            st.markdown("#### 🤖 Diagnóstico Salarial Estratégico")
            col_diag1, col_diag2, col_diag3 = st.columns(3)
            with col_diag1:
                st.markdown("##### 🏢 Frente al Mercado Interno")
                if metricas_comparativa_global:
                    if analisis['salario_propuesto'] > metricas_comparativa_global['max']:
                        st.error(f"⚠️ **Alerta de Inequidad:** El salario propuesto (USD {analisis['salario_propuesto']:,.2f}) superaría el máximo actual pagado internamente (USD {metricas_comparativa_global['max']:,.2f}).")
                    elif analisis['salario_propuesto'] < metricas_comparativa_global['mediana']:
                        st.success(f"✅ **Viable en Equidad:** El salario propuesto (USD {analisis['salario_propuesto']:,.2f}) se mantiene por debajo de la mediana comparativa interna (USD {metricas_comparativa_global['mediana']:,.2f}).")
                    else:
                        st.info(f"ℹ️ **Posicionamiento Competitivo:** El salario propuesto se encuentra en el rango superior competitivo del mercado interno.")
            
            with col_diag2:
                st.markdown("##### 📊 Riesgo de Retención (Compa-Ratio)")
                if compa_ratio_actual < 0.8:
                    st.warning(f"⚠️ **Riesgo Alto (CR: {compa_ratio_actual:.2f}):** El empleado está subpagado frente a sus pares. Aumento recomendado para evitar fuga.")
                elif compa_ratio_actual > 1.2:
                    st.info(f"ℹ️ **Alta Inversión (CR: {compa_ratio_actual:.2f}):** El empleado está en el tope salarial interno.")
                else:
                    st.success(f"✅ **Alineado (CR: {compa_ratio_actual:.2f}):** El salario base es competitivo frente a sus colegas.")

            st.markdown("<hr style='border: 2px solid #f2c72e; margin: 50px 0;'>", unsafe_allow_html=True)



        with tab2:
            st.markdown(f"### 🌍 Benchmark de Mercado Externo - **Ecuador**")
            st.markdown(f"Análisis salarial enfocado al mercado corporativo nacional para el cargo de **{cargo_para_busqueda.title()}**.")
            st.markdown("<br>", unsafe_allow_html=True)
            
            t2_c1, t2_c2 = st.columns([1, 1.5])
            
            with t2_c1:
                salario_mercado_externo = st.number_input(
                    "Sueldo Promedio Mercado (USD)", 
                    min_value=0.0, value=float(salario_mercado_estimado), step=50.0, 
                    help="Puedes modificar manualmente si el CEO requiere probar otro escenario de mercado externo."
                )
                
                st.markdown(render_kpi_card("Mediana Externa (Referencial)", f"USD {salario_mercado_externo:,.0f}", border_color="#0b2659"), unsafe_allow_html=True)
                
            with t2_c2:
                # Ficha de calidad de datos CEO Level
                html_ficha = f"""
                <div style="background: rgba(255,255,255,0.9); padding: 20px; border-radius: 12px; border-left: 5px solid #0b2659; box-shadow: 0 5px 15px rgba(0,0,0,0.05); color: #0b2659;">
                    <h4 style="margin-top: 0; color: #0b2659; font-weight: bold;">📑 Ficha Técnica Comercial (Ecuador)</h4>
                    <p style="margin-bottom: 5px;"><b>🏢 Empresas de Referencia:</b> {datos_mercado['empresa_referencia']}</p>
                    <p style="margin-bottom: 5px;"><b>📊 Fuentes Contrastadas:</b> {datos_mercado['fuente']}</p>
                    <p style="margin-bottom: 5px;"><b>✅ Nivel de Confianza:</b> {datos_mercado['confianza']}</p>
                    <hr style="border-top: 1px solid rgba(11, 38, 89, 0.2); margin: 10px 0;">
                    <p style="margin-bottom: 0; font-size: 0.9em; font-style: italic;">{datos_mercado['mensaje']}</p>
                </div>
                """
                st.markdown(html_ficha, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### 🤖 Diagnóstico Estratégico frente a Competencia Nacional", unsafe_allow_html=True)
            
            if salario_mercado_externo > 0:
                diferencia_ext = analisis['salario_propuesto'] - salario_mercado_externo
                pct_ext = (diferencia_ext / salario_mercado_externo) * 100
                if pct_ext < -10:
                    st.error(f"📉 **Desventaja vs Ecuador:** Nuestra propuesta final (USD {analisis['salario_propuesto']:,.2f}) está **{abs(pct_ext):.1f}% por debajo** del mercado nacional (USD {salario_mercado_externo:,.0f}). \n\n⚠️ **Riesgo:** Alta probabilidad de perder a este perfil frente a competidores directos como **{datos_mercado['empresa_referencia']}**.")
                elif pct_ext > 10:
                    st.warning(f"📈 **Por Encima del Mercado:** La propuesta está **{pct_ext:.1f}% superior** a la media nacional en Ecuador. \n\n🛡️ **Evaluación:** Estratégicamente garantiza alta retención de talento y exclusividad, pero incrementa costos operativos por encima del benchmark de la industria.")
                else:
                    st.success(f"🎯 **Alineación Perfecta (Ecuador):** Nuestra propuesta (USD {analisis['salario_propuesto']:,.2f}) es equilibrada y competitiva (**±10%**) frente a los estándares manejados por referentes como **{datos_mercado['empresa_referencia']}**.")
            else:
                 st.info("ℹ️ Investiga e ingresa el salario de mercado para obtener un diagnóstico externo.")


        # Dashboard Global removido según requerimiento

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")

else:
    st.info("👈 Sube tu base de datos salarial en el panel lateral izquierdo para comenzar.")
    
    st.markdown("#### Formato de archivo esperado:")
    ejemplo = pd.DataFrame({
        "Codigo": ["EMP01", "EMP02", "EMP03"],
        "Trabajador": ["Juan Perez", "Maria Gomez", "Carlos Diaz"],
        "Cargo": ["Analista Financiero", "Analista Financiero", "Gerente"],
        "Area": ["Finanzas", "Finanzas", "Finanzas"],
        "Antigüedad": ["15/05/2021", "10/01/2019", "01/08/2013"],
        "Edad": [28, 32, 45],
        "Salario": [1200, 1400, 3000],
        "HE 25%": [50, 0, 0],
        "HE 50%": [0, 100, 0],
        "HE 100%": [0, 0, 150]
    })
    st.dataframe(ejemplo)
