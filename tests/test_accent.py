# pylint: disable=duplicate-code,protected-access
# coding=utf-8

import unittest

from connect.utils import strip_accents
from connect.library_index import build_title_index

class TestAccent(unittest.TestCase):
    def test_strip_accent(self):
        self.assertEqual("Padre no hay mas que uno", strip_accents("Padre no hay más que uno"))
        self.assertEqual("Elite", strip_accents("Élite"))
        self.assertEqual("Pequenas mentirosas", strip_accents("Pequeñas mentirosas"))
        self.assertEqual("Capitan America: El primer vengador", strip_accents("Capitán América: El primer vengador"))
        self.assertEqual("Aladdin", strip_accents("Aladdín"))
        self.assertEqual("Alita: Angel del combate", strip_accents("Alita: Ángel del combate"))
        self.assertEqual("Animales fantasticos y donde encontrarlos", strip_accents("Animales fantásticos y dónde encontrarlos"))
        self.assertEqual("Animales fantasticos: Los crimenes de Grindelwald", strip_accents("Animales fantásticos: Los crímenes de Grindelwald"))
        self.assertEqual("Cafarnaum", strip_accents("Cafarnaúm"))
        self.assertEqual("El Camino: Una pelicula de Breaking Bad", strip_accents("El Camino: Una película de Breaking Bad"))
        self.assertEqual("Como entrenar a tu dragon", strip_accents("Cómo entrenar a tu dragón"))
        self.assertEqual("Erase una vez en Hollywood", strip_accents("Érase una vez en… Hollywood"))

    def test_library_index(self):
        values = [
            "Padre no hay más que uno",
            "Élite",
            "Pequeñas mentirosas",
            "Capitán América: El primer vengador",
            "Alita: Ángel del combate",
            "Animales fantásticos y dónde encontrarlos",
            "Animales fantásticos: Los crímenes de Grindelwald",
            "Cafarnaúm",
            "El Camino: Una película de Breaking Bad",
            "Cómo entrenar a tu dragón",
        ]

        index, _ = build_title_index([dict(title=value) for value in values], [])

        self.assertGreater(index.search(strip_accents("Capitán América: El primer vengador")), 0.4)
        self.assertEqual(index.search(strip_accents("Capitán América: El primer vengador").lower())[0], 1.0)

if __name__ == '__main__':
    unittest.main()
