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
    /* Fondo llamativo premium (Deep Ocean Gradient) */
    .stApp {
        background: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
    }
    .main {
        background: transparent;
    }
    h1, h2, h3, h4, p, span, div, label {
        color: #E2E8F0 !important;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    h1 {
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #00D2D3, #48BB78);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    
    /* Estilos Premium para Tarjetas de KPI */
    .kpi-container {
        display: flex;
        gap: 20px;
        margin-bottom: 25px;
    }
    .kpi-card {
        background: rgba(15, 23, 42, 0.5);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        width: 100%;
        height: 140px; /* Altura fija uniforme */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
        margin-bottom: 20px;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 255, 255, 0.3);
        box-shadow: 0 20px 40px -10px rgba(0, 210, 211, 0.25);
    }
    .kpi-title {
        font-size: 0.85rem;
        color: #94A3B8 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #F8FAFC !important;
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
        color: #10B981 !important;
        background: rgba(16, 185, 129, 0.15);
    }
    .delta-neg {
        color: #EF4444 !important;
        background: rgba(239, 68, 68, 0.15);
    }
    
    /* Elegante caja de descripción para los gráficos */
    .chart-description {
        font-size: 0.85rem;
        color: #CBD5E0 !important;
        margin-top: 15px;
        margin-bottom: 30px;
        line-height: 1.6;
        background: rgba(15, 23, 42, 0.4);
        padding: 15px 20px;
        border-radius: 10px;
        border-left: 4px solid #00D2D3;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.1);
    }
    
    /* Fix global margins for columns */
    div[data-testid="column"] {
        padding: 0 10px;
    }
    </style>
