# pylint: disable=broad-except,wrong-import-position

import sys
import os
import json
import threading
import logging
from logging.config import dictConfig
import xbmc
import xbmcaddon

__addon__ = xbmcaddon.Addon()

KODI_CONNECT_URL = os.environ.get('KODI_CONNECT_URL', 'wss://kodiconnect.kislan.sk/ws')

RESOURCES_PATH = xbmc.translatePath(os.path.join(__addon__.getAddonInfo('path'), 'resources'))
LIB_RESOURCES_PATH = xbmc.translatePath(os.path.join(__addon__.getAddonInfo('path'), 'resources', 'lib'))
sys.path.append(RESOURCES_PATH)
sys.path.append(LIB_RESOURCES_PATH)

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
from tornado.httpclient import HTTPRequest

from connect import logger, strings
from connect.only_once import OnlyOnce, OnlyOnceException
from connect.handler import Handler
from connect.kodi import KodiInterface
from connect.library_cache import LibraryCache
from connect.custom_monitor import CustomMonitor
from connect.custom_player import CustomPlayer
from connect.utils import notification

logger.debug('RESOURCES_PATHs: {}, {}'.format(RESOURCES_PATH, LIB_RESOURCES_PATH))
logger.debug('__file__: {}'.format(__file__))

__logging_config__ = dict(
    version=1,
    formatters={
        'f': {
            'format':
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    handlers={
        'h': {
            'class': 'logging.StreamHandler',
            'formatter': 'f',
            'level': logging.DEBUG
        }
    },
    loggers={
        'tornado.general': {
            'handlers': ['h'],
            'level': logging.DEBUG
        }
    }
)

dictConfig(__logging_config__)

class Client(object):
    """Kodi Connect Websocket Connection"""
    def __init__(self, url, kodi, handler):
        self.url = url
        self.websocket = None
        self.connected = False
        self.should_stop = False

        self.kodi = kodi
        self.handler = handler

        self.periodic = PeriodicCallback(self.periodic_callback, 20000)

    def start(self):
        """Start IO loop and try to connect to the server"""
        self.connect()
        self.periodic.start()
        IOLoop.current().start()

    def stop(self):
        """Stop IO loop"""
        self.should_stop = True
        if self.websocket is not None:
            self.websocket.close()
        self.periodic.stop()
        IOLoop.current().stop()

    @gen.coroutine
    def connect(self):
        """Connect to the server and update connection to websocket"""
        email = __addon__.getSetting('email')
        secret = __addon__.getSetting('secret')
        if not email or not secret:
            logger.debug('Email and/or secret not defined, not connecting')
            return

        logger.debug('trying to connect')
        try:
            request = HTTPRequest(self.url, auth_username=email, auth_password=secret)

            self.websocket = yield websocket_connect(request)
        except Exception as ex:
            logger.debug('connection error: {}'.format(str(ex)))
            self.websocket = None
            notification(strings.FAILED_TO_CONNECT, level='error', tag='connection')
        else:
            logger.debug('Connected')
            self.connected = True
            notification(strings.CONNECTED, tag='connection')
            self.run()

    @gen.coroutine
    def run(self):
        """Main loop handling incomming messages"""
        while True:
            message_str = yield self.websocket.read_message()
            if message_str is None:
                logger.debug('Connection closed')
                self.websocket = None
                notification(strings.DISCONNECTED, level='warn', tag='connection')
                break

            try:
                message = json.loads(message_str)
                logger.debug(message)
                data = message['data']

                response_data = self.handler.handler(data)
            except Exception as ex:
                logger.error('Handler failed: {}'.format(str(ex)))
                response_data = {"status": "error", "error": "Unknown error"}

            self.websocket.write_message(json.dumps({"correlationId": message['correlationId'], "data": response_data}))

    def periodic_callback(self):
        """Periodic callback"""
        logger.debug('periodic_callback')
        if self.websocket is None:
            self.connect()
        else:
            self.websocket.write_message(json.dumps({"ping": "pong"}))

        try:
            self.kodi.update_cache()
        except Exception as ex:
            logger.error('Failed to update Kodi library: {}'.format(str(ex)))

class ClientThread(threading.Thread):
    """Background thread for Client"""
    def __init__(self, client):
        self.client = client
        threading.Thread.__init__(self)

    def run(self):
        self.client.start()

    def stop(self):
        """Stop client"""
        logger.debug('Stopping client')
        self.client.stop()

def main():
    """Main function"""
    logger.debug('Starting')
    logger.debug('pid={}'.format(os.getpid()))

    try:
        __once__ = OnlyOnce()
        logger.debug(str(__once__))
    except OnlyOnceException:
        logger.debug('Tunnel already running, exiting')
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
        logger.debug('Interrupted')

    logger.debug('Stopping Tunnel')
    client_thread.stop()
    logger.debug('Joining Tunnel Thread')
    client_thread.join()
    logger.debug('Exit')

if __name__ == '__main__':
    main()
