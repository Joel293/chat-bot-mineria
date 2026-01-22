# 🧳 MasterTravel – Asistente Virtual para Solicitudes de Vuelos

## 📌 Descripción del proyecto

**MasterTravel** es un asistente virtual desarrollado en Python capaz de interpretar solicitudes de vuelos expresadas en lenguaje natural en español y transformarlas en información estructurada en formato **JSON**.

El sistema aplica técnicas básicas de **minería de texto** y **procesamiento de lenguaje natural basado en reglas**, sin utilizar modelos de aprendizaje automático, cumpliendo con el alcance definido para fines académicos.

---

## 🎯 Objetivo

Implementar un bot conversacional que permita:

- Recibir frases en lenguaje natural relacionadas con vuelos.
- Extraer información relevante (origen, destino, fecha, cantidad y aerolínea).
- Representar los datos extraídos en una estructura JSON.
- Interactuar con el usuario de forma clara y comprensible.

---

## 🛠️ Tecnologías utilizadas

- **Python 3**
- **Expresiones regulares (`re`)**
- **Formato JSON**
- Enfoque basado en reglas (*Rule-based NLP*)

---

## 📂 Estructura del código

El sistema se organiza en las siguientes funciones principales:

### 🔹 `texto_a_numero(texto)`
Convierte números escritos en español (por ejemplo, *quince*, *diecisiete*) a su equivalente numérico.  
Permite normalizar la cantidad de billetes cuando el usuario no utiliza números explícitos.

---

### 🔹 `extract_flight_info(texto)`
Procesa la frase ingresada por el usuario y extrae las siguientes entidades:

- Ciudad de origen  
- Ciudad de destino  
- Fecha del viaje  
- Cantidad de billetes  
- Aerolínea  

La información se devuelve como un diccionario con estructura JSON.

---

### 🔹 `asistent()`
Función principal del asistente virtual.  
Gestiona la interacción con el usuario, muestra mensajes conversacionales y presenta la salida estructurada.

---

## ▶️ Ejecución del programa

1. Tener **Python 3** instalado.
2. Guardar el código en un archivo, por ejemplo: `asistente_vuelos.py`
3. Ejecuta el programa desde la terminal:

```bash
python asistente_vuelos.py
