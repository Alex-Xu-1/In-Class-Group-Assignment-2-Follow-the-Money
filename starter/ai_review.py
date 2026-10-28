# This module was written by an AI coding assistant. The prompt was:
#
#   "Write two helper functions for our wire-fraud tool.
#    1. extract_refs(text): return every invoice reference in a memo. An invoice
#       reference is INV- followed by exactly 4 digits, e.g. INV-3341.
#    2. find_round_trip(graph, start): the graph is an adjacency dict
#       {account: [(dest, amount), ...]}. Return a chain of accounts showing money
#       leaving start and coming back to it, like [start, ..., start], or [] if
#       money never comes back."
#
# It looks reasonable. It is not. Your job is to find out why.

import re


def extract_refs(text: str) -> list[str]:
    """Return every invoice reference (INV- followed by exactly 4 digits) in text."""
    return re.findall(r"INV-[1-9]{4}", text)


def _visit(graph, account, start, path):
    for dest, _ in graph.get(account, []):
        if dest == start:
            path.append(dest)
            return True
        path.append(dest)
        if _visit(graph, dest, start, path):
            return True
    return False


def find_round_trip(graph: dict, start: str) -> list[str]:
    """Return [start, ..., start] following wires out of start and back, or []."""
    path = [start]
    if _visit(graph, start, start, path):
        return path
    return []
