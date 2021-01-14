#!/usr/bin/env python3

import re

literal_pattern = re.compile(r'"(.*)"')


rules = {}
compiled_rules = {}
num_match_zero = 0
num_not_match_zero = 0


def process_rule(line):
    (rule_id, rule) = line.split(": ")
    rules[rule_id] = rule


def compile_rules():
    # for rule_id in rules.keys():
    #     compile_rule(rule_id)
    modify_rules()
    pass


def modify_rules():
    pat_8 = compile_rule('8')
    pat_8_prime = r'(?:' + pat_8.pattern + ')+'
    compiled_rules['8'] = re.compile(pat_8_prime)

    pat_11 = compile_rule('11')
    pat_11_prime = compile_disjunction([
        '42 31',
        '42 42 31 31',
        '42 42 42 31 31 31',
        '42 42 42 42 31 31 31 31',
        '42 42 42 42 42 31 31 31 31 31',
    ])
    compiled_rules['11'] = re.compile(pat_11_prime)
    print(compiled_rules['11'])


def compile_rule(rule_id):
    if compiled_rules.get(rule_id) is None:
        rule = rules[rule_id]
        print("compiling rule", rule_id, rule)
        disjunction = rule.split(" | ")
        pattern = compile_disjunction(disjunction)
        compiled_rules[rule_id] = re.compile(pattern)
        print("compiled rule", rule_id, pattern)
    return compiled_rules[rule_id]


def compile_disjunction(disjunction):
    print("compiling disjunction", disjunction)
    pattern = '|'.join(map(compile_conjunction, disjunction))
    if len(disjunction) > 1:
        pattern = r'(?:' + pattern + r')'
    return pattern


def compile_conjunction(conjunction):
    tokens = conjunction.split(" ")
    print("compiling conjunction", tokens)
    pattern = ''.join(map(compile_token, tokens))
    # if len(pattern) > 1:
    #     pattern = r'(?:' + pattern + r')'
    print("compiled conjunction", tokens, pattern)
    return pattern


def compile_token(token):
    print("compiling token", token)
    match_literal = literal_pattern.match(token)
    if match_literal:
        return match_literal.groups()[0]
    else:
        return compile_rule(token).pattern


def process_message(line):
    global num_match_zero, num_not_match_zero
    if compile_rule("0").fullmatch(line):
        print("MATCH:", line)
        num_match_zero += 1
    else:
        print("notch:", line)
        num_not_match_zero += 1


handler = process_rule
with open('input.txt') as f:
    for line in f:
        line = line.strip()
        if len(line) == 0:
            compile_rules()
            handler = process_message
            continue
        handler(line)


print("rule 0:", compile_rule("0").pattern)

print("num match rule zero: {}/{}".format(num_match_zero, num_match_zero+num_not_match_zero))
