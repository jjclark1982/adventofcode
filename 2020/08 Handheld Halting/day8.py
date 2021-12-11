#!/usr/bin/env python3

import re

program = []

with open('input.txt') as f:
	for line in f:
		(op, arg) = line.split()
		arg = int(arg)
		program.append((op, arg))

executed = [False for _ in program]
acc = 0
pc = 0

while executed[pc] == False:
	executed[pc] = True
	(op, arg) = program[pc]
	if op == 'jmp':
		pc += arg
		continue
	pc += 1
	if op == 'acc':
		acc += arg
		continue
	elif op == 'nop':
		continue

print("Accumulator at infinite loop:", acc)

# want to get to pc == len(program)
# look for (prev instruction is not a JMP) or (some JMP targets target_pc)

target_pc = len(program)

jmp_targets = [i+op for (i, (acc, op)) in enumerate(program)]
print(jmp_targets)
