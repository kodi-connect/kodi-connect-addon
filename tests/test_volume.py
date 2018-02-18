# eslint: disable=duplicate-code

import unittest

from test_util import run_one
from connect.kodi import KodiInterface
from connect.library_cache import LibraryCache
from connect.handler import Handler
from connect import kodi_rpc

class TestVolume(unittest.TestCase):
    def setUp(self):
        library_cache = LibraryCache()
        self.kodi = KodiInterface(library_cache)
        self.handler = Handler(self.kodi)

        self.handler.handler({
            "type": "command",
            "commandType": "setVolume",
            "volume": 50,
        })
        run_one()

        self.handler.handler({
            "type": "command",
            "commandType": "setMute",
            "volume": False,
        })
        run_one()

    def _test_set_volume(self, volume):
        self.handler.handler({
            "type": "command",
            "commandType": "setVolume",
            "volume": volume,
        })
        run_one()

        kodi_volume = kodi_rpc.get_volume()
        self.assertEqual(kodi_volume, volume)

    def _test_adjust_volume(self, volume, expected_volume):
        self.handler.handler({
            "type": "command",
            "commandType": "adjustVolume",
            "volume": volume,
        })
        run_one()

        kodi_volume = kodi_rpc.get_volume()
        self.assertEqual(kodi_volume, expected_volume)

    def _test_set_mute(self, mute):
        self.handler.handler({
            "type": "command",
            "commandType": "setMute",
            "mute": mute,
        })
        run_one()

        kodi_muted = kodi_rpc.get_muted()
        self.assertEqual(kodi_muted, mute)

    def test_set_volume(self):
        self._test_set_volume(50)
        self._test_set_volume(0)
        self._test_set_volume(100)
        self._test_set_volume(25)

    def test_adjust_volume(self):
        self._test_adjust_volume(20, 70)
        self._test_adjust_volume(100, 100)
        self._test_adjust_volume(10, 100)
        self._test_adjust_volume(-45, 55)
        self._test_adjust_volume(-70, 0)
        self._test_adjust_volume(-20, 0)

    def test_set_mute(self):
        self._test_set_mute(True)
        self._test_set_mute(False)
        self._test_set_mute(False)
        self._test_set_mute(True)
        self._test_set_mute(True)


if __name__ == '__main__':
    unittest.main()
