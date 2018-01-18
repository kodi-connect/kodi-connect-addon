import unittest

from kodi import KodiInterface
from library_cache import LibraryCache
# from library_index import create_library_index

class TestIndexing(unittest.TestCase):
    def setUp(self):
        library_cache = LibraryCache()
        self.kodi = KodiInterface(library_cache)
        self.kodi.update_cache()
        self.movies, self.tvshows = self.kodi._get_video_library()
        # self.library_index = create_library_index(self.movies, self.tvshows)

    def test_indexing(self):
        print('test')

        # ret = None
        # # ret = self.library_index.find_by_title(['how i met your mother'])
        # # ret = self.library_index.find_by_title(['rogue one star wars story'])
        # # ret = self.library_index.find_by_collection(['Fast and furious'])
        # # ret = self.library_index.find_by_collection(['star wars'])
        # # ret = self.library_index.find_by_genre(['Action', 'Comedy'])
        # ret = self.library_index.find_by_filter({
        #     # 'titles': ['star wars episode'],
        #     # 'titles': ['how i met your mother'],
        #     # 'genres': ['action', 'comedy'],
        #     # 'roles': ['marshall eriksen'],
        #     'actors': ['jason statham'],
        # })
        # # print(ret)
        # print([entity['title'] for entity in ret])

        # ret = self.library_index.find_best_by_filter({
        #     # 'titles': ['star wars episode'],
        #     # 'titles': ['how i met your mother'],
        #     # 'genres': ['action', 'comedy'],
        #     # 'roles': ['marshall eriksen'],
        #     'actors': ['jason statham'],
        # })
        # print(ret['title'])

        # # start = time.time()

        # # print('Find similar role took {} ms'.format(int((time.time() - start) * 1000)))

if __name__ == '__main__':
    unittest.main()
