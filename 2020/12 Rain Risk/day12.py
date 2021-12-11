#!/usr/bin/env python3

import numpy as np

translations = {
	'N': np.array([0, 1]),
	'S': np.array([0,-1]),
	'E': np.array([1, 0]),
	'W': np.array([-1,0]),
}
rotations = {
	'R': np.matrix([[0, 1], [-1,0]]),
	'L': np.matrix([[0,-1], [ 1,0]]),
}

loc = np.array([0, 0])
heading = np.array([1, 0])

with open('input.txt') as f:
	for line in f:
		command = line[0]
		value = int(line[1:])

		if command in translations:
			loc += translations[command] * value
		elif command in rotations:
			for _ in range(value//90):
				heading = np.array(rotations[command] @ heading)[0]
		elif command == 'F':
			loc += heading * value

print("Ending loc (heading):", loc)
print("Distance from start:", np.sum(np.abs(loc)))
print()

waypoint = np.array([10,1])
loc = np.array([0, 0])

with open('input.txt') as f:
	for line in f:
		command = line[0]
		value = int(line[1:])

		if command in translations:
			waypoint += translations[command] * value
		elif command in rotations:
			for _ in range(value//90):
				waypoint = np.array(rotations[command] @ waypoint)[0]
		elif command == 'F':
			loc += waypoint * value

print("Ending loc (waypoint):", loc)
print("Distance from start:", np.sum(np.abs(loc)))
