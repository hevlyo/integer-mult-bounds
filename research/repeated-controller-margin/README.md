# Repeated whole-controller rank margins

**Exact negative rank-mass result for one recovery policy. No new κ.**

## Scope and evidence

Original card: `independent-moment` (scope key `c6f2494b197df3bc3591`), chooser
nonce `0ce08b5d1986538ef8eca6579708ff16`, track `independent-verification`.
Scope status: **changed**. The checkout's selected moment already has an
independent price in `research/community-frontier1094-audit/INDEPENDENT1094.json`.
The live upstream handoff left a different pricing claim unchecked: the
repeated-evaluation barrier in open
[PR #4623](https://github.com/CrocSwap/integer-mult-bounds/pull/4623)
(`fd5d3be12b9d6ee92c8fa089d95bd529c3236563`).
[PR #4625](https://github.com/CrocSwap/integer-mult-bounds/pull/4625)
checked the idle-mass identity and the tangent bounds, and left this barrier
open.

The changed controller is charged once for its main outputs and `K>=2` times
for its local helper and paid invoices. At exponent `t=1` the rank-mass margin
is exactly

| Lane | `h(1)` | Two-evaluation margin |
|---|---:|---|
| Complex, `b=8`, `v=112` | `-1856` | `-1920 p - 3616` |
| BIT, `b=7`, `v=111` | `-1617` | `-1680 p - 3138` |

Both coefficients are negative, so every pair count `p>=1` and every `K>=2`
is a rank-mass loss. The added-evaluation step itself is a negative affine
form, so `K=2` is the least negative case. At `p=2` the bills are `-7456` and
`-6498`. Crediting those same main outputs twice instead yields `+160` and
`+162`.

Every positive signed local term lies strictly above the separator (`6` for
complex, `15/2` for BIT), and every negative term lies strictly below it. The
Jensen base is at least `1+b`, which is also above the separator, and the thin
query has rank 1, below it. Under that coefficient hypothesis,
`F(t)/separator^t` is strictly increasing, so negativity at `t=1` implies
negativity for every smaller `t`. The derivative of `a^t` is the standard
calculus fact used by the predecessor; this package checks the hypothesis and
the `t=1` values, and it does not formalize that derivative. A synthetic
profile `5*2^t - 3*4^t` has a positive term below any separator above 4, and
it is negative at `t=1` but positive at `t=0`.

The local invoices are rebuilt from the vendored predecessor bytes:

- complex helpers `{4:28, 7:7, 8:47, 9:326}` and paid calls
  `{1:2237, 2:388, 3:494, 4:147, 5:36, 8:8}`;
- BIT thick count 18, after removing main targets, whole-idle costs and thin
  queries: helpers `{8:439}` and paid calls
  `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`.

Pins, upstream paths and SHA-256 values are in [PINS.json](PINS.json). The
checker does not import or run `budget.py`.

This is not a supplier admission, a decoder obstruction, a precision bound, or
a change to the selected frontier. Discussion writes from this account are
forbidden (`addDiscussionComment` returned FORBIDDEN). That limitation is
recorded here and was not retried.

## Reproduce

Python 3.12, standard library only. `PYTHONOPTIMIZE` was unset. From the
repository root:

```sh
python3 -B research/repeated-controller-margin/verify.py
python3 -B scripts/research_package.py --package research/repeated-controller-margin
```

The direct command prints `PASS_REPEATED_CONTROLLER_RANK_MARGINS`.

## Checks not run

The selected cold replay `make frontier1094-verify` was not run. The tangent
enclosures at `C=.006` and `C=.007`, the copied-input decoder, and the
precision lemma in PR #4623 were not rechecked. No proof assistant was run.

## Open next questions

1. Does the exact copied-input X decoder in PR #4623 fail every concave moment
   on these same invoices? That is the other recovery route left open by
   PR #4625. First step: rebuild its claimed per-port query rank `p-1` and
   compare the `t=1` mass. Blocked by the absence of that schedule from the
   vendored invoices.
2. Can two evaluations share internal paid calls and avoid the single
   main-output credit? The margin above charges the main outputs once. First
   step: name the shared calls and recompute the `t=1` mass. Blocked because
   no shared-call schedule is in the vendored invoices.

## Credit

Dillon's PR #4623 states the repeated-evaluation policy and the published
affine margins. Ryanson Jonathan's PR #4625 checked the complementary idle-mass
identity and tangent bounds. The complex invoice is Cinna Davis's joint-helper
lattice record, and the BIT invoice is the query-thinned controller record, at
predecessor head `fd5d3be12b9d6ee92c8fa089d95bd529c3236563`. Apache-2.0.

Prepared with substantial AI assistance. No coding-agent product is named.
This is not an independent human or formal-kernel review.
