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
    'N': np.array([ 0,-1]),
    'S': np.array([ 0, 1]),
    'E': np.array([ 1, 0]),
    'W': np.array([-1, 0]),
}
rotations = {
    'R': np.matrix([[0, 1], [-1, 0]]),
    'L': np.matrix([[0,-1], [ 1, 0]]),
}


class PaintingRobot:
    def __init__(self):
        self.grid = np.zeros((200, 200), dtype=bool)
        self.heading = translations['N']
        self.loc = np.array([100, 100])
        self.n_commands = 0

    def get(self, **kwargs):
        return self.grid[self.loc]

    def put(self, command):
        if self.n_commands % 2 == 0:
            # paint current location
            self.grid[self.loc] = command
        else:
            # turn 90 degrees
            if command == 0:
                self.heading = np.array(rotations['L'] @ self.heading)[0]
            elif command == 1:
                self.heading = np.array(rotations['R'] @ self.heading)[0]
            # move forward 1 step
            self.loc += self.heading
        self.n_commands += 1
