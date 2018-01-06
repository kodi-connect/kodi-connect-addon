import time
import json

def load_json_file(filepath):
    with open(filepath, 'r') as json_file:
      data = json.load(json_file)
      return data

movies = load_json_file('./mock/movies.json')
tv_shows = load_json_file('./mock/tvshows.json')

class KodiPlayer(object):
    def __init__(self):
        self.id = None
        self.speed = 0

    def _play_id(self, id):
        print('Playing id {}'.format(id))
        self.id = id
        self.speed = 1

    def _play_pause(self):
        if self.id:
            if self.speed == 0:
                print('Resuming player')
                self.speed = 1
            else:
                print('Pausing player')
                self.speed = 0
        else:
            print('No source to play')

    def _stop(self):
        self.id = None
        self.speed = 0
        print('Stopping player')

kodi_player = KodiPlayer()

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
        print(request['params'])
        # TODO - return proper response as if started playback
        kodi_player._play_id(10)
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
    else:
        return None

def translatePath(path):
    return path

def log(message, level):
    print("[{}]: {}".format(level, message))

def Player():
    return kodi_player

LOGNOTICE = 'LOGNOTICE'
