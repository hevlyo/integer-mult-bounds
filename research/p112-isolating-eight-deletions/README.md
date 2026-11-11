# Isolating eight-deletions of the P112 frame incidence

**Finite exact classification; no new κ.** On the 112 lines outside a fixed
coordinate frame, the 8-subsets that isolate at least one line are completely
listed, and each rational frame-incidence kernel is identified.

## Scope

This refines card `complex-masked-decoder`. The eight-term all-pairs copy floor
does not cover decoders that are exact only on the even-entry graph and repair
odd entries with cost-0 terms. Global quadratic extension is the statement that
those masked frame-sum constraints still force the trace-zero quadratic normal
form. [PR #5957](https://github.com/CrocSwap/integer-mult-bounds/pull/5957)
shows extension fails at eight deletions and leaves the classification open,
including a greedy 8-set of kernel dimension 37.

The object here is only the **isolating** part of that classification: an
8-subset `X` of `P112` such that some line lies on no orthogonal 8-frame
disjoint from `X`. Non-isolating 8-subsets and nine-deletions are not
classified. No decoder, supplier, invoice, or selected frontier is changed.

Discussion writes to `CrocSwap/integer-mult-bounds` were rejected with
`Resource not accessible by integration`. That write was not retried.

## Result

Use doubled E8 roots, true inner product `dot/4`, and the coordinate frame
`FRAME0` of the lines `e_{2a} ± e_{2a+1}`. `P112` is the other 112 lines.
A live frame is an orthogonal 8-subset of `P112`. There are 1260 live frames,
and each line lies on 90 of them.

For each line the other lines meet it in 15 frames (8 lines, its heavy octet)
or 10 frames (51 lines). The 14 heavy octets partition `P112` and pair up:
the heavy octet of every line in one octet is the partner octet.

**Census.** Every line has exactly 13 eight-point transversals of its 90
frames. Globally these are 686 distinct subsets.

| Family | Sets | Lines isolated | GF(2) rank | Rational rank | Kernel dimension | Excess over the 35 quadratics |
|---|---:|---:|---:|---:|---:|---:|
| Heavy octet | 14 | 8, the partner octet | 61 | 62 | 42 | 7 |
| Double isolation | 672 | 2 | 66 | 67 | 37 | 2 |

No isolating 8-subset isolates exactly one line. The kernel-37 sets in the
PR #5957 note are the 672 double-isolation sets, and each isolates two lines.
Among isolating deletions the maximum excess is 7, attained exactly by the 14
octets.

The rational kernel is spanned by the restrictions of the 35 trace-zero
quadratic forms and the indicators of the isolated lines. For an octet the
eight indicators contribute seven dimensions; for a double set the two
indicators are independent of the quadratics.

## Argument

Eight pairwise orthogonal roots form a basis. With doubled coordinates `v = 2r`
and true norm 2, `sum_k v_a v_b = 8 δ_ab` on every frame. Every trace-zero
quadratic therefore sums to 0 on every frame, over `Z`. An isolated line meets
no surviving frame, so its indicator is also in the integer kernel.

Let `A` be the surviving incidence matrix and `K` the span of those kernel
rows. Over any field, `rank(A) + dim K ≤ |L|`. Reducing modulo
`p = 1000003` gives `rank(A) = 62` and `dim K = 42` on every octet, and
`rank(A) = 67` and `dim K = 37` on every double set. Both pairs sum to
`|L| = 104`, so those modular ranks are the rational ranks and `K` is the full
rational kernel. The same sandwich on one 7-subset of an octet gives rank 70
and quadratic dimension 35 on 105 lines.

The GF(2) ranks are one less (61, 66, and 69 on the 7-subset) because every
frame has even size, so the all-1 vector is an extra GF(2) kernel vector. The
acceptance ranks are the rational ones.

The census is exhaustive for isolating sets: a line is isolated exactly when
the deleted set is one of its 13 transversals, and those transversals were
enumerated by splitting off the heavy octet. This does not decide whether a
non-isolating 8-subset can have positive excess.

## Controls

- Every 7-subset of the first octet is not fully rerun. The verifier deletes
  one explicit point and checks that nothing is isolated, the rational rank is
  70, and the quadratics still have rank 35.
- Replacing one point of an octet by another `P112` line leaves a live frame
  through the old partner line.
- The first eight `P112` lines are not an isolating set, isolate nothing, and
  have rational rank 69 (excess 0).
- A covered line of an octet deletion still meets a surviving frame, so its
  indicator is not a kernel vector. Every frame has cardinality 8, so the
  constant function is not a rational kernel vector.

## What was not run

- The classification of non-isolating 8-subsets. `C(112,8) = 475491062970`.
- Nine-deletion excess.
- A recheck of the `|X| ≤ 7` theorem of PR #5697, except the one 7-subset above.
- `make frontier1094-verify` and any selected-frontier replay. This package
  does not touch that construction.
- Discussion comments. The integration token cannot write to
  `CrocSwap/integer-mult-bounds` discussions.

## Reproduce

From the repository root, CPython 3.12, standard library, assertions not
required. `PYTHONOPTIMIZE` may be set; the verifier does not use `assert`.

```sh
python3 -B research/p112-isolating-eight-deletions/verify.py
python3 -B scripts/research_package.py --package research/p112-isolating-eight-deletions
```

Expected final line:

```text
PASS_P112_ISOLATING_EIGHT_DELETIONS octets=14 excess=7 doubles=672 excess=2 isolating=686 seven_control=1 damaged_control=1 generic_control=1
```

The run takes about one minute. One octet deletion was also checked with
exact `Fraction` elimination while preparing the sandwich; the registered
verifier uses the modular comparison above, which is the proof, not a screen.

## Open next questions

1. Does any 8-subset that isolates no line have positive quadratic-extension
   excess? A yes answer would add extension failures beyond the 686 sets and
   could raise the maximum excess above 7. First step: test one lex-minimal
   transversal of the 8-subsets under the stabilizer of `FRAME0`, using the
   same odd-prime sandwich. Blocker: there are `475491062970` subsets, and
   this session did not build a stabilizer-chain census.
2. What is the maximum excess at nine deletions? Nine is the injectivity limit
   named by PR #5957, so the quadratic span can drop there. First step: repeat
   the transversal census at deletion size 9 on the same 1260 frames. Blocker:
   the size-8 shapes (one octet, or a 4+2+2 double) do not list the size-9
   transversals, and the non-isolating gap is still open at size 8.
3. Does a double-isolation kernel of excess 2 produce a masked decoder whose
   fully charged copy cost is below the P112 value 64? That is the budget
   question on this card. First step: turn the two isolated lines and the
   deleted 8-set into an explicit support pattern and price every frame,
   restoration, and copied label. Blocker: kernel excess is not a copy invoice.

## Credit

Prepared by Riquelme Pereira with substantial AI assistance. The geometry and
the open eight-deletion question are Nick Petalas's PR #5957, following Ali
Romman's PR #5697, Josie Elliston's frame censuses, Andrey Mas's PR #1560,
and the retained E8 lineage of Brett Halligan, themilkman216, and
DreamingOfClouds. Apache-2.0.
