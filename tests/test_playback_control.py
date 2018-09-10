# pylint: disable=duplicate-code

import unittest

from test_util import run_one, get_library_cache_and_index
from connect.kodi import KodiInterface
from connect.custom_player import CustomPlayer
from connect.handler import Handler

class TestPlaybackControl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library_cache, cls.library_index = get_library_cache_and_index()

    def setUp(self):
        self.kodi = KodiInterface(self.library_cache)
        self.kodi.library_index = self.library_index

        self.player = CustomPlayer()
        self.player.set_kodi(self.kodi)
        self.handler = Handler(self.kodi)
        self.kodi.find_and_play({
            'titles': ['Maze Runner'],
        })

    def test_pause(self):
        self.handler.handler({
            "type": "command",
            "commandType": "pause",
        })
        run_one()

        self.assertEqual(self.player.speed, 0)

    def test_resume(self):
        self.handler.handler({
            "type": "command",
            "commandType": "pause",
        })
        run_one()

        self.assertEqual(self.player.speed, 0)

        self.handler.handler({
            "type": "command",
            "commandType": "resume",
        })
        run_one()

        self.assertEqual(self.player.speed, 1)

    def test_stop(self):
        self.handler.handler({
            "type": "command",
            "commandType": "stop",
        })
        run_one()

        self.assertEqual(self.player.speed, 0)
        self.assertIsNone(self.player.current_item)

        self.handler.handler({
            "type": "command",
            "commandType": "resume",
        })
        run_one()

        self.assertEqual(self.player.speed, 0)
        self.assertIsNone(self.player.current_item)

if __name__ == '__main__':
    unittest.main()
