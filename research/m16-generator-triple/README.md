# Modular generator triples meet the disjoint bill

**Finite register-model certificate; no new κ.** The selected result, both
primitive suppliers, and `upstream/` are unchanged. The complex primitive
binds. These identities meet their disjoint bills, so register mixing does
not undercut them.

In the group algebra \(\mathbb F_2[M_{16}]\),

\[
M_{16}=\langle a,b\mid a^8=e,\ b^2=e,\ bab=a^5\rangle,
\]

with exactly three roles and paid calls

\[
D_N([g])=I+([g]+[e])N,
\qquad g\in\{a,b\},
\]

the minimum word lengths are

| Target | Disjoint bill | Minimum |
|---|---:|---:|
| \(\operatorname{diag}([a^2],[a^2],[a^2])\) | 6 | 6 |
| \(\operatorname{diag}([a^3],[a^3],[a^3])\) | 9 | 9 |
| \(\operatorname{diag}([a^5],[a^5],[a^5])\) | 9 | 9 |

Here \(N\) runs over all 28 rank-one idempotents in \(M_3(\mathbb F_2)\).
Matrix equality is an operator identity on arbitrary dirty states. Elements
are encoded by \(a^k=k\) and \(a^kb=8+k\).

The changed hypothesis is the address group. The abelian three-register model
uses arbitrary rational rank-one frames and concludes that nine calls are
necessary for three invertible lower-triangular targets. This alphabet uses
only the two modular generators and charges every call. There is no free
scalar mixing outside the 28 idempotents and no fourth role. The group is not
the generalized quaternion or semidihedral group of order 16: its center is
\(\{e,a^2,a^4,a^6\}\) and its derived subgroup is \(\{e,a^4\}\).

## Priced baseline

Generator lengths, from the right Cayley graph on \(\{a,b\}\), computed
before the matrix search:

| Element | Shortest generator word | Disjoint three-role bill |
|---|---|---:|
| \(a^2\) | \(aa\) | 6 |
| \(a^3\) | \(aaa\) | 9 |
| \(a^4\) | \(aaaa\) | 12 |
| \(a^5\) | \(bab\) | 9 |
| \(a^6\) | \(baba=(ab)^2\) | 12 |

The degree-1 relaxation does not decide these bills. The augmentation powers
of \(\mathbb F_2[M_{16}]\) have dimensions \(15,13,11,9,7,5,3,1,0\). The
quotient \(\Delta/\Delta^2\) has basis \(\alpha=[a]+1\) and \(\beta=[b]+1\).
Odd powers of \(a\) are congruent to \(\alpha\); \(a^2\), \(a^4\) and \(a^6\)
lie in \(\Delta^2\); \(b\) is congruent to \(\beta\).

Every paid deviation \(S=([g]+1)N\) has entries in \(\Delta\). For every pair
of paid calls, the cross term \(S_iS_j\) has entries in \(\Delta^2\). By
induction on those pairs, a product of calls is

\[
I+\alpha\sum_{a\text{-calls}}N_j+\beta\sum_{b\text{-calls}}N_j
\]

modulo \(M_3(\Delta^2)\). Both odd triples are congruent to \(I+\alpha I\).
Each admitted projector has trace 1 and \(I\) has trace 1, so every word for
either odd triple has an odd number of \(a\)-calls and an even number of
\(b\)-calls. Even lengths are impossible. The same congruence gives only an
even-length floor for \(a^2\), \(a^4\) and \(a^6\).

## Result

Lengths 1 through 4 were enumerated in \(M_3(\mathbb F_2[M_{16}])\). The exact
frontiers have sizes 56, 2052, 68955 and 2199152. Meet-in-the-middle on these
frontiers finds no word of length at most 7 for either odd triple. The
coordinate words

- \((E_{00},a)\) three times, then the same for \(E_{11}\) and \(E_{22}\),
- \((E_{00},b),(E_{00},a),(E_{00},b)\), then the same for \(E_{11}\) and \(E_{22}\),

equal the two odd targets and have length 9. Both minima are therefore 9.

The same frontiers find \(\operatorname{diag}([a^2]^3)\) at length 6 and not
earlier, realized by two \(a\)-calls on each coordinate projector. The
disjoint bill of 6 is sharp.

