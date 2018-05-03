# pylint: disable=duplicate-code

import unittest

from test_util import run_one, wait_for_library_index
from connect.kodi import KodiInterface
from connect.library_cache import LibraryCache
from connect.custom_player import CustomPlayer
from connect.handler import Handler

class TestPreviousNext(unittest.TestCase):
    def setUp(self):
        library_cache = LibraryCache()
        self.kodi = KodiInterface(library_cache)
        self.kodi.update_cache()
        wait_for_library_index(self.kodi)
        self.player = CustomPlayer()
        self.player.set_kodi(self.kodi)
        self.handler = Handler(self.kodi)

    def test_no_current_item_previous(self):
        current_item = self.player._get_current_item()
        self.assertIsNone(current_item)

        self.assertFalse(self.kodi.previous_item())

        current_item = self.player._get_current_item()
        self.assertIsNone(current_item)

    def test_no_previous_item(self):
        self.kodi.find_and_play({
            'titles': ['How I Met Your Mother'],
            'season': '1',
            'episode': '1',
        })

        self.handler.handler({
            "type": "command",
            "commandType": "previous",
        })
        run_one()

        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'episode')
        self.assertEqual(current_item['tvshowid'], 21)
        self.assertEqual(current_item['id'], 401)
        self.assertEqual(current_item['season'], 1)
        self.assertEqual(current_item['episode'], 1)

    def test_no_next_item(self):
        self.kodi.find_and_play({
            'titles': ['How I Met Your Mother'],
            'season': '6',
            'episode': '24',
        })

        self.handler.handler({
            "type": "command",
            "commandType": "next",
        })
        run_one()

        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'episode')
        self.assertEqual(current_item['tvshowid'], 21)
        self.assertEqual(current_item['id'], 536)
        self.assertEqual(current_item['season'], 6)
        self.assertEqual(current_item['episode'], 24)

    def test_previous_item(self):
        self.kodi.find_and_play({
            'titles': ['How I Met Your Mother'],
            'season': '2',
            'episode': '2',
        })

        self.handler.handler({
            "type": "command",
            "commandType": "previous",
        })
        run_one()

        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'episode')
        self.assertEqual(current_item['tvshowid'], 21)
        self.assertEqual(current_item['id'], 423)
        self.assertEqual(current_item['season'], 2)
        self.assertEqual(current_item['episode'], 1)

    def test_previous_item_cross_season(self):
        self.kodi.find_and_play({
            'titles': ['How I Met Your Mother'],
            'season': '2',
            'episode': '1',
        })

        self.handler.handler({
            "type": "command",
            "commandType": "previous",
        })
        run_one()

        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'episode')
        self.assertEqual(current_item['tvshowid'], 21)
        self.assertEqual(current_item['id'], 422)
        self.assertEqual(current_item['season'], 1)
        self.assertEqual(current_item['episode'], 22)

    def test_next_item(self):
        self.kodi.find_and_play({
            'titles': ['How I Met Your Mother'],
            'season': '1',
            'episode': '1',
        })

        self.handler.handler({
            "type": "command",
            "commandType": "next",
        })
        run_one()

        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'episode')
        self.assertEqual(current_item['tvshowid'], 21)
        self.assertEqual(current_item['id'], 402)
        self.assertEqual(current_item['season'], 1)
        self.assertEqual(current_item['episode'], 2)

    def test_next_item_cross_season(self):
        self.kodi.find_and_play({
            'titles': ['How I Met Your Mother'],
            'season': '1',
            'episode': '22',
        })

        self.handler.handler({
            "type": "command",
            "commandType": "next",
        })
        run_one()

        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'episode')
        self.assertEqual(current_item['tvshowid'], 21)
        self.assertEqual(current_item['id'], 423)
        self.assertEqual(current_item['season'], 2)
        self.assertEqual(current_item['episode'], 1)

if __name__ == '__main__':
    unittest.main()
