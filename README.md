# 💼 Analizador Salarial Corporativo (Ecuador)

Herramienta profesional de análisis y simulación salarial para departamentos de Recursos Humanos. Permite evaluar equidad interna, competitividad de mercado y simular incrementos basados en datos reales.

## 🚀 Características Principales

- **Análisis de Equidad Interna**: Comparativa automática de Compa-Ratio y cuartiles frente a pares internos.
- **Consulta de Mercado en Tiempo Real**: Motor de búsqueda dinámico que consulta salarios reales en Ecuador (Talent.com y Google/DuckDuckGo) para evitar datos desactualizados o ficticios.
- **Simulador de Incrementos**: Evaluación detallada del impacto de aumentos en la estructura salarial (Horas Extras, Proyecciones, etc.).
- **Visualizaciones Premium**: Gráficos interactivos de dispersión (Antigüedad vs Salario), diagramas de caja y velocímetros de competitividad.
- **Exportación de Datos**: Compatible con formatos Excel y CSV.

## 🛠️ Instalación

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecuta la aplicación:
   ```bash
   streamlit run app.py
   ```

## 📂 Formato de Datos
La herramienta espera una base de datos con las siguientes columnas principales:
- `Trabajador`: Nombre del empleado.
- `Cargo`: Título oficial.
- `Salario`: Monto base.
- `Antigüedad`: Fecha de ingreso (para curvas de experiencia).