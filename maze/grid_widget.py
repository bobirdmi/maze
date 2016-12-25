from PyQt5 import QtWidgets, QtGui, QtCore, QtSvg, uic
import numpy

from maze import analyze
from . import const


class GridWidget(QtWidgets.QWidget):
    def __init__(self, array):
        super().__init__()  # musíme zavolat konstruktor předka

        self.game_mode = False

        # initialize grid according to array size
        self.init_grid(array)

    def pixels_to_logical(self, x, y):
        return y // const.CELL_SIZE, x // const.CELL_SIZE

    def logical_to_pixels(self, row, column):
        return column * const.CELL_SIZE, row * const.CELL_SIZE

    def init_grid(self, array):
        """
        Saves the input array as self.array and initializes grid of the appropriate size.
        """
        self.array = array

        # check whether there is already a target
        index = numpy.where(self.array == const.TARGET_VALUE)
        if len(index[0]) < 1:
            self.array[1, 1] = const.TARGET_VALUE

        self.analyzed_maze = None
        self.path_list = None
        self.all_path_cells = None

        size = self.logical_to_pixels(*array.shape)
        self.setMinimumSize(*size)
        self.setMaximumSize(*size)
        self.resize(*size)

        self.update_path()

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
                rect = QtCore.QRectF(x, y, const.CELL_SIZE, const.CELL_SIZE)

                # podkladová barva pod poloprůhledné obrázky
                white = QtGui.QColor(255, 255, 255)
                painter.fillRect(rect, QtGui.QBrush(white))

                # trávu dáme všude, protože i zdi stojí na trávě
                const.SVG_GRASS.render(painter, rect)

                if not self.game_mode and self.array[row, column] in const.ROAD:
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

                if self.array[row, column] < 0:
                    # zdi dáme jen tam, kam patří
                    const.SVG_WALL.render(painter, rect)
                elif self.array[row, column] == const.TARGET_VALUE:
                    # target = castle
                    const.SVG_TARGET.render(painter, rect)
                else:
                    if self.array[row, column] in const.DUDE_VALUE_LIST:
                        # if there is any dude then draw him
                        const.SVG_DUDE_LIST[const.DUDE_VALUE_LIST.index(self.array[row, column])].render(painter, rect)

    def mousePressEvent(self, event):
        # převedeme klik na souřadnice matice
        row, column = self.pixels_to_logical(event.x(), event.y())

        # Pokud jsme v matici, aktualizujeme data
        if 0 <= row < self.array.shape[0] and 0 <= column < self.array.shape[1]:
            # too few targets, cannot remove
            if self.array[row, column] == const.TARGET_VALUE:
                index = numpy.where(self.array == const.TARGET_VALUE)
                if len(index[0]) < 2:
                    return

            if event.button() == QtCore.Qt.LeftButton:
                if self.selected in const.DUDE_VALUE_LIST or self.selected == const.TARGET_VALUE:
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
            self.update_path()

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

    def update_path(self):
        self.analyzed_maze = analyze(self.array)
        self.path_list = [[] for x in range(const.DUDE_NUM)]

        for i in range(const.DUDE_NUM):
            index = numpy.where(self.array == const.DUDE_VALUE_LIST[i])
            if len(index[0]) > 0:
                try:
                    self.path_list[i] = self.analyzed_maze.path(index[0][0], index[1][0])
                except ValueError:
                    # unreachable cell so do nothing
                    pass

        # get set of all path cells
        flatten = lambda l: [item for sub_list in l for item in sub_list]
        self.all_path_cells = set(flatten(self.path_list))