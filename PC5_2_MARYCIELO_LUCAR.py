# Problema 2

import os
import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np
from pymongo import MongoClient


URL_WINE = input("Ingresa la ruta local del archivo 'winemag-data-130k-v2.csv': ").strip('"').strip("'")
while not os.path.exists(URL_WINE):
    URL_WINE = input("Ruta no válida. Ingresa nuevamente la ruta completa del archivo: ").strip('"').strip("'")


URL_PAISES = "https://gist.githubusercontent.com/kintero/7d1db891401f56256c79/raw/a61f6d0dda82c3f04d2e6e76c3870552ef6cf0c6/paises.csv"

BASE = Path(__file__).resolve().parent
REPORTES = BASE / "reportes"
REPORTES.mkdir(exist_ok=True)


MONGO_URI = "mongodb+srv://marycielolucar_db_user:QbQdtNeLGU2QiZv2@marycielolucar.kiumxvc.mongodb.net/?retryWrites=true&w=majority&appName=MarycieloLucar"
MONGO_DB = "wine_reports"
MONGO_COLLECTION = "distribucion_precio"


def clasificar_precio(v):
    if pd.isna(v):
        return "sin_dato"
    limites = [0, 10, 20, 35, 50, 75, 100, np.inf]
    etiquetas = ["≤10", "10-20", "20-35", "35-50", "50-75", "75-100", "≥100"]
    i = np.digitize([v], limites, right=True)[0] - 1
    return etiquetas[max(0, min(i, len(etiquetas)-1))]

def categorizar_puntaje(p):
    if pd.isna(p):
        return "sin_dato"
    p = float(p)
    if p >= 95:
        return "excelente (95+)"
    if p >= 90:
        return "muy_bueno (90-94)"
    if p >= 85:
        return "bueno (85-89)"
    if p >= 80:
        return "regular (80-84)"
    return "bajo (<80)"

def explorar_df(df: pd.DataFrame, path_txt: Path):
    with open(path_txt, "w", encoding="utf-8") as f:
        f.write("==== DIMENSIONES ====\n")
        f.write(str(df.shape) + "\n\n")

        f.write("==== COLUMNAS ====\n")
        f.write(", ".join(df.columns) + "\n\n")

        f.write("==== TIPOS ====\n")
        f.write(str(df.dtypes) + "\n\n")

        f.write("==== HEAD ====\n")
        f.write(str(df.head(10)) + "\n\n")

        f.write("==== DESCRIBE (numérico) ====\n")
        f.write(str(df.describe(include=[np.number])) + "\n\n")

        f.write("==== NULOS POR COLUMNA ====\n")
        f.write(str(df.isna().sum().sort_values(ascending=False)) + "\n\n")


def main():
    df = pd.read_csv(URL_WINE, low_memory=False)

    paises = pd.read_csv(
        URL_PAISES,
        sep=",",
        encoding="utf-8",
        skipinitialspace=True,
        engine="python"
    )

    paises.columns = (
        paises.columns.astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )

    if "name" not in paises.columns or "continente" not in paises.columns:
        raise KeyError(f"No encuentro columnas 'name' y/o 'continente' en países. Columnas leídas: {list(paises.columns)}")

    # Renombrar columnas
    renombres = {
        "title": "titulo",
        "country": "pais",
        "province": "provincia",
        "variety": "variedad",
        "winery": "bodega",
        "designation": "denominacion",
        "points": "puntos",
        "price": "precio",
    }
    df = df.rename(columns=renombres)


    df["precio"] = pd.to_numeric(df["precio"], errors="coerce")
    df["puntos"] = pd.to_numeric(df["puntos"], errors="coerce")
    df["pais"] = df["pais"].astype(str).str.strip()
    paises["name"] = paises["name"].astype(str).str.strip()
    paises["continente"] = paises["continente"].astype(str).str.strip()

    df = df.merge(
        paises[["name", "continente"]],
        left_on="pais",
        right_on="name",
        how="left"
    )

    # Agregar 3 columnas
    df["rango_precio"] = df["precio"].map(clasificar_precio)
    df["ratio_puntos_precio"] = np.where(
        (df["precio"].notna()) & (df["precio"] > 0),
        df["puntos"] / df["precio"],
        np.nan
    )
    df["categoria_puntaje"] = df["puntos"].map(categorizar_puntaje)


    explorar_df(df, REPORTES / "exploracion.txt")

    # Reporte 1
    d1 = df.dropna(subset=["continente", "puntos"]).copy()
    d1["orden"] = d1["puntos"] * 1_000_000 - d1["precio"].fillna(0)
    idx = d1.groupby("continente")["orden"].idxmax()
    rep1 = d1.loc[idx, ["continente", "pais", "variedad", "bodega", "puntos", "precio", "titulo"]].sort_values("continente")
    rep1_path = REPORTES / "reporte1_top_continente.csv"
    rep1.to_csv(rep1_path, index=False, encoding="utf-8")

    # Reporte 2
    rep2 = (
        df.groupby("pais", dropna=True)
          .agg(
              promedio_precio=("precio", "mean"),
              cantidad_reviews=("puntos", "size"),
              promedio_puntuacion=("puntos", "mean")
          )
          .reset_index()
          .sort_values(["promedio_puntuacion", "cantidad_reviews"], ascending=[False, False])
    )
    rep2_path = REPORTES / "reporte2_pais.xlsx"
    with pd.ExcelWriter(rep2_path, engine="openpyxl") as w:
        rep2.to_excel(w, index=False, sheet_name="por_pais")

    # Reporte 3: Top 10 variedades por ratio
    rep3 = (
        df.groupby("variedad", dropna=True)
          .agg(
              reviews=("puntos", "size"),
              ratio_prom=("ratio_puntos_precio", "mean"),
              puntos_prom=("puntos", "mean"),
              precio_prom=("precio", "mean")
          )
          .query("reviews >= 50")
          .sort_values(["ratio_prom", "puntos_prom"], ascending=False)
          .head(10)
          .reset_index()
    )
    rep3_path = REPORTES / "reporte3.sqlite"
    con = sqlite3.connect(rep3_path)
    rep3.to_sql("top_variedades_ratio", con, if_exists="replace", index=False)
    con.close()

    # Reporte 4: Distribución por continente y rango
    rep4 = (
        df.groupby(["continente", "rango_precio"], dropna=False)
          .size()
          .reset_index(name="conteo")
          .sort_values(["continente", "rango_precio"])
    )

    inserted = 0
    try:
        cli = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
        _ = cli.admin.command("ping")
        db = cli[MONGO_DB]
        col = db[MONGO_COLLECTION]
        col.delete_many({})
        result = col.insert_many(rep4.fillna("sin_dato").to_dict(orient="records"))
        inserted = len(result.inserted_ids)
        cli.close()
    except Exception as e:
        print(f"No se pudo escribir en MongoDB: {e}")

    print("\n FINALIZADO")

if __name__ == "__main__":
    main()
