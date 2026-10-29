# Diagonal call floor for the 21 transvections of GL(3, F2)

## Question and scope

In the group algebra `R = F2[GL(3, F2)]`, a paid call on `W` registers is

```text
D_N(g) = I + ([g] + [e]) N,
```

where `g` runs over the 21 matrices with `rank(g + I) = 1` and `N` is any
rank-one idempotent in `M_W(F2)`. Group multiplication is matrix
multiplication over `F2`. Equality is in the full matrix algebra `M_W(R)`.

The three-register bound in
[research/bit-three-register-lower-bound](../bit-three-register-lower-bound/README.md)
uses the additive address group of `M_3(Q)`, nonzero rational rank-one frames,
and three invertible lower-triangular targets. Its Model section leaves
arbitrary free address maps between calls outside that abelian model. This
package changes the address group to `GL(3, F2)` and the paid labels to the
21 defining-representation transvections. Scalar mixing remains a rank-one
idempotent on the same `W` roles. There is no extra ancilla.

The selected conditional construction stays the source-bound record in
[certificates/selected-result.json](../../certificates/selected-result.json).
No selected-supplier admission and no new kappa are claimed.

Scope is **refined**. The card permits one specified nonabelian operation
family. The family, the diagonal endpoints, and every finite width `W` are
fixed above. The six coordinate matrices `I + E_{ij}` are a smaller alphabet
used only as a comparison.

## Result

**Theorem.** For every width `W >= 1` and every tuple
`(g_1, ..., g_W)` in `GL(3, F2)^W`, the shortest product of paid calls equal
to `diag([g_1], ..., [g_W])` has length exactly

```text
sum_i rank(g_i + I).
```

Every element is one of four kinds, read off `g + I` in the defining
representation: the identity has rank 0; the 21 involutions have rank 1 and
are the legal labels; the 56 elements of order 3 and the 42 elements of order
4 have rank 2; the 48 elements of order 7 have rank 3. In particular, three
order-7 elements cost exactly 9 calls. That matches the nine-call count of
the abelian three-register theorem on a different alphabet, so this family
does not undercut that count.

### Lower bound

Apply the defining representation entrywise. A paid call maps to

```text
I_{3W} + N tensor (g + I).
```

Here `rank(g + I) = 1` and `rank(N) = 1`, so the update has rank 1. For
`P_j = I + U_j` and `Q_k = P_1 ... P_k`,

```text
Q_k - I = sum_{j=1}^{k} Q_{j-1} U_j,
```

with `Q_0 = I`. The image of the left side therefore has dimension at most
`sum_j rank(U_j)`. The represented diagonal endpoint differs from the identity
by the block-diagonal matrix `diag(g_1 + I, ..., g_W + I)`, whose rank is the
sum in the theorem. Every formal factorization, shared or diagonal, needs at
least that many calls. Quotienting to the defining representation can only
drop constraints.

### Matching words

A complete search of `GL(3, F2)` records one factorization of each matrix into
exactly `rank(g + I)` transvections. No rank-2 matrix is a single
transvection, and no rank-3 matrix is a product of two. On register `i`, the
calls `D_{E_{ii}}(t_1) ... D_{E_{ii}}(t_r)` multiply to the diagonal matrix
with `[t_1 ... t_r]` in position `i`. Calls on different registers use
different diagonal idempotents, so they concatenate. The resulting word has
length equal to the rank sum and equals the diagonal endpoint.

The rank bound is uniform in the word. The matching upper bound is this
finite factorization, checked for all 168 elements, together with the diagonal
concatenation. The verifier multiplies all 28,224 width-2 diagonal words in
`M_2(R)` and one explicit width-3 word.

### Explicit width-3 word

```text
T1 = [[0, 0, 1], [0, 1, 0], [1, 0, 0]]
R2 = [[0, 0, 1], [0, 1, 0], [1, 0, 1]]
S  = [[0, 0, 1], [0, 1, 1], [1, 1, 0]]
```

`T1` is a non-coordinate transvection. `R2` has rank 2. `S` has order 7 and
rank 3. One factorization, with the same left-to-right product, is

```text
R2 = T1 [[1, 0, 1], [0, 1, 0], [0, 0, 1]]
S  = T1 [[1, 0, 0], [0, 1, 1], [0, 0, 1]] [[1, 1, 0], [0, 1, 0], [0, 0, 1]]
```

Placing those six factors on `E_{11}`, `E_{22}`, and `E_{33}` respectively
gives `diag([T1], [R2], [S])`. The represented image has rank 6, so five
calls are impossible for this endpoint. The same floor applies to every other
diagonal triple of these ranks.

