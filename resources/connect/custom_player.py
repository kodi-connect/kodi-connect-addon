import xbmc

class CustomPlayer(xbmc.Player):
    def __init__(self, kodi):
        xbmc.Player.__init__(self)
        self.kodi = kodi

    def onPlayBackStarted(self):
        self.kodi.update_current_item()
