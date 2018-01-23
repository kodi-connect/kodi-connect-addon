import xbmc
import xbmcgui
import xbmcaddon

__Addon = xbmcaddon.Addon()

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

class Notifications():
    def __init__(self):
        self.last_notifications = {}

    def show(self, message, level='info', tag=None, recurring=False):
        if level == 'info':
            icon = xbmcgui.NOTIFICATION_INFO
        elif level == 'warn':
            icon = xbmcgui.NOTIFICATION_WARNING
        elif level == 'error':
            icon = xbmcgui.NOTIFICATION_ERROR
        else:
            icon = xbmcgui.NOTIFICATION_INFO

        if not recurring and tag in self.last_notifications and self.last_notifications[tag] == message:
            return

        if tag:
            self.last_notifications[tag] = message

        xbmcgui.Dialog().notification('Kodi Connect', encode(message), icon=icon, time=4000)

notif = Notifications()


def showInfoNotification(message):
    xbmcgui.Dialog().notification('Kodi Connect', encode(message), time=4000, sound=False)

def showErrorNotification(message):
    xbmcgui.Dialog().notification('Kodi Connect', encode(message), icon=xbmcgui.NOTIFICATION_ERROR, time=4000, sound=False)
