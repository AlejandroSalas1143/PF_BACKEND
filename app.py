import io
from fastapi import FastAPI, File, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import BytesIO
import unidecode
from functions import create_rolling_flattened_blocks, calcular_indicadores
import google.generativeai as genai
from config import API_KEY 
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las solicitudes de cualquier origen. Cambia esto en producción.
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP: GET, POST, etc.
    allow_headers=["*"],  # Permite todos los headers
)

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

        columnas_a_convertir = [
            'RI Costo mercancia/bienes vendidos', 'RI Valor promedio del inventario',
            'LIQ Activos corrientes', 'LIQ Pasivos corrientes',
            'ECP Pasivo no corriente', 'ECP Patrimonio neto',
            'ELP Pasivo corriente', 'ELP Patrimonio neto',
            'CI Utilidades antes de intereses e impuestos', 'CI Gastos financieros',
            'MUB Ingresos totales', 'MUB Costo de productos y servicios',
            'MUN Gastos fijos y variables', 'MUN Gastos e impuestos',
            'MUN Ingresos totales', 'ROA Ganancia antes de impuestos',
            'ROA Impuestos pagados', 'ROA Activos totales',
            'ROI Ganancia', 'ROI Inversion',
            'SOL Activos no corrientes', 'SOL Activos corrientes',
            'SOL Pasivos corrientes', 'SOL Pasivos no corrientes'
        ]

        for col in columnas_a_convertir:
            df_transposed[col] = pd.to_numeric(df_transposed[col], errors='coerce')
        
        df_transposed.to_csv('process_data.csv', index=False)
        indicadores_data= calcular_indicadores(df_transposed)
        indicadores_data.to_csv('data_indicadores.csv', index=False, float_format="%.3f")
        final = create_rolling_flattened_blocks( df_transposed, 'Fecha', block_size=12)

        result = final.to_dict(orient="records")
        
        return result
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/prediction")
async def get_prediction():
    df_prediccion = pd.read_csv("result.csv")
    df_ordenado = df_prediccion.sort_values(by="Fecha")
    result = df_ordenado.to_dict(orient="records")
    return result

@app.get("/prediction-indicators")
async def get_indicadores(nombre: str):

    df_indicadores = pd.read_csv("prediccion_indicadores.csv")

    if nombre not in df_indicadores.columns:
        raise HTTPException(status_code=404, detail="Indicador no encontrado")

    result = df_indicadores[["Fecha", nombre]].sort_values(by="Fecha")

    result_list = result.to_dict(orient="records")

    return result_list

@app.get("/data")
async def get_data():
    df_data = pd.read_csv("process_data.csv")
    df_ordenado = df_data.sort_values(by="Fecha")
    result = df_ordenado.to_dict(orient="records")
    return result

@app.get("/data-indicators")
async def get_data_indicadores(nombre: str):
    df_data = pd.read_csv("data_indicadores.csv")

    if nombre not in df_data.columns:
        raise HTTPException(status_code=404, detail="Indicador no encontrado")

    result = df_data[["Fecha", nombre]].sort_values(by="Fecha")

    result_list = result.to_dict(orient="records")
    return result_list

genai.configure(api_key=API_KEY)
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 300,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)
prompts = [
    "A partir de los datos proporcionados\n {informacion}\n\nPregunta: {pregunta}\nPor favor, proporciona una respuesta en un máximo de 300 palabras.",
    "Basado en los datos que me diste, responde la siguiente pregunta: {pregunta}\nInformación: {informacion}\nLimítate a 150 palabras.",
    "Utilizando la información proporcionada: {informacion}, por favor responde a la pregunta: {pregunta} de manera clara y concisa, máximo 150 palabras.",
]
# Función para generar respuesta según el número de prompt
def generar_respuesta(informacion, pregunta, prompt_numero):
    prompt = prompts[prompt_numero].format(informacion=informacion, pregunta=pregunta)
    
    # Llamada al modelo para generar respuesta
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(prompt)
    
    return response.text




@app.post("/preguntar")
async def preguntar(request: Request):
    data = await request.json()
    preguntas = pd.read_csv("data_indicadores.csv")
    
    nombres_variables = data["nombres_variables"]  # Lista con los nombres de las variables
    pregunta = data["pregunta"]
    prompt_numero = data["prompt_numero"]
    
    # Validar que las variables existan en el DataFrame
    columnas_disponibles = [col for col in nombres_variables if col in preguntas.columns]
    if not columnas_disponibles:
        return {"error": "Ninguna de las variables proporcionadas existe en el archivo CSV."}
    
    # Obtener los datos de las columnas solicitadas
    informacion = preguntas[columnas_disponibles].to_dict(orient="records")
    
    # Generar la respuesta
    respuesta = generar_respuesta(informacion, pregunta, prompt_numero)
    
    return {"respuesta": respuesta}
