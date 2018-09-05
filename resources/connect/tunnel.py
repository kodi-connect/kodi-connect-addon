# pylint: disable=bare-except

import json
import traceback
import xbmcaddon

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
from tornado.httpclient import HTTPRequest

from connect import logger, strings
from connect.utils import notification

__addon__ = xbmcaddon.Addon()

class Tunnel(object):
    """Kodi Connect Websocket Connection"""
    def __init__(self, url, kodi, handler):
        self.ioloop = None
        self.url = url
        self.websocket = None
        self.connected = False
        self.should_stop = False

        self.kodi = kodi
        self.handler = handler

        self.periodic = PeriodicCallback(self.periodic_callback, 20000)

    def start(self):
        """Start IO loop and try to connect to the server"""
        self.ioloop = IOLoop.current()

        self.connect()
        self.periodic.start()
        self.ioloop.call_later(1, self.periodic_callback)
        logger.debug('Starting IOLoop')
        self.ioloop.start()
        logger.debug('IOLoop ended')
        IOLoop.clear_current()

    def stop(self):
        """Stop IO loop"""
        self.should_stop = True
        if self.websocket is not None:
            self.websocket.close()
            logger.debug('Websocket closed')
        self.periodic.stop()
        logger.debug('Periodic stopped')
        self.ioloop.stop()
        logger.debug('IOLoop stopped')

    def write_message(self, message):
        """Send message through websocket"""
        if self.websocket is None:
            logger.error('Not connected')
            return

        self.websocket.write_message(json.dumps(message))

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
        except:
            logger.debug('connection error: {}'.format(traceback.format_exc()))
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
                self.ioloop.call_later(1, self.periodic_callback)
                self.ioloop.call_later(3, self.periodic_callback)
                self.ioloop.call_later(5, self.periodic_callback)
                break

            message = json.loads(message_str)
            logger.debug(message)
            data = message['data']

            try:
                response_data = self.handler.handler(data)
            except:
                logger.error('Handler failed: {}'.format(traceback.format_exc()))
                response_data = {"status": "error", "error": "Unknown error"}

            response_message = {"correlationId": message['correlationId'], "data": response_data}

            self.write_message(response_message)

    def periodic_callback(self):
        """Periodic callback"""
        if self.websocket is None:
            self.connect()
        else:
            self.write_message({"ping": "pong"})

        try:
            self.kodi.update_cache()
        except:
            logger.error('Failed to update Kodi library: {}'.format(traceback.format_exc()))

    def get_async_tunnel(self):
        tunnel = self

        def send_async_message(data):
            """Send async message through websocket"""
            tunnel.ioloop.add_callback(tunnel.write_message, {"async": True, 'data': data})

        return send_async_message
