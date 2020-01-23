# pylint: disable=duplicate-code,protected-access
# coding=utf-8

import unittest

from ngram import NGram

from connect.utils import strip_accents
from connect.library_index import build_title_index

class TestAccent(unittest.TestCase):
    def test_strip_accent(self):
        self.assertEqual("Padre no hay mas que uno", strip_accents("Padre no hay más que uno"))
        self.assertEqual("Elite", strip_accents("Élite"))
        self.assertEqual("Pequenas mentirosas", strip_accents("Pequeñas mentirosas"))
        self.assertEqual("Capitan America: El primer vengador", strip_accents("Capitán América: El primer vengador"))

    def test_library_index(self):
        values = [
            "Padre no hay más que uno",
            "Élite",
            "Pequeñas mentirosas",
            "Capitán América: El primer vengador",
        ]

        index, _ = build_title_index([dict(title=value) for value in values], [])

        self.assertGreater(index.search(strip_accents("Capitán América: El primer vengador")), 0.4)

if __name__ == '__main__':
    unittest.main()
