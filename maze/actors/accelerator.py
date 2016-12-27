import random

from .actor import Actor


class Accelerator(Actor):
    def __init__(self, grid, row, column, kind, probability=0.1):
        super().__init__(grid, row, column, kind)
        self.probability = probability
        self.speed = 1
        self.speedup = 0.25

    async def step(self, dr, dc, duration=1):
        if random.uniform(0, 1) <= self.probability:
            if self.speed > 0.25:
                self.speed -= self.speedup

            if self.speedup > 0:
                self.speedup -= 0.05

        await super().step(dr, dc, self.speed)