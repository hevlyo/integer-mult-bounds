# One added total on one pinned P104 frame-pair decoder

This is a theorem about one finite algebraic model. The executable
certificate checks every finite premise below. The argument for arbitrary
real parameters is this note, not a proof assistant and not a search over
the correction vector.

## Model

Use the 120 real E8 root lines and the coordinate frame

```text
F0 = {e0±e1, e2±e3, e4±e5, e6±e7}
```

in the doubled-coordinate model of
`research/complex-frame-pair-decoders`. Let F1 be the first 8-clique, in
the orthogonal graph of the complementary 112 lines, that admits a
cross-frame decoder, and let the decoder be the first solution of that
clique in split-mask order. Both are deterministic. The verifier records

```text
F1 = (96, 95, 85, 74, 47, 38, 14, 13)
pairs = (1,13), (26,85), (27,74), (44,47), (96,54), (95,55), (38,45), (14,0).
```

The live set L is the complementary 104 lines. Index ports by L. For each
pair (α_j, β_j) with coupling e_j = ⟨α_j, β_j⟩ ∈ {±1}, the reader and source
columns are

```text
x_j(i) = ⟨r_i, α_j⟩,          y_j(i) = 2 e_j ⟨r_i, β_j⟩.
```

Every reader entry lies in {-1,0,1} and every source entry lies in
{-2,0,2}. The pinned columns satisfy

```text
sum_{j=0}^{7} x_j y_j^T = 2G
```

on all 104×104 live pairs, and each of the eight terms has label-pairing
cost 7.

Labels are the rows N_i ∈ F2^{120} with bit u equal to (⟨r_i, r_u⟩+1) mod 2.
Their span has dimension 9. For a real column d write S(d) for the span of
{N_i : d_i ≠ 0}, and write Ann(U) for the vectors in that nine-dimensional
space which vanish on every line in U. The copied-information cost is the
F2 rank of the rows {N_i : d_i ≠ 0} restricted to {u : t_u ≠ 0}. Rank-nullity
gives

```text
β(d,t) = dim S(d) - dim(S(d) ∩ Ann(supp t)),
```

and β = 0 when either support is empty. Each pinned reader has dim S(x_j) = 8,
so the original source has a one-dimensional kernel K_j inside S(x_j).

## Statement

**Theorem.** For every a ∈ R^8 and every z ∈ R^{104},

```text
sum_{j=0}^{7} β(x_j, y_j - a_j z) + β(Xa, z) ≥ 56.
```

Equality holds at z = 0, and also when a single term is moved into the
ninth slot. No new κ, supplier, frame schedule or restoration bill is
claimed. Frames, restoration and hosting are charged zero in this
relaxation; the copy sum still does not fall.

The identity

```text
sum_j x_j (y_j - a_j z)^T + (Xa) z^T = sum_j x_j y_j^T
```

holds for every real a and z, so every such correction remains an exact
nine-term factorization on the live pairs. A zero ninth source is the
original decoder.

## Boundary cases

Let J = {j : a_j ≠ 0} and k = |J|.

If k = 0, the ninth reader is zero and the eight sources are unchanged, so
the cost is 56.

If k = 1, say a_j ≠ 0, the other seven sources stay at cost 7. The ninth
reader is a nonzero multiple of x_j, so it has the same support and
β(Xa, z) = β(x_j, z). Every port with y_j(i) ≠ 0 lies in supp(y_j - a_j z)
or in supp(z). Subadditivity of pairing rank on a fixed row support gives

```text
β(x_j, y_j) ≤ β(x_j, y_j - a_j z) + β(x_j, z).
```

The left side is 7, so the changed term and the ninth term cost at least 7
together. The total is at least 56.

## Parity equations

Now k ≥ 2. Write s_j = y_j - a_j z and

```text
H_j = S(x_j) ∩ Ann(supp s_j),     H_0 = Ann(supp z).
```

Thus β(x_j, s_j) = 8 - dim H_j for every j, whether or not j lies in J.
For j ∉ J the source is the original column, so dim H_j = 1. Therefore

```text
cost = 7(8-k) + sum_{j∈J} (8 - dim H_j) + β(Xa, z)
     = 56 + k - sum_{j∈J} dim H_j + β(Xa, z).
```

The desired bound is β(Xa, z) ≥ sum_{j∈J} dim H_j - k.

