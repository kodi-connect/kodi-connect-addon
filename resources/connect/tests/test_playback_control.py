import unittest

from kodi import KodiInterface
from library_cache import LibraryCache
from custom_player import CustomPlayer

class TestPlaybackControl(unittest.TestCase):
    def setUp(self):
        library_cache = LibraryCache()
        self.kodi = KodiInterface(library_cache)
        self.kodi.update_cache()
        self.player = CustomPlayer(self.kodi)
        self.kodi.find_and_play({
            'titles': ['Maze Runner'],
        })

    def test_pause(self):
        self.kodi.pause()

        self.assertEqual(self.player.speed, 0)

    def test_resume(self):
        self.kodi.pause()

        self.assertEqual(self.player.speed, 0)

        self.kodi.resume()

        self.assertEqual(self.player.speed, 1)

    def test_stop(self):
        self.kodi.stop()

        self.assertEqual(self.player.speed, 0)
        self.assertIsNone(self.player.current_item)

        self.kodi.resume()

        self.assertEqual(self.player.speed, 0)
        self.assertIsNone(self.player.current_item)

if __name__ == '__main__':
    unittest.main()
