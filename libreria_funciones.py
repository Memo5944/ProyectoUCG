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
    
    # Extraer horas extras evitando cualquier columna que no sea de rubros (e.g. total, salario, cargo)
    he_cols = [c for c in datos_empleado.index if ('he ' in str(c).lower() or 'hora' in str(c).lower() or 'extra' in str(c).lower())]
    he_cols = [c for c in he_cols if 'total' not in str(c).lower() and 'salario' not in str(c).lower() and 'base' not in str(c).lower() and 'cargo' not in str(c).lower() and 'area' not in str(c).lower()]
    
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


import statistics

def estimar_mercado_externo(cargo, area, mediana_interna):
    """
    SMART HUNTER EXTERN (Ecuador):
    Minería de ofertas reales y activas con RADAR BIDIRECCIONAL.
    """
    cargo_base = str(cargo).strip()
    area_base = str(area).strip() if area else ""
    
    # Queries diversificadas y MÁS FLEXIBLES (sin comillas exactas)
    search_queries = [
        f'sueldo {cargo_base} ecuador',
        f'cuanto gana un {cargo_base} en ecuador',
        f'salario promedio {cargo_base} ecuador',
        f'ofertas empleo {cargo_base} ecuador salario',
        f'site:computrabajo.com.ec {cargo_base} ecuador'
    ]
    
    todas_evidencias = []
    
    try:
        from duckduckgo_search import DDGS
        
        with DDGS() as ddgs:
            for q in search_queries:
                if len(todas_evidencias) >= 10: break
                
                try:
                    # Traemos los primeros 5 resultados reales por cada query geolocalizando explícitamente en Ecuador
                    results = ddgs.text(q, region='ec-es', max_results=5)
                    if not results: continue
                    
                    for res in results:
                        title = res.get('title', '')
                        snippet = res.get('body', '')
                        link = res.get('href', 'web')
                        
                        full_text = (title + " " + snippet).lower()
                        
                        # --- COMPONENTE RADAR BIDIRECCIONAL ---
                        # Patrón: detecta números cerca de disparadores salariales en cualquier orden
                        regex_patrones = [
                            r'(?:sueldo|salario|remuneración|pagamos|ofrece|usd|\$)\D*([\d\.,]{3,6})',
                            r'([\d\.,]{3,6})\D*(?:usd|dólares|mensuales|mensual)'
                        ]
                        
                        for p in regex_patrones:
                            matches = re.finditer(p, full_text)
                            for m in matches:
                                raw_val = m.group(1)
                                clean_val = re.sub(r'[^\d]', '', raw_val)
                                if clean_val:
                                    v = float(clean_val)
                                    if v in [2023, 2024, 2025, 2026]: continue
                                    if v > 15000: v /= 12
                                    
                                    if 425 <= v <= 10000: # Salario básico Ecuador como piso
                                        # Intentamos obtener el dominio principal rápido para la fuente
                                        portal = "Web / " + link.split('/')[2].replace('www.', '') if '://' in link else "Referencia"
                                        if not any(abs(e['valor'] - v) < 5 for e in todas_evidencias):
                                            todas_evidencias.append({
                                                "empresa": portal,
                                                "cargo_hallado": title[:100].strip() + ("..." if len(title) > 100 else ""),
                                                "valor": round(v, 2),
                                                "url": link
                                            })
                        if len(todas_evidencias) >= 10: break
                except Exception:
                    pass
    except ImportError:
        pass # Si falla por alguna razón instalar pip install duckduckgo-search

    # Estadísticas y Respuesta
    valores = [e['valor'] for e in todas_evidencias]
    resultado = {
        "salario_estimado": 0.0, "media": 0.0, "mediana": 0.0, "evidencias": todas_evidencias,
        "mensaje": "❌ Smart Hunter: No se detectaron sueldos legibles en las ofertas actuales.",
        "confianza": "Sin datos", "original_url": f"https://www.google.com/search?q={urllib.parse.quote_plus(cargo_base + ' sueldo ecuador')}"
    }

    if valores:
        m_val = statistics.median(valores)
        resultado.update({
            "salario_estimado": round(m_val, 2),
            "media": round(sum(valores) / len(valores), 2),
            "mediana": round(m_val, 2),
            "confianza": "Validada por Red" if len(valores) >= 3 else "Referencial",
            "mensaje": f"✅ Éxito: {len(valores)} evidencias encontradas con Radar Bidireccional."
        })
    
    return resultado


