def replace_colors():
    path = r'c:\Users\aramos\Desktop\JAER\Maestria\Repositorio\Github\ProyectoUCG\app.py'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Change parameter default & calls
    text = text.replace('border_color="#00D2D3"', 'border_color="#f2c72e"')

    # Change gauge bar color
    text = text.replace("'bar': {'color': \"#00D2D3\"}", "'bar': {'color': \"#f2c72e\"}")

    # Change scatter fill color
    text = text.replace("'fillcolor': 'rgba(0, 210, 211, 0.1)'", "'fillcolor': 'rgba(242, 199, 46, 0.1)'")

    # Change bar default highlight color
    text = text.replace("['#FF4B4B' if t == trabajador_seleccionado else '#00D2D3' for t in df_pares_local['trabajador']]", "['#FF4B4B' if t == trabajador_seleccionado else '#0b2659' for t in df_pares_local['trabajador']]")

    # Table highlight
    text = text.replace("['background-color: rgba(0, 210, 211, 0.2); font-weight: bold; color: white']", "['background-color: rgba(242, 199, 46, 0.3); font-weight: bold; color: white']")

    # HR
    text = text.replace("<hr style='border: 2px solid #00D2D3;", "<hr style='border: 2px solid #f2c72e;")

    # Box highlight lines
    text = text.replace('line_color="#00D2D3"', 'line_color="#f2c72e"')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

if __name__ == "__main__":
    replace_colors()
