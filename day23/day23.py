########################################
# day23 of Advent Of Code 2024         #
# https://adventofcode.com/2024/day/13 #
# dimdung                              #
########################################
import sys
from collections import defaultdict


with open(sys.argv[1], 'r') as f:
    pairs = [l.strip().split('-') for l in f.readlines()]

conns = defaultdict(set)
for a, b in pairs:
    conns[a].add(b)
    conns[b].add(a)

triples = set()
for conn in conns:
    for neighbor in conns[conn]:
        for nn in conns[neighbor]:
            if conn in conns[nn]:
                triples.add(tuple(sorted([conn, neighbor, nn])))

part1 = len([t for t in triples if any(x.startswith("t") for x in t)])
print(f"The Day23 Puzzle input # Part 1: {part1}")


passwords = set()

def build_set_day23(conn: str, group: set[str]) -> None:
    password = ','.join(sorted(group))
    if password in passwords: return
    passwords.add(password)
    for neighbor in conns[conn]:
        if neighbor in group: continue
        if any(neighbor not in conns[node] for node in group): continue
        build_set_day23(neighbor, {*group, neighbor})


groups = set()
for conn in conns:
    build_set_day23(conn, {conn})
part2 = max(passwords, key=len)
print(f"The Day23 Puzzle input # Part 2: {part2}")
