import re
import json
import requests
from datetime import datetime
from pathlib import Path

# ============================================================
# Credenciales Air-Port-Codes (TU CUENTA)
# ============================================================
APC_KEY = "d639931778"
APC_SECRET = "bd043be0e0e86f8"
APC_REFERER = "http://localhost"  # evita error de referrer

RESULTADOS_PATH = Path("resultados.json")

# ============================================================
# 0) Normalización ES -> EN (para que la API responda mejor)
# ============================================================
def normalizar_ciudad_para_api(ciudad: str):
    if not ciudad:
        return None

    c = ciudad.strip()
    key = c.lower()
    key = key.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

    trad = {
        "roma": "Rome",
        "londres": "London",
        "nueva york": "New York",
        "paris": "Paris",
        "parís": "Paris",
        "sevilla": "Seville",
        "munich": "Munich",
        "múnich": "Munich",
        "francfort": "Frankfurt",
        "fráncfort": "Frankfurt",
        "franfurt": "Frankfurt",  # 👈 AÑADE ESTA
        "bogota": "Bogota",
        "bogotá": "Bogota",
    }
    return trad.get(key, c)

# ============================================================
# 1) Números en texto (0–99)
# ============================================================
def texto_a_numero(texto: str):
    if not texto:
        return None
    t = texto.strip().lower()
    t = t.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

    unidades = {
        "cero": 0, "uno": 1, "un": 1, "una": 1, "dos": 2, "tres": 3,
        "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9
    }
    especiales = {"diez": 10, "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15}
    decenas = {
        "veinte": 20, "treinta": 30, "cuarenta": 40, "cincuenta": 50,
        "sesenta": 60, "setenta": 70, "ochenta": 80, "noventa": 90
    }

    if t in unidades:
        return unidades[t]
    if t in especiales:
        return especiales[t]
    if t in decenas:
        return decenas[t]

    if t.startswith("dieci"):
        resto = t[5:]
        if resto in unidades:
            return 10 + unidades[resto]

    if t.startswith("veinti"):
        resto = t[6:]
        if resto in unidades:
            return 20 + unidades[resto]

    m = re.match(r"^(veinte|treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa)\s+y\s+([a-z]+)$", t)
    if m:
        d, u = m.group(1), m.group(2)
        if d in decenas and u in unidades:
            return decenas[d] + unidades[u]

    return None

# ============================================================
# 2) Fecha → dd-mm-yyyy
# ============================================================
MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12
}

def normalizar_fecha(texto: str):
    if not texto:
        return None
    t = texto.lower()

    m = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", t)
    if m:
        dd, mm, yyyy = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{dd:02d}-{mm:02d}-{yyyy:04d}"

    m = re.search(r"\b(\d{1,2})\s+de\s+([a-záéíóú]+)(?:\s+de\s+(\d{4}))?\b", t)
    if m:
        dd = int(m.group(1))
        mes = m.group(2).strip().lower()
        mes = mes.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        yyyy = int(m.group(3)) if m.group(3) else datetime.now().year
        if mes in MESES:
            return f"{dd:02d}-{MESES[mes]:02d}-{yyyy:04d}"

    m = re.search(r"\ben\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)\b", t)
    if m:
        mes = m.group(1)
        yyyy = datetime.now().year
        return f"01-{MESES[mes]:02d}-{yyyy:04d}"

    return None

# ============================================================
# 3) Limpieza de ciudad
# ============================================================
CORTES = [" el ", " la ", " los ", " las ", " en ", " para ", " con ", " por ", " del ", " de "]

def limpiar_ciudad(ciudad: str):
    if not ciudad:
        return None
    c = ciudad.strip()

    lower = c.lower()
    cut = None
    for token in CORTES:
        p = lower.find(token)
        if p != -1:
            cut = p if cut is None else min(cut, p)
    if cut is not None:
        c = c[:cut].strip()

    c = re.sub(r"[^\w\sÁÉÍÓÚáéíóúÑñ-]", "", c).strip()
    c = re.sub(r"\s{2,}", " ", c).strip()

    # Quita restos tipo "Madrid el", "Quito de", etc.
    c = re.sub(r"\s+(el|la|los|las|de|del|en|para|con|por)\b.*$", "", c, flags=re.IGNORECASE).strip()

    return c if c else None

