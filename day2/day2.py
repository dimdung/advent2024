########################################
# day2 of Advent Of Code 2024          #
# https://adventofcode.com/2024/day/2  #
# dimdung                              #
########################################

import sys


def report_safe_day2(nums: list[int]) -> bool:
    diffs = [abs(x1 - x2) for x1, x2 in zip(nums, nums[1:])]
    if not all(1 <= d <= 3 for d in diffs):
        return False
    if all(x1 < x2 for x1, x2 in zip(nums, nums[1:])):
        return True
    if all(x1 > x2 for x1, x2 in zip(nums, nums[1:])):
        return True
    return False


def check_report_day2(line: str, part1: bool = True) -> bool:
    nums = list(map(int, line.split(" ")))
    if report_safe_day2(nums):
        return True
    if part1:
        return False
    for i in range(len(nums)):
        if report_safe_day2(nums[:i] + nums[i + 1 :]):
            return True
    return False


with open(sys.argv[1], "r") as f:
    lines = f.readlines()
# Part1 result 
part1 = len([r for r in lines if check_report_day2(r)])
print(f"The Day2 Puzzle input # Part 1: {part1}")
# Part2 result 
part2 = len([r for r in lines if check_report_day2(r, part1=False)])
print(f"The Day2 Puzzle input # Part 2: {part2}")
