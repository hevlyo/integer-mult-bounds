# Selected complex endpoint enclosure

**Scoped audit of the selected certificate's complex moment signs and outer
grid. No new κ and no change to the selected frontier.**

## Scope and evidence

Task card `independent-moment`, scope key `c6f2494b197df3bc3591`, chooser nonce
`6baf9c652cdae179eafc865c06c39688`, priority revision 2. Base commit
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Scope status: **refined**. The card
allows a certified enclosure by a different method. This package does that for
one object: the selected gauge44/T16 complex histogram and the outer grid
stored beside it. It does not rebuild the histogram from scalar operations.

The pinned inputs are the selected record, `ASSEMBLY.json` for that record, and
`research/complex-t16-rare-pattern-exchanges/data/PLAN.json`. The profile counts
agree. The parameters used by the retained admission are `M = 73`,
`live = T*8*112 = 14336` and deficit `5120`, checked by the rank-mass identity
`M*live - Σ r n_r = 5120`. The halving inequality `73^2 > 2*48^2` holds for this
histogram; the enclosure does not use it.

At the published native complex endpoint the independent upper bound is strictly
below one. At the next `10^-24` grid point the independent lower bound is
strictly above one. The same signs hold for the published conservative endpoint
after the retained surcharge `32*M*(number of calls)/(10^16*live) * exp(a ln M)`.
Adding that surcharge at the native endpoint pushes the lower bound above one,
and one extra rank-48 call does the same. A separate one-child fixture equals
`1/2` at saving zero and equals `3/2` for three children.

The seven-step common-rate recurrence, its cutoffs, the `10^18` κ grid and all
47 outer slacks are recomputed from those endpoint rationals. They match the
selected assembly exactly, including
`κ = 836330098538459/500000000000000000`. The first argument of the slack map is
the bootstrapped common rate, which is the calling convention of the retained
assembly driver. The bit endpoint enters that recurrence through
`min(bit, (1-β) complex) - 10^-27`. Four mutations (next κ grid point, `η = 0`,
`β = 0`, `β = 1`) each make some slack nonpositive.

Logarithms are not the retained Mercator reduction to `[1, 3/2)` and not the
artanh series. `ln 2` is the sum of `ln(1+1/k)` for `k = 64..127`, and every
other logarithm is reduced to factors of that shape plus one alternating series
`ln(1+z)`, `z < 1`. Exponentials are degree-30 Taylor polynomials with a
geometric tail. Bounds are outward at scale `10^60`. No function from
`engines/moment.py`, `engines/base_two_moment.py` or `engines/outer.py` is
imported.

The selected conditional saving stays the published value. This is not a
supplier improvement, not a word-level ledger, and not a Lean multiplication
theorem. All-size/compiler, common-label/mutable-source, whole-call hosting,
precision/tape, analytic-transfer and bit H1–H5 assumptions remain inherited.

An overlap refresh at 2026-11-13T12:25:15Z covered 797 open PR records and
7391 discussion records, with complete pagination. Closed PRs were searched
only through local notes and the ledger. Matches on the selected κ mostly cite
that fraction. [Discussion comment 19022543](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19022543)
checks stored assembly cutoffs and both recorded κ values from the receipt.
`research/gauge44-barch-t16` prices a T16 profile by importing the retained
moment engines. This package does not import those engines.

Discussion writes were not available: the session's GitHub interface is
read-only and there is no Discussion posting action. No claim was posted, and
the write was not retried.

## Reproduce

From the repository root, with `PYTHONOPTIMIZE` unset, CPython 3.12, standard
library only:

```sh
python3 -B scripts/research_package.py --package research/selected-complex-endpoint-enclosure --check-only
python3 -B scripts/research_package.py --package research/selected-complex-endpoint-enclosure
```

Expected marker: `PASS_SELECTED_COMPLEX_ENDPOINT_ENCLOSURE`.

Not run: `make frontier1094-verify`, the T16 word census, Lean, and any
regeneration of `ASSEMBLY.json`.

## Open next questions

The bit supplier is the other half of the same assembly, but this package never
sees its histogram. `ASSEMBLY.json` stores the bit endpoint and its residuals,
not the rank counts. The smallest follow-up is to apply this same series,
without importing the retained engines, to the pinned PR589 nine-stage profile
at width 64, including the bad-residue surcharge, and to compare the sign with
the published bit residuals. That would catch a bit-side transcription error
that cannot move the selected κ while the complex side binds. It is blocked
here because the bit histogram is not one of the pinned inputs.

A second, larger gap is the histogram itself. Agreement of `PLAN.json` with
`complex_profile` does not prove that the scalar word emits those counts. The
useful step is the frozen T16 literal-window census in an isolated worktree,
with the checked native local word. This package does not run that replay.

## Credit

The selected assembly and the T16 profile are Rohan Arun's PR1094 composition
of the gauge44/T16 line (jeremykothe2 and the retained PR1087/PR799/PR589
lineage). The seven-step outer recipe and the 47 slacks are the retained
balanced assembly of eumemic, icekylinx and Zhihao Chen. The predecessor
`independent/price_profile.py` prices an earlier 7168-role profile by importing
the Mercator and artanh engines; this package does not call that driver.

Prepared by a donated research session with substantial AI assistance. The
assistant derived the enclosure and wrote the verifier. This is not an
independent human review and not a proof-kernel check. New material is
Apache-2.0.
