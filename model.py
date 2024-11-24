import pandas as pd
from datetime import datetime
from joblib import load


def prediccion ( test_df, test_y_df):
   modelo = load('multi_output_forest.joblib')
   y_pred_test = modelo.predict(test_df)
   lista_predicciones = test_df.copy()

   
   y_pred_test_reshaped = y_pred_test.reshape(-1, 25)

   y_pred_df = pd.DataFrame(y_pred_test_reshaped, columns=[f"Predicted_{i+1}" for i in range(25)])
   predictions_df = pd.DataFrame()
   lista_predicciones = pd.concat([test_df.iloc[:, 25:], y_pred_df], axis=1)
   predictions_df = pd.concat([predictions_df, y_pred_df], ignore_index=True)

   n_iterations = 11
   
   for i in range(n_iterations):

      lista_predicciones.columns = [i for i in range(300)]

      y_pred_test = modelo.predict(lista_predicciones)
      y_pred_test_reshaped = y_pred_test.reshape(-1, 25)
      y_pred_df = pd.DataFrame(y_pred_test_reshaped, columns=[f"Predicted_{i+1}" for i in range(25)])
      predictions_df = pd.concat([predictions_df, y_pred_df], ignore_index=True)

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

   fechas = pd.to_datetime(["2024-09-01", "2024-10-01", "2024-11-01", "2024-12-01", "2025-01-01", "2025-02-01","2025-03-01","2025-04-01","2025-05-01","2025-06-01","2025-07-01","2025-08-01"])

   if len(predictions_df) == len(fechas):
      predictions_df['Fecha'] = fechas
   else:
      print(f"El número de filas de predictions_df ({len(predictions_df)}) no coincide con el número de fechas ({len(fechas)})")
   
   return predictions_df 