from random import shuffle
from fuzzywuzzy import fuzz
from log import logger

def fuzzy_contains(array, value, threshold):
    tmp = [(v, fuzz.token_set_ratio(value, v)) for v in array]
    tmp = [v for v, score in tmp if score > threshold]
    return len(tmp) > 0

def custom_title_ratio(s1, s2):
    functions = [fuzz.token_set_ratio, fuzz.partial_ratio, fuzz.ratio]

    sum = 0
    for function in functions:
        sum += function(s1, s2)

    return sum / len(functions)

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
    entity_roles = [cast['role'] for cast in entity['cast'] if fuzzy_contains(filter_roles, cast['role'])]
    return len(entity_roles) > 0

def filter_by_role(entities, roles):
    # return [(entity, score) for ]
    return [(entity, score) for entity, score in entities if has_role(entity, roles)]

filters = [
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

    for filter_type, filter_function in filters:
        if filter_type in video_filter and video_filter[filter_type]:
            entities = filter_function(entities, video_filter[filter_type])

    logger.debug(str([(entity['title'], entity['genre'], score) for entity, score in entities]))

    return entities

    if entities:
        logger.debug(str(entities[0]))
        max_score = max(entities, key=lambda (entity, score): score)[1]
        logger.debug('max_score: {}'.format(max_score))
        best_entities = [entity for (entity, score) in entities if score == max_score]
        logger.debug(str([entity['title'] for entity in best_entities]))
        shuffle(best_entities)
        return best_entities[0], max_score

    return None, 0

def get_best_matches(entities, count):
    entities = sorted(entities, key=lambda (entity, score): score, reverse=True)

    max_score = entities[0][1]

    t = []
    for entity, score in entities:
        if score == max_score:
            t.append((entity, score))
        else:
            break

    shuffle(t)
    t.extend(entities[len(t):])

    return [entity for entity, score in t[:count]]

def get_best_match(entities):
    if not entities: return None

    max_score = max(entities, key=lambda (entity, score): score)[1]
    best_entities = [entity for (entity, score) in entities if score == max_score]
    shuffle(best_entities)
    return best_entities[0]
