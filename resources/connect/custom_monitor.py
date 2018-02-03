import xbmc
from log import logger

class CustomMonitor(xbmc.Monitor):
    def __init__(self, kodi):
        xbmc.Monitor.__init__(self)
        self.kodi = kodi

    def onScanFinished(self, library):
        logger.debug('onScanFinished: {}'.format(library))
        self.kodi.invalidate_cache()
