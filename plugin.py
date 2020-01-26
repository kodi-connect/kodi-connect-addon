# pylint: disable=wrong-import-position

import os
import sys
import urlparse

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

__addon__ = xbmcaddon.Addon()
__handle__ = int(sys.argv[1])
__args__ = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(__handle__, 'movies')

RESOURCES_PATH = xbmc.translatePath(os.path.join(__addon__.getAddonInfo('path'), 'resources'))
LIB_RESOURCES_PATH = xbmc.translatePath(os.path.join(__addon__.getAddonInfo('path'), 'resources', 'lib'))
sys.path.append(RESOURCES_PATH)
sys.path.append(LIB_RESOURCES_PATH)

from connect import logger, strings, kodi_rpc

logger.debug(u'RESOURCES_PATHs: {}, {}'.format(RESOURCES_PATH, LIB_RESOURCES_PATH))
logger.debug(u'__file__: {}'.format(__file__))

def main():
    logger.debug(u'argv: {}'.format(sys.argv[2][1:]))
    logger.debug(u'args: {}'.format(str(__args__)))

    entities = __args__.get('entities', [''])[0].split('x')
    total_items = len(entities)

    logger.debug(u'entities: {}'.format(str(entities)))

    if not entities:
        xbmcplugin.addDirectoryItem(__handle__, '', xbmcgui.ListItem(strings.NO_ITEMS_FOUND), isFolder=False)

    for entity in entities:
        entity_type = entity[:1]
        entity_id = entity[1:]

        if not entity_id:
            continue

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
            item.setInfo('video', {"plot": plot})
            if fanart:
                item.setArt({"fanart": fanart})
            if thumbnail:
                item.setArt({"thumbnail": thumbnail, "poster": thumbnail})

            xbmcplugin.addDirectoryItem(__handle__, url, item, totalItems=total_items)
        elif entity_type == 't':
            details = kodi_rpc.get_tvshow_details(entity_id)
            logger.debug(details)

            label = details.get('label', 'N/A')
            plot = details.get('plot', 'N/A')

            item = xbmcgui.ListItem(label)
            item.setInfo('video', {"plot": plot})

            xbmcplugin.addDirectoryItem(__handle__, '', item, totalItems=total_items)

    xbmcplugin.endOfDirectory(__handle__)

main()
