import numpy as np

from intcode import Intcode

"""
An Intcode peripheral should support asynchronous input/output
with an Intcode machine.

When the CPU runs an Input instruction, it should block or error
based on properties of the peripheral.

When the CPU runs an Output instruction, it should enqueue output
on the peripheral.
There should be a simple interface to view all output as ints or ASCII.
"""

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
