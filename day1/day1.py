########################################
# day1 of Advent Of Code 2024          #
# https://adventofcode.com/2024/day/1  #
# dimdung                              #
########################################

import sys

# File open with arguments 
with open(sys.argv[1], "r") as f:
    lines = [list(map(int, line.split())) for line in f.readlines()]

list1, list2 = list(map(list, zip(*lines)))


part1 = sum(abs(x1 - x2) for x1, x2 in zip(sorted(list1), sorted(list2)))
print(f"Part 1: {part1}")

part2 = sum(x * len([y for y in list2 if y == x]) for x in list1)
print(f"Part 2: {part2}")
