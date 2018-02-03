import unittest

from test_util import run_one
from kodi import KodiInterface
from library_cache import LibraryCache
from handler import Handler

class TestHandler(unittest.TestCase):
    def setUp(self):
        library_cache = LibraryCache()
        self.kodi = KodiInterface(library_cache)
        self.kodi.update_cache()
        self.handler = Handler(self.kodi)

    def test_unknown_type(self):
        response = self.handler.handler({
            "type": "unknownType",
        })

        self.assertEqual(response['status'], 'error')
        self.assertEqual(response['error'], 'unknown_command')

    def test_unknown_command_type(self):
        response = self.handler.handler({
            "type": "command",
            "commandType": "unknownCommandType",
        })

        self.assertEqual(response['status'], 'error')
        self.assertEqual(response['error'], 'unknown_command')

if __name__ == '__main__':
    unittest.main()
