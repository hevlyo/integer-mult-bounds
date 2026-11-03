# Central bills in the semidirect product of order 16

**Finite register-model certificate; no new κ.** The selected result, both
primitive suppliers, and `upstream/` are unchanged. The complex primitive
binds. In this alphabet the proved central bills meet their coordinate
constructions, so register mixing does not undercut them.

Let \(G\) be the unique nonabelian semidirect product \(C_4\rtimes C_4\),

\[
G=\langle a,b\mid a^4=e,\ b^4=e,\ bab^{-1}=a^{-1}\rangle.
\]

Work in \(M_3(\mathbb F_2[G])\) with exactly three roles and paid calls

\[
D_N([g])=I+([g]+[e])N,
\qquad g\in\{a,b\},
\]

where \(N\) runs over all 28 rank-one idempotents in \(M_3(\mathbb F_2)\).
Matrix equality is an operator identity on arbitrary dirty states. Elements
are encoded by \(a^ib^j=i+4j\).

| Target | Coordinate bill | Minimum |
|---|---:|---:|
| \(\operatorname{diag}([a^2],[a^2],[a^2])\) | 6 | 6 |
| \(\operatorname{diag}([b^2],[b^2],[b^2])\) | 6 | 6 |
| \(\operatorname{diag}([a^2],[b^2],[a^2b^2])\) | 8 | 8 |
| \(\operatorname{diag}([a^2b^2],[a^2b^2],[e])\) | 8 | 8 |
| \(\operatorname{diag}([a^2b^2],[a^2b^2],[a^2b^2])\) | 12 | in \(\{8,10,12\}\) |

The last minimum is not claimed to be sharp. It is absent through length 6.

The changed hypothesis is the address group. The abelian three-register model
uses arbitrary rational rank-one frames and concludes that nine calls are
necessary for three invertible lower-triangular targets. This alphabet uses
only the two semidirect generators and charges every call. There is no free
scalar mixing outside the 28 idempotents and no fourth role. The group has
exponent 4, so it is not the dihedral, modular, semidihedral, or generalized
quaternion group of order 16. Its center is \(\{e,a^2,b^2,a^2b^2\}\) and its
derived subgroup is \(\{e,a^2\}\). In particular \(b^2\) is not a commutator,
which separates this group from \(Q_8\times C_2\).

## Priced baseline

Generator lengths, from the right Cayley graph on \(\{a,b\}\), computed
before the matrix search:

| Element | Shortest generator word | One-output minimum | Three-role coordinate bill |
|---|---|---:|---:|
| \(a^2\) | \(aa\) | 2 | 6 |
| \(b^2\) | \(bb\) | 2 | 6 |
| \(a^2b^2\) | \(aabb\) | 4 | 12 |

The one-output column allows every rank-one idempotent. The two idle roles
may be used and must be restored. They do not beat the generator word.
Thus a scratch role inside this three-role alphabet does not change the
coordinate bills above. The word \(abab\) is another expression for \(b^2\),
because \((ab)^2=b^2\), but it is longer than \(bb\).

The degree-1 relaxation excludes odd lengths for every target in the table.
The augmentation powers of \(\mathbb F_2[G]\) have dimensions
\(15,13,10,6,3,1,0\). The quotient \(\Delta/\Delta^2\) is two-dimensional, with
basis \(\alpha=[a]+1\) and \(\beta=[b]+1\). For \(a^ib^j\),

\[
[a^ib^j]+1\equiv (i\bmod 2)\,\alpha+(j\bmod 2)\,\beta
\pmod{\Delta^2}.
\]

Every square and the product \(a^2b^2\) therefore lie in \(\Delta^2\). Each
paid deviation has entries in \(\Delta\), and every product of two or more
deviations has entries in \(\Delta^2\). A word is congruent modulo
\(M_3(\Delta^2)\) to

\[
I+\alpha\sum_{a\text{-calls}}N_j+\beta\sum_{b\text{-calls}}N_j.
\]

Each admitted projector has trace 1. A target congruent to \(I\) hence needs
an even number of \(a\)-calls and an even number of \(b\)-calls, so its length
is even. All four central targets in the table are congruent to \(I\).

## Result

Lengths 1 through 3 were enumerated in \(M_3(\mathbb F_2[G])\). The exact
frontiers have sizes 56, 2352 and 92374. Meet-in-the-middle on these
frontiers finds the two square triples at length 6 and not earlier, the
mixed triple and the two-role product at no length through 6, and the
three-role product at no length through 6. The coordinate words

- \((E_{00},a)\) twice, then the same for \(E_{11}\) and \(E_{22}\),
- the same pattern with \(b\),
- \(aa\) on the first role, \(bb\) on the second, and \(aabb\) on the third,
- \(aabb\) on two roles, leaving the third at \(e\),
- \(aabb\) on all three roles,

