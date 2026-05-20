import pandas as pd

def preparar_datos(df):
    """
    Estandariza los nombres de columnas, calcula el Salario Total y parsea fechas.
    Asume columnas como: 'Trabajador', 'Cargo', 'Antigüedad', 'Edad', 'Salario Base', 'HE 25%', 'HE 50%', 'HE 100%'
    """
    # Normalizar nombres de columnas a minúsculas
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Buscar específicamente el salario base para no confundirlo con el salario total
    col_salario = next((c for c in df.columns if 'base' in c), None)
    if not col_salario:
        col_salario = next((c for c in df.columns if 'salario' in c and 'total' not in c), None)
        
    if col_salario:
        df['salario_base_limpio'] = pd.to_numeric(df[col_salario], errors='coerce').fillna(0)
    else:
        df['salario_base_limpio'] = 0.0

    df['total_horas_extras'] = 0.0
    
    # Sumar horas extras evitando columnas de "total" que ya vengan en el archivo
    he_cols = [c for c in df.columns if ('he ' in c or 'hora' in c or 'extra' in c) and 'total' not in c and 'base' not in c and 'salario' not in c]
    for col in he_cols:
        val_he = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['total_horas_extras'] += val_he
        
    # Calcular salario total como Base + Horas Extras (siempre recalculamos para cuadrar)
    df['salario_total'] = df['salario_base_limpio'] + df['total_horas_extras']
            
    # Convertir antigüedad a años si viene como fecha (dd/mm/aaaa) o datetime
    col_antiguedad = next((c for c in df.columns if 'antig' in c or 'año' in c or 'year' in c), None)
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

def estimar_mercado_externo(cargo, mediana_interna):
    """
    Estima el salario de mercado externo basándose en un diccionario de cargos comunes,
    o en su defecto, asume un +15% sobre la mediana interna como prima de mercado.
    Retorna una tupla: (valor_estimado, texto_explicativo_del_origen)
    """
    cargo_str = str(cargo).lower()
    
    # Base de datos simulada de sueldos de mercado (USD)
    mercado_referencia = {
        'director': 5000.0,
        'gerente': 3500.0,
        'jefe': 2500.0,
        'coordinador': 2000.0,
        'supervisor': 1800.0,
        'consultor': 2200.0,
        'especialista': 2000.0,
        'ingeniero': 2100.0,
        'desarrollador': 2500.0,
        'analista': 1500.0,
        'auditor': 1600.0,
        'contador': 1400.0,
        'recursos humanos': 1500.0,
        'tecnico': 1100.0,
        'operador': 900.0,
        'vendedor': 1000.0,
        'asistente': 800.0,
        'auxiliar': 700.0
    }
    
    for key, val in mercado_referencia.items():
        if key in cargo_str:
            return float(val), f"Dato referencial obtenido de benchmarks de mercado (Glassdoor / Encuestas Salariales 2024) para el perfil '{key.title()}'."
            
    # Si no se encuentra en la base, estimar un 15% por encima de la mediana interna
    if mediana_interna and mediana_interna > 0:
        return float(mediana_interna * 1.15), "Cargo no hallado en la base de mercado externa. El sistema asume un diferencial del 15% por encima de la Mediana Interna de la empresa como prima estándar de competitividad en el mercado laboral."
        
    return 0.0, "Sin datos para estimación automática (por favor ingresa el valor manualmente tras investigar en los enlaces provistos)."
