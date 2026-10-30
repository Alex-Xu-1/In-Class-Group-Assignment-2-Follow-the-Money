# Report — Follow the Money

**Group members and roles**

| Name | Role (Parser / Searcher / Reviewer) |
|---|---|
| Yuzhe Xue | Parser — Part A |
| Chenyao An | Searcher — Part B |
| Zihao Liu | Reviewer — Part C, first half (`extract_refs`) |
| Penggan Xu | Reviewer — Part C, second half (`find_round_trip`); final integration and report |

This was a group project, and ideally the repository would retain each member's
commit history. However, during class, we encountered some problems with the repository created. To keep making progress within the class time limit, some members worked locally without committing their changes. By the time Penggan Xu received the code for final integration and submission, substantial portions of the assignment had already been completed by teammates. The implementation commits under Penggan Xu's name therefore include the team's earlier work as well as his own final integration and remaining tasks. The commit history does not fully reflect individual contributions; the table above records the agreed division of responsibilities.

---

## Part C — AI code review

One row per bug. "Failing test" is the test function name in `test_ai_review.py`.

| # | Function | Failing test | Input that triggers it | What the AI's code did | What it should do | Your fix |
|---|---|---|---|---|---|---|
| 1 | `extract_refs` | `test_extract_refs_accepts_zero_digits` | `INV-0000 INV-1020` | Returned `[]`. | Return `["INV-0000", "INV-1020"]`. | Replace `[1-9]` with `[0-9]` so zero is a valid digit. |
| 2 | `extract_refs` | `test_extract_refs_rejects_more_than_four_digits` | `INV-12345` | Returned `["INV-1234"]`, a prefix of an invalid five-digit reference. | Return `[]`. | Add `(?![0-9])` after the four digits to reject a following digit. |
| 3 | `find_round_trip` | `test_find_round_trip_backtracks_after_dead_end` | Edges `A → B`, `A → A`; B has no outgoing wire. | Returned `["A", "B", "A"]`, inventing `B → A`. | Return `["A", "A"]`. | Pop the destination from `path` when its recursive search fails, before trying the next edge. |
| 4 | `find_round_trip` | `test_find_round_trip_handles_cycle_not_involving_start` | Edges `A → B`, `B → B`; start A. | Repeatedly visited B until `RecursionError`. | Return `[]`, since B's cycle never returns to A. | Track visited accounts and skip revisits; check for an edge back to start before skipping visited destinations. |

---

## Part D — Investigation

Run `python wire_trace.py ../data/wires.txt` from `starter/`.

**Q1. Rejected lines.** How many lines were rejected? For each one, which rule does it break?

The program accepted 28 wires and rejected these six lines:

| Rejected line | Formatting violation |
|---|---|
| `2026-10-06 10:02 WIRE $4,200.00 from ACCT-2045 to ACCT-33010 ref INV-1060` | `ACCT-2045` has four digits; account identifiers require exactly five digits after `ACCT-`. |
| `2026-10-07 11:40 WIRE $1,150.00 from acct-20789 to ACCT-41122 ref INV-1071` | `acct-20789` uses lowercase letters; the required prefix is uppercase `ACCT-`. |
| `2026-10-08 09:05 WIRE 3,000.00 from ACCT-41500 to ACCT-20456 ref INV-1080` | The amount is missing the required `$` symbol. |
| `2026-10-09 14:22 ACH $850.00 from ACCT-20456 to ACCT-33010 ref INV-1090` | The transaction keyword is `ACH` instead of the required `WIRE`. |
| `2026-10-10 16:18 WIRE $9,900.00 from ACCT-61204 ref INV-3310` | The required destination field, `to ACCT-xxxxx`, is missing. |
| `2026-10-12 09:30 WIRE $9,800.5 from ACCT-33010 to ACCT-90001 ref INV-3311` | The amount has one decimal digit; a decimal part, when present, must have exactly two digits. |

**Q2. Within 2 hops of ACCT-50117.** List the accounts and hop counts. ACCT-10234 exchanged
money with ACCT-50117. Why is it not on the list?

| Reachable account | Minimum hops |
|---|---:|
| ACCT-33010 | 1 |
| ACCT-61204 | 1 |
| ACCT-61388 | 1 |
| ACCT-41122 | 2 |
| ACCT-72019 | 2 |
| ACCT-73550 | 2 |

The starting account, ACCT-50117, is at hop 0 and is omitted from the output. ACCT-10234 is excluded because its wires run from ACCT-10234 to ACCT-50117 (`INV-1001` and `INV-1101`). The search follows outgoing transfers, so these wires cannot be traversed backward from ACCT-50117.

**Q3. Shortest chain to ACCT-90001.** Give the chain. Name one other chain the money could
have taken, and say why BFS did not return it.

The shortest chain is 3 hops:

`ACCT-50117 → ACCT-61204 → ACCT-72019 → ACCT-90001`

These transfers are recorded in `INV-3302`, `INV-3304`, and `INV-3308`.

Another is 4 hops:

`ACCT-50117 → ACCT-61388 → ACCT-73550 → ACCT-84102 → ACCT-90001`

These transfers are recorded in `INV-3301`, `INV-3303`, `INV-3305`, and `INV-3307`. BFS explores paths in increasing hop count, so it reaches ACCT-90001 through the 3-hop path before the 4-hop alternative and returns the shorter path.

**Q4. Round trip.** What did `find_round_trip` print **before** you fixed `ai_review.py`, and
what does it print after? Which wire in the "before" chain does not exist in the log?

The original pre-fix output was:

```text
ACCT-50117 -> ACCT-61388 -> ACCT-73550 -> ACCT-84102 -> ACCT-90001 -> ACCT-50117
```

The post-fix output is:

```text
ACCT-50117 -> ACCT-61388 -> ACCT-73550 -> ACCT-84102 -> ACCT-50117
```

The nonexistent wire in the original output is ACCT-90001 → ACCT-50117.
ACCT-90001 has no outgoing wires in the log. The original DFS reached this dead end
from ACCT-84102 but left ACCT-90001 in `path`. It then tried the actual return edge
ACCT-84102 → ACCT-50117 and appended the start, incorrectly joining the two branches.
Backtracking removes the dead end before exploring the next edge.
