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
        tab1, tab2 = st.tabs(["👤 Análisis Individual (Simulador)", "🏢 Dashboard Global (Empresa)"])
        
        with tab1:
            st.markdown("### Simulador de Incremento para: **{}**".format(trabajador_seleccionado.title()))
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
            
            # Gráficos Individuales
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                st.markdown("#### 📊 Equidad Interna: Rango Salarial")
                df_pares = df[df['cargo'].str.lower() == cargo_empleado.lower()]
                fig_box = px.box(df_pares, y="salario_total", points="all", hover_data=["trabajador"],
                                 labels={"salario_total": "Salario Total ($)"},
                                 color_discrete_sequence=['#00D2D3'])
                fig_box.add_hline(y=analisis['salario_propuesto'], line_dash="dash", line_color="#FF4B4B", annotation_text="Propuesto")
                fig_box.add_hline(y=salario_actual, line_dash="solid", line_color="#FFA500", annotation_text="Actual")
                fig_box.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=350)
                st.plotly_chart(fig_box, use_container_width=True)

            with col_graf2:
                st.markdown("#### 📈 Antigüedad vs Salario (Mismo Cargo)")
                col_antiguedad = next((c for c in df.columns if 'antig' in c or 'año' in c or 'year' in c), None)
                if col_antiguedad:
                    fig_scatter = px.scatter(df_pares, x=col_antiguedad, y="salario_total", text="trabajador",
                                             size="salario_total", color="salario_total",
                                             labels={col_antiguedad: "Antigüedad", "salario_total": "Salario Total ($)"})
                    fig_scatter.add_trace(go.Scatter(
                        x=[datos_empleado[col_antiguedad]], y=[salario_actual], mode='markers+text',
                        marker=dict(color='#FF4B4B', size=15, symbol='star'), text=['Actual'], name="Trabajador Evaluado"
                    ))
                    fig_scatter.update_traces(textposition='bottom center')
                    fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=350)
                    st.plotly_chart(fig_scatter, use_container_width=True)
                else:
                    st.warning("No se encontró columna de antigüedad.")
            
            # Conclusión
            st.markdown("#### 🤖 Conclusión del Asistente")
            if metricas_cargo:
                if analisis['salario_propuesto'] > metricas_cargo['max']:
                    st.error(f"⚠️ **Alerta:** El salario propuesto (${analisis['salario_propuesto']:,.2f}) superaría el máximo actual pagado para este cargo (${metricas_cargo['max']:,.2f}). Podría generar inequidad interna.")
                elif analisis['salario_propuesto'] < metricas_cargo['mediana']:
                    st.success(f"✅ **Viable:** El salario propuesto (${analisis['salario_propuesto']:,.2f}) se mantiene por debajo de la mediana del cargo (${metricas_cargo['mediana']:,.2f}). Es un ajuste seguro.")
                else:
                    st.info(f"ℹ️ **Observación:** El salario propuesto se encuentra dentro del rango competitivo superior para este cargo.")
                
                if aumento_solicitado <= inflacion:
                    st.warning(f"⚠️ El incremento solicitado ({aumento_solicitado}%) no supera la inflación ({inflacion}%). El empleado perderá poder adquisitivo real.")

        with tab2:
            st.markdown("### 🏢 Análisis Global de la Organización")
            
            # KPIs globales
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Empleados", len(df))
            m2.metric("Costo Nómina Mensual", f"${df['salario_total'].sum():,.2f}")
            m3.metric("Promedio Salarial", f"${df['salario_total'].mean():,.2f}")
            m4.metric("Cargos Distintos", df['cargo'].nunique())
            
            st.markdown("---")
            
            col_dash1, col_dash2 = st.columns(2)
            
            with col_dash1:
                # Si existe columna de departamento
                col_dpto = next((c for c in df.columns if 'departamento' in c or 'area' in c or 'área' in c), None)
                if col_dpto:
                    st.markdown("#### 📊 Distribución Salarial por Departamento")
                    df_dpto = df.groupby(col_dpto)['salario_total'].sum().reset_index()
                    fig_pie = px.pie(df_dpto, values='salario_total', names=col_dpto, hole=0.4,
                                     color_discrete_sequence=px.colors.sequential.Teal)
                    fig_pie.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=350)
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Añade una columna 'Departamento' para ver distribución por áreas.")
            
            with col_dash2:
                # Si existe columna de género
                col_genero = next((c for c in df.columns if 'genero' in c or 'género' in c or 'sexo' in c), None)
                if col_genero:
                    st.markdown("#### ⚖️ Equidad por Género (Brecha Salarial)")
                    fig_gender = px.box(df, x=col_genero, y="salario_total", color=col_genero,
                                        labels={"salario_total": "Salario Total ($)", col_genero: "Género"})
                    fig_gender.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=350)
                    st.plotly_chart(fig_gender, use_container_width=True)
                else:
                    st.info("Añade una columna 'Género' para visualizar la equidad de género.")
            
            # Matriz de Desempeño si existe la columna
            col_desempeno = next((c for c in df.columns if 'desempeño' in c or 'evaluacion' in c or 'rating' in c), None)
            if col_desempeno:
                st.markdown("---")
                st.markdown("#### ⭐ Matriz: Desempeño vs. Remuneración")
                fig_perf = px.scatter(df, x=col_desempeno, y="salario_total", color="cargo", size="salario_total",
                                      hover_data=["trabajador"],
                                      labels={"salario_total": "Salario Total ($)", col_desempeno: "Calificación de Desempeño"})
                fig_perf.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=400)
                st.plotly_chart(fig_perf, use_container_width=True)

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
