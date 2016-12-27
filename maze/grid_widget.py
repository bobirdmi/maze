from PyQt5 import QtWidgets, QtGui, QtCore, QtSvg
import numpy
import asyncio

from maze import analyze
from . import const


class GridWidget(QtWidgets.QWidget):
    def __init__(self, array, cell_size, game):
        super().__init__()  # musíme zavolat konstruktor předka

        self.cell_size = cell_size
        # self.game_mode = False
        self.game = game

        # initialize grid according to array size
        self.init_grid(array)

    def pixels_to_logical(self, x, y):
        return y // self.cell_size, x // self.cell_size

    def logical_to_pixels(self, row, column):
        return column * self.cell_size, row * self.cell_size

    def init_grid(self, array):
        """
        Saves the input array as self.array and initializes grid of the appropriate size.
        """
        self.array = array
        self.actor_pos = {}

        # check whether there is already a target
        index = numpy.where(self.array == const.TARGET_VALUE)
        if len(index[0]) < 1:
            self.array[1, 1] = const.TARGET_VALUE

        self.analyzed_maze = None
        self.path_list = None
        self.all_path_cells = None

        # there are no unreachable dudes by default
        self.unreachable = False

        size = self.logical_to_pixels(*array.shape)
        self.setMinimumSize(*size)
        self.setMaximumSize(*size)
        self.resize(*size)

        self.update_path()

    def _draw_paths(self, painter, rect, row, column):
        if self.all_path_cells and self.array[row, column] in const.ROAD:
            # there is an empty cell so we draw the paths by arrows and roads if needed
            for i in range(const.DUDE_NUM):
                if self.path_list[i] is not None and (row, column) in self.path_list[i]:
                    # draw roads
                    cross_sum = 0
                    for func in [self.up, self.down, self.left, self.right]:
                        cross_sum += func((row, column))

                    if 0 < cross_sum <= 15:
                        svg = QtSvg.QSvgRenderer(const.get_filename(const.ROAD_PATH + str(cross_sum) + '.svg'))
                        svg.render(painter, rect)

                    # draw arrows
                    if self.array[row, column] == const.GRASS_VALUE:
                        const.DIRS[self.analyzed_maze.directions[row, column]].render(painter, rect)

                    break

    def paintEvent(self, event):
        rect = event.rect()  # získáme informace o překreslované oblasti

        # zjistíme, jakou oblast naší matice to představuje
        # nesmíme se přitom dostat z matice ven
        row_min, col_min = self.pixels_to_logical(rect.left(), rect.top())
        row_min = max(row_min, 0)
        col_min = max(col_min, 0)
        row_max, col_max = self.pixels_to_logical(rect.right(), rect.bottom())
        row_max = min(row_max + 1, self.array.shape[0])
        col_max = min(col_max + 1, self.array.shape[1])

        painter = QtGui.QPainter(self)  # budeme kreslit

        for row in range(row_min, row_max):
            for column in range(col_min, col_max):
                # získáme čtvereček, který budeme vybarvovat
                x, y = self.logical_to_pixels(row, column)
                rect = QtCore.QRectF(x, y, self.cell_size, self.cell_size)

                # podkladová barva pod poloprůhledné obrázky
                white = QtGui.QColor(255, 255, 255)
                painter.fillRect(rect, QtGui.QBrush(white))

                # trávu dáme všude, protože i zdi stojí na trávě
                const.SVG_GRASS.render(painter, rect)

                if not self.game.game_mode:
                    self._draw_paths(painter, rect, row, column)

                if self.array[row, column] < 0:
                    # zdi dáme jen tam, kam patří
                    const.SVG_WALL.render(painter, rect)
                elif self.array[row, column] == const.TARGET_VALUE:
                    # target = castle
                    const.SVG_TARGET.render(painter, rect)
                else:
                    if not self.game.game_mode and self.array[row, column] in const.DUDE_VALUE_LIST:
                        # if there is any dude then draw him
                        const.SVG_DUDE_LIST[const.DUDE_VALUE_LIST.index(self.array[row, column])].render(painter, rect)

        if self.game.game_mode:
            # game is on!
            # move the dudes
            for act in self.game.actors:
                if act.kind in self.actor_pos.keys():
                    x, y = self.actor_pos[act.kind]
                    rect = QtCore.QRectF(x, y, self.cell_size, self.cell_size)

                    const.SVG_DUDE_LIST[act.kind - 2].render(painter, rect)

            if self.game.game_over:
                self.game.disable_actors()
                self.game.show_result()

    def mousePressEvent(self, event):
        # převedeme klik na souřadnice matice
        row, column = self.pixels_to_logical(event.x(), event.y())

        # Pokud jsme v matici, aktualizujeme data
        if 0 <= row < self.array.shape[0] and 0 <= column < self.array.shape[1]:
            # game mode ON
            if self.game.game_mode and \
                    (self.array[row, column] == const.TARGET_VALUE or
                             self.game.is_actor_on_tile(row, column)):
                # there are dudes or target -> do nothing
                return

            # too few targets (castles), cannot remove
            if self.array[row, column] == const.TARGET_VALUE:
                index = numpy.where(self.array == const.TARGET_VALUE)
                if len(index[0]) < 2:
                    return

            old_value = const.GRASS_VALUE

            # removes existed dude path if this dude will be removed
            if self.array[row, column] in const.DUDE_VALUE_LIST:
                self.path_list[self.array[row, column] - 2] = []

            if event.button() == QtCore.Qt.LeftButton:
                if self.game.game_mode:
                    old_value = self.array[row, column]
                    self.array[row, column] = const.WALL_VALUE
                else:
                    if self.selected in const.DUDE_VALUE_LIST or self.selected == const.TARGET_VALUE:
                        if self.analyzed_maze.directions[row, column] == b' ':
                            # a player cannot give dude or target on an unreachable cell
                            return

                        index = numpy.where(self.array == self.selected)
                        if len(index[0]) > 0:
                            self.array[index[0][0], index[1][0]] = const.GRASS_VALUE

                    self.array[row, column] = self.selected
            elif event.button() == QtCore.Qt.RightButton:
                self.array[row, column] = const.GRASS_VALUE
            else:
                return

            # tímto zajistíme překreslení celého widgetu
            self.update()

            # computes new paths
            status = self.update_path()
            if status:
                # revert changes
                self.array[row, column] = old_value

    def up(self, loc):
        if loc[0] == 0:
            return 0
        elif (loc[0] - 1, loc[1]) in self.all_path_cells:
            return 1
        else:
            return 0

    def down(self, loc):
        if loc[0] == (self.array.shape[0] - 1):
            return 0
        elif (loc[0] + 1, loc[1]) in self.all_path_cells:
            return 4
        else:
            return 0

    def left(self, loc):
        if loc[1] == 0:
            return 0
        elif (loc[0], loc[1] - 1) in self.all_path_cells:
            return 2
        else:
            return 0

    def right(self, loc):
        if loc[1] == (self.array.shape[1] - 1):
            return 0
        elif (loc[0], loc[1] + 1) in self.all_path_cells:
            return 8
        else:
            return 0

    def compute_paths(self):
        if self.game.game_mode:
            for act in self.game.actors:
                try:
                    index = act.kind - 2
                    old_path = self.path_list[index]

                    if act.direction == b'>':
                        row = act.row
                        column = int(act.column + 1.0)
                    elif act.direction == b'<':
                        row = act.row
                        column = int(act.column)
                    elif act.direction == b'^':
                        row = int(act.row)
                        column = act.column
                    elif act.direction == b'v':
                        row = int(act.row + 1.0)
                        column = act.column
                    else:
                        row = int(act.row)
                        column = int(act.column)

                    self.path_list[index] = self.analyzed_maze.path(int(column), int(row))
                except ValueError:
                    # set status in case of unreachable dudes (fools)
                    self.path_list[index] = old_path
                    return True
        else:
            for i in range(const.DUDE_NUM):
                index = numpy.where(self.array == const.DUDE_VALUE_LIST[i])
                if len(index[0]) > 0:
                    try:
                        old_path = self.path_list[i]
                        self.path_list[i] = self.analyzed_maze.path(index[0][0], index[1][0])
                    except ValueError:
                        # set status in case of unreachable dudes (fools)
                        self.path_list[i] = old_path
                        return True

        return False

    def update_path(self):
        if self.analyzed_maze:
            prev_directions = self.analyzed_maze.directions
        else:
            prev_directions = None

        self.analyzed_maze = analyze(self.array)

        if not self.path_list:
            self.path_list = [[] for x in range(const.DUDE_NUM)]

        # computes paths
        # in game mode returns "True" if there are unreachable dudes
        hopeless_fools = self.compute_paths()

        if hopeless_fools:
            if prev_directions is None:
                # we load a file with unreachable dudes
                self.unreachable = True
                raise ValueError('There is an unreachable dude...')

            self.analyzed_maze.directions = prev_directions

        self.unreachable = False

        # get set of all path cells
        flatten = lambda l: [item for sub_list in l for item in sub_list]
        self.all_path_cells = set(flatten(self.path_list))

        self.directions = self.analyzed_maze.directions

        return hopeless_fools

    def update_actor(self, actor):
        # save new position of an actor
        x, y = self.logical_to_pixels(actor.row, actor.column)
        self.actor_pos[actor.kind] = (x, y)

        # is it game over (dude is in a castle)?
        if actor.row - int(actor.row) == 0 and actor.column - int(actor.column) == 0 \
                and self.directions[int(actor.row), int(actor.column)] == b'X':
            self.game.game_over = True

        self.update()





