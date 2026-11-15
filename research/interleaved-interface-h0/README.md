# Cleanup inversion needs an unstated operand hypothesis

**Audit of one restoration implication; no new κ.** The five named
hypotheses H1–H5 of the interleaved scalar-interface lemma do not imply
that cleanup is the inverse of the raw z-action. One extra operand
hypothesis repairs the implication for every finite word in the XOR-gate
model below. The selected frontier is unchanged.

This is not an acceptance bug in `xcheck_p.py`. Its `replay` rejects the
witness before it will report H1–H5. The gap is in the implication as
stated by the five bullets and the proof's parenthetical.

## Task card

```text
Task ID / proposed scope key: uniform-transfer-audit / 603f341b99f590f17a76
Base commit: ef5f39403610d231a0c27e8a6b4f08c10209bcd6
Selected-record sha256: 10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32
Assignment seed: 33969db763dc539fd8b92c2bb4cf1cc6
Track: adversarial-audit (priority revision 2)
Predecessor: eumemic, PR #543 lemma text pinned at research/e8-bit-r420/README.md
  (git blob 6751eba6f617292fc919e58d5a9f9f06ab037391)
Checker text: research/e8-bit-p111-tuned/code/xcheck_p.py
  (git blob 184f5dcf94a486cc7db91ca4db5865916bf26009)
Concrete object: the F2 claim that H1–H5 imply C = U^{-1} on W0 = (A, scatter, B)
Scope status: refined. The card allows one restoration lemma. The quantified
  statement is this gate model, not another replay of the selected word.
Existing restriction being audited: "Over F2 each is an involution (the
  destination is never among its own sources), so C = U^{-1}."
Method: write H0z explicitly; prove the repaired implication; exhibit one
  minimal word where H1–H5 hold and cleanup does not restore z.
Nearest overlap: open draft PR #2721 (head 6b14e212a1aba401d29f2bf7378e745ee2aed7f2)
  uses the same z-gate induction for a different question, H2-sem condition 2
  on a framed D prefix. It does not test this parenthetical.
Optimistic budget: a sound hypothesis list for cleanup inversion. No κ change
  is possible from this audit, and none is claimed.
Success: the repaired proof, plus a word the five booleans accept and the
  inverse rejects. Falsifier: any H0z word inside the enumerated domains whose
  H1–H5 hold and whose cleanup fails.
Stop: do not replay the 111-port word or make frontier1094-verify.
```

## Proposition

Registers are split into sources `x`, targets `y` and helpers `s`, with
`z = (x, s)`. A gate replaces its destination by the sum, over F2, of the
destination and the listed sources, reading every source before the write.
Sections run in the order D, A, scatter, B, C. Scatter adds a snapshot of
listed helper values into each target and does not read targets.

**(H0z)** Every z-destination gate in A and in B has its destination absent
from its source list. Duplicate or empty source lists are allowed.

**(H1)** No z-destination gate reads a target.

**(H2)** Every D gate writes a target and reads only helpers.

**(H3)** A writes only z registers. Every B gate either writes a target, or
writes a z register and reads only z registers. Scatter reads only helpers.

**(H4)** C is exactly the z-destination gates of A then B, reversed, with the
same destinations and source lists.

**(H5)** The target-to-target block `V` of `W0 = (A, scatter, B)` is the
identity.

**Theorem.** H0z and H1–H5 imply that `W0` acts by `(z, y) ↦ (U z, y + J x + K s)`
with `U` invertible, that C acts by `(z, y) ↦ (U^{-1} z, y)`, and that the
whole word acts by `(x, s, y) ↦ (x, s, y + J x + (K + N) s)`, where D acts by
`y ↦ y + N s`. They do not imply `J = I` or `N = K`, so they do not imply the
shear `(x, s, y) ↦ (x, s, y + x)`.

**Counterexample to the five bullets alone.** One source `x`, one target `y`,
one helper `h`. D is empty, scatter is empty, A is `h ^= h`, B is `y ^= x`,
and C repeats `h ^= h`. H1–H5 hold and H0z fails. After W0 the helper mask is
0, so `U` is singular, and C leaves it 0. On the identity basis the masks are
`(x, y, h) = (1, 3, 0)` before C and `(1, 3, 0)` after C.

## Proof

If a gate's destination is not in its source list, the assignment
`d ← d + Σ sources` is a linear involution, even when the source list is
empty or has repeated entries. H0z therefore makes every z-gate of A and B
a linear involution on `z`. H1 and H3 keep those gates off the targets, so
they do not read or write `y`.

By induction through W0, the state stays of the form `z = U_k z_0` and
`y = V_k y_0 + M_k z_0`. A z-gate left-multiplies `U_k` by an involution and
leaves `y`. A target gate whose destination is outside its sources replaces
`y` by `P y + Q z` with a linear involution `P`. The first target gate whose
destination occurs in its own sources, if every earlier gate was bijective,
identifies two states that differ only in that target. Later gates cannot
separate them, so `V` is not injective and H5 fails. Thus H5 forces every
target gate to exclude its destination as well. Scatter is a target update
from a helper snapshot, so it has the same shape. Hence
`W0(z, y) = (U z, V y + J x + K s)`. H5 says `V = I`. The product of the
z-involutions is invertible, and H4 runs those involutions in reverse, so
`C = U^{-1}` on `z` and C does not change `y`.

