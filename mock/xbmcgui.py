# pylint: disable=print-statement

NOTIFICATION_INFO = 'NOTIFICATION_INFO'
NOTIFICATION_WARNING = 'NOTIFICATION_WARNING'
NOTIFICATION_ERROR = 'NOTIFICATION_ERROR'

class Dialog(object):
    def notification(self, heading, message, icon=NOTIFICATION_INFO, time=5000, sound=True):
        print('[GUI NOTIFICATION] |{}| |{}|'.format(heading, message))

class ListItem(object):
    def __init__(self, name):
        print('ListItem: {}'.format(name))

    def setProperty(self, name, value):
        print('setProperty {}={}'.format(name, value))

    def setArt(self, art):
        print('setArt: {}'.format(str(art)))

    def setInfo(self, type, infoLabels):
        print('setInfo: {} - {}'.format(type, str(infoLabels)))
