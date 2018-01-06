import json
import xbmc
from fuzzywuzzy import fuzz, process

def kodi_rpc(obj):
    return json.loads(xbmc.executeJSONRPC(json.dumps(obj)))

def _get(dictionary, *keys):
    return reduce(lambda d, key: d.get(key) if d else None, keys, dictionary)

def get_active_playerid():
    res = kodi_rpc({ "jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1 })
    players = _get(res, 'result')
    if not players:
        return None
    players = [player for player in players if _get(player, 'type') == 'video']
    if not players:
        return None
    return players[0]['playerid']

def is_player_playing(playerid):
    if not playerid:
        return None

    res = kodi_rpc({
        "jsonrpc": "2.0",
        "method": "Player.GetProperties",
        "id": 1,
        'params': {
            'playerid': playerid,
            'properties': ['speed']
        }
    })

    speed = _get(res, 'result', 'speed')
    if speed is None:
        return None

    return speed != 0

def play_pause_player(playerid):
    if not playerid:
        return

    res = kodi_rpc({
        "jsonrpc": "2.0",
        "method": "Player.PlayPause",
        "id": 1,
        'params': {
            'playerid': playerid
        }
    })

def stop_player(playerid):
    if not playerid:
        return

    res = kodi_rpc({
        "jsonrpc": "2.0",
        "method": "Player.Stop",
        "id": 1,
        'params': {
            'playerid': playerid
        }
    })

def get_movies():
    res = kodi_rpc({ "jsonrpc": "2.0", "method": 'VideoLibrary.GetMovies', "id": 1 })
    return _get(res, 'result', 'movies')

def get_tv_shows():
    res = kodi_rpc({ "jsonrpc": "2.0", "method": 'VideoLibrary.GetTVShows', "id": 1 })
    return _get(res, 'result', 'tvshows')

def get_best_match(requested_titles, entities):
    if not entities:
        return None, 0

    labels = [entity['label'] for entity in entities]
    best_matches = [process.extractOne(requested_title, labels, scorer=fuzz.ratio) for requested_title in requested_titles]
    best_matches = [best_match for best_match in best_matches if best_match[1] > 75]
    print(best_matches)
    if not best_matches:
        return None, 0

    best_match = max(best_matches, key=lambda bm: bm[1])
    print(best_match)

    return ((entity, best_match[1]) for entity in entities if entity['label'] == best_match[0]).next()

def get_next_unwatched_episode_of_tv_show(tv_show_id):
    FILTER_UNWATCHED = { "operator": "lessthan", "field": "playcount", "value": "1" };
    SORT_EPISODE = { "method": "episode", "order": "ascending" };

    res = kodi_rpc({
        "jsonrpc": "2.0",
        "method": 'VideoLibrary.GetEpisodes',
        "id": 1,
        'params': {
            'tvshowid': tv_show_id,
            'filter': FILTER_UNWATCHED,
            'sort': SORT_EPISODE,
            'properties': ['playcount'],
            'limits': { 'start': 0, 'end': 1 },
        }
    })

    episodes = _get(res, 'result', 'episodes')

    if not episodes:
        return None

    return episodes[0]['episodeid']

def play_movie_handler(movie):
    print('Playing movie:')
    print(movie)
    play_movie(movie['movieid'])

def play_tv_show_handler(tv_show):
    print('Playing tv show:')
    print(tv_show)

    episode_id = get_next_unwatched_episode_of_tv_show(tv_show['tvshowid'])
    print('Episode id: {}'.format(episode_id))
    if episode_id:
        play_episode(episode_id)

def play_movie(movie_id):
  res = kodi_rpc({
    "jsonrpc": "2.0",
    "method": 'Player.Open',
    "id": 1,
    'params': {
      'item': { 'movieid': movie_id },
      'options': { 'resume': True },
    },
  })

  print(res)

def play_episode(episode_id):
  res = kodi_rpc({
    "jsonrpc": "2.0",
    "method": 'Player.Open',
    "id": 1,
    'params': {
      'item': { 'episodeid': episode_id },
      'options': { 'resume': True },
    },
  })

  print(res)
