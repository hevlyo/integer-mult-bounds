# Quaternion triple squares need six calls

**Finite register-model certificate; no new κ.** The selected result, both
primitive suppliers, and `upstream/` are unchanged. The complex primitive
binds, and these identities meet their disjoint bills.

In the group algebra \(\mathbb F_2[Q_{16}]\),

\[
Q_{16}=\langle x,y\mid x^8=e,\ y^2=x^4,\ yxy^{-1}=x^{-1}\rangle,
\]

with exactly three roles and paid calls

\[
D_N([g])=I+([g]+[e])N,
\qquad g\in\{x,y\},
\]

the minimum word lengths of \(\operatorname{diag}([x^2],[x^2],[x^2])\) and
\(\operatorname{diag}([x^4],[x^4],[x^4])\) are both 6. Here \(N\) runs over
all 28 rank-one idempotents in \(M_3(\mathbb F_2)\). Matrix equality is an
operator identity on arbitrary dirty states. The element \(x^4\) is the unique
order-2 element and is central; it is also \(y^2\).

The changed hypothesis is the address group. The abelian three-register model
uses arbitrary rational rank-one frames. This alphabet uses only the two
quaternion generators and charges every call. There is no free scalar mixing
between calls and no fourth role.

## Priced baseline

Generator lengths, computed before the matrix search:

| Target element | Shortest generator word | Disjoint three-role bill |
|---|---|---:|
| \(x^2\) | \(xx\) | 6 |
| \(x^4\) | \(yy\) | 6 |
| \(x^6\) | \(xxyy\) | 12 |

The degree-1 relaxation does not decide these bills. The augmentation powers
of \(\mathbb F_2[Q_{16}]\) have dimensions \(15,13,11,9,7,5,3,1,0\). The
quotient \(\Delta/\Delta^2\) is spanned by \([x]+1\) and \([y]+1\). A product
of calls has degree-1 symbol equal to the sum of its projectors on each
generator: every call augments to \(I\), and the cross term \((M-I)\alpha N\)
has entries in \(\Delta^2\). Both triple squares, and the \(x^6\) triple, lie
in \(I+M_3(\Delta^2)\). Vanishing of the symbol forces each projector sum to
be zero. Every admitted projector has trace 1, so both label counts are even.
The relaxation therefore gives only the even-length floor 2.

## Result

Lengths 1 through 5 were enumerated in \(M_3(\mathbb F_2[Q_{16}])\). The exact
frontiers have sizes 56, 2352 and 92374. None contains either triple square.
The doubled coordinate words

- \((E_{00},x)\) twice, then the same for \(E_{11}\) and \(E_{22}\),
- \((E_{00},y)\) twice, then the same for \(E_{11}\) and \(E_{22}\),

equal the two targets. Both minima are therefore 6. A released two-role note
already observed that two copies of \(x^4\) cost 4 by the direct word. The
three-role search is the new statement: every admissible mixer still leaves
the disjoint bill of 6 unchanged.

There are 799 length-3 prefix matrices with a length-3 continuation to the
central target. All 799 prefixes are pure \(y\)-words, and 792 of them use a
projector outside \(\{E_{00},E_{11},E_{22}\}\). Off-diagonal mixing occurs at
length 6 and still does not produce a shorter word. The same prefix-matrix
count 799 appears for the \(x^2\) triple. An earlier semidihedral package
reported the same count for a different presentation and different frontiers
(2051 and 68899). The count is not treated as a new mechanism.

Separately, \(\operatorname{diag}([x^6],[x^6],[x^6])\) has no word of length
at most 6, and the coordinate word \(xxyy\) on each role has length 12. The
parity lemma above excludes the odd lengths 7, 9 and 11, which were not
enumerated. The exact minimum is therefore in \(\{8,10,12\}\) and is not
claimed to be sharp.

## Reproduce

From the repository root, with Python 3.12 and `PYTHONOPTIMIZE` unset:

```sh
python3 -B research/q16-central-square/verify.py
python3 -B scripts/research_package.py --package research/q16-central-square
```

Expected final verifier line:

```text
PASS_Q16_CENTRAL_SQUARE x2=6 x4=6 x6_through6=0 x6_upper=12 idempotents=28 calls=56 frontier2=2352 frontier3=92374 len4=0 len6_x2=799 len6_x4=799 len6_x6=0 central_nondiagonal_prefixes=792 group_lengths=2,2,4 controls=7 no_new_kappa
```

The script uses the standard library only. It checks the presentation,
associativity, the unique order-2 element, the augmentation dimensions, the
28-idempotent scan of all \(512\) matrices, call inverses, and the frontiers.
Seven controls are required: \(\operatorname{diag}([x]^3)\) and
\(\operatorname{diag}([y]^3)\) at length 3, the two-role square
\(\operatorname{diag}([x^2],[x^2],[e])\) at length 4, one role of \(x^4\) at
length 2, a dropped call failing on the dirty state
\(([x^5],[y],[x^2]+[y])\), an \(x\)-for-\(y\) substitution failing, and the
false relation \(y^2=e\) making the central witness fail. The rank-2 matrix
\(E_{00}+E_{11}\) is not admitted.

Recorded environment: CPython 3.12.3, `g++` 13.3.0 with `/usr/bin/c++` pointing
at `/usr/bin/g++`, `libboost-dev` 1.83.0.1ubuntu2, and
`research/e8-bit-p111-tuned/requirements.txt` already satisfied by a
`python3 -m pip install --user` run. This package imports none of those
libraries.

Not run: `make frontier1094-verify`, the three-register C++ replay, a
four-role search, and lengths 8, 10 and 12 except for the explicit length-12
upper word. Odd lengths 7, 9 and 11 are excluded by the parity argument, not
by enumeration.

## Open next questions

1. Is the minimum of \(\operatorname{diag}([x^6]^3)\) equal to 8, 10, or 12?
   A value below the disjoint bill of 12 would be a real mixing saving in
   this alphabet. First step: meet in the middle at length 8 on the depth-4
   frontier. That frontier was not built; depth 3 already has 92374 matrices.
2. Can one restored scratch role realize
   \(\operatorname{diag}([x^4],[x^4],[x^4],[e])\) in fewer than 6 calls?
   A scratch role is the usual route past a three-role disjoint bill. First
   step: shortest-path search to depth 3 on the four-role alphabet of both
   generators and every rank-one idempotent in \(M_4(\mathbb F_2)\). That
   alphabet was not built.

## Credit

Predecessor model: the scalar-idempotent calls in
`research/bit-three-register-lower-bound`, from eumemic's pinned PR #288.
Discussion comment
[18926868](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18926868)
records the same presentation and releases a two-role schedule: \(x^4=y^2\),
so two copies cost 4 by the direct word, not an assumed 8. That note does
not determine the three-role minimum. The \(Q_8\) central-pair claims are the
order-8 group. The semidihedral triple-square certificate uses
\(srs=r^3\) and \(s^2=e\); its frontiers are 2051 and 68899, not these.
Apache-2.0.

Substantial AI assistance was used to build the multiplication table, search
the paid words, and write these notes.

Discussion writes for this account return FORBIDDEN / Resource not accessible
by integration. No claim was posted, and the write was not retried.

Base commit `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Selector nonce
`bfe60b39ce1400e38d330c639d8e904a`, card `bit-new-register-model`, scope key
`7084092dd726e7ba1f2f`, priority revision 2.
