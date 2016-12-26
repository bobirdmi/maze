from .grid_widget import GridWidget
from . import const, actor

import numpy
import copy
import asyncio


class Game:
    def __init__(self, array, gui):
        self.edit_array = copy.deepcopy(array)
        self.actors = []
        self.game_mode = False
        self.grid = GridWidget(array, const.CELL_SIZE, self)
        self.gui = gui

    def check_play(self):
        self.game_mode = not self.game_mode

        if self.grid.unreachable:
            self.gui.error_dialog("Error", 'Cannot run the game: there is an unreachable dude')
            return

        if self.game_mode:
            self.gui.hide_palette()

            self.edit_array = copy.deepcopy(self.grid.array)

            # initialize actors
            self.actors = []
            for i in range(const.DUDE_NUM):
                index = numpy.where(self.edit_array == const.DUDE_VALUE_LIST[i])
                if len(index[0]) > 0:
                    self.actors.append(actor.Actor(self.grid, index[0][0], index[1][0], const.DUDE_VALUE_LIST[i]))
                    # remove dude from a grid array
                    self.grid.array[index[0][0], index[1][0]] = const.GRASS_VALUE
        else:
            self.gui.show_palette()

            self.grid.array = copy.deepcopy(self.edit_array)
            self.grid.update_path()
            self.grid.update()



