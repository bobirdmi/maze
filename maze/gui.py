from PyQt5 import QtWidgets, QtGui, QtCore, QtSvg, uic
import numpy
from os.path import expanduser
import os

from maze import analyze


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

DIRS_DELTA = {
    UP: 1,
    DOWN: 4,
    LEFT: 2,
    RIGHT: 8,
    b'X': 0,
}

ANTIDIRS_DELTA = {
    UP: 4,
    DOWN: 1,
    LEFT: 8,
    RIGHT: 2,
    b'X': 0,
}

DIRS = {
    UP: SVG_UP,
    LEFT: SVG_LEFT,
    RIGHT: SVG_RIGHT,
    DOWN: SVG_DOWN,
}

ROAD = [TARGET_VALUE, GRASS_VALUE] + DUDE_VALUE_LIST


def pixels_to_logical(x, y):
    return y // CELL_SIZE, x // CELL_SIZE


def logical_to_pixels(row, column):
    return column * CELL_SIZE, row * CELL_SIZE


class MazeGUI:
    def __init__(self):
        self.app = QtWidgets.QApplication([])

        self.window = QtWidgets.QMainWindow()

        with open(UI_MAIN_WINDOW) as f:
            uic.loadUi(f, self.window)

        # bludiště zatím nadefinované rovnou v kódu
        array = numpy.zeros((15, 20), dtype=numpy.int8)

        # získáme oblast s posuvníky z Qt Designeru
        scroll_area = self.window.findChild(QtWidgets.QScrollArea, 'scrollArea')

        # dáme do ní náš grid
        self.grid = GridWidget(array)
        scroll_area.setWidget(self.grid)

        self.set_buttons()
        self.set_list_widget()

    def set_buttons(self):
        action = self.window.findChild(QtWidgets.QAction, 'actionNew')
        action.triggered.connect(lambda: self.new_dialog())

        action = self.window.findChild(QtWidgets.QAction, 'actionSave')
        action.triggered.connect(lambda: self.save_dialog())

        action = self.window.findChild(QtWidgets.QAction, 'actionLoad')
        action.triggered.connect(lambda: self.load_dialog())

        action = self.window.findChild(QtWidgets.QAction, 'actionAbout')
        action.triggered.connect(lambda: self.about_dialog())

    def set_list_widget(self):
        # získáme paletu vytvořenou v Qt Designeru
        palette = self.window.findChild(QtWidgets.QListWidget, 'palette')

        def item_activated():
            """Tato funkce se zavolá, když uživatel zvolí položku"""

            # Položek může obecně být vybráno víc, ale v našem seznamu je to
            # zakázáno (v Designeru selectionMode=SingleSelection).
            # Projdeme "všechny vybrané položky", i když víme že bude max. jedna
            for item in palette.selectedItems():
                self.grid.selected = item.data(CELL_ROLE)

        palette.itemSelectionChanged.connect(item_activated)

        palette.addItem(self.create_list_widget_item('Grass', GRASS_FILE, GRASS_VALUE))  # přidáme položku do palety
        palette.addItem(self.create_list_widget_item('Wall', WALL_FILE, WALL_VALUE))
        palette.addItem(self.create_list_widget_item('Target', TARGET_FILE, TARGET_VALUE))
        for i in range(DUDE_NUM):
            palette.addItem(self.create_list_widget_item('Dude ' + str(i), DUDE_FILE_LIST[i], DUDE_VALUE_LIST[i]))

        palette.setCurrentRow(1)

    def create_list_widget_item(self, item_label, image_file, role_value):
        item = QtWidgets.QListWidgetItem(item_label)  # vytvoříme položku
        icon = QtGui.QIcon(image_file)  # ikonu
        item.setIcon(icon)  # přiřadíme ikonu položce

        item.setData(CELL_ROLE, role_value)

        return item

    def save_dialog(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(
            self.window, "Save file", expanduser("~"), "Text Files (*.txt)"
        )[0]

        if filename:
            numpy.savetxt(filename, self.grid.array)

    def load_dialog(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self.window, "Open file", expanduser("~"), "Text Files (*.txt)"
        )[0]

        try:
            if filename:
                self.grid.init_grid(numpy.loadtxt(filename, dtype=numpy.int8))
        except ValueError as e:
            self.error_dialog("Load error", e.__str__())

    def about_dialog(self):
        title = "Maze"
        description = "<p>This app provides maze solver in Cython with GUI.</p>\n"
        link = "<p>Link on <a href='https://github.com/bobirdmi/maze'>GitHub</a></p>\n"
        images = "<p>All images were created by the <a href='http://kenney.nl/'>Kenney</a> studio, " \
                 "and were kindly released into the Public Domain. They can be downloaded from " \
                 "<a href='http://opengameart.org/users/kenney'>OpenGameArt.org</a>.</p>\n"
        authors = "<p>Copyright (C) 2016 Dmitriy Bobir bobirdima@gmail.com</p>" \
                  "<p>Copyright (C) 2016 Miro Hrončok miro@hroncok.cz</p>" \
                  "<p>Copyright (C) 2016 Red Hat, Inc.</p>"
        license_text = "<p>Licensed under GNU General Public License version 3</p>"

        body = description + link + images + authors + license_text

        QtWidgets.QMessageBox.about(self.window, title, body)

    def error_dialog(self, title, body):
        QtWidgets.QMessageBox.critical(self.window, title, body)

    def new_dialog(self):
        # Vytvoříme nový dialog.
        # V dokumentaci mají dialogy jako argument `this`;
        # jde o "nadřazené" okno
        dialog = QtWidgets.QDialog(self.window)

        # Načteme layout z Qt Designeru
        with open(UI_NEW_MAZE) as f:
            uic.loadUi(f, dialog)

        # Zobrazíme dialog.
        # Funkce exec zajistí modalitu (tj.  tzn. nejde ovládat zbytek aplikace,
        # dokud je dialog zobrazen), a vrátí se až potom, co uživatel dialog zavře.
        result = dialog.exec()

        # Výsledná hodnota odpovídá tlačítku/způsobu, kterým uživatel dialog zavřel.
        if result == QtWidgets.QDialog.Rejected:
            # Dialog uživatel zavřel nebo klikl na Cancel
            return

        # Načtení hodnot ze SpinBoxů
        cols = dialog.findChild(QtWidgets.QSpinBox, 'widthBox').value()
        rows = dialog.findChild(QtWidgets.QSpinBox, 'heightBox').value()

        # Vytvoření nového bludiště
        # Bludiště může být jinak velké, tak musíme změnit velikost Gridu
        self.grid.init_grid(numpy.zeros((rows, cols), dtype=numpy.int8))

        # Překreslení celého Gridu
        self.grid.update()


class GridWidget(QtWidgets.QWidget):
    def __init__(self, array):
        super().__init__()  # musíme zavolat konstruktor předka
        # initialize grid according to array size
        self.init_grid(array)

    def init_grid(self, array):
        """
        Saves the input array as self.array and initializes grid of the appropriate size.
        """
        self.array = array
        self.array[1, 1] = TARGET_VALUE
        self.analyzed_maze = None
        self.path_list = None
        # self.all_path_cells = None
        # self.path_matrix = numpy.zeros(*array.shape, dtype=numpy.int8)
        # self.path_matrix = {}

        size = logical_to_pixels(*array.shape)
        self.setMinimumSize(*size)
        self.setMaximumSize(*size)
        self.resize(*size)

        self.update_path()

    def paintEvent(self, event):
        rect = event.rect()  # získáme informace o překreslované oblasti

        # zjistíme, jakou oblast naší matice to představuje
        # nesmíme se přitom dostat z matice ven
        row_min, col_min = pixels_to_logical(rect.left(), rect.top())
        row_min = max(row_min, 0)
        col_min = max(col_min, 0)
        row_max, col_max = pixels_to_logical(rect.right(), rect.bottom())
        row_max = min(row_max + 1, self.array.shape[0])
        col_max = min(col_max + 1, self.array.shape[1])

        painter = QtGui.QPainter(self)  # budeme kreslit

        self.path_matrix = {}
        for row in range(row_min, row_max):
            for column in range(col_min, col_max):
                # získáme čtvereček, který budeme vybarvovat
                x, y = logical_to_pixels(row, column)
                rect = QtCore.QRectF(x, y, CELL_SIZE, CELL_SIZE)

                # podkladová barva pod poloprůhledné obrázky
                white = QtGui.QColor(255, 255, 255)
                painter.fillRect(rect, QtGui.QBrush(white))

                # trávu dáme všude, protože i zdi stojí na trávě
                SVG_GRASS.render(painter, rect)

                if self.array[row, column] in ROAD:
                    # there is an empty cell so we draw the paths by arrows and roads if needed
                    for i in range(DUDE_NUM):
                        if self.path_list[i] is not None and (row, column) in self.path_list[i]:
                            # draw roads
                            cross_sum = 0
                            for func in [self.up, self.down, self.left, self.right]:
                                cross_sum += func((row, column), i)

                            delta = 0
                            if self.path_matrix.get((row, column), 0) > 0:
                                if cross_sum != self.path_matrix[(row, column)]:
                                    direction = self.analyzed_maze.directions[row, column]

                                    delta = DIRS_DELTA[direction]
                                    if delta == 0:
                                        # there is an end point (castle)
                                        self.path_matrix[(row, column)] = cross_sum
                                    else:
                                        self.path_matrix[(row, column)] = self.path_matrix[(row, column)] + cross_sum - delta
                            else:
                                self.path_matrix[(row, column)] = cross_sum

                            svg = QtSvg.QSvgRenderer(get_filename(ROAD_PATH + str(self.path_matrix[(row, column)]) + '.svg'))
                            svg.render(painter, rect)

                            # draw arrows
                            if self.array[row, column] == GRASS_VALUE:
                                DIRS[self.analyzed_maze.directions[row, column]].render(painter, rect)

                if self.array[row, column] < 0:
                    # zdi dáme jen tam, kam patří
                    SVG_WALL.render(painter, rect)
                elif self.array[row, column] == TARGET_VALUE:
                    # target = castle
                    SVG_TARGET.render(painter, rect)
                else:
                    if self.array[row, column] in DUDE_VALUE_LIST:
                        # if there is any dude then draw him
                        SVG_DUDE_LIST[DUDE_VALUE_LIST.index(self.array[row, column])].render(painter, rect)

    def mousePressEvent(self, event):
        # převedeme klik na souřadnice matice
        row, column = pixels_to_logical(event.x(), event.y())

        # Pokud jsme v matici, aktualizujeme data
        if 0 <= row < self.array.shape[0] and 0 <= column < self.array.shape[1]:
            # too few targets, cannot remove
            if self.array[row, column] == TARGET_VALUE:
                index = numpy.where(self.array == TARGET_VALUE)
                if len(index[0]) < 2:
                    return

            if event.button() == QtCore.Qt.LeftButton:
                if self.selected in DUDE_VALUE_LIST or self.selected == TARGET_VALUE:
                    index = numpy.where(self.array == self.selected)
                    if len(index[0]) > 0:
                        self.array[index[0][0], index[1][0]] = GRASS_VALUE

                self.array[row, column] = self.selected
            elif event.button() == QtCore.Qt.RightButton:
                self.array[row, column] = GRASS_VALUE
            else:
                return

            # tímto zajistíme překreslení celého widgetu
            self.update()
            self.update_path()

    def up(self, loc, dude_id):
        if loc[0] == 0:
            return 0
        elif (loc[0] - 1, loc[1]) in self.path_list[dude_id]:
            return 1
        else:
            return 0

    def down(self, loc, dude_id):
        if loc[0] == (self.array.shape[0] - 1):
            return 0
        elif (loc[0] + 1, loc[1]) in self.path_list[dude_id]:
            return 4
        else:
            return 0

    def left(self, loc, dude_id):
        if loc[1] == 0:
            return 0
        elif (loc[0], loc[1] - 1) in self.path_list[dude_id]:
            return 2
        else:
            return 0

    def right(self, loc, dude_id):
        if loc[1] == (self.array.shape[1] - 1):
            return 0
        elif (loc[0], loc[1] + 1) in self.path_list[dude_id]:
            return 8
        else:
            return 0

    def update_path(self):
        self.analyzed_maze = analyze(self.array)
        self.path_list = [[] for x in range(DUDE_NUM)]
        self.path_matrix = {}

        for i in range(DUDE_NUM):
            index = numpy.where(self.array == DUDE_VALUE_LIST[i])
            if len(index[0]) > 0:
                try:
                    self.path_list[i] = self.analyzed_maze.path(index[0][0], index[1][0])
                except ValueError:
                    # unreachable cell so do nothing
                    pass


def show_gui():
    gui = MazeGUI()

    gui.window.show()
    return gui.app.exec()

