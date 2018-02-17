import time

from tornado.ioloop import IOLoop

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
