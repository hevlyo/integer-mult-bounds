# One added total does not lower a pinned P104 frame-pair copy sum

**Scoped negative result. No new κ and no selected-frontier change.**

On one pinned admissible frame-pair decoder, every real single-lift
correction

```text
sum_j x_j (y_j - a_j z)^T + (Xa) z^T = 2G
```

has label-pairing copy cost at least **56**. The original eight cost-7
terms attain 56, and so does moving any one of those terms into the ninth
slot. Frames, restoration and hosting are charged zero in this relaxation.
The copied-information sum still does not fall, so the relaxation has no
headroom on the copy term of the ratio-optimal eight-term budget.

The eight reader columns stay fixed. They are the first cross-frame decoder
on the first admissible partner frame of the coordinate frame, in the
enumeration of `research/complex-frame-pair-decoders`. The live set is that
pair's 104-line complement. Transpose is ordinary transpose. The argument
is the rank-nullity note in [PROOF.md](PROOF.md); [verify.py](verify.py)
checks its finite premises, equality fixtures and failure controls.

This is the overcomplete (nine-term) relaxation of one frame-pair decoder.
It is not the eight-term all-pairs search, and it is not Mihir Srivastava's
coordinate P112 single lift, whose floor is 64 on a different reader
matrix. The asymmetric sources are what make the parity corank equal to the
number of active readers rather than zero.

## Reproduce

From the repository root, with Python 3.12 and the standard library only.
`PYTHONOPTIMIZE` may be unset or set; the checks raise explicit exceptions.

```sh
python3 -B research/p104-frame-pair-single-lift/verify.py
python3 -B scripts/research_package.py --package research/p104-frame-pair-single-lift
```

The verifier's final line is

```text
PASS_P104_FRAME_PAIR_SINGLE_LIFT frame=96,95,85,74,47,38,14,13 patterns=3272 census=495/16 specials=8 floor=56 no_new_kappa
```

The registered replay prints `PASS_REGISTERED_RESEARCH_PACKAGE` with
outcome `negative-result`. Both commands are read-only.

## What is certified

- The E8 line model, the pinned frame `F1 = (96, 95, 85, 74, 47, 38, 14, 13)`,
  and its first decoder. The Gram identity holds on all 10,816 live pairs.
- Eight reader label spans of dimension 8 and eight original costs equal to 7.
- All 3,272 sign patterns with at least two active readers, up to global
  sign. Each parity system has corank equal to the number of active readers
  and is spanned by those readers' original kernels.
- All 511 nonzero label functionals on the reader matrix: 495 supports have
  rank 8, and 16 have rank 7. The kernels are the eight axes and eight
  explicit weight-4 directions.
- Each weight-4 direction and its negative has ninth-reader span 8 and
  parity-sum quotient rank 1.
- Equality fixtures: the zero correction costs 56, moving the first term
  costs 56 with vector `(0,7,7,7,7,7,7,7,7)`, and one dense correction on a
  weight-4 direction is strictly above 56.
- Failure controls: a one-entry source mutation breaks the Gram identity;
  rebuilding the parity systems from reader signs yields corank 0 on every
  pattern; a weight-8 vector is not a deficient kernel; an empty support
  has rank 0; exactly eight computed kernels are axes.

## Scope

Covered: real `a` and `z`, this one reader matrix, one added total, exact
equality on every live pair, and the optimistic copy-rank sum.

Not covered: the other admissible frames, two or more added totals, a
change of the eight readers, masked identities, complex scalars, and any
positive frame, restoration, hosting or recursive-child charge. Inherited
all-size, compiler, common-label, mutable-source, hosting, precision, tape,
analytic and bit-interface assumptions of the selected construction remain
untouched. This is not a supplier and not a multiplication theorem.

The selected conditional κ stays
`836330098538459/500000000000000000`. Cold replay
`make frontier1094-verify` was not run. The orientation command

```sh
python3 -B research/complex-decoder-field-extension-seed44/verify.py
```

returned `PASS_COMPLEX_DECODER_FIELD_EXTENSION_S44` before this experiment.
That replay is a predecessor check, not a premise of the new theorem.

## Task

Card `complex-masked-decoder`, scope key `7acfe4d9cac04f7ba4cb`, selector
nonce `e3b6b9b79d8c7c1a4f913ad65565283d`, priority revision 2. Base
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Scope status: **refined** to one
overcomplete family, as the card allows. The eight-term all-pairs search
inside its proved scope was not repeated.

An overlap refresh on 2026-10-19T12:25:53Z, with complete pagination of 767
open PR bodies and 2,606 discussion records, matched the phrases
`frame-pair single lift`, `P104 single`, `p104-frame-pair` and
`weight-4 frame-pair` only in this package. Nearby results are different
objects: the coordinate P112 single lift, the eight-term all-pairs floor,
and other nine-term or masked families. Discussion writes for this account
return FORBIDDEN / Resource not accessible by integration. No claim was
posted, and the write was not retried.

## Open next questions

1. Does the same copy floor hold for every admissible frame, or only for
   this first clique? A single frame whose ninth term costs less than 56
   would be a new copy budget inside the ratio-optimal puncture. The first
   step is to rerun the census and the 3,272-pattern corank check on the
   next admissible clique in the same enumeration. Nothing in the argument
   uses a special property of this clique beyond the certified census, but
   that census is not yet known for the other 895 frames.

2. Can two added totals lower the copy sum? The single-correction identity
   is the smallest overcomplete relaxation, and a second free column can
   evade both the k=1 subadditivity step and the nine-dimensional kernel
   bound used here. The first step is to write the two-correction identity
   with both new readers kept inside the present eight-dimensional reader
   span and to test its parity map. The blocker is that the second source
   adds an unconstrained column, so the sign equations no longer close by
   themselves.

## Credit

The frame-pair model, the cost-7 mechanism and the eight-term floor are
from the frame-pair decoder package (PR968's line of work, including
DreamingOfClouds' PR717 model). The single-lift identity and the
sign-pattern annihilator method are adapted from Mihir Srivastava's
coordinate P112 note `research/p112-single-lift`. The ordinary-transpose
complex eight-term floor in `research/complex-decoder-field-extension-seed44`
is the orientation predecessor and is not reproved here. Apache-2.0.

Prepared for the hevlyo research account. Substantial AI assistance was
used to isolate this single-lift question, adapt the parity argument, and
write the checker and notes.
