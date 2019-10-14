import xbmc

from connect import logger
from connect.utils import send_playback_status


class CustomPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self, args, kwargs)
        self.io_loop = None
        self.kodi = None
        self.async_tunnel = None

    def set_io_loop(self, io_loop):
        self.io_loop = io_loop

    def set_kodi(self, kodi):
        self.kodi = kodi

    def set_async_tunnel(self, async_tunnel):
        self.async_tunnel = async_tunnel

    def onPlayBackStarted(self):
        logger.debug('onPlayBackStarted')
        if self.kodi:
            self.kodi.update_current_item()
        self.async_send_playback_status()

    def onPlayBackResumed(self):
        logger.debug('onPlayBackResumed')
        if self.kodi:
            self.kodi.update_current_item()
        self.async_send_playback_status()

    def onPlayBackPaused(self):
        logger.debug('onPlaybackPaused')
        self.async_send_playback_status()

    def onPlayBackStopped(self):
        logger.debug('onPlaybackStopped')
        self.async_send_playback_status()

    def async_send_playback_status(self):
        if self.io_loop and self.async_tunnel and self.kodi:
            logger.debug('async_send_playback_status')
            self.io_loop.add_callback(
                self.io_loop.call_later, 1, send_playback_status, self.kodi, self.async_tunnel
            )
