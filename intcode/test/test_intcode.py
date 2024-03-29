from unittest import TestCase

from intcode import Intcode, Memory, ParameterMode, Parameter, Instruction, Operator, Output, MachineState
from queue import Queue


class TestOperator(TestCase):
    def test_invalid(self):
        with self.subTest(msg="should instantiate without error"):
            op = Operator(0)
        with self.subTest("should error when trying to execute"):
            with self.assertRaises(ValueError):
                op.operate(machine=None)

    def test_load_from_opcode(self):
        operations = Operator.__subclasses__()
        self.assertGreater(len(operations), 0)
        for cls in Operator.__subclasses__():
            with self.subTest(msg=f"{cls.opcode} {cls.__name__}"):
                op = Operator.from_opcode(cls.opcode)
                self.assertIsNotNone(op.name())
                self.assertTrue(callable(op.operate))

    def test_instantiate_from_class(self):
        operations = Operator.__subclasses__()
        self.assertGreater(len(operations), 0)
        for cls in Operator.__subclasses__():
            with self.subTest(msg=f"{cls.opcode} {cls.__name__}"):
                op = cls()
                self.assertIsInstance(op, cls)


class TestInstruction(TestCase):
    def test_instantiate(self):
        instr = Instruction(1, 2, 3, 4)
        self.assertIsInstance(instr, Instruction)


class TestParameter(TestCase):
    def test_position_mode(self):
        memory = Memory([1, 2, 3])
        param = Parameter(1, ParameterMode.Position)
        self.assertEqual(memory[param], 2)

    def test_immediate_mode(self):
        memory = Memory([1, 2, 3])
        param = Parameter(1, ParameterMode.Immediate)
        self.assertEqual(memory[param], 1)

    def test_relative_mode(self):
        memory = Memory([1, 2, 3], relative_base=1)
        param = Parameter(1, ParameterMode.Relative)
        self.assertEqual(memory[param], 3)


class TestProgram(TestCase):
    def check_program(self, program=[], input=[], expected_memory=None, expected_output=None):
        machine = Intcode(program, input=input)
        with self.subTest(msg="program runs without error"):
            machine.run()
        if expected_output is not None:
            with self.subTest(msg="output matches expectation"):
                output = machine.output_values()
                self.assertListEqual(output, expected_output)
        if expected_memory is not None:
            with self.subTest(msg="resulting memory matches expectation"):
                self.assertListEqual(machine.memory.data, expected_memory)

    def test_empty_program(self):
        self.check_program([])

    def test_halt(self):
        self.check_program([99])

    def test_add(self):
        self.check_program(
            program=[1,9,10,3,2,3,11,0,99,30,40,50],
            expected_memory=[3500,9,10,70,2,3,11,0,99,30,40,50]
        )

    def test_multiply(self):
        self.check_program(
            program=[2,3,0,3,99],
            expected_memory=[2,3,0,6,99]
        )

    def test_dynamic_decode(self):
        self.check_program(
            program=[1,1,1,4,99,5,6,0,99],
            expected_memory=[30,1,1,4,2,5,6,0,99]
        )

    def test_jump_position(self):
        self.check_program(
            program=[3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9],
            input=[1],
            expected_output=[1]
        )

    def test_jump_immediate(self):
        self.check_program(
            program=[3,3,1105,-1,9,1101,0,0,12,4,12,99,1],
            input=[1],
            expected_output=[1]
        )

    def test_jump(self):
        self.check_program(
            program=[3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,
1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,
999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99],
            input=[8],
            expected_output=[1000]
        )

    def test_quine(self):
        program = [109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99]
        self.check_program(
            program=program,
            expected_output=program
        )

    def test_64bit_mult(self):
        self.check_program(
            program=[1102,34915192,34915192,7,4,7,99,0],
            expected_output=[1219070632396864]
        )

    def test_64bit_output(self):
        self.check_program(
            program=[104,1125899906842624,99],
            expected_output=[1125899906842624]
        )


class TestPause(TestCase):
    def test_pause_on_blocked_input(self):
        cpu = Intcode([3, 4, 99], io_timeout=0.01)
        with self.subTest(msg="pause"):
            cpu.run()
            self.assertEqual(cpu.state, MachineState.Blocked)
        with self.subTest(msg="resume"):
            cpu.input.put(1)
            cpu.run()
            self.assertEqual(cpu.state, MachineState.Halted)

    def test_pause_on_blocked_output(self):
        cpu = Intcode([104, 1, 104, 1, 99], output=Queue(maxsize=1), io_timeout=0.01)
        with self.subTest(msg="pause"):
            cpu.run()
            self.assertEqual(cpu.state, MachineState.Blocked)
        with self.subTest(msg="resume"):
            cpu.output.get()
            cpu.run()
            self.assertEqual(cpu.state, MachineState.Halted)

    def test_pause_on_ready_output(self):
        cpu = Intcode([104, 1, 99], io_timeout=0.01)
        with self.subTest(msg="pause"):
            cpu.run(pause_on_output=True)
            self.assertEqual(cpu.state, MachineState.Paused)
        with self.subTest(msg="resume"):
            cpu.output.get()
            cpu.run()
            self.assertEqual(cpu.state, MachineState.Halted)
