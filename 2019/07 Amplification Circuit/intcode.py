from collections import deque
from typing import List, Tuple
from enum import IntEnum

# would like to write:
# Intcode(program).run(input).output

class Intcode(object):
    """An Intcode machine holds the state of a program, its memory and i/o"""
    def __init__(self, program: List[int], input=[]):
        self.mem = list(program)
        self.halted = False
        self.input = deque(input)
        self.output = []
        self.pc = 0
        
    def __str__(self):
        lines = [
            f"{[' ', '>'][int(addr == self.pc)]}{addr: 4d}: {i}" for addr, i in self.all_instructions()
        ]
        return '\n'.join(lines)
    
    def __repr__(self):
        return f"<Intcode pc:{self.pc}/{len(self.mem)} in:{len(self.input)} out:{self.output}>"
    
    def __getitem__(self, param: "Param") -> int:
        # Handle dereferencing a param or using an immediate value
        param = Param(param)
        if param.mode == ParamMode.REFERENCE:
            return self.mem[param.value]
        elif param.mode == ParamMode.IMMEDIATE:
            return param.value
        
    def __setitem__(self, addr: "Param", value: int):
        # Always write to the param as an address
        addr = Param(addr)
        self.mem[addr.value] = value

    def instruction_at(self, pc: int) -> "Instruction":
        return Instruction(self.mem, pc)
    
    def next_instruction(self) -> "Instruction":
        return self.instruction_at(self.pc)
    
    def all_instructions(self) -> List["Instruction"]:
        instrs = []
        pc = 0
        while pc < len(self.mem):
            instr = self.instruction_at(pc)
            instrs.append((pc, instr))
            pc += instr.width
        return instrs
    
    def run_instruction(self, instr: "Instruction"):
        instr.OpClass().operate(self, *instr.params)        
    
    def run(self, *input, pc=0, verbose=False):
        if input:
            self.input = deque(input)
        self.pc = pc
        while self.pc < len(self.mem):
            instr = self.instruction_at(self.pc)
            if verbose:
                print(f"{self.pc: 6d}: {instr}")
            self.pc += instr.width
            self.run_instruction(instr)
            if self.halted:
                break
        return self.output


class ParamMode(IntEnum):
    REFERENCE = 0
    IMMEDIATE = 1

    def __str__(self):
        return ["*", "'"][self.value]


class Param(object):
    """
    A Param is a combination of referencing mode and value.
    It is used as the argument to Intcode indexing.
    For example, Intcode([102, 3, 4, 5])[Param(1)] == 3
    """
    def __init__(self, value: int, mode: int = 0):
        if isinstance(value, Param):
            self.value = value.value
            self.mode = ParamMode(value.mode)
        else:
            self.value = value
            self.mode = ParamMode(mode)
    
    def __str__(self):
        return f"{str(self.mode)}{self.value}"


class Instruction(object):
    """An Instruction is a concrete instance of an Operation and its parameters"""
    
    def __init__(self, mem: List[int], pc: int):
        code = mem[pc]
        opcode, modes = self.decode(code)
        OpClass = Operation.from_code(opcode)
        if OpClass:
            params = mem[pc + 1 : pc + 1 + OpClass.num_params]
        else:
            params = []
        self.code = code
        self.OpClass = OpClass

        self.params = []
        for i in range(len(params)):
            param = params[i]
            mode = modes[i]
            self.params.append(Param(param, mode))

        self.width = 1 + len(params)
    
    def __str__(self):
        param_strs = [str(p) for p in self.params]
        if self.OpClass:
            return ' '.join([self.OpClass.__name__] + param_strs)
        return f"{self.code}"
    
    def __repr__(self):
        return f"[{self}]"
                
    @staticmethod
    def decode(instruction: int) -> Tuple[int, List[int]]:
        opcode = instruction % 100
        modes = (
            (instruction // 100) % 10,
            (instruction // 1000) % 10,
            (instruction // 10000) % 10
        )
        return opcode, modes


class Operation(object):
    """An Operation is an abstract form of something the machine can do."""
    
    code = None
    num_params = 0
    modes = [0,0,0,0]
    
    def __init__(self, code):
        OpClass = self.from_code(code)
        self.__class__ = OpClass

    def __str__(self):
        return self.__class__.__name__.ljust(10)
    
    def operate(self, state: Intcode, **params):
        raise NotImplementedError("Subclasses should override this")
    
    @classmethod
    def width(cls):
        return 1 + cls.num_params
    
    @classmethod
    def from_code(cls, code):
        operations = {}
        for item in cls.__subclasses__():
            if type(item) == type and issubclass(item, cls):
                operations[item.code] = item
        if code in operations:
            return operations[code]

class Add(Operation):
    code = 1
    num_params = 3

    def operate(self, state, lhs, rhs, result):
        state[result] = state[lhs] + state[rhs]

class Multiply(Operation):
    code = 2
    num_params = 3

    def operate(self, state, lhs, rhs, result):
        state[result] = state[lhs] * state[rhs]

class Input(Operation):
    code = 3
    num_params = 1

    def operate(self, state, result):
        state[result] = state.input.popleft()

class Output(Operation):
    code = 4
    num_params = 1

    def operate(self, state, param):
        state.output.append(state[param])

class JumpIfTrue(Operation):
    code = 5
    num_params = 2

    def operate(self, state, test, addr):
        if state[test] != 0:
            state.pc = state[addr]

class JumpIfFalse(Operation):
    code = 6
    num_params = 2

    def operate(self, state, test, addr):
        if state[test] == 0:
            state.pc = state[addr]
            
class LessThan(Operation):
    code = 7
    num_params = 3

    def operate(self, state, lhs, rhs, result):
        state[result] = int(state[lhs] < state[rhs])

class Equals(Operation):
    code = 8
    num_params = 3

    def operate(self, state, lhs, rhs, result):
        state[result] = int(state[lhs] == state[rhs])
        
class Halt(Operation):
    code = 99
    num_params = 0

    def operate(self, state):
        state.halted = True

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
