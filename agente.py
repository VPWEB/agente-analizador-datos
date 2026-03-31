import anthropic
import pandas as pd
import json
from dotenv import load_dotenv
import os

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
# ============================================================
# HERRAMIENTAS — funciones Python que el agente puede usar
# ============================================================

df = None  # el dataframe global que cargaremos

def cargar_datos(ruta: str) -> str:
    """Carga el CSV y devuelve información básica del dataset."""
    global df
    df = pd.read_csv(ruta)
    info = {
        "filas": len(df),
        "columnas": list(df.columns),
        "tipos": df.dtypes.astype(str).to_dict()
    }
    return json.dumps(info, ensure_ascii=False)

def calcular_estadisticas(columna: str) -> str:
    """Calcula estadísticas básicas de una columna numérica."""
    if df is None:
        return "Error: primero carga los datos"
    if columna not in df.columns:
        return f"Error: la columna '{columna}' no existe"
    stats = df[columna].describe().to_dict()
    return json.dumps(stats, ensure_ascii=False)

def contar_por_categoria(columna: str) -> str:
    """Cuenta cuántas veces aparece cada valor en una columna."""
    if df is None:
        return "Error: primero carga los datos"
    if columna not in df.columns:
        return f"Error: la columna '{columna}' no existe"
    conteo = df[columna].value_counts().head(10).to_dict()
    return json.dumps(conteo, ensure_ascii=False)

def filtrar_datos(columna: str, valor: str) -> str:
    """Filtra el dataset por un valor concreto y devuelve cuántas filas hay."""
    if df is None:
        return "Error: primero carga los datos"
    filtrado = df[df[columna].astype(str) == valor]
    return f"Filas encontradas con {columna}='{valor}': {len(filtrado)}"

def obtener_muestra(n_filas: int = 5) -> str:
    """Devuelve las primeras N filas del dataset."""
    if df is None:
        return "Error: primero carga los datos"
    return df.head(n_filas).to_string()

# ============================================================
# DEFINICIÓN DE HERRAMIENTAS PARA LA API
# ============================================================

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
                "columna": {"type": "string", "description": "Nombre de la columna a analizar"}
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
        "description": "Devuelve las primeras filas del dataset para ver cómo son los datos",
        "input_schema": {
            "type": "object",
            "properties": {
                "n_filas": {"type": "integer", "description": "Número de filas a mostrar (por defecto 5)"}
            },
            "required": []
        }
    }
]

# Mapa nombre → función
herramientas_disponibles = {
    "cargar_datos": cargar_datos,
    "calcular_estadisticas": calcular_estadisticas,
    "contar_por_categoria": contar_por_categoria,
    "filtrar_datos": filtrar_datos,
    "obtener_muestra": obtener_muestra
}

# ============================================================
# EL BUCLE DEL AGENTE — exactamente igual que antes
# ============================================================

def ejecutar_agente(pregunta: str):
    print(f"\n👤 Pregunta: {pregunta}")
    print("-" * 50)

    mensajes = [{"role": "user", "content": pregunta}]

    while True:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2048,
            tools=tools,
            messages=mensajes
        )

        if response.stop_reason == "end_turn":
            for bloque in response.content:
                if hasattr(bloque, "text"):
                    print(f"\n🤖 Respuesta:\n{bloque.text}")
            break

        if response.stop_reason == "tool_use":
            mensajes.append({"role": "assistant", "content": response.content})
            resultados = []

            for bloque in response.content:
                if bloque.type == "tool_use":
                    print(f"🔧 Herramienta: {bloque.name} | Parámetros: {bloque.input}")
                    funcion = herramientas_disponibles[bloque.name]
                    resultado = funcion(**bloque.input)
                    print(f"✅ Resultado: {resultado[:200]}...")  # mostramos solo los primeros 200 caracteres
                    resultados.append({
                        "type": "tool_result",
                        "tool_use_id": bloque.id,
                        "content": resultado
                    })

            mensajes.append({"role": "user", "content": resultados})

# ============================================================
# PRUEBA — conversación con el agente
# ============================================================

if __name__ == "__main__":
    # Primero cargamos los datos
    ejecutar_agente("Carga el archivo datos.csv y dime qué columnas tiene y cuántas filas")

    # Luego hacemos preguntas de análisis
    ejecutar_agente("¿Cuáles son los tipos de incidencia más frecuentes?")