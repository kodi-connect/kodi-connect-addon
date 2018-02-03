import os
import sys
import urlparse

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

addon = xbmcaddon.Addon()
handle = int(sys.argv[1])

xbmcplugin.setContent(handle, 'movies')

LIB_RESOURCE_PATH = xbmc.translatePath(os.path.join(addon.getAddonInfo('path'), 'resources', 'lib' ))
APP_RESOURCE_PATH = xbmc.translatePath(os.path.join(addon.getAddonInfo('path'), 'resources', 'connect' ))
sys.path.append(LIB_RESOURCE_PATH)
sys.path.append(APP_RESOURCE_PATH)

import strings
from log import logger

logger.debug('RESOURCE_PATHs: {}, {}'.format(LIB_RESOURCE_PATH, APP_RESOURCE_PATH))
logger.debug('__file__: {}'.format(__file__))

import kodi_rpc
from utils import _get

args = urlparse.parse_qs(sys.argv[2][1:])

logger.debug('argv: {}'.format(sys.argv[2][1:]))
logger.debug('args: {}'.format(str(args)))

entities = args.get('entities', [''])[0].split('x')
total_items = len(entities)

logger.debug('entities: {}'.format(str(entities)))

if not entities:
    xbmcplugin.addDirectoryItem(handle, '', xbmcgui.ListItem(strings.NO_ITEMS_FOUND), isFolder=False)

for entity in entities:
    entity_type = entity[:1]
    entity_id = entity[1:]

    if not entity_id: continue
    entity_id = int(entity_id)

    if entity_type == 'm':
        details = kodi_rpc.get_movie_details(entity_id)
        logger.debug(details)

        label = details.get('label', 'N/A')
        plot = details.get('plot', 'N/A')
        url = details.get('file', '')
        fanart = details.get('fanart')
        thumbnail = details.get('thumbnail')

        item = xbmcgui.ListItem(label)
        item.setProperty('IsPlayable', 'true')
        item.setInfo('video', { "plot": plot })
        if fanart: item.setArt({ "fanart": fanart })
        if thumbnail: item.setArt({ "thumbnail": thumbnail, "poster": thumbnail })

        xbmcplugin.addDirectoryItem(handle, url, item, totalItems=total_items)
    elif entity_type == 't':
        details = kodi_rpc.get_tvshow_details(entity_id)
        logger.debug(details)

        label = details.get('label', 'N/A')
        plot = details.get('plot', 'N/A')

        item = xbmcgui.ListItem(label)
        item.setInfo('video', { "plot": plot })

        xbmcplugin.addDirectoryItem(handle, '', item, totalItems=total_items)

xbmcplugin.endOfDirectory(handle)
