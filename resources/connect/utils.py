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

def showNotification(message):
    xbmcgui.Dialog().notification('Kodi Connect', encode(message), time=4000, icon=xbmc.translatePath(__Addon.getAddonInfo('path') + '/icon.png'), sound=False)
