import sys
import os
import json
import threading
import xbmc
import xbmcaddon
import logging
from logging.config import dictConfig

__settings__ = xbmcaddon.Addon()

KODI_CONNECT_URL = os.environ.get('KODI_CONNECT_URL', 'wss://kodiconnect.kislan.sk/ws')
BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(__settings__.getAddonInfo('path'), 'resources', 'lib' ))
sys.path.append(BASE_RESOURCE_PATH)

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
from tornado.httpclient import HTTPRequest

from only_once import OnlyOnce, OnlyOnceException
from handler import Handler
from kodi import KodiInterface
from library_cache import LibraryCache
from custom_monitor import CustomMonitor
from custom_player import CustomPlayer
from utils import showNotification

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
        self.last_notification_message = None

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

    def show_notification(self, message):
        if self.last_notification_message != message:
            self.last_notification_message = message
            showNotification(message)

    @gen.coroutine
    def connect(self):
        username = __settings__.getSetting('username')
        secret = __settings__.getSetting('secret')
        if len(username) == 0 or len(secret) == 0:
            print('Username and/or secret not defined, not connecting')
            return

        print('trying to connect')
        try:
            request = HTTPRequest(self.url, auth_username=username, auth_password=secret)

            self.ws = yield websocket_connect(request)
        except Exception, e:
            print('connection error:', e)
            self.ws = None
            self.show_notification('Failed to connect')
        else:
            print('connected')
            self.connected = True
            self.show_notification('Connected')
            self.run()

    @gen.coroutine
    def run(self):
        while True:
            message_str = yield self.ws.read_message()
            if message_str is None:
                print('connection closed')
                self.ws = None
                self.show_notification('Disconnected')
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
        print('periodic_callback')
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
    player = CustomPlayer()
    player.set_kodi(kodi)

    client = Client(KODI_CONNECT_URL, kodi, handler)
    client_thread = ClientThread(client)
    client_thread.start()

    try:
        while not monitor.abortRequested():
            # Sleep/wait for abort for 3 seconds
            if monitor.waitForAbort(3):
                # Abort was requested while waiting. We should exit
                break
    except KeyboardInterrupt:
        print('Interrupted')

    print('Stopping Kodi Connect Tunnel')
    client_thread.stop()
    print('Joining Tunnel Thread')
    client_thread.join()
    print('Kodi Connect Exit')


