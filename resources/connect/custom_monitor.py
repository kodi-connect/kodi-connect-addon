import xbmc
from connect import logger

class CustomMonitor(xbmc.Monitor):
    def __init__(self, kodi):
        xbmc.Monitor.__init__(self)
        self.kodi = kodi

# pylint: disable=invalid-name
    def onScanFinished(self, library):
        logger.debug(u'onScanFinished: {}'.format(library))
        self.kodi.invalidate_cache()
