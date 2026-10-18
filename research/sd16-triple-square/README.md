# Semidihedral triple square: exact length 6

**Scoped negative result; no new κ.** In the three-role semidihedral register
model below, `diag([r^2], [r^2], [r^2])` has minimum paid length 6. The
matching uniform identity is the doubled coordinate word. Reflections are in
the paid alphabet and do not make a shorter word. The selected frontier is
unchanged.

This does not escape the scoped three-register obstruction. It prices one
nonabelian alphabet outside that obstruction and shows that this target does
not undercut its disjoint bill.

## Scope

Assignment: track `bit-mechanisms`, card `bit-new-register-model`, selector
scope key `7084092dd726e7ba1f2f`, OS nonce `6f7a9ea6cd4e657dcf8c3a81f9840d4a`.
Exact base `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Selected-record SHA-256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. Catalogue
priority revision 2.

**Changed hypothesis.** The predecessor in
[research/bit-three-register-lower-bound](../bit-three-register-lower-bound/README.md)
uses the additive abelian group `M_3(Q)` and forbids arbitrary free address
maps between calls. This package replaces that address group by the
semidihedral group of order 16,

```text
SD16 = <r, s | r^8 = s^2 = e, s r s = r^3>.
```

The relation is not the dihedral relation `s r s = r^{-1}`. Scope status is
**refined**: the card allows one specified nonabelian family, and the family
here is exactly this presentation, the charged labels `{r, s}`, and three
output roles.

**Roles and alphabet.** There are three roles and no scratch role. A paid call
is

```text
D_N([g]) = I + ([g] + [e]) N,
```

where `g` is `r` or `s` and `N = x y^T` runs through the 28 binary rank-one
idempotents on `F_2^3` (`y^T x = 1`). The alphabet has 56 calls. A final
matrix equality in `M_3(F_2[SD16])` is an operator identity, so it holds for
every dirty input state in `(F_2[SD16])^3`.

**Target.** `diag([r^2], [r^2], [r^2])`.

## Priced baselines

| Bill | Length | What it says |
|---|---:|---|
| Disjoint diagonal word, two `r`-calls on each `E_ii` | 6 | Achieved by the identity below |
| First-order abelianization, ignoring the `αβ` term | 2 | Necessary for the image to be `I`, and not sufficient |
| Exact minimum in the 56-call alphabet | 6 | Shortest-word search |

`SD16 / <r^2> ≅ C_2 × C_2`. Write `α = [x] + 1` and `β = [y] + 1` for the
images of `r` and `s`. Then `α^2 = β^2 = 0`, while `αβ ≠ 0`. Every word maps
to `I + α (∑ N_r) + β (∑ N_s) + αβ K`. The target maps to `I`, so both
projector sums must vanish and so must `K`. Vanishing sums already force
length at least 2. That optimistic floor is the priced relaxation. It does
not meet the disjoint bill, so the exact search is what decides the target.

## Uniform identity

Each call `D_{E_ii}([g])` is diagonal, with `[g]` in position `i` and `[e]`
elsewhere. Diagonal entries therefore multiply in call order. The word

```text
(E11, r), (E11, r), (E22, r), (E22, r), (E33, r), (E33, r)
```

has diagonal `[r][r] = [r^2]` in every role. The same reasoning gives two
companion identities used as controls and upper bounds:

- `(E11, r)` twice equals `diag([r^2], [e], [e])`.
- `(E11, s), (E11, r), (E11, r), (E11, s)` equals `diag([r^6], [e], [e])`,
  because `s r^2 s = r^6`. Two pure rotations do not isolate `[r^6]`.
- Four rotations on one `E_ii` equal `[r^4]` there. Repeating either long
  element on all three roles costs 12.

The length-4 reflection word is the smallest witness that the semidihedral
operation is not idle: `[r^6]` on one role has minimum length 4.

## Exact minimum

A shortest-path enumeration of the 56 calls produces 56, 2,051 and 68,899
matrices at lengths 1, 2 and 3. The target is absent. Every length-2 and
length-3 matrix in that frontier is invertible as an operator on
`(F_2[SD16])^3`. Splitting a hypothetical shorter word into shortest halves
gives no length-4 or length-5 factorization (0 pairs). The same split at
length 6 finds 799 ordered pairs, in agreement with the explicit word.

The search is a minimum-length argument. If a word of length `L ≤ 6` exists,
some word of length `ℓ = min length` exists, and that shortest word splits
into shortest halves of lengths `(2,2)`, `(3,2)` or `(3,3)`. Those halves lie
in the enumerated frontiers. One matrix reachable by a two-call word is the
identity itself: every repeated reflection square `(I + ([s] + [e]) N)^2`
equals `I`. Exact length 2 therefore has 2,052 distinct matrices, one more
than the shortest frontier.

The same length-6 sieve shows that `diag([r^4], [r^4], [r^4])` and
`diag([r^6], [r^6], [r^6])` have **no** word of length at most 6. The
disjoint words give upper bound 12. Those two bounds are not claimed to be
sharp.

A positive sieve control keeps the empty counts meaningful:
`diag([r], [r], [r])` has minimum length 3, and the length-5 split still
finds 196 non-minimal factorizations of it.

## What is not claimed

- No new κ and no change to the selected record. The complex primitive binds.
  This note does not alter either supplier. `make frontier1094-verify` was
  not run.
- No four-role or scratch-register statement. Three roles are the whole model.
- No claim about dihedral groups, quaternion groups, or other presentations.
  The dihedral order-16 reflection model (central involution, two roles) and
  the D8 central-commutator models are different groups, alphabets or targets.
- The length-6 absence for the two longer triples is not a minimum. Lengths
  7 through 11 were not searched.
- Finite `F_2`-column checks are not the certificate. The certificate is
  equality of all nine group-algebra entries, recomputed by the diagonal
  group word for the explicit identities and by the operator search for the
  lower bound.
- This is not a proof-assistant formalization and not an integer-multiplication
  theorem.

## Reproduce

Standard library only, from the repository root. `PYTHONOPTIMIZE` is unset;
the checks are explicit branches, not assertions.

```sh
python3 -B research/sd16-triple-square/verify.py
python3 -B scripts/research_package.py --package research/sd16-triple-square --check-only
```

Expected final line of the verifier:

```text
PASS_SD16_TRIPLE_SQUARE length=6 frontier=1,56,2051,68899 exact2=2052 len4=0 len5=0 len6=799 r4_through6=0 r6_through6=0 generator_len5_hits=196 rejected=6 no_new_kappa
```

The run is about 20 seconds on CPython 3.12. The registered replay command is
the same verifier. Session toolchain, not imported by this package: `c++`
already selected `/usr/bin/g++`, `libboost-dev` 1.83.0.1ubuntu2 was present,
and `research/e8-bit-p111-tuned/requirements.txt` was installed with
`python3 -m pip install --user`. The positive control
`python3 -B scripts/research_baseline.py` returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`.

