import os
import time
import json
import urllib
from tornado.httpclient import HTTPClient

KODI_HOST = os.environ['KODI_HOST']

http = HTTPClient()

def _kodi_rpc(obj):
    return json.loads(executeJSONRPC(json.dumps(obj)))

def load_json_file(filepath):
    with open(filepath, 'r') as json_file:
      data = json.load(json_file)
      return data

def kodi_rpc(request):
    print('Calling kodi rpc')
    query = urllib.urlencode({ 'request': request })

    resp = http.fetch('{}/jsonrpc?{}'.format(KODI_HOST, query), auth_username='kodi', auth_password='password')
    return resp.body

def get_tvshow_by_episodeid(episodeid):
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

def get_item_by_params(params):
    item = { 'type': 'unknown' }
    if 'movieid' in params['item']:
        item = { 'type': 'movie', 'id': params['item']['movieid'] }
    elif 'episodeid' in params['item']:
        item = get_tvshow_by_episodeid(params['item']['episodeid'])

    return item

kodi_player = None

class Player(object):
    def __init__(self):
        self.current_item = None
        self.speed = 0
        global kodi_player
        kodi_player = self

    def _play(self, params):
        self.current_item = get_item_by_params(params)
        print('current_item:', self.current_item)
        self.speed = 1
        self.onPlayBackStarted()

    def _play_pause(self):
        if self.current_item:
            if self.speed == 0:
                print('Resuming player')
                self.speed = 1
            else:
                print('Pausing player')
                self.speed = 0
        else:
            print('No source to play')

    def _stop(self):
        self.current_item = None
        self.speed = 0
        print('Stopping player')

    def _get_current_item(self):
        return self.current_item

    def onPlayBackStarted(self):
        pass

class Monitor(object):
    def __init__(self):
        print('Creating Monitor')

    def abortRequested(self):
        return False

    def waitForAbort(self, seconds):
        time.sleep(seconds)
        return False

def executeJSONRPC(request_str):
    request = json.loads(request_str)
    print('executeJSONRPC', request)

    if request['method'].find('Player') != 0:
        return kodi_rpc(request_str)

    if request['method'] == 'VideoLibrary.GetMovies':
        # return {"id":1,"jsonrpc":"2.0","result":{"limits":{"end":0,"start":0,"total":0}}}
        return json.dumps(movies)
    elif request['method'] == 'VideoLibrary.GetTVShows':
        # return {"id":1,"jsonrpc":"2.0","result":{"limits":{"end":0,"start":0,"total":0}}}
        return json.dumps(tv_shows)
    elif request['method'] == 'VideoLibrary.GetEpisodes':
        return json.dumps({ 'result': { 'episodes': [{ 'episodeid': 10 }] }})
    elif request['method'] == 'Player.Open':
        print('Player.Open:')
        print(request)
        # TODO - return proper response as if started playback
        kodi_player._play(request['params'])
        return json.dumps({})
    elif request['method'] == 'Player.GetActivePlayers':
        return json.dumps({ 'result': [{ 'type': 'video', 'playerid': 1 }]})
    elif request['method'] == 'Player.GetProperties':
        properties = request['params']['properties']
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

        # Nothing playing
        return json.dumps({
            "jsonrpc": "2.0",
            "id": "VideoGetItem",
            "result": {
                "item": {
                    "title": "",
                    "type": "unknown",
                    "label": ""
                }
            }
        })

        # Movie
        return json.dumps({
            "jsonrpc": "2.0",
            "id": "VideoGetItem",
            "result": {
                "item": {
                    "tvshowid": -1,
                    "episode": -1,
                    "title": "Baywatch",
                    "season": -1,
                    "label": "Baywatch",
                    "type": "movie",
                    "id": 85
                }
            }
        })

        # Episode
        return json.dumps({
            "jsonrpc": "2.0",
            "id": "VideoGetItem",
            "result": {
                "item": {
                    "tvshowid": 16,
                    "episode": 11,
                    "title": "New Dimensions",
                    "season": 1,
                    "label": "New Dimensions",
                    "type": "episode",
                    "id": 308
                }
            }
        })
    else:
        return None

def translatePath(path):
    return path

def log(message, level):
    print("[{}]: {}".format(level, message))

# def Player():
#     return kodi_player

LOGNOTICE = 'LOGNOTICE'
