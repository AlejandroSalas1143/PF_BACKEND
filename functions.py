import pandas as pd
from model import prediccion
import os
def create_rolling_flattened_blocks(df, date_column, block_size=12):
    """
    Crea un nuevo DataFrame aplanado a partir de bloques de tamaño especificado
    en un DataFrame original, ordenado por la columna de fecha.

    Args:
        df (pd.DataFrame): El DataFrame original.
        date_column (str): El nombre de la columna de fechas.
        block_size (int): El número de filas por bloque (por defecto 12).

    Returns:
        pd.DataFrame: Un nuevo DataFrame donde cada fila es un bloque aplanado de 'block_size' filas.
    """
    df[date_column] = pd.to_datetime(df[date_column])
    df = df.sort_values(by=date_column)

    test_y_df = df.copy()

    df[date_column] = df[date_column].apply(lambda x: x.toordinal())

    result_df = pd.DataFrame()

    for i in range(0, len(df) - block_size + 1):

        block = df.iloc[i:i + block_size]
        flattened_block = pd.DataFrame([block.values.flatten()])


        result_df = pd.concat([result_df, flattened_block], ignore_index=True)
    
    result_rf = prediccion( result_df, test_y_df)
    result_rf.to_csv('result.csv', index=False)
    print(f"Archivo guardado en: {os.path.abspath('result.csv')}")
    indicadores_prediccion = calcular_indicadores(result_rf)
    indicadores_prediccion.to_csv('prediccion_indicadores.csv', index=False)
    return result_rf



def calcular_indicadores(data):
    # Crear un nuevo DataFrame para los resultados
    resultados = pd.DataFrame()

    # Calcular cada indicador y agregarlo al DataFrame de resultados
    resultados['ROTACION INVENTARIO'] = data['RI Costo mercancia/bienes vendidos'] / data['RI Valor promedio del inventario']
    resultados['LIQUIDEZ'] = data['LIQ Activos corrientes'] / data['LIQ Pasivos corrientes']
    resultados['ENDEUDAMIENTO CORTO PLAZO'] = data['ECP Pasivo no corriente'] / data['ECP Patrimonio neto']
    resultados['ENDEUDAMIENTO LARGO PLAZO'] = data['ELP Pasivo corriente'] / data['ELP Patrimonio neto']
    resultados['COBERTURA DE INTERESES'] = data['CI Utilidades antes de intereses e impuestos'] / data['CI Gastos financieros']
    resultados['MARGEN DE UTILIDAD BRUTA (%)'] = ((data['MUB Ingresos totales'] - data['MUB Costo de productos y servicios']) / data['MUB Ingresos totales']) * 100
    resultados['MARGEN DE UTILIDAD NETA (%)'] = ((data['MUN Ingresos totales'] - data['MUN Gastos fijos y variables'] - data['MUN Gastos e impuestos']) / data['MUN Ingresos totales']) * 100
    resultados['ROA (%)'] = ((data['ROA Ganancia antes de impuestos'] - data['ROA Impuestos pagados']) / data['ROA Activos totales']) * 100
    resultados['ROI (%)'] = (data['ROI Ganancia'] / data['ROI Inversion']) * 100
    resultados['SOLVENCIA'] = (data['SOL Activos corrientes'] + data['SOL Activos no corrientes']) / (data['SOL Pasivos corrientes'] + data['SOL Pasivos no corrientes'])
    resultados['Fecha'] = data['Fecha']
    
    resultados = resultados.round(3)
    
    return resultados