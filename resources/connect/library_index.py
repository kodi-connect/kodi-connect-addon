import itertools
import time
import re

from ngram import NGram

from connect import logger
from connect.utils import strip_accents

def build_title_index(movies, tvshows):
    start = time.time()

    entities = list(itertools.chain.from_iterable([movies, tvshows]))
    values = [strip_accents(entity['title']) for entity in entities]
    # values = [entity['title'] for entity in entities]

    mapped_entities = {}
    for entity in entities:
        value = strip_accents(entity['title'])
        # value = entity['title']
        if value not in mapped_entities:
            mapped_entities[value] = []

        mapped_entities[value].append(entity)

    logger.debug('Iterating title took {} ms'.format(int((time.time() - start) * 1000)))

    start = time.time()
    index = NGram(items=values, key=lambda x: x.lower())
    logger.debug('Building title index took {} ms'.format(int((time.time() - start) * 1000)))

    return index, mapped_entities

def parse_collection(collection):
    match = re.search('(.*) Collection', collection)
    return match.group(1) if match else collection

def build_collection_index(movies, tvshows):
    start = time.time()

    entities = list(itertools.chain.from_iterable([movies, tvshows]))
    values = list(set([
        parse_collection(strip_accents(entity['set']))
        for entity in entities if 'set' in entity and len(entity['set']) > 0
    ]))

    mapped_entities = {}
    for entity in entities:
        if 'set' in entity and entity['set']:
            value = parse_collection(strip_accents(entity['set']))
            if value not in mapped_entities:
                mapped_entities[value] = []

            mapped_entities[value].append(entity)

    logger.debug('Iterating collection took {} ms'.format(int((time.time() - start) * 1000)))

    start = time.time()
    index = NGram(items=values, key=lambda x: x.lower())
    logger.debug('Building collection index took {} ms'.format(int((time.time() - start) * 1000)))

    return index, mapped_entities

def build_genre_index(movies, tvshows):
    start = time.time()

    entities = list(itertools.chain.from_iterable([movies, tvshows]))
    values = list(set(filter(
        strip_accents,
        itertools.chain.from_iterable([entity['genre'] for entity in entities])
    )))

    mapped_entities = {}
    for entity in entities:
        for genre in [strip_accents(genre) for genre in entity['genre']]:
            if genre not in mapped_entities:
                mapped_entities[genre] = []

            mapped_entities[genre].append(entity)

    logger.debug('Iterating genre took {} ms'.format(int((time.time() - start) * 1000)))

    start = time.time()
    index = NGram(items=values, key=lambda x: x.lower())
    logger.debug('Building genre index took {} ms'.format(int((time.time() - start) * 1000)))

    return index, mapped_entities

def build_cast_index(movies, tvshows, key):
    start = time.time()

    entities = list(itertools.chain.from_iterable([movies, tvshows]))
    values = [[strip_accents(cast[key]) for cast in entity['cast']] for entity in entities]
    values = list(set(itertools.chain.from_iterable(values)))

    mapped_entities = {}
    for entity in entities:
        for cast in entity['cast']:
            value = strip_accents(cast[key])
            if value not in mapped_entities:
                mapped_entities[value] = []

            mapped_entities[value].append(entity)

    logger.debug('Iterating {} took {} ms'.format(key, int((time.time() - start) * 1000)))

    start = time.time()
    index = NGram(items=values, key=lambda x: x.lower())
    logger.debug('Building {} index took {} ms'.format(key, int((time.time() - start) * 1000)))

    return index, mapped_entities

def remove_duplicates(entities):
    filtered_entities = []
    for entity, score in entities:
        if not any(f_score for f_entity, f_score in filtered_entities if f_entity == entity):
            filtered_entities.append((entity, score))

    return filtered_entities

def cross_section(results):
    if len(results) < 1:
        return []

    def cross_section_results(list_a, list_b):
        return [
            a_entity_with_score
            for a_entity_with_score
            in list_a
            if any([b_entity_with_score[0] == a_entity_with_score[0] for b_entity_with_score in list_b])
        ]

    entities_union = reduce(cross_section_results, results)

    return entities_union

