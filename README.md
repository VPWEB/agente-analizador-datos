# 🤖 Agente Analizador de Datos

Agente de inteligencia artificial que permite analizar cualquier dataset CSV
mediante preguntas en lenguaje natural. Construido con la API de Anthropic
(Claude) usando tool use nativo.

## 🎯 ¿Qué hace?

El agente recibe una pregunta en lenguaje natural, decide qué herramienta
de análisis necesita, la ejecuta sobre los datos reales y devuelve
una respuesta clara y estructurada.

Ejemplo:
> "¿Cuáles son los tipos de incidencia más frecuentes?"

El agente razona, selecciona la herramienta correcta y responde:
> "Los tipos más frecuentes son: Refund request (20.8%), Technical issue (20.7%)..."

## 🛠️ Herramientas del agente

| Herramienta | Función |
|---|---|
| `obtener_muestra` | Muestra las primeras filas del dataset |
| `calcular_estadisticas` | Media, mínimo, máximo de columnas numéricas |
| `contar_por_categoria` | Frecuencia de valores en columnas categóricas |
| `filtrar_datos` | Filtra filas por columna y valor |
| `cargar_datos` | Carga un CSV desde ruta |

## 🏗️ Arquitectura
```
Usuario (lenguaje natural)
        ↓
   Claude (razona y decide)
        ↓
   Tool use (elige herramienta)
        ↓
   Python + Pandas (ejecuta)
        ↓
   Claude (interpreta resultado)
        ↓
   Respuesta estructurada
```

## 🚀 Cómo ejecutarlo

**1. Clona el repositorio**
```bash
git clone https://github.com/VPWEB/agente-analizador-datos.git
cd agente-analizador-datos
```

**2. Crea el entorno virtual e instala dependencias**
```bash
python -m venv venv
venv\Scripts\activate
pip install anthropic pandas streamlit python-dotenv
```

**3. Configura tu API key de Anthropic**

Crea un archivo `.env` en la raíz del proyecto:
```
ANTHROPIC_API_KEY=sk-ant-tu_clave_aqui
```

**4. Ejecuta la aplicación**
```bash
streamlit run app.py
```

## 🧰 Stack técnico

- **Python** — lenguaje principal
- **Anthropic API** — modelo Claude con tool use nativo
- **Pandas** — análisis y manipulación de datos
- **Streamlit** — interfaz web

## 👤 Autor

Víctor José Pacheco Martín — Alumno de DAM en prácticas en NTT Data  
[LinkedIn](https://www.linkedin.com/in/v%C3%ADctor-jos%C3%A9-pacheco-mart%C3%ADn-780002320/) | [GitHub](https://github.com/VPWEB)