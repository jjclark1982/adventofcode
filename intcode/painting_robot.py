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

translations = {
    'W': np.array([ 0,-1]),
    'E': np.array([ 0, 1]),
    'S': np.array([ 1, 0]),
    'N': np.array([-1, 0]),
}
rotations = {
    'R': np.matrix([[0, 1], [-1, 0]]),
    'L': np.matrix([[0,-1], [ 1, 0]]),
}


class PaintingRobot:
    def __init__(self):
        self.color = np.zeros((256, 256), dtype=bool)
        self.count = np.zeros((256, 256), dtype=int)
        self.heading = translations['N']
        self.loc = (128, 128)
        self.n_commands = 0

    def get(self, **kwargs):
        return self.color[self.loc]

    def put(self, command):
        if self.n_commands % 2 == 0:
            # paint current location
            self.color[self.loc] = command
            self.count[self.loc] += 1
        else:
            # turn 90 degrees
            if command == 0:
                self.heading = np.array(rotations['L'] @ self.heading)[0]
            elif command == 1:
                self.heading = np.array(rotations['R'] @ self.heading)[0]
            # move forward 1 step
            self.loc = tuple(self.heading + self.loc)
        self.n_commands += 1
