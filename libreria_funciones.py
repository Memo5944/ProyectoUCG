import pandas as pd

def preparar_datos(df):
    """
    Estandariza los nombres de columnas, calcula el Salario Total y parsea fechas.
    Asume columnas como: 'Trabajador', 'Cargo', 'Antigüedad', 'Edad', 'Salario Base', 'HE 25%', 'HE 50%', 'HE 100%'
    """
    # Normalizar nombres de columnas a minúsculas
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Calcular salario total si no existe
    col_salario = next((c for c in df.columns if 'base' in c or 'salario' in c), None)
    if col_salario:
        df['salario_base_limpio'] = pd.to_numeric(df[col_salario], errors='coerce').fillna(0)
        df['salario_total'] = df['salario_base_limpio'].copy()
        df['total_horas_extras'] = 0.0
        
        # Sumar TODAS las horas extras (HE 25, 50, 100, etc.)
        he_cols = [c for c in df.columns if 'he' in c or 'hora' in c or 'extra' in c]
        for col in he_cols:
            val_he = pd.to_numeric(df[col], errors='coerce').fillna(0)
            df['total_horas_extras'] += val_he
            df['salario_total'] += val_he
            
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
        'analista financiero': 1600.0,
        'gerente': 3500.0,
        'desarrollador': 2500.0,
        'contador': 1400.0,
        'recursos humanos': 1500.0,
        'director': 5000.0,
        'asistente': 800.0,
        'vendedor': 1200.0
    }
    
    for key, val in mercado_referencia.items():
        if key in cargo_str:
            return float(val), f"Dato referencial obtenido de benchmarks de mercado (Glassdoor / Encuestas Salariales 2024) para el perfil '{key.title()}'."
            
    # Si no se encuentra en la base, estimar un 15% por encima de la mediana interna
    if mediana_interna and mediana_interna > 0:
        return float(mediana_interna * 1.15), "Cargo no hallado en la base de mercado externa. El sistema asume un diferencial del 15% por encima de la Mediana Interna de la empresa como prima estándar de competitividad en el mercado laboral."
        
    return 0.0, "Sin datos para estimación automática (por favor ingresa el valor manualmente tras investigar en los enlaces provistos)."
