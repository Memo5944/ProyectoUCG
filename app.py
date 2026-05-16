import streamlit as st
import pandas as pd
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

# Estilo CSS personalizado para un look "Premium"
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
    }
    .stMetric {
        background-color: #1E2127;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    h1, h2, h3 {
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

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
        
        st.markdown("---")
        st.subheader(f"Análisis para: **{trabajador_seleccionado.title()}**")
        st.markdown(f"**Cargo:** {cargo_empleado.title()} | **Antigüedad:** {datos_empleado.get('antigüedad', 'N/D')} años")
        
        # Cálculos
        analisis = lf.evaluar_incremento(salario_actual, aumento_solicitado, inflacion)
        metricas_cargo = lf.obtener_metricas_cargo(df, cargo_empleado)
        
        # Fila de Métricas Principales (KPIs)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Salario Total Actual", f"${salario_actual:,.2f}")
        col2.metric(f"Salario Propuesto (+{aumento_solicitado}%)", f"${analisis['salario_propuesto']:,.2f}", f"+${analisis['aumento_real_monto']:,.2f}")
        col3.metric("Pérdida por Inflación", f"-${analisis['perdida_inflacion']:,.2f}", f"-{inflacion}%", delta_color="inverse")
        
        if metricas_cargo:
            col4.metric("Mediana del Cargo (Interna)", f"${metricas_cargo['mediana']:,.2f}")
        else:
            col4.metric("Mediana del Cargo", "N/D")

        st.markdown("---")
        
        # Gráficos
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.markdown("### 📊 Equidad Interna: Rango Salarial del Cargo")
            # Filtrar pares del mismo cargo
            df_pares = df[df['cargo'].str.lower() == cargo_empleado.lower()]
            
            fig_box = px.box(df_pares, y="salario_total", points="all", hover_data=["trabajador"],
                             title=f"Distribución Salarial: {cargo_empleado.title()}",
                             labels={"salario_total": "Salario Total ($)"},
                             color_discrete_sequence=['#00D2D3'])
            
            # Añadir línea del salario propuesto
            fig_box.add_hline(y=analisis['salario_propuesto'], line_dash="dash", line_color="red", 
                              annotation_text="Salario Propuesto", annotation_position="bottom right")
            
            # Añadir línea del salario actual
            fig_box.add_hline(y=salario_actual, line_dash="solid", line_color="orange", 
                              annotation_text="Salario Actual", annotation_position="top right")
                              
            fig_box.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig_box, use_container_width=True)

        with col_graf2:
            st.markdown("### 📈 Antigüedad vs Salario (Mismo Cargo)")
            # Asumiendo que la columna de antigüedad se llama 'antigüedad' o similar
            col_antiguedad = next((c for c in df.columns if 'antig' in c or 'año' in c or 'year' in c), None)
            
            if col_antiguedad:
                fig_scatter = px.scatter(df_pares, x=col_antiguedad, y="salario_total", text="trabajador",
                                         size="salario_total", color="salario_total",
                                         title=f"Dispersión: Experiencia vs Remuneración",
                                         labels={col_antiguedad: "Antigüedad", "salario_total": "Salario Total ($)"})
                
                # Resaltar al trabajador actual
                fig_scatter.add_trace(go.Scatter(
                    x=[datos_empleado[col_antiguedad]],
                    y=[salario_actual],
                    mode='markers+text',
                    marker=dict(color='red', size=15, symbol='star'),
                    text=['Actual'],
                    textposition="top center",
                    name="Trabajador Evaluado"
                ))
                
                fig_scatter.update_traces(textposition='bottom center')
                fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.warning("No se encontró una columna de antigüedad para generar este gráfico.")
        
        # Conclusión Automática
        st.markdown("### 🤖 Conclusión del Asistente")
        if metricas_cargo:
            if analisis['salario_propuesto'] > metricas_cargo['max']:
                st.error(f"⚠️ **Alerta:** El salario propuesto (${analisis['salario_propuesto']:,.2f}) superaría el máximo actual pagado para este cargo (${metricas_cargo['max']:,.2f}). Podría generar inequidad interna.")
            elif analisis['salario_propuesto'] < metricas_cargo['mediana']:
                st.success(f"✅ **Viable:** El salario propuesto (${analisis['salario_propuesto']:,.2f}) se mantiene por debajo de la mediana del cargo (${metricas_cargo['mediana']:,.2f}). Es un ajuste seguro y competitivo.")
            else:
                st.info(f"ℹ️ **Observación:** El salario propuesto se encuentra dentro del rango competitivo superior para este cargo.")
                
            if aumento_solicitado <= inflacion:
                st.warning(f"⚠️ El incremento solicitado ({aumento_solicitado}%) es igual o inferior a la inflación ({inflacion}%). En términos reales, el trabajador no ganará poder adquisitivo.")

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
        "Antigüedad": [2, 5, 10],
        "Edad": [28, 32, 45],
        "Salario Base": [1200, 1400, 3000],
        "HE 25%": [50, 0, 0],
        "HE 50%": [0, 100, 0]
    })
    st.dataframe(ejemplo)
