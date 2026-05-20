import codecs
import re

# 1. FIX URLS EN LIBRERIA (SOLVE 404)
lf_path = r'c:\Users\aramos\Desktop\JAER\Maestria\Repositorio\Github\ProyectoUCG\libreria_funciones.py'
with codecs.open(lf_path, 'r', 'utf-8') as f:
    lf_text = f.read()

lf_text = lf_text.replace("'https://www.glassdoor.com/Reviews/index.htm'", "'https://www.computrabajo.com.ec/salarios'")
lf_text = lf_text.replace("'https://hireline.io/ec/salarios'", "'https://www.computrabajo.com.ec/salarios'")
lf_text = re.sub(r"f'https://www\.glassdoor\.com/.*?\'", "'https://www.computrabajo.com.ec/salarios'", lf_text)

# Ensures generic_roles also uses a solid link
lf_text = re.sub(r"'url': f'[^']*'", "'url': 'https://www.computrabajo.com.ec/salarios'", lf_text)

with codecs.open(lf_path, 'w', 'utf-8') as f:
    f.write(lf_text)

# 2. INJECT CSS AGAIN (SOLVING NEGRO TEXT IN + / - AND COLORS)
app_path = r'c:\Users\aramos\Desktop\JAER\Maestria\Repositorio\Github\ProyectoUCG\app.py'
with codecs.open(app_path, 'r', 'utf-8') as f:
    app_text = f.read()

missing_css = """
    /* ARCHIVO SUBIDO: Forzar amarillo agresivamente */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] > div > div > div:nth-child(2) > div,
    [data-testid="stSidebar"] [data-testid="stFileUploader"] [data-testid="stUploadedFile"] {
        background-color: #f2c72e !important;
        border-radius: 6px !important;
        padding: 5px !important;
        border: none !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] > div > div > div:nth-child(2) > div *,
    [data-testid="stSidebar"] [data-testid="stFileUploader"] [data-testid="stUploadedFile"] * {
        color: #0b2659 !important; 
        fill: #0b2659 !important; 
        stroke: #0b2659 !important;
        font-weight: bold !important;
    }

    /* INPUT NUMÉRICO (+/- botones en blanco y azul) */
    div[data-testid="stNumberInput"] button {
        background-color: #ffffff !important;
        color: #0b2659 !important;
        border: 1px solid #0b2659 !important;
    }
    div[data-testid="stNumberInput"] button svg {
        fill: #0b2659 !important;
        color: #0b2659 !important;
        stroke: #0b2659 !important;
    }
    
    /* Titulo Azul en tab principal, texto blanco en sidebar */
    [data-testid="stSidebar"] div[data-testid="stNumberInput"] label {
        color: #ffffff !important;
    }
    div[data-testid="stNumberInput"] label {
        color: #0b2659 !important;
        font-weight: bold !important;
    }
    div[data-testid="stNumberInput"] input {
        color: #0b2659 !important;
        background-color: #ffffff !important;
        font-weight: bold !important;
        border: 2px solid #0b2659 !important;
    }
"""

if '/* ARCHIVO SUBIDO: Forzar amarillo' in app_text:
    app_text = re.sub(r'/\* ARCHIVO SUBIDO:.*?(?=\/\* Elegante caja de)', missing_css + '\n    ', app_text, flags=re.DOTALL)
else:
    app_text = app_text.replace("/* Elegante caja de descripción corporativa - Modo Claro */", missing_css + "\n    /* Elegante caja de descripción corporativa - Modo Claro */")

# Verify col_diag3 is STILL there!
# It should be there because we manually modified it via apply_v6! We won't touch it.

with codecs.open(app_path, 'w', 'utf-8') as f:
    f.write(app_text)

print("V7 Done!")
