import pandas as pd

# Columnas que nunca deben llegar al análisis ni imprimirse (datos personales sensibles).
COLUMNAS_SENSIBLES = ["password"]

# Columnas con fechas ISO ("2026-02-27T10:00:00.000Z"). Se convierten a fecha real antes de
# estandarizar el texto; si no, quedaban en minúsculas ("2026-02-27t10:00:00.000z").
COLUMNAS_FECHA = ["creation_date", "last_update"]


def manejar_valores_nulos(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte textos vacíos en nulos y elimina filas sin ningún dato."""
    df_limpio = df.copy()

    # "", "   " y tabulaciones se consideran valores nulos.
    df_limpio = df_limpio.replace(r"^\s*$", pd.NA, regex=True)

    # Solo elimina registros completamente vacíos.
    df_limpio = df_limpio.dropna(how="all")

    return df_limpio


def quitar_columnas_sensibles(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina columnas como la contraseña: no sirven para el análisis y no deben imprimirse."""
    return df.drop(columns=[columna for columna in COLUMNAS_SENSIBLES if columna in df.columns])


def convertir_fechas(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte las columnas de fecha a datetime. Las fechas inválidas quedan como nulas (NaT)."""
    df_limpio = df.copy()
    for columna in COLUMNAS_FECHA:
        if columna in df_limpio.columns:
            df_limpio[columna] = pd.to_datetime(df_limpio[columna], errors="coerce", utc=True)
    return df_limpio


def estandarizar_texto(df: pd.DataFrame) -> pd.DataFrame:
    """Pasa textos a minúsculas y elimina espacios adicionales."""
    df_limpio = df.copy()

    columnas_texto = df_limpio.select_dtypes(
        include=["object", "string"]
    ).columns

    for columna in columnas_texto:
        df_limpio[columna] = df_limpio[columna].map(
            lambda valor: " ".join(valor.strip().lower().split())
            if isinstance(valor, str)
            else valor
        )

    return df_limpio


def convertir_a_entero(valor: object) -> int | None:
    """
    Convierte un id a número entero.
    Si no es un entero válido (texto, lista, negativo, decimal o vacío),
    devuelve None para que pandas lo trate como valor nulo.
    """
    # En Python True vale 1, pero un booleano no es un id.
    if isinstance(valor, bool):
        return None

    try:
        numero = float(valor)
    except (TypeError, ValueError):
        # Por ejemplo: "abc", [1, 2] o None.
        return None

    # Descarta negativos como -5 y decimales como 3.7 (NaN tampoco es entero).
    if numero < 0 or not numero.is_integer():
        return None

    return int(numero)


def limpieza_especifica_petmind(
    nombre_recurso: str, df: pd.DataFrame
) -> pd.DataFrame:
    """
    Elimina registros inválidos según el recurso obtenido por PetMind.
    Solo usa columnas que realmente existan en el DataFrame.
    """
    df_limpio = df.copy()

    columnas_id = {
        "user": ["id"],
        "favorite": ["id", "id_user", "id_campaign", "id_pet", "id_foundation"],
    }

    # Los ids inválidos quedan como nulos.
    # "Int64" es el tipo entero de pandas que acepta valores nulos.
    for columna in columnas_id.get(nombre_recurso, []):
        if columna in df_limpio.columns:
            df_limpio[columna] = (
                df_limpio[columna].map(convertir_a_entero).astype("Int64")
            )

    campos_obligatorios = {
        "user": ["id", "name", "email"],
        "favorite": ["id", "id_user"],
    }

    columnas_existentes = [
        columna
        for columna in campos_obligatorios.get(nombre_recurso, [])
        if columna in df_limpio.columns
    ]

    if columnas_existentes:
        df_limpio = df_limpio.dropna(subset=columnas_existentes)

    # Un correo debe conservarse en minúsculas.
    if nombre_recurso == "user" and "email" in df_limpio.columns:
        df_limpio["email"] = df_limpio["email"].str.lower().str.strip()

    # La ciudad solo puede tener letras: "medellín!!!###" pasa a "medellín".
    if nombre_recurso == "user" and "city" in df_limpio.columns:
        df_limpio["city"] = (
            df_limpio["city"]
            .str.replace(r"[^a-zA-ZáéíóúüñÁÉÍÓÚÜÑ ]", "", regex=True)
            .str.strip()
            .replace("", pd.NA)
        )

    # Un id no se puede repetir, igual que una cédula. Se conserva el primero.
    if "id" in df_limpio.columns:
        df_limpio = df_limpio.drop_duplicates(subset="id", keep="first")

    return df_limpio


def limpiar_datos(datos: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Limpia todos los DataFrames cargados desde la API."""
    datos_limpios = {}

    for nombre, df in datos.items():
        if not isinstance(df, pd.DataFrame):
            print(f'No se pudo limpiar "{nombre}": no es un DataFrame.')
            continue

        cantidad_inicial = len(df)

        df_limpio = quitar_columnas_sensibles(df)
        df_limpio = manejar_valores_nulos(df_limpio)
        df_limpio = convertir_fechas(df_limpio)
        df_limpio = estandarizar_texto(df_limpio)
        df_limpio = limpieza_especifica_petmind(nombre, df_limpio)
        df_limpio = df_limpio.drop_duplicates()

        cantidad_eliminada = cantidad_inicial - len(df_limpio)

        print(
            f'Datos de "{nombre}" limpiados. '
            f"Registros eliminados: {cantidad_eliminada}."
        )

        datos_limpios[nombre] = df_limpio

    return datos_limpios