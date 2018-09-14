# pylint: disable=duplicate-code

import unittest

from ngram import NGram

class TestHandler(unittest.TestCase):
    def setUp(self):
        pass

    def test_scifi_genre(self):
        index = NGram(items=['Sci-Fi'], key=lambda x: x.lower())

        self.assertGreater(index.search('science fiction')[0][1], 0)
        self.assertEqual(index.search('sci-fi')[0][1], 1)

if __name__ == '__main__':
    unittest.main()
