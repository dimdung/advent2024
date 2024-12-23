########################################
# day12 of Advent Of Code 2024         #
# https://adventofcode.com/2024/day/11 #
# dimdung                              #
########################################
import sys
from collections import deque


def perimeter_day12(region: set[tuple[int]]) -> int:
    total = 0
    for r, c in region:
        num_neighbors = len(
            [
                1
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
                if (r + dr, c + dc) in region
            ]
        )
        total += 4 - num_neighbors
    return total


def sides_day12(region: set[tuple[int]]) -> int:
    up, down, left, right = (set() for _ in range(4))
    for r, c in region:
        if (r - 1, c) not in region:
            up.add((r, c))
        if (r + 1, c) not in region:
            down.add((r, c))
        if (r, c - 1) not in region:
            left.add((r, c))
        if (r, c + 1) not in region:
            right.add((r, c))

    count = 0
    for r, c in up:
        if (r, c) in left:
            count += 1
        if (r, c) in right:
            count += 1
        if (r - 1, c - 1) in right and (r, c) not in left:
            count += 1
        if (r - 1, c + 1) in left and (r, c) not in right:
            count += 1

    for r, c in down:
        if (r, c) in left:
            count += 1
        if (r, c) in right:
            count += 1
        if (r + 1, c - 1) in right and (r, c) not in left:
            count += 1
        if (r + 1, c + 1) in left and (r, c) not in right:
            count += 1

    return count


with open(sys.argv[1], "r") as f:
    grid = list(map(str.strip, f.readlines()))
num_rows = len(grid)
num_cols = len(grid[0])

regions = []
seen = set()
for r in range(num_rows):
    for c in range(num_cols):
        if (r, c) in seen:
            continue
        region = set()
        queue = deque([(r, c)])
        while queue:
            rr, cc = queue.popleft()
            region.add((rr, cc))
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = rr + dr, cc + dc
                if (
                    (nr, nc) not in seen
                    and 0 <= nr < num_rows
                    and 0 <= nc < num_cols
                    and grid[nr][nc] == grid[rr][cc]
                ):
                    queue.append((nr, nc))
                    seen.add((nr, nc))
        regions.append(region)


part1 = sum(len(r) * perimeter_day12(r) for r in regions)
print(f"The Day12 Puzzle input # Part 1: {part1}")

part2 = sum(len(r) * sides_day12(r) for r in regions)
print(f"The Day12 Puzzle input # Part 2: {part2}")
