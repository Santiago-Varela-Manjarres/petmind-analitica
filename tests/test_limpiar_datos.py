import unittest

import pandas as pd

from src.transform.limpiar_datos import convertir_a_entero, limpiar_datos


# Pruebas de la limpieza con datos sucios parecidos a los de la API.
# Se ejecutan con: python -m unittest
class LimpiarDatosTest(unittest.TestCase):
    def setUp(self):
        self.usuarios = pd.DataFrame(
            [
                {"id": 1, "name": "  Carlos ", "email": "CARLOS@Mail.com", "password": "Secreta#1",
                 "city": "Medellín!!!###", "creation_date": "2026-02-27T10:00:00.000Z"},
                {"id": "2", "name": "María", "email": "maria@mail.com", "password": "Otra#2",
                 "city": "Cali", "creation_date": "no es fecha"},
                {"id": 1, "name": "Repetido", "email": "rep@mail.com", "password": "x",
                 "city": "Cali", "creation_date": "2026-01-01T00:00:00.000Z"},
                {"id": -5, "name": "Id negativo", "email": "neg@mail.com", "password": "x",
                 "city": "Cali", "creation_date": "2026-01-01T00:00:00.000Z"},
                {"id": 3, "name": "   ", "email": "sin.nombre@mail.com", "password": "x",
                 "city": "Cali", "creation_date": "2026-01-01T00:00:00.000Z"},
            ]
        )
        self.favoritos = pd.DataFrame(
            [
                {"id": 100, "id_user": 1, "id_pet": 5},
                {"id": 101, "id_user": [1, 2], "id_pet": 6},
                {"id": 102, "id_user": True, "id_pet": 7},
                {"id": 103, "id_user": "3.7", "id_pet": 8},
            ]
        )
        self.limpios = limpiar_datos({"user": self.usuarios, "favorite": self.favoritos})

    def test_quita_la_contrasena(self):
        self.assertNotIn("password", self.limpios["user"].columns)

    def test_convierte_las_fechas_sin_pasarlas_a_minusculas(self):
        fechas = self.limpios["user"]["creation_date"]
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(fechas))
        carlos = self.limpios["user"].loc[self.limpios["user"]["id"] == 1].iloc[0]
        self.assertEqual(carlos["creation_date"], pd.Timestamp("2026-02-27T10:00:00Z"))
        maria = self.limpios["user"].loc[self.limpios["user"]["id"] == 2].iloc[0]
        self.assertTrue(pd.isna(maria["creation_date"]))

    def test_estandariza_texto_y_ciudades(self):
        carlos = self.limpios["user"].loc[self.limpios["user"]["id"] == 1].iloc[0]
        self.assertEqual(carlos["name"], "carlos")
        self.assertEqual(carlos["email"], "carlos@mail.com")
        self.assertEqual(carlos["city"], "medellín")

    def test_elimina_ids_invalidos_repetidos_y_campos_obligatorios_vacios(self):
        self.assertEqual(sorted(self.limpios["user"]["id"].tolist()), [1, 2])

    def test_favoritos_con_id_de_usuario_invalido_se_descartan(self):
        self.assertEqual(self.limpios["favorite"]["id"].tolist(), [100])


class ConvertirAEnteroTest(unittest.TestCase):
    def test_casos(self):
        self.assertEqual(convertir_a_entero("7"), 7)
        self.assertEqual(convertir_a_entero(7.0), 7)
        for invalido in ["abc", -1, 3.7, True, None, [1, 2]]:
            self.assertIsNone(convertir_a_entero(invalido), invalido)


if __name__ == "__main__":
    unittest.main()
