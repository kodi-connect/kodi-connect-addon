# pylint: disable=print-statement

import os
import time
import json
import urllib
from tornado.httpclient import HTTPClient

KODI_HOST = os.environ['KODI_HOST']
LOG_FILE = os.environ.get('LOG_FILE', '/tmp/kodi.log')

def write_log(token, message):
    with open(LOG_FILE, 'a') as f:
        f.write('[{}] {}\n'.format(token, message))

def _kodi_rpc(obj):
    return json.loads(executeJSONRPC(json.dumps(obj)))

def kodi_rpc(request):
    print('[XBMC] Calling kodi rpc')
    query = urllib.urlencode({ 'request': request })

    http_client = HTTPClient()
    resp = http_client.fetch('{}/jsonrpc?{}'.format(KODI_HOST, query), auth_username='kodi', auth_password='password', connect_timeout=60.0)
    http_client.close()
    return resp.body

def _get_tvshow_by_episodeid(episodeid):
    res = _kodi_rpc({
        "jsonrpc": "2.0",
        "method": 'VideoLibrary.GetEpisodeDetails',
        "id": 1,
        'params': {
            'episodeid': episodeid,
            'properties': ["title", "season", "episode", "tvshowid"],
        }
    })
    if 'result' in res and 'episodedetails' in res['result']:
        episodedetails = res['result']['episodedetails']
        return {
            'type': 'episode',
            'id': episodeid,
            'tvshowid': episodedetails['tvshowid'],
            'season': episodedetails['season'],
            'episode': episodedetails['episode'],
        }
    return None

def _get_item_by_params(params):
    item = { 'type': 'unknown' }
    if 'movieid' in params['item']:
        item = { 'type': 'movie', 'id': params['item']['movieid'] }
    elif 'episodeid' in params['item']:
        item = _get_tvshow_by_episodeid(params['item']['episodeid'])

    return item

class MockApplication(object):
    def __init__(self):
        self.muted = False
        self.volume = 100

    def get_properties(self):
        return { 'result': { 'volume': self.volume, 'muted': self.muted } }

    def set_volume(self, volume):
        self.volume = volume

    def set_muted(self, muted):
        self.muted = muted

mock_application = MockApplication()

kodi_player = None

class Player(object):
    def __init__(self, *args, **kwargs):
        self.current_item = None
        self.speed = 0
        global kodi_player
        kodi_player = self

    def _play(self, params):
        self.current_item = _get_item_by_params(params)
        print('[XBMC] current_item: {}'.format(str(self.current_item)))
        self.speed = 1
        self.onPlayBackStarted()

    def _play_pause(self):
        if self.current_item:
            if self.speed == 0:
                print('[XBMC] Resuming player')
                write_log('Player', 'RESUME')
                self.speed = 1
                self.onPlayBackStarted()
            else:
                print('[XBMC] Pausing player')
                write_log('Player', 'PAUSE')
                self.speed = 0
                self.onPlayBackPaused()

        else:
            print('[XBMC] No source to play')

    def _stop(self):
        print('[XBMC] Stopping player')
        write_log('Player', 'STOP')
        self.current_item = None
        self.speed = 0
        self.onPlayBackStopped()

    def _get_current_item(self):
        return self.current_item

    def _is_active(self):
        return self.current_item is not None

    def onPlayBackStarted(self):
        pass

    def onPlayBackPaused(self):
        pass

    def onPlayBackStopped(self):
        pass

    def onPlayBackResumed(self):
        pass

abort_file_path = '/tmp/abort'

class Monitor(object):
    def __init__(self):
        print('[XBMC] Creating Monitor')

    def abortRequested(self):
        should_abort = os.path.isfile(abort_file_path)
        if should_abort:
            os.remove(abort_file_path)
        return should_abort

    def waitForAbort(self, seconds):
        if self.abortRequested():
            return True
        time.sleep(seconds)
        return self.abortRequested()

def _executeJSONRPC(request_str):
    request = json.loads(request_str)
    print('[XBMC] executeJSONRPC: {}'.format(str(request)))

    if request['method'].startswith('Player.'):
        if request['method'] == 'Player.Open':
            print('[XBMC] Player.Open: {}'.format(str(request)))
            # TODO - return proper response as if started playback
            kodi_player._play(request['params'])
            return json.dumps({})
        elif request['method'] == 'Player.GetActivePlayers':
            players = []
            if kodi_player._is_active():
                players = [{ 'type': 'video', 'playerid': 1 }]
            return json.dumps({'result': players})
        elif request['method'] == 'Player.GetProperties':
            return json.dumps({ 'result': { 'speed': kodi_player.speed }})
        elif request['method'] == 'Player.PlayPause':
            kodi_player._play_pause()
            return json.dumps({ 'result': 'OK' })
        elif request['method'] == 'Player.Stop':
            kodi_player._stop()
            return json.dumps({ 'result': 'OK' })
        elif request['method'] == 'Player.GetItem':
            return json.dumps({
                "jsonrpc": "2.0",
                "id": "VideoGetItem",
                "result": { 'item': kodi_player._get_current_item() },
            })
    elif request['method'].startswith('Application.'):
        if request['method'] == 'Application.GetProperties':
            return json.dumps(mock_application.get_properties())
        elif request['method'] == 'Application.SetMute':
            mock_application.set_muted(request['params']['mute'])
            return json.dumps({ 'result': 'OK' })
        elif request['method'] == 'Application.SetVolume':
            mock_application.set_volume(request['params']['volume'])
            return json.dumps({ 'result': 'OK' })
    elif request['method'].startswith('VideoLibrary.'):
        return kodi_rpc(request_str)
    elif request['method'].startswith('Addons.'):
        print('Addons RPC')
        print(request_str)
        return json.dumps({ 'result': 'OK' })

    print('Invalid request')
    print(request_str)
    raise Exception('Invalid request')

def executeJSONRPC(request_str):
    write_log('JSONRPC_OUT', request_str)
    result = _executeJSONRPC(request_str)
    write_log('JSONRPC_IN', result)
    return result

def executebuiltin(str):
    print('[XBMC] executebuiltin: {}'.format(str))

def translatePath(path):
    return path

LOGDEBUG = 'LOGDEBUG'
LOGNOTICE = 'LOGNOTICE'

def log(message, level=LOGDEBUG):
    print("[{}]: {}".format(level, message))
