########################################
# day7 of Advent Of Code 2024          #
# https://adventofcode.com/2024/day/7  #
# dimdung                              #
########################################
import sys


def check_possible_day7(target: int, nums: list[int], part2=False) -> bool:
    if len(nums) == 1:
        return target == nums[0]
    num = nums.pop()
    if target / num == target // num:
        if check_possible_day7(target // num, nums[:], part2=part2):
            return True
    if target - num >= 0:
        if check_possible_day7(target - num, nums[:], part2=part2):
            return True
    if not part2:
        return False
    target_str = str(target)
    num_str = str(num)
    if target_str.endswith(num_str) and len(target_str) > len(num_str):
        new_target = int(target_str[: -len(num_str)])
        if check_possible_day7(new_target, nums[:], part2=part2):
            return True
    return False


with open(sys.argv[1], "r") as f:
    lines = list(map(str.strip, f.readlines()))

part1 = 0
part2 = 0
for line in lines:
    target = int(line.split(":")[0])
    nums = list(map(int, line.split(": ")[1].split(" ")))
    if check_possible_day7(target, nums[:]):
        part1 += target
    if check_possible_day7(target, nums[:], part2=True):
        part2 += target

print(f"The Day7 Puzzle input # Part 1: {part1}")
print(f"The Day7 Puzzle input #  Part 2: {part2}")
