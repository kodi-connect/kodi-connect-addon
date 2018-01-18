import itertools
import time
import re
from random import shuffle

import setix.trgm

def build_title_index(movies, tvshows):
    start = time.time()

    entities = list(itertools.chain.from_iterable([movies, tvshows]))
    values = [entity['title'] for entity in entities]

    mapped_entities = {}
    for entity in entities:
        value = entity['title']
        if not value in mapped_entities:
            mapped_entities[value] = []

        mapped_entities[value].append(entity)

    print('Iterating title took {} ms'.format(int((time.time() - start) * 1000)))

    start = time.time()
    ix = setix.trgm.TrigramIndex()
    for value in values:
        ix.add(value)
    print('Building title index took {} ms'.format(int((time.time() - start) * 1000)))

    return ix, mapped_entities

def parse_collection(collection):
    m = re.search('(.*) Collection', collection)
    return m.group(1) if m else collection

def build_collection_index(movies, tvshows):
    start = time.time()

    entities = list(itertools.chain.from_iterable([movies, tvshows]))
    values = list(set([parse_collection(entity['set']) for entity in entities if 'set' in entity and len(entity['set']) > 0]))

    mapped_entities = {}
    for entity in entities:
        if 'set' in entity and len(entity['set']) > 0:
            value = parse_collection(entity['set'])
            if not value in mapped_entities:
                mapped_entities[value] = []

            mapped_entities[value].append(entity)

    print('Iterating collection took {} ms'.format(int((time.time() - start) * 1000)))

    start = time.time()
    ix = setix.trgm.TrigramIndex()
    for value in values:
        ix.add(value)
    print('Building collection index took {} ms'.format(int((time.time() - start) * 1000)))

    return ix, mapped_entities

def build_genre_index(movies, tvshows):
    start = time.time()

    entities = list(itertools.chain.from_iterable([movies, tvshows]))
    values = list(set(itertools.chain.from_iterable([entity['genre'] for entity in entities])))

    mapped_entities = {}
    for entity in entities:
        for genre in entity['genre']:
            if not genre in mapped_entities:
                mapped_entities[genre] = []

            mapped_entities[genre].append(entity)

    print('Iterating genre took {} ms'.format(int((time.time() - start) * 1000)))

    start = time.time()
    ix = setix.trgm.TrigramIndex()
    for value in values:
        ix.add(value)
    print('Building genre index took {} ms'.format(int((time.time() - start) * 1000)))

    return ix, mapped_entities

def build_cast_index(movies, tvshows, key):
    start = time.time()

    entities = list(itertools.chain.from_iterable([movies, tvshows]))
    values = [[cast[key] for cast in entity['cast']] for entity in entities]
    values = list(set(itertools.chain.from_iterable(values)))

    mapped_entities = {}
    for entity in entities:
        for cast in entity['cast']:
            value = cast[key]
            if not value in mapped_entities:
                mapped_entities[value] = []

            mapped_entities[value].append(entity)

    print('Iterating {} took {} ms'.format(key, int((time.time() - start) * 1000)))

    start = time.time()
    ix = setix.trgm.TrigramIndex()
    for value in values:
        ix.add(value)
    print('Building {} index took {} ms'.format(key, int((time.time() - start) * 1000)))

    return ix, mapped_entities

def remove_duplicates(entities):
    t = []
    for score, entity in entities:
        if not any(t_score for t_score, t_entity in t if t_entity == entity):
            t.append((score, entity))

    return t

def cross_section(results):
    first = results[0]
    rest = results[1:]

    if not rest:
        return first

    t = []
    for score, entity in first:
        for result in rest:
            if any(r_score for r_score, r_entity in result if r_entity == entity):
                t.append((score, entity))

    return t

class LibraryIndex(object):
    def __init__(self, ix):
        self.ix = ix

    def _find_by(self, filter_value, value_type):
        ix = self.ix[value_type]['ix']
        m = self.ix[value_type]['map']
        threshold = self.ix[value_type]['threshold']

        similar_values = ix.find_similar(filter_value).get_list()
        similar_values = [(score, value) for (score, value) in similar_values if score > threshold]
        similar_values = [[(score, value) for value in nested_values] for score, nested_values in similar_values]
        similar_values = list(itertools.chain.from_iterable(similar_values))
        print(similar_values)

        matched_entities = [(score, m[value]) for score, value in similar_values]
        matched_entities = [[(score, entity) for entity in entities] for score, entities in matched_entities]
        matched_entities = list(itertools.chain.from_iterable(matched_entities))

        return matched_entities

    def _find_by_values(self, filter_values, value_type):
        start = time.time()

        matched_entities = list(itertools.chain.from_iterable([self._find_by(filter_value, value_type) for filter_value in filter_values]))

        print('Find similar {} took {} ms'.format(value_type, int((time.time() - start) * 1000)))

        print('Length: {}'.format(len(matched_entities)))
        print('Length: {}'.format(len(remove_duplicates(matched_entities))))

        return remove_duplicates(matched_entities)

    def find_by_filter(self, f):
        start = time.time()

        results = []
        if 'titles' in f:
            results.append(self._find_by_values(f['titles'], 'title'))
        if 'collections' in f:
            results.append(self._find_by_values(f['collections'], 'collection'))
        if 'genres' in f:
            results.append(self._find_by_values(f['genres'], 'genre'))
        if 'actors' in f:
            results.append(self._find_by_values(f['actors'], 'actor'))
        if 'roles' in f:
            results.append(self._find_by_values(f['roles'], 'role'))

        entities = cross_section(results)

        # TODO - filter by mediaType

        print('Find by filter took {} ms'.format(int((time.time() - start) * 1000)))

        if not entities:
            return []

        entities = sorted(entities, key=lambda (score, entity): score, reverse=True)

        max_score = entities[0][0]
        print(max_score)
        max_items = 2
        print([(score, entity['title']) for score, entity in entities])

        t = []
        for score, entity in entities:
            if score == max_score:
                t.append((score, entity))
            else:
                break

        shuffle(t)
        t.extend(entities[len(t):])

        return [entity for score, entity in t[:max_items]]

    def find_best_by_filter(self, f):
        entities = self.find_by_filter(f)

        return entities[0] if entities else None


def create_library_index(movies, tvshows):
    title_ix, mapped_titles = build_title_index(movies, tvshows)
    collection_ix, mapped_collections = build_collection_index(movies, tvshows)
    genre_ix, mapped_genres = build_genre_index(movies, tvshows)
    role_ix, mapped_roles = build_cast_index(movies, tvshows, 'role')
    actor_name_ix, mapped_actor_names = build_cast_index(movies, tvshows, 'name')

    ix = {
        'title': { 'ix': title_ix, 'map': mapped_titles, 'threshold': 0.2 },
        'collection': { 'ix': collection_ix, 'map': mapped_collections, 'threshold': 0.7 },
        'genre': { 'ix': genre_ix, 'map': mapped_genres, 'threshold': 0.8 },
        'role': { 'ix': role_ix, 'map': mapped_roles, 'threshold': 0.8 },
        'actor': { 'ix': actor_name_ix, 'map': mapped_actor_names, 'threshold': 0.85 },
    }

    return LibraryIndex(ix)
