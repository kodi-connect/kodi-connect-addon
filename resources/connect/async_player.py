from tornado.ioloop import IOLoop

import kodi_rpc
from log import logger

def play_movie(movie):
    IOLoop.instance().add_callback(_play_movie, movie)

def play_tvshow(tvshow, season, episode):
    IOLoop.instance().add_callback(_play_tvshow, tvshow, season, episode)

def play_episodeid(episodeid):
    IOLoop.instance().add_callback(_play_episodeid, episodeid)

def play_pause(playerid):
    IOLoop.instance().add_callback(_play_pause, playerid)

def stop(playerid):
    IOLoop.instance().add_callback(_stop, playerid)
