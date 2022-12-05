from unittest import TestCase
from subprocess import Popen, PIPE
from pathlib import Path


class TestCLI(TestCase):
    def test_import(self):
        from intcode.cli import main as cli_main
        self.assertIsNotNone(cli_main)

    def test_hello_world(self):
        cli_path = Path(__file__).parent.parent / 'cli.py'
        hello_world_path = Path(__file__).parent / 'hello_world.ints'

        process = Popen([cli_path, hello_world_path], stdin=PIPE, stdout=PIPE)
        out, err = process.communicate()
        if process.returncode:
            raise RuntimeError('something bad happened')
        self.assertEqual(out, b"Hello, world!\n")
