import os

PATH = os.path.dirname(os.path.realpath(__file__))

# setup
WIDTH = 1600
HEIGHT = 720
FPS = 60
TILESIZE = 50
LEVEL_SIZE = [30, 30]
LEVEL_VIEW_RANGE = 1

HITBOX_SIZE_FILTER = TILESIZE * 2

DEBUG = False
DEBUG_VECTOR_SIZE = 5

GOD_MODE = False

#####################

PLAYER_LAST_POSITION = [1000, 150]