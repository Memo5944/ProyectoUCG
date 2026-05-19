import pandas as pd

def preparar_datos(df):
    """
    Estandariza los nombres de columnas y calcula el Salario Total.
    Asume columnas como: 'Trabajador', 'Cargo', 'Antigüedad', 'Edad', 'Salario Base', 'HE 25%', 'HE 50%', 'HE 100%'
    """
    # Intentar normalizar nombres de columnas a minúsculas y sin espacios extras para facilitar acceso
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Buscar posibles nombres de columnas para salario y horas extras
    col_salario = next((c for c in df.columns if 'base' in c or 'salario' in c), None)
    
    # Calcular salario total si no existe
    if col_salario:
        df['salario_total'] = df[col_salario].fillna(0)
        
        # Sumar horas extras si existen
        he_cols = [c for c in df.columns if 'he' in c or 'hora' in c or 'extra' in c]
        for col in he_cols:
            df['salario_total'] += df[col].fillna(0)
    
    return df

def obtener_metricas_cargo(df, cargo):
    """
    Obtiene métricas estadísticas (mediana, promedio, min, max) para un cargo específico.
    """
    df_cargo = df[df['cargo'].str.lower() == cargo.lower()]
    if df_cargo.empty:
        return None
    
    metricas = {
        'mediana': df_cargo['salario_total'].median(),
        'promedio': df_cargo['salario_total'].mean(),
        'min': df_cargo['salario_total'].min(),
        'max': df_cargo['salario_total'].max(),
        'cantidad': len(df_cargo)
    }
    return metricas

def evaluar_incremento(salario_actual, porcentaje_incremento, porcentaje_inflacion):
    """
    Calcula el impacto del incremento y la inflación.
    """
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
