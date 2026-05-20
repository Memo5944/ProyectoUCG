import pandas as pd

def preparar_datos(df):
    """
    Estandariza los nombres de columnas, verifica obligatoriedad y calcula el Salario Total.
    """
    # Normalizar nombres de columnas a minúsculas
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    # Validar que existan todas las columnas requeridas estrictamente
    columnas_requeridas = ['codigo', 'trabajador', 'cargo', 'area', 'antigüedad', 'edad', 'salario', 'he 25%', 'he 50%', 'he 100%']
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    
    if len(columnas_faltantes) > 0:
        faltantes_str = ", ".join([c.title() for c in columnas_faltantes]).replace('He', 'HE').replace('Area', 'Área').replace('Codigo', 'Código')
        raise ValueError(f"Faltan las siguientes columnas en el archivo: {faltantes_str}. Verifica que los nombres sean exactamente los indicados.")
        
    df['salario_base_limpio'] = pd.to_numeric(df['salario'], errors='coerce').fillna(0)

    # Sumar específicamente estas horas extras
    df['total_horas_extras'] = (pd.to_numeric(df['he 25%'], errors='coerce').fillna(0) +
                                pd.to_numeric(df['he 50%'], errors='coerce').fillna(0) +
                                pd.to_numeric(df['he 100%'], errors='coerce').fillna(0))
        
    # Calcular salario total
    df['salario_total'] = df['salario_base_limpio'] + df['total_horas_extras']
            
    # Convertir antigüedad a años si viene como fecha (dd/mm/aaaa) o datetime
    col_antiguedad = 'antigüedad'
    if col_antiguedad:
        if pd.api.types.is_datetime64_any_dtype(df[col_antiguedad]):
            df[col_antiguedad] = (pd.Timestamp('today') - df[col_antiguedad]).dt.days / 365.25
        elif df[col_antiguedad].dtype == 'object':
            try:
                fechas = pd.to_datetime(df[col_antiguedad], format='%d/%m/%Y', errors='coerce')
                # Si alguna fecha es válida, transformar la columna entera a años desde la fecha actual
                if not fechas.isna().all():
                    df[col_antiguedad] = (pd.Timestamp('today') - fechas).dt.days / 365.25
            except Exception:
                pass
            
        # Asegurar numérico en caso de que viniera texto raro o si ya se convirtió a años
        df[col_antiguedad] = pd.to_numeric(df[col_antiguedad], errors='coerce').fillna(0)
    
    return df

def obtener_metricas_cargo(df, cargo):
    df_cargo = df[df['cargo'].str.lower() == cargo.lower()]
    if df_cargo.empty:
        return None
    
    return {
        'mediana': df_cargo['salario_total'].median(),
        'promedio': df_cargo['salario_total'].mean(),
        'min': df_cargo['salario_total'].min(),
        'max': df_cargo['salario_total'].max(),
        'cantidad': len(df_cargo)
    }

def evaluar_incremento(salario_actual, porcentaje_incremento, porcentaje_inflacion):
    salario_propuesto = salario_actual * (1 + (porcentaje_incremento / 100))
    perdida_por_inflacion = salario_actual * (porcentaje_inflacion / 100)
    salario_real_actual = salario_actual - perdida_por_inflacion
    aumento_real = salario_propuesto - salario_actual
    
    return {
        'salario_propuesto': salario_propuesto,
        'salario_real_actual': salario_real_actual,
        'perdida_inflacion': perdida_por_inflacion,
        'aumento_real_monto': aumento_real
    }

