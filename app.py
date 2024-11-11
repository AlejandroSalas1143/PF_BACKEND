import io
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import BytesIO
import unidecode
from functions import create_rolling_flattened_blocks 



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las solicitudes de cualquier origen. Cambia esto en producción.
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP: GET, POST, etc.
    allow_headers=["*"],  # Permite todos los headers
)

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if file.content_type != 'text/csv':
        return {"error": "Invalid file type. Please upload a CSV file."}

    # Leer el contenido del archivo en un DataFrame de pandas
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    # Realiza cualquier procesamiento necesario en el DataFrame `df`
    # Por ejemplo, contar filas
    num_rows = df.shape[0]

    return {"message": f"CSV file received successfully!", "num_rows": num_rows}



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
        print("VOY POR AQUI")
        # print(df_transposed)
        final = create_rolling_flattened_blocks(df_transposed, 'Fecha', block_size=12)

        result = final.to_dict(orient="records")
        
        return result
    except Exception as e:
        return {"error": str(e)}

# async def upload_excel(file: UploadFile = File(...)):
#     # Cargar el archivo Excel en un DataFrame de pandas
#     contents = await file.read()
#     df = pd.read_excel(BytesIO(contents), sheet_name='Hoja1', usecols="B:Z")

#     # Limpiar y organizar los datos
#     df_cleaned = df.drop([0, 1]).reset_index(drop=True)
#     df_cleaned.columns = [
#         'Id', 'Enero_2024', 'Febrero_2024', 'Marzo_2024', 'Abril_2024', 'Mayo_2024', 'Junio_2024', 'Julio_2024',
#         'Agosto_2024', 'Enero_2023', 'Febrero_2023', 'Marzo_2023', 'Abril_2023', 'Mayo_2023', 'Junio_2023', 'Julio_2023',
#         'Agosto_2023', 'Septiembre_2023', 'Octubre_2023', 'Noviembre_2023', 'Diciembre_2023'
#     ] + list(df.columns[21:])
#     df_cleaned = df_cleaned.loc[:, ~df_cleaned.columns.str.contains('Unnamed')]
#     df_cleaned = df_cleaned.dropna(how='all')

#     # Convertir los datos limpios a un formato JSON para enviarlos como respuesta
#     result = df_cleaned.to_dict(orient="records")
#     return {"data": result}
