import xbmc

def _log(message):
    xbmc.log('[KodiConnect] {}'.format(message))

class Logger():
    def debug(self, message):
        _log(message)

    def error(self, message):
        _log('[ERROR] {}'.format(message))

logger = Logger()
