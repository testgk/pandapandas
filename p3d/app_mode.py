"""
App Mode — defines the launch mode of the globe application.
"""
from enum import Enum


class AppMode( Enum ):
    GLOBE = "globe"   # pure globe viewer, no game
    GAME  = "game"    # full GeoChallenge game mode

