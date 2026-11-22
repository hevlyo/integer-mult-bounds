# Width-9 spectator charts do not imply family uniqueness

**Finite audit of one selected-supplier implication. No new κ.** The selected
frontier is unchanged. The published PR1094 owner map still has one helper per
physical family in each invocation. This package shows that fact is not a
consequence of the per-route greedy spectator chart.

Prepared with substantial AI assistance. Apache-2.0. This is not independent
human peer review.

## Task card

```text
Task ID / proposed scope key:
  supplier-boundary-audit / 66632af6c86d34fb0fdc
Base commit; exact predecessor and dependency heads:
  ef5f39403610d231a0c27e8a6b4f08c10209bcd6
  Selected record certificates/selected-result.json
  Owner map research/complex-t16-rare-pattern-exchanges/data/OWNERS.json.gz
  Phases and split-centres canonical word under
  research/community-k492-audit/pr622/replay/baseline558/
  Parent template ROUND20-PARENT-TEMPLATE.json.gz in the k492 vendor tree
  Obligation text research/complex-double-replica-owners/PROOF.md
Concrete object and question:
  On the selected 69,120-role T16 map, does one-helper-per-physical-family
  follow from the per-route greedy spectator chart?
Scope status: refined; reason for refinement:
  The card asks for one named current obligation. This names family uniqueness
  on the selected map and compares it with the spectator-chart predicate.
  The historical PR626 timing-only bridge omission is the orientation control,
  not the result.
Existing restriction being changed (or exact claim being audited):
  PROOF.md says the whole-family uniqueness rule is necessary because spectator
  coordinates can borrow other coordinates of that family, and that each route
  supplies 9-width spectator axes.
Method; explicit parameter ranges/candidate alphabet:
  Exact port bases for all 112 phase queries, all 48,384 pending axes, and
  every selected role. One synthetic pair: child 8, port 0, owner 0, width 9,
  offsets 0 and 9.
Nearest overlapping PRs and why this adds something:
  Josie Elliston's owner audit checks family uniqueness directly. The
  double-replica proof states why the rule is present. Neither derives the
  rule from the spectator chart, nor separates width 9 from narrower widths.
Optimistic full cost budget; required observable improvement:
  No κ target. The observable is a yes/no implication, with the published map
  still unique.
Success evidence; falsification test; time/compute cap:
  PASS_SELECTED_WIDTH9_SPECTATOR_GAP. A width-9 same-family pair must pass
  both charts and fail uniqueness; a width-8 pair on the same port must have
  spectator lists that meet at index 0. One second of standard-library work.
Predecessor authors; intended artifact and reproduction command:
  See Credit. Artifact is this package.
  python3 -B research/selected-width9-spectator-gap/verify.py
```

Assignment seed `0fa775fca4a5024608b1dbd3382569b3`, track `adversarial-audit`,
catalogue revision 2. The first card command
`python3 -B research/owner-boundary-audit/verify.py` returned
`PASS_PR626_NEXT_TOUCH_BOUNDARY_AUDIT` and was not reused as a new bug report.

## Statement

For every pinned phase query `q`, the orthogonal port basis is the same
9-plus-64 construction used by the T16 emitter. Its index 0 is `q`. None of
the 48,384 idle-child pending axes equals that vector, so every pending axis
has frame index at least 1.

The greedy spectator list of a width-`w` slice is the first `9-w` basis
indices outside the slice. For `w ≤ 8` that list is nonempty and starts at
index 0. Any two such lists on one port meet at the port vector. The selected
map has 34,560 roles of width at most 8, and each of their stored spectator
lists starts at index 0.

A width-9 route stores no spectator coordinates: the slice `[:0]` of the
complement is empty, and the emitted route is `[3, child, offset]`. Two
width-9 slices can still be disjoint. On child 8, port 0, owner 0, offsets 0
and 9:

- each slice is nine distinct frame vectors, and each chart completes to a
  permutation of all 73 basis indices;
- both spectator lists are empty, hence disjoint;
- both slices determine physical family `672 = 0·896 + (2·3+0)·112 + 0`;
- the one-helper-per-family predicate rejects that pair.

The same two widths on ports 0 and 1 determine different families, and the
uniqueness predicate accepts them. Family uniqueness on this geometry is
therefore a separate check from the per-route chart. For widths at most 8,
spectator-list disjointness inside one family already forbids a second narrow
helper, because every such list contains index 0. Width 9 is the case the
spectator budget does not cover.

The published map has 69,120 roles, 144 calls, 480 helpers in each call, and
240 width-9 helpers in each call. Every stored family matches the formula
above, every chart completes, and no call repeats a family. The gap is an
implication between two predicates. It is not an acceptance bug in the
published map, and the production controller still binds one owner per family.

## Reproduce

From the repository root, with `PYTHONOPTIMIZE` unset or set. The checks raise
exceptions, so they stay active when assertions are stripped.

```sh
python3 -B research/selected-width9-spectator-gap/verify.py
python3 -O -B research/selected-width9-spectator-gap/verify.py
python3 scripts/research_package.py --package research/selected-width9-spectator-gap
```

Expected final line: `PASS_SELECTED_WIDTH9_SPECTATOR_GAP`.

The run that produced this note used Python 3.12.3, g++ 13.2.0, libboost-dev
1.83.0, and `/usr/bin/c++` already pointing at `/usr/bin/g++`. The package uses
only the standard library. `research/e8-bit-p111-tuned/requirements.txt` was
installed with `python3 -m pip install --user` (numpy 2.5.4, sympy 1.14.0,
scipy 1.18.1) and is not imported here.

## What was not run

`make frontier1094-verify` was not run. No native scalar replay, emitted
controller, invoice, or moment engine was executed. There is no claim that two
width-9 helpers may share a family under the scalar residual contract. The
inherited all-size/compiler, common-label/mutable-source, whole-call hosting,
precision/tape, analytic, and bit H1–H5 obligations remain open.

Discussion writes were not available in this session's GitHub interface, so no
claim was posted. That limitation was not retried.

## Open next questions

Can two width-9 helpers whose pending blocks are disjoint share one physical
family for a single invocation under the scalar residual contract? It matters
because the spectator chart accepts that pair while the owner rule rejects it.
The smallest step is to evaluate the emitted `[3, child, offset]` route and
the residual adapter on child 8, port 0, offsets 0 and 9, inside one
invocation. The blocker is the inherited whole-call hosting assumption and the
emitter's one-owner assertion; this package does not rebuild that controller.

## Credit

The uniqueness sentence and the `9-width` spectator budget are Hao Yan's
double-replica proof, retained in
`research/complex-double-replica-owners/PROOF.md`. The selected roles are
Rohan Arun's PR1094 exchanges on Jeremy Kothe's T16 packing. Josie Elliston's
`research/t16-owner-audit-seed67` checks one helper per family directly. The
phase queries and split-centres canonical ports are the pinned PR558/PR622
baseline. The historical bridge-omission audit in
`research/owner-boundary-audit` is the card's orientation example and concerns
a different obligation.
