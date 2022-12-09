from queue import SimpleQueue
from typing import List, Tuple, Union, Iterator, Generator, Optional
from enum import Enum, IntEnum
from threading import Thread


class MachineState(Enum):
    Paused = 1
    Running = 2
    Blocked = 3
    Halted = 4


class Intcode:
    """
    An Intcode machine consists of:
    - memory, initialized with a program
    - program counter, pointing to an address of memory
    - input/output queues
    - other devices

    Usage: Intcode(program).run(input=[...]).output
    """
    memory: List[int]
    relative_base: int = 0
    pc: int = 0
    state: MachineState = MachineState.Paused
    num_cycles: int = 0
    input: Union[SimpleQueue, Iterator, Generator]
    output: SimpleQueue
    breakpoints: set
    _thread: Thread

    def __init__(self, program: List[int], input=None, output=None, breakpoints=None, **kwargs):
        self.memory = list(program)

        if input is None:
            self.input = SimpleQueue()
        elif callable(getattr(input, '__next__', None)):
            self.input = input
        elif callable(getattr(input, '__iter__', None)):
            self.input = iter(input)
        else:
            self.input = input

        if output is None:
            output = SimpleQueue()
        self.output = output

        if breakpoints is None:
            breakpoints = set()
        self.breakpoints = breakpoints

        self.__dict__.update(kwargs)
        
    def __str__(self):
        lines = [
            f"{[' ', '>'][int(addr == self.pc)]}{addr: 4d}: {i}" for addr, i in self.all_instructions()
        ]
        return '\n'.join(lines)
    
    def __repr__(self):
        return f"<Intcode pc:{self.pc}/{len(self.memory)} cycles:{self.num_cycles} state:{self.state.name}>"
    
    def __getitem__(self, key: Union[int, slice, "Parameter"]) -> int:
        # Handle loading a slice of memory
        if type(key) is slice:
            return [self[i] for i in range(key.start, key.stop + 1, key.step or 1)]
        # Handle loading a single memory address
        elif type(key) is int:
            addr = key
        # Handle loading specific parameter types
        elif key.mode == ParameterMode.Immediate:
            return key.value
        elif key.mode == ParameterMode.Position:
            addr = key.value
        elif key.mode == ParameterMode.Relative:
            addr = key.value + self.relative_base
        else:
            raise NotImplementedError(f"Unsupported memory address {key}")

        if addr >= len(self.memory):
            return 0
        return self.memory[addr]
        
    def __setitem__(self, key: Union[int, "Parameter"], value: int):
        if type(key) is int:
            addr = key
        elif key.mode == ParameterMode.Position:
            addr = key.value
        elif key.mode == ParameterMode.Relative:
            addr = key.value + self.relative_base
        else:
            raise NotImplementedError(f"Unsupported ParameterMode {key.mode}")

        # Expand memory as needed (slow for very high addresses)
        while len(self.memory) <= addr:
            self.memory.append(0)
        self.memory[addr] = value

    def instruction_at(self, address: int) -> "Instruction":
        return Instruction(*self[address:address+3])
    
    def all_instructions(self) -> List[Tuple[int, "Instruction"]]:
        instructions = []
        pc = 0
        while pc < len(self.memory):
            instr = self.instruction_at(pc)
            instructions.append((pc, instr))
            pc += instr.width
        return instructions
    
    def step(self, verbose=False):
        instruction = self.instruction_at(self.pc)
        if verbose:
            print(f"{self.pc: 6d}: {instruction}")
        self.pc += instruction.width
        instruction.run(self)
        self.num_cycles += 1

    def run(self, pc=None, verbose=False, pause_on_output=False):
        if pc is not None:
            self.pc = pc
        self.state = MachineState.Running
        while self.state == MachineState.Running:
            if self.pc >= len(self.memory):
                self.state = MachineState.Halted

            elif self.pc in self.breakpoints:
                self.state = MachineState.Paused

            elif pause_on_output and not self.output.empty():
                self.state = MachineState.Paused

            else:
                self.step(verbose=verbose)

        return self

    def run_in_thread(self):
        self._thread = Thread(target=self.run)
        self._thread.start()
        return self._thread

    def join(self):
        self._thread.join()

    def output_values(self):
        values = []
        while not self.output.empty():
            values.append(self.output.get())
        if isinstance(self.output, SimpleQueue):
            for val in values:
                self.output.put(val)
        return values

    def output_str(self):
        return ''.join(map(chr, self.output_values()))

    def fork(self, **kwargs):
        return Intcode(program=self.memory.copy(), relative_base=self.relative_base, pc=self.pc, **kwargs)


class ParameterMode(IntEnum):
    Position = 0
    Immediate = 1
    Relative = 2

    def __str__(self):
        return ["*", " ", "+"][self.value]


class Parameter:
    """
    A Parameter is a combination of referencing mode and value.
    It is used as the argument to Intcode indexing.
    For example, Intcode([102, 3, 4, 5])[Parameter(1)] == 3
    """

    def __init__(self, value: int, mode: int = 0):
        if isinstance(value, Parameter):
            self.value = value.value
            self.mode = ParameterMode(value.mode)
        else:
            self.value = value
            self.mode = ParameterMode(mode)

    def __str__(self):
        return f"{str(self.mode)}{self.value}".rjust(4, " ")


