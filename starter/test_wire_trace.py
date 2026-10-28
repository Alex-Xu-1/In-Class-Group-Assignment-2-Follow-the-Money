# Provided tests. Do not change this file -- make your code pass it.
# If a graph test hangs, press Ctrl-C: your search is probably missing a visited set.

from wire_trace import Graph, load_wires, parse_wire

GOOD = "2026-10-02 09:14 WIRE $12,500.00 from ACCT-10423 to ACCT-88812 ref INV-3341"


def make_graph(edges):
    """Build a Graph from a list of (src, dst) pairs. Every wire is $100."""
    g = Graph()
    for src, dst in edges:
        g.add_edge(src, dst, 100.0)
    return g


# ------------------------------------------------------------------
# Part A: parse_wire -- lines that should parse
# ------------------------------------------------------------------

def test_parse_good_line():
    assert parse_wire(GOOD) == ("ACCT-10423", "ACCT-88812", 12500.0)


def test_parse_amount_without_cents():
    line = "2026-10-02 09:14 WIRE $500 from ACCT-10423 to ACCT-88812 ref INV-3341"
    assert parse_wire(line) == ("ACCT-10423", "ACCT-88812", 500.0)


def test_parse_amount_without_commas():
    line = "2026-10-02 09:14 WIRE $750.25 from ACCT-10423 to ACCT-88812 ref INV-3341"
    assert parse_wire(line) == ("ACCT-10423", "ACCT-88812", 750.25)


def test_parse_seven_figure_amount():
    line = "2026-10-02 09:14 WIRE $1,250,000.00 from ACCT-10423 to ACCT-88812 ref INV-3341"
    assert parse_wire(line) == ("ACCT-10423", "ACCT-88812", 1250000.0)


def test_parse_trailing_newline():
    assert parse_wire(GOOD + "\n") == ("ACCT-10423", "ACCT-88812", 12500.0)


# ------------------------------------------------------------------
# Part A: parse_wire -- lines that should be rejected
# ------------------------------------------------------------------

def test_reject_four_digit_account():
    line = "2026-10-02 09:14 WIRE $12,500.00 from ACCT-1042 to ACCT-88812 ref INV-3341"
    assert parse_wire(line) is None


def test_reject_six_digit_account():
    line = "2026-10-02 09:14 WIRE $12,500.00 from ACCT-10423 to ACCT-888120 ref INV-3341"
    assert parse_wire(line) is None


def test_reject_lowercase_account():
    line = "2026-10-02 09:14 WIRE $12,500.00 from acct-10423 to ACCT-88812 ref INV-3341"
    assert parse_wire(line) is None


def test_reject_missing_dollar_sign():
    line = "2026-10-02 09:14 WIRE 12,500.00 from ACCT-10423 to ACCT-88812 ref INV-3341"
    assert parse_wire(line) is None


def test_reject_one_digit_of_cents():
    line = "2026-10-02 09:14 WIRE $12,500.5 from ACCT-10423 to ACCT-88812 ref INV-3341"
    assert parse_wire(line) is None


def test_reject_ach():
    line = "2026-10-02 09:14 ACH $12,500.00 from ACCT-10423 to ACCT-88812 ref INV-3341"
    assert parse_wire(line) is None


def test_reject_missing_to_clause():
    line = "2026-10-02 09:14 WIRE $12,500.00 from ACCT-10423 ref INV-3341"
    assert parse_wire(line) is None


def test_reject_text_before_line():
    assert parse_wire("REVERSED " + GOOD) is None


def test_reject_text_after_line():
    assert parse_wire(GOOD + " (reversed)") is None


# ------------------------------------------------------------------
# Part A: load_wires
# ------------------------------------------------------------------

def test_load_wires_sample_file():
    wires, rejected = load_wires("sample_wires.txt")
    assert wires == [
        ("ACCT-11111", "ACCT-22222", 1000.0),
        ("ACCT-22222", "ACCT-33333", 250.0),
    ]
    assert rejected == [
        "2026-10-01 08:31 ACH $50.00 from ACCT-11111 to ACCT-33333 ref INV-0002",
        "2026-10-02 09:05 WIRE $75.00 from ACCT-2222 to ACCT-11111 ref INV-0004",
    ]


# ------------------------------------------------------------------
# Part B: accounts_within
# ------------------------------------------------------------------

def test_within_one_hop():
    g = make_graph([("A", "B"), ("A", "C"), ("B", "D")])
    assert g.accounts_within("A", 1) == {"B": 1, "C": 1}


def test_within_two_hops():
    g = make_graph([("A", "B"), ("A", "C"), ("B", "D"), ("D", "E")])
    assert g.accounts_within("A", 2) == {"B": 1, "C": 1, "D": 2}


def test_within_follows_wire_direction():
    # X sent money TO A. That does not make X reachable FROM A.
    g = make_graph([("X", "A"), ("A", "B")])
    assert g.accounts_within("A", 5) == {"B": 1}


def test_within_uses_fewest_hops():
    # D is 3 hops away along A-B-C-D, but only 1 hop along A-D.
    g = make_graph([("A", "B"), ("B", "C"), ("C", "D"), ("A", "D")])
    assert g.accounts_within("A", 5) == {"B": 1, "D": 1, "C": 2}


def test_within_uses_fewest_hops_other_branch():
    # D is 3 hops away along A-C-E-D, but only 2 hops along A-B-D.
    g = make_graph([("A", "B"), ("A", "C"), ("C", "E"), ("E", "D"), ("B", "D")])
    assert g.accounts_within("A", 5) == {"B": 1, "C": 1, "E": 2, "D": 2}


def test_within_survives_cycle_and_excludes_start():
    g = make_graph([("A", "B"), ("B", "C"), ("C", "B"), ("C", "A")])
    assert g.accounts_within("A", 10) == {"B": 1, "C": 2}


def test_within_zero_hops():
    g = make_graph([("A", "B")])
    assert g.accounts_within("A", 0) == {}


def test_within_account_with_no_outgoing_wires():
    g = make_graph([("A", "B")])
    assert g.accounts_within("B", 3) == {}


# ------------------------------------------------------------------
# Part B: shortest_hop_path
# ------------------------------------------------------------------

def test_path_simple_chain():
    g = make_graph([("A", "B"), ("B", "C")])
    assert g.shortest_hop_path("A", "C") == ["A", "B", "C"]


def test_path_prefers_fewest_hops():
    # Depth-first search finds A-B-C-D-E or A-Y-P-Q-R-E, depending on the order it tries
    # wires. The shortest is A-X-E.
    g = make_graph([
        ("A", "B"), ("A", "X"), ("A", "Y"),
        ("B", "C"), ("C", "D"), ("D", "E"),
        ("X", "E"),
        ("Y", "P"), ("P", "Q"), ("Q", "R"), ("R", "E"),
    ])
    assert g.shortest_hop_path("A", "E") == ["A", "X", "E"]


def test_path_unreachable_with_cycle():
    g = make_graph([("A", "B"), ("B", "C"), ("C", "A"), ("Z", "A")])
    assert g.shortest_hop_path("A", "Z") == []


def test_path_to_self():
    g = make_graph([("A", "B")])
    assert g.shortest_hop_path("A", "A") == ["A"]
