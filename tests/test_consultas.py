import unittest

import pandas as pd

from src.analyze.consultas import favoritos_por_ciudad, usuario_con_mas_favoritos, usuarios_de_ciudad


class ConsultasTest(unittest.TestCase):
    def setUp(self):
        self.combinados = pd.DataFrame(
            [
                {"id_user": 1, "name": "carlos", "city": "medellín"},
                {"id_user": 1, "name": "carlos", "city": "medellín"},
                {"id_user": 2, "name": "maría", "city": "cali"},
            ]
        )
        self.usuarios = pd.DataFrame([{"id": 1, "city": "medellín"}, {"id": 2, "city": "cali"}])

    def test_usuario_con_mas_favoritos(self):
        self.assertEqual(usuario_con_mas_favoritos(self.combinados), (1, "carlos", 2))

    def test_sin_favoritos_no_falla(self):
        # Antes idxmax() sobre una tabla vacía lanzaba ValueError y cerraba el programa
        self.assertIsNone(usuario_con_mas_favoritos(self.combinados.iloc[0:0]))

    def test_favoritos_por_ciudad(self):
        self.assertEqual(favoritos_por_ciudad(self.combinados).to_dict(), {"cali": 1, "medellín": 2})

    def test_usuarios_de_ciudad_sin_importar_mayusculas(self):
        self.assertEqual(usuarios_de_ciudad(self.usuarios, "Medellín"), 1)


if __name__ == "__main__":
    unittest.main()
