# pylint: disable=duplicate-code

import unittest

from test_util import run_one, wait_for_library_index
from connect.kodi import KodiInterface
from connect.library_cache import LibraryCache
from connect.custom_player import CustomPlayer
from connect.handler import Handler

class TestPlaybackControl(unittest.TestCase):
    def setUp(self):
        library_cache = LibraryCache()
        self.kodi = KodiInterface(library_cache)
        self.kodi.update_cache()
        wait_for_library_index(self.kodi)
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
