#!/usr/bin/env python3

import numpy as np 

def parse_line(line):
    return np.array(list(line)) == ord('#')

terrain = np.loadtxt("input.txt",
    dtype=bool, comments=None, delimiter='\n', converters={0: parse_line}
)

# print(terrain.astype(int))

def make_path(slope):
    right, down = slope
    path = np.zeros_like(terrain, dtype=bool)
    col = 0
    for row in range(len(terrain)):
        if row % down != 0:
            continue
        path[row, col] = True
        col = (col + right) % terrain.shape[1]
    return path

def count_collisions(path):
    return np.count_nonzero(path & terrain) 

slopes = [(1, 1), (3, 1), (5, 1), (7, 1), (1, 2)]

paths = map(make_path, slopes)

path_collisions = [*map(count_collisions, paths)]

for i in range(len(slopes)):
    # print(path.astype(int))
    print("Collisions at {} slope: {}".format(slopes[i], path_collisions[i]))

print("Product: {}".format(np.product(path_collisions)))
