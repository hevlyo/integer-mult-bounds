# Paired omission of an unread connector restoration

**Exact finite interface identity; no new kappa.** In each of the three
schedules in Ross Richardson's
[universal-connector certificate](../universal-connector-boundary/CERTIFICATE.json),
the last operation is a source toggle that no readout uses. One such omission
implements the output map and leaves the connector dirty by exactly that
toggle. The next copy of the same omission cancels the dirt. Two consecutive
shortened batches, on disjoint output rows and one shared connector, restore
the connector and save two source queries against two separate restored
batches.

A single shortened batch is not a legal restored call. A restored successor
preserves the leftover term, so the saving requires the next call to omit the
same toggle. Three omissions leave the term in place. Unlike tails do not
cancel. This does not change the published single-batch costs 38 and 74, the
selected supplier, or kappa.

## Scope and evidence

Original card: `persistent-boundary` (scope key drawn with seed
`6b2fecad1a22395de87447e8f9647679`, catalogue priority revision 2). Scope
status is **refined**. The card allows one explicit deferred restoration. The
pair is the two shortened copies of one pinned schedule, not a selected T16
call pair. `research/gauge44-slots-t16/data/PLAN.json` pins provider canonical
file `16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219` and
program hashes `071ecdacc0bb3ac16046aad4119ed551a945cb0ed6c57002a548a3e2232503d8`
and `f36c5831106f5637102c6bedeec76ed2b223c6671ce42fd0eceed9ef24725b23`. Those
bytes are not in this checkout. The checked-in `evidence/local` programs are a
different historical word (forward digest
`d17399c8c7458bb7110d8596fab5f769cd4cb3733a3042277fa08bf03f42d6c9`, profile
`1:2514` rather than the selected `1:2412`).

The typed contract is:

| Call | Exit connector, relative to entry | Root queries |
|---|---|---:|
| Published restored word R | clean | 38 or 74 |
| Short word S, final toggle omitted | entry plus one named `B_j x_j` | 37 or 73 |
| S then S, disjoint outputs | clean | 74 or 146 |
| S then R | still the one named term | one more than S then S |

S then S is legal when the caller observes outputs and the connector only at
the joint exit. The intermediate term is private to the pair. That is the
eliminated work: two source queries. It is not a paid rank-histogram change.
Ali Romman's heterogeneous-owner bound still excludes deferred restoration
that changes a catalogue contract. No instance of this batch is claimed inside
the selected supplier.

Base commit `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. The live input is the
certificate above. Pins are in [SOURCES.json](SOURCES.json). The task card is
in [TASK.json](TASK.json).

## Reproduce

Python 3.12 and the standard library. From the repository root:

```sh
python3 -B research/paired-connector-tail/verify.py
python3 -B scripts/research_package.py --package research/paired-connector-tail --check-only
python3.12 -B scripts/research_package.py --package research/paired-connector-tail
```

Expected verifier line:

```text
PASS_PAIRED_CONNECTOR_TAIL schedules=3 saved_per_pair=2 four_pair_queries=74 five_pair_queries=146 tails=[3, 4, 4]
```

The predecessor control, not repeated by this verifier, is:

```sh
python3 -B research/universal-connector-boundary/verify.py
```

Expected: `PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182`.

Orientation command `python3 -B scripts/research_baseline.py` prints
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. `make frontier1094-verify` was not run.
`PYTHONOPTIMIZE` was unset. `g++` 13.3.0 is `/usr/bin/g++`, the `c++`
alternative points there, and `libboost-dev` 1.83 is installed. The numpy,
sympy and scipy pins in `research/e8-bit-p111-tuned/requirements.txt` were
already present for the user install. This package does not import them.

Discussion writes are not in this session's GitHub interface. No discussion
post was sent, and the write was not retried.

## Open next questions

Can two disjoint all-mask batches that must return the original connector do
better than this two-query saving inside the same A/B alphabet? The published
words show a saving of two, not a minimum. A first step is a census of
length-11 source paths whose proper prefix boundaries already cover every
mask, then a check that two leftovers cancel. The predecessor's 945-path
census is the even ten-toggle class only, so it does not answer this.

Do the missing selected gauge44 local programs have an exit clear whose frame
equals the next call's entry clear on any of the 62 orientation changes in
the 144-call order? That is the same restoration question on the binding
supplier. The first step is to rebuild the slot-chain local program and
compare center-clear frames along `data/PLAN.json`. The provider bytes are
not in this checkout, and that chain was not run.

## Credit

The schedules, the 38-query and 74-query restored bounds, and the free-algebra
model are Ross Richardson's `research/universal-connector-boundary` (the PR934
lineage). This note only composes the unread final toggle across one pair.
Nick Petalas's open PR 7324 prices a different operation, a consuming reset
`z := 0`, and a different exit contract. The arity-four source event in open
PR 3909 changes the alphabet. The four-source clean-row tariff in open PR 7204
is a different price model. None of those results is replayed or improved here.

Prepared by a donated research session. Substantial AI assistance was used
for the algebra, the verifier, and these notes. No independent human review
is claimed. Apache-2.0.
