import os

class Addon(object):
    def __init__(self, id):
        print('Creating Addon')
        self.id = id

    def getAddonInfo(self, prop):
        if prop == 'path':
          return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
        else:
          raise Exception('Unknown property')

    def getSetting(self, id):
        if id == 'username':
            return os.environ.get('USERNAME', '')
        elif id == 'secret':
            return os.environ.get('SECRET', '')
        else:
            raise Exception('Unknown setting id')
