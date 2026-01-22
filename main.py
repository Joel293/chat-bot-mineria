import re
import json

def texto_a_numero(texto):
    """
    Convierte números escritos en español (hasta 99) a número entero.
    """
    unidades = {
        "cero": 0, "uno": 1, "un": 1, "dos": 2, "tres": 3,
        "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7,
        "ocho": 8, "nueve": 9
    }

    especiales = {
        "diez": 10, "once": 11, "doce": 12, "trece": 13,
        "catorce": 14, "quince": 15
    }

    decenas = {
        "dieci": 10,
        "veinti": 20,
        "treinta": 30,
        "cuarenta": 40,
        "cincuenta": 50,
        "sesenta": 60,
        "setenta": 70,
        "ochenta": 80,
        "noventa": 90
    }

    texto = texto.lower()

    if texto in especiales:
        return especiales[texto]

    if texto in unidades:
        return unidades[texto]

    # dieciseis, diecisiete...


def extract_flight_info(texto):
    """
    Extrae información relevante de una frase en lenguaje natural
    y la transforma en una estructura JSON.
    """

    resultado = {
        "origen": None,
        "destino": None,
        "fecha": None,
        "cantidad": None,
        "aerolinea": None
    }

    texto_lower = texto.lower()

    # -----------------------------
    # Cantidad de billetes
    # -----------------------------
    match_texto = re.search(
        r"([a-záéíóú]+)\s+(billete|billetes|pasaje|pasajes)",
        texto_lower
    )

    if match_texto:
        cantidad_texto = match_texto.group(1)
        numero = texto_a_numero(cantidad_texto)
        if numero is not None:
            resultado["cantidad"] = str(numero)

    # Cantidades numéricas asociadas a billetes
    match_num = re.search(
        r"(\d+)\s+(billete|billetes|pasaje|pasajes)",
        texto_lower
    )
    if match_num:
        resultado["cantidad"] = match_num.group(1)



    # -----------------------------
    # Fecha
    # -----------------------------
    fecha_match = re.search(
        r"\d{1,2}\s+de\s+[a-záéíóú]+", texto_lower
    )
    if fecha_match:
        resultado["fecha"] = fecha_match.group()

    # -----------------------------
    # Aerolínea (palabras con mayúscula)
    # -----------------------------
    aerolinea_match = re.search(
        r"\b(Iberia|Avianca|LATAM|KLM|Air France)\b",
        texto,
        re.IGNORECASE
    )
    if aerolinea_match:
        resultado["aerolinea"] = aerolinea_match.group()

    # -----------------------------
    # Origen y destino
    # -----------------------------
    ruta_match = re.search(
        r"de\s+([A-ZÁÉÍÓÚa-záéíóú]+)\s+a\s+([A-ZÁÉÍÓÚa-záéíóú]+)",
        texto
    )
    if ruta_match:
        resultado["origen"] = ruta_match.group(1)
        resultado["destino"] = ruta_match.group(2)

    return resultado


def asistent():
    """
    Asistente virtual principal
    """

    print("Hola, bienvenido a MasterTravel. ¿Cómo te puedo ayudar?")

    while True:
        entrada = input("> ")

        if entrada.lower() == "salir":
            print("Gracias por usar el asistente. ¡Hasta pronto!")
            break

        datos = extract_flight_info(entrada)

        # Mensaje conversacional
        print(
            f"Perfecto, comienzo la búsqueda de tu viaje a "
            f"{datos['destino']} desde {datos['origen']} "
            f"para el {datos['fecha']} con {datos['aerolinea']}."
        )

        # Salida estructurada
        print("\nJSON generado:")
        print(json.dumps(datos, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    asistent()