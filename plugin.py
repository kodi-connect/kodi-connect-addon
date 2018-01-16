import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

addon = xbmcaddon.Addon()

item = xbmcgui.ListItem('Hello, World')
xbmcplugin.addDirectoryItem(int(sys.argv[1]), '', item, isFolder=0)
xbmcplugin.endOfDirectory(int(sys.argv[1]))
