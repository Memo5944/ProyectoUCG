import codecs
import re

# 1. FIX LIBRERIA FUNCIONES URLS FOR REAL
lf_path = r'c:\Users\aramos\Desktop\JAER\Maestria\Repositorio\Github\ProyectoUCG\libreria_funciones.py'
with codecs.open(lf_path, 'r', 'utf-8') as f:
    lf_text = f.read()

# Make all URLs point to generic valid portals instead of specific 404 pages
lf_text = re.sub(r"'https://www\.glassdoor\.com/Salary/[^']*'", "'https://www.glassdoor.com/Reviews/index.htm'", lf_text)
lf_text = re.sub(r"'https://www\.glassdoor\.com/Salaries/[^']*'", "'https://www.glassdoor.com/Reviews/index.htm'", lf_text)
lf_text = re.sub(r"'https://hireline\.io/salarios/.*?'", "'https://hireline.io/ec/salarios'", lf_text)
lf_text = re.sub(r"'https://www\.computrabajo\.com\.ec/salarios/.*?'", "'https://www.computrabajo.com.ec/salarios'", lf_text)

with codecs.open(lf_path, 'w', 'utf-8') as f:
    f.write(lf_text)

# 2. RESTORE DIAGNOSTIC TO TAB 1 (col_diag3)
app_path = r'c:\Users\aramos\Desktop\JAER\Maestria\Repositorio\Github\ProyectoUCG\app.py'
with codecs.open(app_path, 'r', 'utf-8') as f:
    app_text = f.read()

# Find the end of col_diag2 and insert col_diag3
diag2_end_pattern = r'st\.success\(f"✅ \*\*Alineado \(CR: \{compa_ratio_actual:\.2f\}\):\*\* El salario base es competitivo frente a sus colegas\."\)'
diag3_block = """
            with col_diag3:
                st.markdown("##### 🌍 Mercado Local (Ecuador)")
                if salario_mercado_estimado > 0:
                    diferencia_ext = analisis['salario_propuesto'] - salario_mercado_estimado
                    pct_ext = (diferencia_ext / salario_mercado_estimado) * 100
                    if pct_ext < -10:
                        st.error(f"📉 **Desventaja vs EC:** Propuesta (USD {analisis['salario_propuesto']:,.2f}) está **{abs(pct_ext):.1f}% debajo** del mercado nacional (USD {salario_mercado_estimado:,.0f}). Riesgo pérdida frente a {datos_mercado['empresa_referencia']}")
                    elif pct_ext > 10:
                        st.warning(f"📈 **Media Superior:** Propuesta es **{pct_ext:.1f}% encima** del mercado Ecuador. Garantiza retención de talento pero eleva costos.")
                    else:
                        st.success(f"🎯 **Alineado EC:** Propuesta muy competitiva y equilibrada (±10%) frente a {datos_mercado['empresa_referencia']}.")
                else:
                    st.info("ℹ️ Carga un cargo compatible para medir su benchmark.")
"""

if "with col_diag3:" not in app_text and "##### 🌍 Mercado Local (Ecuador)" not in app_text:
    app_text = app_text.replace('st.success(f"✅ **Alineado (CR: {compa_ratio_actual:.2f}):** El salario base es competitivo frente a sus colegas.")', 
                                'st.success(f"✅ **Alineado (CR: {compa_ratio_actual:.2f}):** El salario base es competitivo frente a sus colegas.")\n' + diag3_block)

with codecs.open(app_path, 'w', 'utf-8') as f:
    f.write(app_text)

print("V6 Applied successfully")