def evaluar_incremento_detallado(datos_empleado, porcentaje_incremento, porcentaje_inflacion):
    salario_total_actual = float(datos_empleado.get('salario_total', 0))
    salario_base_actual = float(datos_empleado.get('salario_base_limpio', salario_total_actual))
    
    # Extraer horas extras evitando cualquier columna de 'total', 'salario' o 'base'
    he_cols = [c for c in datos_empleado.index if ('he ' in str(c).lower() or 'hora' in str(c).lower() or 'extra' in str(c).lower())]
    he_cols = [c for c in he_cols if 'total' not in str(c).lower() and 'salario' not in str(c).lower() and 'base' not in str(c).lower()]
    
    factor_incremento = 1 + (porcentaje_incremento / 100)
    
    desglose = []
    
    # Base
    base_propuesto = salario_base_actual * factor_incremento
    desglose.append({
        'Rubro': 'Salario Base',
        'Actual': salario_base_actual,
        'Propuesto': base_propuesto,
        'Diferencia': base_propuesto - salario_base_actual
    })
    
    # Horas Extras Individuales
    for col in he_cols:
        try:
            val_actual = float(datos_empleado.get(col, 0))
            if val_actual > 0:
                val_propuesto = val_actual * factor_incremento
                desglose.append({
                    'Rubro': str(col).upper(),
                    'Actual': val_actual,
                    'Propuesto': val_propuesto,
                    'Diferencia': val_propuesto - val_actual
                })
        except Exception:
            pass
            
    # Totales
    salario_propuesto = salario_total_actual * factor_incremento
    desglose.append({
        'Rubro': 'TOTAL',
        'Actual': salario_total_actual,
        'Propuesto': salario_propuesto,
        'Diferencia': salario_propuesto - salario_total_actual
    })
    
    df_desglose = pd.DataFrame(desglose)
    
    perdida_por_inflacion = salario_total_actual * (porcentaje_inflacion / 100)
    salario_real_actual = salario_total_actual - perdida_por_inflacion
    aumento_real = salario_propuesto - salario_total_actual
    
    return {
        'salario_propuesto': salario_propuesto,
        'salario_real_actual': salario_real_actual,
        'perdida_inflacion': perdida_por_inflacion,
        'aumento_real_monto': aumento_real,
        'df_desglose': df_desglose
    }

def obtener_metricas_cargos_multiples(df, cargos):
    """
    Obtiene métricas estadísticas (mediana, promedio, min, max) para una lista de cargos.
    """
    df_cargos = df[df['cargo'].str.lower().isin([c.lower() for c in cargos])]
    if df_cargos.empty:
        return None
    
    metricas = {
        'mediana': df_cargos['salario_total'].median(),
        'promedio': df_cargos['salario_total'].mean(),
        'min': df_cargos['salario_total'].min(),
        'max': df_cargos['salario_total'].max(),
        'cantidad': len(df_cargos)
    }
    return metricas

def calcular_compa_ratio(salario_total, mediana_cargo):
    if not mediana_cargo or mediana_cargo == 0:
        return 1.0
    return salario_total / mediana_cargo

import urllib.parse
import requests
from bs4 import BeautifulSoup
import re

def generar_enlaces_investigacion(cargo):
    """
    Genera enlaces de búsqueda REALES en fuentes confiables del mercado laboral
    ecuatoriano para que el usuario investigue datos salariales verdaderos.
    """
    cargo_limpio = str(cargo).strip()
    cargo_encoded = urllib.parse.quote_plus(cargo_limpio)
    
    enlaces = [
        {
            'fuente': 'Glassdoor',
            'descripcion': 'Salarios reportados por empleados reales',
            'url': f'https://www.glassdoor.com/Search/results.htm?keyword={cargo_encoded}+Ecuador'
        },
        {
            'fuente': 'Computrabajo Ecuador',
            'descripcion': 'Ofertas laborales activas con rangos salariales',
            'url': f'https://www.computrabajo.com.ec/trabajo-de-{urllib.parse.quote_plus(cargo_limpio.lower().replace(" ", "-"))}'
        },
        {
            'fuente': 'Indeed Ecuador',
            'descripcion': 'Salarios y ofertas del mercado ecuatoriano',
            'url': f'https://ec.indeed.com/jobs?q={cargo_encoded}&l=Ecuador'
        },
        {
            'fuente': 'LinkedIn Salary',
            'descripcion': 'Insights salariales de profesionales verificados',
            'url': f'https://www.linkedin.com/salary/search?keywords={cargo_encoded}&countryCode=ec'
        }
    ]
    
    return enlaces


