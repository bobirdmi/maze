from .grid_widget import GridWidget


class Game:
    def __init__(self, array):
        self.edit_array = array
        self.grid = GridWidget(array)

    @property
    def game_mode(self):
        return self.grid.game_mode

    def check_play(self):
        # TODO
        self.grid.game_mode = not self.grid.game_mode

        self.grid.update()