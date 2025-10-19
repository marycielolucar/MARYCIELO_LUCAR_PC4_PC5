# Problema 1

import urllib.request
def analizar_registros_temperaturas():
    ruta_entrada = "https://raw.githubusercontent.com/gdelgador/ProgramacionPython202508/main/Modulo4/src/temperaturas.txt"
    archivo_salida = "resumen_temperaturas.txt"

    try:
        with urllib.request.urlopen(ruta_entrada) as archivo_web:
            contenido = archivo_web.read().decode("utf-8").splitlines()

        lista_temperaturas = []

        for registro in contenido:
            try:
                fecha_registro, valor_temp = registro.strip().split(",")
                lista_temperaturas.append(float(valor_temp))
            except ValueError:
                print(f"Línea omitida, formato incorrecto: {registro.strip()}")

        if not lista_temperaturas:
            print("No se encontraron registros válidos en el archivo.")
            return

        promedio_temp = sum(lista_temperaturas) / len(lista_temperaturas)
        temp_maxima = max(lista_temperaturas)
        temp_minima = min(lista_temperaturas)

        with open(archivo_salida, "w", encoding="utf-8") as resumen:
            resumen.write("Resumen: \n")
            resumen.write(f"Temperatura promedio: {promedio_temp:.2f} °C\n")
            resumen.write(f"Temperatura máxima: {temp_maxima:.2f} °C\n")
            resumen.write(f"Temperatura mínima: {temp_minima:.2f} °C\n")

        print(f"Resumen generado correctamente en '{archivo_salida}'")

    except Exception as e:
        print(f"Vuelve a intentar, ocurrió un error: {e}")

if __name__ == "__main__":
    analizar_registros_temperaturas()