#!/usr/bin/env python3

import numpy as np


inputs = np.loadtxt("input.txt", dtype=int)

sorted_adaptors = np.sort(inputs)
jolt_levels = np.hstack([0, sorted_adaptors, sorted_adaptors[-1]+3])

print(jolt_levels)

diffs = np.diff(jolt_levels)

print(diffs)

counts = np.unique(diffs, return_counts=True)

print(counts)

print("Product of joltage counts:", np.product(counts[1]))
