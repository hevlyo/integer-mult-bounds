# Selected T16 pending-axis disjointness is a separate check

**Audit of one selected-supplier obligation. No new κ.** The published
PR1094 owner map does satisfy cross-child pending-axis disjointness. That
fact does not follow from the role audit or from the rebuilt port-basis
chart predicate: both accept a one-axis transplant that the separate X2
scan rejects. This is not an acceptance bug in the published map, and it
is not the historical PR626 bridge-omission example.

Assignment seed `679c8b9611f457f3f76b2fc2b6afa362`, track
`adversarial-audit`, card `supplier-boundary-audit`, scope key
`dcdb0fa8e49b08a958d0`. Base `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`.
Scope status: **refined**.

## Obligation

For the selected sixteen-replica map, distinct positive-rank idle children
of one physical family have disjoint pending axes at every port. Josie
Elliston's owner audit records this as X2 in
`research/t16-owner-audit-seed67/verify.py`. The idle suffix of each child
is charged as a remainder, so a shared axis is shared physical ownership
even when the hosted slices do not overlap.

The selected cold replay (`make frontier1094-verify`) was not run. It
hash-pins `DATA-PHASES.json` through the PR1087 archive's
`data/UPSTREAM-PINS.json` and then runs `t16/indep16.py` and
`code/audit_allcold.py`. Those two files in
`research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz` are
byte-identical to the working-tree copies pinned here. Their chart
predicate rebuilds a 73-axis permutation from the hosted slice only. It
does not compare pending axes across children.

## Result

The pinned phase file passes X2 on all 2,016 child/port checks. All 69,120
roles pass the rebuilt chart predicate, the hosted slices share no ambient
axis, and the predecessor role audit returns deficit 5,120 with idle
profile `{1: 2276, 3: 377, 7: 7, 48: 4866}`.

The first idle-suffix transplant, in sorted `(pair, side)`, port, child
order, is:

| Field | Value |
| --- | --- |
| Physical family class | pair 3, side 1, port 0 |
| Source | child 11, index 0, axis `2^49` |
| Hosted by | all 16 owner replicas |
| Target | child 10, index 0, which no replica hosts |
| Replaced axis | 13 |
| Target rank | 48, so the whole list is idle remainder |

X2 reports exactly one shared axis, that `2^49`. The predecessor
`geometry` call raises `X2:`. Every rebuilt chart is identical to the
published chart, so the spectator lists and sigma vectors of the hosted
roles do not move. The role audit still accepts, because it never reads
axis vectors. Hosted-slice collisions stay at zero: the duplicate sits in
child 10's idle list, not in a second hosted slice.

A separate control duplicates an axis inside one hosted slice of child 0
at port 0. The chart predicate rejects that role. 69,104 of the 69,120
charts still pass, so the predicate is not vacuous.

## Reproduce

Python 3.12, standard library only, from the repository root. Leave
`PYTHONOPTIMIZE` unset. The verifier does not write a file.

```sh
python3 -B research/selected-t16-axis-gap/verify.py
```

Expected final line: `PASS_SELECTED_T16_AXIS_DISJOINTNESS_GAP`.

The registered package replay is:

```sh
python3 scripts/research_package.py --package research/selected-t16-axis-gap
```

Orientation, not part of this receipt: `python3 -B research/owner-boundary-audit/verify.py` prints `PASS_PR626_NEXT_TOUCH_BOUNDARY_AUDIT`. That historical timing-only bridge omission is not restated here as a current bug.

## What was not run

`make frontier1094-verify` and the PR1087 `verify_t16.py` cold replay were
not run. One attempt to comment on discussion 1166 returned FORBIDDEN
(`Resource not accessible by integration`) and was not retried. This package
does not execute `indep16.py` or `audit_allcold.py`;
it reimplements the chart predicate those files state and checks that the
archive members match the pinned sources. No Lean proof, no new supplier,
and no change to the selected frontier.

## Open next questions

Does the emitted idle-remainder frame export reject this same transplant
when the phase hash pin is not used? The pin already fails closed on a
substituted file, so it cannot answer whether the remainder frames
themselves enforce disjointness. The smallest step is to recompute child
10's port-0 tails from the transplanted axes and compare them with the
pinned tails. That needs the emitted frames, which the cold replay
produces and this package does not.

The nearest board thread is the bit-supplier ambient-axis audit in discussion
1289 and `research/selected-bit-hosting-audit`. That work checks PR589
projectors, not this complex T16 chart predicate. `research/owner-boundary-audit`
is the PR626 orientation example named by the task card.

## Credit

The selected map is Rohan Arun's PR1094, on Jeremy Kothe's PR1087 T16
packing and Hao Yan's controller and chart checks. The X2 statement and
the role audit used here are Josie Elliston's
`research/t16-owner-audit-seed67`. The phase file and parent template are
the pinned PR558 inputs those audits already use. New material is
Apache-2.0.

Prepared by hevlyo with substantial AI assistance. This is not an
independent human review.
