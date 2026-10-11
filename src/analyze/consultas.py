import pandas as pd


def usuario_con_mas_favoritos(datos_combinados: pd.DataFrame) -> tuple[int, str, int] | None:
    """Devuelve (id, nombre, cantidad) del usuario con más favoritos, o None si no hay datos."""
    if datos_combinados.empty:
        return None
    conteo = datos_combinados["id_user"].value_counts()
    id_usuario = conteo.idxmax()
    nombre = datos_combinados.loc[datos_combinados["id_user"] == id_usuario, "name"].iloc[0]
    return int(id_usuario), nombre, int(conteo.max())


def favoritos_por_ciudad(datos_combinados: pd.DataFrame) -> pd.Series:
    """Cantidad de favoritos agrupados por la ciudad del usuario."""
    return datos_combinados.groupby("city").size()


def usuarios_de_ciudad(usuarios: pd.DataFrame, ciudad: str) -> int:
    """Cuántos usuarios viven en la ciudad indicada (la limpieza deja las ciudades en minúsculas)."""
    return int((usuarios["city"] == ciudad.strip().lower()).sum())


def imprimir_consultas(datos_combinados: pd.DataFrame, usuarios: pd.DataFrame) -> None:
    """Responde en consola las tres preguntas del caso 6 del menú."""
    print("\n1. ¿Qué usuario tiene más favoritos?")
    resultado = usuario_con_mas_favoritos(datos_combinados)
    if resultado is None:
        print("No hay favoritos para analizar.")
    else:
        id_usuario, nombre, cantidad = resultado
        print(f"{nombre} (id {id_usuario}) con {cantidad} favoritos.")

    print("\n2. ¿Cuántos favoritos hay por ciudad?")
    print(favoritos_por_ciudad(datos_combinados).to_string())

    print("\n3. ¿Cuántos usuarios son de Medellín?")
    print(f"{usuarios_de_ciudad(usuarios, 'Medellín')} usuarios.")
