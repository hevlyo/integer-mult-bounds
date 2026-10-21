# One E-graph term does not beat the fixed coordinate readers

This is a theorem about one finite model. The executable checks in
`verify.py` certify the finite premises. The classical all-pairs floor is
an inherited theorem, pinned in `SOURCES.json` and not re-proved here.

## Model

Start from the 120 real E8 root lines and delete the eight mutually
orthogonal frame lines `e_(2a) ± e_(2a+1)`. The remaining 112 ports have
coordinate matrix `X`, with columns `x_0, ..., x_7`. Every entry of `X` is
0 or ±1, every row has four nonzeros, and each column support (a star) has
size 56. The Gram matrix `M4 = X X^T` equals 4 on the diagonal. Its
off-diagonal entry is 0 exactly on the pairs with label product 1. That
undirected graph, including loops at every port, is the E-graph: 60 ones
in each row. The other 52 ports in a row are the odd neighborhood. Label
pairing is the F2 matrix of this graph; its rank on all 112 ports is 9.

A term has a reader vector and a source vector in `R^112`. Its copy cost
is the F2 rank of the label pairing between those two supports. The eight
coordinate terms `(x_k, x_k)` cost 8 each, total 64. That value belongs
to the coordinate decoder of PR620. An extra term is a pair `(d, t)`.

**Theorem.** Suppose the eight coordinate readers stay equal to the columns
of `X`, and equality to `M4` is required only on the E-graph. For every
real reader `d`, every real source `t`, and every real source matrix whose
eight columns `s_0, ..., s_7` satisfy

```text
sum_k X[i,k] s_k[j] + d[i] t[j] = M4[i,j]
```

whenever port `i` is on the E-graph at port `j`,

```text
sum_k beta(x_k, s_k) + beta(d, t) >= 64.
```

Equality is attained by an E-graph-exact term that is not exact on the odd
pairs. No new multiplication exponent is claimed. Frames, restoration,
hosting, precision, and all-size analytic charges were not priced; they
were left at zero, and the copy-rank sum still does not fall below 64.

## Normal form

Write `N(j)` for the E-graph neighborhood of port `j`, a set of 60 ports.
`X` restricted to `N(j)` has rank 8, so it is injective on `R^8`. The same
count on `N(j) ∩ N(j')` is 8 for every one of the 3,304 E-graph edges and
6 for every one of the 2,912 odd pairs. Thus, at each `j`:

- if `t[j] = 0`, the source row equals the row `X[j]`;
- if `t[j] ≠ 0`, then `d` agrees on `N(j)` with `X a` for a unique
  `a = a(j) in R^8`, and the source row is `X[j] - t[j] a(j)`.

Adjacent ports of the support `J = supp(t)` have the same `a`, because
their neighborhoods intersect in rank 8. So `a` is constant on each
E-component of `J`.

`N(v)` without `v` has rank 7 and is orthogonal to the row `X[v]`. The
right kernel of those rows is the line through `X[v]`.

## Star code

On each star, the E-graph adjacency has F2 rank 8. Its 255 nonempty
codewords, 2,040 in total, fall into six families:

| weight | components | common odd neighbors | count |
|---:|---|---:|---:|
| 28 | one | 0 | 576 |
| 32 | one | 0 | 504 |
| 28 | one | 1 | 448 |
| 24 | one | 1 | 448 |
| 24 | one | 0 | 56 |
| 56 | one | 0 | 8 |

Every codeword is E-connected, and the minimum weight is 24. A coordinate
pairing rank drops below 8 only when the zero set of that source column
contains one of these codewords. Outside `J`, every source column agrees
with `X`, whose star support is the whole star. Therefore every dropped
coordinate meets a codeword inside `J`.

Each of the 448 star memberships has 27 E-neighbors inside its star. The
pairing rank of that one column is 1. The 27 neighbors have rank 7, and
adding the point does not raise it. Those neighbors are disjoint from the
odd neighborhood of the point. While they remain in the source support,
changing the source entry at that single port does not change the
coordinate cost.

## One codeword leaves at most one extra port

If `J` contains no star codeword, every coordinate costs 8 and the extra
term costs at least 0, so the sum is at least 64.

Now suppose `J` contains a codeword `W`.

If `W` has no common odd neighbor, every port outside `W` has an E-edge
into `W`. Any further point of `J` joins the same component, so there is
one vector `a`. The reader `d` equals `Xa` on every E-neighborhood of `J`.
The complementary ports, if any, are orthogonal to all of `J`, so their
pairing rows do not affect `beta(d, t)`. The sources are exactly the
classical sources `X - t a^T`. The cost equals the classical single-lift
cost of `(a, t)`.

