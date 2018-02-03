import unittest

from test_util import run_one
from kodi import KodiInterface
from library_cache import LibraryCache
from custom_player import CustomPlayer
from handler import Handler

class TestSearchAndPlay(unittest.TestCase):
    def setUp(self):
        library_cache = LibraryCache()
        self.kodi = KodiInterface(library_cache)
        self.kodi.update_cache()
        self.player = CustomPlayer()
        self.player.set_kodi(self.kodi)
        self.handler = Handler(self.kodi)

    def test_search_and_play_not_found(self):
        self.handler.handler({
            "type": "command",
            "commandType": "searchAndPlay",
            "filter": {
                'titles': ['some made up name'],
            }
        })
        run_one()

        current_item = self.player._get_current_item()

        self.assertIsNone(current_item)

    def test_search_and_play_tvshow(self):
        self.handler.handler({
            "type": "command",
            "commandType": "searchAndPlay",
            "filter": {
                'titles': ['How I Met Your Mother'],
                'season': '2',
                'episode': '1',
            }
        })
        run_one()

        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'episode')
        self.assertEqual(current_item['tvshowid'], 21)
        self.assertEqual(current_item['id'], 423)
        self.assertEqual(current_item['season'], 2)
        self.assertEqual(current_item['episode'], 1)

    def test_search_and_play_tvshow_next_episode(self):
        self.handler.handler({
            "type": "command",
            "commandType": "searchAndPlay",
            "filter": {
                u'genres': [],
                u'episode': None,
                u'roles': [],
                u'season': None,
                u'mediaType': None,
                u'titles': [u'How I Met Your Mother', u'Goodbye How I Met Your Mother', u'How I Met Your Mother: Extras', u'How I Met Your Puppet Mother'],
                u'actors': [],
                u'collections': [],
            }
        })
        run_one()

        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'episode')
        self.assertEqual(current_item['tvshowid'], 21)
        self.assertEqual(current_item['id'], 487)
        self.assertEqual(current_item['season'], 4)
        self.assertEqual(current_item['episode'], 23)

    def test_search_and_play_movie_by_title(self):
        self.handler.handler({
            "type": "command",
            "commandType": "searchAndPlay",
            "filter": {
                'titles': ['Maze Runner'],
            }
        })
        run_one()

        current_item = self.player._get_current_item()

        print(current_item)
        self.assertEqual(current_item['type'], 'movie')
        self.assertEqual(current_item['id'], 161)

    def test_search_and_play_movie_by_actor(self):
        self.handler.handler({
            "type": "command",
            "commandType": "searchAndPlay",
            "filter": {
                'actors': ['Jason Statham'],
            }
        })
        run_one()

        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'movie')
        self.assertIn(current_item['id'], [202, 163, 48])

    def test_search_and_play_movie_by_title_and_actor(self):
        self.handler.handler({
            "type": "command",
            "commandType": "searchAndPlay",
            "filter": {
                'titles': ['Furious'],
                'actors': ['Jason Statham'],
            }
        })
        run_one()

        current_item = self.player._get_current_item()

        self.assertEqual(current_item['type'], 'movie')
        self.assertEqual(current_item['id'], 202)

if __name__ == '__main__':
    unittest.main()
