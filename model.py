import pandas as pd
from datetime import datetime
from joblib import load


def prediccion ( test_df, test_y_df):
   modelo = load('multi_output_forest.joblib')
   y_pred_test = modelo.predict(test_df)
   lista_predicciones = test_df.copy()

   
   y_pred_test_reshaped = y_pred_test.reshape(-1, 25)  # Asegúrate de que tenga la forma (n_filas, 25)

   # Convertir a DataFrame con nombres de columnas apropiados
   y_pred_df = pd.DataFrame(y_pred_test_reshaped, columns=[f"Predicted_{i+1}" for i in range(25)])
   predictions_df = pd.DataFrame()
   # Concatenar el DataFrame test_df (desde el índice 25) y y_pred_df
   lista_predicciones = pd.concat([test_df.iloc[:, 25:], y_pred_df], axis=1)
   predictions_df = pd.concat([predictions_df, y_pred_df], ignore_index=True)

   # Número de repeticiones
   n_iterations = 12  # Ajusta este número según lo que necesites

   # Iterar sobre el número de veces que desees hacer la predicción
   for i in range(n_iterations):
      # Asegurarse de que las columnas tengan nombres enteros del 0 al 299
      lista_predicciones.columns = [i for i in range(300)]

      # Realizar la predicción para lista_predicciones
      y_pred_test = modelo.predict(lista_predicciones)
      # Redimensionar las predicciones (asegurarse de que sea de la forma (n_filas, 25))
      y_pred_test_reshaped = y_pred_test.reshape(-1, 25)
      # Convertir las predicciones a DataFrame con nombres de columnas apropiados
      y_pred_df = pd.DataFrame(y_pred_test_reshaped, columns=[f"Predicted_{i+1}" for i in range(25)])
      # Agregar las predicciones como una nueva fila en el DataFrame predictions_df
      predictions_df = pd.concat([predictions_df, y_pred_df], ignore_index=True)

      # Imprimir el progreso (opcional)
      print(f"Iteration {i+1} completed.")

      # Actualizar lista_predicciones con las predicciones acumuladas como nuevas columnas
      lista_predicciones = pd.concat([lista_predicciones.iloc[:, 25:], y_pred_df], axis=1)



   # Mostrar el DataFrame
   predictions_df.columns = ['RI Costo mercancia/bienes vendidos',
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

   # Lista de fechas que deseas asignar
   fechas = pd.to_datetime(["2024-08-01","2024-09-01", "2024-10-01", "2024-11-01", "2024-12-01", "2025-01-01", "2025-02-01","2025-03-01","2025-04-01","2025-05-01","2025-06-01","2025-07-01","2025-08-01"])

   # Verificar si el número de filas en predictions_df coincide con la cantidad de fechas
   if len(predictions_df) == len(fechas):
      # Asignar las fechas al DataFrame
      predictions_df['Fecha'] = fechas
   else:
      print(f"El número de filas de predictions_df ({len(predictions_df)}) no coincide con el número de fechas ({len(fechas)})")


   return predictions_df 