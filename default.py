import os
import sys
import xbmc
import xbmcgui
import xbmcaddon

__settings__ = xbmcaddon.Addon(id='script.kodiconnect')

BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(__settings__.getAddonInfo('path'), 'resources', 'lib'))
sys.path.append(BASE_RESOURCE_PATH)

#get actioncodes from https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Key.h
ACTION_PREVIOUS_MENU = 10

class MyClass(xbmcgui.Window):
  def onAction(self, action):
    if action == ACTION_PREVIOUS_MENU:
      self.close()

mydisplay = MyClass()
mydisplay.doModal()
del mydisplay
