import xbmc

def log(message, level=xbmc.LOGDEBUG):
    xbmc.log('[KodiConnect] {}'.format(message), level=level)

def _log(message, level=xbmc.LOGDEBUG):
    xbmc.log('[KodiConnect] {}'.format(message), level=level)

class Logger():
    def debug(self, message):
        _log(message, level=xbmc.LOGDEBUG)

    def notice(self, message):
        _log(message, xbmc.LOGNOTICE)

    def error(self, message):
        _log(message, xbmc.LOGERROR)

logger = Logger()
