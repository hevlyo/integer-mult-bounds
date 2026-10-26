# One paid checkpoint does not lower the uniform connector budget

**Scoped alphabet extension and exact uniform-cost obstruction. No new kappa.**

The fixed universal-connector alphabet forbids an extra root. This package adds one call, and charges it:

```
S: w += z
```

`z` is the original dirty connector. `w` is one auxiliary dirty row. Source calls `B_j: z += B_j x_j` still touch only `z`. An output call may read either row, `y_i += A_i z` or `y_i += A_i w`. Every source row, `z`, and `w` may start dirty and must return to those initial values. Each `S` is one complete root call. It is not a free copy, a clean projection, or a second independent source root.

On the three-source all-7 batch the uniform optimum stays **20**. On the five-source all-31 batch it stays **74**. Every covering schedule that uses `S` at least once costs at least **76**. Eight checkpoints can realize the mask that every ten-toggle path misses, at cost **80**, which is worse than 74 when every complete call has the same positive price.

## Scope

Original card: `connector-alphabet-change`, scope key `ff4f5113ed2256ab19ed`. Selector seed `20f4988602bbc7215eb9b2af37e16dc0`. Track `recursive-interfaces`. Priority revision 2. Base `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`.

Scope status: **refined**. The card asks for one legally priced operation. The operation is this checkpoint, the pilot is the three-source all-7 batch, and the charged comparison is the five-source all-31 batch. The singleton source alphabet is not enlarged by adding sources.

The predecessor interface said there is no extra root connector. That is the premise this package changes. Combined source toggles, a reverse transfer `z += w`, and freely chosen source ports are a different alphabet. In particular, merged PR 1812 lets a source call choose either physical root and transfers in the direction `z0 += z1`. PR 3417 serializes uncoupled extra roots. Neither is this one-way checkpoint.

## Why two, four, or six checkpoints add no mask

Write source prefixes on `z` as `q` in `F_2^n`. Each `S` happens at a visited prefix `p_i` and replaces the source content `r` of `w` by `r XOR p_i`. Restoring arbitrary `z_initial` inside `w` forces the number of checkpoints to be even. Restoring the source content forces `p_1 XOR ... XOR p_{2m} = 0`.

A pair of `w` reads cancels `w_initial` only when both reads see the same checkpoint-count parity, and then the mask is a difference of two partial sums. That difference is a contiguous block of the `p_i` whose length is even. For `2m <= 6` every such block is already a difference of two visited `z` prefixes:

- length 2 is a pairwise difference;
- length `2m` is the full sum, which is 0;
- length 4, when six checkpoints are used, equals the complementary pair, again a pairwise difference.

So those checkpoints create no output mask outside the ordinary prefix-difference set of the source walk. The same argument applies to every walk, not only the ten-toggle words. A pair of reads on `z` and a pair on `w` still cannot share the cancellation of `z_initial` with the cancellation of `w_initial`.

## Uniform five-source bound

Let every complete call cost 1. The all-31 batch has 31 outputs and 5 sources.

- Each active source is used an even number of times, at least twice, so there are at least 10 source calls. Each output needs at least two reads. An output that mixes the two roots, or that uses four reads on one root, pays at least four reads.
- No canonical ten-toggle word covers all 32 masks. The independent census matches the predecessor: 945 pairings, maximum coverage 31, digest `1419cd57230138cc8a37c0411c513cf4109d0bba03c10cd1196e137a9a10ea9c`.
- With at most six checkpoints, a covering schedule therefore needs at least 12 source calls. Two cancelling checkpoints on the twelve-toggle repair

  `B2 B0 B2 B1 B2 B0 B3 B1 B4 B2 B3 B4`

  are legal and cost 76. Zero checkpoints, with that repair's 62 output reads, cost 74.
- Eight or more checkpoints cost at least `10 + 8 + 62 = 80`, even if every output uses only two reads.

Thus the extended alphabet still has optimum 74, attained without `S`, and every schedule that uses `S` costs at least 76.

## Eight-checkpoint witness

