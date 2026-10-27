# Exact eight-term copy cost on every 16-line frame pair

**Scoped exact cost. No new κ and no change to the selected record.**

On each of the 1,260 ways to add one E8 frame to the coordinate frame, the
16 live lines have an exact all-pairs factorization into eight terms of
label-pairing rank 2. The copied-information cost is exactly 16 for every
real or complex eight-term factorization that uses ordinary transpose. The
same matrices attain the even-entry mask, so masking the odd cross pairs does
not lower this eight-term charge. The fixed coordinate-reader form of the
same statement is also sharp at 16.

The 16 lines are the puncture of a P104 frame pair, not the 104-line live
complement bounded by `research/complex-frame-pair-decoders`. That complement
bound is not reopened. The ratio here is 16/16 = 1, strictly coarser than
7/13, so this alphabet does not improve the supplier moment.

## Scope and evidence

Assignment seed `e40e6919c4355ecbd8119bf42f3ffc2f`, scope key
`7acfe4d9cac04f7ba4cb`, task `complex-masked-decoder`, priority revision 2.
Base commit `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Scope status is
**refined**: the card asks for one masked or overcomplete decoder and a
complete moment, and its first experiment is one finite support alphabet
before a network. The alphabet is the frame pair itself. The eight-term
all-pairs search on punctures of size at most 24 is not repeated.

The proof is in [PROOF.md](PROOF.md). The finite census, the rank-2 column
pattern, the complex ordinary-transpose gauge, and the failure controls are
in [verify.py](verify.py). Pins are in [SOURCES.json](SOURCES.json). The
selected record is historical provenance only.

Checked positive facts:

- 120 lines and the coordinate frame.
- 1,260 complementary frames, of which 896 admit a root-pair decoder in the
  sense already counted by the frame-pair census. All 1,260, admissible or
  not, satisfy O O^T = O^T O = 4 I and D0 D0^T = 2G.
- Every standard column has exactly four odd partners and label rank 2.
- 13,440 ordered pairs of distinct standard columns have rectangular label
  rank 1. Those pairs are orthogonal in coefficient space, so the dual
  condition in the eight-term lower bound is necessary.

Failure controls: one altered cross entry misses 2G; the block-diagonal
matrix misses the odd entries; scaling both factors of one column by 1+i
misses 2G; the reciprocal complex scale preserves 2G and the support.

## Reproduce

From the repository root, Python 3.12, standard library only. Leave
`PYTHONOPTIMIZE` unset; the checks also pass under `-O` because they raise
explicitly.

```sh
python3 -B research/frame-pair-sixteen-exact/verify.py
```

Expected final line:

```text
PASS_FRAME_PAIR_SIXTEEN_EXACT frames=1260 admissible=896 cost=16 column_rank=2 orthogonal_rank_one_pairs=13440 controls=7
```

Registered replay:

```sh
python3 scripts/research_package.py --package research/frame-pair-sixteen-exact --check-only
python3.12 scripts/research_package.py --package research/frame-pair-sixteen-exact
```

This run used Python 3.12.3. `g++` 13 and `libboost-dev` 1.83 were already
installed, and `/usr/bin/c++` already selected `/usr/bin/g++`. This package
does not compile native code. The selected cold replay `make frontier1094-verify`
was not run.

## Open next questions

1. Can a factorization into more than eight real terms make the sum of
   label-pairing ranks strictly less than 16 on one of these Grams?
   That is the difference between the eight-term theorem and the absolute
   copied-information cost of the alphabet. A first step is to test whether
   any orthogonal rank-1 column pair can replace a rank-2 term and still sum
   to D0 D0^T. The blocker is that those pairs have coefficient dot product 0,
   and no identity yet rules out every longer rectangle decomposition.

2. Can these centres be hosted so that frame changes and dirty-state
   restoration cost less than the unpaid asymmetric-centre obligations of the
   P104 complement? The copied-information charge alone is a worse ratio than
   7/13. The blocker is a physical entry/exit contract, which this note does
   not supply.

## Credit

The root-line model, the 1,260-frame census, and the complementary eight-term
floor are from `research/complex-frame-pair-decoders`, following
DreamingOfClouds' PR717 decoder model. This note only changes which 16 lines
are live. Prepared by hevlyo with substantial AI assistance. Apache-2.0.
Discussion writes to CrocSwap/integer-mult-bounds were forbidden for this
account (`Resource not accessible by integration`). No claim or finding was
posted, and the write was not retried.
