# pylint: disable=print-statement

NOTIFICATION_INFO = 'NOTIFICATION_INFO'
NOTIFICATION_WARNING = 'NOTIFICATION_WARNING'
NOTIFICATION_ERROR = 'NOTIFICATION_ERROR'

class Dialog(object):
    def notification(self, heading, message, icon=NOTIFICATION_INFO, time=5000, sound=True):
        print(u'[GUI NOTIFICATION] |{}| |{}|'.format(heading, message))

class ListItem(object):
    def __init__(self, name):
        print(u'ListItem: {}'.format(name))

    def setProperty(self, name, value):
        print(u'setProperty {}={}'.format(name, value))

    def setArt(self, art):
        print(u'setArt: {}'.format(str(art)))

    def setInfo(self, type, infoLabels):
        print(u'setInfo: {} - {}'.format(type, str(infoLabels)))
