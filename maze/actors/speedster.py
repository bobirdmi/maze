from .actor import Actor


class Speedster(Actor):
    def __init__(self, grid, row, column, kind):
        super().__init__(grid, row, column, kind)

    async def step(self, dr, dc, duration=0.5):
        await super().step(dr, dc, duration)