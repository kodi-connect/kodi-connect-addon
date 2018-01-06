import kodi

def search_and_play_handler(requested_titles):
    print('search_and_play_handler', requested_titles)
    movies = kodi.get_movies()
    movie, movie_score = kodi.get_best_match(requested_titles, movies)
    print(movie, movie_score)

    tv_shows = kodi.get_tv_shows()
    tv_show, tv_show_score = kodi.get_best_match(requested_titles, tv_shows)
    print(tv_show, tv_show_score)

    if movie and movie_score > tv_show_score:
        kodi.play_movie_handler(movie)
    elif tv_show:
        kodi.play_tv_show_handler(tv_show)
    else:
        print('NOT FOUND')
        return { 'status': 'error', 'error': 'not_found' }

    return { 'status': 'OK' }

def pause_handler():
    print('pause_handler')
    playerid = kodi.get_active_playerid()
    is_playing = kodi.is_player_playing(playerid)
    if is_playing is None:
        return { 'status': 'OK' }

    print('pause_handler, is_playing: {}'.format(is_playing))
    if is_playing:
        kodi.play_pause_player(playerid)

    return { 'status': 'OK' }

def resume_handler():
    print('resume_handler')
    playerid = kodi.get_active_playerid()
    is_playing = kodi.is_player_playing(playerid)
    if is_playing is None:
        return { 'status': 'Nothing playing' } # TODO - handle this, as user is expecting that something plays

    print('resume_handler, is_playing: {}'.format(is_playing))
    if not is_playing:
        kodi.play_pause_player(playerid)

    return { 'status': 'OK' }

def stop_handler():
    print('stop_handler')
    playerid = kodi.get_active_playerid()
    is_playing = kodi.is_player_playing(playerid)

    print('stop_handler, is_playing: {}'.format(is_playing))
    kodi.stop_player(playerid)

    return { 'status': 'OK' }

def handler(data):
    print('handler data:', data)
    responseData = { 'status': 'Not found' }
    if data['type'] == 'command':
        if data['commandType'] == 'searchAndPlay':
            responseData = search_and_play_handler(data['requestedTitles'])
        elif data['commandType'] == 'pause':
            responseData = pause_handler()
        elif data['commandType'] == 'resume':
            responseData = resume_handler()
        elif data['commandType'] == 'stop':
            responseData = stop_handler()

    print('handler responseData:', responseData)

    return responseData
