import re

app_path = r'c:\Users\aramos\Desktop\JAER\Maestria\Repositorio\Github\ProyectoUCG\app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove Sidebar Step 5 completely
sidebar_5_pattern = r'st\.sidebar\.markdown\("---"\)\s*st\.sidebar\.header\("🌍 5\. Benchmark de Mercado Externo"\).*?st\.sidebar\.caption\(f"📝 \*\*Origen del dato estimado:\*\* \{fuente_estimacion\}"\)'
text = re.sub(sidebar_5_pattern, '', text, flags=re.DOTALL)

# 2. Extract cargo and fetch new dict
fetch_code = """
        cargo_para_busqueda = str(datos_empleado.get('cargo', '')).strip()
        datos_mercado = lf.estimar_mercado_externo(cargo_para_busqueda, mediana_global)
        salario_mercado_estimado = datos_mercado['salario_estimado']
"""

# 3. Replace the old tab setup
old_tab_setup = r'st\.markdown\("<br>", unsafe_allow_html=True\)\s*tab1 = st\.container\(\)\s*df_pares_global = df\[df\[\'cargo\'\]\.str\.lower\(\)\.isin\(\[c\.lower\(\) for c in cargos_comparativa\]\)\]\s*with tab1:'

new_tab_setup = fetch_code + """

        st.markdown("<br>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["📊 1. Análisis Interno y Simulación", "🌍 2. Mercado Externo (Ecuador)"])
        
        df_pares_global = df[df['cargo'].str.lower().isin([c.lower() for c in cargos_comparativa])]

        with tab1:
"""
text = re.sub(old_tab_setup, new_tab_setup, text, flags=re.DOTALL)

# 4. Remove col_diag3 and adjust columns to 2
diag_cols_old = r'col_diag1, col_diag2, col_diag3 = st\.columns\(3\)'
text = text.replace(diag_cols_old, 'col_diag1, col_diag2 = st.columns(2)')

diag3_pattern = r'with col_diag3:.*?st\.markdown\("<hr style=\'border: 2px solid #f2c72e; margin: 50px 0;\'>", unsafe_allow_html=True\)'
text = re.sub(diag3_pattern, "st.markdown(\"<hr style='border: 2px solid #f2c72e; margin: 50px 0;'>\", unsafe_allow_html=True)", text, flags=re.DOTALL)

# 5. Build Tab 2 content
tab2_content = """

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
                html_ficha = f\"\"\"
                <div style="background: rgba(255,255,255,0.9); padding: 20px; border-radius: 12px; border-left: 5px solid #0b2659; box-shadow: 0 5px 15px rgba(0,0,0,0.05); color: #0b2659;">
                    <h4 style="margin-top: 0; color: #0b2659; font-weight: bold;">📑 Ficha Técnica Comercial (Ecuador)</h4>
                    <p style="margin-bottom: 5px;"><b>🏢 Empresas de Referencia:</b> {datos_mercado['empresa_referencia']}</p>
                    <p style="margin-bottom: 5px;"><b>📊 Fuentes Contrastadas:</b> {datos_mercado['fuente']}</p>
                    <p style="margin-bottom: 5px;"><b>✅ Nivel de Confianza:</b> {datos_mercado['confianza']}</p>
                    <hr style="border-top: 1px solid rgba(11, 38, 89, 0.2); margin: 10px 0;">
                    <p style="margin-bottom: 0; font-size: 0.9em; font-style: italic;">{datos_mercado['mensaje']}</p>
                </div>
                \"\"\"
                st.markdown(html_ficha, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### 🤖 Diagnóstico Estratégico frente a Competencia Nacional", unsafe_allow_html=True)
            
            if salario_mercado_externo > 0:
                diferencia_ext = analisis['salario_propuesto'] - salario_mercado_externo
                pct_ext = (diferencia_ext / salario_mercado_externo) * 100
                if pct_ext < -10:
                    st.error(f"📉 **Desventaja vs Ecuador:** Nuestra propuesta final (USD {analisis['salario_propuesto']:,.2f}) está **{abs(pct_ext):.1f}% por debajo** del mercado nacional (USD {salario_mercado_externo:,.0f}). \\n\\n⚠️ **Riesgo:** Alta probabilidad de perder a este perfil frente a competidores directos como **{datos_mercado['empresa_referencia']}**.")
                elif pct_ext > 10:
                    st.warning(f"📈 **Por Encima del Mercado:** La propuesta está **{pct_ext:.1f}% superior** a la media nacional en Ecuador. \\n\\n🛡️ **Evaluación:** Estratégicamente garantiza alta retención de talento y exclusividad, pero incrementa costos operativos por encima del benchmark de la industria.")
                else:
                    st.success(f"🎯 **Alineación Perfecta (Ecuador):** Nuestra propuesta (USD {analisis['salario_propuesto']:,.2f}) es equilibrada y competitiva (**±10%**) frente a los estándares manejados por referentes como **{datos_mercado['empresa_referencia']}**.")
            else:
                 st.info("ℹ️ Investiga e ingresa el salario de mercado para obtener un diagnóstico externo.")

"""

text = text.replace("        # Dashboard Global removido según requerimiento", tab2_content + "\n        # Dashboard Global removido según requerimiento")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated app.py successfully!")