def filter_by_media_type(entities, media_type):
    if media_type == 'movie':
        return [(entity, score) for entity, score in entities if 'movieid' in entity]
    elif media_type == 'tv show':
        return [(entity, score) for entity, score in entities if 'tvshowid' in entity]

    return entities

class LibraryIndex(object):
    def __init__(self, movies, tvshows, compose_index):
        self.movies = movies
        self.tvshows = tvshows
        self.compose_index = compose_index

    def _find_by(self, filter_value, value_type):
        index = self.compose_index[value_type]['ix']
        value_map = self.compose_index[value_type]['map']
        threshold = self.compose_index[value_type]['threshold']

        similar_values = index.search(strip_accents(filter_value).lower())
        similar_values = [(value, score) for value, score in similar_values if score > threshold]
        logger.debug(similar_values)

        matched_entities = [(value_map[value], score) for value, score in similar_values]
        matched_entities = [[(entity, score) for entity in entities] for entities, score in matched_entities]
        matched_entities = list(itertools.chain.from_iterable(matched_entities))

        return matched_entities

    def _find_by_values(self, filter_values, value_type):
        start = time.time()

        matched_entities = list(itertools.chain.from_iterable([self._find_by(filter_value, value_type) for filter_value in filter_values]))

        logger.debug('Find similar {} took {} ms'.format(value_type, int((time.time() - start) * 1000)))

        logger.debug('Length: {}'.format(len(matched_entities)))
        logger.debug('Length: {}'.format(len(remove_duplicates(matched_entities))))

        return remove_duplicates(matched_entities)

    def _get_entities(self, media_type):
        if media_type == 'movie':
            return self.movies
        elif media_type == 'tv show':
            return self.tvshows
        return []

    def find_by_filter(self, video_filter):
        start = time.time()

        results = []
        if 'titles' in video_filter and video_filter['titles']:
            results.append(self._find_by_values(video_filter['titles'], 'title'))
        if 'collections' in video_filter and video_filter['collections']:
            title_matches = self._find_by_values(video_filter['collections'], 'title')
            collection_matches = self._find_by_values(video_filter['collections'], 'collection')
            results.append(list(itertools.chain.from_iterable([title_matches, collection_matches])))
        if 'genres' in video_filter and video_filter['genres']:
            results.append(self._find_by_values(video_filter['genres'], 'genre'))
        if 'actors' in video_filter and video_filter['actors']:
            results.append(self._find_by_values(video_filter['actors'], 'actor'))
        if 'roles' in video_filter and video_filter['roles']:
            results.append(self._find_by_values(video_filter['roles'], 'role'))

        entities = cross_section(results)

        if 'mediaType' in video_filter:
            if len(results) < 1:
                entities = [(entity, 1.0) for entity in self._get_entities(video_filter['mediaType'])]
            else:
                entities = filter_by_media_type(entities, video_filter['mediaType'])

        logger.debug('Indexed find by filter took {} ms'.format(int((time.time() - start) * 1000)))

        return entities

    def find_best_by_filter(self, video_filter):
        entities = self.find_by_filter(video_filter)

        return entities[0] if entities else None


def create_library_index(movies, tvshows):
    title_ix, mapped_titles = build_title_index(movies, tvshows)
    collection_ix, mapped_collections = build_collection_index(movies, tvshows)
    genre_ix, mapped_genres = build_genre_index(movies, tvshows)
    role_ix, mapped_roles = build_cast_index(movies, tvshows, 'role')
    actor_name_ix, mapped_actor_names = build_cast_index(movies, tvshows, 'name')

    index = {
        'title': {'ix': title_ix, 'map': mapped_titles, 'threshold': 0.4},
        'collection': {'ix': collection_ix, 'map': mapped_collections, 'threshold': 0.4},
        'genre': {'ix': genre_ix, 'map': mapped_genres, 'threshold': 0.8},
        'role': {'ix': role_ix, 'map': mapped_roles, 'threshold': 0.8},
        'actor': {'ix': actor_name_ix, 'map': mapped_actor_names, 'threshold': 0.85},
    }

    return LibraryIndex(movies, tvshows, index)
