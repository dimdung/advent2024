########################################
#         Advent Of Code 2024          #
# https://adventofcode.com/2024/day/11 #
# dimdung                              #
########################################
import sys
from functools import cache


with open(sys.argv[1], "r") as f:
    stones = list(map(int, f.read().strip().split(" ")))


@cache
def count_stones_day11(val: int, blinks: int) -> int:
    if blinks == 0:
        return 1
    if val == 0:
        return count_stones_day11(1, blinks - 1)
    str_val = str(val)
    len_str_val = len(str_val)
    if len_str_val % 2 == 0:
        return count_stones_day11(
            int(str_val[: len_str_val // 2]), blinks - 1
        ) + count_stones_day11(int(str_val[len_str_val // 2 :]), blinks - 1)
    return count_stones_day11(val * 2024, blinks - 1)


part1 = sum(count_stones_day11(s, 25) for s in stones)
print(f"The Day11 Puzzle input # Part 1: {part1}")

part2 = sum(count_stones_day11(s, 75) for s in stones)
print(f"The Day11 Puzzle input # Part 2: {part2}")
