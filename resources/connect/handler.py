from tornado.ioloop import IOLoop
from connect import utils, logger

class Handler(object):
    def __init__(self, kodi):
        self.kodi = kodi

    def capabilities_handler(self):
        capabilities = [
            {
                "type": 'AlexaInterface',
                "interface": 'Alexa.RemoteVideoPlayer',
                "version": '3',
            },
            {
                "type": 'AlexaInterface',
                "interface": 'Alexa.PlaybackController',
                "version": '3',
                "supportedOperations": ['Play', 'Pause', 'Stop', 'StartOver', 'Previous', 'Next', 'Rewind', 'FastForward'],
            },
        ]

        if utils.cec_available():
            capabilities.append({
                "type": "AlexaInterface",
                "interface": "Alexa.PowerController",
                "version": "3",
                "properties": {
                    "supported": [{"name": "powerState"}],
                    "proactivelyReported": True,
                },
            })

        return capabilities

    def search_and_play_handler(self, video_filter):
        logger.debug('search_and_play_handler: {}'.format(str(video_filter)))
        IOLoop.instance().add_callback(self.kodi.find_and_play, video_filter)

    def search_and_display_handler(self, video_filter):
        logger.debug('search_and_display_handler: {}'.format(str(video_filter)))
        IOLoop.instance().add_callback(self.kodi.find_and_display, video_filter)

    def next_handler(self):
        logger.debug('next_handler')
        IOLoop.instance().add_callback(self.kodi.next_item)

    def previous_handler(self):
        logger.debug('previous_handler')
        IOLoop.instance().add_callback(self.kodi.previous_item)

    def start_over_handler(self):
        logger.debug('start_over_handler')
        IOLoop.instance().add_callback(self.kodi.start_over)

    def pause_handler(self):
        logger.debug('pause_handler')
        IOLoop.instance().add_callback(self.kodi.pause)

    def resume_handler(self):
        logger.debug('resume_handler')
        IOLoop.instance().add_callback(self.kodi.resume)

    def stop_handler(self):
        logger.debug('stop_handler')
        IOLoop.instance().add_callback(self.kodi.stop)

    def rewind_handler(self):
        logger.debug('rewind_handler')
        IOLoop.instance().add_callback(self.kodi.rewind)

    def fastforward_handler(self):
        logger.debug('fastforward_handler')
        IOLoop.instance().add_callback(self.kodi.fastforward)

    def turnon_handler(self):
        logger.debug('turnon_handler')
        IOLoop.instance().add_callback(self.kodi.turnon)

    def turnoff_handler(self):
        logger.debug('turnoff_handler')
        IOLoop.instance().add_callback(self.kodi.turnoff)

    def handler(self, data):
        logger.debug('handler data: {}'.format(str(data)))
        response_data = {'status': 'ok'}
        if data['type'] == 'command':
            if data['commandType'] == 'searchAndPlay':
                self.search_and_play_handler(data.get('filter', {}))
            elif data['commandType'] == 'searchAndDisplay':
                self.search_and_display_handler(data.get('filter', {}))
            elif data['commandType'] == 'next':
                self.next_handler()
            elif data['commandType'] == 'previous':
                self.previous_handler()
            elif data['commandType'] == 'startOver':
                self.start_over_handler()
            elif data['commandType'] == 'pause':
                self.pause_handler()
            elif data['commandType'] == 'resume':
                self.resume_handler()
            elif data['commandType'] == 'stop':
                self.stop_handler()
            elif data['commandType'] == 'rewind':
                self.rewind_handler()
            elif data['commandType'] == 'fastForward':
                self.fastforward_handler()
            elif data['commandType'] == 'turnOn' and utils.cec_available():
                self.turnon_handler()
            elif data['commandType'] == 'turnOff' and utils.cec_available():
                self.turnoff_handler()
            else:
                response_data = {'status': 'error', 'error': 'unknown_command'}
        elif data['type'] == 'capabilities':
            response_data = {"status": "ok", "capabilities": self.capabilities_handler()}
        else:
            response_data = {'status': 'error', 'error': 'unknown_command'}

        logger.debug('handler response_data: {}'.format(str(response_data)))

        return response_data
