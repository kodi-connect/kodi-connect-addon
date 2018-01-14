import os
import sys
import xbmc
import xbmcgui
import xbmcaddon

__settings__ = xbmcaddon.Addon(id='plugin.kodiconnect')

BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(__settings__.getAddonInfo('path'), 'resources', 'lib'))
sys.path.append(BASE_RESOURCE_PATH)

