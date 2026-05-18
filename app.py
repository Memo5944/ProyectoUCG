import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import libreria_funciones as lf

# Configuración premium de la página
st.set_page_config(
    page_title="Bot Analizador Salarial", 
    page_icon="💼", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado para un look "Premium" (Glassmorphism & Neon Shadows)
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
    }
    h1, h2, h3, h4 {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Estilos Premium para Tarjetas de KPI */
    .kpi-container {
        display: flex;
        gap: 15px;
        margin-bottom: 20px;
    }
    .kpi-card {
        background: rgba(30, 33, 43, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s ease-in-out;
        width: 100%;
        height: 120px; /* Altura fija para que todas estén perfectamente alineadas */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
    }
    .kpi-title {
        font-size: 0.75rem;
        color: #A0AEC0;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis; /* Evita que el título se sobresalga */
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-top: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis; /* Evita desborde de números */
    }
    .kpi-delta {
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        align-self: flex-start;
    }
    .delta-pos {
        color: #48BB78;
        background: rgba(72, 187, 120, 0.15);
    }
    .delta-neg {
        color: #F56565;
        background: rgba(245, 101, 101, 0.15);
    }
    
    /* Elegante caja de descripción para los gráficos */
    .chart-description {
        font-size: 0.82rem;
        color: #CBD5E0;
        margin-top: 5px;
        margin-bottom: 25px;
        line-height: 1.45;
        background: rgba(255, 255, 255, 0.03);
        padding: 10px 15px;
        border-radius: 8px;
        border-left: 3px solid #00D2D3;
    }
    </style>
""", unsafe_allow_html=True)

def render_kpi_card(title, value, delta=None, delta_type="positive", border_color="#00D2D3"):
    delta_html = ""
    if delta:
        d_class = "delta-pos" if delta_type == "positive" else "delta-neg"
        delta_html = f'<div class="kpi-delta {d_class}">{delta}</div>'
    else:
        # Espaciador invisible para que la alineación flex vertical sea idéntica en todas las tarjetas
        delta_html = '<div style="visibility: hidden;" class="kpi-delta">&nbsp;</div>'
    
    return f"""
    <div class="kpi-card" style="border-left: 4px solid {border_color};">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """

st.title("💼 Bot de Análisis de Equidad e Incremento Salarial")
st.markdown("Evalúa incrementos salariales basándote en datos reales, equidad interna y factores macroeconómicos.")

# Sidebar - Carga de Datos
st.sidebar.header("📂 1. Cargar Base de Datos")
archivo_cargado = st.sidebar.file_uploader("Sube tu archivo (Excel o CSV)", type=['csv', 'xlsx'])

if archivo_cargado is not None:
    # Leer archivo
    try:
        if archivo_cargado.name.endswith('.csv'):
            df_raw = pd.read_csv(archivo_cargado)
        else:
            df_raw = pd.read_excel(archivo_cargado)
            
        # Preparar datos
        df = lf.preparar_datos(df_raw.copy())
        
        # Validar columnas necesarias (simplificado)
        if 'trabajador' not in df.columns or 'cargo' not in df.columns:
            st.error("El archivo debe contener al menos las columnas 'Trabajador' y 'Cargo'.")
            st.stop()

        # Sidebar - Selección de Trabajador
        st.sidebar.header("👤 2. Seleccionar Trabajador")
        nombres_trabajadores = df['trabajador'].dropna().unique().tolist()
        trabajador_seleccionado = st.sidebar.selectbox("Buscar empleado solicitante:", nombres_trabajadores)
        
        # Obtener datos del trabajador
        datos_empleado = df[df['trabajador'] == trabajador_seleccionado].iloc[0]
        cargo_empleado = datos_empleado['cargo']
        salario_actual = datos_empleado.get('salario_total', 0)
        
        # Sidebar - Parámetros de Simulación
        st.sidebar.header("📈 3. Parámetros de Simulación")
        inflacion = st.sidebar.number_input("Inflación Anual Esperada (%)", min_value=0.0, max_value=100.0, value=3.0, step=0.1)
        aumento_solicitado = st.sidebar.slider("Incremento a simular (%)", min_value=0.0, max_value=50.0, value=5.0, step=0.5)

        # -- MAIN DASHBOARD --
        tab1, tab2 = st.tabs(["👤 Análisis Individual (Simulador)", "🏢 Dashboard Global (Empresa)"])
        
        with tab1:
            st.markdown("### Simulador de Incremento para: **{}**".format(trabajador_seleccionado.title()))
            st.markdown(f"**Cargo:** {cargo_empleado.title()} | **Antigüedad:** {datos_empleado.get('antigüedad', 'N/D')} años")
            
            # Cálculos
            analisis = lf.evaluar_incremento(salario_actual, aumento_solicitado, inflacion)
            metricas_cargo = lf.obtener_metricas_cargo(df, cargo_empleado)
            
            mediana_cargo = metricas_cargo['mediana'] if metricas_cargo else 0
            compa_ratio_actual = lf.calcular_compa_ratio(salario_actual, mediana_cargo)
            compa_ratio_propuesto = lf.calcular_compa_ratio(analisis['salario_propuesto'], mediana_cargo)
            
            # Fila de Métricas Principales (KPIs) usando HTML Premium (Misma altura)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(render_kpi_card("Salario Total Actual", f"${salario_actual:,.2f}", border_color="#00D2D3"), unsafe_allow_html=True)
            with c2:
                st.markdown(render_kpi_card("Salario Propuesto", f"${analisis['salario_propuesto']:,.2f}", f"+{aumento_solicitado}% (+${analisis['aumento_real_monto']:,.2f})", delta_type="positive", border_color="#48BB78"), unsafe_allow_html=True)
            with c3:
                st.markdown(render_kpi_card("Pérdida por Inflación", f"-${analisis['perdida_inflacion']:,.2f}", f"-{inflacion}%", delta_type="negative", border_color="#F56565"), unsafe_allow_html=True)
            with c4:
                val_mediana = f"${mediana_cargo:,.2f}" if mediana_cargo > 0 else "N/D"
                st.markdown(render_kpi_card("Mediana del Cargo (Interna)", val_mediana, border_color="#ED8936"), unsafe_allow_html=True)

            st.markdown("---")
            
            # Gráficos Individuales (Tamaños igualados a 440px en total para simetría)
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                st.markdown("#### 📊 Equidad Interna y Compa-Ratio")
                # Velocímetro (Gauge) para Compa-Ratio (Altura: 200px)
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = compa_ratio_actual,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Compa-Ratio Actual", 'font': {'size': 13, 'color': "white"}},
                    number = {'valueformat': ".2f", 'font': {'color': "white", 'size': 28}},
                    gauge = {
                        'axis': {'range': [0.5, 1.5], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': "#00D2D3"},
                        'bgcolor': "rgba(0,0,0,0)",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0.5, 0.8], 'color': 'rgba(245, 101, 101, 0.2)'},
                            {'range': [0.8, 1.2], 'color': 'rgba(72, 187, 120, 0.2)'},
                            {'range': [1.2, 1.5], 'color': 'rgba(237, 137, 54, 0.2)'}
                        ],
                        'threshold': {
                            'line': {'color': "#FF4B4B", 'width': 4},
                            'thickness': 0.75,
                            'value': compa_ratio_propuesto
                        }
                    }
                ))
                fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=200, margin=dict(t=25, b=10, l=10, r=10))
                st.plotly_chart(fig_gauge, use_container_width=True)
                st.markdown('<div class="chart-description"><b>Velocímetro de Compa-Ratio:</b> Mide la competitividad salarial del empleado frente a la mediana de su cargo. La zona verde indica equilibrio con el mercado. La línea roja marca el cambio si se aprueba el aumento.</div>', unsafe_allow_html=True)
                
                # Distribución en Box Plot (Altura: 200px)
                df_pares = df[df['cargo'].str.lower() == cargo_empleado.lower()]
                fig_box = px.box(df_pares, y="salario_total", points="all", hover_data=["trabajador"],
                                 labels={"salario_total": "Salario Total ($)"},
                                 color_discrete_sequence=['#00D2D3'])
                fig_box.add_hline(y=analisis['salario_propuesto'], line_dash="dash", line_color="#FF4B4B", annotation_text="Propuesto")
                fig_box.add_hline(y=salario_actual, line_dash="solid", line_color="#FFA500", annotation_text="Actual")
                fig_box.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=200, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_box, use_container_width=True)
                st.markdown('<div class="chart-description"><b>Rango Salarial del Cargo:</b> Muestra los cuartiles de pago del mismo puesto de trabajo. La caja representa el 50% central de los sueldos para evaluar si el empleado está subpagado o sobrecompensado.</div>', unsafe_allow_html=True)

            with col_graf2:
                st.markdown("#### 📈 Antigüedad vs Salario con Línea de Tendencia")
                col_antiguedad = next((c for c in df.columns if 'antig' in c or 'año' in c or 'year' in c), None)
                if col_antiguedad:
                    # Crear scatter base (Altura: 410px para que coincida con el lado izquierdo)
                    fig_scatter = px.scatter(df_pares, x=col_antiguedad, y="salario_total", text="trabajador",
                                             size="salario_total", color="salario_total",
                                             labels={col_antiguedad: "Antigüedad (Años)", "salario_total": "Salario Total ($)"},
                                             color_continuous_scale=px.colors.sequential.Teal)
                    
                    # Calcular línea de regresión de forma nativa con NumPy
                    x_vals = df_pares[col_antiguedad].values
                    y_vals = df_pares['salario_total'].values
                    if len(x_vals) > 1:
                        m, c = np.polyfit(x_vals, y_vals, 1)
                        x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
                        y_line = m * x_line + c
                        
                        fig_scatter.add_trace(go.Scatter(
                            x=x_line, y=y_line, mode='lines',
                            line=dict(color='rgba(255, 255, 255, 0.4)', dash='dash'),
                            name='Tendencia del Cargo'
                        ))
                        
                        fig_scatter.add_trace(go.Scatter(
                            x=np.concatenate([x_line, x_line[::-1]]),
                            y=np.concatenate([y_line * 1.15, (y_line * 0.85)[::-1]]),
                            fill='toself',
                            fillcolor='rgba(0, 210, 211, 0.08)',
                            line=dict(color='rgba(255,255,255,0)'),
                            hoverinfo="skip",
                            name="Banda Aceptable (±15%)"
                        ))
                    
                    # Resaltar al trabajador evaluado
                    fig_scatter.add_trace(go.Scatter(
                        x=[datos_empleado[col_antiguedad]], y=[salario_actual], mode='markers+text',
                        marker=dict(color='#FF4B4B', size=16, symbol='star', line=dict(color='white', width=2)),
                        text=['Actual ⭐'], textposition="top center", name="Trabajador Evaluado"
                    ))
                    
                    fig_scatter.update_traces(textposition='bottom center')
                    fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=410, margin=dict(t=10, b=10, l=10, r=10))
                    st.plotly_chart(fig_scatter, use_container_width=True)
                    st.markdown('<div class="chart-description"><b>Curva de Experiencia:</b> Mapea la relación entre antigüedad laboral y salario. La línea discontinua marca la progresión estándar y la zona verde sombreada define el rango de tolerancia.</div>', unsafe_allow_html=True)
                else:
                    st.warning("No se encontró columna de antigüedad para la tendencia.")
            
            # Conclusión
            st.markdown("#### 🤖 Diagnóstico Salarial")
            col_diag1, col_diag2 = st.columns(2)
            with col_diag1:
                if metricas_cargo:
                    if analisis['salario_propuesto'] > metricas_cargo['max']:
                        st.error(f"⚠️ **Alerta de Inequidad:** El salario propuesto (${analisis['salario_propuesto']:,.2f}) superaría el máximo actual pagado para este cargo (${metricas_cargo['max']:,.2f}). Podría generar tensión interna.")
                    elif analisis['salario_propuesto'] < metricas_cargo['mediana']:
                        st.success(f"✅ **Viable en Equidad:** El salario propuesto (${analisis['salario_propuesto']:,.2f}) se mantiene por debajo de la mediana del cargo (${metricas_cargo['mediana']:,.2f}). Es un ajuste seguro.")
                    else:
                        st.info(f"ℹ️ **Posicionamiento Competitivo:** El salario propuesto se encuentra en el rango superior competitivo del mercado interno.")
            
            with col_diag2:
                if compa_ratio_actual < 0.8:
                    st.warning(f"⚠️ **Alerta de Retención (Compa-Ratio: {compa_ratio_actual:.2f}):** El empleado está subpagado con respecto a sus compañeros. Un aumento es recomendado para evitar fuga de talento.")
                elif compa_ratio_actual > 1.2:
                    st.info(f"ℹ️ **Alta Inversión (Compa-Ratio: {compa_ratio_actual:.2f}):** El empleado está altamente compensado. Asegúrate de que su desempeño justifique este nivel.")
                else:
                    st.success(f"✅ **Alineación de Mercado (Compa-Ratio: {compa_ratio_actual:.2f}):** El salario del empleado es competitivo y está bien alineado.")

        with tab2:
            st.markdown("### 🏢 Dashboard de Compensación Organizacional")
            
            # KPIs globales Premium (Misma altura)
            g1, g2, g3, g4 = st.columns(4)
            with g1:
                st.markdown(render_kpi_card("Total Empleados", len(df), border_color="#00D2D3"), unsafe_allow_html=True)
            with g2:
                st.markdown(render_kpi_card("Nómina Total (Mensual)", f"${df['salario_total'].sum():,.2f}", border_color="#48BB78"), unsafe_allow_html=True)
            with g3:
                st.markdown(render_kpi_card("Promedio Salarial", f"${df['salario_total'].mean():,.2f}", border_color="#ED8936"), unsafe_allow_html=True)
            with g4:
                st.markdown(render_kpi_card("Cargos Distintos", f"{df['cargo'].nunique()}", border_color="#9F7AEA"), unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Gráficos de fila 1 (Alturas igualadas a 330px)
            col_dash1, col_dash2 = st.columns(2)
            
            with col_dash1:
                col_dpto = next((c for c in df.columns if 'departamento' in c or 'area' in c or 'área' in c), None)
                if col_dpto:
                    st.markdown("#### 📊 Distribución de Nómina por Departamento")
                    df_dpto = df.groupby(col_dpto)['salario_total'].sum().reset_index()
                    fig_pie = px.pie(df_dpto, values='salario_total', names=col_dpto, hole=0.5,
                                     color_discrete_sequence=px.colors.sequential.Mint)
                    fig_pie.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=330, margin=dict(t=20, b=10, l=10, r=10))
                    st.plotly_chart(fig_pie, use_container_width=True)
                    st.markdown('<div class="chart-description"><b>Gasto por Departamento:</b> Muestra qué porcentaje del presupuesto total de nómina mensual se asigna a cada una de las áreas funcionales de la empresa.</div>', unsafe_allow_html=True)
                else:
                    st.info("Añade la columna 'Departamento' en el archivo para ver este análisis.")
            
            with col_dash2:
                col_genero = next((c for c in df.columns if 'genero' in c or 'género' in c or 'sexo' in c), None)
                if col_genero:
                    st.markdown("#### ⚖️ Equidad Salarial por Género (Brecha)")
                    fig_gender = px.box(df, x=col_genero, y="salario_total", color=col_genero,
                                        color_discrete_sequence=['#48BB78', '#FF4B4B'],
                                        labels={"salario_total": "Salario Total ($)", col_genero: "Género"})
                    fig_gender.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=330, margin=dict(t=20, b=10, l=10, r=10))
                    st.plotly_chart(fig_gender, use_container_width=True)
                    st.markdown('<div class="chart-description"><b>Distribución Salarial de Género:</b> Permite contrastar la dispersión de ingresos entre hombres y mujeres para auditar que no existan brechas injustificadas de compensación.</div>', unsafe_allow_html=True)
                else:
                    st.info("Añade la columna 'Género' en el archivo para visualizar brechas.")
            
            # --- NUEVA MATRIZ DE TALENTO INTERACTIVA (DESEMPEÑO VS COMPA-RATIO) (Altura: 420px) ---
            col_desempeno = next((c for c in df.columns if 'desempeño' in c or 'evaluacion' in c or 'rating' in c), None)
            if col_desempeno:
                st.markdown("---")
                st.markdown("#### 🎯 Matriz Estratégica: Desempeño vs. Posición Salarial (Compa-Ratio)")
                
                # Calcular medianas para todos los cargos y agregarlas al df
                medianas_df = df.groupby('cargo')['salario_total'].median().reset_index()
                medianas_df.rename(columns={'salario_total': 'mediana_cargo_global'}, inplace=True)
                df_matrix = df.merge(medianas_df, on='cargo', how='left')
                df_matrix['compa_ratio_global'] = df_matrix['salario_total'] / df_matrix['mediana_cargo_global']
                
                # Gráfica de matriz
                fig_matrix = px.scatter(
                    df_matrix, x=col_desempeno, y="compa_ratio_global", color="cargo",
                    hover_data=["trabajador", "salario_total"],
                    labels={"compa_ratio_global": "Compa-Ratio (Salario / Mediana)", col_desempeno: "Desempeño (Calificación)"},
                    title="Matriz de Retención: Identifica Riesgos de Fuga e Ineficiencias"
                )
                
                # Líneas divisorias de la matriz de decisión (Desempeño medio = 3.5, Compa-ratio ideal = 1.0)
                fig_matrix.add_hline(y=1.0, line_dash="dash", line_color="rgba(255,255,255,0.4)")
                fig_matrix.add_vline(x=3.5, line_dash="dash", line_color="rgba(255,255,255,0.4)")
                
                # Agregar etiquetas a los 4 cuadrantes
                fig_matrix.add_annotation(x=1.5, y=1.35, text="⚠️ Ineficiencia Salarial", showarrow=False, font=dict(color="rgba(245,101,101,0.8)", size=12))
                fig_matrix.add_annotation(x=4.5, y=1.35, text="⭐ Estrella Clave", showarrow=False, font=dict(color="rgba(72,187,120,0.8)", size=12))
                fig_matrix.add_annotation(x=1.5, y=0.65, text="📈 En Desarrollo", showarrow=False, font=dict(color="rgba(160,174,192,0.8)", size=12))
                fig_matrix.add_annotation(x=4.5, y=0.65, text="🏃‍♂️ RIESGO DE FUGA", showarrow=False, font=dict(color="rgba(237,137,54,0.9)", size=12))
                
                fig_matrix.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=420, margin=dict(t=20, b=10, l=10, r=10))
                st.plotly_chart(fig_matrix, use_container_width=True)
                st.markdown('<div class="chart-description"><b>Matriz de Posición vs Desempeño:</b> Cruza el mérito con la compensación. Destaca de inmediato a las personas con alto desempeño y bajo sueldo para planes de retención urgentes.</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
        st.info("Asegúrate de que el archivo tenga un formato tabular con encabezados claros en la primera fila.")

else:
    st.info("👈 Sube tu base de datos salarial en el panel lateral izquierdo para comenzar.")
    
    # Mostrar dataset de ejemplo esperado
    st.markdown("#### Formato de archivo esperado:")
    ejemplo = pd.DataFrame({
        "Trabajador": ["Juan Perez", "Maria Gomez", "Carlos Diaz"],
        "Cargo": ["Analista Financiero", "Analista Financiero", "Gerente"],
        "Departamento": ["Finanzas", "Finanzas", "Finanzas"],
        "Género": ["M", "F", "M"],
        "Desempeño": [4, 5, 3],
        "Antigüedad": [2, 5, 10],
        "Edad": [28, 32, 45],
        "Salario Base": [1200, 1400, 3000],
        "HE 25%": [50, 0, 0],
        "HE 50%": [0, 100, 0]
    })
    st.dataframe(ejemplo)
