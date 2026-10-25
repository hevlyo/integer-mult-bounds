# Two five-source batches can skip the intermediate connector restoration

**Recursive-interface certificate. No new kappa and no selected-supplier admission.**
On the pinned singleton source-toggle connector, two consecutive all-31-mask
batches with disjoint output rows have exact complete-query cost **144**.
Two batches that each restore the connector cost **148**. The four saved
queries are source toggles. The intermediate return of the connector to zero
is not required.

The one-batch restored optimum is unchanged at **74**. A single batch must
still exit clean, and every universal walk of length 10 exits dirty.

```sh
python3 -B research/five-source-dirty-handoff/verify.py
```

Expected:

```text
PASS_FIVE_SOURCE_DIRTY_HANDOFF length9_covers=0 length10_covers=188 length10_zero_end=0 handoff_queries=144 restored_queries=148 witness_b_leaves=152 restored_b_leaves=240 leaf_screen_through=12 min_segment_leaf_through_12=76
```

Python 3.12 and the standard library suffice. `python3 -I -O -B` passes the
same line. The checker does not import the predecessor and does not write
files.

## Task card

```text
Task ID / proposed scope key: persistent-boundary / 026be4b6e61971d51838
Base commit: ef5f39403610d231a0c27e8a6b4f08c10209bcd6
Selector seed: d5d9544b2eed6422f062a78ef710d59c
Catalogue: priority revision 2, SHA256 89b5928bc92c81e2647b6d702a7ad85a6795b8f44e2eb267b2ff3145d8f2b2ce
Selected record SHA256: 10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32
Predecessor: research/universal-connector-boundary (Ross Richardson, PR943/PR934 lineage)
Concrete object and question: two consecutive all-31-mask batches, five singleton sources, disjoint outputs, one shared dirty connector. Can the second batch accept the first batch's exit state and thereby delete the intermediate restoration?
Scope status: refined. The card asks for one specified pair and one deferred restoration. The alphabet is unchanged.
Existing restriction being changed: the predecessor restores the connector at the end of every batch. Here only the pair's final exit must be clean.
Method: exhaustive restricted-growth census of singleton walks through length 12, plus one explicit doubled witness and a symbolic coefficient replay.
Nearest overlap: the predecessor's closed one-batch bound, and later alphabet extensions (combined toggles, higher arity). Those extensions add an operation. This package does not.
Optimistic budget: fewer than 24 source toggles for the pair, with both output bills still 62 reads.
Success evidence: unit-cost optimum 20 source toggles and 144 root queries. Falsifier: any universal walk of length at most 9, or a length-10 universal walk that ends clean.
Time cap: one session. Stop at five sources and two batches.
```

## Contract

The predecessor's interface is the live pin
[research/universal-connector-boundary/README.md](../universal-connector-boundary/README.md).
Sources `x_j`, connector `z`, and output rows are distinct and arbitrarily
dirty. The only root operations are `B_j: z += B_j x_j` and `A_i: y_i += A_i z`.
Maps are exact `F2`-linear and need not commute. There is still no free copy,
combined toggle, direct product query, overwrite, or second connector.

Call `H` is one all-31-nonzero-mask batch on its own 31 output rows:

- Entry state `q_in` is the source parity of `z`.
- The call applies a length-10 singleton walk and 62 paired readouts.
- Exit state is `q_in XOR e` with `e ≠ 0`.
- Each child call still restores its private scratch and tape heads.
- Output rows of the two calls are disjoint, so the second call does not
  reconstruct the first call's targets.

The witness walk, in first-use coordinate order, is

```text
B0 B1 B0 B2 B0 B1 B0 B3 B4 B3
```

Its prefixes are `0,1,3,2,6,7,5,4,12,28,20`. The exit is `20`, which is the
sum of the two once-used coordinates. Repeating the same walk sends `20` to
`0`. Both segments' prefix-difference sets are all of `F2^5`.

Under unit complete-query cost the normalized comparison is

```text
C(H, H) = 20 source toggles + 124 readouts = 144
C(R, R) = 24 source toggles + 124 readouts = 148
```

where `R` is a batch that must exit clean. The saved work is the intermediate
restoration, not a relabeling of one batch's scalar recurrence.

## Why 20 source toggles is exact

Rename coordinates by first appearance. Every walk becomes one restricted-growth
word, and this renaming preserves universality, the property of ending at `0`,
and the sorted multiplicity. The Stirling totals
`sum_{k=0..5} S(9,k) = 18002` and `sum_{k=0..5} S(10,k) = 86472`
match the enumerator's leaf counts.

No word of length 9 has all 32 prefix differences. Exactly 188 words of length
10 do, and none ends at `0`. Therefore every universal singleton walk has
length at least 10, and every length-10 universal walk exits dirty. Differences
are translation-invariant, so each batch of the pair needs at least 10 toggles
whatever its entry state is. The doubled witness attains 10+10 and ends clean.

A restored batch is a universal walk that ends where it started. Its length is
even. Length 10 is impossible, and the published repair

```text
B2 B0 B2 B1 B2 B0 B3 B1 B4 B2 B3 B4
```

is a universal closed walk of length 12. So a clean exit costs at least 12
source toggles. Two clean batches cost at least 24. The handoff saves exactly
four.

