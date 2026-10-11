import pandas as pd
import requests

from src.analyze.consultas import imprimir_consultas
from src.extract.fetch_api import fetch as ejecutar_extraccion
from src.transform.cargar_datos import cargar_datos
from src.transform.combinar_datos import combinar_datos
from src.transform.limpiar_datos import limpiar_datos

MENU = """
    Haz ingresado al menú, estas son las opciones disponibles:
    1. Traer datos desde la API
    2. Cargar datos
    3. Limpiar datos
    4. Imprimir datos limpios
    5. Mergear datos
    6. Consultas de datos
    0. Salir"""


def leer_opcion() -> int | None:
    """Pide una opción del 0 al 6. Devuelve None si se cerró la entrada (Ctrl+D) o se pulsó Ctrl+C."""
    while True:
        try:
            opcion = int(input("Seleccione su opción: \n"))
        except ValueError:
            # Solo se atrapa el texto que no es número. Antes un "except:" vacío atrapaba también
            # Ctrl+C y el fin de la entrada, y el programa quedaba en un ciclo infinito.
            print("Opción no disponible")
            continue
        except (EOFError, KeyboardInterrupt):
            return None
        if 0 <= opcion <= 6:
            return opcion
        print("Seleccione una opción válida")


def imprimir_datos_limpios(datos_limpios: dict[str, pd.DataFrame]) -> None:
    for nombre, df in datos_limpios.items():
        print(f"\n{'=' * 55}")
        print(f"DATAFRAME LIMPIO: {nombre.upper()}")
        print(f"{'=' * 55}")
        print(df.to_string(index=False))

        print("\nValores nulos por columna:")
        print(df.isnull().sum())

        print(f"\nCantidad de registros limpios: {len(df)}")


def main() -> None:
    datos = {}
    datos_limpios = {}
    datos_combinados = None
    print("Bienvenido al sistema de análisis de datos (en proceso) de PetMind")

    while True:
        print(MENU)
        opcion = leer_opcion()
        if opcion is None or opcion == 0:
            print("\nHasta pronto.")
            break

        # Cada opción maneja sus errores esperados para que un fallo no cierre el programa.
        match opcion:
            case 1:
                try:
                    ejecutar_extraccion()
                except requests.RequestException as error:
                    print(f"No se pudieron descargar los datos. Revisa tu conexión o la API.\nDetalle: {error}")
            case 2:
                try:
                    datos = cargar_datos()
                except FileNotFoundError:
                    print("No están los archivos de Data/raw. Primero trae los datos con la opción 1.")
                except ValueError as error:
                    print(f"Los archivos de Data/raw no tienen un JSON válido. Vuelve a usar la opción 1.\nDetalle: {error}")
            case 3:
                if not datos:
                    print("Primero debes cargar los datos usando la opción 2.")
                else:
                    datos_limpios = limpiar_datos(datos)
                    print("Proceso de limpieza finalizado.")
            case 4:
                if not datos_limpios:
                    print("Primero debes limpiar los datos usando la opción 3.")
                else:
                    imprimir_datos_limpios(datos_limpios)
            case 5:
                if not datos_limpios:
                    print("Primero debes limpiar los datos usando la opción 3.")
                else:
                    datos_combinados = combinar_datos(datos_limpios)
                    print(datos_combinados.to_string(index=False))
            case 6:
                if datos_combinados is None:
                    print("Primero debes combinar los datos usando la opción 5.")
                else:
                    imprimir_consultas(datos_combinados, datos_limpios["user"])


# Así el menú solo arranca al ejecutar "python analisis.py", no al importar el archivo (p. ej. en pruebas).
if __name__ == "__main__":
    main()
