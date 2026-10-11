import pandas as pd


def combinar_datos(datos: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Une cada favorito con los datos del usuario que lo marcó."""
    # Las dos tablas tienen columna "id". Con los sufijos quedan "id_favorito" e "id_usuario"
    # en vez de los "id_x" e "id_y" que pandas pone por defecto.
    return pd.merge(
        datos["favorite"],
        datos["user"],
        left_on="id_user",
        right_on="id",
        suffixes=("_favorito", "_usuario"),
    )
