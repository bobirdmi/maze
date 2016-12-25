from .grid_widget import GridWidget


class Game:
    def __init__(self, array, gui):
        self.edit_array = array
        self.grid = GridWidget(array)
        self.gui = gui

    @property
    def game_mode(self):
        return self.grid.game_mode

    def check_play(self):
        # TODO
        self.grid.game_mode = not self.grid.game_mode

        if self.grid.unreachable:
            self.gui.error_dialog("Error", 'Cannot run the game: there is an unreachable dude')
            return

        if self.game_mode:
            self.gui.hide_palette()
        else:
            self.gui.show_palette()

