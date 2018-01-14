class LibraryCache(object):
    def __init__(self):
        self.dirty = True
        self.movies = []
        self.tvshows = []

    def is_dirty(self):
        return self.dirty

    def invalidate(self):
        self.dirty = True

    def set_library(self, movies, tvshows):
        self.movies = movies
        self.tvshows = tvshows

    def get_library(self):
        return self.movies, self.tvshows
