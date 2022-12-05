from queue import SimpleQueue
from typing import List, Tuple, Iterable, Union
from enum import Enum, IntEnum


class MachineState(Enum):
    Paused = 1
    Running = 2
    Blocked = 3
    Halted = 4


class Intcode(object):
    """
    An Intcode machine consists of:
    - memory, initialized with a program
    - program counter, pointing to an address of memory
    - input/output queues
    - other devices

    Usage: Intcode(program).run(input=[...]).output
    """
    memory: List[int]
    pc: int = 0
    relative_base: int = 0
    state: MachineState = MachineState.Paused
    num_cycles: int = 0
    input: SimpleQueue
    output: List[int]

    def __init__(self, program: List[int], input:Iterable=None, output=None):
        self.memory = list(program)
        if callable(getattr(input, 'get', None)):
            self.input = input
        else:
            self.input = SimpleQueue()
        if callable(getattr(input, '__iter__', None)):
            for i in input:
                self.input.put(i)

        if output is None:
            output = []
        self.output = output
        self.breakpoints = set()
        
    def __str__(self):
        lines = [
            f"{[' ', '>'][int(addr == self.pc)]}{addr: 4d}: {i}" for addr, i in self.all_instructions()
        ]
        return '\n'.join(lines)
    
    def __repr__(self):
        return f"<Intcode pc:{self.pc}/{len(self.memory)} in:{self.input.qsize()} out:{self.output}>"
    
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
    
    def run(self, pc=None, verbose=False):
        if pc is not None:
            self.pc = pc
        self.state = MachineState.Running
        while self.state == MachineState.Running:
            if self.pc >= len(self.memory):
                self.state = MachineState.Halted

            elif self.pc in self.breakpoints:
                self.state = MachineState.Paused

            else:
                self.step(verbose=verbose)

        return self.output


class ParameterMode(IntEnum):
    Position = 0
    Immediate = 1
    Relative = 2

    def __str__(self):
        return ["*", " ", "+"][self.value]


class Parameter(object):
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


class Operation(object):
    """
    An Operation is an abstract form of something the machine can do.
    """
    
    opcode = None
    num_params = 0

    def __init__(self, opcode=None):
        if opcode is not None:
            self.opcode = opcode
            OpClass = self.from_opcode(opcode)
            if OpClass:
                self.__class__ = OpClass

    def __repr__(self):
        if self.__class__ is Operation:
            return f"{self.__class__.__name__}({self.opcode})"
        else:
            return f"{self.__class__.__name__}()"

    def __str__(self):
        return self.name.ljust(18)

    @property
    def name(self):
        if self.__class__ is Operation:
            return str(self.opcode)
        else:
            return self.__class__.__name__
    
    def operate(self, machine: Intcode, **params):
        raise ValueError(f"Invalid instruction with opcode {self.opcode}")
    
    @classmethod
    def width(cls):
        return 1 + cls.num_params
    
    @classmethod
    def from_opcode(cls, opcode) -> type:
        operations = {}
        for item in cls.__subclasses__():
            if type(item) == type and issubclass(item, cls):
                operations[item.opcode] = item
        if opcode in operations:
            return operations[opcode]


class Add(Operation):
    opcode = 1
    num_params = 3

    def operate(self, machine: Intcode, lhs: Parameter, rhs: Parameter, result: Parameter):
        machine[result] = machine[lhs] + machine[rhs]


class Multiply(Operation):
    opcode = 2
    num_params = 3

    def operate(self, machine: Intcode, lhs: Parameter, rhs: Parameter, result: Parameter):
        machine[result] = machine[lhs] * machine[rhs]


class Input(Operation):
    opcode = 3
    num_params = 1

    def operate(self, machine: Intcode, result: Parameter):
        machine[result] = machine.input.get()


class Output(Operation):
    opcode = 4
    num_params = 1

    def operate(self, machine: Intcode, param: Parameter):
        machine.output.append(machine[param])


class JumpIfTrue(Operation):
    opcode = 5
    num_params = 2

    def operate(self, machine: Intcode, test: Parameter, addr: Parameter):
        if machine[test] != 0:
            machine.pc = machine[addr]


class JumpIfFalse(Operation):
    opcode = 6
    num_params = 2

    def operate(self, machine: Intcode, test: Parameter, addr: Parameter):
        if machine[test] == 0:
            machine.pc = machine[addr]


class LessThan(Operation):
    opcode = 7
    num_params = 3

    def operate(self, machine, lhs: Parameter, rhs: Parameter, result: Parameter):
        machine[result] = int(machine[lhs] < machine[rhs])


class Equals(Operation):
    opcode = 8
    num_params = 3

    def operate(self, machine, lhs: Parameter, rhs: Parameter, result: Parameter):
        machine[result] = int(machine[lhs] == machine[rhs])


class AdjustRelativeBase(Operation):
    opcode = 9
    num_params = 1

    def operate(self, machine: Intcode, value: Parameter):
        machine.relative_base += machine[value]


class Halt(Operation):
    opcode = 99
    num_params = 0

    def operate(self, machine: Intcode):
        machine.state = MachineState.Halted


class Instruction(object):
    """
    An Instruction is a concrete instance of an Operation and its parameters
    """

    value: int
    operation: Operation
    parameters: List[Parameter]
    width: int = 1

    def __init__(self, value: int, *param_values: Tuple[int]):
        self.value = value
        opcode, modes = self.decode(self.value)
        self.operation = Operation(opcode)
        self.width = 1 + self.operation.num_params

        self.parameters = []
        for i in range(self.operation.num_params):
            value = param_values[i]
            mode = modes[i]
            self.parameters.append(Parameter(value, mode))

    def __str__(self):
        param_strs = [str(p) for p in self.parameters]
        return ' '.join([str(self.operation)] + param_strs)

    def __repr__(self):
        args = [self.value] + [p.value for p in self.parameters]
        return f"Instruction({', '.join(str(a) for a in args)})"

    def run(self, machine: Intcode):
        self.operation.operate(machine, *self.parameters)

    @staticmethod
    def decode(instruction: int) -> Tuple[int, List[int]]:
        opcode = instruction % 100
        modes = (
            (instruction // 100) % 10,
            (instruction // 1000) % 10,
            (instruction // 10000) % 10
        )
        return opcode, modes


def main():
    import os
    from pathlib import Path

    program_file = Path(os.argv[1])
    with program_file.open() as f:
        program = [*map(int, f.read().strip().split(','))]
    machine = Intcode(program)
    # TODO: take input from stdin
    output = machine.run()
    print(output)


if __name__ == '__main__':
    main()
