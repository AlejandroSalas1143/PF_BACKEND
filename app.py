import io
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import BytesIO
import unidecode
from functions import create_rolling_flattened_blocks, calcular_indicadores

# from model import train_predict_and_format_df

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las solicitudes de cualquier origen. Cambia esto en producción.
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP: GET, POST, etc.
    allow_headers=["*"],  # Permite todos los headers
)

# train_df, train_y_df = process_data()
# multi_output_forest = train_predict_and_format_df(train_df, train_y_df)

# @app.post("/upload-csv")
# async def upload_csv(file: UploadFile = File(...)):
#     if file.content_type != 'text/csv':
#         return {"error": "Invalid file type. Please upload a CSV file."}

#     contents = await file.read()
#     df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

#     num_rows = df.shape[0]

#     return {"message": f"CSV file received successfully!", "num_rows": num_rows}



@app.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    try:
        df = pd.read_excel(file.file, sheet_name='Hoja1', usecols="B:N")
        
        df_cleaned = df.drop([0, 1]).reset_index(drop=True)
        df_cleaned.columns = ['Id', 'Enero_2024', 'Febrero_2024', 'Marzo_2024', 'Abril_2024', 'Mayo_2024', 
                              'Junio_2024', 'Julio_2024', 'Agosto_2024', 'Septiembre_2023', 'Octubre_2023', 'Noviembre_2023', 'Diciembre_2023'] \
                            + list(df_cleaned.columns[21:])
        
        df_cleaned = df_cleaned.loc[:, ~df_cleaned.columns.str.contains('Unnamed')]
        df_cleaned = df_cleaned.dropna(how='all')

        df_cleaned = df_cleaned.where(pd.notnull(df_cleaned), None)

        df_transposed = df_cleaned.set_index('Id').T.reset_index()

        df_transposed['Mes'] = df_transposed['index'].apply(lambda x: x.split('_')[0])
        df_transposed['Anho'] = df_transposed['index'].apply(lambda x: x.split('_')[1])

        meses_map = {
            'Enero': '1', 'Febrero': '2', 'Marzo': '3', 'Abril': '4', 'Mayo': '5', 'Junio': '6',
            'Julio': '7', 'Agosto': '8', 'Septiembre': '9', 'Octubre': '10', 'Noviembre': '11', 'Diciembre': '12'
        }

        df_transposed['Numero del mes'] = df_transposed['Mes'].map(meses_map)

        df_transposed['Fecha'] = pd.to_datetime(df_transposed['Anho'].astype(str) + '-' + df_transposed['Numero del mes'].astype(str), format='%Y-%m', errors='coerce')

        df_transposed = df_transposed.drop(columns=['index'])

        df_transposed.columns = [unidecode.unidecode(col) for col in df_transposed.columns]

        df_transposed = df_transposed.drop(['RC Ventas a credito periodo fiscal anterior', 'RC Cuentas por cobrar promedio','Mes', 'Anho', 'Numero del mes'], axis=1)
        
        df_transposed.to_csv('process_data.csv', index=False)
        indicadores_data= calcular_indicadores(df_transposed)

        indicadores_data.to_csv('data_indicadores.csv', index=False)
        final = create_rolling_flattened_blocks( df_transposed, 'Fecha', block_size=12)

        result = final.to_dict(orient="records")
        
        return result
    except Exception as e:
        return {"error": str(e)}

@app.get("/indicadores")
async def get_indicadores(nombre: str):
    # Leer el archivo CSV
    df_indicadores = pd.read_csv("prediccion_indicadores.csv")
    # Verificar si el nombre del indicador existe en las columnas
    if nombre not in df_indicadores.columns:
        raise HTTPException(status_code=404, detail="Indicador no encontrado")
    
    # Retornar los valores del indicador y la fecha correspondiente
    # result = df_indicadores[["Fecha", nombre]]result = df_indicadores[["Fecha", nombre]].sort_values(by="Fecha")

    result = df_indicadores[["Fecha", nombre]].sort_values(by="Fecha")


    print(result)
    # Convertir a una lista de diccionarios (uno por cada fila)
    result_list = result.to_dict(orient="records")
    print(result_list)
    return result_list

@app.get("/data")
async def get_data():
    df_data = pd.read_csv("data_indicadores.csv")
    result = df_data.to_dict(orient="records")
    return result