#!/usr/bin/env python3

import re
from collections import defaultdict

rule_pattern = re.compile(r'(.*?) bags contain (.*).')
item_pattern = re.compile(r'(\d+) (.*?) bags?')

rules = defaultdict(list)
valid_parents = defaultdict(set)

with open('input.txt') as f:
	for line in f:
		match = rule_pattern.match(line)
		# print(match.groups())
		parent_adj = match[1]
		children = match[2]
		if children == 'no other bags':
			continue
		for child in children.split(', '):
			match = item_pattern.match(child)
			# print(match.groups())
			child_num = int(match[1])
			child_adj = match[2]

			valid_parents[child_adj].add(parent_adj)
			rules[parent_adj].append((child_num, child_adj))



valid_roots = set()

my_bag_adj = 'shiny gold'
to_check = valid_parents[my_bag_adj]
while (len(to_check) > 0):
	checking = to_check
	to_check = set()
	for item in checking:
		if item not in valid_roots:
			to_check = to_check | valid_parents[item]
	valid_roots |= checking

print("Valid outer bags:", len(valid_roots))


def count_inner(adj):
	count = 1
	for item in rules[adj]:
		count += item[0] * count_inner(item[1])
	return count

# print(rules[my_bag_adj])

print("Required inner bags:", count_inner(my_bag_adj)-1)
