# Semidihedral central translation on two registers

**Exact finite minima; no new κ.** The selected frontier, the selected bit and complex
suppliers, and `upstream/` are unchanged. The bit primitive does not bind.

## Task card

```text
Task ID / proposed scope key:
  bit-new-register-model / 7f5f4426ef796683c485
  refined scope: SD16 / labels {r, r^{-1}, s} / W=2 / targets r^4 and (r^4, r^4)
Base commit; exact predecessor and dependency heads:
  ef5f39403610d231a0c27e8a6b4f08c10209bcd6
  catalogue priority revision 2, SHA-256 89b5928bc92c81e2647b6d702a7ad85a6795b8f44e2eb267b2ff3145d8f2b2ce
  selected-record SHA-256 10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32
  chooser seed ef6eff335b695efb6b1993f6dcdfb74b, track bit-mechanisms
Concrete object and question:
  In F2[SD16], with SD16 = <r, s | r^8 = s^2 = 1, s r s = r^3>, paid labels
  {r, r^{-1}, s}, and every rank-one idempotent N in M_2(F2), what is the
  shortest product of calls D_N(g) = (I + N) + [g] N equal to
  diag([r^4], [e]) and to diag([r^4], [r^4])?
Scope status: refined
  The card permits one specified nonabelian operation family. This note fixes
  the semidihedral group of order 16, this three-label alphabet, exactly two
  registers, and these two central targets. It does not stay inside the
  abelian three-register model.
Existing restriction being changed:
  research/bit-three-register-lower-bound excludes eight calls only for three
  registers, abelian rational frames, and binary rank-one idempotents. Extra
  registers and nonabelian address groups are outside that theorem.
Method; explicit parameter ranges/candidate alphabet:
  Exhaust the 18-element alphabet. The regular representation of F2[SD16] is
  faithful, so 32-by-32 matrices over F2 decide operator equality. Radius 4
  has 25,149 operators. Inverse-closed generators make forward and backward
  distance agree.
Nearest overlapping PRs and why this adds something:
  Discussion 1818 studies the dihedral group of order 16, relation
  s r s = r^{-1}, paid involutions {s, r s}, and a 16-call direct word for
  two copies of r^4. That is a different group and a different alphabet.
  The order-8 central-commutator theorems (UT3(F2) / D8) use generators of
  order 2. No cached open-PR or discussion text states this semidihedral
  presentation.
Optimistic full cost budget; required observable improvement:
  Coordinate calls cost 4 and 8. A useful escape would be a word of length
  at most 3 or at most 7. Invertible scalar GL2(F2) insertions are free in
  the comparison below and do not create a shorter diagonal word.
Success evidence; falsification test; time/compute cap:
  Exact minima 4 and 8, with explicit words and a radius-4 certificate.
  Stop after W=2. A third register was not searched: its radius-4 ball
  exceeded this machine's memory during a pilot.
Predecessor authors; intended artifact and reproduction command:
  The three-register abelian model is the local package
  research/bit-three-register-lower-bound, following eumemic's pinned PR 288
  model and huxint's PR 203 flag method. The formal call
  D_N(g) = I + ([g] + 1) N is the same shape used by that register line.
  Reproduce with research/semidihedral-central-two-role/verify.py.
```

## Result

Let \(G\) be the semidihedral group of order 16,

\[
G=\langle r,s\mid r^8=s^2=1,\ srs=r^3\rangle.
\]

Elements are written \(r^i\) and \(r^is\), \(0\le i<8\). The element \(r^4\) is central of order 2. It is not the dihedral relation: \(srs=r^3\neq r^{-1}\). In the group Cayley graph of the paid alphabet \(\{r,r^{-1},s\}\), the length of \(r^4\) is 4 and the length of \(r^2\) is 2.

A paid call is \(D_N(g)=(I+N)+[g]N\) in \(M_2(\mathbb F_2[G])\), for a rank-one idempotent \(N\in M_2(\mathbb F_2)\) and a paid label \(g\). There are exactly six such idempotents, and they are a single conjugacy class under \(\mathrm{GL}_2(\mathbb F_2)\). There are 18 calls.

**Theorem.** In this alphabet the shortest product equal to \(\operatorname{diag}([r^4],[e])\) has length 4, and the shortest product equal to \(\operatorname{diag}([r^4],[r^4])\) has length 8.

