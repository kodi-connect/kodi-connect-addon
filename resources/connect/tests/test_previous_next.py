import unittest

from kodi import KodiInterface
from library_cache import LibraryCache
from custom_player import CustomPlayer

class TestPreviousNext(unittest.TestCase):
    def setUp(self):
        library_cache = LibraryCache()
        self.kodi = KodiInterface(library_cache)
        self.kodi.update_cache()
        self.player = CustomPlayer(self.kodi)

    def test_no_current_item_previous(self):
      current_item = self.player._get_current_item()
      self.assertIsNone(current_item)

      self.assertFalse(self.kodi.previous_item())

      current_item = self.player._get_current_item()
      self.assertIsNone(current_item)

    def test_no_previous_item(self):
        self.kodi.find_and_play({
            'titles': ['how i met your mother'],
            'season': '1',
            'episode': '1',
        })

        self.assertFalse(self.kodi.previous_item())

        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'episode')
        self.assertEqual(current_item['tvshowid'], 21)
        self.assertEqual(current_item['id'], 401)
        self.assertEqual(current_item['season'], 1)
        self.assertEqual(current_item['episode'], 1)

    def test_no_next_item(self):
        self.kodi.find_and_play({
            'titles': ['how i met your mother'],
            'season': '6',
            'episode': '24',
        })

        self.assertFalse(self.kodi.next_item())

        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'episode')
        self.assertEqual(current_item['tvshowid'], 21)
        self.assertEqual(current_item['id'], 536)
        self.assertEqual(current_item['season'], 6)
        self.assertEqual(current_item['episode'], 24)

    def test_previous_item(self):
        self.kodi.find_and_play({
            'titles': ['how i met your mother'],
            'season': '2',
            'episode': '2',
        })
        self.assertTrue(self.kodi.previous_item())

        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'episode')
        self.assertEqual(current_item['tvshowid'], 21)
        self.assertEqual(current_item['id'], 423)
        self.assertEqual(current_item['season'], 2)
        self.assertEqual(current_item['episode'], 1)

    def test_previous_item_cross_season(self):
        self.kodi.find_and_play({
            'titles': ['how i met your mother'],
            'season': '2',
            'episode': '1',
        })
        self.assertTrue(self.kodi.previous_item())

        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'episode')
        self.assertEqual(current_item['tvshowid'], 21)
        self.assertEqual(current_item['id'], 422)
        self.assertEqual(current_item['season'], 1)
        self.assertEqual(current_item['episode'], 22)

    def test_next_item(self):
        self.kodi.find_and_play({
            'titles': ['how i met your mother'],
            'season': '1',
            'episode': '1',
        })
        self.assertTrue(self.kodi.next_item())

        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'episode')
        self.assertEqual(current_item['tvshowid'], 21)
        self.assertEqual(current_item['id'], 402)
        self.assertEqual(current_item['season'], 1)
        self.assertEqual(current_item['episode'], 2)

    def test_next_item_cross_season(self):
        self.kodi.find_and_play({
            'titles': ['how i met your mother'],
            'season': '1',
            'episode': '22',
        })
        self.assertTrue(self.kodi.next_item())

        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'episode')
        self.assertEqual(current_item['tvshowid'], 21)
        self.assertEqual(current_item['id'], 423)
        self.assertEqual(current_item['season'], 2)
        self.assertEqual(current_item['episode'], 1)

if __name__ == '__main__':
    unittest.main()