""", unsafe_allow_html=True)

def render_kpi_card(title, value, delta=None, delta_type="positive", border_color="#00D2D3"):
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

st.title("💼 Bot de Análisis Salarial")
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

        st.sidebar.header("👤 2. Seleccionar Trabajador")
        nombres_trabajadores = df['trabajador'].dropna().unique().tolist()
        trabajador_seleccionado = st.sidebar.selectbox("Buscar empleado solicitante:", nombres_trabajadores)
        
        datos_empleado = df[df['trabajador'] == trabajador_seleccionado].iloc[0]
        cargo_empleado = datos_empleado['cargo']
        salario_actual = datos_empleado.get('salario_total', 0)
        
        # Sidebar - Parámetros de Simulación
        st.sidebar.header("📈 3. Parámetros de Simulación")
        inflacion = st.sidebar.number_input("Inflación Anual Esperada (%)", min_value=0.0, max_value=100.0, value=3.0, step=0.1)
        
        # Calcular incremento sugerido
        sugerencia = inflacion
        st.sidebar.markdown(f"💡 **El sistema sugiere un incremento base de {sugerencia:.1f}%** alineado a la inflación esperada.")
        aumento_solicitado = st.sidebar.slider("Incremento a simular (%)", min_value=0.0, max_value=50.0, value=float(sugerencia), step=0.5)

        st.markdown("<br>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["👤 Análisis Individual (Simulador)", "🏢 Dashboard Global (Empresa)"])
        
        with tab1:
            st.markdown(f"### Simulador de Incremento para: **{trabajador_seleccionado.title()}**")
            st.markdown(f"**Cargo:** {cargo_empleado.title()} | **Antigüedad:** {datos_empleado.get('antigüedad', 'N/D')} años")
            st.markdown("<br>", unsafe_allow_html=True)
            
            analisis = lf.evaluar_incremento(salario_actual, aumento_solicitado, inflacion)
            metricas_cargo = lf.obtener_metricas_cargo(df, cargo_empleado)
            
            mediana_cargo = metricas_cargo['mediana'] if metricas_cargo else 0
            compa_ratio_actual = lf.calcular_compa_ratio(salario_actual, mediana_cargo)
            compa_ratio_propuesto = lf.calcular_compa_ratio(analisis['salario_propuesto'], mediana_cargo)
            
            # Fila de KPIs
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(render_kpi_card("Salario Actual", f"USD {salario_actual:,.2f}", border_color="#00D2D3"), unsafe_allow_html=True)
            with c2:
                st.markdown(render_kpi_card("Salario Propuesto", f"USD {analisis['salario_propuesto']:,.2f}", f"+{aumento_solicitado}% (+USD {analisis['aumento_real_monto']:,.2f})", delta_type="positive", border_color="#48BB78"), unsafe_allow_html=True)
            with c3:
                st.markdown(render_kpi_card("Pérdida por Inflación", f"-USD {analisis['perdida_inflacion']:,.2f}", f"-{inflacion}%", delta_type="negative", border_color="#F56565"), unsafe_allow_html=True)
            with c4:
                val_mediana = f"USD {mediana_cargo:,.2f}" if mediana_cargo > 0 else "N/D"
                st.markdown(render_kpi_card("Mediana del Cargo", val_mediana, border_color="#F59E0B"), unsafe_allow_html=True)

            st.markdown("---")
            
            col_antiguedad = next((c for c in df.columns if 'antig' in c or 'año' in c or 'year' in c), None)
            
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                st.markdown("#### 📊 Equidad Interna y Compa-Ratio")
                # Velocímetro
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = compa_ratio_actual,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Compa-Ratio Actual", 'font': {'size': 14, 'color': "#E2E8F0"}},
                    number = {'valueformat': ".2f", 'font': {'color': "#F8FAFC", 'size': 32}},
                    gauge = {
                        'axis': {'range': [0.5, 1.5], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': "#00D2D3"},
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
                fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#E2E8F0", height=240, margin=dict(t=30, b=10, l=20, r=20))
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                # Gráfico de Barras Comparativo (Reemplazo del Box Plot)
                df_pares = df[df['cargo'].str.lower() == cargo_empleado.lower()].sort_values('salario_total', ascending=False)
                
                # Resaltar al evaluado con otro color
                df_pares['Color'] = ['#FF4B4B' if t == trabajador_seleccionado else '#00D2D3' for t in df_pares['trabajador']]
                
                fig_bar = px.bar(df_pares, x="trabajador", y="salario_total", 
                                 text="salario_total",
                                 color="Color", color_discrete_map="identity",
                                 labels={"trabajador": "Empleado", "salario_total": "Salario (USD)"})
                
                fig_bar.update_traces(texttemplate='USD %{text:,.0f}', textposition='outside')
                fig_bar.add_hline(y=analisis['salario_propuesto'], line_dash="dash", line_color="#FF4B4B", annotation_text="Propuesto")
                fig_bar.add_hline(y=mediana_cargo, line_dash="solid", line_color="#F59E0B", annotation_text="Mediana")
                
                fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#E2E8F0", height=260, margin=dict(t=20, b=20, l=10, r=10))
                fig_bar.update_yaxes(gridcolor="rgba(255,255,255,0.1)", range=[0, max(df_pares['salario_total'].max(), analisis['salario_propuesto']) * 1.25])
                st.plotly_chart(fig_bar, use_container_width=True)
                
                st.markdown('<div class="chart-description"><b>Comparativa de Salarios:</b> Muestra lo que ganan todos los empleados en el mismo cargo. La barra roja eres tú. La línea punteada marca adónde llegará tu sueldo con el aumento.</div>', unsafe_allow_html=True)

                # Cuadro Comparativo (Ranking)
                st.markdown("#### 📋 Cuadro Comparativo de Pares (Ranking Salarial)")
                
                cols_to_select = ['trabajador']
                if col_antiguedad: cols_to_select.append(col_antiguedad)
                cols_to_select.append('salario_total')
                
                df_comparativo = df_pares[cols_to_select].copy()
                df_comparativo['Salario Nuevo'] = df_comparativo['salario_total'].astype(float)
                df_comparativo.loc[df_comparativo['trabajador'] == trabajador_seleccionado, 'Salario Nuevo'] = float(analisis['salario_propuesto'])
                
                columnas_finales = ['Empleado']
                if col_antiguedad: columnas_finales.append('Años')
                columnas_finales.extend(['Salario Actual', 'Salario Nuevo'])
                
                df_comparativo.columns = columnas_finales
                
                if 'Años' in df_comparativo.columns:
                    df_comparativo['Años'] = df_comparativo['Años'].round(1)
                    
                df_comparativo = df_comparativo.sort_values('Salario Nuevo', ascending=False).reset_index(drop=True)
                
                def highlight_selected(row):
                    if row['Empleado'] == trabajador_seleccionado:
                        return ['background-color: rgba(239, 68, 68, 0.2); color: white; font-weight: bold'] * len(row)
                    return [''] * len(row)
                    
                st.dataframe(df_comparativo.style.apply(highlight_selected, axis=1).format({
                    'Salario Actual': '${:,.2f}',
                    'Salario Nuevo': '${:,.2f}'
                }), use_container_width=True)
                st.markdown('<div class="chart-description"><b>Ranking Post-Aumento:</b> Simula la nueva jerarquía salarial dentro de tu cargo. Permite validar que tu nuevo sueldo sea justo frente a colegas con mayor desempeño o experiencia.</div>', unsafe_allow_html=True)

            with col_graf2:
                st.markdown("#### 📈 Antigüedad vs Salario con Línea de Tendencia")
                if col_antiguedad:
                    # Scatter simplificado sin barra de color para evitar solapamientos
                    fig_scatter = px.scatter(df_pares, x=col_antiguedad, y="salario_total", text="trabajador",
                                             size="salario_total",
                                             labels={col_antiguedad: "Antigüedad (Años)", "salario_total": "Salario Total (USD)"})
                    fig_scatter.update_traces(marker=dict(color='#00D2D3', opacity=0.7), textposition='top center')
                    
                    x_vals = df_pares[col_antiguedad].values
                    y_vals = df_pares['salario_total'].values
                    if len(x_vals) > 1:
                        m, c = np.polyfit(x_vals, y_vals, 1)
                        x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
                        y_line = m * x_line + c
                        
                        fig_scatter.add_trace(go.Scatter(
                            x=x_line, y=y_line, mode='lines',
                            line=dict(color='rgba(255, 255, 255, 0.6)', dash='dash'),
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
                    
                    # Resaltar evaluado (texto explícito y claro)
                    fig_scatter.add_trace(go.Scatter(
                        x=[datos_empleado[col_antiguedad]], y=[salario_actual], mode='markers+text',
                        marker=dict(color='#EF4444', size=22, symbol='star', line=dict(color='white', width=2)),
                        text=[f"Eval: {trabajador_seleccionado}"], textposition="bottom center", name="Evaluado",
                        textfont=dict(color="#EF4444", size=12, weight="bold")
                    ))
                    
                    fig_scatter.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)", 
                        paper_bgcolor="rgba(0,0,0,0)", 
                        font_color="#E2E8F0", 
                        height=500, 
                        margin=dict(t=20, b=20, l=20, r=20),
                        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0.5)")
                    )
                    fig_scatter.update_xaxes(gridcolor="rgba(255,255,255,0.1)")
                    fig_scatter.update_yaxes(gridcolor="rgba(255,255,255,0.1)")
                    st.plotly_chart(fig_scatter, use_container_width=True)
                    
                    st.markdown('<div class="chart-description"><b>Curva de Experiencia:</b> Mapea la relación entre antigüedad laboral y salario sin barra de color extra. La zona sombreada marca el rango aceptable. Puntos por fuera requieren atención.</div>', unsafe_allow_html=True)
                else:
                    st.warning("No se encontró columna de antigüedad para la tendencia.")
            
            st.markdown("#### 🤖 Diagnóstico Salarial Estratégico")
            col_diag1, col_diag2 = st.columns(2)
            with col_diag1:
                if metricas_cargo:
                    # IMPORTANTE: Reemplazar $ por USD para evitar error de renderizado LaTeX en Streamlit
                    if analisis['salario_propuesto'] > metricas_cargo['max']:
                        st.error(f"⚠️ Alerta de Inequidad: El salario propuesto (USD {analisis['salario_propuesto']:,.2f}) superaría el máximo actual pagado para este cargo (USD {metricas_cargo['max']:,.2f}). Podría generar tensión interna.")
                    elif analisis['salario_propuesto'] < metricas_cargo['mediana']:
                        st.success(f"✅ Viable en Equidad: El salario propuesto (USD {analisis['salario_propuesto']:,.2f}) se mantiene por debajo de la mediana del cargo (USD {metricas_cargo['mediana']:,.2f}). Es un ajuste seguro.")
                    else:
                        st.info(f"ℹ️ Posicionamiento Competitivo: El salario propuesto se encuentra en el rango superior competitivo del mercado interno.")
            
            with col_diag2:
                if compa_ratio_actual < 0.8:
                    st.warning(f"⚠️ Alerta de Retención (Compa-Ratio: {compa_ratio_actual:.2f}): El empleado está subpagado con respecto a sus compañeros. Un aumento es recomendado para evitar fuga de talento.")
                elif compa_ratio_actual > 1.2:
                    st.info(f"ℹ️ Alta Inversión (Compa-Ratio: {compa_ratio_actual:.2f}): El empleado está altamente compensado. Asegúrate de que su desempeño justifique este nivel.")
                else:
                    st.success(f"✅ Alineación de Mercado (Compa-Ratio: {compa_ratio_actual:.2f}): El salario del empleado es competitivo y está bien alineado.")

        with tab2:
            st.markdown("### 🏢 Dashboard de Compensación Organizacional")
            st.markdown("<br>", unsafe_allow_html=True)
            
            g1, g2, g3, g4 = st.columns(4)
            with g1:
                st.markdown(render_kpi_card("Total Empleados", len(df), border_color="#00D2D3"), unsafe_allow_html=True)
            with g2:
                st.markdown(render_kpi_card("Nómina Total Mensual", f"USD {df['salario_total'].sum():,.2f}", border_color="#48BB78"), unsafe_allow_html=True)
            with g3:
                st.markdown(render_kpi_card("Promedio Salarial", f"USD {df['salario_total'].mean():,.2f}", border_color="#F59E0B"), unsafe_allow_html=True)
            with g4:
                st.markdown(render_kpi_card("Cargos Distintos", f"{df['cargo'].nunique()}", border_color="#8B5CF6"), unsafe_allow_html=True)
            
            st.markdown("---")
            
            col_dash1, col_dash2 = st.columns(2)
            
            with col_dash1:
                col_dpto = next((c for c in df.columns if 'departamento' in c or 'area' in c or 'área' in c), None)
                if col_dpto:
                    st.markdown("#### 📊 Distribución de Nómina por Departamento")
                    df_dpto = df.groupby(col_dpto)['salario_total'].sum().reset_index()
                    fig_pie = px.pie(df_dpto, values='salario_total', names=col_dpto, hole=0.6,
                                     color_discrete_sequence=px.colors.sequential.Mint)
                    fig_pie.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#E2E8F0", height=350, margin=dict(t=20, b=10, l=10, r=10))
                    st.plotly_chart(fig_pie, use_container_width=True)
                    st.markdown('<div class="chart-description"><b>Gasto por Departamento:</b> Muestra qué porcentaje del presupuesto total de nómina mensual se asigna a cada una de las áreas funcionales de la empresa.</div>', unsafe_allow_html=True)
                else:
                    st.info("Añade la columna 'Departamento' en el archivo para ver este análisis.")
            
            with col_dash2:
                st.info("Espacio reservado para futuros análisis organizacionales.")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")

else:
    st.info("👈 Sube tu base de datos salarial en el panel lateral izquierdo para comenzar.")
    
    st.markdown("#### Formato de archivo esperado:")
    ejemplo = pd.DataFrame({
        "Trabajador": ["Juan Perez", "Maria Gomez", "Carlos Diaz"],
        "Cargo": ["Analista Financiero", "Analista Financiero", "Gerente"],
        "Departamento": ["Finanzas", "Finanzas", "Finanzas"],
        "Antigüedad": ["15/05/2021", "10/01/2019", "01/08/2013"],
        "Edad": [28, 32, 45],
        "Salario Base": [1200, 1400, 3000],
        "HE 25%": [50, 0, 0],
        "HE 50%": [0, 100, 0],
        "HE 100%": [0, 0, 150]
    })
    st.dataframe(ejemplo)
