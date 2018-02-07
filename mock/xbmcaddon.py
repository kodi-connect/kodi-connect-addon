# pylint: disable=print-statement

import os
import re

class Addon(object):
    def __init__(self, id='plugin.video.kodiconnect'):
        print('[XBMCADDON] Creating Addon')
        self.id = id

    def getAddonInfo(self, prop):
        if prop == 'path':
          return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
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