Let q_j ∈ H_j and q_0 ∈ H_0 satisfy q_0 = sum_{j∈J} q_j. Write b_j(i) for
the bit of q_j at live line i. Then b_0(i) = sum_{j∈J} b_j(i). If z_i ≠ 0,
membership of q_0 in H_0 forces b_0(i) = 0, hence sum_j b_j(i) = 0. If
b_j(i) = 1, the source vanishes, so y_j(i) = a_j z_i.

For each port i and each sign ε ∈ {+1,−1},

```text
sum_{j∈J : sign(y_j(i)) sign(a_j) = ε} b_j(i) = 0.          (*)
```

These equations do not depend on the magnitudes |a_j|. If z_i ≠ 0, every
firing index has sign(y_j(i) sign(a_j)) = sign(z_i), so one sign class is
empty and the other is even. If z_i = 0, every firing index has y_j(i) = 0,
so both nonzero sign classes are empty.

Relative to the certified eight-vector basis of each S(x_j), (*) is an F2
linear system in 8k unknowns. Up to replacing a by −a, which swaps the two
sign classes and leaves the system unchanged, there are 3,272 patterns with
k ≥ 2. Each system has corank exactly k. The k original kernels of the
active readers satisfy (*), sit in distinct coefficient blocks, and
therefore span the solution space. Every kernel tuple of the addition map
has its (q_j) in that space, so the kernel has dimension at most k.

The addition map lands in the nine-dimensional label space. Rank-nullity
gives

```text
sum_{j∈J} dim H_j + dim H_0 ≤ k + 9.                         (†)
```

## Full reader span

Evaluate all 511 nonzero linear functionals q on the nine-dimensional label
space, and let I_q be the live ports where q equals 1. Of the integer
matrices X[I_q, :], 495 have rational rank 8 and 16 have rank 7 with a
one-dimensional kernel. Those kernels are the eight coordinate axes and the
eight weight-4 vectors in the verifier. Hence S(Xa) fails to be the full
label space only when a is a real multiple of one of those sixteen vectors.

An axis has k = 1 and was already bounded. For every other a with k ≥ 2,
S(Xa) is the whole label space, so β(Xa, z) = 9 − dim H_0. Combined with (†),

```text
sum_{j∈J} dim H_j - k ≤ 9 - dim H_0 = β(Xa, z).
```

The cost is at least 56.

## The eight weight-4 directions

Each remaining vector v has exactly four nonzero coordinates. For a = t v
with t ≠ 0, the reader Xa has the same support as Xv, and the certificate
shows that this support spans an eight-dimensional hyperplane S. The sign
pattern of −v produces the same parity system as v. Its four-dimensional
solution space maps onto the one-dimensional quotient of the label space by
S, so the solutions whose sums lie in S form a subspace of dimension at
most 3.

If H_0 is not contained in S, then H_0 + S is the whole label space because
S is a hyperplane. Dimension counting gives

```text
dim(S ∩ H_0) = dim H_0 - 1,
β(Xa, z) = 8 - dim(S ∩ H_0) = 9 - dim H_0.
```

The kernel bound dim ≤ 4 and (†) then give sum dim H_j − 4 ≤ β(Xa, z).

If H_0 ⊆ S, every kernel sum lies in S, so the kernel dimension is at most
3 and

```text
sum_{j∈J} dim H_j + dim H_0 ≤ 12.
```

Here β(Xa, z) = 8 − dim H_0, and sum dim H_j − 4 ≤ 8 − dim H_0. In both
branches the cost is at least 56.

## Equality and scope

At z = 0 every source is unchanged and the ninth source is empty, so the
cost is exactly 56. Taking a = e_0 and z = y_0 moves the first term into
the ninth slot and the cost vector is (0,7,7,7,7,7,7,7,7), still 56. The
bound is sharp inside this family.

The result is one pinned frame and one pinned decoder. It does not cover
the other 895 admissible frames, two or more added totals, a change of the
eight reader columns, a masked identity, complex scalars, or any positive
charge for frames, restoration, hosting or recursive children. It does not
reopen the eight-term all-pairs theorem, and it does not replace the
coordinate P112 single-lift theorem. No selected frontier, supplier or
multiplication theorem is changed.

The method adapts the sign-pattern annihilator argument of the coordinate
single-lift note. The adaptation is essential: the same equations built
from reader signs, rather than source signs, have corank 0 on every
pattern, which is too strong for kernels that are already one-dimensional
at z = 0. A verifier control records that distinction.
