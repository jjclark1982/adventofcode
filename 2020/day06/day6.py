#!/usr/bin/env python3

import re

records = []
current_record = set([])

with open('input.txt') as f:
	for line in f:
		line = line.strip()
		if len(line) == 0:
			records.append(current_record)
			current_record = set([])
			continue

		current_record = current_record | set(list(line))
records.append(current_record)

record_lens = (len(r) for r in records)

print("Sum of 'any' counts:", sum(record_lens))


records = []
current_record = None
with open('input.txt') as f:
	for line in f:
		line = line.strip()
		if len(line) == 0:
			records.append(current_record)
			current_record = None
			continue

		if current_record is None:
			current_record = set(list(line))
		else:
			current_record = current_record & set(list(line))
records.append(current_record)

record_lens = (len(r) for r in records)

print("Sum of 'all' counts:", sum(record_lens))
