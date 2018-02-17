# eslint: disable=duplicate-code

import unittest

from test_util import run_one, wait_for_library_index
from connect.kodi import KodiInterface
from connect.library_cache import LibraryCache
from connect.handler import Handler

class TestSearchAndPlay(unittest.TestCase):
    def setUp(self):
        library_cache = LibraryCache()
        self.kodi = KodiInterface(library_cache)
        self.kodi.update_cache()
        wait_for_library_index(self.kodi)
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
