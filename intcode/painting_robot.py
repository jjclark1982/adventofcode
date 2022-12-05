import numpy as np

from .intcode import Intcode


class PaintingRobot:
    def __init__(self):
        self.grid = np.zeros((100, 100), dtype=bool)
        self.loc = (50, 50)
        self.direction = (-1, 0)
        self.n_commands = 0

    def get(self, **kwargs):
        return self.grid[self.loc]

    def append(self, command):
        if self.n_commands % 2 == 0:
            # paint current location
            self.grid[self.loc] = command
        else:
            # turn 90 degrees
            pass
        self.n_commands += 1
