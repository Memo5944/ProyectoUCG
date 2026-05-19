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

        # Sidebar - Selección de Trabajadores
        st.sidebar.header("👤 2. Seleccionar Trabajadores")
        nombres_trabajadores = df['trabajador'].dropna().unique().tolist()
        trabajadores_seleccionados = st.sidebar.multiselect(
            "Buscar empleado(s) solicitante(s):", 
            nombres_trabajadores, 
            default=[nombres_trabajadores[0]] if nombres_trabajadores else []
        )
        
        if not trabajadores_seleccionados:
            st.warning("👈 Por favor, selecciona al menos un empleado en el panel izquierdo.")
            st.stop()
            
        # Determinar cargos de los seleccionados para default
        cargos_default = df[df['trabajador'].isin(trabajadores_seleccionados)]['cargo'].unique().tolist()
        
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

        # Sidebar - Parámetros de Simulación
        st.sidebar.header("📈 4. Parámetros de Simulación")
        inflacion = st.sidebar.number_input("Inflación Anual Esperada (%)", min_value=0.0, max_value=100.0, value=3.0, step=0.1)
        aumento_solicitado = st.sidebar.slider("Incremento a simular (%)", min_value=0.0, max_value=50.0, value=5.0, step=0.5)

        # -- MAIN DASHBOARD --
        
        st.markdown("---")
        st.subheader("👥 Análisis Individual de Solicitantes")
        
        metricas_comparativa = lf.obtener_metricas_cargos_multiples(df, cargos_comparativa)
        
        # Guardar info de salarios propuestos para los gráficos
        dict_salarios_propuestos = {}

        for trabajador in trabajadores_seleccionados:
            datos_empleado = df[df['trabajador'] == trabajador].iloc[0]
            cargo_empleado = datos_empleado['cargo']
            salario_actual = datos_empleado.get('salario_total', 0)
            
            analisis = lf.evaluar_incremento(salario_actual, aumento_solicitado, inflacion)
            dict_salarios_propuestos[trabajador] = analisis['salario_propuesto']
            
            with st.container():
                st.markdown(f"#### **{trabajador.title()}**")
                st.markdown(f"**Cargo:** {cargo_empleado.title()} | **Antigüedad:** {datos_empleado.get('antigüedad', 'N/D')} años")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Salario Total Actual", f"${salario_actual:,.2f}")
                col2.metric(f"Propuesto (+{aumento_solicitado}%)", f"${analisis['salario_propuesto']:,.2f}", f"+${analisis['aumento_real_monto']:,.2f}")
                col3.metric("Pérdida por Inflación", f"-${analisis['perdida_inflacion']:,.2f}", f"-{inflacion}%", delta_color="inverse")
                
                if metricas_comparativa:
                    col4.metric("Mediana Comparativa", f"${metricas_comparativa['mediana']:,.2f}")
                else:
                    col4.metric("Mediana Comparativa", "N/D")
            st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("---")
        
        # Gráficos
        col_graf1, col_graf2 = st.columns(2)
        
        # Filtrar pares de los cargos seleccionados
        df_pares = df[df['cargo'].str.lower().isin([c.lower() for c in cargos_comparativa])]
        
        with col_graf1:
            st.markdown("### 📊 Equidad Interna: Rango Salarial")
            
            fig_box = px.box(df_pares, x="cargo", y="salario_total", points="all", hover_data=["trabajador"],
                             title="Distribución Salarial por Cargo",
                             labels={"salario_total": "Salario Total ($)", "cargo": "Cargo"},
                             color="cargo")
            
            # Añadir a los trabajadores seleccionados como estrellas rojas
            df_seleccionados = df[df['trabajador'].isin(trabajadores_seleccionados)]
            if not df_seleccionados.empty:
                fig_box.add_trace(go.Scatter(
                    x=df_seleccionados['cargo'],
                    y=df_seleccionados['salario_total'],
                    mode='markers',
                    marker=dict(color='red', size=12, symbol='star', line=dict(width=1, color='white')),
                    name="Actuales (Seleccionados)",
                    hovertext=df_seleccionados['trabajador'],
                    hoverinfo="text+y"
                ))
                
                # Añadir propuestos como diamantes
                salarios_prop = [dict_salarios_propuestos[t] for t in df_seleccionados['trabajador']]
                fig_box.add_trace(go.Scatter(
                    x=df_seleccionados['cargo'],
                    y=salarios_prop,
                    mode='markers',
                    marker=dict(color='orange', size=10, symbol='diamond', line=dict(width=1, color='white')),
                    name=f"Propuestos (+{aumento_solicitado}%)",
                    hovertext=df_seleccionados['trabajador'],
                    hoverinfo="text+y"
                ))
                              
            fig_box.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig_box, use_container_width=True)

        with col_graf2:
            st.markdown("### 📈 Antigüedad vs Salario")
            col_antiguedad = next((c for c in df.columns if 'antig' in c or 'año' in c or 'year' in c), None)
            
            if col_antiguedad:
                fig_scatter = px.scatter(df_pares, x=col_antiguedad, y="salario_total", text="trabajador",
                                         color="cargo",
                                         title="Dispersión: Experiencia vs Remuneración",
                                         labels={col_antiguedad: "Antigüedad", "salario_total": "Salario Total ($)", "cargo": "Cargo"})
                
                if not df_seleccionados.empty:
                    # Resaltar a los trabajadores seleccionados
                    fig_scatter.add_trace(go.Scatter(
                        x=df_seleccionados[col_antiguedad],
                        y=df_seleccionados['salario_total'],
                        mode='markers+text',
                        marker=dict(color='red', size=15, symbol='star', line=dict(width=2, color='white')),
                        text=df_seleccionados['trabajador'],
                        textposition="top center",
                        name="Seleccionados"
                    ))
                
                fig_scatter.update_traces(textposition='bottom center')
                fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.warning("No se encontró una columna de antigüedad para generar este gráfico.")
        
        # Conclusión Automática
        st.markdown("### 🤖 Conclusión del Asistente")
        if metricas_comparativa:
            for trabajador in trabajadores_seleccionados:
                sal_propuesto = dict_salarios_propuestos[trabajador]
                if sal_propuesto > metricas_comparativa['max']:
                    st.error(f"⚠️ **Alerta ({trabajador.title()}):** El salario propuesto (${sal_propuesto:,.2f}) superaría el máximo actual pagado en la comparativa (${metricas_comparativa['max']:,.2f}). Podría generar inequidad interna.")
                elif sal_propuesto < metricas_comparativa['mediana']:
                    st.success(f"✅ **Viable ({trabajador.title()}):** El salario propuesto (${sal_propuesto:,.2f}) se mantiene por debajo de la mediana comparativa (${metricas_comparativa['mediana']:,.2f}). Es un ajuste seguro y competitivo.")
                else:
                    st.info(f"ℹ️ **Observación ({trabajador.title()}):** El salario propuesto se encuentra dentro del rango competitivo superior para los cargos comparados.")
            
            if aumento_solicitado <= inflacion:
                st.warning(f"⚠️ El incremento solicitado ({aumento_solicitado}%) es igual o inferior a la inflación ({inflacion}%). En términos reales, el/los trabajador(es) no ganarán poder adquisitivo.")

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
