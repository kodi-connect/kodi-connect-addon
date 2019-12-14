import unittest

import xbmcaddon


class TestHandler(unittest.TestCase):
    def setUp(self):
        pass

    def test_mocked_version(self):
        __addon__ = xbmcaddon.Addon()
        VERSION = __addon__.getAddonInfo('version')

        self.assertEqual('xversionx', VERSION)

if __name__ == '__main__':
    unittest.main()
