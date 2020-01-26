import xbmc

def _log(message):
    xbmc.log(u'[KodiConnect] {}'.format(message), level=xbmc.LOGDEBUG)

def debug(message):
    _log(message)

def error(message):
    _log(u'[ERROR] {}'.format(message))
