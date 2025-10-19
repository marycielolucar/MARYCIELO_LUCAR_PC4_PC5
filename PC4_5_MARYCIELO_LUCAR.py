import io
import csv
import requests
from pymongo import MongoClient

CSV_URL = "https://raw.githubusercontent.com/gdelgador/ProgramacionPython202508/main/Modulo4/src/total_ventas.txt"
MONGO_URI = "mongodb+srv://marycielolucar_db_user:QbQdtNeLGU2QiZv2@marycielolucar.kiumxvc.mongodb.net/?retryWrites=true&w=majority&appName=MarycieloLucar"
NOMBRE_BASE = "base"
TABLA_TIPOS = "sunat_info"
TABLA_SALIDA = "ventas_solarizadas"

def convertir_a_float(x):
    try:
        return float(str(x).strip().replace(",", "."))
    except:
        return 0.00

def obtener_tc_promedio_2023(col_tipos):
    cur = col_tipos.aggregate([
        {"$match": {"fecha": {"$regex": r"^2023-"}}},
        {"$group": {"_id": None, "tc_prom": {"$avg": "$venta"}}}
    ])
    doc = next(cur, None)
    return float(doc["tc_prom"]) if doc and doc.get("tc_prom") is not None else None

def leer_archivo(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    texto = r.content.decode("utf-8", errors="ignore").strip()
    return list(csv.reader(io.StringIO(texto), delimiter=","))

def main():
    cliente = MongoClient(MONGO_URI)
    db = cliente[NOMBRE_BASE]
    col_tipos = db[TABLA_TIPOS]
    col_salida = db[TABLA_SALIDA]
    col_salida.delete_many({})

    tc_prom = obtener_tc_promedio_2023(col_tipos)
    if tc_prom is None:
        print("No hay tipo de cambio promedio 2023 en la BBDD sunat_info.")
        return

    filas = leer_archivo(CSV_URL)
    totales = {}
    for fila in filas:
        if len(fila) < 2:
            continue
        producto = str(fila[0]).strip()
        precio_usd = convertir_a_float(fila[1])
        if not producto:
            continue
        if producto not in totales:
            totales[producto] = 0.0
        totales[producto] += precio_usd

    documentos = []
    for producto, total_usd in totales.items():
        documentos.append({
            "Producto": producto,
            "Total_usd": round(total_usd, 2),
            "Tipo_cambio_prom_2023": round(tc_prom, 4),
            "Total_soles": round(total_usd * tc_prom, 2)
        })

    if documentos:
        col_salida.insert_many(documentos)

    for d in col_salida.find({}, {"_id": 0}).sort("producto", 1):
        print(d)

if __name__ == "__main__":
    main()