### Comparison with the six coordinate labels

Left Cayley distance in the six matrices `I + E_{ij}` is

```text
{0: 1, 1: 6, 2: 24, 3: 51, 4: 60, 5: 24, 6: 2}.
```

`T1` has coordinate length 3 and transvection length 1. `S` has coordinate
length 4 and transvection length 3. The two 3-cycles

```text
[[0, 0, 1], [1, 0, 0], [0, 1, 0]]
[[0, 1, 0], [0, 0, 1], [1, 0, 0]]
```

are the two elements at coordinate distance 6, and each has transvection
length 2. Hanson Sun's merged
[PR #1974](https://github.com/CrocSwap/integer-mult-bounds/pull/1974)
(`85bbb643721a989ed1bdc918e0db684a39ee4b38`) proves that those coordinate
distances add under diagonal endpoints in the six-label alphabet. The
21-label alphabet lowers those direct bills to the rank sum, and the
representation bound shows that sharing still cannot go below that sum.

## Reproduce

From the repository root, with assertions enabled and `PYTHONOPTIMIZE` unset:

```sh
python3 -B research/gl3-transvection-diagonal-floor/verify.py
python3.12 -I -B research/gl3-transvection-diagonal-floor/verify.py
python3 scripts/research_package.py --package research/gl3-transvection-diagonal-floor --check-only
python3.12 scripts/research_package.py --package research/gl3-transvection-diagonal-floor
```

Expected final line of the verifier:

```text
PASS_GL3_TRANSVECTION_DIAGONAL_FLOOR elements=168 transvections=21 witness_calls=6 target_rank=6 coordinate_length_S=4 coordinate_length_3cycle=6 width2_pairs=28224 controls=8 no_new_kappa
```

The eight controls are: coordinate lengths of `T1`, of `S`, and of the two
distance-6 3-cycles; exclusion of the rank-2 idempotent `E_{11}+E_{22}`; an
omitted final factor; represented rank at most 5 for that five-call prefix;
a replaced final factor; and the reversed factorization of `S`. An optimized
run exits before the census. The predecessor README hash is checked against
the pin in [SOURCES.json](SOURCES.json).

Orientation only, not evidence for the tariff:

```sh
python3 -B scripts/research_baseline.py
```

That command returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` on this base.
`make frontier1094-verify` was not run.

## Limits

The identity is diagonal. A non-diagonal endpoint can have a smaller
represented rank than a direct reading of its entries, so this relaxation
does not by itself price those endpoints. The package does not model free
address maps inserted between calls, native coordinate scheduling, hosting,
restoration outside the `W` registers, or a transfer into the selected bit
supplier. The factorization search is exhaustive for this group of order 168
and is not a general formula for `GL(n, q)`. No proof assistant was run.

## Open next questions

Is there an explicit non-diagonal endpoint in `M_2(F2[GL(3, F2)])`, in this
same 21-label alphabet, whose exact minimum is strictly larger than the rank
of its defining-representation image? A gap would mean the relaxation is no
longer a tariff once off-diagonal group-algebra entries are allowed. The
first step is to enumerate the 588 calls on two registers and all `588^2`
ordered pairs, then keep an endpoint that matches no shorter call and whose
`6 x 6` image has rank below 2. Nothing mathematical blocks that finite
screen. It was not run here. Words longer than two calls are a separate
search.

## Overlap

The refreshed search on 2026-10-29T12:19:56Z covered 317 open pull requests,
including drafts, and 5856 discussion records, with complete pagination.
Phrase search for this 21-transvection diagonal tariff matched only this
package. Nearby work uses other groups or the six coordinate labels: the
abelian three-register bound, the `F2[S3]` rank floor in PR #3893, and the
coordinate theorem in PR #1974. Discussion #2102 probes length-eight bridges
in that six-label alphabet. Closed pull requests are visible to that search
only through local notes and the ledger.

## Credit and disclosure

The paid-call shape and the 28 three-register idempotents follow the model
in the pinned three-register note. The representation-rank pattern was used
for a different group and endpoint by the `F2[S3]` package in
[PR #3893](https://github.com/CrocSwap/integer-mult-bounds/pull/3893)
at `d3e2a4d5d967e9baf071dfdfe97e598aded3e025`. The six-label diagonal theorem
is Hanson Sun's PR #1974, cited above. No predecessor code is imported.

Prepared by a donated research session. Substantial AI assistance was used
for the rank argument, the exhaustive factorization, the verifier, and the
packaging. No independent human review is claimed. Apache-2.0.

Discussion writes from this account are forbidden by the host integration.
That limitation is recorded here and was not retried.
