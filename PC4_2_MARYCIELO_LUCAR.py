# Problema 2

def generar_tabla_multiplicar():
    try:
        numero_tabla = int(input("Ingrese un número entre 1 y 10 para generar su tabla: "))
        if not 1 <= numero_tabla <= 10:
            print("El número debe estar entre 1 y 10.")
            return
        
        nombre_archivo = f"tabla-{numero_tabla}.txt"
        
        with open(nombre_archivo, "w", encoding="utf-8") as archivo_tabla:
            for multiplicador in range(1, 11):
                resultado = numero_tabla * multiplicador
                archivo_tabla.write(f"{numero_tabla} x {multiplicador} = {resultado}\n")

        print(f"Se generó correctamente el archivo '{nombre_archivo}'.")
    except ValueError:
        print("Error: Usted debe ingresar un número entero.")


def mostrar_tabla_completa():
    try:
        numero_tabla = int(input("Ingrese el número de la tabla que desea ver (1 al 10): "))
        nombre_archivo = f"tabla-{numero_tabla}.txt"

        with open(nombre_archivo, "r", encoding="utf-8") as archivo_tabla:
            print(f"\n Contenido de {nombre_archivo}:")
            print(archivo_tabla.read())

    except FileNotFoundError:
        print(f"El archivo 'tabla-{numero_tabla}.txt' no existe. Primero debe generarlo.")
    except ValueError:
        print("Debe ingresar un número válido.")


def mostrar_linea_especifica():
    try:
        numero_tabla = int(input("Ingrese el número de la tabla (1 al 10): "))
        numero_linea = int(input("Ingrese el número de línea que desea mostrar (1 al 10): "))
        nombre_archivo = f"tabla-{numero_tabla}.txt"

        with open(nombre_archivo, "r", encoding="utf-8") as archivo_tabla:
            lineas_tabla = archivo_tabla.readlines()

            if 1 <= numero_linea <= len(lineas_tabla):
                print(f"\n Línea {numero_linea}: {lineas_tabla[numero_linea - 1].strip()}")
            else:
                print("La línea indicada no existe en el archivo.")

    except FileNotFoundError:
        print(f"El archivo 'tabla-{numero_tabla}.txt' no existe.")
    except ValueError:
        print("Debe ingresar números enteros válidos.")


def menu_principal():
    while True:
        print("\n MENÚ DE TABLAS DE MULTIPLICAR")
        print("1. Generar tabla y guardar en archivo")
        print("2. Mostrar tabla completa desde archivo")
        print("3. Mostrar línea específica de una tabla")
        print("4. Salir")

        opcion_elegida = input("Seleccione una opción (1 al 4): ").strip()

        if opcion_elegida == "1":
            generar_tabla_multiplicar()
        elif opcion_elegida == "2":
            mostrar_tabla_completa()
        elif opcion_elegida == "3":
            mostrar_linea_especifica()
        elif opcion_elegida == "4":
            print("Programa finalizado. Gracias :)")
            break
        else:
            print("Opción no válida. Intente nuevamente.")


if __name__ == "__main__":
    menu_principal()



