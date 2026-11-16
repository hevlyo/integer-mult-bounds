# Two totals, three ports, and the P112 coordinate copy rank

This is a finite exact argument about one decoder family. It is not a
proof-assistant formalization and it does not change the selected conditional
kappa.

## Model

Use the pinned P112 coordinate matrix `X` from
`research/p112-single-lift/geometry.py` (DreamingOfClouds' PR717 model, as
recorded for Mihir Srivastava's one-total theorem). Rows are indexed by the
112 surviving real E8 root lines. Each row lies in `{-1,0,1}^8` and has
squared length 4. The eight columns are the coordinate readers `x_0,...,x_7`.
Labels and duals are the pinned nine-bit vectors, and the pairing-rank cost
`beta(reader, source)` is the F2 rank of the label pairings between the
nonzero reader positions and the nonzero source positions. Each single column
against itself costs 8, so the eight coordinate terms cost 64.

For real `a,b in R^8` and real `z,w in R^112`, the ten-term identity

```text
X X^T = sum_j x_j (x_j - a_j z - b_j w)^T + (X a) z^T + (X b) w^T
```

holds by expansion. The investigated invoice is

```text
sum_j beta(x_j, x_j - a_j z - b_j w) + beta(X a, z) + beta(X b, w).
```

Mihir Srivastava's one-total theorem is the case of a single added source.
Two added totals are outside that theorem. Coefficients here are real. Frames,
restoration, hosting and the recursive moment are not charged.

## Plane census

**Theorem.** No two rows of `X` are real scalar multiples. Every
two-dimensional real subspace contains at most three rows of `X`. There are
exactly 896 subspaces that contain three rows, and none that contain four.

The finite check enumerates all `C(112,2) = 6216` pairs. A pair is dependent
when every 2-by-2 minor vanishes. A third integer row lies in the real span
when every 3-by-3 minor vanishes. That minor test is complete for real
coefficients: a real dependence among integer vectors is a rational
dependence. The census finds 0 dependent pairs and, for every independent
pair, at most one further row in the span. The sum of those extra rows over
the 6216 pairs is 2688. Each three-point plane contributes three pairs and
therefore three extras, so there are `2688/3 = 896` such planes.

The bound is sharp. The rows

```text
(1, 1, 1, 1, 0, 0, 0, 0),
(1, 1, 0, 0, 1, 1, 0, 0),
(0, 0, 1, 1,-1,-1, 0, 0)
```

satisfy the third = the first minus the second, and the span of the first two
contains no other row of `X`.

## Reader cocircuits

**Theorem.** For each coordinate reader, the 56 nonzero ports carry 56
distinct evaluation vectors and those vectors span an 8-dimensional space.
Every nonzero F2-linear form on that space is 1 on 24, 28, 32, or all 56
ports, with multiplicities 63, 128, 63 and 1. The two sides of each form have
pairing ranks `(7,7)`, except the unique form that is 1 on every port, whose
ranks are `(8,0)`. Consequently every set of source deletions that drops the
reader's pairing rank has size at least 24, and 24 is achieved.

The rank drops if and only if the surviving evaluation vectors lie in a
hyperplane, if and only if the deleted set contains the positive set of some
nonzero form. The census shows every positive set has size at least 24. The
same census shows that deleting any 23 ports of an explicit 24-port positive
set leaves rank 8, so the threshold is sharp. The histogram is the same for
all eight readers. Both the predecessor's row-wise rank and a separate
column-wise rank produce this histogram.

## Three-port corollary

**Corollary.** If the set `U = {i : z_i != 0 or w_i != 0}` has size at most 3,
the ten-term invoice is at least 64. The zero correction `z = w = 0` attains
64.

The source vector `x_j - a_j z - b_j w` differs from `x_j` only on `U`.
Deleting at most three original support ports cannot drop a reader rank, by
the cocircuit threshold. Turning a zero into a nonzero only adds an evaluation
vector and cannot lower rank. The two extra terms are nonnegative. Therefore
each of the eight readers still costs at least 8.

Full-row absorption is the subfamily in which `(z_i, w_i)` is nonzero only
where the whole row equals `z_i a + w_i b`. Any such row lies in
`span{a, b}`, so the plane theorem supplies at most three such ports. The
corollary covers every real full-row absorption. The sharp triple above, with
`a` and `b` equal to the first two rows and `(z, w)` equal to `(1,0)`,
`(0,1)` and `(1,-1)` on those three ports, absorbs each of them completely.
Its measured invoice is `[8,8,8,8,8,8,8,8]` plus extras `[2,2]`, total 68.

## What this does not say

A correction supported on 4 or more ports is outside the corollary. The
cocircuit theorem says a reader rank can drop only at size at least 24, but
it does not price the two shared extra terms at that scale. Complex
coefficients, masked identities, changed readers, frames, restoration and the
moment are not treated. No new kappa is claimed.