If `W` has one common odd neighbor `v`, the same counting leaves at most
the port `v` outside `W`'s component: a second component would need
another port orthogonal to every point of `W`, and every such codeword has
only one. Both the 448 weight-28 codewords and the 448 weight-24 codewords
lie entirely in the odd neighborhood of their neighbor `v`. For each of
them, `X` on `N(v) ∩ (union of N(w) for w in W)` has rank 7 and is
orthogonal to `X[v]`, so its kernel is the line through `X[v]`. A larger
odd component only adds rows, so it does not enlarge that kernel.

- If `v` is not in `J`, the sources are classical. The pairing row of `v`
  against `J` is zero, so a reader value at `v` does not change the extra
  rank.
- If `v` is in `J` and some E-neighbor of `v` is also in `J`, that neighbor
  meets `W` (otherwise it would be a second common odd neighbor) and the
  edge to `v` pulls `v` into `W`'s component. Again there is one vector `a`.
- If `v` is in `J` and no E-neighbor of `v` is in `J`, then
  `J ⊆ {v} ∪ odd(v)`. The big component has a vector `a` and the singleton
  `{v}` has a vector `b` with `b - a` in the joint kernel, hence
  `b = a + λ X[v]`. The 27 E-neighbors of `v` stay outside `J`, so every
  coordinate cost equals the classical cost of `(a, t)`. On `N(v)` the
  Gram column of `v` vanishes off the diagonal, so `X b` and `X a` differ
  only at port `v`. Ports outside every E-neighborhood of `J` contribute
  zero pairing rows. The masked reader therefore differs from `Xa`, for
  pairing against `J`, by at most the membership of port `v`.

## Reduction to the classical floor, except one parallel line

The inherited theorem, `research/p112-single-lift/PROOF.md`, states that
every classical single lift costs at least 64, and it says explicitly that
its argument does not cover a masked completion. This package uses that
theorem only after the masked term has been given the same coordinate
costs and the same extra rank as a classical lift. It does not replay the
3,272 sign systems.

Let `S = supp(Xa)`. Over all 511 nonzero label functionals `q` and every
port `v` in the support `I_q`, the rows `X[I_q without v]` have corank at
most 1. The 112 corank-1 kernels that meet `X[v]` are parallel to that
row. The other 448 corank-1 kernels are orthogonal to `X[v]`. There is no
corank greater than 1.

Consequently `v` is label-critical for `S` only when `a` is a nonzero
multiple of the row `X[v]`. If `a` is not such a multiple, `lab[v]` is in
the span of the other rows of `S`, so toggling port `v` in the reader does
not change the extra rank. The masked cost equals the classical cost and
is at least 64.

If `a` is a nonzero multiple of `X[v]`, the four stars that do not contain
`v` have a zero coefficient, so they are not cancelled and cost 8. Each of
the four stars that contain `v` keeps its 27 E-neighbors in the source, so
it costs at least 7. When all four cost 8, the sum is at least 64. When
one costs less than 8, `J` contains an active codeword `W` of weight 28.
There are 448 of these, four at each port. Every odd neighbor of `v` lies
in an E-neighborhood of `W`, the Gram column is nonzero on all 52 of them,
and their pairing rank against `W` is 7. The coefficient `λ` does not
change that column off `N(v)`. The extra term therefore costs at least 7,
the coordinates cost at least 60, and the sum is at least 67. The zero
vector `a` cancels nothing; redundancy again leaves every coordinate at 8.

## Equality and a strict deformation

At port `v`, take `d` equal to the Gram column of `v` on the odd
neighborhood and equal to 0 on `N(v)`, with the extra source supported
only at `v` and with the eight coordinate sources left equal to `X`. The
E-graph column is unchanged. Every odd entry of that column is nonzero, so
the term is not all-pairs exact. All eight stars still cost 8, and the odd
reader pairs with `{v}` at rank 0. The sum is 64.

A second witness cancels one active weight-28 codeword and retunes port
`v` by `λ = 1`. The resulting E-graph identity holds, one coordinate falls
to 7, and the extra rank rises enough that the sum is 71.

## What was not proved

The verifier's rational ranks are modular ranks at the prime 65,537. Every
8×8 minor of a 0/±1 matrix has absolute value at most `8^4 = 4096`, so
this prime does not hide a nonzero minor. Kernel vectors used for the
parallelism test are rebuilt over `Q` from seven original rows.

The classical sign census inside the inherited proof was not run. Two
extra terms, a replaced coordinate reader, and any cost outside this
pairing-rank sum are outside the theorem.
