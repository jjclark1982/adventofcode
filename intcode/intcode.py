from collections import deque
from typing import List, Tuple, Iterable
from enum import IntEnum


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
    halted: bool = False
    num_cycles: int = 0
    output = []

    def __init__(self, program: List[int], input:Iterable=None, output=None):
        self.memory = list(program)
        if input is None:
            input = []
        self.input = iter(input)
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
        return f"<Intcode pc:{self.pc}/{len(self.memory)} in:{len(self.input)} out:{self.output}>"
    
    def __getitem__(self, param: "Parameter") -> int:
        # Handle dereferencing a param or using an immediate value
        param = Parameter(param)
        if param.mode == ParameterMode.Immediate:
            return param.value
        elif param.mode == ParameterMode.Position:
            addr = param.value
        elif param.mode == ParameterMode.Relative:
            addr = param.value + self.relative_base
        else:
            raise NotImplementedError("Unsupported ParameterMode")
        if addr >= len(self.memory):
            return 0
        return self.memory[addr]
        
    def __setitem__(self, param: "Parameter", value: int):
        if param.mode == ParameterMode.Position:
            addr = param.value
        elif param.mode == ParameterMode.Relative:
            addr = param.value + self.relative_base
        else:
            raise NotImplementedError("Unsupported ParameterMode")
        while len(self.memory) <= addr:
            self.memory.append(0)
        self.memory[addr] = value

    def instruction_at(self, address: int) -> "Instruction":
        return Instruction(self.memory, address)
    
    def next_instruction(self) -> "Instruction":
        return self.instruction_at(self.pc)
    
    def all_instructions(self) -> List["Instruction"]:
        instrs = []
        pc = 0
        while pc < len(self.memory):
            instr = self.instruction_at(pc)
            instrs.append((pc, instr))
            pc += instr.width
        return instrs
    
    def run_instruction(self, instr: "Instruction"):
        instr.run(self)

    def step(self, verbose=False):
        instr = self.instruction_at(self.pc)
        if verbose:
            print(f"{self.pc: 6d}: {instr}")
        self.pc += instr.width
        self.run_instruction(instr)
        self.num_cycles += 1
    
    def run(self, input=None, pc=None, verbose=False):
        if input:
            self.input = deque(input)
        if pc is not None:
            self.pc = pc
        while self.pc < len(self.memory):
            self.step(verbose=verbose)
            if self.pc in self.breakpoints:
                break
            if self.halted:
                break
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
    """An Operation is an abstract form of something the machine can do."""
    
    opcode = None
    num_params = 0

    def __init__(self, opcode=None):
        if opcode is not None:
            self.opcode = opcode
            OpClass = self.from_opcode(opcode)
            if OpClass:
                self.__class__ = OpClass

    def __str__(self):
        if self.__class__ is Operation:
            return str(self.opcode)
        return self.__class__.__name__.ljust(18)
    
    def operate(self, state: Intcode, **params):
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

    def operate(self, state: Intcode, lhs: Parameter, rhs: Parameter, result: Parameter):
        state[result] = state[lhs] + state[rhs]


class Multiply(Operation):
    opcode = 2
    num_params = 3

    def operate(self, state: Intcode, lhs: Parameter, rhs: Parameter, result: Parameter):
        state[result] = state[lhs] * state[rhs]


class Input(Operation):
    opcode = 3
    num_params = 1

    def operate(self, state: Intcode, result: Parameter):
        state[result] = next(state.input)


class Output(Operation):
    opcode = 4
    num_params = 1

    def operate(self, state: Intcode, param: Parameter):
        state.output.append(state[param])


class JumpIfTrue(Operation):
    opcode = 5
    num_params = 2

    def operate(self, state: Intcode, test: Parameter, addr: Parameter):
        if state[test] != 0:
            state.pc = state[addr]


class JumpIfFalse(Operation):
    opcode = 6
    num_params = 2

    def operate(self, state: Intcode, test: Parameter, addr: Parameter):
        if state[test] == 0:
            state.pc = state[addr]


class LessThan(Operation):
    opcode = 7
    num_params = 3

    def operate(self, state, lhs: Parameter, rhs: Parameter, result: Parameter):
        state[result] = int(state[lhs] < state[rhs])


class Equals(Operation):
    opcode = 8
    num_params = 3

    def operate(self, state, lhs: Parameter, rhs: Parameter, result: Parameter):
        state[result] = int(state[lhs] == state[rhs])


class AdjustRelativeBase(Operation):
    opcode = 9
    num_params = 1

    def operate(self, state: Intcode, value: Parameter):
        state.relative_base += state[value]


class Halt(Operation):
    opcode = 99
    num_params = 0

    def operate(self, state: Intcode):
        state.halted = True


class Instruction(object):
    """An Instruction is a concrete instance of an Operation and its parameters"""

    value: int
    operation: Operation
    parameters: List[Parameter]
    width: int = 1

    def __init__(self, mem: List[int], addr: int):
        self.value = mem[addr]
        opcode, modes = self.decode(self.value)
        self.operation = Operation(opcode)
        if self.operation:
            param_values = mem[addr + 1: addr + 1 + self.operation.num_params]
        else:
            param_values = []

        self.params = []
        for i in range(len(param_values)):
            value = param_values[i]
            mode = modes[i]
            self.params.append(Parameter(value, mode))

        self.width = 1 + len(self.params)

    def __str__(self):
        param_strs = [str(p) for p in self.params]
        if self.operation:
            return ' '.join([str(self.operation)] + param_strs)
        else:
            return f"{self.value}"

    def __repr__(self):
        return f"[{self}]"

    def run(self, machine: Intcode):
        self.operation.operate(machine, *self.params)

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
