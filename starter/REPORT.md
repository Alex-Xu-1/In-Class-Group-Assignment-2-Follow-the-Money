# Report — Follow the Money

**Group members and roles**

| Name | Role (Parser / Searcher / Reviewer) |
|---|---|
| | |
| | |
| | |
| | |

---

## Part C — AI code review

One row per bug. "Failing test" is the test function name in `test_ai_review.py`.

| # | Function | Failing test | Input that triggers it | What the AI's code did | What it should do | Your fix |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |

---

## Part D — Investigation

Run `python wire_trace.py ../data/wires.txt` from `starter/`.

**Q1. Rejected lines.** How many lines were rejected? For each one, which rule does it break?

**Q2. Within 2 hops of ACCT-50117.** List the accounts and hop counts. ACCT-10234 exchanged
money with ACCT-50117. Why is it not on the list?

**Q3. Shortest chain to ACCT-90001.** Give the chain. Name one other chain the money could
have taken, and say why BFS did not return it.

**Q4. Round trip.** What did `find_round_trip` print **before** you fixed `ai_review.py`, and
what does it print after? Which wire in the "before" chain does not exist in the log?
