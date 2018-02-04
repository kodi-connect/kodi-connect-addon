import time
import urlparse

import xbmc

import kodi_rpc
import filtering
from utils import notif, _get, _pick
import strings
from log import logger

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

def play_movie(movie):
    logger.debug('Playing movie: {}'.format(movie['title']))
    kodi_rpc.play_movieid(movie['movieid'])

def play_tvshow(tvshow, season, episode):
    logger.debug('Playing tv show: {}, season: {}, episode: {}'.format(tvshow['title'], season, episode))

    if season and episode:
        episode_id = kodi_rpc.get_episodeid(tvshow['tvshowid'], int(season), int(episode))
    else:
        episode_id = kodi_rpc.get_next_unwatched_episode_of_tvshow(tvshow['tvshowid'])

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
    ids = []

    for entity in entities:
        if 'movieid' in entity: ids.append(('movieid', entity['movieid']))
        elif 'tvshowid' in entity: ids.append(('tvshowid', entity['tvshowid']))

    qs = '&'.join(['{}={}'.format(key, id) for key, id in ids])

    return 'plugin://plugin.video.kodiconnect?' + qs

def get_display_entities(entities):
    display_entities = []

    for entity in entities:
        if 'movieid' in entity: display_entities.append('m{}'.format(entity['movieid']))
        elif 'tvshowid' in entity: display_entities.append('t{}'.format(entity['tvshowid']))

    return 'x'.join(display_entities)

class KodiInterface(object):
    def __init__(self, library_cache):
        self.library_cache = library_cache
        self.library_index = None
        self.current_item = None

    def _get_video_library(self):
        movies, tvshows = self.library_cache.get_library()

        return movies, tvshows

    def invalidate_cache(self):
        self.library_cache.invalidate()

    def update_cache(self):
        if self.library_cache.is_dirty():
            logger.debug('Updating library cache')
            movies = kodi_rpc.get_movies()
            tvshows = kodi_rpc.get_tv_shows()
            logger.debug('Found {} movies and {} tvshows'.format(len(movies), len(tvshows)))
            self.library_cache.set_library(movies, tvshows)

    def update_current_item(self):
        current_item = get_current_item()
        if current_item:
            logger.debug('current_item: {}'.format(current_item))
            self.current_item = current_item

    def fuzzy_filter(self, video_filter):
        start = time.time()

        movies, tvshows = self._get_video_library()

        entities = []
        if 'mediaType' in video_filter and video_filter['mediaType'] and video_filter['mediaType'] != 'movie':
            pass
        else:
            entities = entities + movies

        if 'mediaType' in video_filter and video_filter['mediaType'] and video_filter['mediaType'] != 'tv show':
            pass
        else:
            entities = entities + tvshows

        filtered_entities = filtering.filter_entities(video_filter, entities)

        logger.debug('Fuzzy filter took {} ms'.format(int((time.time() - start) * 1000)))

        return filtered_entities

    def fuzzy_find_and_play(self, video_filter):
        filtered_entities = self.fuzzy_filter(video_filter)

        entity = filtering.get_best_match(filtered_entities)
        logger.debug('Found Entity {}'.format(str(entity)))

        if not entity:
            notif.show(strings.NOTHING_FOUND)
            return False

        if 'movieid' in entity:
            play_movie(entity)
        elif 'tvshowid' in entity:
            season, episode = _pick(video_filter, 'season', 'episode')
            play_tvshow(entity, season, episode)
        else:
            return False

        return True

    def find_and_play(self, video_filter):
        return self.fuzzy_find_and_play(video_filter)

    def find_and_display(self, video_filter):
        filtered_entities = self.fuzzy_filter(video_filter)

        if not filtered_entities:
            notif.show(strings.NOTHING_FOUND)
            return False

        best_matches = filtering.get_best_matches(filtered_entities, 10)

        display_entities = get_display_entities(best_matches)

        logger.debug('display_entities: {}'.format(str(display_entities)))

        kodi_rpc.execute_addon({ "entities": display_entities })

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

        if is_playing:
            play_pause(playerid)

        return True

    def resume(self):
        playerid = kodi_rpc.get_active_playerid()
        is_playing = kodi_rpc.is_player_playing(playerid)

        # TODO - handle this, as user is expecting that something plays
        if not is_playing:
            play_pause(playerid)

        return True

    def stop(self):
        playerid = kodi_rpc.get_active_playerid()
        stop(playerid)

        return True
