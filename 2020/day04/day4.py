#!/usr/bin/env python3

import re

required_fields = set([
    'byr', # (Birth Year)
    'iyr', # (Issue Year)
    'eyr', # (Expiration Year)
    'hgt', # (Height)
    'hcl', # (Hair Color)
    'ecl', # (Eye Color)
    'pid', # (Passport ID)
])
optional_fields = set([
    'cid', # (Country ID)
])
permitted_fields = required_fields | optional_fields

def validate_hgt(hgt):
	'''
	hgt (Height) - a number followed by either cm or in:
	    If cm, the number must be at least 150 and at most 193.
	    If in, the number must be at least 59 and at most 76.
	'''
	if hgt.endswith('cm'):
		val = int(hgt[:-2])
		return 150 <= val <= 193
	if hgt.endswith('in'):
		val = int(hgt[:-2])
		return 59 <= val <= 76
	return False

validators = {
    'byr': lambda x: 1920 <= int(x) <= 2002, #(Birth Year) - four digits; at least 1920 and at most 2002.
    'iyr': lambda x: 2010 <= int(x) <= 2020, #(Issue Year) - four digits; at least 2010 and at most 2020.
    'eyr': lambda x: 2020 <= int(x) <= 2030, #(Expiration Year) - four digits; at least 2020 and at most 2030.
    'hgt': validate_hgt,
    'hcl': lambda x: re.match('^#[0-9a-f]{6}',x) is not None, # (Hair Color) - a # followed by exactly six characters 0-9 or a-f.
    'ecl': lambda x: x in ['amb','blu','brn','gry','grn','hzl','oth'], #(Eye Color) - exactly one of: amb blu brn gry grn hzl oth.
    'pid': lambda x: re.match('^[0-9]{9}$',x) is not None, #(Passport ID) - a nine-digit number, including leading zeroes.
    'cid': lambda x: True #(Country ID) - ignored, missing or not.	
}


current_record = {}
records = [current_record]

with open('input.txt') as f:
	for line in f:
		line = line.strip()
		if len(line) == 0:
			current_record = {}
			records.append(current_record)
			continue

		fields = line.split()
		for field in fields:
			(name, value) = field.split(':')
			current_record[name] = value

def is_valid(record):
	fields = set(record.keys())
	if fields & required_fields != required_fields:
		return False
	for field, value in record.items():
		if field not in permitted_fields:
			return False
		if not validators[field](value):
			return False
	return True

valid_records = [*filter(is_valid, records)]
print("Valid records:", len(valid_records))
