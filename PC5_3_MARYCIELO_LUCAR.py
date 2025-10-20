import io
import sys
import zipfile
from pathlib import Path

import requests
import pandas as pd
from pymongo import MongoClient

ZIP_URL = "https://netsg.cs.sfu.ca/youtubedata/0303.zip"

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MONGO_URI = "mongodb+srv://marycielolucar_db_user:QbQdtNeLGU2QiZv2@marycielolucar.kiumxvc.mongodb.net/?retryWrites=true&w=majority&appName=MarycieloLucar"
MONGO_DB = "youtube_db"
MONGO_COLL = "videos_filtered"


OFFICIAL_COLUMNS = [
    "video ID", "uploader", "age", "category", "length",
    "views", "rate", "ratings", "comments"
]
FINAL_COLUMNS = ["VideoID", "age", "category", "views", "rate"]


def download_zip(url: str) -> bytes:
    print(f"Descargando archivo desde: {url}")
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    print("Descarga completa.")
    return r.content


def read_zip_to_df(zip_bytes: bytes) -> pd.DataFrame:
    dfs = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for name in z.namelist():

            if "log" in name.lower():
                print(f"Omitiendo archivo no válido (log): {name}")
                continue

            if name.lower().endswith((".txt", ".tsv")):
                print(f"Leyendo archivo: {name}")
                with z.open(name) as f:
                    df = pd.read_csv(
                        f,
                        sep="\t",
                        header=None,
                        names=OFFICIAL_COLUMNS,
                        usecols=range(9),      
                        engine="python",
                        on_bad_lines="skip",
                        dtype=str
                    )
                    dfs.append(df)

    if not dfs:
        raise RuntimeError("No se encontraron archivos .txt/.tsv válidos dentro del ZIP.")
    return pd.concat(dfs, ignore_index=True)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df[["video ID", "age", "category", "views", "rate"]].copy()
    df.columns = FINAL_COLUMNS

    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["views"] = pd.to_numeric(df["views"], errors="coerce")
    df["rate"] = pd.to_numeric(df["rate"], errors="coerce")

    df["category"] = df["category"].astype(str).str.strip()

    df = df.dropna(subset=["VideoID", "category"]).reset_index(drop=True)
    print(f"Filas finales limpias: {len(df)}")
    return df


def export_local(df: pd.DataFrame) -> None:
    output_path = OUTPUT_DIR / "youtube_clean.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Archivo CSV guardado en: {output_path}")


def export_mongo(df: pd.DataFrame) -> None:
    if df.empty:
        print("No hay datos para insertar en MongoDB.")
        return

    print("Conectando a MongoDB Atlas...")
    client = MongoClient(MONGO_URI)
    coll = client[MONGO_DB][MONGO_COLL]

    try:
        coll.create_index("VideoID")
    except Exception:
        pass

    data = df.where(pd.notnull(df), None).to_dict(orient="records")

    coll.delete_many({})
    coll.insert_many(data, ordered=False)
    print(f"Datos cargados en {MONGO_DB}.{MONGO_COLL} ({len(data)} documentos).")
    client.close()


def main():
    print("Iniciando análisis de datos de YouTube")
    zip_bytes = download_zip(ZIP_URL)
    df_raw = read_zip_to_df(zip_bytes)
    df_clean = clean_data(df_raw)
    export_local(df_clean)
    export_mongo(df_clean)
    print("Finalizado, se generaron los reportes y se cargaron los datos en MongoDB :)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
