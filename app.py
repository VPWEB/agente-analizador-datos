import streamlit as st
import anthropic
import pandas as pd
import json
from dotenv import load_dotenv
import os

# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Agente Analizador de Datos",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Agente Analizador de Datos")
st.caption("Haz preguntas en lenguaje natural sobre tu CSV")

# ============================================================
# ESTADO DE LA SESIÓN
# — Streamlit re-ejecuta el script entero en cada interacción,
#   por eso guardamos el estado aquí
# ============================================================

if "df" not in st.session_state:
    st.session_state.df = None

if "mensajes_chat" not in st.session_state:
    st.session_state.mensajes_chat = []  # historial visible en pantalla

if "mensajes_api" not in st.session_state:
    st.session_state.mensajes_api = []   # historial que mandamos a la API

# ============================================================
# HERRAMIENTAS — igual que en agente.py
# ============================================================

def cargar_datos(ruta: str) -> str:
    st.session_state.df = pd.read_csv(ruta)
    df = st.session_state.df
    info = {
        "filas": len(df),
        "columnas": list(df.columns),
        "tipos": df.dtypes.astype(str).to_dict()
    }
    return json.dumps(info, ensure_ascii=False)

def calcular_estadisticas(columna: str) -> str:
    df = st.session_state.df
    if df is None:
        return "Error: primero carga los datos"
    if columna not in df.columns:
        return f"Error: columna '{columna}' no existe"
    return json.dumps(df[columna].describe().to_dict(), ensure_ascii=False)

def contar_por_categoria(columna: str) -> str:
    df = st.session_state.df
    if df is None:
        return "Error: primero carga los datos"
    if columna not in df.columns:
        return f"Error: columna '{columna}' no existe"
    return json.dumps(df[columna].value_counts().head(10).to_dict(), ensure_ascii=False)

def filtrar_datos(columna: str, valor: str) -> str:
    df = st.session_state.df
    if df is None:
        return "Error: primero carga los datos"
    filtrado = df[df[columna].astype(str) == valor]
    return f"Filas encontradas con {columna}='{valor}': {len(filtrado)}"

def obtener_muestra(n_filas: int = 5) -> str:
    df = st.session_state.df
    if df is None:
        return "Error: primero carga los datos"
    return df.head(n_filas).to_string()

herramientas_disponibles = {
    "cargar_datos": cargar_datos,
    "calcular_estadisticas": calcular_estadisticas,
    "contar_por_categoria": contar_por_categoria,
    "filtrar_datos": filtrar_datos,
    "obtener_muestra": obtener_muestra
}

tools = [
    {
        "name": "cargar_datos",
        "description": "Carga un archivo CSV desde una ruta y devuelve sus columnas y tipos de datos",
        "input_schema": {
            "type": "object",
            "properties": {
                "ruta": {"type": "string", "description": "Ruta al archivo CSV"}
            },
            "required": ["ruta"]
        }
    },
    {
        "name": "calcular_estadisticas",
        "description": "Calcula media, mínimo, máximo y otros stats de una columna numérica",
        "input_schema": {
            "type": "object",
            "properties": {
                "columna": {"type": "string", "description": "Nombre de la columna"}
            },
            "required": ["columna"]
        }
    },
    {
        "name": "contar_por_categoria",
        "description": "Cuenta cuántas veces aparece cada valor en una columna categórica",
        "input_schema": {
            "type": "object",
            "properties": {
                "columna": {"type": "string", "description": "Nombre de la columna"}
            },
            "required": ["columna"]
        }
    },
    {
        "name": "filtrar_datos",
        "description": "Filtra las filas del dataset por un valor concreto en una columna",
        "input_schema": {
            "type": "object",
            "properties": {
                "columna": {"type": "string", "description": "Columna por la que filtrar"},
                "valor": {"type": "string", "description": "Valor a buscar"}
            },
            "required": ["columna", "valor"]
        }
    },
    {
        "name": "obtener_muestra",
        "description": "Devuelve las primeras filas del dataset",
        "input_schema": {
            "type": "object",
            "properties": {
                "n_filas": {"type": "integer", "description": "Número de filas (por defecto 5)"}
            },
            "required": []
        }
    }
]

# ============================================================
# SIDEBAR — carga del archivo y vista previa
# ============================================================

with st.sidebar:
    st.header("📁 Dataset")
    archivo = st.file_uploader("Sube tu CSV", type=["csv"])

    if archivo:
        st.session_state.df = pd.read_csv(archivo)
        st.success(f"✅ {len(st.session_state.df)} filas cargadas")
        st.dataframe(st.session_state.df.head(3), use_container_width=True)

        # Guardamos el archivo en disco para que la herramienta pueda leerlo
        st.session_state.df.to_csv("datos_subidos.csv", index=False)

    st.divider()
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.mensajes_chat = []
        st.session_state.mensajes_api = []
        st.rerun()

# ============================================================
# CHAT — historial de mensajes
# ============================================================

for mensaje in st.session_state.mensajes_chat:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

# ============================================================
# INPUT — caja de texto del usuario
# ============================================================

if pregunta := st.chat_input("Haz una pregunta sobre los datos..."):

    # Mostramos la pregunta del usuario
    st.session_state.mensajes_chat.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    # Añadimos al historial de la API
    st.session_state.mensajes_api.append({"role": "user", "content": pregunta})

    # ============================================================
    # BUCLE DEL AGENTE — igual que antes, pero mostrando en UI
    # ============================================================

    load_dotenv()
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    # System prompt dinámico segun si hay datos cargados
    system_prompt = "Eres un agente analizador de datos. Responde siempre en español."

    if st.session_state.df is not None:
        columnas = list(st.session_state.df.columns)
        filas = len(st.session_state.df)
        system_prompt += f"""
        
    El usuario ya ha subido un CSV con {filas} filas y las siguientes columnas: {columnas}.
    Los datos YA ESTÁN CARGADOS en memoria. NO pidas ninguna ruta de archivo.
    Usa directamente las herramientas de análisis como contar_por_categoria, calcular_estadisticas, filtrar_datos u obtener_muestra.
    """
        
    with st.chat_message("assistant"):
        with st.spinner("El agente está pensando..."):

            while True:
                response = client.messages.create(
                    model="claude-opus-4-5",
                    max_tokens=2048,
                    tools=tools,
                    system=system_prompt,
                    messages=st.session_state.mensajes_api
                )

                if response.stop_reason == "end_turn":
                    for bloque in response.content:
                        if hasattr(bloque, "text"):
                            st.markdown(bloque.text)
                            st.session_state.mensajes_chat.append({
                                "role": "assistant",
                                "content": bloque.text
                            })
                    break

                if response.stop_reason == "tool_use":
                    st.session_state.mensajes_api.append({
                        "role": "assistant",
                        "content": response.content
                    })
                    resultados = []

                    for bloque in response.content:
                        if bloque.type == "tool_use":
                            # Mostramos qué herramienta está usando
                            with st.expander(f"🔧 Usando herramienta: `{bloque.name}`"):
                                st.json(bloque.input)

                            funcion = herramientas_disponibles[bloque.name]
                            resultado = funcion(**bloque.input)

                            resultados.append({
                                "type": "tool_result",
                                "tool_use_id": bloque.id,
                                "content": resultado
                            })

                    st.session_state.mensajes_api.append({
                        "role": "user",
                        "content": resultados
                    })