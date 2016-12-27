import copy
import time

import numpy

from maze.actors.actor import Actor
from maze.actors.speedster import Speedster
from maze.actors.accelerator import Accelerator
from maze.actors.scatterbrain import Scatterbrain
from . import const
from .grid_widget import GridWidget


class Game:
    def __init__(self, array, gui):
        self.edit_array = copy.deepcopy(array)
        self.actors = []
        self.game_mode = False
        self.game_over = False
        self.grid = GridWidget(array, const.CELL_SIZE, self)
        self.gui = gui
        self.start_time = None

    def check_play(self):
        if self.grid.unreachable:
            self.gui.uncheck_game_mode_button()
            self.gui.error_dialog("Error", 'Cannot run the game: there is an unreachable dude')
            return

        self.game_mode = not self.game_mode

        if self.game_mode:
            self.gui.hide_palette()
            self.gui.turn_nongame_buttons(False)

            self.edit_array = copy.deepcopy(self.grid.array)
            self.game_over = False

            self.start_time = time.time()

            # initialize actors
            self.actors = []
            for i in range(const.DUDE_NUM):
                self._init_actor(const.DUDE_VALUE_LIST[i])
                # index = numpy.where(self.edit_array == const.DUDE_VALUE_LIST[i])
                # if len(index[0]) > 0:
                #     if i == 0:
                #         self.actors.append(Scatterbrain(self.grid, index[0][0], index[1][0], const.DUDE_VALUE_LIST[i]))
                #     else:
                #         self.actors.append(Actor(self.grid, index[0][0], index[1][0], const.DUDE_VALUE_LIST[i]))
                #     # remove dude from a grid array
                #     self.grid.array[index[0][0], index[1][0]] = const.GRASS_VALUE
        else:
            self.disable_actors()

            self.gui.show_palette()
            self.gui.turn_nongame_buttons(True)

            self.grid.array = copy.deepcopy(self.edit_array)
            self.grid.update_path()
            self.grid.update()

    def _init_actor(self, kind):
        index = numpy.where(self.edit_array == kind)

        if len(index[0]) > 0:
            if kind == 2:
                self.actors.append(Scatterbrain(self.grid, index[0][0], index[1][0], kind))
            elif kind == 3:
                self.actors.append(Speedster(self.grid, index[0][0], index[1][0], kind))
            elif kind == 4:
                self.actors.append(Accelerator(self.grid, index[0][0], index[1][0], kind))
            # elif kind == 5:
            #     self.actors.append(Scatterbrain(self.grid, index[0][0], index[1][0], kind))
            # elif kind == 6:
            #     self.actors.append(Scatterbrain(self.grid, index[0][0], index[1][0], kind))

            self.grid.array[index[0][0], index[1][0]] = const.GRASS_VALUE

    def disable_actors(self):
        for act in self.actors:
            act.task.cancel()

    def is_actor_on_tile(self, row, column):
        for act in self.actors:
            if act.direction == b'>':
                if act.row == row and int(act.column + 1.0) == column:
                    return True
            elif act.direction == b'<':
                if act.row == row and int(act.column) == column:
                    return True
            elif act.direction == b'^':
                if act.column == column and int(act.row) == row:
                    return True
            elif act.direction == b'v':
                if act.column == column and int(act.row + 1.0) == row:
                    return True
            else:
                return False

    def show_result(self):
        self.game_over = False
        end_time = time.time()

        self.gui.game_result_dialog(end_time - self.start_time)

