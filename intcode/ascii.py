#!/usr/bin/env python3

from intcode import Intcode


def main():
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('program_file', type=argparse.FileType('r'))
    args = parser.parse_args()

    program = [*map(int, args.program_file.read().strip().split(','))]
    args.program_file.close()

    machine = Intcode(program)

    # while sys.stdin.readable():
    #     line = sys.stdin.readline()
    #     for value in line.strip().split(','):
    #         if value:
    #             machine.input.put(value)
    #         else:
    #             break

    output = machine.run()
    for c in output:
        sys.stdout.write(chr(c))


if __name__ == '__main__':
    main()
