# Even constraints force the geometric Gram on the P112 frame complement

## Statement

Let the true E8 roots be vectors \(ρ ∈ \mathbb{R}^8\) of norm 2. Coordinate roots
are the vectors \(±e_i ± e_j\). A **geometric** decoder is one whose Gram entries
come from a single matrix \(M ∈ \mathbb{C}^{8×8}\): the entry on root lines \(ρ, σ\)
is \(ρ^T M σ\), with ordinary transpose. The all-pairs target is
\(ρ^T M σ = 2⟨ρ, σ⟩\). The **masked** target imposes that equality only when
\(⟨ρ, σ⟩\) is even, that is, only on orthogonal pairs and on diagonals.

Delete the coordinate frame

\[
F = \{e_{2a}+e_{2a+1},\; e_{2a}-e_{2a+1} : a = 0,1,2,3\}.
\]

These are eight pairwise orthogonal lines. On the remaining 112 lines, every
complex matrix satisfying the masked target equals \(2I\). Consequently every
odd pair on those lines satisfies the all-pairs target as well.

An eight-column geometric factorization of this \(M\) is a dual basis
\(AB^T = 2I\). It is an exact all-pairs decoder. Dropping the odd equations
does not add a cost-0 repair, a frame, or a restoration inside this family.
Overcomplete factorizations of the same \(M\), and Grams that are not bilinear
forms on \(\mathbb{C}^8\), are outside the statement.

## Coordinate calculation

Write \(S = (M+M^T)/2\) and \(K = (M-M^T)/2\). For a live orthogonal pair
\(u, v\), both orders vanish, so \(u^T S v = 0\) and \(u^T K v = 0\).

There are 24 axis pairs \(\{i, j\}\) other than the four frame pairs. Both
\(u = e_i+e_j\) and \(v = e_i-e_j\) are live. Their diagonal equations are

\[
S_{ii}+S_{jj}+2S_{ij} = 4, \qquad S_{ii}+S_{jj}-2S_{ij} = 4,
\]

so \(S_{ij} = 0\) and \(S_{ii}+S_{jj} = 4\). The cross evaluation is
\(u^T S v = S_{ii}-S_{jj}\) and \(u^T K v = -2K_{ij}\). Both are zero, hence
\(S_{ii} = S_{jj} = 2\) and \(K_{ij} = 0\).

Every axis belongs to at least one of these 24 pairs, so every diagonal entry
of \(S\) is 2. Every off-diagonal entry whose axes are not a frame pair is
already zero in both \(S\) and \(K\). The undecided entries are the four
frame parameters \(s_a = S_{2a,2a+1}\) and \(k_a = K_{2a,2a+1}\).

The live orthogonal pair \(e_0+e_2\) and \(e_1+e_3\) has disjoint axes, and so
does \(e_0+e_2\) with \(e_1-e_3\). Expanding and discarding the entries already
proved zero gives

\begin{align*}
s_0+s_1 &= 0, & k_0+k_1 &= 0, \\
s_0-s_1 &= 0, & k_0-k_1 &= 0.
\end{align*}

Thus the first two frame parameters vanish. The same expansion on
\((e_0+e_4,\, e_1±e_5)\) and \((e_0+e_6,\, e_1±e_7)\) kills the other two
blocks. Therefore \(M = 2I\).

The same identities are 108 linear equations on the 64 entries of \(M\). They
have rank 64 and unique solution \(2I\). Removing the four equations from the
last block leaves rank 62. The two-dimensional nullspace is spanned by the
symmetric and skew matrices supported on axes 6 and 7, so that block is
necessary to the written argument. Replacing one right-hand side by 1 makes
the system inconsistent.

## Live census

The stored model uses \(v = 2ρ\), so \(v_i^T (2I) v_j = 2(v_i·v_j)\) is the
stored form of \(ρ^T(2I)σ = 2⟨ρ, σ⟩\). Among the \(112^2\) ordered live pairs,
6720 have even stored inner product \(0\) or \(8\), and 5824 have odd stored
inner product \(±4\). The label pairing bit \((⟨ρ, σ⟩+1) \bmod 2\) is 1 on the
even pairs and 0 on the odd pairs. Odd singleton repairs are the cost-0 sites
in the masked model. None of them is required: \(M = 2I\) already matches the
all-pairs value on all 5824.

The 6720 even rows, as an integer matrix of width 64, have rank 64 modulo
1000003 and modulo 1000033. A minor that is nonzero modulo either prime is
nonzero over \(\mathbb{Q}\), so this is an independent proof that the full
even system, not only the 108 coordinate equations, has no second solution.
Direct evaluation shows that \(2I\) meets every even row, so it is the unique
solution.

## What is not claimed

The eight-term copy-cost inequality of the frame-pair theorem is inherited
only as a scope statement: an eight-column decoder in this family is one of
the decoders that theorem already bounds. This note does not re-prove that
inequality, does not price a nine-column factorization of \(2I\), and does not
treat a Gram whose entries are not of the form \(ρ^T M σ\). No supplier,
child histogram, or selected \(κ\) changes.

The abstract E-graph rigidity arguments, which allow an arbitrary matrix on
the 112 lines rather than a bilinear form on \(\mathbb{C}^8\), are a different
object. They are not used and are not extended.
