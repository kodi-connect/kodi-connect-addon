# pylint: disable=print-statement

import os
import re
from xml.dom import minidom

class Addon(object):
    def __init__(self, id='plugin.video.kodiconnect'):
        print('[XBMCADDON] Creating Addon')
        self.id = id

    def getAddonInfo(self, prop):
        if prop == 'path':
          return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
        elif prop == 'version':
          with minidom.parse(os.path.join(self.getAddonInfo('path'), 'addon.xml')) as xmldoc:
            return xmldoc.getElementsByTagName('addon')[0].attributes['version'].value
        else:
          raise Exception('Unknown property')

    def getSetting(self, id):
        if id == 'email':
            return os.environ.get('EMAIL', '')
        elif id == 'secret':
            return os.environ.get('SECRET', '')
        else:
            raise Exception('Unknown setting id')

    def getLocalizedString(self, string_id):
        with open('./resources/language/English/strings.po', 'r') as f:
            content = f.read()

            match = re.search('msgctxt "#{}"\nmsgid "(.*)"\n'.format(string_id), content)

            if not match:
                raise Exception('Didn\'t find string id')
            return match.group(1)
