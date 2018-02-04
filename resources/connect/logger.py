import xbmc

def _log(message):
    xbmc.log('[KodiConnect] {}'.format(message))

def debug(message):
    _log(message)

def error(message):
    _log('[ERROR] {}'.format(message))
