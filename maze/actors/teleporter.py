import random
import numpy
import asyncio

from .actor import Actor


class Teleporter(Actor):
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

            if random.uniform(0, 1) <= self.probability:
                # teleportation!
                await self.teleport()
                await self.teleport()

                self.row, self.column = await self._get_random_coord(shape)

                await self.teleport()
                await self.teleport()

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

    async def _get_random_coord(self, shape):
        castle_pos = numpy.where(self.grid.array == 1)
        castle_row = castle_pos[0][0]
        castle_column = castle_pos[1][0]

        while True:
            new_row = random.randrange(0, shape[0])
            new_column = random.randrange(0, shape[1])

            # teleportation cannot be closer to castle than 5 tiles
            if (abs(new_column - castle_column) >= 5 or abs(new_row - castle_row) >= 5) \
                    and self.grid.directions[new_row, new_column] != b'#':
                break

        return new_row, new_column

    async def teleport(self, duration=0.1):
        """Coroutine for a teleport

        Smoothly moves a bit diagonal (top left and center) in ``duration`` seconds.
        """
        start_column = self.column
        start_row = self.row

        for p in self._progress(duration):
            with self._update_context():
                # vibrate along a parabola
                self.column = start_column - p * (1 - p)
                self.row = start_row - p * (1 - p)

            await asyncio.sleep(duration / self.grid.cell_size * 2)

        with self._update_context():
            self.column = start_column
            self.row = start_row

