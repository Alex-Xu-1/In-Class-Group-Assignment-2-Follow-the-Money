# In-Class Group Assignment 2 — Follow the Money

**Covers:** Lectures 13–16 (trees, search, regex, graphs) · **Group size:** 3–4 · **Time:** 60 minutes
**Turn in:** your `starter/` folder, with `REPORT.md` filled in

A bank's monitoring system flagged account **ACCT-50117**: two wires just under $10,000 went
out of it within two minutes. Compliance has given you the raw wire log for the first half of
October and wants to know where the money went.

You have a raw text log, not a clean CSV. You will:

- **A.** Use a regular expression to turn log lines into wires and reject the malformed ones.
- **B.** Build a directed graph of who sent money to whom, and search it with BFS.
- **C.** Review a module an AI assistant wrote for this project. It has four bugs. Find them,
  prove each one with a failing test, and fix them.
- **D.** Run the investigation and report what you found.

---

## 1. Files

```
data/wires.txt            the October wire log -- your investigation data
starter/
  wire_trace.py           Parts A and B: you fill in the four functions marked NotImplementedError
  test_wire_trace.py      provided tests for Parts A and B -- do not change
  sample_wires.txt        small file used by one of the provided tests
  ai_review.py            Part C: the AI's code
  test_ai_review.py       Part C: your tests go here
  REPORT.md               Parts C and D: fill this in
```

Work inside `starter/`:

```bash
python -m pytest test_wire_trace.py        # Parts A and B
python -m pytest test_ai_review.py         # Part C
python wire_trace.py ../data/wires.txt     # Part D
```

---

## 2. Part A — Regular expressions

Implement `parse_wire(line)` and `load_wires(path)` in `wire_trace.py`. The docstrings are the
spec. A well-formed line looks exactly like this:

```
2026-10-02 09:14 WIRE $12,500.00 from ACCT-10423 to ACCT-88812 ref INV-3341
```

- `parse_wire` returns `("ACCT-10423", "ACCT-88812", 12500.0)`, or `None` if the line is not
  a well-formed WIRE.
- Use **one** regular expression with capture groups, and `re.search` with `^` and `$` anchors.
- Amounts may be `$500`, `$750.25`, or `$1,250,000.00`. Cents, when present, are exactly two
  digits.
- Some lines in the real log are malformed on purpose. Each one breaks exactly one rule.

Build your pattern a piece at a time on regex101.com, then check it against the tests.

## 3. Part B — Graph search

`Graph` is the same adjacency-list class as the lecture's `graph.py`, but **directed**: a wire
from X to Y is an edge X → Y only. `add_edge` is provided. Implement:

- `accounts_within(start, max_hops)` returns `{account: hops}` for everything `start` can
  reach in 1..`max_hops` wires, using the fewest hops.
- `shortest_hop_path(start, end)` returns the chain of accounts that uses the fewest wires.

Both use **breadth-first search**. Before you write either one, decide as a group why BFS
gives the fewest hops and DFS does not. The provided tests include a graph built to catch a
DFS.

The Part B tests build small graphs by hand, so you can start Part B without waiting for
Part A.

## 4. Part C — Review the AI's code

Read `ai_review.py`. The comment at the top is the prompt the AI was given. The module has
**four bugs, two in each function.** For each bug:

1. Write a test in `test_ai_review.py` that **fails** on the AI's code. Name it after the bug.
2. Fix the bug in `ai_review.py`, changing as little as possible, and confirm the test passes.
3. Fill in its row in `REPORT.md`: the input that triggers it, what happened, what should
   have happened, and your fix.

Your test has to be the evidence. "This looks wrong" is not a finding. A test that fails is.

Finding a bug by reading is good. Proving it with the smallest possible input is better.

## 5. Part D — Investigate

Once Parts A and B pass their tests, run `python wire_trace.py ../data/wires.txt`. It prints
the answers to four questions. Run it **before** you fix `ai_review.py` and again after, and
answer the questions in `REPORT.md`.

---

## 6. Ground rules

**AI — Reviewer Mode.** For Parts A and B, you may ask an AI to **critique code you
wrote**. You may not ask it to write `parse_wire`, your regex, or your search. **Part C is done
without AI.** Reviewing AI output is the skill being tested, and pasting the code back into
an AI skips it.

**Do not change** `test_wire_trace.py`, `main()`, or `add_edge`.

**Standard library only.** `re`, `collections.deque`, and `pytest`.

---

## 7. Who does what

Each member owns a part. Write the owners at the top of `REPORT.md`.

| Role | Owns | Starts on |
|---|---|---|
| **Parser** | Part A | `parse_wire`, then `load_wires` |
| **Searcher** | Part B | `accounts_within`, then `shortest_hop_path` |
| **Reviewer(s)** | Part C | `extract_refs` first, it is smaller. With 4 members, split the two functions. |
| **Everyone** | Part D | Together, in the last 15 minutes |

If you finish early, review another member's code: try to break it with an input that the
provided tests miss.

## 8. Timeline

| | |
|---|---|
| 0:00–0:05 | Read this page together. Assign roles. |
| 0:05–0:40 | Parts A, B, and C in parallel. |
| 0:40–0:55 | Merge into one `starter/` folder. All provided tests pass. Run Part D, fill in `REPORT.md`. |
| 0:55–1:00 | Turn in. |

If Part A or B is not done by 0:40, stop and get help. Part D needs both.

## 9. Done when

- `python -m pytest` in `starter/` runs every provided test plus your Part C tests, and all pass
- `test_ai_review.py` has one test per bug, and each would fail on the AI's original code
- `REPORT.md` is complete: owners, four bug rows, four investigation answers
