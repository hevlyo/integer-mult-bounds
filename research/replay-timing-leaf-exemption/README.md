# Replay timing leaf exemption

**No κ change. The selected frontier is unchanged.** This repairs one canonical
comparison used to decide whether two #741 complex replay trees agree.

## Scope and evidence

Original card: `portable-replay`, refined to the timing exemption in
[`research/complex741-parallel-replay/compare_replays.py`](../complex741-parallel-replay/compare_replays.py).
The pinned predecessor is git blob `6afb9d956f5012346ee16a08f94c69a63f1f453a`
at base `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Its `ok` predicate accepted
every JSON path containing `seconds` or `elapsed_seconds`, with no type check.
On small fixtures, that accepts all of the following:

- `/seconds/kappa` changing from `1/2` to `1/3`
- `/additional_evidence/seconds` changing from `1` to `7` while `rank` stays `4`
- a numeric `seconds` value replaced by a boolean, string, NaN, negative, or object

The supplier identity in
[`research/complex-sw4-frame8/code/generated_identity.py`](../complex-sw4-frame8/code/generated_identity.py)
drops only `CLIFFORD-REVIEW.json`'s root `seconds`, and only when that value is
a nonnegative finite real number. Its controls keep `additional_evidence.seconds`
and an inserted root `seconds` on `INDEPENDENT-LOCAL-REPLAY.json` as proof.
The predecessor comparator omitted those fields.

The working comparator exempts a leaf only when the leaf name is `seconds` or
`elapsed_seconds`, both values are nonnegative finite reals, and the leaf is at
the JSON root or directly inside a list element (`/seconds`, `/0/seconds`,
`/stages/0/seconds`). Gzip containers with different `mtime` and the same
payload still compare equal. A SHA-256 difference is accepted only when it is
the digest of a file that itself compared equal or was already accepted, so a
hidden kappa change also rejects the receipt that digests it.

Marker: `PASS_REPLAY_TIMING_LEAF_EXEMPTION`.

Selected record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`,
κ = `836330098538459/500000000000000000`. `python3 -B scripts/research_baseline.py`
printed `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. `make frontier1094-verify` and
`make complex741-parallel-verify` were not run. The historical 304-file
comparison table in the #741 parallel-replay note was not rerun.

Python equality still treats `1 == True` and `0 == False`, so a boolean
substituted for the same integer is not a reported leaf. Log lines may still
differ by decimal floats. Root numeric `seconds` on every JSON file remains
exempt; see the open question.

Assignment nonce `0ce1e0530c69bff452c22989ee10e531`, scope key
`831cc1a3c8f9ff01b197`, priority revision 2. A portable-replay overlap search
at 2026-11-28 12:06 UTC covered 1388 open PRs and 7979 discussion records and
found many other portable-replay threads. A refreshed search at 12:14 UTC for
`additional_evidence.seconds`, `/seconds/kappa`, and `timing leaf exemption`
matched only this package and the comparator note edited with it.

## Reproduce

From the repository root, with `PYTHONOPTIMIZE` unset:

```sh
python3 -B research/replay-timing-leaf-exemption/verify.py
python3 -B -m unittest tests.test_complex741_parallel
python3 -B scripts/research_package.py --package research/replay-timing-leaf-exemption --check-only
python3 -B scripts/research_package.py --package research/replay-timing-leaf-exemption
```

The package replay needs Python 3.12 and this checkout's git history so the
predecessor blob can be loaded. Environment used for the recorded run: Linux,
CPython 3.12.3, g++ 13.3.0 as `/usr/bin/c++`, Boost headers 1.83.0.1ubuntu2.
No third-party modules are imported by the verifier.

## Open next questions

Which root numeric `seconds` leaves in a real #741 work tree are wall-clock
times, and which are proof counts that should not be exempt? This matters
because the repaired rule still treats every such leaf as timing, while
`generated_identity.py` drops that field only for `CLIFFORD-REVIEW.json`. The
first step is to list every accepted timing path in one saved sequential and
one saved parallel work tree. It is blocked here because no 304-file work tree
is in the checkout and the full parallel replay was not run.

## Credit

The comparator and its replay driver are navinor's (Aaron Wang), from the #741
parallel-replay package. The nonnegative finite timing predicate and the
`nested_phase_seconds_retained` control are in the #741 supplier lineage
(`research/complex-sw4-frame8`). The payload-versus-container distinction
follows the gzip-container reproducibility note. Prepared by hevlyo. Substantial
AI assistance was used to locate the comparison gap, draft the leaf rule, and
write the fixtures and notes. Apache-2.0.

One `addDiscussionComment` on discussion #1166 returned FORBIDDEN
(`Resource not accessible by integration`) and was not retried.
