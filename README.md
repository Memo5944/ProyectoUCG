# 💼 Analizador Salarial de Recursos Humanos — Ecuador
### Proyecto Final Integrador · Módulo de Ciencia de Datos

---

## 📋 Resumen del Proyecto

| Campo | Detalle |
|---|---|
| **Área de Dominio** | Recursos Humanos / Gestión Salarial Corporativa |
| **Tecnología Principal** | Python · Streamlit |
| **Fuente de Datos** | Dataset propio de nómina corporativa (compatible con plantilla Excel/CSV descrita abajo) |
| **Despliegue** | Streamlit Cloud |
| **Repositorio** | [github.com/Memo5944/ProyectoUCG](https://github.com/Memo5944/ProyectoUCG) |

---

## 1. Introducción

La gestión salarial es uno de los pilares estratégicos de un departamento de Recursos Humanos moderno. Tomar decisiones de ajuste salarial sin datos objetivos expone a las organizaciones a inequidades internas, pérdida de talento y costos no planificados. Este proyecto nace de esa necesidad real y propone una solución tecnológica interactiva que integra análisis estadístico, visualización de datos y consulta del mercado laboral en tiempo real, orientada exclusivamente al mercado ecuatoriano.

---

## 2. Problemática

Las áreas de Recursos Humanos en Ecuador frecuentemente basan sus decisiones salariales en criterios subjetivos o en datos de mercado desactualizados. Esto genera:

- **Inequidad interna**: Empleados con perfiles similares percibiendo salarios desproporcionados entre sí.
- **Desconexión con el mercado externo**: Ofertas salariales por debajo de lo que publica el mercado, generando fuga de talento.
- **Falta de herramientas accesibles**: Las plataformas de benchmarking salarial profesionales tienen costos elevados para PYMEs ecuatorianas.

---

## 3. Objetivos

### Objetivo General
Desarrollar una aplicación web interactiva en Streamlit que permita a los equipos de Recursos Humanos analizar, simular y validar decisiones salariales con base en datos internos y del mercado ecuatoriano.

### Objetivos Específicos
1. Permitir la carga y exploración de un dataset de nómina corporativa en formato Excel o CSV.
2. Calcular métricas estadísticas de equidad interna (mediana, cuartiles, Compa-Ratio).
3. Comparar el salario de un colaborador con sus pares internos mediante visualizaciones interactivas.
4. Simular el impacto de un incremento salarial contemplando la inflación.
5. Consultar en tiempo real ofertas de empleo en portales ecuatorianos (Computrabajo, LinkedIn, Indeed) para estimar el salario de mercado.

---

## 4. Justificación

El proyecto está directamente relacionado con el área profesional del autor (Recursos Humanos y Compensaciones), aplicando los conocimientos del módulo sobre carga de datos, análisis exploratorio, visualización y despliegue de aplicaciones de Ciencia de Datos. Se eligió un dataset de nómina porque representa un escenario real, sensible y de alto impacto para la toma de decisiones organizacionales. La solución reduce el tiempo de análisis de horas (usando Excel manual) a segundos, aportando valor inmediato y medible.

---

## 5. Marco Teórico

- **Compa-Ratio**: Indicador de equidad salarial que relaciona el salario de un colaborador con la mediana de su grupo de referencia. Valores entre 0.8 y 1.2 se consideran zona de equidad (WorldatWork, 2021).
- **Mediana Salarial**: Estadístico robusto ante valores atípicos, preferido sobre la media en análisis de compensaciones (Armstrong & Murlis, 2007).
- **Benchmarking de Mercado**: Proceso de comparación de la estructura salarial interna con ofertas activas del mercado externo para mantener la competitividad (Milkovich et al., 2014).
- **Web Scraping con BeautifulSoup**: Técnica de extracción de datos estructurados desde páginas web, empleada aquí para capturar sueldos publicados en portales de empleo (Mitchell, 2018).
- **Streamlit**: Framework de Python de código abierto para la creación rápida de aplicaciones de datos interactivas orientadas a ciencia de datos y machine learning (Streamlit Inc., 2023).

---

## 6. Metodología

El proyecto sigue la metodología **CRISP-DM** (Cross-Industry Standard Process for Data Mining) adaptada al contexto de la aplicación:

```
1. Comprensión del Negocio → Definición de requisitos de RRHH
2. Comprensión de los Datos → Exploración del dataset de nómina
3. Preparación de los Datos → Limpieza, normalización y cálculo de antigüedad
4. Modelado → Cálculo de métricas estadísticas y scoring de mercado
5. Evaluación → Validación de resultados con fuentes externas
6. Despliegue → Publicación en Streamlit Cloud
```

---

## 7. Arquitectura del Proyecto

```
ProyectoUCG/
├── app.py                  # Interfaz principal de Streamlit (frontend)
├── libreria_funciones.py   # Módulo de lógica de negocio y motor de búsqueda
├── requirements.txt        # Dependencias del proyecto
├── .streamlit/
│   └── config.toml         # Configuración visual del tema de la app
└── README.md               # Documentación del proyecto
```

### Descripción de Módulos

| Archivo | Rol |
|---|---|
| `app.py` | Interfaz visual: carga de datos, tabs de análisis, gráficos interactivos y diagnóstico |
| `libreria_funciones.py` | Lógica pura: preparación de datos, métricas, simulaciones y **Smart Hunter** de mercado |

---

## 8. Funcionalidades de la Aplicación

### 8.1 Carga y Exploración de Datos
- Soporte para archivos **Excel (.xlsx)** y **CSV (.csv)**.
- Validación automática de columnas obligatorias con mensaje de error descriptivo.
- Cálculo automático de **Antigüedad en años** a partir de la columna `Fecha de ingreso`.
- Cálculo del **Salario Total** sumando salario base + horas extras (HE 25%, 50%, 100%).

### 8.2 Análisis de Equidad Interna
- Selección del colaborador a evaluar mediante un desplegable inteligente.
- Filtro de cargos similares para definir el **grupo comparativo**.
- Cálculo de **mediana, promedio, mínimo y máximo** del grupo.
- **Velocímetro de Compa-Ratio** que indica visualmente si el salario está dentro, por debajo o por encima del mercado interno.

### 8.3 Simulador de Incrementos
- Ingreso del **porcentaje de incremento** propuesto.
- Ingreso de la **inflación anual esperada**.
- El sistema precalcula el porcentaje de ajuste sugerido para alcanzar la mediana del grupo.
- Desglose detallado del impacto en cada rubro salarial (salario base, HE 25%, HE 50%, HE 100%).

### 8.4 Visualizaciones Interactivas
| Gráfico | Descripción |
|---|---|
| **Velocímetro Compa-Ratio** | Posición actual vs. propuesta en la escala de equidad |
| **Dispersión Antigüedad vs Salario** | Curva de experiencia con línea de tendencia y banda de tolerancia ±15% |
| **Barras comparativas de pares** | Ranking salarial del grupo con líneas de referencia de mediana y propuesta |
| **Diagrama de Caja (Box Plot)** | Distribución estadística del grupo con posición actual y propuesta |

### 8.5 Motor de Mercado Externo — *Smart Hunter v2.1*
Motor de búsqueda propio que consulta Yahoo Search en tiempo real, filtrando y puntuando resultados de portales de empleo ecuatorianos:

- **Portales priorizados**: Computrabajo EC, Multitrabajo, PorFinEmpleo, LinkedIn Jobs, Indeed EC, SocioEmpleo (Gobierno).
- **Búsquedas combinadas**: Cruza Cargo + Área para maximizar la precisión (ej: *"Analista Financiero"* + *"Finanzas"*).
- **Filtros geográficos**: Bloquea dominios extranjeros (`.co`, `.pe`, `.mx`) y descarta resultados que mencionen países fuera de Ecuador.
- **Filtros de calidad**: Elimina calculadoras de impuestos, noticias genéricas y valores del SBU sin contexto.
- **Score de confianza**: Califica cada evidencia y prioriza las más relevantes en el Top 10 final.

---

## 9. Instalación y Ejecución Local

### Prerrequisitos
- Python 3.9 o superior
- pip (gestor de paquetes de Python)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Memo5944/ProyectoUCG.git
cd ProyectoUCG

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
streamlit run app.py
```

---

## 10. Formato del Dataset

La aplicación espera un archivo Excel o CSV con las siguientes columnas (los nombres deben ser exactos):

| Columna | Tipo | Descripción |
|---|---|---|
| `Codigo` | Texto | Identificador único del empleado |
| `Trabajador` | Texto | Nombre completo del colaborador |
| `Cargo` | Texto | Título del puesto de trabajo |
| `Area` | Texto | Departamento o área organizacional |
| `Fecha de ingreso` | Fecha `dd/mm/aaaa` | Día de inicio laboral (la antigüedad se calcula automáticamente) |
| `Edad` | Número | Edad del colaborador en años |
| `Salario` | Número | Salario base mensual en USD |
| `HE 25%` | Número | Valor de horas extras al 25% |
| `HE 50%` | Número | Valor de horas extras al 50% |
| `HE 100%` | Número | Valor de horas extras al 100% |

### Ejemplo de plantilla:

| Codigo | Trabajador | Cargo | Area | Fecha de ingreso | Edad | Salario | HE 25% | HE 50% | HE 100% |
|---|---|---|---|---|---|---|---|---|---|
| EMP01 | Juan Pérez | Analista Financiero | Finanzas | 15/05/2021 | 28 | 1200 | 50 | 0 | 0 |
| EMP02 | María Gómez | Analista Financiero | Finanzas | 10/01/2019 | 32 | 1400 | 0 | 100 | 0 |
| EMP03 | Carlos Díaz | Gerente | Finanzas | 01/08/2013 | 45 | 3000 | 0 | 0 | 150 |

---

## 11. Dependencias

```
streamlit
pandas
numpy
plotly
requests
beautifulsoup4
openpyxl
```

---

## 12. Resultados Esperados

Al cargar una base de datos válida, la aplicación produce:

1. **KPIs instantáneos**: Salario actual, propuesto, pérdida por inflación y mediana comparativa.
2. **Diagnóstico de equidad interna**: Alerta si el salario propuesto supera el máximo del grupo o si el empleado está subpagado.
3. **Diagnóstico de mercado externo**: Compara la propuesta con el mercado ecuatoriano real y emite un semáforo (riesgo, alineado, superior).
4. **Evidencias verificables**: Tabla enlazada de ofertas reales detectadas en portales ecuatorianos.
5. **Exportación**: Cuadro comparativo de pares descargable.

---

## 13. Conclusiones

- Se logró desarrollar una aplicación funcional y visualmente profesional que cubre el ciclo completo de análisis de datos: carga → exploración → análisis → visualización → resultado.
- La integración del motor de mercado externo (*Smart Hunter*) agrega un valor diferencial frente a herramientas estáticas, permitiendo benchmarking en tiempo real sin costos adicionales.
- El uso de Streamlit demostró ser una plataforma ideal para prototipos de ciencia de datos orientados a usuarios no técnicos, reduciendo significativamente el tiempo de desarrollo de la interfaz.
- El proyecto queda como base escalable para incorporar predicción salarial con modelos de Machine Learning en una próxima iteración.

---

## 14. Referencias (APA 7.ª edición)

- Armstrong, M., & Murlis, H. (2007). *Reward management: A handbook of remuneration strategy and practice* (5.ª ed.). Kogan Page.
- Milkovich, G. T., Newman, J. M., & Gerhart, B. (2014). *Compensation* (11.ª ed.). McGraw-Hill Education.
- Mitchell, R. (2018). *Web scraping with Python: Collecting more data from the modern web* (2.ª ed.). O'Reilly Media.
- Streamlit Inc. (2023). *Streamlit documentation*. https://docs.streamlit.io
- Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Cournapeau, D., Burovski, E., Peterson, P., Weckesser, W., Bright, J., van der Walt, S. J., Brett, M., Wilson, J., Millman, K. J., Mayorov, N., Nelson, A. R. J., Jones, E., Kern, R., Larson, E., … SciPy 1.0 Contributors. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods*, *17*(3), 261–272. https://doi.org/10.1038/s41592-019-0686-2
- WorldatWork. (2021). *Compensation programs and practices survey*. https://worldatwork.org
- McKinney, W. (2010). Data structures for statistical computing in Python. *Proceedings of the 9th Python in Science Conference*, 51–56. https://doi.org/10.25080/Majora-92bf1922-00a

---

*Proyecto desarrollado como entregable del módulo de Ciencia de Datos · Universidad de Guayaquil · MBA · 2026*