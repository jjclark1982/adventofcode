import re
import numpy as np
from collections import defaultdict

line_pattern = re.compile(r'(\S+) = (\S+)')

# memory = defaultdict(lambda x:0)
memory = [0] * 65536
mask_on = 0
mask_off = 0

with open('input.txt') as f:
	for line in f:
		match = line_pattern.match(line)
		lhs, rhs = match.groups()
		if lhs == 'mask':
			mask_on = int(rhs.replace('X', '0'), 2)
			mask_off = int(rhs.replace('X', '1'), 2)

			# print("mask:     "+rhs)
			# print("mask_on:  {0:036b}".format(mask_on))
			# print("mask_off: {0:036b}".format(mask_off))

		if lhs.startswith('mem'):
			addr = int(lhs[4:-1])
			val = int(rhs)

			# print("val:      {0:036b}".format(val))

			val = val | mask_on
			val = val & mask_off
			# print("mask val: {0:036b}".format(val))

			memory[addr] = val

# values = np.array(list(memory.values()))
values = np.array(memory)
print("version 1")
print("count nonzero:", np.count_nonzero(values))
print("sum of values:", np.sum(values))
print()


print("version 2")
memory = defaultdict(lambda x:0)

with open('input.txt') as f:
	for line in f:
		match = line_pattern.match(line)
		lhs, rhs = match.groups()
		if lhs == 'mask':
			mask_on = int(rhs.replace('X', '0'), 2)
			mask_float = np.array(list(rhs)) == 'X'
			print(rhs)
			print(mask_float.astype(int))


		if lhs.startswith('mem'):
			addr = int(lhs[4:-1])
			val = int(rhs)

			val = val | mask_on
			# TODO: enumerate mask_float

			memory[addr] = val
