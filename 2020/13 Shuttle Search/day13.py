#!/usr/bin/env python3

import numpy as np

with open('input.txt') as f:
	start_time = int(f.readline())
	bus_ids = f.readline().strip().split(',')

active_bus_ids = [int(b) for b in bus_ids if b != 'x']

wait_times = [-start_time % b for b in active_bus_ids]
min_wait = np.argmin(wait_times)
best_id = active_bus_ids[min_wait]

print("Bus ID * wait time:", best_id * wait_times[min_wait])
print()


offsets = []
primes = []
for i, b in enumerate(bus_ids):
	if b == 'x':
		continue
	p = int(b)
	offsets.append(i)
	primes.append(p)

offsets = np.array(offsets)
primes = np.array(primes)

print(offsets)
print(primes)

offsets = offsets[np.flip(np.argsort(primes))]
primes = primes[np.flip(np.argsort(primes))]

print("sorted")
print(offsets)
print(primes)
print()


N = primes[0] - offsets[0]
increment = primes[0]

for i in range(1,len(primes)):
	print("N:", N, "increment:", increment)
	p = primes[i]
	o = offsets[i]
	while (N+o) % p != 0:
		N += increment
	increment *= p

print(N)


# def valid_N(n):
# 	for i in range(len(primes)):
# 		p = primes[i]
# 		o = offsets[i]
# 		if (N+o) % p != 0:
# 			return False
# 	return True


# while not valid_N(N):
# 	print(N)
# 	N += lcm
# 	break

# find N such that
# for each item p at index offset in primes:
# (N+offset)%p == 0
