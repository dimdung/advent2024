########################################
# day2 of Advent Of Code 2024          #
# https://adventofcode.com/2024/day/5  #
# dimdung                              #
########################################

import sys
from collections import defaultdict
from functools import cmp_to_key


with open(sys.argv[1], "r") as f:
    data = f.read()

rules, jobs = data.split("\n\n")
rules = [tuple(map(int, l.split("|"))) for l in rules.splitlines()]
jobs = [tuple(map(int, l.split(","))) for l in jobs.splitlines()]


invalid_map = defaultdict(bool)
for x, y in rules:
    invalid_map[(y, x)] = True


def check_job(job: list[int]) -> bool:
    for i in range(len(job)):
        for j in range(i + 1, len(job)):
            if invalid_map[(job[i], job[j])]:
                return False
    return True


def sort_job(a: int, b: int) -> int:
    if invalid_map[(a, b)]:
        return 1
    return -1


part1 = 0
part2 = 0
for job in jobs:
    if check_job(job):
        part1 += job[len(job) // 2]
    else:
        fixed_job = sorted(job, key=cmp_to_key(sort_job))
        part2 += fixed_job[len(fixed_job) // 2]
## Printing Input # 
print(f"The Day5 Puzzle input # Part 1: {part1}")
print(f"The Day5 Puzzle input # Part 2: {part2}")
