########################################
# day4 of Advent Of Code 2024          #
# https://adventofcode.com/2024/day/1  #
# dimdung                              #
########################################

import sys
from collections import defaultdict


with open(sys.argv[1], "r") as f:
    lines = list(map(str.strip, f.readlines()))

char_map = defaultdict(set)
for r, row in enumerate(lines):
    for c, val in enumerate(row):
        char_map[val].add((r, c))

part1 = 0
for r, c in char_map["X"]:
    for dr, dc in [
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (0, -1),
        (0, 1),
        (1, -1),
        (1, 0),
        (1, 1),
    ]:
        for i, char in enumerate("MAS", 1):
            if (r + (dr * i), c + (dc * i)) not in char_map[char]:
                break
        else:
            part1 += 1
print(f"Part 1: {part1}")

upleft = lambda r, c: (r - 1, c - 1)
upright = lambda r, c: (r - 1, c + 1)
downleft = lambda r, c: (r + 1, c - 1)
downright = lambda r, c: (r + 1, c + 1)
get = lambda r, c: lines[r][c]

part2 = 0
for r, c in char_map["A"]:
    # Cleaner Solution (Thanks HyperNeutrino)
    if r == 0 or c == 0 or r == len(lines) - 1 or c == len(lines[0]) - 1:
        continue
    corners = (
        get(*upleft(r, c))
        + get(*upright(r, c))
        + get(*downright(r, c))
        + get(*downleft(r, c))
    )
    if corners in ["MMSS", "MSSM", "SSMM", "SMMS"]:
        part2 += 1
print(f"Part 2: {part2}")
