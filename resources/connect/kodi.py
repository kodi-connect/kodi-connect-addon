# pylint: disable=no-self-use

import os
import time
from concurrent import futures

from tornado.concurrent import run_on_executor

from connect import kodi_rpc, filtering, strings, utils, logger
from connect.utils import notification, _get, _pick
from connect.library_index import create_library_index
from connect.fuzzy_filter import fuzzy_filter

ADDON_CHANGE_THRESHOLD = 5  # seconds

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
    logger.debug('Current item: {}'.format(str(item)))
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

def convert_time_to_milliseconds(value):
    milliseconds = 0
    milliseconds += value['hours'] * 1000 * 60 * 60
    milliseconds += value['minutes'] * 1000 * 60
    milliseconds += value['seconds'] * 1000
    milliseconds += value['milliseconds']
    return milliseconds

def get_player_time():
    player_id = kodi_rpc.get_active_playerid()
    if not player_id:
        return None

    player_time = kodi_rpc.get_player_time(player_id)
    milliseconds = convert_time_to_milliseconds(player_time)

    return milliseconds

def play_movie(movie):
    logger.debug('Playing movie: {}'.format(movie['title']))
    kodi_rpc.play_movieid(movie['movieid'])

def play_tvshow(tvshow, season, episode):
    logger.debug('Playing tv show: {}, season: {}, episode: {}'.format(tvshow['title'], season, episode))

    if season and episode:
        episode_id = kodi_rpc.get_episodeid(tvshow['tvshowid'], int(season), int(episode))
    else:
        episode_id = kodi_rpc.get_next_unwatched_episode(tvshow['tvshowid'])

    if episode_id:
        logger.debug('Playing episodeid: {}'.format(episode_id))
        play_episodeid(episode_id)

def play_episodeid(episodeid):
    kodi_rpc.play_episodeid(episodeid)

def play_pause(playerid):
    kodi_rpc.play_pause_player(playerid)

def stop(playerid):
    kodi_rpc.stop_player(playerid)

def get_display_url(entities):
    entity_ids = []

    for entity in entities:
        if 'movieid' in entity:
            entity_ids.append(('movieid', entity['movieid']))
        elif 'tvshowid' in entity:
            entity_ids.append(('tvshowid', entity['tvshowid']))

    query_string = '&'.join(['{}={}'.format(key, entity_id) for key, entity_id in entity_ids])

    return 'plugin://plugin.video.kodiconnect?' + query_string

def get_display_entities(entities):
    display_entities = []

    for entity in entities:
        if 'movieid' in entity:
            display_entities.append('m{}'.format(entity['movieid']))
        elif 'tvshowid' in entity:
            display_entities.append('t{}'.format(entity['tvshowid']))

    return 'x'.join(display_entities)

