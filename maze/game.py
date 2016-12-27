from .grid_widget import GridWidget
from . import const, actor

import numpy
import copy
import time
import asyncio


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
                index = numpy.where(self.edit_array == const.DUDE_VALUE_LIST[i])
                if len(index[0]) > 0:
                    self.actors.append(actor.Actor(self.grid, index[0][0], index[1][0], const.DUDE_VALUE_LIST[i]))
                    # remove dude from a grid array
                    self.grid.array[index[0][0], index[1][0]] = const.GRASS_VALUE
        else:
            self.disable_actors()

            self.gui.show_palette()
            self.gui.turn_nongame_buttons(True)

            self.grid.array = copy.deepcopy(self.edit_array)
            self.grid.update_path()
            self.grid.update()

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

    # async def check_game_over(self):
    #     if (await self.actors[0].task): #\
    #             # or (await self.actors[1].task) or (await self.actors[2].task) or \
    #             # (await self.actors[3].task) or (await self.actors[4].task):
    #         return
