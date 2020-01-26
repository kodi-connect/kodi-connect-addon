from tornado.ioloop import IOLoop
from connect import utils, logger


def get_alexa_capabilities():
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
        {
            "type": "AlexaInterface",
            "interface": "Alexa.PlaybackStateReporter",
            "version": "1.0",
            "properties": {
                "supported": [{"name": "playbackState"}],
                "proactivelyReported": True,
                "retrievable": True,
            },
        },
        {
            "type": "AlexaInterface",
            "interface": "Alexa.SeekController",
            "version": "3"
        },
        {
            "type": "AlexaInterface",
            "interface": "Alexa.Speaker",
            "version": "3",
            "properties": {
                "supported": [{"name": "volume"}, {"name": "muted"}],
                "proactivelyReported": False,
                "retrievable": True,
            },
        },
    ]

    if utils.cec_available():
        capabilities.append({
            "type": "AlexaInterface",
            "interface": "Alexa.PowerController",
            "version": "3",
            "properties": {
                "supported": [{"name": "powerState"}],
                "proactivelyReported": False,
                "retrievable": True,
            },
        })

    return capabilities

class Handler(object):
    def __init__(self, kodi):
        self.kodi = kodi

    def search_and_play_handler(self, video_filter):
        logger.debug(u'search_and_play_handler: {}'.format(str(video_filter)))
        IOLoop.instance().add_callback(self.kodi.find_and_play, video_filter)

    def search_and_display_handler(self, video_filter):
        logger.debug(u'search_and_display_handler: {}'.format(str(video_filter)))
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

    def seek_handler(self, delta_position):
        logger.debug(u'seek_handler: {}'.format(delta_position))
        milliseconds = self.kodi.seek(delta_position)
        return {"status": "ok", "positionMilliseconds": milliseconds}

    def set_volume_handler(self, volume):
        logger.debug(u'set_volume_handler: {}'.format(volume))
        IOLoop.instance().add_callback(self.kodi.set_volume, volume)

    def adjust_volume_handler(self, volume):
        logger.debug(u'adjust_volume_handler: {}'.format(volume))
        IOLoop.instance().add_callback(self.kodi.adjust_volume, volume)

    def set_mute_handler(self, mute):
        logger.debug(u'set_mute_handler: {}'.format(mute))
        IOLoop.instance().add_callback(self.kodi.set_mute, mute)

    def turnon_handler(self):
        logger.debug('turnon_handler')
        IOLoop.instance().add_callback(self.kodi.turnon)

    def turnoff_handler(self):
        logger.debug('turnoff_handler')
        IOLoop.instance().add_callback(self.kodi.turnoff)

    # pylint: disable=too-many-branches
    def handler(self, data):
        logger.debug(u'handler data: {}'.format(str(data)))
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
            elif data['commandType'] == 'play' or data['commandType'] == 'resume':
                self.resume_handler()
            elif data['commandType'] == 'stop':
                self.stop_handler()
            elif data['commandType'] == 'rewind':
                self.rewind_handler()
            elif data['commandType'] == 'fastForward':
                self.fastforward_handler()
            elif data['commandType'] == 'seek':
                response_data = self.seek_handler(data.get('deltaPosition', 0))
            elif data['commandType'] == 'setVolume':
                self.set_volume_handler(data.get('volume', 0))
            elif data['commandType'] == 'adjustVolume':
                self.adjust_volume_handler(data.get('volume', 0))
            elif data['commandType'] == 'setMute':
                self.set_mute_handler(data.get('mute', False))
            elif data['commandType'] == 'turnOn' and utils.cec_available():
                self.turnon_handler()
            elif data['commandType'] == 'turnOff' and utils.cec_available():
                self.turnoff_handler()
            else:
                response_data = {'status': 'error', 'error': 'unknown_command'}
        elif data['type'] == 'capabilities' or data['type'] == 'alexa_capabilities':
            response_data = {"status": "ok", "capabilities": get_alexa_capabilities()}
        elif data['type'] == 'state':
            response_data = {"status": "ok", "state": self.kodi.get_state()}
        else:
            response_data = {'status': 'error', 'error': 'unknown_command'}

        logger.debug(u'handler response_data: {}'.format(str(response_data)))

        return response_data
