from PyQt5 import QtWidgets, QtGui, QtCore, QtSvg, uic
import numpy


CELL_SIZE = 32
CELL_ROLE = QtCore.Qt.UserRole
WALL_VALUE = -1
GRASS_VALUE = 0

UI_PATH = './ui/'
IMAGE_PATH = './ui/images/'
SVG_GRASS = QtSvg.QSvgRenderer(IMAGE_PATH + 'grass.svg')
SVG_WALL = QtSvg.QSvgRenderer(IMAGE_PATH + 'wall.svg')


class MazeGUI():
    def __init__(self):
        self.app = QtWidgets.QApplication([])

        self.window = QtWidgets.QMainWindow()

        with open(UI_PATH + 'mainwindow.ui') as f:
            uic.loadUi(f, self.window)

        # bludiště zatím nadefinované rovnou v kódu
        array = numpy.zeros((15, 20), dtype=numpy.int8)
        array[:, 5] = -1  # nějaká zeď

        # získáme oblast s posuvníky z Qt Designeru
        scroll_area = self.window.findChild(QtWidgets.QScrollArea, 'scrollArea')

        # dáme do ní náš grid
        self.grid = GridWidget(array)
        scroll_area.setWidget(self.grid)

        action = self.window.findChild(QtWidgets.QAction, 'actionNew')
        action.triggered.connect(lambda: self.new_dialog())

        self.set_list_widget()

    def set_list_widget(self):
        # získáme paletu vytvořenou v Qt Designeru
        palette = self.window.findChild(QtWidgets.QListWidget, 'palette')

        def item_activated():
            """Tato funkce se zavolá, když uživatel zvolí položku"""

            # Položek může obecně být vybráno víc, ale v našem seznamu je to
            # zakázáno (v Designeru selectionMode=SingleSelection).
            # Projdeme "všechny vybrané položky", i když víme že bude max. jedna
            for item in palette.selectedItems():
                # print(item.data(CELL_ROLE))
                # grid.selected = item.data(QtCore.Qt.UserRole)
                self.grid.selected = item.data(CELL_ROLE)

        palette.itemSelectionChanged.connect(item_activated)

        palette.addItem(self.create_list_widget_item('Grass', 'grass.svg', GRASS_VALUE))  # přidáme položku do palety
        palette.addItem(self.create_list_widget_item('Wall', 'wall.svg', WALL_VALUE))
        palette.setCurrentRow(1)

    def create_list_widget_item(self, item_label, image_file, role_value):
        item = QtWidgets.QListWidgetItem(item_label)  # vytvoříme položku
        icon = QtGui.QIcon(IMAGE_PATH + image_file)  # ikonu
        item.setIcon(icon)  # přiřadíme ikonu položce

        item.setData(CELL_ROLE, role_value)

        return item

    def new_dialog(self):
        # Vytvoříme nový dialog.
        # V dokumentaci mají dialogy jako argument `this`;
        # jde o "nadřazené" okno
        dialog = QtWidgets.QDialog(self.window)

        # Načteme layout z Qt Designeru
        with open(UI_PATH + 'newmaze.ui') as f:
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
        self.grid.array = numpy.zeros((rows, cols), dtype=numpy.int8)

        # Bludiště může být jinak velké, tak musíme změnit velikost Gridu;
        self.grid.set_size()

        # Překreslení celého Gridu
        self.grid.update()


def pixels_to_logical(x, y):
    return y // CELL_SIZE, x // CELL_SIZE


def logical_to_pixels(row, column):
    return column * CELL_SIZE, row * CELL_SIZE


class GridWidget(QtWidgets.QWidget):
    def __init__(self, array):
        super().__init__()  # musíme zavolat konstruktor předka
        self.array = array
        # nastavíme velikost podle velikosti matice, jinak je náš widget příliš malý
        self.set_size()

    def set_size(self, array=None):
        """
        Set grid size according to self.array, if "array" parameter is None.
        Otherwise set it by "array" parameter.
        """
        if array is not None:
            size = logical_to_pixels(*array.shape)
        else:
            size = logical_to_pixels(*self.array.shape)

        self.setMinimumSize(*size)
        self.setMaximumSize(*size)
        self.resize(*size)

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

                # zdi dáme jen tam, kam patří
                if self.array[row, column] < 0:
                    SVG_WALL.render(painter, rect)

    def mousePressEvent(self, event):
        # převedeme klik na souřadnice matice
        row, column = pixels_to_logical(event.x(), event.y())

        # Pokud jsme v matici, aktualizujeme data
        if 0 <= row < self.array.shape[0] and 0 <= column < self.array.shape[1]:
            if event.button() == QtCore.Qt.LeftButton:
                self.array[row, column] = self.selected
            elif event.button() == QtCore.Qt.RightButton:
                self.array[row, column] = GRASS_VALUE
            else:
                return

            # tímto zajistíme překreslení celého widgetu
            self.update()


def show_gui():
    gui = MazeGUI()

    gui.window.show()
    return gui.app.exec()

show_gui()