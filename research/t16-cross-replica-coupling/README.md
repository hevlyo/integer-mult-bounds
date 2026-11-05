# Cross-replica coupling needs both hosting hypotheses

**Audit of one restoration implication. No new κ.** The selected saving stays
`836330098538459/500000000000000000`. Owner-window admission of one pinned
cross-replica role does not discharge the inherited no-coupling sentence.
Atomic restoration and the absence of an internal lender read are separately
necessary for that sentence, on an exact three-coordinate model in the
seven-slot word's gate encoding.

Prepared by Riquelme Pereira with substantial AI assistance. This is not
independent human review. Apache-2.0.

## Scope and evidence

Selector nonce `9332192c4263f5939bc98e5a64f92f45`, track `adversarial-audit`,
card `uniform-transfer-audit`, scope key `603f341b99f590f17a76`. Base
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Scope status: **refined**.

The card asks for one exact restoration implication. The proposition is this
paragraph of
[research/complex-double-replica-owners/PROOF.md](../complex-double-replica-owners/PROOF.md),
inherited by the selected sixteen-replica owner map:

> A hosted helper may use a family belonging to the other group. This relies on
> the existing whole-invocation interface: the hash-bound local supplier and its
> normalization wrappers restore arbitrary initial helper contents after each
> complete invocation. The scheduler does not interleave operations inside a
> local invocation. At its boundaries, the borrowed family therefore has the
> same contents it had before the borrow. This is why a cross-group helper
> assignment does not introduce a new scalar coupling between the two data
> controllers.

The pinned object is owner role 0 of
`research/complex-t16-rare-pattern-exchanges/data/OWNERS.json.gz`: replica 0,
helper 0, width 9, borrows family `13006` from replica 14, child 4, port 14,
at time 0. That time sits in the committed window `14,4` (rank 32, 92 legal
times). The selected owner audit admits the whole map: 69,120 roles, 57,480
cross-replica, 144 calls, 288 windows, rank mass 1,041,408, deficit 5,120,
idle remainders `{1:2276, 3:377, 7:7, 48:4866}`.

The scalar projection uses three coordinates `(x, h, y)`: the borrowed family
coordinate, one helper scratch, and the lender's later accumulator. Gates use
the pinned word encoding. The first `A` gate is `['add', 499, 498, 1, 1, []]`
and the first precondition gate is `['scale', 174, -1, 2, []]`. An `add` is
`target += (numerator/denominator) * source`. These four work and cleanup
gates are a minimal word in that encoding. They are not claimed to be helper
0's real program.

| Schedule | What happens | Image of `(3, -5, 7)` |
|---|---|---|
| No borrow | Lender reads `y += x` only | `(3, -5, 10)` |
| Atomic | Work, cleanup, then the lender read | `(3, -5, 10)` |
| Omitted cleanup | Work, then the lender read | `(1, -2, 8)` |
| Interleaved read | Lender reads between the write and the cleanup | `(3, -5, 8)` |
| Private scratch | Round-trip on `h` only, then the lender read | `(3, -5, 10)` |

The atomic and private schedules match the no-borrow linear map on the whole
space. Omitting cleanup changes it. Interleaving restores `(x, h)` on every
basis vector and still changes `y`: final restoration of the borrowed family
is not enough. A cleanup coefficient `-1/2` instead of `-1` also changes the
map. Empty and nonempty frame annotations do not. Denominator 3, a zero
numerator, a self-add and a non-dyadic scale are rejected. Narrowing the
pinned role's width from 9 to 8 is rejected by the owner rule `R2`. The
`audit` function's source does not mention adds, numerators or cleanup, and
the owner record has no gate field, so this admission is unchanged by either
scalar failure.

Positive controls run before this package: `python3 -B scripts/research_baseline.py`
returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`, and
`python3 -B research/owner-boundary-audit/verify.py` returned
`PASS_PR626_NEXT_TOUCH_BOUNDARY_AUDIT`. That historical bridge-omission
diagnostic is a different object. It was not re-reported as a current
acceptance bug.

Targeted overlap for `no new scalar coupling`, `borrowed family` and
`cross-group helper` was refreshed on 2026-11-05. Coverage was complete for
683 open pull requests, fetched at 2026-11-05T12:11:50Z, and 6,806 discussion
records, fetched at 2026-11-05T12:14:51Z. That search reported no matches.
No matches is not a novelty proof. The card's generic terms `uniform transfer`,
`all-size` and `precision` match a large amount of unrelated open work; this
package does not repeat those precision budgets.

Discussion writes to `CrocSwap/integer-mult-bounds` are forbidden for this
account. This run did not retry them.

## Reproduce

Python 3.12, standard library only, from the repository root. Leave
`PYTHONOPTIMIZE` unset. The checker reads the pinned inputs and writes nothing.

```sh
python3 -B research/t16-cross-replica-coupling/verify.py
python3 scripts/research_package.py --package research/t16-cross-replica-coupling --check-only
python3.12 scripts/research_package.py --package research/t16-cross-replica-coupling
```

Expected final line: `PASS_T16_CROSS_REPLICA_COUPLING`.

Environment used for the recorded run: CPython 3.12, `g++` 13.3.0 with
`/usr/bin/c++` pointing at `/usr/bin/g++`, `libboost-dev` 1.83.0.1ubuntu2, and
`research/e8-bit-p111-tuned/requirements.txt` already satisfied
(`numpy==2.5.4`, `sympy==1.14.0`, `scipy==1.18.1`). This package does not
import those libraries. `PYTHONOPTIMIZE` was unset.

## What this does not prove

- The selected cold command `make frontier1094-verify` was not run.
- Helper 0's real cleanup on family 13006 was not executed. The local word's
  existing `drop_restore` control was not rerun. This is not a claim that the
  local scalar auditor misses restoration.
- The fifteen production controller mutations, charts, invoices, moments and
  the 47 outer inequalities were not rerun.
- All-size compilation, common-label realization, precision, tape, exact
  recovery, analytic transfer and bit H1–H5 remain inherited.
- Frame annotations are ignored by the scalar projection. Agreement here is
  not frame admission.
- A finite identity is not a uniform multiplication theorem, and κ is unchanged.

## Open next questions

1. Does helper 0's shipped cleanup restore every coordinate of family 13006
   written by its width-9 residual and its spectators, for arbitrary dirty
   input? That is the hypothesis this model isolates. The feasible step is to
   bind the role's chart to register ids and compare the real cleanup
   projection with the identity. It is blocked here because the owner auditor
   does not carry those registers and the local scalar replay was not rerun.

2. Can the emitted controller place a lender scalar read inside one local
   invocation while keeping the thirty-event per-replica projection? Final
   restoration does not protect that read. The feasible step is to inspect one
   serialized `local_cover_sweep` for a lender gate on the borrowed family.
   It is blocked here because that internal gate list was not opened.

## Credit

The no-coupling sentence is Hao Yan's, in the sixteen-replica owner proof;
that package records its own assistance. The selected map is
Rohan Arun's PR1094 on Jeremy Kothe's T16 packing and the retained
PR1018/PR1005/PR858 lineage. The owner auditor reused here is the independent
T16 checker in `research/t16-owner-audit-seed67`. The historical PR626
bridge-omission audit is a separate predecessor and was not the object of
this check. Source notices and the Apache-2.0 license stay in force.