class Instruction:
    """
    An Instruction is a concrete instance of an operation and its parameters
    """

    value: int
    parameters: List[Parameter]

    @property
    def width(self):
        return self.operator.num_params + 1

    @staticmethod
    def decode(instruction: int) -> Tuple[int, List[int]]:
        opcode = instruction % 100
        modes = (
            (instruction // 100) % 10,
            (instruction // 1000) % 10,
            (instruction // 10000) % 10
        )
        return opcode, modes

    def __init__(self, value: int, *param_values: Tuple[int]):
        self.value = value
        opcode, self.modes = self.decode(value)
        self.operator = Operator(opcode)
        self.parameters = []
        for i in range(self.operator.num_params):
            if i >= len(param_values):
                value = 0
            else:
                value = param_values[i]
            mode = self.modes[i]
            self.parameters.append(Parameter(value, mode))

    def __str__(self):
        parts = [self.operator.name().ljust(18)] + [*map(str, self.parameters)]
        return ' '.join(parts)

    def __repr__(self):
        args = [self.value] + [p.value for p in self.parameters]
        return f"Instruction({', '.join(str(a) for a in args)})"

    def run(self, machine: Intcode):
        self.operator.operate(machine, *self.parameters)


class Operator:
    opcode: Optional[int] = None
    num_params: int = 0
    _by_opcode = {}

    def __new__(cls, opcode: int = None):
        """
        Operator(opcode) returns an object or class with an operate() method.
        """
        if cls is Operator:
            OpClass = Operator.from_opcode(opcode)
            if OpClass.opcode is not None:
                return OpClass
        return super().__new__(cls)

    def __init_subclass__(cls, **kwargs):
        Operator._by_opcode[cls.opcode] = cls

    @staticmethod
    def from_opcode(opcode) -> type:
        return Operator._by_opcode.get(opcode, NoOp)

    @classmethod
    def name(cls):
        return cls.__name__

    def operate(self, machine: Intcode, *params: Tuple[Parameter, ...]):
        raise ValueError(f"Invalid instruction with opcode {self.opcode}")


class NoOp(Operator):
    opcode = None
    num_params = 0

    def name(self=None):
        return str((self or NoOp).opcode)

    def __init__(self, opcode=None):
        self.opcode = opcode


class Add(Operator):
    opcode = 1
    num_params = 3

    @staticmethod
    def operate(machine: Intcode, lhs: Parameter, rhs: Parameter, result: Parameter):
        machine[result] = machine[lhs] + machine[rhs]


class Multiply(Operator):
    opcode = 2
    num_params = 3

    @staticmethod
    def operate(machine: Intcode, lhs: Parameter, rhs: Parameter, result: Parameter):
        machine[result] = machine[lhs] * machine[rhs]


class Input(Operator):
    opcode = 3
    num_params = 1

    @staticmethod
    def operate(machine: Intcode, result: Parameter):
        if callable(getattr(machine.input, '__next__', None)):
            value = next(machine.input)
        else:
            value = machine.input.get()

        machine[result] = value


class Output(Operator):
    opcode = 4
    num_params = 1

    @staticmethod
    def operate(machine: Intcode, param: Parameter):
        value = machine[param]
        machine.output.put(value)
        if machine.pause_on_output:
            machine.state = MachineState.Paused


class JumpIfTrue(Operator):
    opcode = 5
    num_params = 2

    @staticmethod
    def operate(machine: Intcode, test: Parameter, addr: Parameter):
        if machine[test] != 0:
            machine.pc = machine[addr]


class JumpIfFalse(Operator):
    opcode = 6
    num_params = 2

    @staticmethod
    def operate(machine: Intcode, test: Parameter, addr: Parameter):
        if machine[test] == 0:
            machine.pc = machine[addr]


class LessThan(Operator):
    opcode = 7
    num_params = 3

    @staticmethod
    def operate(machine, lhs: Parameter, rhs: Parameter, result: Parameter):
        machine[result] = int(machine[lhs] < machine[rhs])


class Equals(Operator):
    opcode = 8
    num_params = 3

    @staticmethod
    def operate(machine, lhs: Parameter, rhs: Parameter, result: Parameter):
        machine[result] = int(machine[lhs] == machine[rhs])


class AdjustRelativeBase(Operator):
    opcode = 9
    num_params = 1

    @staticmethod
    def operate(machine: Intcode, value: Parameter):
        machine.relative_base += machine[value]


class Halt(Operator):
    opcode = 99
    num_params = 0

    @staticmethod
    def operate(machine: Intcode):
        machine.state = MachineState.Halted


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('program_file', type=argparse.FileType('r'))
    args = parser.parse_args()

    program = [*map(int, args.program_file.read().strip().split(','))]
    args.program_file.close()

    machine = Intcode(program)

    output = machine.run()
    print(''.join([*map(chr, output)]))


if __name__ == '__main__':
    main()