class KodiInterface(object):
    def __init__(self, library_cache):
        self.library_cache = library_cache
        self.library_index = None
        self.current_item = None
        self.disable_ngram_index = 'DISABLE_NGRAM_INDEX' in os.environ
        self.last_playback_change_at = 0
        self.executor = futures.ThreadPoolExecutor(max_workers=1)

    def __del__(self):
        self.executor.shutdown()

    def _get_video_library(self):
        movies, tvshows = self.library_cache.get_library()

        return movies, tvshows

    @run_on_executor
    def _update_library_index(self, movies, tvshows):
        logger.debug('Updating library index')
        library_index = create_library_index(movies, tvshows)
        self.library_index = library_index
        logger.debug('Updated library index')

    def _set_last_playback_change_at(self):
        self.last_playback_change_at = time.time()

    def set_disable_ngram_index(self, disable_ngram_index):
        self.disable_ngram_index = disable_ngram_index

    def invalidate_cache(self):
        self.library_cache.invalidate()

    def update_cache(self):
        if self.library_cache.is_dirty():
            logger.debug('Updating library cache')
            movies = kodi_rpc.get_movies() or []
            tvshows = kodi_rpc.get_tv_shows() or []
            logger.debug('Found {} movies and {} tvshows'.format(len(movies), len(tvshows)))
            self.library_cache.set_library(movies, tvshows)
            # self.library_index = create_library_index(movies, tvshows)
            self._update_library_index(movies, tvshows)

    def update_current_item(self):
        current_item = get_current_item()
        if current_item:
            logger.debug('current_item: {}'.format(current_item))
            self.current_item = current_item

    def find_entities(self, video_filter):
        if self.disable_ngram_index is True:
            movies, tvshows = self._get_video_library()
            return fuzzy_filter(movies, tvshows, video_filter)

        return self.library_index.find_by_filter(video_filter)

    def find_and_play(self, video_filter):
        filtered_entities = self.find_entities(video_filter)

        entity = filtering.get_best_match(filtered_entities)
        logger.debug('Found Entity {}'.format(str(entity)))

        if not entity:
            notification(strings.NOTHING_FOUND)
            return False

        if 'movieid' in entity:
            self._set_last_playback_change_at()
            play_movie(entity)
        elif 'tvshowid' in entity:
            season, episode = _pick(video_filter, 'season', 'episode')
            self._set_last_playback_change_at()
            play_tvshow(entity, season, episode)
        else:
            return False

        return True

    def find_and_display(self, video_filter):
        filtered_entities = self.find_entities(video_filter)

        if not filtered_entities:
            notification(strings.NOTHING_FOUND)
            return False

        best_matches = filtering.get_best_matches(filtered_entities, 10)

        display_entities = get_display_entities(best_matches)

        logger.debug('display_entities: {}'.format(str(display_entities)))

        kodi_rpc.execute_addon({"entities": display_entities})

        return True

    def next_item(self):
        logger.debug('Next item, current_item: {}'.format(str(self.current_item)))
        if not self.current_item:
            return False

        if 'tvshowid' in self.current_item:
            tvshow_id, season, episode = _pick(self.current_item, 'tvshowid', 'season', 'episode')

            if tvshow_id and season and episode:
                next_episode_id = get_next_episode_id(tvshow_id, season, episode)
                if next_episode_id:
                    self._set_last_playback_change_at()
                    play_episodeid(next_episode_id)
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
                    self._set_last_playback_change_at()
                    play_episodeid(previous_episode_id)
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

        self._set_last_playback_change_at()
        if is_playing:
            play_pause(playerid)

        return True

    def resume(self):
        playerid = kodi_rpc.get_active_playerid()
        is_playing = kodi_rpc.is_player_playing(playerid)

        self._set_last_playback_change_at()
        if not is_playing:
            play_pause(playerid)

        return True

    def stop(self):
        playerid = kodi_rpc.get_active_playerid()
        self._set_last_playback_change_at()
        stop(playerid)

        return True

    def rewind(self):
        kodi_rpc.small_skip_backwards()
        return True

    def fastforward(self):
        kodi_rpc.small_skip_forward()
        return True

    def seek(self, delta_position):
        playerid = kodi_rpc.get_active_playerid()
        kodi_rpc.seek_player(playerid, delta_position)
        player_time = kodi_rpc.get_player_time(playerid)
        milliseconds = convert_time_to_milliseconds(player_time)
        return milliseconds

    def set_volume(self, volume):
        kodi_rpc.set_volume(volume)
        return True

    def adjust_volume(self, volume):
        current_volume = kodi_rpc.get_volume()
        logger.debug('Current volume: {}'.format(current_volume))

        new_volume = max(min(current_volume + volume, 100), 0)
        logger.debug('Adjusting volume to: {}'.format(new_volume))

        kodi_rpc.set_volume(new_volume)
        return True

    def set_mute(self, mute):
        kodi_rpc.set_mute(mute)
        return True

    def turnon(self):
        kodi_rpc.turn_on()
        return True

    def turnoff(self):
        kodi_rpc.turn_off()
        return True

    def get_state(self):
        start = time.time()

        volume = kodi_rpc.get_volume()
        muted = kodi_rpc.get_muted()

        player_status = 'stopped'
        player_id = kodi_rpc.get_active_playerid()
        if player_id is not None:
            player_status = 'playing' if kodi_rpc.is_player_playing(player_id) else 'paused'

        state = [
            {"name": "volume", "value": volume},
            {"name": "muted", "value": muted},
            {"name": "player", "value": player_status},
        ]

        if utils.cec_available():
            state.append({"name": "power", "value": True})

        logger.debug('Fetching state took {} ms'.format(int((time.time() - start) * 1000)))

        return state

    def is_playback_addon_change(self):
        return time.time() - self.last_playback_change_at < ADDON_CHANGE_THRESHOLD
