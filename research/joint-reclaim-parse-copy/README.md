# joint-reclaim-parse-copy

**No new kappa.** The conditional joint-dual value stays
`4764513337/100000000000000`. This package records one measured speedup of
the isolated test module that replays the pinned ranked-reclamation words.

## Scope and evidence

Assignment seed `bcdd8ced93d371cc66f1bf8e89078298`, track
`verifier-engineering`, card `replay-runtime`, catalogue scope key
`a76657a85478d269d19f`, priority revision 2. The chooser base was
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Package pins are the following
commit, `ce769385cca354c4ab5c1935e324ecc32bbf219a`, which contains the copy
change. Scope status is **refined**: the card's question is kept, and the
object is `tests/test_joint_reclaim.py` on the two pinned words
`certificates/joint-dual-word-23.json.gz` and
`certificates/joint-dual-word-25.json.gz`.

`scripts/run_isolated_tests.py --workers 4` on this checkout ran all 104
modules in 72.54s before the edit and 72.95s after it. Both runs passed.
`test_joint_reclaim.py` was the slowest single module in the before run
(49.75s under contention). The suite makespan did not move, so this result
does not claim a faster full isolated suite. The measured fixture is the
module alone, before the edit:

```sh
python3 -B -m unittest discover -s tests -p test_joint_reclaim.py -v
```

16 tests, 45.679s. A cProfile of that version spent 94.350s of 125.323s
profiled time in `copy.deepcopy` (24 copies). One unprofiled deepcopy was
0.873s for h=23 and 1.455s for h=25. The replay and prepare checkers were
the smaller part.

The module now serializes each pinned word once and parses that text for
every mutation. `binary_frame_replay.py` and
`binary_frame_profile_prepare.py` are unchanged. After the edit the same
command passed 17 tests in 31.381s and again in 31.820s. The added test
checks that a shared `ops` list leaks an inner write and that a fresh parse
does not. `tearDownClass` rejects a mutated class-level word.

`scripts/experiments/pin_joint_dual_sources.py` updated only the test digest
in `research/joint-dual/SOURCE.json`, from
`c4e2817bf6e699f462aa3c589ee45e24ab0dcad6bcdb6152ca2a1e16ac7bffeb` to
`f24486d01ac1612b686d04bff3da68c5e2c07c87fd4f2f249182b91a41e7fcb0`.
`joint_dual_compose.compose` then changed only
`certificates/joint-dual-kappa.json` field `source_manifest_sha256`, from
`e60f1f78c9729700ef9606a6576163de0b553792e5e8f24591dce5f51597158c` to
`a240ec681bb6b6a8e0aeb0df53c0a2a42270053647750aab873f6094a591f02d`.
`check_sources` passed. `tests/test_assembly_ceiling.py` passed, 22 tests
in 2.153s.

## Reproduce

From the repository root, with `PYTHONOPTIMIZE` unset and Python 3.12:

```sh
python3 scripts/research_package.py --package research/joint-reclaim-parse-copy --check-only
python3 scripts/research_package.py --package research/joint-reclaim-parse-copy
```

The second command reruns the joint-reclaim module. It does not rerun
`make frontier1094-verify`.

Environment for the timings above: Linux, CPython 3.12.3, g++ 13.3.0 with
`/usr/bin/c++` pointing at `/usr/bin/g++`, libboost-dev 1.83.0.1ubuntu2.
`PYTHONOPTIMIZE` was unset. NumPy, SymPy, and SciPy were importable and were
not used by this check.

## Open next questions

Can one inner loop of `binary_frame_replay.replay` on
`certificates/joint-dual-word-25.json.gz` be made faster while keeping the
histogram, the scatter multiset, and both basis orientations?

That matters because the remaining time in this module is the unchanged
replay and prepare work. The full isolated-suite makespan is set by other
modules as well, so a further cut here speeds this check directly.
A feasible first step is to profile one h=25 replay and change only that
loop, then regenerate `research/joint-dual/SOURCE.json` with
`scripts/experiments/pin_joint_dual_sources.py`. The blocker is that
`binary_frame_replay.py` is inside the joint-dual source freeze, and any
faster loop still has to match the stored replay receipt. This session did
not change that scan.

## Overlap

`python3 scripts/find_overlap.py 'joint reclaim' deepcopy test_joint_reclaim 'structural clone'`
on 2026-11-23, with complete pagination of 1380 open PRs and 7949 discussion
records, returned eight matches. They concern other deepcopy speedups
(`audit_allcold.py`, mutant payloads) or comments that keep
`tests/test_joint_reclaim.py` frozen behind an opt-in adapter. This package
edits the live module and updates the joint-dual pin so
`joint_dual_compose.check_sources` still matches. No open-PR body in that
search already replaced this module's deepcopy.

Discussion writes were not available from this session's GitHub interface.
No Discussion post was sent, and the write was not retried.

## Credit

The joint-dual freeze and pin script are Chafik Boukhalfa's, with the
ranked-reclamation lineage those files already name. The source-pin update
follows that script rather than leaving `SOURCE.json` stale. New notes and
the test edit are Apache-2.0.

Prepared by Riquelme Soares (hevlyo). Substantial AI assistance was used to
profile the isolated test module, replace the word copy, and record the
measurement.

## Checks not run

`make frontier1094-verify` was not run. `scripts/experiments/verify_joint_dual.py`
was not run, so the native profiler and `compile_axis` regeneration were not
repeated. The selected frontier is unchanged.