Each nonzero output row needs an even number of reads, because the coefficient
of the entry dirt is the read parity, and it needs at least one pair in order
to see a nonzero mask. Disjoint rows cannot share reads. Each batch therefore
needs at least 62 reads, and the witness uses 62. The root-query bills 144 and
148 are exact in this alphabet.

The published controls used to tie the difference routine to the predecessor
are the four-source prefixes `0,1,3,2,0,4,12,8,0` and the ten-toggle word that
misses only mask 21. Both are rechecked.

## Factor-length pricing

The predecessor's balanced leaf recurrence gives prices `ell(1..5) = (1,4,10,16,28)`.
Assigning expensive factors to rare toggles, the witness multiplicity
`(4,2,2,1,1)` costs **76** primitive `B` leaves. The doubled schedule costs
**152**. Each restored batch has multiplicity `(4,2,2,2,2)` and costs **120**,
so two restored batches cost **240**. Output leaves stay `124` in both
schedules when every `A` factor has length 1. These are charged constructions.

The 120-leaf restored figure is the minimum over every closed universal walk:
any such walk uses five positive even counts, and the cheapest composition of
length at least 12 puts the extra pair of toggles on the price-1 factor.
The 76-leaf open figure is the minimum only through length 12. The census
found minimum assignment costs 76, 77, and 78 at lengths 10, 11, and 12.
A longer walk with multiplicity `(L-4,1,1,1,1)` would be cheaper if one
exists. No such optimum is claimed.

## What was run

Orientation, from this checkout, with `PYTHONOPTIMIZE` unset:

```text
python3 -B scripts/research_baseline.py
-> PASS_RESEARCH_BASELINE_BINDINGS_ONLY
   binding primitive complex
   kappa 836330098538459/500000000000000000
```

That is a source-bound arithmetic check, not `make frontier1094-verify`.
The full selected cold replay was not run. This package does not touch the
selected assembly, and the C++ toolchain was not used. `g++` 13.3.0 is the
active `c++` alternative and `libboost-dev` 1.83 is installed; neither is an
input to the certificate.

Checker checksums that are not otherwise headline claims: 4,716 universal
restricted-growth words of length 11, all dirty, and 68,328 of length 12, of
which 1,116 end clean. Those counts are frozen so a drifted enumerator fails.

## Limitations

- No instance of this connector is claimed inside the selected supplier.
  Common-label realization, hosting, frames, precision, tape, and the bit
  H1–H5 obligations are uninstantiated. Kappa does not change.
- One restored batch is still 74 queries. The length-10 walk is illegal as a
  one-batch schedule because its exit is dirty.
- Three copies of the witness end at `20`, not at `0`. The two-batch identity
  uses characteristic two (`e XOR e = 0`) and does not price a third batch.
- Unequal `B` prices above length 12 were not optimized.
- Odd characteristic, weight-2 steps, shared output rows, and a second
  connector are outside the contract. Reusing one output row would require a
  charged delivery or a further restoration; that cost is not analyzed.
- The certificate is a finite exact argument plus an exhaustive census. It is
  not a Lean proof or a multiplication theorem.

Discussion writes to `CrocSwap/integer-mult-bounds` are forbidden for this
account (the integration returns FORBIDDEN). The claim is recorded in this
package and the pull request. The write was not retried.

## Open next questions

1. **Unequal leaf prices past length 12.** A covering walk of length `L>=13`
   with sorted multiplicity `(1,1,1,1,L-4)` would cost `L+54` under
   `(28,16,10,4,1)`, which is below 76 once `L<=21`. That would make the
   doubled witness's 152 `B` leaves suboptimal without changing the unit-cost
   theorem. First step: continue the same restricted-growth census at length
   13 and reject a branch whose optimistic remaining assignment cannot beat
   76. Blocker: this package stops at length 12 on purpose; the shape was
   absent through that bound, which is not an argument for longer walks.

2. **Three consecutive batches.** Two copies restore the connector because
   the endpoint is added twice. Three copies leave endpoint `20`. First step:
   among the 188 length-10 restricted-growth covers, search for three endpoints
   that sum to `0` and price 30 source toggles against three restored batches
   at 36. Blocker: the search was not run, and a failed search would be a
   statement about length 10 only.

3. **Same output ports.** If the second batch must reuse the first batch's
   31 rows, the caller has to deliver or copy those results before the rows
   can be overwritten. First step: charge one concrete copy of 31 rows and
   compare it with the four saved source toggles. Blocker: no delivery price
   is pinned by the predecessor's root-query model, so the comparison needs
   an explicit copy contract before it can falsify the saving.

## Credit

The singleton alphabet, the prefix-difference reduction, the four-source word,
the ten-toggle obstruction, and the twelve-toggle repair are Ross Richardson's
`research/universal-connector-boundary`, following the PR934/PR943 connector
lineage recorded in that package's NOTICE. This package adds the open-walk
minimum and the two-batch dirty handoff. It does not reuse the predecessor's
executables.

Prepared by an AI-assisted research session. Substantial AI assistance was
used for the enumeration, the witness check, and the writing. New work is
Apache-2.0. No independent human review is claimed.
