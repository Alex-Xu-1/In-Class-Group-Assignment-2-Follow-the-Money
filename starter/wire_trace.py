"""Wire-transfer fraud trace: parse a wire log, build a graph, follow the money.

Run the provided tests:   python -m pytest test_wire_trace.py
Run the investigation:    python wire_trace.py ../data/wires.txt
"""

import re
import sys
from collections import deque

from ai_review import find_round_trip

FLAGGED = "ACCT-50117"
CASH_OUT = "ACCT-90001"


# ------------------------------------------------------------------
# Part A: regular expressions
# ------------------------------------------------------------------

def parse_wire(line: str) -> tuple[str, str, float] | None:
    """Return (from_account, to_account, amount) for a well-formed WIRE line, else None.

    A well-formed line looks exactly like this, and nothing else may come before or after it:

        2026-10-02 09:14 WIRE $12,500.00 from ACCT-10423 to ACCT-88812 ref INV-3341

    - date YYYY-MM-DD, a space, time HH:MM, a space
    - the word WIRE (any other transfer type, such as ACH, is rejected)
    - an amount: a $ sign, then digits, optionally with thousands commas, then optionally
      a decimal point and exactly two digits of cents ($500, $750.25, $1,250,000.00)
    - "from" and "to" accounts: ACCT- followed by exactly 5 digits, uppercase
    - "ref" and an invoice reference: INV- followed by exactly 4 digits

    The returned amount is a float with the commas removed: "$12,500.00" -> 12500.0
    A trailing newline or surrounding whitespace on line is fine.

    Use one regular expression with capture groups, and re.search with ^ and $ anchors.
    """

    pattern = (
        r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2} WIRE \$"
        r"([0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(\.[0-9]{2})? "
        r"from (ACCT-[0-9]{5}) to (ACCT-[0-9]{5}) ref INV-[0-9]{4}$"
    )

    match = re.search(pattern, line.strip())
    if match is None:
        return None

    amount, cents, src, dst = match.groups()
    amount = float(amount.replace(",", "") + (cents or ""))

    return src, dst, amount
    

def load_wires(path: str) -> tuple[list[tuple[str, str, float]], list[str]]:
    """Read the log file at path and parse every line with parse_wire.

    Return (wires, rejected):
    - wires: a list of (from_account, to_account, amount) tuples, in file order
    - rejected: the lines that did not parse, in file order, with whitespace stripped

    Blank lines are skipped. They are neither wires nor rejected lines.
    """

    wires = []
    rejected = []

    with open(path, encoding="utf-8") as log:
        for line in log:
            line = line.strip()

            if not line:
                continue

            wire = parse_wire(line)

            if wire is None:
                rejected.append(line)
            else:
                wires.append(wire)

    return wires, rejected


# ------------------------------------------------------------------
# Part B: graph search
# ------------------------------------------------------------------

class Graph:
    def __init__(self):
        self.graph = {}  # adjacency list: {account: [(dest, amount), ...]}

    def add_edge(self, src, dst, amount):
        """Record one wire from src to dst. Wires are directed: money goes one way."""
        if src not in self.graph:
            self.graph[src] = []
        self.graph[src].append((dst, amount))

    def accounts_within(self, start: str, max_hops: int) -> dict[str, int]:
        """Return {account: hops} for every account start can reach in 1..max_hops wires.

        hops is the FEWEST wires needed to reach that account. start itself is not included,
        even if money comes back to it. Return {} if max_hops is 0 or start sent no wires.

        Use breadth-first search.
        """
        if max_hops <= 0:
            return {}

        visited = {start}
        queue = deque([(start, 0)])
        result = {}

        while queue:
            account, hops = queue.popleft()
            if hops >= max_hops:
                continue

            for dest, _ in self.graph.get(account, []):
                if dest not in visited:
                    visited.add(dest)
                    result[dest] = hops + 1
                    queue.append((dest, hops + 1))

        return result

    def shortest_hop_path(self, start: str, end: str) -> list[str]:
        """Return the chain of accounts [start, ..., end] that uses the fewest wires.

        Return [start] if start == end, and [] if end cannot be reached from start.

        Use breadth-first search. Record each account's predecessor when you first reach
        it, then walk back from end -- the same idea as the lecture's dijkstra().
        """
        if start == end:
            return [start]

        queue = deque([start])
        previous = {start: None}

        while queue:
            account = queue.popleft()
            for dest, _ in self.graph.get(account, []):
                if dest in previous:
                    continue
                previous[dest] = account

                if dest == end:
                    path = [end]
                    while path[-1] != start:
                        path.append(previous[path[-1]])
                    path.reverse()
                    return path

                queue.append(dest)

        return []


# ------------------------------------------------------------------
# Provided: run the investigation. Do not change.
# ------------------------------------------------------------------

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} wireLog", file=sys.stderr)
        sys.exit(1)

    wires, rejected = load_wires(sys.argv[1])
    print(f"Q1. Loaded {len(wires)} wires; rejected {len(rejected)} lines:")
    for line in rejected:
        print(f"    {line}")

    g = Graph()
    for src, dst, amount in wires:
        g.add_edge(src, dst, amount)

    within = g.accounts_within(FLAGGED, 2)
    print(f"\nQ2. Accounts within 2 hops of {FLAGGED}:")
    for account in sorted(within, key=lambda a: (within[a], a)):
        print(f"    {account}  ({within[account]} hop)")

    path = g.shortest_hop_path(FLAGGED, CASH_OUT)
    print(f"\nQ3. Shortest chain from {FLAGGED} to {CASH_OUT}:")
    print("    " + (" -> ".join(path) if path else "(none)"))

    trip = find_round_trip(g.graph, FLAGGED)
    print(f"\nQ4. Round trip back to {FLAGGED}:")
    print("    " + (" -> ".join(trip) if trip else "(none)"))


if __name__ == "__main__":
    main()
