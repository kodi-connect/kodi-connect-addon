import time
from fuzzywuzzy import fuzz
from connect import logger

def fuzzy_contains(array, value, threshold):
    tmp = [(v, fuzz.token_set_ratio(value, v)) for v in array]
    tmp = [v for v, score in tmp if score > threshold]
    return len(tmp) > 0

def custom_title_ratio(str1, str2):
    functions = [fuzz.token_set_ratio, fuzz.partial_ratio, fuzz.ratio]

    total = 0
    for function in functions:
        total += function(str1, str2)

    return total / len(functions)

def get_best_title_score(entity_title, filter_titles):
    scores = [custom_title_ratio(entity_title, title) for title in filter_titles]
    return max(scores)

def filter_by_title(entities, titles, threshold=60):
    entities = [(entity, get_best_title_score(entity['title'], titles)) for entity, score in entities]
    return [(entity, score) for entity, score in entities if score >= threshold]

def is_genre(entity, filter_genres):
    entity_genres = entity['genre']
    matched_entity_genres = [entity_genre for entity_genre in entity_genres if fuzzy_contains(filter_genres, entity_genre, 90)]
    return len(matched_entity_genres) > 0

def filter_by_genre(entities, genres):
    return [(entity, score) for entity, score in entities if is_genre(entity, genres)]

def has_actor(entity, filter_actors):
    entity_actors = [cast['name'] for cast in entity['cast'] if fuzzy_contains(filter_actors, cast['name'], 90)]
    return len(entity_actors) > 0

def filter_by_actor(entities, actors):
    return [(entity, score) for entity, score in entities if has_actor(entity, actors)]

def has_role(entity, filter_roles):
    entity_roles = [cast['role'] for cast in entity['cast'] if fuzzy_contains(filter_roles, cast['role'], 90)]
    return len(entity_roles) > 0

def filter_by_role(entities, roles):
    return [(entity, score) for entity, score in entities if has_role(entity, roles)]

FILTERS = [
    ('titles', filter_by_title),
    ('collections', filter_by_title),
    ('genres', filter_by_genre),
    ('actors', filter_by_actor),
    ('roles', filter_by_role),
]

def filter_entities(video_filter, entities):
    if not entities:
        return []

    entities = [(entity, 100) for entity in entities]

    for filter_type, filter_function in FILTERS:
        if filter_type in video_filter and video_filter[filter_type]:
            entities = filter_function(entities, video_filter[filter_type])

    logger.debug(str([(entity['title'], entity['genre'], score) for entity, score in entities]))

    return entities

def fuzzy_filter(movies, tvshows, video_filter):
    start = time.time()

    entities = []
    if 'mediaType' in video_filter and video_filter['mediaType'] and video_filter['mediaType'] != 'movie':
        pass
    else:
        entities = entities + movies

    if 'mediaType' in video_filter and video_filter['mediaType'] and video_filter['mediaType'] != 'tv show':
        pass
    else:
        entities = entities + tvshows

    filtered_entities = filter_entities(video_filter, entities)

    logger.debug('Fuzzy filter took {} ms'.format(int((time.time() - start) * 1000)))

    return filtered_entities
