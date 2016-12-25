from PyQt5 import QtSvg, QtCore
import os

CELL_SIZE = 32
CELL_ROLE = QtCore.Qt.UserRole


WALL_VALUE = -1
GRASS_VALUE = 0
TARGET_VALUE = 1
DUDE_VALUE_LIST = [2, 3, 4, 5, 6]
DUDE_NUM = len(DUDE_VALUE_LIST)

UI_PATH = './ui/'
IMAGE_PATH = UI_PATH + 'pics/'
ARROW_PATH = IMAGE_PATH + 'arrows/'
ROAD_PATH = IMAGE_PATH + 'lines/'


def get_filename(name):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), name)


UI_MAIN_WINDOW = get_filename(UI_PATH + 'mainwindow.ui')
UI_NEW_MAZE = get_filename(UI_PATH + 'newmaze.ui')

GRASS_FILE = get_filename(IMAGE_PATH + 'grass.svg')
WALL_FILE = get_filename(IMAGE_PATH + 'wall.svg')
TARGET_FILE = get_filename(IMAGE_PATH + 'castle.svg')
DUDE_FILE_LIST = [get_filename(IMAGE_PATH + 'dude1.svg'), get_filename(IMAGE_PATH + 'dude2.svg'),
                  get_filename(IMAGE_PATH + 'dude3.svg'), get_filename(IMAGE_PATH + 'dude4.svg'),
                  get_filename(IMAGE_PATH + 'dude5.svg')]

UP_FILE = get_filename(ARROW_PATH + 'up.svg')
DOWN_FILE = get_filename(ARROW_PATH + 'down.svg')
LEFT_FILE = get_filename(ARROW_PATH + 'left.svg')
RIGHT_FILE = get_filename(ARROW_PATH + 'right.svg')

SVG_GRASS = QtSvg.QSvgRenderer(GRASS_FILE)
SVG_WALL = QtSvg.QSvgRenderer(WALL_FILE)
SVG_TARGET = QtSvg.QSvgRenderer(TARGET_FILE)
SVG_DUDE_LIST = [QtSvg.QSvgRenderer(DUDE_FILE_LIST[0]), QtSvg.QSvgRenderer(DUDE_FILE_LIST[1]),
                 QtSvg.QSvgRenderer(DUDE_FILE_LIST[2]), QtSvg.QSvgRenderer(DUDE_FILE_LIST[3]),
                 QtSvg.QSvgRenderer(DUDE_FILE_LIST[4])]

SVG_DOWN = QtSvg.QSvgRenderer(DOWN_FILE)
SVG_UP = QtSvg.QSvgRenderer(UP_FILE)
SVG_LEFT = QtSvg.QSvgRenderer(LEFT_FILE)
SVG_RIGHT = QtSvg.QSvgRenderer(RIGHT_FILE)

UP = b'^'
DOWN = b'v'
LEFT = b'<'
RIGHT = b'>'

DIRS = {
    UP: SVG_UP,
    LEFT: SVG_LEFT,
    RIGHT: SVG_RIGHT,
    DOWN: SVG_DOWN,
}

ROAD = [TARGET_VALUE, GRASS_VALUE] + DUDE_VALUE_LIST