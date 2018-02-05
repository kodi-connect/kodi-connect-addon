# pylint: disable=global-statement

import os
import xbmcgui

from connect import strings

def _get(dictionary, *keys):
    return reduce(lambda d, key: d.get(key) if d else None, keys, dictionary)

def _pick(dictionary, *keys):
    return (dictionary.get(key) for key in keys)

def encode(string):
    result = ''

    try:
        result = string.encode('UTF-8', 'replace')
    except UnicodeDecodeError:
        result = 'Unicode Error'

    return result

__last_notifications__ = {}

def notification(message, level='info', tag=None, recurring=False):
    global __last_notifications__

    if level == 'info':
        icon = xbmcgui.NOTIFICATION_INFO
    elif level == 'warn':
        icon = xbmcgui.NOTIFICATION_WARNING
    elif level == 'error':
        icon = xbmcgui.NOTIFICATION_ERROR
    else:
        icon = xbmcgui.NOTIFICATION_INFO

    if tag and tag in __last_notifications__ and __last_notifications__[tag] == message and not recurring:
        return

    if tag:
        __last_notifications__[tag] = message

    xbmcgui.Dialog().notification(strings.KODI_CONNECT, encode(message), icon=icon, time=4000)

def cmd_exists(cmd):
    return any(
        os.access(os.path.join(path, cmd), os.X_OK)
        for path in os.environ["PATH"].split(os.pathsep)
    )

__cec_client_found__ = None

def cec_available():
    global __cec_client_found__
    if __cec_client_found__ is None:
        __cec_client_found__ = cmd_exists('cec-client')
    return __cec_client_found__
