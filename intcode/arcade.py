#!/usr/bin/env python3

from enum import IntEnum
import numpy as np
import curses
import time


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

    def __init__(self, stdscr=None):
        self.screen = np.zeros((24, 40), dtype=int)
        self.stdscr = stdscr

    def put(self, value):
        if self.n_commands % 3 == 0:
            self.x = value
        elif self.n_commands % 3 == 1:
            self.y = value
        elif self.x == -1:
            self.score = value
            if self.stdscr:
                self.stdscr.addstr(23, 0, f"Score: {value}")
        else:
            self.screen[self.y, self.x] = value
            if self.stdscr:
                tile_str = ["  ", "##", "[]", "==", "()"][value]
                self.stdscr.addstr(self.y, self.x*2, tile_str)
                self.stdscr.move(0,0)
                self.stdscr.refresh()
        self.n_commands += 1


class JoystickPosition(IntEnum):
    Left = -1
    Neutral = 0
    Right = 1


class RandomJoystick:
    def __init__(self, delay=0.0):
        self.delay = delay

    def get(self, **kwargs):
        time.sleep(self.delay)
        return np.random.randint(-1, 2)


class TTYJoystick:
    def __init__(self, stdscr):
        self.stdscr = stdscr

    def get(self):
        key = self.stdscr.getch()
        if key in [curses.KEY_LEFT, ord("A"), ord("a"), ord("H"), ord("h")]:
            return JoystickPosition.Left
        elif key in [curses.KEY_RIGHT, ord("D"), ord("d"), ord("L"), ord("l")]:
            return JoystickPosition.Right
        else:
            return JoystickPosition.Neutral


def run_in_tty(stdscr):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('program_file', type=argparse.FileType('r'))
    parser.add_argument('--random', action="store_true")
    args = parser.parse_args()
    program = [*map(int, args.program_file.read().strip().split(','))]

    from intcode import Intcode, MachineState

    if args.random:
        joystick = RandomJoystick(delay=0.025)
    else:
        joystick = TTYJoystick(stdscr)
    cabinet = ArcadeCabinet(stdscr)
    cpu = Intcode(program=program, input=joystick, output=cabinet)
    cpu.run()

    # await any key to quit
    stdscr.getch()


def main():
    from curses import wrapper
    wrapper(run_in_tty)


if __name__ == "__main__":
    main()