Rejected fixtures: a dropped final call, an `r → s` substitution, a projector
moved onto a role that already has its two calls, every trace-zero `x y^T`,
the dihedral relation `s r s = r^7`, and the dirty state
`([r^5], [s], [r^2] + [s])` on the dropped word. Accepted controls: the
length-6 word, the single-role square, the reflection square back to `I`,
the length-4 conjugation, the length-12 upper bounds, inverse roundtrip, and
the 196 length-5 hits on the generator triple.

## Open next questions

1. **One restored scratch role.** Can `diag([r^2], [r^2], [r^2], [e])` be
   realized in `M_4(F_2[SD16])` with the same labels and all 120 rank-one
   idempotents in fewer than 6 calls? A scratch role is the usual way past a
   three-role disjoint bill; the D8 central-pair precedent needed an extra
   role for a different target. First step: shortest-path BFS to depth 3 on
   the 240-call alphabet. Blocker: that depth-3 set was not built here, so
   this package claims nothing about four roles.

2. **Sharp length of the longer triples.** Is the minimum of
   `diag([r^4], [r^4], [r^4])`, and likewise `[r^6]`, equal to 12 or to some
   length in 7..11? A value below 12 would be the first triple-target saving
   in this alphabet. The length-6 sieve already excludes 1..6, and the
   disjoint words give 12. First step: meet in the middle at length 8 on the
   depth-4 frontier. Blocker: that frontier has 2,198,276 matrices and was
   not inverted here.

## Credit and coordination

The abelian three-register model and its nine-call theorem are the pinned
predecessor, including eumemic's PR #288 scalar-idempotent model and the
local package above. Nearby register-model work uses different groups or
targets: D8 central commutators, the order-eight dihedral reflection alphabet
on two roles with target `[r^4]`, odd-dihedral joint tariffs, and the Dic3
generator alphabet. Those results are not inputs to this search.

Overlap refresh at 2026-10-18T12:23:05Z covered 348 open PRs and 2,454
discussion records with complete pagination. The exact terms `semidihedral`
and `SD16` matched only this package. Closed PRs are visible to that search
only through local notes and the ledger.

Discussion writes for this account return FORBIDDEN / Resource not accessible
by integration. No claim was posted, and the write was not retried.

Prepared by an AI-assisted contributor. Substantial AI assistance was used to
set up the multiplication table, implement the shortest-word search, and write
these notes. New work is Apache-2.0.
