import pandas as pd
from model import train_predict_and_format_df

def process_data():
    data = pd.read_csv('https://docs.google.com/spreadsheets/d/1qwgm-JvaNb8brhYQBnGgvOQ9nQZOFP3aPRcHC_9VEAY/export?format=csv')
    # Convertir la columna 'Fecha' a tipo datetime
    data['Fecha'] = pd.to_datetime(data['Fecha'])
    data = data.sort_values(by='Fecha')


    train_data = data[data['Fecha'] < '2023-08-01']
    test_data = data[data['Fecha'] >= '2023-08-01']

    train_data.loc[:, 'Fecha'] = train_data['Fecha'].apply(lambda x: x.toordinal())
    test_data.loc[:, 'Fecha'] = test_data['Fecha'].apply(lambda x: x.toordinal())

    print("AQUI ESTOY MAL")
    train_df = pd.DataFrame()

    for i in range(0, len(train_data)-12, 1):

        block = train_data.iloc[i:i+12]

        train_df = pd.concat([train_df, pd.DataFrame([block.values.flatten()])], ignore_index=True)
    
    train_y_df = train_data[12:]
    return train_df, train_y_df

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
    print("WEJEEEE")
    print(df)
    test_y_df = df.copy()
    # dataframe_test_y['Fecha'] = dataframe_test_y['Fecha'].apply(lambda x: datetime.fromordinal(x))

    df[date_column] = df[date_column].apply(lambda x: x.toordinal())
    print(df)
    result_df = pd.DataFrame()

    for i in range(0, len(df) - block_size + 1):

        block = df.iloc[i:i + block_size]
        flattened_block = pd.DataFrame([block.values.flatten()])


        result_df = pd.concat([result_df, flattened_block], ignore_index=True)
    print(result_df)
    print("AQUI ESTOY BIEN")
    train_df, train_y_df = process_data()
    print("PASEE")
    result_rf = train_predict_and_format_df(train_df, train_y_df, result_df, test_y_df)
    return result_rf