realize the five targets at lengths 6, 6, 8, 8 and 12. The symbol lemma
turns the length-6 absence of the two length-8 targets into the exact
minimum 8. The three-role product remains unresolved at the even lengths
8, 10 and 12.

## Reproduce

From the repository root, with Python 3.12 and `PYTHONOPTIMIZE` unset:

```sh
python3 -B research/c4-semidirect-central-floor/verify.py
python3 -B scripts/research_package.py --package research/c4-semidirect-central-floor
```

Expected final verifier line:

```text
PASS_C4_SEMIDIRECT_CENTRAL a2=6 b2=6 mixed=8 two_z=8 z_through6=0 z_upper=12 one_z=4 idempotents=28 calls=56 frontier2=2352 frontier3=92374 center=4 derived=2 involutions=3 aug=15,13,10,6,3,1,0 controls=8 no_new_kappa
```

The script uses the standard library only. It checks the presentation,
associativity, the exponent, the order-4 center, the derived subgroup, the
augmentation dimensions and the degree-1 classes, the 28-idempotent scan of
all 512 matrices, call inverses, associativity of the 56 paid calls, the
symbol congruence on every length-2 and length-3 frontier matrix, and the
frontiers. Eight controls are required: the positive lengths listed above;
the symbol congruence on every length-2 and length-3 frontier matrix;
the \(a^2\) witness on the dirty state
\(([ab]+[b],[a^2],[a^2b^2]+[a^3])\); a dropped call failing on that state;
an \(a\)-for-\(b\) substitution failing; the direct-product law
\(ab=ba\) making the \(abab\) witness fail; rejection of the rank-2 matrix
\(E_{00}+E_{11}\); and one explicit five-call word whose matrix is first
reached at length 5.

Recorded environment: CPython 3.12.3, `g++` 13.3.0 with `/usr/bin/c++` pointing
at `/usr/bin/g++`, `libboost-dev` 1.83.0.1ubuntu2, and
`research/e8-bit-p111-tuned/requirements.txt` already satisfied by
`python3 -m pip install --user` (numpy 2.5.4, sympy 1.14.0, scipy 1.18.1).
`PYTHONOPTIMIZE` was unset. This package imports none of those libraries.
Direct verifier runtime on this machine was about 13 seconds.

Not run: `make frontier1094-verify`, the three-register C++ replay, a
four-role search, and the length-8, length-10 and length-12 frontiers.
Odd lengths for the central targets are excluded by the symbol argument.
The three-role product was not searched past length 6.

## Open next questions

1. Is the minimum of \(\operatorname{diag}([a^2b^2]^3)\) equal to 8, 10, or
   12? A value below 12 would be a real mixing saving in this alphabet.
   First step: store one length-4 word for each length-4 matrix and test the
   target by inverse meet-in-the-middle, using the symbol lemma to skip odd
   lengths. This package builds only the length-2 and length-3 frontiers.
   Blocker: the length-4 set was not stored, and the length-6 screen only
   splits words as 3+3.
2. Can one restored fourth role realize
   \(\operatorname{diag}([a^2b^2],[a^2b^2],[a^2b^2],[e])\) in fewer than 12
   calls? A scratch role outside the three output roles is the usual route
   past a sharp three-role bill. First step: shortest-path search on the
   four-role alphabet of both generators and every rank-one idempotent in
   \(M_4(\mathbb F_2)\). Blocker: that alphabet was not built, and it is
   premature until the three-role minimum above is known.

## Credit

Predecessor model: the scalar-idempotent calls in
`research/bit-three-register-lower-bound`, from eumemic's pinned PR #288,
section 1.2. That theorem concerns rational rank-one frames, not this
generator alphabet. Order-eight and order-sixteen dihedral certificates,
including the two-register reflection search for \(\operatorname{diag}([r^4],[r^4])\),
use a different relation and do not admit the order-4 element \(b\) of this
presentation. Quaternion, modular, and semidihedral generator alphabets have
elements of order 8; their frontiers and targets are not reused. Apache-2.0.

Substantial AI assistance was used to build the multiplication table, search
the paid words, and write these notes.

Discussion writes for this account return FORBIDDEN / Resource not accessible
by integration. No claim was posted, and the write was not retried.

Base commit `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Selector nonce
`b97b573eb6e23057911515d5e72ca8f3`, card `bit-new-register-model`, scope key
`7f5f4426ef796683c485`, priority revision 2. Catalogue SHA-256
`89b5928bc92c81e2647b6d702a7ad85a6795b8f44e2eb267b2ff3145d8f2b2ce`.
Selected-record SHA-256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
The required baseline command returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`.
