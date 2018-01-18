import xbmc

class CustomPlayer(xbmc.Player):
    def set_kodi(self, kodi):
        self.kodi = kodi

    def onPlayBackStarted(self):
        print('onPlayBackStarted')
        if self.kodi:
            self.kodi.update_current_item()