The predecessor's near-miss word is `B0 B1 B2 B0 B3 B1 B4 B2 B3 B4`. It misses mask 21. Cinna Davis's placement in discussion 1412 puts checkpoints at source-boundaries `1,2,3,3,4,6,8,9`. The source contents of `w` immediately after the third and seventh checkpoints are 5 and 16. Both have odd checkpoint parity, and `5 XOR 16 = 21`. The compiled schedule uses 10 source calls, 8 checkpoints, and 62 output reads: **80** root calls. Mask 21 is read from `w`. An alternate placement, counts `(0,1,1,0,1,0,1,2,1,1,0)`, also covers at 80.

Both schedules pass an L=1 identity-map check on every source basis vector, zero input, and all four dirty patterns of `(z, w)`, with output rows starting at 0 and at 1. Sufficiency for a general linear pair is the same cancellation as in the predecessor: two reads on one root cancel that root's initial dirt and contribute the prefix difference. This package does not replay the predecessor's noncommuting matrix banks.

## Three-source pilot

The word `B0 B1 B0 B1 B2 B2` supports every one of the 8 masks. Fourteen output reads and six source calls cost 20, which meets `2 * (3 + 7)`. All 4,096 dirty L=1 states, including `w`, accept that schedule. Deleting one read of mask 7 is rejected. One checkpoint followed by a restored source pair keeps a dirty `z` inside `w`. No placement of two, four, or six checkpoints on any of the 15 canonical three-source words adds a mask. Eight checkpoints would cost at least 28, so they cannot beat 20 at a positive unit price.

## Reproduce

From the repository root, with Python 3.12 and `PYTHONOPTIMIZE` unset unless noted:

```sh
python3 -B research/universal-connector-boundary/verify.py
python3 -B research/checkpoint-connector-copy/verify.py
python3 -I -O -B research/checkpoint-connector-copy/verify.py
python3 -B scripts/research_package.py --package research/checkpoint-connector-copy
```

The orientation control is `PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182`. The package status line is:

```text
PASS_CHECKPOINT_CONNECTOR_COPY pairings=945 max_coverage=31 queries_without_s=74 min_queries_using_s=76 witness_queries=80 checkpoint_states=5,16 mask21=21 three_dirty=4096 sha5=1419cd57230138cc8a37c0411c513cf4109d0bba03c10cd1196e137a9a10ea9c
```

`scripts/research_baseline.py` returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` for the selected bindings. That is not a cold replay. `make frontier1094-verify` was not run.

## Open next questions

1. Can a row-add `w += z` be priced strictly below one quarter of both the repeated source call and the repeated output call in the predecessor's tape account? That is the threshold at which the 80-call witness would beat both singleton repairs. The first step is to charge one length-L row add with the same head-travel and scratch rules as `research/universal-connector-boundary/README.md`, then compare eight such charges with two extra `B2` leaves. This package blocks that comparison: it charges every complete call as one root query and does not build the tape trace.
2. Does one checkpoint mixed with one already published two-source toggle beat 74 under the same unit ledger? A mixed alphabet is a second new symbol. The first step is to charge both and test this pilot word, after checking that the schedule is not the 72-query DUO construction. This package stops at the single checkpoint.

## Credit

Ross Richardson's `research/universal-connector-boundary` (PR 943 / PR 934 lineage) supplies the singleton alphabet, the prefix-difference reduction, the 945-pairing boundary, and the twelve-toggle repair. Cinna Davis's discussion 1412 named this checkpoint, the pilot word, the boundary list `1,2,3,3,4,6,8,9`, and the eight-copy threshold. That claim had no completion comment; this package checks the placement and proves the uniform budget. The alternate eight-copy counts were found by a direct search on the same pilot.

Substantial AI assistance was used to derive the parity collapse, check the schedules, and draft the notes. No coding-agent product is named. No independent human review is claimed. New work is Apache-2.0.

Discussion writes to `CrocSwap/integer-mult-bounds` are forbidden for this account. The claim is recorded in this package and the pull request. The write was not retried.

## Unrun obligations

No selected-supplier admission, no change to kappa, and no full multiplication theorem. Noncommuting dense banks, leaf prices, and the predecessor's tape trace were not replayed. Unequal positive prices are not optimized. Odd characteristic, a reverse transfer, and more than one auxiliary row are outside the proof. The selected cold replay was not run.
