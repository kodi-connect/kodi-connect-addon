import kodi_rpc
from filtering import get_best_match
from utils import _get, _pick

def play_movie(movie):
    print('Playing movie:')
    print(movie['title'])
    kodi_rpc.play_movieid(movie['movieid'])

def play_tvshow(tvshow, season, episode):
    print('Playing tv show:')
    print(tvshow['title'])

    if season and episode:
        episode_id = kodi_rpc.get_episodeid(tvshow['tvshowid'], season, episode)
    else:
        episode_id = kodi_rpc.get_next_unwatched_episode_of_tvshow(tvshow['tvshowid'])

    print('Episode id: {}'.format(episode_id))
    if episode_id:
        kodi_rpc.play_episodeid(episode_id)

def get_next_episode_id(tvshow_id, season, episode):
    next_episode_id = kodi_rpc.get_episodeid(tvshow_id, season, episode + 1)
    if not next_episode_id:
        next_episode_id = kodi_rpc.get_episodeid(tvshow_id, season + 1, 1)

    return next_episode_id

def get_previous_episode_id(tvshow_id, season, episode):
    previous_episode_id = None
    if episode > 1:
        previous_episode_id = kodi_rpc.get_episodeid(tvshow_id, season, episode - 1)
    elif season > 1:
        previous_episode_id = kodi_rpc.get_last_episodeid(tvshow_id, season - 1)

    return previous_episode_id

def get_current_item():
    player_id = kodi_rpc.get_active_playerid()
    if not player_id:
        return None
    item = kodi_rpc.get_current_item(player_id)
    print(item)
    item_type = _get(item, 'type')

    if item_type == 'movie':
        return {
            'type': item_type,
            'movieid': item['id'],
        }
    elif item_type == 'episode':
        return {
            'type': item_type,
            'episodeid': item['id'],
            'tvshowid': item['tvshowid'],
            'season': item['season'],
            'episode': item['episode'],
        }

    return None

class KodiInterface(object):
    def __init__(self, library_cache):
        self.library_cache = library_cache
        self.current_item = None

    def _get_video_library(self):
        movies, tvshows = self.library_cache.get_library()

        return movies, tvshows

    def invalidate_cache(self):
        self.library_cache.invalidate()

    def update_cache(self):
        if self.library_cache.is_dirty():
            movies = kodi_rpc.get_movies()
            tvshows = kodi_rpc.get_tv_shows()
            self.library_cache.set_library(movies, tvshows)

    def update_current_item(self):
        current_item = get_current_item()
        if current_item:
            self.current_item = current_item

    def find_and_play(self, video_filter):
        movies, tvshows = self._get_video_library()

        if 'mediaType' in video_filter and video_filter['mediaType'] != 'movie':
            movie, movie_score = None, 0
        else:
            movie, movie_score = get_best_match(video_filter, movies)
        print('Movie:', movie, movie_score)

        if 'mediaType' in video_filter and video_filter['mediaType'] != 'tv show':
            tvshow, tvshow_score = None, 0
        else:
            tvshow, tvshow_score = get_best_match(video_filter, tvshows)
        print('TvShow:', tvshow, tvshow_score)

        if movie and movie_score >= tvshow_score:
            play_movie(movie)
        elif tvshow:
            season = video_filter.get('season')
            if season:
                season = int(season)
            episode = video_filter.get('episode')
            if episode:
                episode = int(episode)
            play_tvshow(tvshow, season, episode)
        else:
            return False

        return True

    def next_item(self):
        print('NEXT ITEM:', self.current_item)
        if not self.current_item:
            return False

        if 'tvshowid' in self.current_item:
            tvshow_id, season, episode = _pick(self.current_item, 'tvshowid', 'season', 'episode')

            if tvshow_id and season and episode:
                next_episode_id = get_next_episode_id(tvshow_id, season, episode)
                if next_episode_id:
                    kodi_rpc.play_episodeid(next_episode_id)
                    return True

        return False

    def previous_item(self):
        if not self.current_item:
            return False

        if 'tvshowid' in self.current_item:
            tvshow_id, season, episode = _pick(self.current_item, 'tvshowid', 'season', 'episode')

            if tvshow_id and season and episode:
                previous_episode_id = get_previous_episode_id(tvshow_id, season, episode)
                if previous_episode_id:
                    kodi_rpc.play_episodeid(previous_episode_id)
                    return True

        return False

    def start_over(self):
        current_playing_item = get_current_item()
        if current_playing_item:
            player_id = kodi_rpc.get_active_playerid()
            if player_id:
                kodi_rpc.seek_to_percentage(player_id, 0)
                return True

        return False

    def pause(self):
        playerid = kodi_rpc.get_active_playerid()
        is_playing = kodi_rpc.is_player_playing(playerid)

        if is_playing:
            kodi_rpc.play_pause_player(playerid)

        return True

    def resume(self):
        playerid = kodi_rpc.get_active_playerid()
        is_playing = kodi_rpc.is_player_playing(playerid)

        # TODO - handle this, as user is expecting that something plays
        if not is_playing:
            kodi_rpc.play_pause_player(playerid)

        return True

    def stop(self):
        playerid = kodi_rpc.get_active_playerid()
        kodi_rpc.stop_player(playerid)

        return True
