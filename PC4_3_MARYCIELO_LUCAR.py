# Problema 3

def contar_loc_en_python(ruta_objetivo: str) -> int:
    
    with open(ruta_objetivo, "r", encoding="utf-8") as manejador_archivo:
        listado_lineas = manejador_archivo.readlines()

    total_lineas_codigo = 0

    for linea_original in listado_lineas:
        linea_purificada = linea_original.strip()

        if linea_purificada == "":
            continue

        if linea_purificada.startswith("#"):
            continue

        total_lineas_codigo += 1

    return total_lineas_codigo


def ejecutar_contador_loc():
    ruta_ingresada = input("Ingrese la ruta completa del archivo .py: ").strip()
    if not ruta_ingresada.lower().endswith(".py"):
        return  

    try:
        conteo_resultante = contar_loc_en_python(ruta_ingresada)

        print(f"Líneas de código (sin comentarios ni vacías): {conteo_resultante}")

    except FileNotFoundError:
        return
    except Exception:
        return

if __name__ == "__main__":
    ejecutar_contador_loc()
