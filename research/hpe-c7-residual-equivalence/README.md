# Selected hyperplane residual C7 is an equivalence

**Finite exact proof that the selected residual is a linear automorphism.
No new κ. The selected frontier is unchanged.**

## Task card

```text
Task ID / scope key: formal-interface-lemma / e3ffea67887eeb4c396c
Seed: 2214a0660d44883c91479d187c80c260
Track: independent-verification
Method drawn: audit a formal theorem-to-certificate binding independently
Base: ef5f39403610d231a0c27e8a6b4f08c10209bcd6
Selected record sha256: 10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32
Catalogue sha256: 89b5928bc92c81e2647b6d702a7ad85a6795b8f44e2eb267b2ff3145d8f2b2ce
Scope status: refined
```

The card asks for one interface lemma, or one theorem-to-certificate binding.
`HyperplaneEnd.factor_iff_pre` already proves the abstract cancellation: if (N)
holds and the residual `C` is a linear equivalence, then
`L⁻¹ T_U T_E⁻¹ R'⁻¹ = C ⊗ id` if and only if `R' = R`. The selected theorem
`hpe_word_exact` uses `C7`, and `Exact.lean` defines

```text
noncomputable def C7 : A →ₗ[ℂ] A := cL 128 (fourierC 7)
```

That is a linear map, not an equivalence. No pinned declaration has the shape
`C7 : A ≃ₗ[ℂ] A`. The two in-repo instance checkers
(`scripts/verify_hpe_lean_binding.py` and
`research/hyperplane-end-lean/code/check_hpe_pairs.py`) do not mention `C7`.
So the converse half of `factor_iff_pre` is not yet bound to the selected
residual, even though Jeremy Kothe's `gL_adj` and `cL_adjC` would supply it
after `cOk 128 (fourierC 7) = true`.

## Lemma

Let `A = ℂ^128`, with coordinates `x ∈ {0,…,127}`. For `i ∈ {0,…,6}` and
`s ∈ {+1,−1}` define the ℂ-linear map `G_{i,s}` by

```text
G_{i,s}(v)(x) = ((1 + s i) v(x) + (1 − s i) v(x ⊕ 2^i)) / 2.
```

This is the Lean gate `.cg (2^i) (s = +1)` on `ℂ^128`: `sg true = 1` and
`sg false = −1`. Let `C₇ = G_{6,+1} ∘ ⋯ ∘ G_{0,+1}` (qubit 0 first, as `cL`
applies the head of `fourierC 7` first). Let `C₇† = G_{0,−1} ∘ ⋯ ∘ G_{6,−1}`
(qubit 6 first). This `C₇†` is `cL 128 (adjC (fourierC 7))`.

**Claim.** `C₇† ∘ C₇ = id = C₇ ∘ C₇†` on `ℂ^128`. The same holds if the seven
sign-flipped gates are applied in qubit order `0,…,6` instead of reverse
order. In particular `C₇` is a linear automorphism, which is the residual
hypothesis of `factor_iff_pre`.

The single-gate coefficient identity is checked exactly: if
`α = (1+i)/2` and `β = (1−i)/2`, then the sign flip swaps `(α, β)` to
`(β, α)`, `2αβ = 1` and `α² + β² = 0`. Each shift `2^i` for `i < 7` is an
involution of `{0,…,127}` and stays inside that set, which is Lean's `Gate.ok`
test `((x XOR q) % 128 XOR q) % 128 = x`. The executable certificate then
applies both full circuits to every basis vector, both ways. Linearity of the
formula extends the basis identity to every vector. A witness:
`C₇(e_0)` has coordinate 0 equal to `1/16 − i/16`, so `C₇` is not the identity.

## What this does not prove

- The Lean kernel did not run. `cOk 128 (fourierC 7) = true` and
  `cE (fourierC 7)` were not `decide`d. `lake build` was not run.
- (N), `exact_N`, emitted monomials and `hpe_word_exact`'s other hypotheses
  (recipes, labels, unit row, hosting footprints) are untouched.
