import sys

import xbmc

def _log(message):
    log_message = u'[KodiConnect] {}'.format(message)
    if sys.version_info >= (3,):
        encoded_message_data = log_message
    else:
        encoded_message_data = log_message.encode('utf-8')
    xbmc.log(encoded_message_data, level=xbmc.LOGDEBUG)

def debug(message):
    _log(message)

def error(message):
    _log(u'[ERROR] {}'.format(message))
