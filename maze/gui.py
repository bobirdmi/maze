from PyQt5 import QtWidgets, QtGui, uic
import numpy
from os.path import expanduser
from quamash import QEventLoop
import asyncio

from . import const
from .game import Game


PALETTE_WIDTH = 100


class MazeGUI:
    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.loop = QEventLoop(self.app)
        asyncio.set_event_loop(self.loop)

        self.window = QtWidgets.QMainWindow()

        with open(const.UI_MAIN_WINDOW) as f:
            uic.loadUi(f, self.window)

        # bludiště zatím nadefinované rovnou v kódu
        array = numpy.zeros((15, 20), dtype=numpy.int8)

        # získáme oblast s posuvníky z Qt Designeru
        scroll_area = self.window.findChild(QtWidgets.QScrollArea, 'scrollArea')

        # dáme do ní náš grid
        self.game = Game(array, self)
        self.grid = self.game.grid
        scroll_area.setWidget(self.grid)

        # získáme paletu vytvořenou v Qt Designeru
        self.palette = self.window.findChild(QtWidgets.QListWidget, 'palette')

        self._set_buttons()
        self._set_list_widget()

    def run(self):
        self.window.show()
        self.loop.run_forever()

    def _set_buttons(self):
        action = self.window.findChild(QtWidgets.QAction, 'actionNew')
        action.triggered.connect(lambda: self.new_dialog())

        action = self.window.findChild(QtWidgets.QAction, 'actionSave')
        action.triggered.connect(lambda: self.save_dialog())

        action = self.window.findChild(QtWidgets.QAction, 'actionLoad')
        action.triggered.connect(lambda: self.load_dialog())

        action = self.window.findChild(QtWidgets.QAction, 'actionAbout')
        action.triggered.connect(lambda: self.about_dialog())

        action = self.window.findChild(QtWidgets.QAction, 'actionGame_Mode_on_off')
        action.triggered.connect(lambda: self.game.check_play())

    def uncheck_game_mode_button(self):
        action = self.window.findChild(QtWidgets.QAction, 'actionGame_Mode_on_off')
        action.setChecked(False)

    def turn_nongame_buttons(self, bool):
        action = self.window.findChild(QtWidgets.QAction, 'actionNew')
        action.setEnabled(bool)

        action = self.window.findChild(QtWidgets.QAction, 'actionSave')
        action.setEnabled(bool)

        action = self.window.findChild(QtWidgets.QAction, 'actionLoad')
        action.setEnabled(bool)

    def _set_list_widget(self):
        # získáme paletu vytvořenou v Qt Designeru
        # palette = self.window.findChild(QtWidgets.QListWidget, 'palette')

        def item_activated():
            """Tato funkce se zavolá, když uživatel zvolí položku"""

            # Položek může obecně být vybráno víc, ale v našem seznamu je to
            # zakázáno (v Designeru selectionMode=SingleSelection).
            # Projdeme "všechny vybrané položky", i když víme že bude max. jedna
            for item in self.palette.selectedItems():
                self.grid.selected = item.data(const.CELL_ROLE)

        self.palette.itemSelectionChanged.connect(item_activated)

        self.palette.addItem(self.create_list_widget_item('Grass', const.GRASS_FILE, const.GRASS_VALUE))  # přidáme položku do palety
        self.palette.addItem(self.create_list_widget_item('Wall', const.WALL_FILE, const.WALL_VALUE))
        self.palette.addItem(self.create_list_widget_item('Target', const.TARGET_FILE, const.TARGET_VALUE))

        dude_types = ['Scatterbrain', 'Speedster', 'Accelerator', 'TODO', 'TODO2']
        for i, dude_type in zip(range(const.DUDE_NUM), dude_types):
            self.palette.addItem(self.create_list_widget_item(dude_type, const.DUDE_FILE_LIST[i], const.DUDE_VALUE_LIST[i]))

        self.palette.setCurrentRow(1)

    def create_list_widget_item(self, item_label, image_file, role_value):
        item = QtWidgets.QListWidgetItem(item_label)  # vytvoříme položku
        icon = QtGui.QIcon(image_file)  # ikonu
        item.setIcon(icon)  # přiřadíme ikonu položce

        item.setData(const.CELL_ROLE, role_value)

        return item

    def hide_palette(self):
        self.palette.setMaximumWidth(0)

    def show_palette(self):
        self.palette.setMaximumWidth(PALETTE_WIDTH)

    def save_dialog(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(
            self.window, "Save file", expanduser("~"), "Text Files (*.txt)"
        )[0]

        try:
            if filename:
                numpy.savetxt(filename, self.grid.array)
        except Exception as e:
            self.error_dialog("Error", e.__str__())

    def load_dialog(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self.window, "Open file", expanduser("~"), "Text Files (*.txt)"
        )[0]

        try:
            if filename:
                self.grid.init_grid(numpy.loadtxt(filename, dtype=numpy.int8))
        except Exception as e:
            self.error_dialog("Error", e.__str__())

    def game_result_dialog(self, time_result):
        title = 'Game Over'
        body = 'You resisted fate for {:.2f} minutes!'.format(time_result/60)

        QtWidgets.QMessageBox.about(self.window, title, body)

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
        with open(const.UI_NEW_MAZE) as f:
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


def show_gui():
    gui = MazeGUI()
    gui.run()


