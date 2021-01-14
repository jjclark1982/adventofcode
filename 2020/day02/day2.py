#!/usr/bin/env python3

import re
pattern = re.compile(r'(\d+)-(\d+) (.): (.*)')

valid_count = 0

with open('input.txt') as f:
	for line in f.readlines():
		m = pattern.match(line)
		assert(m is not None)
		low = int(m[1])
		high = int(m[2])
		letter = m[3]
		password = m[4]
		count = password.count(letter)
		if low <= count <= high:
			valid_count += 1

print("Valid passwords (occurrences): {}".format(valid_count))


valid_count = 0

with open('input.txt') as f:
	for line in f.readlines():
		m = pattern.match(line)
		assert(m is not None)
		a = int(m[1])
		b = int(m[2])
		letter = m[3]
		password = m[4]

		count = int(password[a-1] == letter) + int(password[b-1] == letter)
		if count == 1:
			valid_count += 1

print("Valid passwords (indices): {}".format(valid_count))
