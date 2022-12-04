from unittest import TestCase

from intcode import Intcode, Operation, ParameterMode, Parameter, Instruction


class TestOperation(TestCase):
    def test_invalid(self):
        op = Operation(0)

    def test_instantiate_from_code(self):
        operations = Operation.__subclasses__()
        self.assertGreater(len(operations), 0)
        for cls in Operation.__subclasses__():
            with self.subTest(msg=f"{cls.opcode} {cls.__name__}"):
                op = Operation(cls.opcode)
                self.assertTrue(isinstance(op, cls))

    def test_instantiate_from_class(self):
        operations = Operation.__subclasses__()
        self.assertGreater(len(operations), 0)
        for cls in Operation.__subclasses__():
            with self.subTest(msg=f"{cls.opcode} {cls.__name__}"):
                op = cls()
                self.assertTrue(isinstance(op, cls))


class TestParameter(TestCase):
    def test_position_mode(self):
        state = Intcode([1,2,3])
        param = Parameter(1, ParameterMode.Position)
        self.assertEqual(state[param], 2)

    def test_immediate_mode(self):
        state = Intcode([1, 2, 3])
        param = Parameter(1, ParameterMode.Immediate)
        self.assertEqual(state[param], 1)

    def test_relative_mode(self):
        state = Intcode([1, 2, 3])
        state.relative_base = 1
        param = Parameter(1, ParameterMode.Relative)
        self.assertEqual(state[param], 3)


class TestIntcode(TestCase):
    def test_halt(self):
        state = Intcode([99])
        state.run()

    def test_add(self):
        program = [1,9,10,3,2,3,11,0,99,30,40,50]
        state = Intcode(program)
        state.run()
        expected_result = [3500,9,10,70,2,3,11,0,99,30,40,50]
        self.assertListEqual(state.memory, expected_result)

    def test_quine(self):
        program = [109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99]
        state = Intcode(program)
        state.run()
        self.assertListEqual(state.output, program)