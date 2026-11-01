# Two-column retained loss through source union 51

This is a finite exact-matrix argument. It is not a formal proof of integer
multiplication, and it does not replay the rank-one or off-column reductions
from earlier two-total notes.

## Setting

`X` is the pinned 112 by 8 coordinate matrix in
`research/p112-single-lift/reference-geometry.json`. Labels `l_t` and duals
`v_i` are the nine-bit integers stored there. Reader `j` has support
`S_j = {t : X_{t j} != 0}`, with `|S_j| = 56`. The pairing rank is

```text
beta(d, s) = rank_F2 (v_i · l_t) over i in supp(d), t in supp(s).
```

`C_j` is the F2-span of the literal pairing rows of reader `j` on `S_j`.
For a port set `U`,

```text
K_j(U) = {c in C_j : supp(c) subset U},    g_j(U) = dim K_j(U).
```

A closed support is a union of codewords of one `C_j`. A two-column
correction has the shape `Y = X - Z A^t` with `A` an 8 by 2 matrix and `Z`
a 112 by 2 matrix, so the correction `W = Z A^t` has rank at most 2. Its
source union `U` is the set of nonzero rows of `Z`. The retained loss of
reader `j` is `8 - beta(x_j, y_j)`.

## Premises checked by the verifier

P1. Each `C_j` has 256 words, of weights `0, 24^63, 28^128, 32^63, 56`, and
the duals on `S_j` span an 8-dimensional space. Thus every reader kernel
dimension equals the codimension of the surviving source labels inside that
8-dimensional quotient.

P2. For `j != k`, `|S_j ∩ S_k| = 24`. That cut is a codeword of both readers,
it is the only nonzero word of `C_k` supported inside `S_j`, and every other
nonzero word of `C_k` has at least 12 ports outside `S_j`.

P3. The 112 source labels are distinct. On every cut, the coordinate product
`X_{t j} X_{t k}` is `+1` on 12 ports and `-1` on 12 ports.

P4. The closed supports of size at most 51 are enumerated by breadth-first
union of codewords. Each reader has the same census. There is no closed
support of size 49 or 51. Size 50 occurs, in dimensions 3 and 4 only. No
closed support in this range has dimension greater than 4.

## Necessary rank condition

Let `P_j` be the union of the supports of the kernel words of reader `j`
against `supp(y_j)`. Then `P_j` is a closed support, `P_j` is contained in
the source union, and the retained loss of reader `j` is at most `g_j(P_j)`.
On `P_j` the correction reproduces the coordinate column. Therefore, for
every set `K` of at least three readers whose patterns `P_k` are nonempty,
the intersection of those patterns has rational rank at most 2 in the
columns `K`. Call this condition N. It uses only `rank W <= 2`.

## Why unions 49, 50 and 51 do not raise the loss bound

Write `s` for the size of the largest pattern in a configuration.

- If `s >= 40`, then for a cap of 51 the number of ports outside that pattern
  is at most 11. By P2 the only companion patterns that can fit are the cut
  words already named by the lead reader. The verifier searches every such
  lead of size 40 through 50 and every subset of fitting cuts. No
  configuration with retained loss 6 or more satisfies N. Loss 5 does occur.
- If `s = 36`, a cap of 51 allows 15 ports outside the lead. For every
  size-36 lead and every other reader, the closed supports of size at most
  36 that meet this 15-port budget are exactly the supports that already meet
  a 12-port budget. The widened budget therefore adds no patterns. The
  resulting search has maximum N-satisfying loss 5.
- If `s <= 32`, every pattern is a single codeword. All tuples of codewords
  from distinct readers with union at most 51 were enumerated: 196 tuples use
  six readers, 56 use seven, and 7 use eight, but every tuple of six or more
  readers fails N. The largest tuple that satisfies N uses five readers.

The same three branches at caps 49 and 50 are subsets of the cap-51 search,
except that the explicit witness below has union 48 and therefore remains
admissible at each cap. The two-column retained-loss maximum is exactly 5 at
caps 49, 50 and 51.

On a closed support, the cut-count `g_j(V) + #{k : C_{jk} subset V}` has
maximum 8 for every cap in {49, 50, 51}. That is a geometric loss of deletion
sets, before condition N. It is not a copy-cost claim.

## Full-rank on-column floor

The explicit correction with `A = [e_0, e_1]` and `Z` equal to column 0 of
`X` on a dimension-4 48-port support of reader 0, together with column 1 of
`X` on the cut `S_0 ∩ S_1`, satisfies `X X^t = Y X-side + (X A) Z^t` on all
12,544 ordered port pairs. Its retained losses are 4 and 1 on readers 0 and
1, and 0 elsewhere. The two added pairing ranks are 8 and 7. The separate-total
bill is 74, and the source union has 48 ports. This attains retained loss 5.
It does not attain the relaxation floor below.

In the full-rank on-column case both added sources are nonzero, their supports
cover the source union, and distinct labels identify active-label counts with
those support sizes. The inherited price function

```text
p(m) = min{r >= 1 : m <= 2^(r+1)}
```

then charges at least `p(1) + p(M-1) = 6` whenever the union has size
`M` in {49, 50, 51}, and the same 6 already applies at size 48. Combined
with retained loss at most 5,

```text
copy-rank sum >= 64 - 5 + 6 = 65.
```

This is a lower bound in that full-rank on-column case. The explicit witness
costs 74, so attainment of 65 is not claimed. Rank-one corrections,
off-column sources, changed readers, masked identities, and every positive
frame, restoration, hosting or recursive charge are outside this equality.
Granting those extra charges the value zero does not produce a copy-rank sum
below 65 in the case proved here.

Bands of size 52 and above are not covered. At cap 52 a size-40 lead has 12
ports of outside budget, so P2 no longer reduces the companions to cut words.
