from PyQt5 import QtWidgets, QtGui, QtCore, QtSvg, uic
import numpy


CELL_SIZE = 32
CELL_ROLE = QtCore.Qt.UserRole
WALL_VALUE = -1
GRASS_VALUE = 0

UI_PATH = './gui/'
IMAGE_PATH = './gui/images/'
SVG_GRASS = QtSvg.QSvgRenderer(IMAGE_PATH + 'grass.svg')
SVG_WALL = QtSvg.QSvgRenderer(IMAGE_PATH + 'wall.svg')


def create_list_widget_item(item_label, image_file, role_value):
    item = QtWidgets.QListWidgetItem(item_label)  # vytvoříme položku
    icon = QtGui.QIcon(IMAGE_PATH + image_file)  # ikonu
    item.setIcon(icon)  # přiřadíme ikonu položce

    item.setData(CELL_ROLE, role_value)

    return item


def pixels_to_logical(x, y):
    return y // CELL_SIZE, x // CELL_SIZE


def logical_to_pixels(row, column):
    return column * CELL_SIZE, row * CELL_SIZE


class GridWidget(QtWidgets.QWidget):
    def __init__(self, array):
        super().__init__()  # musíme zavolat konstruktor předka
        self.array = array
        # nastavíme velikost podle velikosti matice, jinak je náš widget příliš malý
        size = logical_to_pixels(*array.shape)
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
            self.array[row, column] = self.selected

            # tímto zajistíme překreslení widgetu v místě změny:
            # (pro Python 3.4 a nižší volejte jen self.update() bez argumentů)
            # self.update(*logical_to_pixels(row, column), CELL_SIZE, CELL_SIZE)
            self.update()


def main():
    app = QtWidgets.QApplication([])

    window = QtWidgets.QMainWindow()

    with open(UI_PATH + 'mainwindow.ui') as f:
        uic.loadUi(f, window)

    # bludiště zatím nadefinované rovnou v kódu
    array = numpy.zeros((15, 20), dtype=numpy.int8)
    array[:, 5] = -1  # nějaká zeď

    # získáme oblast s posuvníky z Qt Designeru
    scroll_area = window.findChild(QtWidgets.QScrollArea, 'scrollArea')

    # dáme do ní náš grid
    grid = GridWidget(array)
    scroll_area.setWidget(grid)

    # získáme paletu vytvořenou v Qt Designeru
    palette = window.findChild(QtWidgets.QListWidget, 'palette')

    def item_activated():
        """Tato funkce se zavolá, když uživatel zvolí položku"""

        # Položek může obecně být vybráno víc, ale v našem seznamu je to
        # zakázáno (v Designeru selectionMode=SingleSelection).
        # Projdeme "všechny vybrané položky", i když víme že bude max. jedna
        for item in palette.selectedItems():
            # print(item.data(CELL_ROLE))
            # grid.selected = item.data(QtCore.Qt.UserRole)
            grid.selected = item.data(CELL_ROLE)

    palette.itemSelectionChanged.connect(item_activated)

    palette.addItem(create_list_widget_item('Grass', 'grass.svg', GRASS_VALUE))  # přidáme položku do palety
    palette.addItem(create_list_widget_item('Wall', 'wall.svg', WALL_VALUE))
    palette.setCurrentRow(1)

    window.show()

    return app.exec()

main()
