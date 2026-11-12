# Masked rank of an E8 double frame

**Scoped negative result for a moment improvement, plus a label-rank
classification. No new κ and no supplier.**

## Scope and evidence

Original card: `complex-masked-decoder` (scope key `2a6f2c726b78f9ae7d26`),
priority revision 2. Scope status: **refined**. The card asks whether one masked
decoder can improve the complete moment. This package fixes the alphabet first,
as the card's opening experiment asks, and stops before building a network.

The alphabet is the sixteen root lines `F0 ∪ F1`: the coordinate frame together
with any of the 1260 frames in its complement. The identity is the masked
E-graph system on those lines only: diagonal entries 4, and zeros on orthogonal
pairs. Odd inner-product entries are free. This is not the eight-term all-pairs
search already proved for punctures of size at most 24.

On every such alphabet:

- every masked matrix has rank at least 8, and `2G` attains rank 8;
- every perfect matching of the odd cross graph gives an explicit rank-8 masked
  matrix whose eight terms have label-pairing cost 16;
- the label-pairing rank of the sixteen lines is 8, 6, or 4 according to the
  three frame-pair relative types (896, 336, and 28 frames).

Inadmissibility of `F1`, which blocks an all-pairs frame-pair decoder on the
complement, does not lower this masked term count and does not lower the
separated matching cost. It does lower the alphabet's label rank. The written
argument is in [PROOF.md](PROOF.md). The census is exhaustive, not a sample.

The selected frontier is unchanged. Orientation used the card's positive
control `PASS_COMPLEX_DECODER_FIELD_EXTENSION_S44` at base
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Predecessor geometry and the
admissible/inadmissible split 896/364 come from
`research/complex-frame-pair-decoders` (PR968; DreamingOfClouds' PR717 for the
masked model and the B14 lines). This package reconstructs the roots, frames,
and pairings itself and does not import that verifier.

## Reproduce

From the repository root, Python 3.10+ with assertions enabled. The run here
used CPython 3.12.3. No third-party packages. `PYTHONOPTIMIZE` must be unset.

```sh
python3 -B research/double-frame-masked-rank/verify.py
```

Expected final line:

```text
PASS_DOUBLE_FRAME_MASKED_RANK frames=1260 types=896+336+28 label-ranks=8/6/4 matchings=356608 controls=5
```

The same command is the registered replay:

```sh
python3 scripts/research_package.py --package research/double-frame-masked-rank --check-only
python3.12 -B scripts/research_package.py --package research/double-frame-masked-rank
```

The checker enumerates all 1260 frames, all 356,608 odd perfect matchings, the
cross-Gram identity `N^T N = 4 I`, the share-4 graphs, and the label ranks. Five
negative fixtures must fail: an orthogonal pair (label block `J_2`, rank 1), a
zero cross block (Schur complement `I`), one corrupted orthogonal entry, one
zeroed row of a real cross-Gram, and a one-frame histogram drift.

## Accounting and checks not run

No word, frame schedule, restoration, or odd-entry correction is built, so there
is no paid profile and no moment. The separated cost 16 is not claimed as a
lower bound for every factorization. Not run: `make frontier1094-verify`, any
selected-frontier cold replay, Lean, and a search for a mixed factorization of
cost below 16. `g++` was already `/usr/bin/g++` and `libboost-dev` was already
installed; this package does not compile anything.

Discussion writes on `CrocSwap/integer-mult-bounds` were forbidden
(`Resource not accessible by integration` on `createDiscussion`). The finding
was not posted. That attempt was not repeated.

## Open next questions

1. On one fixed frame of type `(0, 16), (4, 12)`, is every complex factorization
   of the separated matching matrix of label-pairing cost at least 16?
   *Why it matters:* the label rank on that alphabet is 4, not 8, so repeated
   rows might let a mixed factorization undercut the separated cost 16. A cost
   below 16 would be the first sign that inadmissibility helps this masked
   relaxation; a matching lower bound would close that hope on the sixteen-line
   alphabet. *First step:* restrict to the four label classes of one such frame
   and decide the minimum of `Σ rank(supp v_t, supp w_t)` over
   `Σ v_t w_t^T = I_8`. *Blocked by:* cross terms between classes can cancel, and
   this package only prices the separated matching.

## Credit

The line model and the masked E-graph reading are DreamingOfClouds' PR717. The
1260-frame census and the admissible count 896 are the frame-pair package's.
PR1292 (discussion 1275) already shows that the masked rank-8 solution set is
infinitesimally rigid at `2G` on each 104-line frame-pair puncture, and it uses
the same 896/336/28 split. This note is the complementary 16-line alphabet: the
global Schur rank, the separated matching cost, and the label-rank trichotomy.
Prepared by a research contributor with substantial AI assistance.
Apache-2.0.
