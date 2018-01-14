import sys
import os
import json
import threading
import xbmc
import xbmcaddon
import logging
from logging.config import dictConfig

__settings__ = xbmcaddon.Addon(id='script.kodiconnect')

KODI_CONNECT_URL = os.environ.get('KODI_CONNECT_URL', 'wss://kodiconnect.kislan.sk/ws')
BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(__settings__.getAddonInfo('path'), 'resources', 'lib' ))
sys.path.append(BASE_RESOURCE_PATH)

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect

from only_once import OnlyOnce, OnlyOnceException
from handler import Handler
from kodi import KodiInterface
from library_cache import LibraryCache
from custom_monitor import CustomMonitor
from custom_player import CustomPlayer

logging_config = dict(
    version = 1,
    formatters = {
        'f': {'format':
              '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
        },
    handlers = {
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.DEBUG}
        },
    loggers = {
        'tornado.general': {'handlers': ['h'],
                 'level': logging.DEBUG}
        }
)

dictConfig(logging_config)

class Client(object):
    def __init__(self, url, kodi, handler):
        self.url = url
        self.ioloop = IOLoop.current()
        self.ws = None
        self.should_stop = False

        self.kodi = kodi
        self.handler = handler

        self.periodic = PeriodicCallback(self.periodic_callback, 20000)

    def start(self):
        self.connect()
        self.periodic.start()
        self.ioloop.start()

    def stop(self):
        self.should_stop = True
        if self.ws is not None:
            self.ws.close()
        self.periodic.stop()
        self.ioloop.stop()

    @gen.coroutine
    def connect(self):
        username = __settings__.getSetting('username')
        secret = __settings__.getSetting('secret')
        if len(username) == 0 or len(secret) == 0:
            print('Username and/or secret not defined, not connecting')
            return

        print('trying to connect')
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception, e:
            print('connection error')
        else:
            print('connected')
            self.ws.write_message(json.dumps({ 'username': username, 'secret': secret }))
            self.run()

    @gen.coroutine
    def run(self):
        while True:
            message_str = yield self.ws.read_message()
            if message_str is None:
                print('connection closed')
                self.ws = None
                break

            try:
                message = json.loads(message_str)
                print(message)
                data = message['data']

                responseData = handler.handler(data)
            except Exception as e:
                print('handler failed:', e)
                responseData = { 'status': 'error', 'error': 'Unknown error' }

            self.ws.write_message(json.dumps({ 'correlationId': message['correlationId'], 'data': responseData }))

    def periodic_callback(self):
        if self.ws is None:
            self.connect()
        else:
            self.ws.write_message(json.dumps({ 'ping': 'pong' }))

        self.kodi.update_cache()

class ClientThread(threading.Thread):
    def __init__(self, client):
        self.client = client
        threading.Thread.__init__(self)
        print(self)

    def run(self):
        print(self)
        self.client.start()

    def stop(self):
        print('Stopping client')
        self.client.stop()

if __name__ == '__main__':
    xbmc.log('Starting Kodi connect tunnel', level=xbmc.LOGNOTICE)
    xbmc.log('Kodi connect pid={}'.format(os.getpid()), level=xbmc.LOGNOTICE)

    try:
        once = OnlyOnce()
    except OnlyOnceException:
        xbmc.log('Kodi connect tunnel already running, exiting', level=xbmc.LOGNOTICE)
        sys.exit(0)

    library_cache = LibraryCache()
    kodi = KodiInterface(library_cache)
    handler = Handler(kodi)

    monitor = CustomMonitor(kodi)
    player = CustomPlayer(kodi)
