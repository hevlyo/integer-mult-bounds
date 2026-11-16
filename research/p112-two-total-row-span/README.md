# P112 coordinate rows and a three-port two-total copy bound

**Scoped negative result for one overcomplete family. No new kappa.**

On the pinned P112 coordinate matrix, a real ten-term factorization that keeps
the eight coordinate readers and adds two totals does not lower the
pairing-rank sum below 64 when the two correction sources are supported on at
most three ports. Three is the maximum number of rows that can lie in a real
plane, so this support bound is exactly the full-row absorption regime. The
zero correction attains 64. An explicit three-row absorption costs 68.

## Task card

```text
Task ID / scope key: complex-masked-decoder / 2a6f2c726b78f9ae7d26
Chooser seed / track: cd7812ca070bdb48f6370d96d460ac6d / complex-mechanisms
Base commit: ef5f39403610d231a0c27e8a6b4f08c10209bcd6
Priority revision: 2
Catalogue SHA256: 89b5928bc92c81e2647b6d702a7ad85a6795b8f44e2eb267b2ff3145d8f2b2ce
Selected-record SHA256: 10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32
Concrete object: the real identity
  XX^T = sum_j x_j (x_j - a_j z - b_j w)^T + (Xa) z^T + (Xb) w^T
  on the pinned 112 by 8 coordinate matrix, with invoice the sum of the ten
  binary pairing ranks, restricted to |supp(z) union supp(w)| <= 3.
Scope status: refined. The card allows one specified overcomplete family on a
  fixed support alphabet. This family adds two totals to the eight coordinate
  readers. It is not the eight-term all-pairs search, and it is not a mixture
  of catalogue providers.
Nearest overlap: p112-single-lift (one added total; two totals left open);
  p112-complex-single-lift (complex phases of one total); discussion 2028
  (Walsh ten-term shears, every tested profile sums to 82); discussion 2369 /
  PR 2382 (two-total exclusion for source unions of size 44 through 47, not
  on this checkout). A refreshed open-PR and discussion search on 2026-11-16
  returns those neighboring two-total notes and not another census of the
  896 three-point planes or this three-port corollary.
Optimistic budget: frames, restoration, hosting and recursive children charged
  zero. A copy-rank sum strictly below 64 would be the required improvement.
Success evidence: the plane census, the reader-cocircuit census, and the
  support-size corollary, with the sharp three-row invoice.
Falsification: four coplanar rows, a reader deletion of size at most 23 that
  drops the pairing rank, or a real correction on at most three ports whose
  ten-term invoice is below 64.
Stop rule: stop once those three statements are certified. Do not search
  supports of size 4 or larger in this package.
Predecessor authors: DreamingOfClouds (PR717 geometry and the coordinate cost
  model); Joel Pulikkan / GamingPuzzled (PR620, coordinate cost 64); Mihir
  Srivastava (PR845 / p112-single-lift, one-total theorem); the complex
  single-lift note; the frame-pair eight-term floor that this term count leaves.
```

The other suggestion from the same chooser draw, `complex-new-helper-inventory`,
was not taken. Its live overlap was the denser of the two cards. The draw
itself was not repeated.

## Scope and evidence

The eight-term all-pairs floor is not rerun. The changed hypothesis is the
term count: ten terms, with the original eight reader columns retained and
two arbitrary real totals added. The support alphabet is the pinned P112
label set. [PROOF.md](PROOF.md) records the statements. The executable census
checks every pair of rows and all 255 forms on each of the eight readers.

| Fact | Exact value |
|---|---|
| Pairs of rows | 6216, none parallel over R |
| Planes containing three rows | 896; no plane contains four |
| Sharp plane | `(1,1,1,1,0,0,0,0)`, `(1,1,0,0,1,1,0,0)`, `(0,0,1,1,-1,-1,0,0)` |
| Reader support | 56 distinct evaluation vectors, span dimension 8 |
| Form splits, each reader | `(24,7,7)` × 63, `(28,7,7)` × 128, `(32,7,7)` × 63, `(56,8,0)` × 1 |
| Minimum deletion that drops a reader | 24, and 23 does not |
| Zero correction invoice | 64 |
| Sharp three-port absorption | readers `[8]×8`, extras `[2,2]`, total 68 |

