import unittest

from test_util import run_one
from kodi import KodiInterface
from library_cache import LibraryCache
from handler import Handler

class TestSearchAndPlay(unittest.TestCase):
    def setUp(self):
        library_cache = LibraryCache()
        self.kodi = KodiInterface(library_cache)
        self.kodi.update_cache()
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
