import xbmc

class CustomMonitor(xbmc.Monitor):
    def __init__(self, kodi):
        xbmc.Monitor.__init__(self)
        self.kodi = kodi

    def onScanFinished(self, library):
        xbmc.log('onScanFinished: {}'.format(library), level=xbmc.LOGNOTICE)
        self.kodi.invalidate_cache()
