from random import shuffle

def get_best_matches(entities, count):
    entities = sorted(entities, key=lambda entity: entity[1], reverse=True)

    max_score = entities[0][1]

    tmp = []
    for entity, score in entities:
        if score == max_score:
            tmp.append((entity, score))
        else:
            break

    shuffle(tmp)
    tmp.extend(entities[len(tmp):])

    return [entity for entity, score in tmp[:count]]

def get_best_match(entities):
    if not entities:
        return None

    max_score = max(entities, key=lambda entity: entity[1])[1]
    best_entities = [entity for (entity, score) in entities if score == max_score]
    shuffle(best_entities)
    return best_entities[0]
