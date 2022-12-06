from enum import IntEnum
import numpy as np


class Tile(IntEnum):
    Empty = 0
    Wall = 1
    Block = 2
    Paddle = 3
    Ball = 4


class ArcadeCabinet:
    screen: np.ndarray
    n_commands: int = 0
    x: int = 0
    y: int = 0
    score: int = 0

    def __init__(self):
        self.screen = np.zeros((24, 40), dtype=int)

    def put(self, value):
        if self.n_commands % 3 == 0:
            self.x = value
        elif self.n_commands % 3 == 1:
            self.y = value
        elif self.x == -1:
            self.score = value
        else:
            self.screen[self.y, self.x] = value
        self.n_commands += 1


class JoystickPosition(IntEnum):
    Left = -1
    Neutral = 0
    Right = 1


class RandomJoystick:
    def get(self, **kwargs):
        return np.random.randint(-1, 2)


def main():
    from intcode import Intcode
    cpu = Intcode()
    # TODO: print screen to tty every step, and read joystick from tty
