def flujo_caja_neto(ingresos, costos_operativos, impuestos, otros_gastos):
    """
    Calcula el flujo de caja neto.

    Parámetros:
        ingresos (float): Total de ingresos.
        costos_operativos (float): Costos operativos del periodo.
        impuestos (float): Valor pagado en impuestos.
        otros_gastos (float): Otros gastos adicionales.

    Retorna:
        float: Flujo de caja neto.
    """
    return ingresos - costos_operativos - impuestos - otros_gastos



def cuota_prestamo(principal, tasa_anual, anios, pagos_por_anio):
    """
    Calcula la cuota periódica de un préstamo con fórmula de anualidad.

    Parámetros:
        principal (float): Monto del préstamo.
        tasa_anual (float): Tasa anual en decimal.
        anios (int): Número de años del préstamo.
        pagos_por_anio (int): Cantidad de pagos por año.

    Retorna:
        float: Valor de la cuota periódica.
    """
    tasa_periodica = tasa_anual / pagos_por_anio
    numero_pagos = anios * pagos_por_anio

    if tasa_periodica == 0:
        return principal / numero_pagos

    cuota = principal * (tasa_periodica * (1 + tasa_periodica) ** numero_pagos) / ((1 + tasa_periodica) ** numero_pagos - 1)
    return cuota



def punto_equilibrio(costos_fijos, precio_unitario, costo_variable_unitario, impuesto_pct=0):
    """
    Calcula el punto de equilibrio en unidades.

    Parámetros:
        costos_fijos (float): Costos fijos totales.
        precio_unitario (float): Precio de venta por unidad.
        costo_variable_unitario (float): Costo variable por unidad.
        impuesto_pct (float): Porcentaje de impuesto aplicado sobre la utilidad.

    Retorna:
        float o str: Unidades necesarias para alcanzar el equilibrio.
    """
    margen_unitario = (precio_unitario - costo_variable_unitario) * (1 - impuesto_pct / 100)

    if margen_unitario <= 0:
        return "Error: el margen unitario debe ser mayor que cero"

    return costos_fijos / margen_unitario



def depreciacion_lineal_periodo(costo_activo, valor_residual, vida_util_anios, anio_consultado):
    """
    Calcula la depreciación acumulada hasta un año específico usando línea recta.

    Parámetros:
        costo_activo (float): Costo inicial del activo.
        valor_residual (float): Valor residual esperado.
        vida_util_anios (int): Vida útil del activo en años.
        anio_consultado (int): Año que se desea consultar.

    Retorna:
        float o str: Depreciación acumulada hasta el año indicado.
    """
    if vida_util_anios <= 0:
        return "Error: la vida útil debe ser mayor que cero"

    if anio_consultado < 1 or anio_consultado > vida_util_anios:
        return "Error: año consultado fuera del rango de vida útil"

    depreciacion_anual = (costo_activo - valor_residual) / vida_util_anios
    return depreciacion_anual * anio_consultado



def valor_futuro_inversion(capital_inicial, aporte_mensual, tasa_anual, anios):
    """
    Calcula el valor futuro de una inversión con aportes mensuales.

    Parámetros:
        capital_inicial (float): Capital inicial invertido.
        aporte_mensual (float): Aporte realizado cada mes.
        tasa_anual (float): Tasa anual en decimal.
        anios (int): Tiempo total en años.

    Retorna:
        float: Valor futuro estimado.
    """
    tasa_mensual = tasa_anual / 12
    meses = anios * 12

    if tasa_mensual == 0:
        return capital_inicial + (aporte_mensual * meses)

    valor_capital = capital_inicial * (1 + tasa_mensual) ** meses
    valor_aportes = aporte_mensual * (((1 + tasa_mensual) ** meses - 1) / tasa_mensual)

    return valor_capital + valor_aportes



def costo_energia_mensual(potencia_kw, horas_dia, dias_mes, tarifa_kwh):
    """
    Calcula el costo mensual de consumo energético.

    Parámetros:
        potencia_kw (float): Potencia del equipo en kW.
        horas_dia (float): Horas de uso por día.
        dias_mes (int): Días de uso en el mes.
        tarifa_kwh (float): Tarifa por kWh.

    Retorna:
        float: Costo mensual de energía.
    """
    consumo_kwh = potencia_kw * horas_dia * dias_mes
    return consumo_kwh * tarifa_kwh



def produccion_neta_petroleo(produccion_liquida_bpd, bsw_pct, dias_produccion, precio_barril):
    """
    Calcula el ingreso bruto por producción neta de petróleo.

    Parámetros:
        produccion_liquida_bpd (float): Producción líquida diaria en barriles.
        bsw_pct (float): Porcentaje de agua y sedimentos.
        dias_produccion (int): Días efectivos de producción.
        precio_barril (float): Precio por barril de petróleo.

    Retorna:
        float: Ingreso bruto estimado.
    """
    fraccion_petroleo = 1 - (bsw_pct / 100)
    barriles_netos = produccion_liquida_bpd * fraccion_petroleo * dias_produccion
    return barriles_netos * precio_barril



def factor_capacidad_energia(generacion_real_mwh, capacidad_mw, horas_periodo, disponibilidad_pct):
    """
    Calcula el factor de capacidad ajustado por disponibilidad.

    Parámetros:
        generacion_real_mwh (float): Energía real generada en MWh.
        capacidad_mw (float): Capacidad instalada en MW.
        horas_periodo (float): Horas totales del periodo.
        disponibilidad_pct (float): Disponibilidad operativa en porcentaje.

    Retorna:
        float o str: Factor de capacidad en porcentaje.
    """
    capacidad_ajustada = capacidad_mw * horas_periodo * (disponibilidad_pct / 100)

    if capacidad_ajustada == 0:
        return "Error: la capacidad ajustada no puede ser cero"

    return (generacion_real_mwh / capacidad_ajustada) * 100



def precio_venta_final(costo_base, margen_ganancia_pct, descuento_pct, iva_pct):
    """
    Calcula el precio final de venta aplicando margen, descuento e IVA.

    Parámetros:
        costo_base (float): Costo base del producto.
        margen_ganancia_pct (float): Margen de ganancia deseado en porcentaje.
        descuento_pct (float): Descuento aplicado en porcentaje.
        iva_pct (float): IVA aplicado en porcentaje.

    Retorna:
        float: Precio final de venta.
    """
    precio_con_margen = costo_base * (1 + margen_ganancia_pct / 100)
    precio_con_descuento = precio_con_margen * (1 - descuento_pct / 100)
    precio_final = precio_con_descuento * (1 + iva_pct / 100)
    return precio_final



def disponibilidad_servicio(total_horas, horas_caida, mantenimientos_programados, penalizacion_pct=0):
    """
    Calcula la disponibilidad real de un servicio o sistema.

    Parámetros:
        total_horas (float): Horas totales del periodo.
        horas_caida (float): Horas no disponibles por fallas.
        mantenimientos_programados (float): Horas detenidas por mantenimiento.
        penalizacion_pct (float): Ajuste o penalización adicional en porcentaje.

    Retorna:
        float o str: Disponibilidad real en porcentaje.
    """
    tiempo_disponible = total_horas - horas_caida - mantenimientos_programados

    if total_horas <= 0:
        return "Error: el total de horas debe ser mayor que cero"

    disponibilidad = (tiempo_disponible / total_horas) * 100
    disponibilidad_ajustada = disponibilidad - penalizacion_pct

    return max(disponibilidad_ajustada, 0)
