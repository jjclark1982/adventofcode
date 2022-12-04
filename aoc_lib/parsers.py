import re
import numpy as np

def split_input_sections(input_lines):
    current_section = []
    sections = [current_section]
    for line in input_lines:
        line = line.strip()
        if len(line) > 0:
            current_section.append(line)
        else:
            current_section = []
            sections.append(current_section)
    return sections

def parse_aoc_line(line):
    if re.match(r'^[.#]+$', line):
        return np.array(list(line)) == '#'
    elif re.match(r'^[01]+$', line):
        return np.array(list(line)) == '1'
    elif len(line) > 4 and re.match(r'^[\d]+$', line):
        return np.array(list(line), dtype=int)
    elif re.match(r'^[,\s\d-]*$', line):
        return np.array(re.split('[,\s]+', line), dtype=int)
    else:
        return line

def parse_aoc_lines(lines):
    if callable(getattr(lines, 'split', None)) and '\n' in lines:
        lines = lines.split('\n')
    
    arrays = [parse_aoc_line(line) for line in lines]

    if len(arrays) == 1:
        return arrays[0]
    else:
        return np.array(arrays)
