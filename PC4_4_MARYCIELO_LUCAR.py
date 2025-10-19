# Problema 4

import datetime as dt
import requests
from pymongo import MongoClient, ASCENDING

API_URL = "https://api.apis.net.pe/v1/tipo-cambio-sunat"
MONGO_URI = "mongodb+srv://marycielolucar_db_user:QbQdtNeLGU2QiZv2@marycielolucar.kiumxvc.mongodb.net/?retryWrites=true&w=majority&appName=MarycieloLucar"
DB_NAME = "base"
COLL = "sunat_info"

def obtener_tipo_cambio(fecha_str, max_retrocesos=3):
    fecha = dt.datetime.strptime(fecha_str, "%Y-%m-%d").date()
    for _ in range(max_retrocesos + 1):
        r = requests.get(API_URL, params={"date": fecha.isoformat()}, timeout=15)
        if r.status_code == 200:
            j = r.json()
            compra = j.get("compra")
            venta = j.get("venta")
            if compra is not None and venta is not None:
                return {"fecha": fecha.isoformat(), "compra": float(compra), "venta": float(venta)}
            return None
        elif r.status_code == 404:
            fecha -= dt.timedelta(days=1)
            continue
        else:
            print(f"[{fecha}] HTTP {r.status_code}: {r.text[:120]}")
            return None
    return None

def main():
    cli = MongoClient(MONGO_URI)
    col = cli[DB_NAME][COLL]
    col.create_index([("fecha", ASCENDING)], unique=True)
    inicio = dt.date(2023, 1, 1)
    fin = dt.date(2023, 12, 31)
    d = inicio
    total = 0
    while d <= fin:
        f = d.isoformat()
        doc = obtener_tipo_cambio(f)
        if doc:
            col.update_one({"fecha": doc["fecha"]}, {"$set": doc}, upsert=True)
            total += 1
            print(f"[{f}] OK -> {doc['compra']}/{doc['venta']}")
        else:
            print(f"[{f}] Sin datos válidos.")
        d += dt.timedelta(days=1)
    print(f"\n Listo. Insertados/actualizados (2023): {total}")

if __name__ == "__main__":
    main()
