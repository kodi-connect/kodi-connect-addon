import time

from tornado.ioloop import IOLoop

from connect.kodi import KodiInterface
from connect.library_cache import LibraryCache

def run_one():
    IOLoop.instance().add_callback(lambda: IOLoop.instance().stop())
    IOLoop.instance().start()

def wait_for_library_index(kodi, max_seconds=10):
    start = time.time()

    while int(time.time() - start) < max_seconds:
        if kodi.library_index is not None:
            return
        time.sleep(0.1)

    raise Exception("Library index not created")

def get_library_cache_and_index():
    library_cache = LibraryCache()
    kodi = KodiInterface(library_cache)
    kodi.update_cache()
    wait_for_library_index(kodi)
    return library_cache, kodi.library_index