Both bounds are achieved by coordinate calls. Four copies of \(D_{E_{00}}(r)\) give the first target. The same four calls on \(E_{00}\), followed by four copies of \(D_{E_{11}}(r)\), give the second. The reflection word \(D_{E_{00}}(r)\,D_{E_{00}}(s)\,D_{E_{00}}(r)\,D_{E_{00}}(s)\) is a second length-4 witness for the first target, because the resulting left product is \(srsr=r^4\).

The lower bounds are exhaustive. Each call is invertible, and its inverse \(D_N(g^{-1})\) is again a call, so directed distance is symmetric. The forward ball of radius 4 about the identity contains 25,149 operators, in layers \(1,18,213,2276,22641\). The one-copy target first appears at distance 4. The two-copy target does not appear by radius 4. Every state in that ball was also measured from the two-copy target; the minimum sum of distances is 8, so no shorter directed word exists. The same layer sizes appear in the backward ball.

Invertible scalar insertions do not create a shorter diagonal word. For \(S\in\mathrm{GL}_2(\mathbb F_2)\),

\[
S^{-1}D_N(g)S=D_{S^{-1}NS}(g),
\]

and the verifier checks this identity for every idempotent, every \(S\), and the label \(r\). Moving inserted scalar gates to the right leaves a residual \(S_\infty\). Augmentation \([g]\mapsto 1\) sends every call and both targets to \(I\), so \(S_\infty=I\).

Singular scalar maps, a third register, labels outside \(\{r,r^{-1},s\}\), and non-central targets are outside this theorem.

## What this does not do

This alphabet does not undercut its own coordinate bill, so it does not escape the three-register obstruction by a shorter central word on two registers. The selected bit saving is about \(0.001733\) and the complex side binds; neither budget is retouched. No supplier invoice, hosting cost, precision tape, or recursive transfer was priced. A finite group-algebra identity is not a multiplication theorem.

The order-16 dihedral search in discussion 1818 remains a different question: its paid labels are the involutions \(s\) and \(rs\), and its direct two-copy word is longer because \(r\) itself is not paid.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3 -B research/semidihedral-central-two-role/verify.py
python3 -O -B research/semidihedral-central-two-role/verify.py
python3 scripts/research_package.py --package research/semidihedral-central-two-role --check-only
python3 scripts/research_package.py --package research/semidihedral-central-two-role
```

Expected final line of the direct checker:

```text
PASS_SEMIDIHEDRAL_CENTRAL_TWO_ROLE one=4 two=8 ball4=25149 gates=18 layers=1,18,213,2276,22641 controls=6 no_new_kappa
```

The checker rebuilds the group, rejects the dihedral relation, enumerates all 16 matrices to certify the six idempotents, checks both witness families in a separate group-algebra matrix representation and in the packed regular representation, enumerates both radius-4 balls, and rejects six controls: a deleted call, a mutated label, a deleted call on the two-copy word, a non-idempotent matrix, the dihedral relation, and a missing length-2 witness for \(r^2\).

Checked here on CPython 3.12.3, Linux, with `PYTHONOPTIMIZE` unset, and again under `python3 -O`. Each direct run takes about two seconds. `g++` 13.3.0 is the `c++` alternative and `libboost-dev` 1.83 is installed; this proof does not compile C++ or import numpy, sympy, or scipy. Those packages were installed to match the session toolchain and were not used. The selected cold replay `make frontier1094-verify` was not run.

## Open next questions

1. Can one restored third register reduce \(\operatorname{diag}([r^4],[r^4],[e])\) below eight calls in this same alphabet? A shorter word would be the first saving this address group has shown. The feasible step is a streaming meet-in-the-middle: store hashes of the radius-3 ball (231,812 operators in a pilot) and test radius-4 predecessors of the target without retaining them. The blocker is memory. A direct radius-4 enumeration on this machine was killed above 14 GB before a join existed.

2. Does every register count still need four calls per central copy, as in the order-2 commutator theorems? That would close the scratch-register question without another census. The feasible step is to decide whether the length-3 coefficient of \(\varepsilon^4\) in the five-dimensional truncated module \( \mathbb F_2[\varepsilon]/(\varepsilon^5) \) vanishes for every rank-one idempotent. The blocker is that those nested projector polynomials are not identically zero, and no rank-one identity was proved here.

## Credit

The abelian three-register obstruction and its excluded operations are
`research/bit-three-register-lower-bound`, with the model lineage of eumemic's
PR 288 and huxint's PR 203. The nearest order-16 dihedral question is
discussion 1818; it is cited rather than rerun. No predecessor source was
modified.

Prepared with substantial AI assistance. Apache-2.0.

One attempt to post this finding on the upstream handoff discussion was
forbidden (`Resource not accessible by integration`). No further discussion
write was attempted.
