import re
import codecs

# 1. FIX URLS IN LIBRERIA_FUNCIONES.PY
lf_path = r'c:\Users\aramos\Desktop\JAER\Maestria\Repositorio\Github\ProyectoUCG\libreria_funciones.py'
with codecs.open(lf_path, 'r', 'utf-8') as f:
    lf_text = f.read()

# Replace any https://www.glassdoor.com/Salary/... with https://www.glassdoor.com/Salaries/ecuador-salary-SRCH_IL.0,7_IN.8,15_IM1035.htm
# Replace hireline.io specific with https://hireline.io/ec/salarios
lf_text = re.sub(r"'https://www\.glassdoor\.com/Salary/[^']+'", "'https://www.glassdoor.com/Salaries/ecuador-salary-SRCH_IL.0,7_IN.8,15_IM1035.htm'", lf_text)
lf_text = re.sub(r"'https://hireline\.io/salarios/.*?'", "'https://hireline.io/ec/salarios'", lf_text)
lf_text = re.sub(r"'https://www\.computrabajo\.com\.ec/salarios/[^']+'", "'https://www.computrabajo.com.ec/salarios'", lf_text)

with codecs.open(lf_path, 'w', 'utf-8') as f:
    f.write(lf_text)

# 2. FIX APP.PY: REPLACE col_diag3 logic completely
app_path = r'c:\Users\aramos\Desktop\JAER\Maestria\Repositorio\Github\ProyectoUCG\app.py'
with codecs.open(app_path, 'r', 'utf-8') as f:
    app_text = f.read()

old_diag3 = r'(with col_diag3:\s*st\.markdown\("##### 🌍 Frente al Mercado Externo"\).*?)st\.markdown\("<hr style=\'border: 2px solid #f2c72e; margin: 50px 0;\'>", unsafe_allow_html=True\)'

# Alternatively, the user might see "Frente al Mercado Externo"
new_diag3 = """with col_diag3:
                st.markdown("##### 🌍 Frente al Mercado Externo (Ecuador)")
                if salario_mercado_estimado > 0:
                    diferencia_ext = analisis['salario_propuesto'] - salario_mercado_estimado
                    pct_ext = (diferencia_ext / salario_mercado_estimado) * 100
                    if pct_ext < -10:
                        st.error(f"📉 **Desventaja vs EC:** Propuesta (USD {analisis['salario_propuesto']:,.2f}) está **{abs(pct_ext):.1f}% debajo** del mercado nacional (USD {salario_mercado_estimado:,.0f}). Riesgo pérdida frente a empresas como {datos_mercado['empresa_referencia']}.")
                    elif pct_ext > 10:
                        st.warning(f"📈 **Media Superior:** Propuesta es **{pct_ext:.1f}% encima** del mercado Ecuador. Garantiza retención pero incrementa costos por encima del bench (USD {salario_mercado_estimado:,.0f}).")
                    else:
                        st.success(f"🎯 **Alineado EC:** Propuesta equilibrada y competitiva frente a los estándares de {datos_mercado['empresa_referencia']}.")
                else:
                    st.info("ℹ️ Investiga este cargo para un diagnóstico.")

            st.markdown("<hr style='border: 2px solid #f2c72e; margin: 50px 0;'>", unsafe_allow_html=True)
"""

# Let's search for the old block
if re.search(r'with col_diag3:.*?st\.markdown\("<hr', app_text, flags=re.DOTALL):
    app_text = re.sub(r'with col_diag3:\s*st\.markdown\("##### 🌍 .*?st\.markdown\("<hr style=\'border: 2px solid #f2c72e; margin: 50px 0;\'>", unsafe_allow_html=True\)', new_diag3, app_text, flags=re.DOTALL)
else:
    print("Could not find the col_diag3 block to replace via regex! Trying backup strategy...")
    
with codecs.open(app_path, 'w', 'utf-8') as f:
    f.write(app_text)

print("V5 fixes done!")
