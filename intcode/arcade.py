#!/usr/bin/env python3

from enum import IntEnum
import numpy as np
import curses
import curses.ascii
import time
from queue import SimpleQueue
import signal
import random


class Tile(IntEnum):
    Empty = 0
    Wall = 1
    Block = 2
    Paddle = 3
    Ball = 4


TILE_SYMBOLS = {
    Tile.Empty: "  ",
    Tile.Wall: "##",
    Tile.Block: "[]",
    Tile.Paddle: "==",
    Tile.Ball: "()"
}


class ArcadeCabinet:
    screen: np.ndarray
    score: int = 0
    n_commands: int = 0
    x: int = 0
    y: int = 0

    def __init__(self, stdscr: curses.window = None):
        self.screen = np.zeros((24, 40), dtype=int)
        self.stdscr = stdscr
        signal.signal(signal.SIGWINCH, self.resize_handler)

    def put(self, value):
        if self.n_commands % 3 == 0:
            self.x = value
        elif self.n_commands % 3 == 1:
            self.y = value
        elif self.x == -1:
            self.score = value
            if self.stdscr:
                # self.stdscr.addstr(23, 0, f"Score: {value}")
                print(f"\033]0;Intcode Arcade – Score: {value}\a")
        else:
            self.screen[self.y, self.x] = value
            self.print_tile(self.y, self.x)

        self.n_commands += 1

    def resize_handler(self, signo, frame=None):
        if self.stdscr:
            curses.endwin()
            self.stdscr = curses.initscr()
            # the following should be signal-safe as it does not call stdscr.refresh()
            self.repaint_screen()

    def repaint_screen(self):
        if self.stdscr:
            for y in range(self.screen.shape[0]):
                s = "".join(TILE_SYMBOLS[tile] for tile in self.screen[y])
                try:
                    self.stdscr.addstr(y, 0, s)
                except curses.error:
                    # tried to write too long a line. perhaps multiple winch signals overlapped.
                    pass

    def print_tile(self, y, x):
        tile_str = TILE_SYMBOLS[self.screen[y, x]]
        if self.stdscr:
            max_y, max_x = self.stdscr.getmaxyx()
            if self.y < max_y and self.x * 2 < max_x-1:
                self.stdscr.addstr(self.y, self.x * 2, tile_str)
                self.stdscr.move(0, 0)
            self.stdscr.refresh()

    def __str__(self):
        return "\n".join([
            "".join(TILE_SYMBOLS[tile] for tile in row)
            for row in self.screen
        ])


class JoystickPosition(IntEnum):
    Left = -1
    Neutral = 0
    Right = 1


class RandomJoystick:
    def __init__(self, delay=0.0):
        self.delay = delay

    def get(self, **kwargs):
        time.sleep(self.delay)
        return random.choice([*JoystickPosition])


class DefaultQueue(SimpleQueue):
    def __init__(self, default=None, delay=0.0):
        super().__init__()
        self.default = default
        self.delay = delay

    def get(self, **kwargs):
        if self.empty():
            time.sleep(self.delay)
            return self.default
        else:
            return super().get(**kwargs)


class TTYJoystick:
    def __init__(self, stdscr, delay=50):
        stdscr.timeout(delay)
        self.stdscr = stdscr

    def get(self):
        key = self.stdscr.getch()
        value = self.parse_keyboard_input(key)
        return value

    @staticmethod
    def parse_keyboard_input(key):
        if key in [curses.KEY_EXIT, curses.KEY_BACKSPACE, curses.ascii.BS, curses.ascii.DEL, curses.ascii.ESC]:
            return None
        if key in [curses.KEY_LEFT, ord("A"), ord("a"), ord("H"), ord("h")]:
            return JoystickPosition.Left
        elif key in [curses.KEY_RIGHT, ord("D"), ord("d"), ord("L"), ord("l")]:
            return JoystickPosition.Right
        else:
            return JoystickPosition.Neutral


def run_in_tty(stdscr: curses.window):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('program_file', type=argparse.FileType('r'))
    parser.add_argument('--random', action="store_true")
    args = parser.parse_args()
    program = [*map(int, args.program_file.read().strip().split(','))]

    from intcode import Intcode

    if args.random:
        joystick = RandomJoystick(delay=0.025)
    else:
        joystick = TTYJoystick(stdscr)
    cabinet = ArcadeCabinet(stdscr)
    cpu = Intcode(program=program, input=joystick, output=cabinet)
    try:
        cpu.run()
        # await any key to quit
        # stdscr.getch()
        # stdscr.clear()

    except KeyboardInterrupt:
        # exit immediately
        pass

    return cabinet.score


def main():
    from curses import wrapper
    score = wrapper(run_in_tty)
    print(f"Score: {score}")


if __name__ == "__main__":
    main()
