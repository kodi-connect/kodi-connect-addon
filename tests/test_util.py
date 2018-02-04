from tornado.ioloop import IOLoop

def run_one():
    IOLoop.instance().add_callback(lambda: IOLoop.instance().stop())
    IOLoop.instance().start()
