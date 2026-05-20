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
    CONSULTA REAL MULTI-FUENTE: 
    1. Intenta consulta directa en Talent.com (Ecuador)
    2. Si falla, realiza búsqueda en DuckDuckGo (Snippet Scraping)
    Cero datos hardcodeados.
    """
    cargo_str = str(cargo).strip()
    cargo_encoded = urllib.parse.quote_plus(cargo_str)
    
    # Headers realistas para evitar bloqueos
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9"
    }
    
    resultado = {
        "salario_estimado": 0.0,
        "enlaces_investigacion": generar_enlaces_investigacion(cargo_str),
        "muestras": [],
        "confianza": "Consultando fuentes en vivo...",
        "fuente": "Pendiente",
        "original_url": "",
        "mensaje": f"Iniciando búsqueda para '{cargo_str}'...",
        "empresa_referencia": "Mercado Ecuador"
    }

    # --- FUENTE 1: Talent.com ---
    url_talent = f"https://ec.talent.com/salary?job={cargo_encoded}"
    try:
        resp = requests.get(url_talent, headers=headers, timeout=8)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Selector actualizado por inspección
            val_el = soup.select_one(".l-card__salary-value") or soup.select_one(".salary-amount") or soup.select_one(".time-card__amount")
            
            if val_el:
                amount_text = val_el.get_text(strip=True)
                # Limpieza robusta
                clean_num = re.sub(r'[^\d\.,]', '', amount_text)
                # Normalizar: quitar puntos de miles, cambiar coma decimal a punto
                if ',' in clean_num and '.' in clean_num:
                    if clean_num.find('.') < clean_num.find(','): clean_num = clean_num.replace('.', '').replace(',', '.')
                    else: clean_num = clean_num.replace(',', '')
                else: clean_num = clean_num.replace('.', '').replace(',', '')
                
                valor = float(clean_num)
                if valor > 6000: valor = round(valor / 12, 2) # anual a mensual
                
                if valor > 0:
                    resultado.update({
                        "salario_estimado": valor,
                        "fuente": "Talent.com Ecuador",
                        "original_url": url_talent,
                        "confianza": "Alta (Dato exacto)",
                        "mensaje": f"✅ Consulta exitosa en Talent.com: USD {valor:,.2f} mensuales."
                    })
                    return resultado
    except:
        pass

    # --- FUENTE 2: Fallback Búsqueda DuckDuckGo (Snippet Extract) ---
    # Este método es casi imposible de bloquear ya que es texto plano
    url_ddg = f"https://html.duckduckgo.com/html/?q=salario+promedio+{cargo_encoded}+ecuador"
    try:
        resultado["mensaje"] = "Consultando motor de búsqueda (Fallback)..."
        resp = requests.get(url_ddg, headers=headers, timeout=8)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            snippets = soup.select(".result__snippet")
            
            encontrados = []
            for s in snippets:
                txt = s.get_text().lower()
                # Buscar patrones de salario en el resumen del resultado
                # Ej: "...salario promedio de $1.200 al mes..." o "$800 - $1200"
                matches = re.finditer(r'\$\s?([\d\.,]+)', txt)
                for m_match in matches:
                    num_str = m_match.group(1)
                    num_clean = re.sub(r'[^\d]', '', num_str) 
                    if num_clean:
                        v = float(num_clean)
                        if 400 < v < 15000: # Rango lógico mensual/anual Ecuador
                            if v > 6000: v = v / 12
                            encontrados.append(v)
            
            if encontrados:
                valor_medio = sum(encontrados) / len(encontrados)
                resultado.update({
                    "salario_estimado": round(valor_medio, 2),
                    "fuente": "Motores de búsqueda (Consenso)",
                    "original_url": url_ddg,
                    "confianza": "Media (Basado en resultados de búsqueda)",
                    "mensaje": f"✅ Datos obtenidos vía búsqueda externa: USD {valor_medio:,.2f} mensuales."
                })
                return resultado
    except:
        pass

    # Si todo falla
    resultado["confianza"] = "Baja / Requiere Manual"
    resultado["mensaje"] = "❌ No pudimos obtener un valor automático confiable. Usa los enlaces de abajo para validar."
    return resultado


