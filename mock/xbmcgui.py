NOTIFICATION_INFO = 'NOTIFICATION_INFO'
NOTIFICATION_WARNING = 'NOTIFICATION_WARNING'
NOTIFICATION_ERROR = 'NOTIFICATION_ERROR'

class Dialog(object):
    def notification(self, heading, message, icon=NOTIFICATION_INFO, time=5000, sound=True):
        print('[GUI NOTIFICATION] |{}| |{}|'.format(heading, message))
