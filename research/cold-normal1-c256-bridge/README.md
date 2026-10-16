# Normal-1 cold chart on \(\mathbb{C}^{256}\otimes\mathbb{C}^{2}\)

**Finite interface identity. No new κ, supplier, or Lean proof term.**

For the empty entrance and one ordered hyperplane, the pinned canonical-frame
circuit and its ordered monomial chart satisfy the hypotheses of
`HyperplaneEnd.exact_cold`. The selected frontier is unchanged.

## Scope and evidence

Original card: `formal-interface-lemma` (independent verification). The scope is
**refined** to one normal, not to a new multiplication theorem. The selector
nonce is `c4b0b5c1cd55ff202ee4ed902021f754`, scope key
`e3ffea67887eeb4c396c`, priority revision 2, base
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. The positive control
`python3 -B scripts/research_baseline.py` returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`.

`HyperplaneEnd.exact_cold` in
[Multi.lean](../hyperplane-end-lean/HyperplaneEnd/Multi.lean) assumes

```text
(T E)⁻¹ = id
T U v = L (C.rTensor B (R v))
```

and concludes the same formula for `T U ((T E)⁻¹ v)`.
`cold_hyperplane_width` says rank 8 on top of the bottom frame has width 8 and
one spectator. Those statements stay conditional. This package instantiates
their numerical content for one frame and does not run Lean.

Let bits of \(x\in\{0,\ldots,511\}\) be \(x_0,\ldots,x_8\). The normal-1
hyperplane is \(\{x_0=0\}\). Its ordered basis, from extending the kernel of
the coordinate functional, is

```text
U = (2, 4, 8, 16, 32, 64, 128, 256).
```

Write \(y=(x\gg 1)\land 255\) and \(s=x\land 1\), and

```text
ρ(x) = y | (s << 8),    ρ⁻¹(z | (s << 8)) = s | (z << 1).
```

The pinned `canonical_frame(9, U)` emits two identity diagonals around
\(P_ρ\), the eight gates \(C\) on qubits \(0..7\), and \(P_{ρ^{-1}}\). The
empty frame emits no gates, so \(T_∅=\mathrm{id}\). On basis vectors the
nontrivial circuit is Fourier on bits \(1..8\), fixing bit \(0\):

\[
T|x\rangle=\sum_{z=0}^{255} c(z,y)\,|s\mid(z\ll 1)\rangle,
\]

where \(c(z,y)=16(-i)^{\mathrm{popcount}(z\oplus y)}/256\). That closed form is
the product of eight disjoint gates \(((1+i)I+(1-i)X)/2\): \((1+i)^8=16\) and
\((1-i)/(1+i)=-i\).

The pinned `lower_child` chart, with source `then` applying the left circuit
first, is the monomial pair

| | quadratic | `linear_Z4` | matrix rows | offset | phase |
|---|---|---|---|---:|---:|
| \(R\) | 0 | `(0,2,2,2,2,2,2,2,2)` | \(ρ\) | 255 | 0 |
| \(L\) | 0 | `(2,2,2,2,2,2,2,2,0)` | \(ρ^{-1}\) | 0 | 0 |

A zero quadratic and coefficient 2 contribute \((-1)\) per selected bit. Thus
\(R|x\rangle=(-1)^{\mathrm{wt}(y)}|(y\oplus 255)\mid(s\ll 8)\rangle\), and \(L\)
multiplies the low byte \(z\) by \((-1)^{\mathrm{wt}(z)}\) before applying
\(ρ^{-1}\). The byte that reaches \(C_8\) is \(y\oplus 255\), so the closed-form
exponent is \(8-d\) with \(d=\mathrm{popcount}(z\oplus y)\), and
\((-i)^{8-d}=i^d\). Expanding \(L(C_8\otimes\mathrm{id})R\) produces the coefficient

\[
\frac{16}{256}(-1)^{\mathrm{wt}(y)+\mathrm{wt}(z)} i^{d},\qquad d=\mathrm{popcount}(z\oplus y).
\]

The target coefficient is \(16(-i)^d/256=(-1)^d i^d\cdot 16/256\). They agree
because \(\mathrm{wt}(z\oplus y)\equiv\mathrm{wt}(z)+\mathrm{wt}(y)\pmod 2\),
after using \((-i)^{8-d}=i^d\). Therefore

\[
T_U=L(C_8\otimes\mathrm{id})R
\]

on \(\mathbb{C}^{512}\), with the tensor split \(x\mapsto(x\bmod 256,\lfloor x/256\rfloor)\).
Both `exact_cold` hypotheses hold for these maps. Global phase is kept.

The verifier re-derives the circuit from `basis_extend` and the quadratic form,
checks it against the pinned compiler, and checks the monomial bytes against
`lower_child`. Equality itself is an independent interpreter: every \(C\) gate
uses the signed average \(((1\pm i)I+(1\mp i)X)/2\), and all 512 basis columns
of \(T_U\) match \(L(C_8\otimes\mathrm{id})R\). The same columns match the
bit-0 formula. The closed form matches the eight \(C\) gates on both spectator
slices. Five mutations fail on a probe of columns \(0,1,255,256,511\): left
phase \(+1\), right offset xor \(256\), one reversed \(C\), a \(C\) moved onto
the spectator, and an omitted \(C\). One superposition checks additivity.

This is the normal-1 case of the cold factorization recorded in
[hyperplane-end-lean/PROOF.md](../hyperplane-end-lean/PROOF.md) section 7. The
all-511 source audit in CrocSwap PR 1697 is the predecessor finite check and is
not in this checkout. The added result is the ordered \(\mathbb{C}^{256}\otimes\mathbb{C}^{2}\)
chart and the coordinate identity for this single basis, which is the handoff
in discussion comment 18917564. It does not repeat that 511-hyperplane search.

## Reproduce

Python 3.12, standard library, from the repository root. `PYTHONOPTIMIZE` was
unset. g++ 13.3.0 and libboost-dev 1.83.0 are installed and `/usr/bin/c++`
points at `/usr/bin/g++`; this package does not compile C++. Lean and Lake were
not installed. `make frontier1094-verify` was not run.

```sh
python3 -B research/cold-normal1-c256-bridge/verify.py
python3 -B scripts/research_package.py --package research/cold-normal1-c256-bridge --check-only
python3.12 -B scripts/research_package.py --package research/cold-normal1-c256-bridge
```

Expected primary line:

```text
PASS_COLD_NORMAL1_C256_BRIDGE columns=512 full_operator_checks=2 controls=5 rank=8 spectators=1 global_phase no_lean no_new_kappa
```

Source commits, blobs and SHA256 pins are in [SOURCES.json](SOURCES.json).
The selected record and catalogue are historical provenance. The pinned
compiler and `Multi.lean` are live inputs.

## Limitations

The identity is one ordered basis of one hyperplane. It is not an emitted
helper word and does not check a unit row, zero column, tail chronology,
recipes on a word, footprints, hosting, precision, all-size compilation, or
analytic transfer. No moment, paid profile, or κ changes. The Lean kernel was
not run, so `exact_cold` is not discharged inside the proof assistant. A
numeric-mask adapter from these bit integers to Lean `Frame` and
`ℂ²⁵⁶ ⊗ ℂ²` is not built. `Exact.lean` still uses the two-spectator split
\(\mathbb{C}^{128}\otimes\mathbb{C}^{4}\).

Discussion writes were forbidden for this account: `addDiscussionComment` on
the handoff thread returned `FORBIDDEN / Resource not accessible by
integration`. The claim was not posted and the write was not retried.

## Open next questions

Can this hardcoded normal-1 chart be named inside Lean so `exact_cold` applies
with no external arithmetic? That would turn one conditional cold hypothesis
into a kernel-checked instance and show the tensor split a 256-by-2 adapter
must use. The smallest step is a theorem whose gate list and monomials are the
tables above, checked by `decide +kernel` on the existing Clifford semantics
after the spectator split is changed from two qubits to one. The blocker is
that split: the shipped `Exact.lean` operators are \(\mathbb{C}^{128}\otimes\mathbb{C}^{4}\),
and this package does not run Lake or Mathlib.

## Credit

Jeremy Kothe / jeremykothe2 supplied the hyperplane-end formalization. DreamingOfClouds
supplied `exact_cold` and `cold_hyperplane_width`. The compiler lineage in
`research/split-centres-global/vendor/clifford_exact.py` is used as the chart
definition and is not modified. Aaron Wang / navinor's all-511 semantic binding
(CrocSwap PR 1697, discussion comment 18917564) is the predecessor finite audit
and the source of this one-chart question. New work is Apache-2.0.

Prepared by a donated research session. Substantial AI assistance was used to
derive the coordinate identity, write the verifier, and prepare these notes.
No coding-agent product is named. No independent human review is claimed.
