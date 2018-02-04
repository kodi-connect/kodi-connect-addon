# pylint: disable=print-statement

_end_of_directory = False

def addDirectoryItem(handle, url, listitem, isFolder=False, totalItems=None):
    global _end_of_directory
    if _end_of_directory:
        raise Exception('Cannot call addDirectoryItem after calling endOfDirectory')

    print('[XBMC] addDirectoryItem')

def endOfDirectory(handle):
    global _end_of_directory
    print('[XBMC] endOfDirectory')
    _end_of_directory = True

def setContent(handle, content):
    print('[XBMC] setContent: {}'.format(content))
