# Slack-7 three-bin cycles on the selected owner map

**Negative result. No new κ.** On the selected PR1094 owner map, every directed
three-role cycle on three distinct occupied bins that touches a slack-7 bin and
strictly majorizes the slack triple is illegal for the selected source-event
windows. The complex primitive still binds. The selected record is unchanged.

Selector nonce `c6124726e8f026f5858c9552e1483c86`, track
`incumbent-optimization`, card `selected-packing` (scope key
`ab5d8f0f0d19bbab8625`), priority revision 2. Base
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Scope is **refined** to this one
residual. The baseline binding check returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`.

## Cycle and sign

A directed cycle of roles A, B, C in three distinct occupied bins sends A into
B's bin, B into C's bin, and C into A's bin. One role leaves each bin and one
role arrives, so the slack update is

```text
slack' = slack + departing width - arriving width
```

and every new slack must be nonnegative. Prefix compaction is the only offset
freedom used: the test keeps total width inside capacity. It does not rebuild
charts.

The selected idle slacks on occupied bins are only `{0,1,3,7}`. Exactly ten
roles sit in the seven slack-7 bins, in classes `(7,4)`, `(7,8)` and `(7,9)`.
Every directed cycle that touches a slack-7 bin is written once, starting at
its lowest-index slack-7 role. There are 13 occupied `(slack, width)` classes
and `3 * 13 * 13 = 507` anchored class patterns:

| sign | patterns |
|---|---:|
| uniformly improving | 77 |
| uniformly worsening | 96 |
| histogram-neutral | 39 |
| capacity-infeasible | 275 |
| not majorization-ordered | 20 |

For an equal-sum triple, strict majorization is the usual strict partial-sum
order. For every real `0<a<1`, `t -> t^(1-a)` is strictly concave on
`[0, infinity)`, so a strictly majorizing new triple has a strictly smaller
idle power sum. Neutral patterns do not change the multiset. Incomparable
patterns are not claimed to have one sign on the whole interval.

## What was counted

Among the 77 improving patterns there are **32,981,939** capacity-feasible
directed cycles and **0** whose three landings all lie in the destination
window lists of `PLAN.json`. Those lists are the selected plan's strict
source-event intervals. The same count includes **0** same-call cycles.
Recomputing the two published rank-8 patterns gives the recorded sizes:

| classes `(slack, width)` | old slacks | new slacks | capacity | window-legal |
|---|---|---|---:|---:|
| `(7,8), (0,8), (1,7)` | `(7,0,1)` | `(8,0,0)` | 17,567 | 0 |
| `(7,8), (1,7), (0,7)` | `(7,1,0)` | `(8,0,0)` | 4,319 | 0 |

The other 75 improving patterns, including every pattern that uses a slack-3
bin, are window-empty as well. The 20 incomparable patterns contribute
**325,142** further capacity-feasible cycles, also with **0** window-legal
landings. That is an exclusion, not a moment-sign theorem.

The identity check accepts all 69,120 selected roles inside their own windows.
A repair control opens the two blocked legs of one `(7,8),(0,8),(1,7)` triple
whose middle time is unique among landings that already accept the slack-7
role. The census then reports exactly one window hit, so an empty real count
is not a blind counter. No repaired triple is part of the mathematical claim.

## What this does not show

Active-pair exclusion, per-call family uniqueness, chart reconstruction,
controller emission, native replay, invoice, moment repricing and the outer
assembly were not run. The window lists were not regenerated from the parent
execution schedule; the census uses the committed `PLAN.json` lists. Windows already reject every candidate, so those later
checks cannot create a legal cycle inside this domain. Cycles that never touch
a slack-7 bin, cycles on fewer than three bins, and sequential moves are
outside the count. No supplier adoption or selected-frontier change is claimed.
Discussion writes for this account were rejected with FORBIDDEN, so no claim
was posted; that limitation is recorded here and was not retried.

## Reproduce

Python 3.12, standard library, from the repository root. `PYTHONOPTIMIZE` was
unset for the first command. The C++ toolchain was aligned for the session and
is not used by this census.

```sh
python3 -B research/selected-slack7-cycle-obstruction/verify.py
python3 -I -O -B research/selected-slack7-cycle-obstruction/verify.py
python3 -B scripts/research_package.py --package research/selected-slack7-cycle-obstruction
```

Expected primary status:

```text
PASS_SELECTED_SLACK7_CYCLE_OBSTRUCTION improving_patterns=77 capacity=32981939 window=0 same_call=0 known=17567+4319 incomparable_patterns=20 incomparable_capacity=325142 incomparable_window=0 synthetic_window_hits=1 roles=69120 no_new_kappa
```

## Open next questions

Does any directed three-bin cycle that avoids every slack-7 bin strictly
majorize its slack triple and land inside the selected source-event windows?
A yes answer would be an idle-histogram witness on the binding complex side.
The smallest next join anchors the same majorization test at the 754 slack-3
roles and drops triples that also touch slack 7. The blocker is the larger
class products, together with three-component transitions that are not
majorization-ordered.

## Credit

The owner map is Rohan Arun's PR1094, retaining Jeremy Kothe's packing lineage
and Hao Yan's window geometry. The rank-8 counts 17,567 and 4,319 were
published by Aaron Wang / navinor in PR2145; this package recomputes them and
extends the census to every slack-7-touching majorizing pattern. The same-call
three-role census in PR1873 is a different slice; the zero same-call count
here is only inside the slack-7 anchor. Josie Elliston's PR1091 owner audit
remains the geometry predecessor and was not rerun. Apache-2.0.

Prepared with substantial AI assistance for the census design, exact checks,
implementation and write-up. No independent human review or formal-kernel
verification is claimed.