Separately, \(\operatorname{diag}([a^4]^3)\) and \(\operatorname{diag}([a^6]^3)\)
have no word of length at most 7. The symbol lemma already excludes the odd
lengths. The coordinate words above have length 12. Both exact minima
therefore lie in \(\{8,10,12\}\) and are not claimed to be sharp.

## Reproduce

From the repository root, with Python 3.12 and `PYTHONOPTIMIZE` unset:

```sh
python3 -B research/m16-generator-triple/verify.py
python3 -B scripts/research_package.py --package research/m16-generator-triple
```

Expected final verifier line:

```text
PASS_M16_GENERATOR_TRIPLE a2=6 a3=9 a5=9 a4_through7=0 a6_through7=0 a4_upper=12 a6_upper=12 idempotents=28 calls=56 frontier2=2052 frontier3=68955 frontier4=2199152 center=4 derived=2 controls=7 no_new_kappa
```

The script uses the standard library only. It checks the presentation,
associativity, the order-4 center, the derived subgroup, the augmentation
dimensions, the 28-idempotent scan of all 512 matrices, call inverses,
associativity of the paid calls and of their inverse-label calls, the
\(\Delta^2\) cross-term identity for every pair, and the frontiers. Seven
controls are required: the generator triples \(\operatorname{diag}([a]^3)\)
and \(\operatorname{diag}([b]^3)\) at length 3; the two-role square
\(\operatorname{diag}([a^2],[a^2],[e])\) at length 4, one role of \(a^4\) at
length 4 and one role of \(a^5\) at length 3; a dropped call failing on the
dirty state \(([a^5]+[b],[a^2],[a^4]+[a^3b])\); an \(a\)-for-\(b\) substitution
failing; the dihedral relation \(bab=a^7\) making the \(a^5\) witness fail;
and one explicit seven-call word whose matrix is first reached at length 7.
The rank-2 matrix \(E_{00}+E_{11}\) is not admitted.

Recorded environment: CPython 3.12.3, `g++` 13.3.0 with `/usr/bin/c++` pointing
at `/usr/bin/g++`, `libboost-dev` 1.83.0.1ubuntu2, and
`research/e8-bit-p111-tuned/requirements.txt` already satisfied by
`python3 -m pip install --user` (numpy 2.5.4, sympy 1.14.0, scipy 1.18.1).
`PYTHONOPTIMIZE` was unset. This package imports none of those libraries.
Direct verifier runtime on this machine was about 60 seconds.

Not run: `make frontier1094-verify`, the three-register C++ replay, a
four-role search, and lengths 8, 10 and 12 except for the explicit length-12
upper words. Odd lengths for the \(a^4\) and \(a^6\) triples are excluded by
the symbol argument, not by a separate search beyond the length-7 sieve.

## Open next questions

1. Is the minimum of \(\operatorname{diag}([a^4]^3)\) equal to 8, 10, or 12?
   The same question applies to \(\operatorname{diag}([a^6]^3)\). A value
   below 12 would be a real mixing saving in this alphabet. First step:
   store one length-4 word for each of the 2,199,152 depth-4 matrices and
   test the two targets by inverse meet-in-the-middle. This package builds
   that set for the length-7 sieve and does not store the words.
2. Can one restored scratch role realize
   \(\operatorname{diag}([a^5],[a^5],[a^5],[e])\) in fewer than 9 calls?
   A scratch role is the usual route past a three-role disjoint bill. First
   step: shortest-path search on the four-role alphabet of both generators
   and every rank-one idempotent in \(M_4(\mathbb F_2)\). That alphabet was
   not built.

## Credit

Predecessor model: the scalar-idempotent calls in
`research/bit-three-register-lower-bound`, from eumemic's pinned PR #288,
section 1.2. That theorem concerns rational rank-one frames, not this
generator alphabet. Quaternion and semidihedral order-16 certificates use
different relations and have center of order 2; their frontiers and targets
are not reused. Apache-2.0.

Substantial AI assistance was used to build the multiplication table, search
the paid words, and write these notes.

Discussion writes for this account return FORBIDDEN / Resource not accessible
by integration. No claim was posted, and the write was not retried.

Base commit `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Selector nonce
`a1330c55bf86b0ea1c2eb0ac57772471`, card `bit-new-register-model`, scope key
`7084092dd726e7ba1f2f`, priority revision 2. Catalogue SHA-256
`89b5928bc92c81e2647b6d702a7ad85a6795b8f44e2eb267b2ff3145d8f2b2ce`.
Selected-record SHA-256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
