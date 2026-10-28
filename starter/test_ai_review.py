# Part C: your tests for ai_review.py.
#
# For each bug you find, add one test that FAILS on the AI's code as given.
# Then fix the bug in ai_review.py and watch the test pass. Do not delete the failing
# version from your history -- REPORT.md asks what the test showed before the fix.
#
# Run:  python -m pytest test_ai_review.py

from ai_review import extract_refs, find_round_trip


# This example passes on the AI's code. It shows the shape of a test; it does not find a bug.
def test_extract_refs_example():
    assert extract_refs("Payment for INV-3341, thanks") == ["INV-3341"]


# This example also passes. Graphs here are plain adjacency dicts, the same shape as Graph.graph.
def test_find_round_trip_example():
    graph = {"A": [("B", 100.0)], "B": [("A", 100.0)]}
    assert find_round_trip(graph, "A") == ["A", "B", "A"]
