# pylint: disable=duplicate-code

import unittest

from test_util import get_library_cache_and_index
from connect.kodi import KodiInterface
from connect.handler import Handler

class TestHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library_cache, cls.library_index = get_library_cache_and_index()

    def setUp(self):
        self.kodi = KodiInterface(self.library_cache)
        self.kodi.library_index = self.library_index

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