def estimar_mercado_externo(cargo, mediana_interna):
    """
    CONSULTA REAL: Realiza una búsqueda dinámica en Talent.com Ecuador
    para obtener el salario real del mercado en tiempo real.
    Cero datos hardcodeados en el código.
    """
    cargo_str = str(cargo).strip()
    cargo_encoded = urllib.parse.quote_plus(cargo_str)
    url_consulta = f"https://ec.talent.com/salary?job={cargo_encoded}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
    
    resultado = {
        "salario_estimado": 0.0,
        "enlaces_investigacion": generar_enlaces_investigacion(cargo_str),
        "muestras": [],
        "confianza": "Buscando datos en tiempo real...",
        "fuente": "Talent.com Ecuador (Consulta Dinámica)",
        "original_url": url_consulta,
        "mensaje": f"Realizando consulta dinámica para '{cargo_str}'...",
        "empresa_referencia": "Mercado General Ecuador"
    }
    
    try:
        # Intentar la consulta dinámica
        response = requests.get(url_consulta, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Intentar encontrar el monto en las clases conocidas de Talent.com
            salary_card = soup.find('div', class_='salary-card') or soup.find('div', class_='l-card')
            
            amount_text = None
            if salary_card:
                amount_el = (salary_card.find('div', class_='salary-amount') or 
                             salary_card.find('div', class_='time-card__amount') or
                             salary_card.find('span', class_='salary-amount'))
                if amount_el:
                    amount_text = amount_el.text.strip()
            
            # Si no se halló por clase, buscar por Regex en el texto plano
            if not amount_text:
                page_text = soup.get_text()
                # Buscar patrón de moneda: $ 1,200 o $1.500
                m = re.search(r'\$\s*([\d\.,]+)', page_text)
                if m:
                    amount_text = m.group(1)
            
            if amount_text:
                # Limpiar el texto: quitar $, espacios, y manejar miles
                # Talent.com suele usar "." para miles y "," para decimales o viceversa según el locale
                clean_raw = re.sub(r'[^\d\.,]', '', amount_text)
                
                # Heurística de conversión: si hay un punto y una coma, el último es el decimal
                if '.' in clean_raw and ',' in clean_raw:
                    if clean_raw.find('.') < clean_raw.find(','): # 1.200,50
                        clean_num = clean_raw.replace('.', '').replace(',', '.')
                    else: # 1,200.50
                        clean_num = clean_raw.replace(',', '')
                else:
                    # Si solo hay uno, asumimos que es separador de miles si el resultado es "lógico" para un sueldo
                    # o simplemente lo quitamos para tener el entero
                    clean_num = clean_raw.replace('.', '').replace(',', '')
                
                try:
                    valor = float(clean_num)
                    
                    # Talent.com a veces muestra anual. Si es > 6000, dividimos para 12
                    # (En Ecuador pocos cargos básicos superan los 5000/mes)
                    if valor > 6000:
                        valor = round(valor / 12, 2)
                    
                    resultado["salario_estimado"] = valor
                    resultado["confianza"] = "Alta (Dato obtenido en vivo)"
                    resultado["mensaje"] = f"Consulta exitosa en Talent.com. Se halló un promedio mensual de USD {valor:,.2f} para '{cargo_str}'."
                except:
                    pass
        
        if resultado["salario_estimado"] == 0:
            resultado["confianza"] = "Consulta realizada — Sin resultado exacto"
            resultado["mensaje"] = f"La consulta automática a Talent.com no arrojó un valor numérico claro para '{cargo_str}'. Por favor, usa los enlaces de apoyo para validar manualmente."
            
    except Exception as e:
        resultado["confianza"] = "Error en consulta dinámica"
        resultado["mensaje"] = f"No se pudo completar la consulta automática (Error: {str(e)}). Usa los enlaces de investigación manual."
        
    return resultado

