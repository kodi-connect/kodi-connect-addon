import xbmc
from log import logger

def not_found_wrap(ret):
    if ret:
        return { 'status': 'OK' }
    else:
        return { 'status': 'error', 'error': 'not_found' }

class Handler(object):
    def __init__(self, kodi):
        self.kodi = kodi

    def search_and_play_handler(self, video_filter):
        logger.notice('search_and_play_handler: {}'.format(str(video_filter)))

        return not_found_wrap(self.kodi.find_and_play(video_filter))

    def next_handler(self):
        logger.notice('next_handler')
        return not_found_wrap(self.kodi.next_item())

    def previous_handler(self):
        logger.notice('previous_handler')
        return not_found_wrap(self.kodi.previous_item())

    def start_over_handler(self):
        logger.notice('start_over_handler')
        self.kodi.start_over()
        return { 'statuts': 'OK' }

    def pause_handler(self):
        logger.notice('pause_handler')
        self.kodi.pause()
        return { 'status': 'OK' }

    def resume_handler(self):
        logger.notice('resume_handler')
        self.kodi.resume()
        return { 'status': 'OK' }

    def stop_handler(self):
        logger.notice('stop_handler')
        self.kodi.stop()
        return { 'status': 'OK' }

    def handler(self, data):
        logger.notice('handler data: {}'.format(str(data)))
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

        logger.notice('handler responseData: {}'.format(str(responseData)))

        return responseData
