from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta


def train_predict_and_format_df(train_df, train_y_df, test_df, test_y_df, random_state=42):
    """
    Entrena un modelo Random Forest de múltiples salidas, realiza predicciones, y formatea los resultados en un DataFrame.

    Args:
        train_df (pd.DataFrame): Datos de entrenamiento para las características.
        train_y_df (pd.DataFrame): Datos de entrenamiento para las etiquetas (salidas).
        test_df (pd.DataFrame): Datos de prueba para realizar las predicciones.
        test_y_df (pd.DataFrame): Datos de prueba con la columna de Fecha para asignar a las predicciones.
        random_state (int): Semilla para el modelo Random Forest (por defecto 42).

    Returns:
        pd.DataFrame: DataFrame con las predicciones formateadas y la columna de Fecha convertida a formato datetime.
    """
    forest = RandomForestRegressor(random_state=random_state)
    multi_output_forest = MultiOutputRegressor(forest)

    multi_output_forest.fit(train_df, train_y_df)
    print("Lo entrene")
    print(test_df)
    y_pred_test = multi_output_forest.predict(test_df)
    print("lo hice")
    df = pd.DataFrame(y_pred_test)

    pd.set_option('display.float_format', '{:.0f}'.format)

    df.columns = ['RI Costo mercancia/bienes vendidos',
       'RI Valor promedio del inventario', 'LIQ Activos corrientes',
       'LIQ Pasivos corrientes', 'ECP Pasivo no corriente',
       'ECP Patrimonio neto', 'ELP Pasivo corriente', 'ELP Patrimonio neto',
       'CI Utilidades antes de intereses e impuestos', 'CI Gastos financieros',
       'MUB Ingresos totales', 'MUB Costo de productos y servicios',
       'MUN Gastos fijos y variables', 'MUN Gastos e impuestos',
       'MUN Ingresos totales', 'ROA Ganancia antes de impuestos',
       'ROA Impuestos pagados', 'ROA Activos totales', 'ROI Ganancia',
       'ROI Inversion', 'SOL Activos no corrientes', 'SOL Activos corrientes',
       'SOL Pasivos corrientes', 'SOL Pasivos no corrientes', 'Fecha']
    print("YEII")
    print(test_y_df)

    # Obtener la última fecha de test_y_df['Fecha']
    last_date = test_y_df['Fecha'].max()
    print(last_date)
    # Sumarle un mes a la última fecha
    new_date = last_date + relativedelta(months=1)

    # Asignar la nueva fecha a toda la columna 'Fecha' de df
    df['Fecha'] = new_date

    # df['Fecha'] = test_y_df['Fecha'].reset_index(drop=True)
    # df['Fecha'] = df['Fecha'].apply(lambda x: datetime.fromordinal(x))
    # print("YEIII2")
    # print(df)
    return df