- `make frontier1094-verify` was not run. κ is unchanged.
- Discussion 2703 and PR 2706 already show that the instance checkers can
  accept a pre-wrapper *name* `E:FULL`. This package does not repeat that
  coverage audit. It only supplies the missing invertibility hypothesis those
  checkers never state.
- The general inverse `gL_adj` / `cL_adjC` is inherited. Replaying its ring
  proof is not the result.

## Reproduce

From the repository root, Python 3.12, standard library only.
`PYTHONOPTIMIZE` was unset. This command does not regenerate frontier artifacts.

```sh
python3 -B research/hpe-c7-residual-equivalence/verify.py
python3 scripts/research_package.py --package research/hpe-c7-residual-equivalence
```

Expected marker: `PASS_HPE_C7_RESIDUAL_EQUIVALENCE`.

The positive checks are the coefficient identity, the seven involutions, and
both two-sided inverses on all 128 basis vectors. The rejected controls are a
same-sign square of qubit 0, an adjoint circuit that drops qubit 0, and the
folded-XOR predicate on `ℤ/6` with shift 4. The verifier also re-reads the
pinned Lean definition lines and checks that the two instance scripts still
do not mention `C7`.

Environment used for this run: Python 3.12, g++ 13.3.0 with `/usr/bin/c++`
pointing at `/usr/bin/g++`, and `libboost-dev` installed. Those compilers are
not used by this verifier. `research/e8-bit-p111-tuned/requirements.txt`
(numpy, sympy, scipy) was already satisfied and is not imported here.

Orientation command, not a cold replay:

```sh
python3 -B scripts/research_baseline.py
```

It printed `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` with complex primitive
`67018507072324140917/40000000000000000000000` binding.

## Open next questions

Can one Lean kernel check turn this finite inverse into the hypothesis
`factor_iff_pre` actually consumes for a certified pair?

That matters because the converse, "a pre-wrapper other than `R` breaks (F)",
is still a docstring sentence for `C7` until `C` has type `A ≃ₗ[ℂ] A` in the
development that `hpe_word_exact` uses.

First step: in the existing `HyperplaneEnd` project, prove
`cOk 128 (fourierC 7) = true` by `decide +kernel`, define
`C7Equiv := cE (fourierC 7) h`, and apply `factor_iff_pre` at `pair1` with
`C := C7Equiv`. Do not rebuild the 512-dimensional `(N)` circuits to do that.

Blocker: this package did not run Lean 4.21 or Mathlib. The three certified
pairs and their emitted words stay outside this inverse.

## Credit

Jeremy Kothe (`jeremykothe2`) defined `C7`, `fourierC`, `factor_iff_pre`,
`gL_adj`, `cL_adjC` and `hpe_word_exact` in `research/hyperplane-end-lean`.
The selected record pins that development and `scripts/verify_hpe_lean_binding.py`.
Discussion 2703 and PR 2706 are about pre-wrapper names accepted by the
instance checkers. [Discussion comment 18982869](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-18982869)
and the handoff for `research/hpe-post-wrapper-lemma` give a post-wrapper
twin of `factor_iff_pre`: with invertible monomials, `L'` is a phase times
`L`. That argument uses `C₇ ⊗ id` as the residual identity. It does not
exhibit an inverse circuit for the linear map `C7`, which is the hypothesis
this package checks. Overlap on 2026-11-19 covered 1093 open PR records and
7775 discussion records, complete pagination, and did not find this basis
inverse. Closed PRs are not fully searched. No selected-frontier edit.

One Discussion write, `addDiscussionComment` on the handoff thread
[#1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166),
returned `FORBIDDEN` (`Resource not accessible by integration`). It was not
retried. The finding is this package and the pull request only.

Prepared by Riquelme Soares. Substantial AI assistance drafted the verifier,
the lemma statement and these notes. No coding-agent product is named. This
is not an independent human review. Apache-2.0.
