import xbmc
from log import logger

class CustomPlayer(xbmc.Player):
    def set_kodi(self, kodi):
        self.kodi = kodi

    def onPlayBackStarted(self):
        logger.debug('onPlayBackStarted')
        if self.kodi:
            self.kodi.update_current_item()
