# pylint: disable=wrong-import-position,wrong-import-order

import sys
import os
import logging
from logging.config import dictConfig
import xbmc
import xbmcaddon

if sys.platform == "win32" and sys.version_info >= (3, 8, 0):
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

__addon__ = xbmcaddon.Addon()

KODI_CONNECT_URL = os.environ.get('KODI_CONNECT_URL', 'wss://kodiconnect.kislan.sk/ws')

RESOURCES_PATH = xbmc.translatePath(os.path.join(__addon__.getAddonInfo('path'), 'resources'))
LIB_RESOURCES_PATH = xbmc.translatePath(os.path.join(__addon__.getAddonInfo('path'), 'resources', 'lib'))
sys.path.append(RESOURCES_PATH)
sys.path.append(LIB_RESOURCES_PATH)

import concurrent.futures
from tornado.ioloop import IOLoop

from connect import logger
from connect.only_once import OnlyOnce, OnlyOnceException
from connect.handler import Handler
from connect.kodi import KodiInterface
from connect.library_cache import LibraryCache
from connect.custom_monitor import CustomMonitor
from connect.custom_player import CustomPlayer
from connect.tunnel import Tunnel
from connect.tunnel_thread import TunnelThread

logger.debug(u'RESOURCES_PATHs: {}, {}'.format(RESOURCES_PATH, LIB_RESOURCES_PATH))
logger.debug(u'__file__: {}'.format(__file__))

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

def main():
    """Main function"""
    logger.debug('Starting')
    logger.debug(u'pid={}'.format(os.getpid()))

    try:
        __once__ = OnlyOnce()
        logger.debug(str(__once__))
    except OnlyOnceException:
        logger.debug('Tunnel already running, exiting')
        sys.exit(0)

    io_loop = IOLoop(make_current=False)

    library_cache = LibraryCache()
    kodi = KodiInterface(library_cache)
    handler = Handler(kodi)

    monitor = CustomMonitor(kodi)
    player = CustomPlayer()
    player.set_io_loop(io_loop)
    player.set_kodi(kodi)

    tunnel = Tunnel(io_loop, KODI_CONNECT_URL, kodi, handler)
    tunnel_thread = TunnelThread(tunnel)
    tunnel_thread.start()

    async_tunnel = tunnel.get_async_tunnel()
    player.set_async_tunnel(async_tunnel)

    try:
        while not monitor.abortRequested():
            # Sleep/wait for abort for 3 seconds
            if monitor.waitForAbort(3):
                # Abort was requested while waiting. We should exit
                break
    except KeyboardInterrupt:
        logger.debug('Interrupted')

    logger.debug('Stopping __once__')
    __once__.stop()
    logger.debug('Stopping Tunnel')
    tunnel_thread.stop()
    logger.debug('Joining Tunnel Thread')
    tunnel_thread.join()
    logger.debug('Clearing main IOLoop')
    IOLoop.clear_current()
    logger.debug('Stopping concurrent ThreadPool')
    concurrent.futures.thread._python_exit()  # pylint: disable=protected-access
    logger.debug('Exit')

if __name__ == '__main__':
    main()
