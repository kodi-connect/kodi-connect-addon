import xbmc

def _log(message):
    xbmc.log(u'[KodiConnect] {}'.format(message).encode('utf-8'), level=xbmc.LOGDEBUG)

def debug(message):
    _log(message)

def error(message):
    _log(u'[ERROR] {}'.format(message))
