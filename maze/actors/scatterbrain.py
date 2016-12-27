import random

from .actor import Actor


DIRS = [b'<', b'>', b'^', b'v']


class Scatterbrain(Actor):
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
            if 0 <= row < shape[0] and 0 <= column < shape[1]:
                self.direction = self.grid.directions[row, column]
            else:
                self.direction = b'?'

            if random.uniform(0, 1) <= self.probability:
                # go in random direction, but not by computed path
                dirs = list(DIRS)

                if row + 1 >= shape[0] or self.grid.directions[row + 1, column] == b'#':
                    dirs.remove(b'v')
                if row - 1 < 0 or self.grid.directions[row - 1, column] == b'#':
                    dirs.remove(b'^')
                if column + 1 >= shape[1] or self.grid.directions[row, column + 1] == b'#':
                    dirs.remove(b'>')
                if column - 1 < 0 or self.grid.directions[row, column - 1] == b'#':
                    dirs.remove(b'<')

                if len(dirs) > 1 and self.direction in dirs:
                    dirs.remove(self.direction)

                index = random.randrange(0, len(dirs))

                self.direction = dirs[index]

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

