# pylint: disable=print-statement

import os
import time
import json
import urllib
from tornado.httpclient import HTTPClient

KODI_HOST = os.environ['KODI_HOST']

http = HTTPClient()

def _kodi_rpc(obj):
    return json.loads(executeJSONRPC(json.dumps(obj)))

def kodi_rpc(request):
    print('[XBMC] Calling kodi rpc')
    query = urllib.urlencode({ 'request': request })

    resp = http.fetch('{}/jsonrpc?{}'.format(KODI_HOST, query), auth_username='kodi', auth_password='password')
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
                self.speed = 1
            else:
                print('[XBMC] Pausing player')
                self.speed = 0
        else:
            print('[XBMC] No source to play')

    def _stop(self):
        self.current_item = None
        self.speed = 0
        print('[XBMC] Stopping player')

    def _get_current_item(self):
        return self.current_item

    def onPlayBackStarted(self):
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

def executeJSONRPC(request_str):
    request = json.loads(request_str)
    print('[XBMC] executeJSONRPC: {}'.format(str(request)))

    if request['method'].find('Player') != 0:
        return kodi_rpc(request_str)

    if request['method'] == 'Player.Open':
        print('[XBMC] Player.Open: {}'.format(str(request)))
        # TODO - return proper response as if started playback
        kodi_player._play(request['params'])
        return json.dumps({})
    elif request['method'] == 'Player.GetActivePlayers':
        return json.dumps({ 'result': [{ 'type': 'video', 'playerid': 1 }]})
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
    else:
        return None

def executebuiltin(str):
    print('[XBMC] executebuiltin: {}'.format(str))

def translatePath(path):
    return path

LOGDEBUG = 'LOGDEBUG'

def log(message, level=LOGDEBUG):
    print("[{}]: {}".format(level, message))
