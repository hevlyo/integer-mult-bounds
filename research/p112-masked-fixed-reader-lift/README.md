# Fixed coordinate readers plus one E-graph term still cost 64

**Negative result for one masked family. No new κ, and the selected frontier is unchanged.**

The eight P112 coordinate readers stay fixed. One extra term has to match
`X X^T` only on the E-graph, not on the odd pairs. In that model the sum of
pairing-rank copy costs is at least 64. Equality is attained by a reader
supported on an odd neighborhood: the term is E-graph exact, it moves odd
Gram entries, and its own pairing rank is 0.

This is the masked gap left open by the classical single-lift theorem. That
theorem already proves the same floor when the identity is required on every
pair, and it says that a masked completion is outside its argument. The
normal form here puts every one-term E-graph completion next to a classical
lift, except for a one-port retuning along the port's own row. That parallel
line is bounded directly. The non-parallel line quotes the classical floor
and does not replay its sign census.

## Scope

Catalogue card `complex-masked-decoder`, scope **refined**. Selector nonce
`9ea1268e3ca1bd3df643b60bf3142efd`, track `complex-mechanisms`, priority
revision 2. Base commit `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`.

The card asks whether one specified masked or overcomplete decoder can
improve the complete moment budget. The family actually proved is narrower:
eight fixed coordinate readers, one extra term, exactness only on the P112
E-graph, and cost equal to the pairing-rank sum. The eight-term all-pairs
search is not repeated. Frames, restoration, hosting, precision, and
all-size analytic obligations were not priced. They were treated as zero,
and the copy-rank sum still does not drop.

A cheaper fully realized decoder could still move the binding complex side.
This family does not. It is a side constraint on one decoder shape, not a
new supplier and not a change to the selected record.

## Evidence

The argument is in [PROOF.md](PROOF.md). The finite census is
[verify.py](verify.py): 3,304 E-pair intersections of rank 8, 2,912 odd
pairs of rank 6, 2,040 star codewords, 112 label-critical rows, 448 active
odd-closure codewords, and five mutation controls. Two algebraic fixtures
are included. One meets 64 and is not all-pairs exact. The other is an
E-graph deformation whose coordinate costs are `[7,8,8,8,8,8,8,8]` and
whose total is 71.

Checks that name an inherited sentence only confirm that the pinned file
still contains it. They are not a replay of that proof.

Overlap refreshed 2026-10-21 against 458 open PRs and 3,225 discussions.
Nearby results are different objects: the classical all-pairs lift, free
odd rectangles mixed into one coordinate, two-column masked Gram
completions and their COPY-power screens, and trimmed-star or rank-8
rigidity censuses. No match was a fixed eight-reader, one-extra-term,
E-graph-only pairing-rank floor. That search is not a novelty certificate.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 scripts/research_package.py --package research/p112-masked-fixed-reader-lift --check-only
python3.12 scripts/research_package.py --package research/p112-masked-fixed-reader-lift
```

Expected final line of the package verifier:

```text
PASS_P112_MASKED_FIXED_READER_LIFT floor=64 readers=coordinate extra-terms=1 mask=E-graph e-pairs=3304 codewords=2040 critical=112 active-closure=448 inactive-closure=448 controls=5
```

`PYTHONOPTIMIZE` must be unset. The script raises on failure, so `python -O`
cannot skip a broken check. No artifact-regenerating suite was run beside
this verifier.

## Open next questions

1. **Two extra terms with the same fixed readers.** The one-term normal form
   uses a single reader, so two source supports can carry two vectors even
   when each codeword has only one odd neighbor. A first step is to fix two
   odd-disjoint star codewords, give each its own reader, and price the sum.
   The blocker is that the rank-8 intersection argument no longer forces
   those readers to be the same classical column.

2. **Replacing one coordinate reader instead of only adding a term.**
   Uniqueness of the neighborhood vector `a(j)` uses the fixed columns of
   `X`. A first step is to delete one star, let that reader be an arbitrary
   real vector, and rerun the neighborhood rank. The blocker is that the
   coordinate frame is an input to the normal form, not a conclusion.

## Attribution and discussion access

Coordinate cost 64 belongs to Joel Pulikkan / GamingPuzzled, PR620. The P112
E-graph model belongs to DreamingOfClouds, PR717. The classical single-lift
floor belongs to Mihir Srivastava, `research/p112-single-lift`. The card's
starting points are `research/complex-decoder-field-extension-seed44` and
`research/complex-frame-pair-decoders`; their eight-term all-pairs floor is
not re-opened here.

Discussion writes to CrocSwap/integer-mult-bounds are forbidden for this
account (`FORBIDDEN` / resource not accessible by integration). No discussion
post was attempted on this run, and none should be retried until that
access changes.

Prepared by hevlyo. Substantial AI assistance was used for the normal form,
the finite census, the verifier, and the write-up. New work is Apache-2.0.
