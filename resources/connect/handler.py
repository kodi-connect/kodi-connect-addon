import xbmc

def not_found_wrap(ret):
    if ret:
        return { 'status': 'OK' }
    else:
        return { 'status': 'error', 'error': 'not_found' }

class Handler(object):
    def __init__(self, kodi):
        self.kodi = kodi

    def search_and_play_handler(self, video_filter):
        xbmc.log('search_and_play_handler: {}'.format(str(video_filter)), level=xbmc.LOGNOTICE)

        return not_found_wrap(self.kodi.find_and_play(video_filter))

    def next_handler(self):
        xbmc.log('next_handler: {}', level=xbmc.LOGNOTICE)
        return not_found_wrap(self.kodi.next_item())

    def previous_handler(self):
        xbmc.log('previous_handler: {}', level=xbmc.LOGNOTICE)
        return not_found_wrap(self.kodi.previous_item())

    def start_over_handler(self):
        xbmc.log('start_over_handler: {}', level=xbmc.LOGNOTICE)
        self.kodi.start_over()
        return { 'statuts': 'OK' }

    def pause_handler(self):
        xbmc.log('pause_handler: {}', level=xbmc.LOGNOTICE)
        self.kodi.pause()
        return { 'status': 'OK' }

    def resume_handler(self):
        xbmc.log('resume_handler: {}', level=xbmc.LOGNOTICE)
        self.kodi.resume()
        return { 'status': 'OK' }

    def stop_handler(self):
        xbmc.log('stop_handler: {}', level=xbmc.LOGNOTICE)
        self.kodi.stop()
        return { 'status': 'OK' }

    def handler(self, data):
        xbmc.log('handler data: {}'.format(str(data)), level=xbmc.LOGNOTICE)
        responseData = { 'status': 'Not found' }
        if data['type'] == 'command':
            if data['commandType'] == 'searchAndPlay':
                responseData = self.search_and_play_handler(data['filter'])
            elif data['commandType'] == 'next':
                responseData = self.next_handler()
            elif data['commandType'] == 'previous':
                responseData = self.previous_handler()
            elif data['commandType'] == 'startOver':
                responseData = self.start_over_handler()
            elif data['commandType'] == 'pause':
                responseData = self.pause_handler()
            elif data['commandType'] == 'resume':
                responseData = self.resume_handler()
            elif data['commandType'] == 'stop':
                responseData = self.stop_handler()

        xbmc.log('handler responseData: {}'.format(str(responseData)), level=xbmc.LOGNOTICE)

        return responseData
