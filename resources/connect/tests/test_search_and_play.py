import unittest

from kodi import KodiInterface
from library_cache import LibraryCache
from custom_player import CustomPlayer

class TestSearchAndPlay(unittest.TestCase):
    def setUp(self):
        library_cache = LibraryCache()
        self.kodi = KodiInterface(library_cache)
        self.kodi.update_cache()
        self.player = CustomPlayer(self.kodi)

    def test_search_and_play_not_found(self):
        ret = self.kodi.find_and_play({
            'titles': ['some made up name'],
        })
        current_item = self.player._get_current_item()

        self.assertFalse(ret)
        self.assertIsNone(current_item)

    def test_search_and_play_tvshow(self):
        self.kodi.find_and_play({
            'titles': ['How I Met Your Mother'],
            'season': '2',
            'episode': '1',
        })
        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'episode')
        self.assertEqual(current_item['tvshowid'], 21)
        self.assertEqual(current_item['id'], 423)
        self.assertEqual(current_item['season'], 2)
        self.assertEqual(current_item['episode'], 1)

    def test_search_and_play_movie_by_title(self):
        self.kodi.find_and_play({
            'titles': ['Maze Runner'],
        })
        current_item = self.player._get_current_item()

        print(current_item)
        self.assertEqual(current_item['type'], 'movie')
        self.assertEqual(current_item['id'], 161)

    def test_search_and_play_movie_by_actor(self):
        self.kodi.find_and_play({
            'actors': ['Jason Statham'],
        })
        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'movie')
        self.assertIn(current_item['id'], [202, 163, 48])

    def test_search_and_play_movie_by_title_and_actor(self):
        self.kodi.find_and_play({
            'titles': ['Furious'],
            'actors': ['Jason Statham'],
        })
        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'movie')
        self.assertEqual(current_item['id'], 202)

if __name__ == '__main__':
    unittest.main()
