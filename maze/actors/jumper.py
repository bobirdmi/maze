import random

from .actor import Actor


class Jumper(Actor):
    def __init__(self, grid, row, column, kind, probability=0.2):
        super().__init__(grid, row, column, kind)
        self.probability = probability

    async def behavior(self):
        """Coroutine containing the actor's behavior

        The base implementation follows directions the actor is standing on.
        If there is no directions (e.g. standing on a wall, unreachable space,
        or on the goal), the actor jumps repeatedly.

        To be reimplemented in subclasses..
        """
        while True:
            shape = self.grid.directions.shape
            row = int(self.row)
            column = int(self.column)

            if random.uniform(0, 1) <= self.probability:
                shortest_existed = await self._check_shortest_path(row, column, shape)
                if shortest_existed is not None:
                    # jump over wall
                    self.row, self.column = shortest_existed
                    row = int(self.row)
                    column = int(self.column)

            if 0 <= row < shape[0] and 0 <= column < shape[1]:
                self.direction = self.grid.directions[row, column]
            else:
                self.direction = b'?'

            if self.direction == b'v':
                await self.step(1, 0)
            elif self.direction == b'>':
                await self.step(0, 1)
            elif self.direction == b'^':
                await self.step(-1, 0)
            elif self.direction == b'<':
                await self.step(0, -1)
            elif self.direction == b'X':
                break
            else:
                await self.jump()

    async def _check_shortest_path(self, row, column, shape):
        if row + 2 < shape[0] and self.grid.directions[row + 1, column] == b'#' \
                and self.grid.directions[row + 2, column] != b'#':

            return await self._compare_paths(row + 2, column)

        elif row - 2 >= 0 and self.grid.directions[row - 1, column] == b'#' \
                and self.grid.directions[row - 2, column] != b'#':

            return await self._compare_paths(row - 2, column)

        elif column + 2 < shape[1] and self.grid.directions[row, column + 1] == b'#' \
                and self.grid.directions[row, column + 2] != b'#':

            return await self._compare_paths(row, column + 2)

        elif column - 2 >= 0 and self.grid.directions[row, column - 1] == b'#' \
                and self.grid.directions[row, column - 2] != b'#':

            return await self._compare_paths(row, column - 2)

        else:
            return None

    async def _compare_paths(self, new_row, new_column):
        new_path = self.grid.analyzed_maze.path(new_row, new_column)
        old_path = self.grid.analyzed_maze.path(self.row, self.column)

        if len(old_path) - len(new_path) >= 5:
            self.grid.path_list[self.kind - 2] = new_path
            return new_row, new_column
        else:
            return None
