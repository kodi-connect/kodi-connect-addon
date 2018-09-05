import xbmc
from connect import logger

class CustomPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self, args, kwargs)
        self.kodi = None
        self.async_tunnel = None

    def set_kodi(self, kodi):
        self.kodi = kodi

    def set_async_tunnel(self, async_tunnel):
        self.async_tunnel = async_tunnel

    def onPlayBackStarted(self):
        logger.debug('onPlayBackStarted')
        if self.kodi:
            self.kodi.update_current_item()
        self._send_playback_status()

    def onPlayBackPaused(self):
        logger.debug('onPlaybackPaused')
        self._send_playback_status()

    def onPlayBackStopped(self):
        logger.debug('onPlaybackStopped')
        self._send_playback_status()

    def _send_playback_status(self):
        if not self.async_tunnel or not self.kodi:
            return

        state = self.kodi.get_state()
        addon_change = self.kodi.is_playback_addon_change()

        self.async_tunnel({
            'type': 'change_state',
            'state': state,
            'changed': 'player',
            'addon_change': addon_change
        })