# ============================================================
# 4) API: ciudad → IATA (con SECRET + REFERER)
# ============================================================
def obtener_iata_ciudad(ciudad: str):
    if not ciudad:
        return None

    url = "https://www.air-port-codes.com/api/v1/multi"
    headers = {
        "APC-Auth": APC_KEY,
        "APC-Auth-Secret": APC_SECRET,
        "Referer": APC_REFERER,
        "Accept": "application/json",
    }
    params = {"term": ciudad, "limit": 5, "size": 0, "type": "a|g"}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        airports = data.get("airports", []) or []
        for a in airports:
            iata = (a.get("iata") or "").strip().upper()
            if len(iata) == 3:
                return iata
        return None
    except Exception as e:
        print(f"[DEBUG] Error API para '{ciudad}': {e}")
        return None

# ============================================================
# 5) Guardar resultados
# ============================================================
def cargar_resultados():
    if not RESULTADOS_PATH.exists():
        return []
    try:
        with open(RESULTADOS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def guardar_resultado_lista(datos):
    resultados = cargar_resultados()
    resultados.append(datos)
    with open(RESULTADOS_PATH, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)

AEROLINEAS = {
    "iberia": "Iberia",
    "latam": "LATAM",
    "avianca": "Avianca",
    "air europa": "Air Europa",
    "aireuropa": "Air Europa",
    "american airlines": "American Airlines",
    "delta": "Delta",
    "united": "United",
    "ryanair": "Ryanair",
    "vueling": "Vueling",
    "klm": "KLM",
    "lufthansa": "Lufthansa",
    "air france": "Air France",
}

def extraer_aerolinea(texto: str):
    if not texto:
        return None
    tl = texto.lower()

    # 1) si viene "con X"
    m = re.search(r"\bcon\s+([a-záéíóúñ\s]+)", tl)
    if m:
        candidato = m.group(1).strip()
        # corta si después viene una preposición típica
        candidato = re.split(r"\b(de|desde|a|para|el|en|por)\b", candidato)[0].strip()

        # normaliza espacios
        candidato = re.sub(r"\s{2,}", " ", candidato)

        # match por diccionario
        if candidato in AEROLINEAS:
            return AEROLINEAS[candidato]

    # 2) buscar por aparición directa en el texto
    for k, v in AEROLINEAS.items():
        if k in tl:
            return v

    return None

def parece_ciudad(texto: str) -> bool:
    if not texto:
        return False
    # max 4 palabras y solo letras/espacios/guion
    if len(texto.split()) > 4:
        return False
    return re.fullmatch(r"[A-ZÁÉÍÓÚa-záéíóúÑñ-]+(?:\s+[A-ZÁÉÍÓÚa-záéíóúÑñ-]+)*", texto.strip()) is not None

def extract_flight_info(texto: str):
    resultado = {
        "Origen": None,
        "CiudadDestino": None,
        "IATAFrom": None,
        "IATATo": None,
        "Fecha": None,
        "Pax": None,
        "Aerolinea": None
    }

    if not texto:
        return resultado

    # =========================
    # TEXTO BASE
    # =========================
    t = texto.strip()
    tl = t.lower()

    # =========================
    # PASAJEROS (Pax)
    # =========================
    resultado["Pax"] = None

    m_num = re.search(
        r"\b(\d+)\s+(billete|billetes|pasaje|pasajes|pasajero|pasajeros)\b",
        tl
    )
    if m_num:
        resultado["Pax"] = int(m_num.group(1))
    else:
        m_txt = re.search(
            r"\b([a-záéíóú]+)\s+(billete|billetes|pasaje|pasajes|pasajero|pasajeros)\b",
            tl
        )
        if m_txt:
            n = texto_a_numero(m_txt.group(1))
            if n is not None:
                resultado["Pax"] = n

    if resultado["Pax"] is None:
        resultado["Pax"] = 1

    # =========================
    # FECHA
    # =========================
    resultado["Fecha"] = normalizar_fecha(t)

    # =========================
    # Aerolinea
    # =========================
    resultado["Aerolinea"] = extraer_aerolinea(t)

    # =========================
    # TEXTO SIN FECHA (para ciudades)
    # =========================
    t_sin_fecha = re.sub(
        r"\b(?:el\s+)?\d{1,2}\s+de\s+[a-záéíóú]+(?:\s+de\s+\d{4})?\b",
        "",
        t,
        flags=re.IGNORECASE
    )

    # =========================
    # ORIGEN / DESTINO
    # =========================
    m_ciudad = re.search(
        r"\bde\s+([A-ZÁÉÍÓÚa-záéíóúÑñ\s-]+?)\s+a\s+([A-ZÁÉÍÓÚa-záéíóúÑñ\s-]+)\b",
        t_sin_fecha
    )

    if m_ciudad:
        resultado["Origen"] = limpiar_ciudad(m_ciudad.group(1))
        resultado["CiudadDestino"] = limpiar_ciudad(m_ciudad.group(2))

    else:
        m_ciudad = re.search(
            r"\bdesde\s+([A-ZÁÉÍÓÚa-záéíóúÑñ\s-]+?)\s+hacia\s+([A-ZÁÉÍÓÚa-záéíóúÑñ\s-]+)\b",
            t_sin_fecha,
            re.IGNORECASE
        )

        if m_ciudad:
            resultado["Origen"] = limpiar_ciudad(m_ciudad.group(1))
            resultado["CiudadDestino"] = limpiar_ciudad(m_ciudad.group(2))

        else:
            # 👉 CASO NUEVO: "Barcelona a Roma"

            t_sin_fecha_limpio = re.sub(
                r"\b(quiero|necesito|comprar|busco|deseo)\b.*?\b(billete|billetes|pasaje|pasajes)\b",
                "",
                t_sin_fecha,
                flags=re.IGNORECASE
            ).strip()

            m_ciudad = re.search(
                r"\b([A-ZÁÉÍÓÚa-záéíóúÑñ-]+(?:\s+[A-ZÁÉÍÓÚa-záéíóúÑñ-]+){0,3})\s+a\s+([A-ZÁÉÍÓÚa-záéíóúÑñ-]+(?:\s+[A-ZÁÉÍÓÚa-záéíóúÑñ-]+){0,3})\b",
                t_sin_fecha_limpio
            )

            if m_ciudad:
                c1 = limpiar_ciudad(m_ciudad.group(1))
                c2 = limpiar_ciudad(m_ciudad.group(2))

                basura = {"billete", "billetes", "pasaje", "pasajes", "comprar", "necesito", "quiero"}
                if c1 and c1.lower() not in basura:
                    resultado["Origen"] = c1
                    resultado["CiudadDestino"] = c2

            else:
                # Último recurso: solo destino
                m_ciudad = re.search(
                    r"\b(a|para)\s+([A-ZÁÉÍÓÚa-záéíóúÑñ\s-]+)\b",
                    t_sin_fecha
                )
                if m_ciudad:
                    resultado["CiudadDestino"] = limpiar_ciudad(m_ciudad.group(2))

    # =========================
    # IATA
    # =========================
    if resultado["Origen"] and parece_ciudad(resultado["Origen"]):
        resultado["IATAFrom"] = obtener_iata_ciudad(
            normalizar_ciudad_para_api(resultado["Origen"])
        )

    if resultado["CiudadDestino"] and parece_ciudad(resultado["CiudadDestino"]):
        resultado["IATATo"] = obtener_iata_ciudad(
            normalizar_ciudad_para_api(resultado["CiudadDestino"])
        )

    return resultado


# ============================================================
# 7) Asistente (consola)
# ============================================================
def asistent():
    print("Escribe 'Salir' para salir del programa")
    print("\nHola, bienvenido a MasterTravel.")

    while True:
        print("\n¿Cómo te puedo ayudar?")
        entrada = input("> ").strip()

        if entrada.lower() == "salir":
            print("Gracias por usar el asistente. ¡Hasta pronto!")
            break

        datos = extract_flight_info(entrada)

        # Mostrar bonito en consola
        print(json.dumps(datos, indent=4, ensure_ascii=False))

        # Guardar bonito en resultados.json (lista)
        guardar_resultado_lista(datos)



if __name__ == "__main__":
    asistent()


