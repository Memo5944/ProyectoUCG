import os
import re

app_path = r'c:\Users\aramos\Desktop\JAER\Maestria\Repositorio\Github\ProyectoUCG\app.py'

with open(app_path, 'r', encoding='utf-8') as f:
    text = f.read()

new_style = """
    <style>
    /* El fondo y colores generales ahora son manejados por .streamlit/config.toml */
    /* Pero añadimos acentos estéticos premium corporativos */
    
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
    }
    
    /* Acentos corporativos en títulos */
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
    
    /* Borde amarillo en sidebar */
    [data-testid="stSidebar"] {
        border-right: 4px solid #f2c72e !important;
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
"""

# Find old style block exactly
text = re.sub(r'<style>.*?</style>', new_style.strip(), text, flags=re.DOTALL)

# Fix fig colors
text = text.replace('font_color="#E2E8F0"', 'font_color="#0b2659"')
text = text.replace('font_color="#F8FAFC"', 'font_color="#0b2659"')
text = text.replace("'color': \"#E2E8F0\"", "'color': \"#0b2659\"")
text = text.replace("'color': \"#F8FAFC\"", "'color': \"#0b2659\"")
text = text.replace("'color': \"white\"", "'color': \"#0b2659\"")
text = text.replace("'tickcolor': \"white\"", "'tickcolor': \"#0b2659\"")

# Fix lines and gauge 
text = text.replace("'bar': {'color': \"#00D2D3\"}", "'bar': {'color': \"#f2c72e\"}")
text = text.replace("line=dict(color='rgba(255, 255, 255, 0.6)'", "line=dict(color='rgba(11, 38, 89, 0.6)'")
text = text.replace("line=dict(color='white'", "line=dict(color='#0b2659'")
text = text.replace("'fillcolor': 'rgba(0, 210, 211, 0.1)'", "'fillcolor': 'rgba(242, 199, 46, 0.2)'")
text = text.replace("gridcolor=\"rgba(255,255,255,0.1)\"", "gridcolor=\"rgba(11,38,89,0.1)\"")
text = text.replace("bgcolor=\"rgba(0,0,0,0.5)\"", "bgcolor=\"rgba(255,255,255,0.7)\"")

# Fix highlighting colors in dataframe and bars
text = text.replace("['#FF4B4B' if t == trabajador_seleccionado else '#00D2D3' for t in df_pares_local['trabajador']]", 
                    "['#FF4B4B' if t == trabajador_seleccionado else '#0b2659' for t in df_pares_local['trabajador']]")
text = text.replace("['background-color: rgba(239, 68, 68, 0.2); color: white; font-weight: bold']", 
                    "['background-color: rgba(239, 68, 68, 0.2); color: #0b2659; font-weight: bold']")
text = text.replace("['background-color: rgba(0, 210, 211, 0.2); font-weight: bold; color: white']", 
                    "['background-color: rgba(242, 199, 46, 0.3); font-weight: bold; color: #0b2659']")

# Fix annotations lines
text = text.replace('line_color="#00D2D3"', 'line_color="#f2c72e"')
text = text.replace('border_color="#00D2D3"', 'border_color="#f2c72e"')
text = text.replace('border: 2px solid #00D2D3', 'border: 2px solid #f2c72e')

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Done updating app.py')
