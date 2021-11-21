#!/usr/bin/env python3

import numpy as np


inputs = np.loadtxt("input.txt", dtype=int)

matrix = np.broadcast_to(inputs, (inputs.size, inputs.size))
matches = np.nonzero(matrix + matrix.T == 2020)
solution = np.product(inputs[matches[0]])

print("2-number solution:", inputs[matches[0]], solution)


x = inputs.reshape((inputs.size, 1, 1))
y = inputs.reshape((1, inputs.size, 1))
z = inputs.reshape((1, 1, inputs.size))

matches = np.nonzero(x + y + z == 2020)
match_values = inputs[np.unique(matches[0])]
solution = np.product(match_values)

print("3-number solution:", match_values, solution)

tril_mask = np.tril(np.ones((inputs.size, inputs.size), dtype=bool)) & ~np.identity(inputs.size, dtype=bool)
# print(tril_mask)
tril_mask_x = tril_mask.reshape((inputs.size, inputs.size, 1))
tril_mask_y = tril_mask.reshape((inputs.size, 1, inputs.size))
tril_mask_z = tril_mask.reshape((1, inputs.size, inputs.size))
xyz_mask = tril_mask_x & tril_mask_y & tril_mask_z
# print(xyz_mask)
matches = np.nonzero((x + y + z == 2020) & xyz_mask)
match_values = inputs[np.array(matches)[:, 0]]
solution = np.product(match_values)

print("3-number solution:", match_values, solution)