The predecessor row-wise rank and a separate column-wise rank agree on the
histogram and on both invoices. A synthetic vector in the sharp plane is
accepted by the minor test and is not a row of `X`. A one-entry mutation of
`X` fails the Gram check. The card's orientation command was run before this
argument:

```text
python3 -B research/complex-decoder-field-extension-seed44/verify.py
PASS_COMPLEX_DECODER_FIELD_EXTENSION_S44 p=0..24 examples=3 attaining=25 pairing=14400 controls=7
```

That replay is the eight-term positive control. It is not part of this
package's registered replay.

## Reproduce

From the repository root, Python 3.12, standard library only. The checks use
explicit exceptions, so they stay active under `-O`.

```sh
python3 -B research/p112-two-total-row-span/verify.py
python3 -O -B research/p112-two-total-row-span/verify.py
python3 -I -S -B research/p112-two-total-row-span/independent_check.py
python3 scripts/research_package.py --package research/p112-two-total-row-span
```

Final lines: `PASS_P112_TWO_TOTAL_ROW_SPAN`, the same line under `-O`,
`PASS_P112_TWO_TOTAL_ROW_SPAN_INDEPENDENT`, and
`PASS_REGISTERED_RESEARCH_PACKAGE`. Each checker takes about one to two
seconds here.

Measured environment: Python 3.12.3; `g++` 13.3.0 at `/usr/bin/g++`, with the
`c++` alternative already pointing there; `libboost-dev` 1.83.0.1ubuntu2;
`PYTHONOPTIMIZE` unset. `python3 -m pip install --user -r
research/e8-bit-p111-tuned/requirements.txt` installed numpy 2.5.4, sympy
1.14.0 and scipy 1.18.1. This package does not import them. No
artifact-regenerating suite was run.

## Limitations

Frames, restoration, hosting, precision and the recursive moment were not
priced. They do not have to be priced to rule out a copy-rank improvement
inside this three-port regime, because the pairing-rank sum already stays at
least 64 when those charges are zero. Supports of size 4 or larger, complex
`a,b,z,w`, masked identities and any change of the eight readers are outside
the corollary. The selected frontier was not replayed (`make frontier1094-verify`
was not run) and is unchanged. This is not a multiplication theorem.

Discussion writes were not available from this environment: the configured
client can read discussions and pull requests, and it cannot create a
discussion. No claim was posted, and the write was not retried.

## Open next questions

Can a real rank-2 correction supported on at least 24 ports, the cocircuit
threshold, make the same ten-term pairing-rank sum strictly less than 64?

It matters because 24 is the first size at which a coordinate reader can lose
pairing rank. A sum below 64 would be the first copy-rank headroom in this
fixed-reader family; a matching lower bound would extend the one-total theorem
to two totals.

First step: fix one explicit 24-port positive form on reader 0, require a
second reader to be cancelled on a subset of that form, solve the resulting
real equations for `(z, w)`, and compute all ten pairing ranks with both rank
implementations in this package.

Blocker: cancelling three or more readers at one port overdetermines `(z, w)`,
and the two shared extra terms are not bounded by the per-reader `(7,7)` split.
PR 2382 already excludes a neighboring large-support model through 47 ports,
but that proof is not on this checkout and uses a different cancellation
shape, so it cannot be quoted as this corollary.

## Credit

Geometry and the pairing-rank definition: DreamingOfClouds, PR717, as pinned
by Mihir Srivastava in `research/p112-single-lift`. The coordinate cost 64 is
PR620 (Joel Pulikkan / GamingPuzzled) and its predecessors. The one-total
theorem and the explicit exclusion of two or more totals are Mihir
Srivastava's `research/p112-single-lift`. Complex phases of one total are
`research/p112-complex-single-lift`. The eight-term floor that this term count
leaves is `research/complex-frame-pair-decoders`. The Walsh ten-term search
(discussion 2028) and the 44-to-47-port two-total exclusion (discussion 2369,
PR 2382) are different regimes.

Prepared by Riquelme Soares (@hevlyo) with substantial AI assistance.
Apache-2.0. No independent human review or proof-assistant check is claimed.