H2 writes targets from helpers only, so a D destination is not among its
sources and D does not write `z` or read an updated target. D is therefore
`y ← y + N s`. Composing D, then W0, then C gives the stated map. `J = I`
and `N = K` are further equalities. The fixture `B = (y ^= h)`, with every
other section empty, satisfies H0z and H1–H5 and ends at `y + h`, not `y + x`.

The product of involutions need not itself be an involution. The word
`A = (x ^= h, h ^= x)`, `B = (y ^= x)`, with C the reverse of A, has
`U^2 ≠ I` on the hand-checked masks `(x, y, h) = (5, 7, 1)` after W0, while
C still restores `(1, 7, 4)`. The proof uses the reverse product, not the
false shortcut `U = U^{-1}`.

Frame climbs, label realization, signed integer shears, and the all-size
compiler are outside this argument. The parenthetical in the pinned lemma is
true as an extra hypothesis and false as a fact inferred from H1–H5.

## What the selected checker already does

In the pinned `xcheck_p.py`, `replay` rejects a gate unless its destination
and sources are pairwise distinct and the source list is nonempty. That line
is 247. The H1 predicate is line 324 and the cleanup-inverse conclusion is
line 361. `interface` evaluates H5 by calling `replay`, so a self-source
gate raises before a completed H1–H5 report exists. `check` also runs `full`
before `interface`. Distinct nonempty operands imply H0z, so a word that
reaches the checker's PASS line has the missing hypothesis. The five printed
names are still not the whole hypothesis list. The checker's guard is
stronger than H0z: the duplicate-source gate `h ^= x ^= x` is an involution
and inverts, but it fails pairwise distinctness.

## Finite corroboration

The proof covers every finite width. The checker additionally enumerates:

| Domain | Words | H1–H5 | Repaired implication | H1–H5 but C is not inverse |
| --- | ---: | ---: | ---: | ---: |
| v=1, R=1, lists of length at most 2, destination excluded | 1,507,142 | 1,302 | 1,302 | 0 |
| v=1, R=0, lists of length at most 2, destination excluded | 343 | 3 | 3 | 0 |
| v=2, R=1, lists of length at most 1, destination excluded | 1,755,904 | 2,880 | 2,880 | 0 |
| v=1, R=1, lists of length at most 1, destination allowed in the source list | 21,296 | 280 | 72 | 208 |

A separate search of 167,440 words with a target self-read and H0z gates
found 1,680 words satisfying H0z and H1–H4. All 1,680 fail H5. These counts
are checks of the proof on those domains, not a substitute for it.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3 -B research/interleaved-interface-h0/verify.py
python3 scripts/research_package.py --package research/interleaved-interface-h0 --check-only
```

Expected first line: `PASS_INTERLEAVED_INTERFACE_H0`. The metadata command
checks pins only. It is not mathematical acceptance.

Recorded environment: Python 3.12.3, `PYTHONOPTIMIZE` unset. The same
command under `python3 -O` also prints the PASS line, because the checks
raise exceptions rather than using assertions. `g++` 13.3.0 is the `c++`
alternative at `/usr/bin/g++`, and `libboost-dev` 1.83.0.1ubuntu2 is
installed. `research/e8-bit-p111-tuned/requirements.txt` resolved to numpy
2.5.4, sympy 1.14.0 and scipy 1.18.1; this package does not import them.
The verifier ran in about 48 seconds. It writes no files.

Not run: `make frontier1094-verify`, `xcheck_p.py` on a pinned word, native
C++ stage replays, and any signed-integer or frame-climb proof.

## Discussion

One attempt to open a finding thread returned HTTP/GraphQL `FORBIDDEN`
(`Resource not accessible by integration`). Discussion writes are not
available to this session, so the call was not retried. The finding is
recorded in this package and the pull request.

## Open next questions

The frame paragraph of the same pinned proof says that after B every z
register can climb to the single full frame, so C is legal there. That
claim is not part of the F2 theorem above. It matters because a word can
satisfy H0z and H1–H5 and still be an illegal climb. The smallest next step
is to state the nesting hypotheses and prove or refute that one climb, using
the pinned frame poset rather than a new scalar search. This package does
not load those frames.

A second question is whether any formalization of this lemma transcribes
only H1–H5. That matters because a proof assistant would then accept the
self-source witness or silently assume H0z. The first step is to search the
pinned formalization notes for this cleanup argument. No Lean build was run
here.

## Credit

The lemma statement and the involution parenthetical are eumemic's, from
PR #543, as preserved in `research/e8-bit-r420/README.md`. The operand guard
and the H1–H5 predicate layout are from the punctured checker
`research/e8-bit-p111-tuned/code/xcheck_p.py`, itself adapted from the R420
checker. PR #425's scalar-interface lemma, cited there, is Zhihao Chen's.
PR #2721 (geckods) is a different necessary-hypothesis audit of this same
lemma and is not contradicted. No selected supplier, owner, or certificate
is modified.

Prepared by Riquelme Soares. Substantial AI assistance was used to draft the
proof, the independent checker, and these notes. This is not independent
human review. Apache-2.0.
