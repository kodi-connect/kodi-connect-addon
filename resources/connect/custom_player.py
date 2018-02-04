import xbmc
from connect import logger

class CustomPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self, args, kwargs)
        self.kodi = None

    def set_kodi(self, kodi):
        self.kodi = kodi

    def onPlayBackStarted(self):
        logger.debug('onPlayBackStarted')
        if self.kodi:
            self.kodi.update_current_item()
