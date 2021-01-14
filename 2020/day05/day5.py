#!/usr/bin/env python3

import re
import numpy as np

def get_row(line):
	bits = np.array(list(line[0:7])) == 'B'
	row = np.packbits(np.flip(bits), bitorder='little')[0]
	return row

def get_col(line):
	bits = np.array(list(line[7:10])) == 'R'
	col = np.packbits(np.flip(bits), bitorder='little')[0]
	return col

def get_sid(row, col):
	return row * 8 + col

# print(get_row('BFFFBBFRRR'))
# print(get_col('BFFFBBFRRR'))
# print(get_sid(70,7))


seats = []

with open('input.txt') as f:
	for line in f:
		line = line.strip()
		row = get_row(line)
		col = get_col(line)
		sid = get_sid(row, col)
		seats.append((line, row, col, sid))
		# print("row={}, col={}, sid={}".format(row,col,sid))

seat_ids = [s[3] for s in seats]
seat_ids = sorted(seat_ids)
highest_id = seat_ids[-1]
print("highest seat id: {}".format(highest_id))

skipped_seats = np.nonzero(np.diff(seat_ids) != 1)[0]
skipped_seat_id = seat_ids[skipped_seats[0]] + 1
print("skipped seat id: {}".format(skipped_seat_id))
