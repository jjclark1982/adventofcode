#!/usr/bin/env python3

import sys


class ASCIIPeripheral:
    pass


class CLIPeripheral:
    def __iter__(self):
        while sys.stdin.readable():
            line = sys.stdin.readline()
            for value in line.strip().split(','):
                if value:
                    yield int(value)
                else:
                    break

    @staticmethod
    def put(value, **kwargs):
        sys.stdout.write(chr(value))
        sys.stdout.flush()


def main():
    from intcode import Intcode
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('program_file', type=argparse.FileType('r'))
    args = parser.parse_args()

    program = [*map(int, args.program_file.read().strip().split(','))]
    args.program_file.close()

    cli = CLIPeripheral()
    machine = Intcode(program, input=cli, output=cli)
    machine.run()


if __name__ == '__main__':
    main()
