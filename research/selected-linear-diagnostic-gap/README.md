# Selected first-order diagnostic gap

**No new κ.** The selected frontier is unchanged.

## Scope and evidence

Task card `independent-moment`, scope **refined**. The original card asks for one
independent exact check of a selected pricing claim. Importing the retained
moment engines would trip that card's scope-change trigger, and those engines
already certify the endpoint. This package rebuilds the selected paid histogram
and encloses the first-order diagnostic `a < D/E` from
[autoresearch.md](../../autoresearch.md).

`D = m W - Σ n_r r` and `E = Σ n_r r ln(m/r)`, with `m = 73` and `W = 14336`.
The published native endpoint is the comparison value

`a = 67018507072324140917/40000000000000000000000`.

The histogram is not read from the saved aggregate. For each of the 69,120
owner roles, the width must equal the gauge44 helper width, the cells in each
owner bin must form a gap-free prefix, and the idle rank is the window capacity
minus that prefix. The gauge44 local profile is then added once per each of the
144 calls. The saved plan aggregate and `ASSEMBLY.json` `complex_profile` are
comparison targets only. They match the recount:

| Rank | Count |
|---:|---:|
| 1 | 349604 |
| 2 | 60192 |
| 3 | 62585 |
| 4 | 20448 |
| 5 | 11808 |
| 7 | 7 |
| 8 | 1152 |
| 48 | 4866 |

Idle remainder inside that sum: `{1: 2276, 3: 377, 7: 7, 48: 4866}`.
Rank mass `1,041,408`. Deficit `5,120`, equal both to `73·14336 - mass` and to
`14336 - 64·144`. Helper count `480`, centres `8`, physical dimension
`14,826`. The invoice integer `2·bit_length(stock) + 9909 + 252 + 1024`
recomputes to `16,469` with stock length `2,642`. That identity is already
enforced by the selected invoice; it is recomputed here from the recounted
helper count and is not a new reserve.

Logarithms use the odd series for `ln(1+x)` after reducing every ratio
`73/r` to `ln 2`, `ln 3`, `ln(5/4)` and three short `ln(1+x)` terms. Twenty-four
terms give a rational enclosure of the gap. The verifier proves

`5128032946218/10^18 < D/E - a < 5128032946219/10^18`.

So the published endpoint lies strictly below the diagnostic, and the diagnostic
overstates the feasible saving by a little more than `5.128032946218·10^-6`.
That separation is slack in the linear screen. It is not moment slack and not a
larger supplier endpoint. The exact moment remains the acceptance test.

Navinor's [discussion comment 18909949](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18909949)
and PR #1293 already report, from the published aggregate histograms, a complex
diagnostic ceiling near `0.0016805907097543` and decimal slack near `0.30%`.
That package is not in this checkout. This note does not repeat its moment-sign
check, its bit-supplier diagnostic, or its convexity argument. The added
statements are the role-and-window recount and the rational gap bracket above.

Four controls must fail: a role width shorter than the provider width, two
slices with the same offset, an endpoint placed at the diagnostic upper bound,
and a histogram whose rank mass leaves a nonpositive deficit.

Chooser seed `e5a891e2b3a91f41675273ab11ae8c7b`, scope key `c6f2494b197df3bc3591`,
base `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`, priority revision 2.
Marker: `PASS_SELECTED_LINEAR_DIAGNOSTIC_GAP`.

## Reproduce

Python 3.12, assertions left on (`PYTHONOPTIMIZE` unset). Standard library only.
From the repository root:

```sh
python3 -B research/selected-linear-diagnostic-gap/verify.py
python3 scripts/research_package.py --package research/selected-linear-diagnostic-gap
```

Pinned inputs, listed with SHA256 in [SOURCES.json](SOURCES.json):

- `research/complex-t16-rare-pattern-exchanges/data/PLAN.json`
- `research/complex-t16-rare-pattern-exchanges/OWNERS.json.gz`
- `research/community-frontier1094-audit/ASSEMBLY.json`

## Not checked

- The moment sign at `a`, the conservative endpoint, and the 47 outer inequalities.
- Climb and center events inside the gauge44 word. The pinned canonical-word
  SHA256 `16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219` is not
  a loose file here, so the 144-fold local profile is the declared
  `actual_paid_profile`.
- Orthogonal 73-column charts, prefix bit count 397, and `make frontier1094-verify`.
- A Lean proof. No new κ and no change to the selected record.

Discussion writes were not available to this session: the configured GitHub
interface can read discussions and cannot add them. No discussion post was
attempted, and none will be retried in this package.

## Open next questions

1. Does the gauge44 local paid profile still equal the declared
   `actual_paid_profile` when the climb and center events of the pinned
   canonical word are counted directly? That would remove the remaining
   aggregate from the 144-fold sum. Count those events in the word whose SHA256
   is `16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219`. The
   blocker is that those bytes are not a loose file in this checkout.
2. Can an enclosure other than the retained Mercator and base-two engines
   certify the moment sign of this recounted histogram at the published
   endpoint? The linear screen overstates the feasible saving by about
   `5.128e-6`, so only the exact moment decides acceptance. Enclose
   `Σ n_r (r/73)^(1-a) - 14336` with an explicit remainder tighter than
   `10^-24`. This package does not run that enclosure; a coarser bound cannot
   separate the published residual.

## Credit

The histogram and endpoint are Rohan Arun's #1094 rare-pattern exchanges on
Jeremy Kothe's #1087 packing, Hao Yan's T16 controller, and the retained
gauge44 line. The row-coefficient product is the integer already used by
`research/gauge44-slots-t16/code/invoice_allcold.py` and `t16/indep16.py`.
Josie Elliston's #1091 is the predecessor owner-window recount; this package
does not repeat that chart audit. Navinor's #1293 is the predecessor aggregate
`D/E` certificate. Selected review:
[docs/research/community-batch1099-review.md](../../docs/research/community-batch1099-review.md).

Substantial AI assistance drafted the verifier, the logarithm bounds, and this
note. AI assistance is declared without a product name. Apache-2.0.
