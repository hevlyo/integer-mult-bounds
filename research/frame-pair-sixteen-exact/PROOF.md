# Eight-term copy cost of a 16-line frame pair

The argument is for one fixed coordinate frame and an arbitrary complementary
frame. `verify.py` checks the finite identities it uses on all 1,260 such
frames. Coefficients may be real or complex. Transpose is ordinary, not
conjugate.

## 1. Alphabet

Let the 120 lines be the root lines of E8, with the doubled-coordinate
enumeration used by `research/complex-frame-pair-decoders`. Inner products of
distinct lines lie in {-1, 0, 1}, and each line has inner product 2 with
itself. The label bit is

```text
S9(a, b) = (<a, b> + 1) mod 2.
```

Thus S9 is 1 on every even inner product, including every diagonal, and 0 on
every odd inner product.

F0 is the coordinate frame: eight mutually orthogonal lines. A complementary
frame F1 is any eight mutually orthogonal lines disjoint from F0. There are
1,260 of them inside the 112-line complement. Let O be the 8 by 8 matrix

```text
O_{f,e} = <f, e>,    f in F1, e in F0.
```

The live support is the ordered 16-line set F0 then F1. Its Gram block is

```text
G = [ 2 I,  O^T ]
    [ O,    2 I ].
```

The copied-information target is the ordinary product 2G. A term is one
column of a factor pair (D, T) with D T^T = 2G. Its cost is the F2 rank of
S9 between the nonzero rows of that column of D and the nonzero rows of that
column of T. The cost of a factorization is the sum of its term costs.

## 2. The isometry factor

Expanding a norm-2 root in the orthogonal basis F0 gives the row identity
O O^T = 4 I. The same expansion in F1 gives O^T O = 4 I. Consequently every
column of O has exactly four entries in {±1} and four zeros: the squared
length is 4 and every nonzero inner product of distinct lines has absolute
value 1.

Define the 16 by 8 matrix D0 by

```text
D0 = [ 2 I ]
     [ O   ].
```

Then

```text
D0 D0^T = [ 4 I,  2 O^T ] = 2G,
          [ 2 O,  4 I   ]
```

because O O^T = 4 I. Also D0^T D0 = 4 I + O^T O = 8 I, so D0 has full column
rank and a left inverse (1/8) D0^T.

## 3. Each standard column costs exactly 2

Index columns by e in F0. Column e is nonzero on the coordinate line e and on
the four odd partners N(e) = {f in F1 : O_{f,e} ≠ 0}. On that five-line
support the label matrix, ordered as e followed by N(e), is

```text
row e:        (1, 0, 0, 0, 0)
row f in N(e):(0, 1, 1, 1, 1).
```

The first row is the diagonal label of e together with S9(e, f) = 0 for each
odd partner. Each partner row is 0 against e and 1 against every line of the
same frame, including itself. These rows span a two-dimensional F2 space, so
the column costs 2. Eight columns cost 16. This is the matching upper bound,
and it is an all-pairs identity, not only an even-entry identity.

## 4. Eight terms cannot cost less

Let M = 2G. Suppose D and T are 16 by 8 matrices, with real or complex
entries, and D T^T = M under ordinary transpose. Rank M = 8, and D0 has image
equal to the image of M, so there is a unique invertible 8 by 8 matrix A with
D = D0 A. The same reasoning gives T = D0 B for a unique invertible B, and

```text
D0 A B^T D0^T = D0 D0^T
```

implies A B^T = I after applying the left inverse of D0. Hence B = A^{-T}.

Write c and e for a paired pair of columns of A and of A^{-T}. Their bilinear
dot product, with no conjugation, equals 1. The corresponding term supports
are the nonzeros of D0 c = (2c, O c) and D0 e = (2e, O e). In particular both
F0 supports are nonempty, and neither Oc nor Oe is zero.

Suppose the label rank of this term were at most 1. The F0 lines in the row
support have label row equal to the all-ones vector on the nonempty F0 column
support, because every pair inside F0 is even. That all-ones vector is
nonzero, so every F1 line f in the support of Oc has the same label row on
that F0 set. Therefore S9(f, x) = 1 for every x in the F0 support of e, which
means O_{f,x} = 0. The row of O indexed by f vanishes on the support of e, so
(Oe)_f = 0. Every coordinate of Oc is therefore paired with a zero coordinate
of Oe, and (Oc) · (Oe) = 0. But

```text
(Oc) · (Oe) = c^T O^T O e = 4 c · e,
```

so c · e = 0, contradicting c · e = 1. Every one of the eight terms has label
rank at least 2. The cost is at least 16, hence exactly 16.

The same dot-product obstruction shows why the hypothesis cannot be dropped.
Across the 1,260 frames, the verifier finds 13,440 ordered pairs of distinct
standard columns whose rectangular label rank is 1. For those pairs the
coefficient dot product is 0, so they are not dual columns of an eight-term
factorization.

## 5. Fixed coordinate readers, including the even mask

The even-entry mask does not relax either frame block: every pair inside F0
or inside F1 is even, and 2G restricts to 4 I on each. It also keeps every
zero of O, because those cross pairs are even. Only the odd cross positions
are free.

Now fix the eight coordinate readers D_{F0} = 2 I and T_{F0} = 2 I, and allow
extra terms only when each extra term misses F0 on at least one side. Even
cross zeros force every F1 coefficient that shares a column with coordinate
line e to lie in N(e). A coordinate term that meets F1 on both sides therefore
contains a 2 by 2 label block

```text
[ 1  0 ]
[ 0  1 ]
```

and costs at least 2. Let t be the number of coordinate terms that meet F1 on
both sides. They contribute at most t to the rank of the F1 block. That block
equals 4 I under the mask, so at least 8 - t further terms are required, each
of cost at least 1. The untouched coordinate terms cost at least 1 each.
The total is at least

```text
(8 - t) + 2t + (8 - t) = 16.
```

The factor in section 2 attains 16 with no extra terms, and its odd cross
values equal the true Gram. With these readers held fixed, forgetting the odd
entries does not lower the copied-information charge.

## 6. Limits

The ratio on 16 live lines is 16/16 = 1, which is strictly coarser than the
complementary P104 ratio 7/13. No frame change, dirty-state restoration,
hosting cost, or outer moment is priced. Conjugate transpose is not the
product used above. A factorization into more than eight real terms is not
bounded here: a term with coefficient dot product 0 can have label rank 1, and
the trace identity on the coefficient matrices no longer forces eight dual
columns. Another odd-supported isometry in place of O is covered by section 5
only when the coordinate readers stay fixed.
