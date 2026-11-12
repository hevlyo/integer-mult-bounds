# Masked rank on a double frame

This note uses the E8 root-line model of DreamingOfClouds' PR717 and the frame-pair
geometry of `research/complex-frame-pair-decoders` (PR968). It does not reuse that
package's eight-term all-pairs theorem. The finite census is executed by
`verify.py`. No supplier, invoice, or kappa is claimed.

## 1. Alphabet and masked equations

Let the 240 roots of E8 be written in the usual doubled coordinates, and let the
120 lines be unordered pairs `{r, -r}`. The coordinate frame `F0` consists of the
eight lines `e_{2a} ± e_{2a+1}`. A second frame `F1` is any eight mutually
orthogonal lines disjoint from `F0`. There are 1260 such frames. Write
`A = F0 ∪ F1`, sixteen lines.

The inner product of two distinct lines lies in `{-1, 0, 1}`, and each line has
square 2. The **masked E-graph equations** on `A` ask for a complex matrix `K`,
indexed by `A`, with

- `K_ii = 4`,
- `K_ij = 0` whenever `i ≠ j` and the lines are orthogonal.

Entries on odd pairs (inner product `±1`) are free. This is the masked model
named in the frame-pair scope note: exactness on orthogonal pairs, with the odd
entries left to cost-0 corrections. It is not the all-pairs equation
`K = 2G`.

## 2. Cross-Gram

Order `F0` and `F1` arbitrarily and let `N` be the `8 × 8` matrix
`N_ab = ⟨F0[a], F1[b]⟩ ∈ {-1, 0, 1}`.

The eight lines of `F0` are orthogonal of square 2, and the four plane pairs
recover the eight coordinate axes. They are a basis of the ambient space. The
coordinates of an `F1` line in that basis are `N_ab / 2`. Because `F1` is also
an orthogonal basis of square-2 lines,

```text
N^T N = 4 I_8.
```

Every row and every column of `N` therefore has exactly four nonzero entries:
each nonzero entry has square 1, and the diagonal of `N^T N` is 4. In
particular the bipartite graph of odd pairs between `F0` and `F1` is 4-regular.
Since `N` is invertible over `Q`, that graph has a perfect matching.

`verify.py` checks `N^T N = 4 I_8` on all 1260 frames, and checks that zeroing
one row of a real cross-Gram destroys the identity.

## 3. Rank of a masked matrix

Partition `K` into `F0` and `F1` blocks. Lines inside one frame are orthogonal,
so the diagonal blocks are `4 I_8`. The off-diagonal blocks vanish on orthogonal
cross pairs and are otherwise free:

```text
K = 4 | I  B |
      | C  I |,
```

with `B` and `C` supported on the odd bipartite graph. The top-left block is
invertible, so the Schur complement gives

```text
rank(K) = 8 + rank(I - C B) ≥ 8,
```

and `rank(K) = 8` if and only if `C B = I_8`. In that case

```text
K = 4 | I | | I  B |.
      | C | 
```

Thus every rank-8 masked matrix is a sum of eight rank-one terms, and no masked
matrix on this alphabet has rank below 8.

The Gram matrix `2G` itself satisfies the masked equations, because an
orthogonal pair has inner product 0. The sixteen lines lie in an 8-dimensional
space and the eight lines of `F0` are independent, so `rank(2G) = 8`. Equality
is attained on every double frame, admissible or not. A zero cross block has
Schur complement `I` and block rank 16; the checker records that negative
fixture.

## 4. Separated matching cost

Let `π` be any perfect matching of the odd graph, and define `B` to be the
corresponding permutation matrix and `C = B^T`. Then `C B = I_8`. The eight
vectors

```text
u_a = e_{F0[a]} + e_{F1[π(a)]}
```

satisfy `K/4 = Σ_a u_a u_a^T`. Term `a` is supported on the pair
`{F0[a], F1[π(a)]}`. Those two lines are distinct and non-orthogonal, so their
label-pairing block, with bits `(⟨x, y⟩ + 1) mod 2`, is

```text
| 1  0 |
| 0  1 |.
```

Its F2 rank is 2. The eight terms are disjoint as pairs and the total
label-pairing cost on `A` is 16.

An orthogonal pair has label block `J_2`, of rank 1, so the same count is false
without the odd-matching hypothesis. The checker rejects that fixture, and it
checks the `I_2` block for every perfect matching of every frame
(356,608 matchings).

This is an attained cost of one explicit family. It is not a lower bound for
every factorization of every masked matrix. Mixtures that use the repeated
labels of an inadmissible frame are left open below.

## 5. Label-rank trichotomy

The label-pairing matrix of `A` is the `16 × 16` F2 matrix of those bits. Its
rank is the dimension of the span of the sixteen label rows.

Two lines of `F1` have the same label row on `A` if and only if they have the
same four neighbors in `F0`. Indeed, lines inside `F1` are pairwise orthogonal,
so their mutual label bits are all 1, and the bits against `F0` are 0 exactly on
the neighbors. Sharing four neighbors is therefore the same as having identical
`F1` label rows. The checker confirms this equivalence on every frame.

The common-neighbor type of `F1`, and the label rank, are constant:

| Relative type (common-neighbor multiplicities) | Frames | Share-4 graph on `F1` | Distinct label rows | Label rank |
|---|---:|---|---:|---:|
| `(0, 4), (2, 24)` admissible | 896 | empty | 16 | 8 |
| `(0, 8), (2, 16), (4, 4)` | 336 | four disjoint edges | 8 | 6 |
| `(0, 16), (4, 12)` | 28 | two disjoint 4-cliques | 4 | 4 |

These 1260 frames are enumerated exhaustively. The three share-4 graphs are
checked, not assumed. Admissible means there is no share-4 pair, which is the
same numerical split 896 / 364 already recorded for frame-pair decoders. The
rank column is the new distinction: inadmissibility does not drop the masked
matrix rank below 8, and it does not drop the separated matching cost below 16,
but it does drop the label-pairing rank of the alphabet from 8 to 6 or 4.

## 6. What this does not say

The separated cost 16 is the copy cost of this factorization on the sixteen
frame lines only. It is not the cost of a decoder on the complementary 104
lines, and it is not a paid recursive moment. Frames, restoration, hosting,
and odd-entry corrections are not priced because no network is built. A
factorization cheaper than 16, if one exists, would have to mix terms across
matched pairs and use label repetition; that search was not run. The result
does not extend the eight-term all-pairs floor, and it does not claim that
every masked matrix on a larger puncture has rank 8.
