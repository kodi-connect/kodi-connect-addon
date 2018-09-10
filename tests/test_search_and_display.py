# pylint: disable=duplicate-code

import unittest

from test_util import run_one, get_library_cache_and_index
from connect.kodi import KodiInterface
from connect.handler import Handler

class TestSearchAndDisplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library_cache, cls.library_index = get_library_cache_and_index()

    def setUp(self):
        self.kodi = KodiInterface(self.library_cache)
        self.kodi.library_index = self.library_index

        self.handler = Handler(self.kodi)

    def test_search_and_display(self):
        self.handler.handler({
            "type": "command",
            "commandType": "searchAndDisplay",
            "filter": {
                'actors': ['Jason Statham'],
            }
        })
        run_one()

if __name__ == '__main__':
    unittest.main()
