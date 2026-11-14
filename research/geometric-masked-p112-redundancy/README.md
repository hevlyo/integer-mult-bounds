# Geometric masking does not enlarge the P112 decoder family

On the complement of one coordinate frame, a geometric E8 decoder that matches
the Gram only on even inner products is already an all-pairs decoder. The mask
does not create a cheaper copied-information account, a new frame, or a
restoration. There is no new \(κ\).

## Task card

```text
Task ID / proposed scope key:
complex-masked-decoder / 7acfe4d9cac04f7ba4cb
Refined object: geometric normals on the P112 coordinate-frame complement.

Base commit; exact predecessor and dependency heads:
ef5f39403610d231a0c27e8a6b4f08c10209bcd6
Chooser seed bbc6e2c522c37e7b4e7a62e0288d92c3; track complex-mechanisms;
priority revision 2.
Catalogue SHA-256 89b5928bc92c81e2647b6d702a7ad85a6795b8f44e2eb267b2ff3145d8f2b2ce
Selected-record SHA-256 10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32
No package file is imported. The eight-term packages below are attribution,
not runtime dependencies.

Concrete object and question:
For M in C^{8×8}, the masked equations ρ^T M σ = 2⟨ρ, σ⟩ on live pairs of
even inner product, with the eight coordinate-frame lines deleted: does any
such M differ from 2I, and if not, do odd pairs still need cost-0 repairs?

Scope status: refined.
The card allows one masked family with exact labels and supports. This family
is the geometric normal model on one pinned 112-line set. It is not the
eight-term all-pairs search, and it is not an abstract E-graph matrix.

Existing restriction being changed:
The eight-term theorem demands the identity on every live pair. Here the odd
pairs are not imposed. Non-geometric coefficients and nine or more columns
stay outside the claim.

Method; explicit parameter ranges/candidate alphabet:
Exact linear algebra on the 64 entries of M. The written equations use the 24
live coordinate axis pairs outside F = {e_{2a}±e_{2a+1} : a = 0,1,2,3} and
three cross-block couplings. The census uses all 112 live lines.

Nearest overlapping PRs and why this adds something:
The frame-pair package and the complex eight-term extension exclude masked
identities rather than solving this bilinear system. Abstract rank-8 E-graph
rigidity (discussions 1210, 1275, 1384, 1395, 1411, and the P108/P109
follow-ups) allows an arbitrary matrix on the lines. No open-PR or discussion
excerpt in the 2026-11-14 overlap snapshot states that the even bilinear
equations force M = 2I.

Optimistic full cost budget; required observable improvement:
An improvement would be an eight-column geometric M other than 2I, or a
nonzero odd-repair count forced by the mask. Either would be a new support
geometry. The result is that both are absent, so the copied-information
account is the all-pairs account.

Success evidence; falsification test; time/compute cap:
Unique solution M = 2I, 5824 odd live pairs already correct, and the two
controls in PROOF.md. One session, standard-library arithmetic only.
Predecessor authors; intended artifact and reproduction command:
DreamingOfClouds' B14/frame-pair model and the complex eight-term extension.
Artifact: this package. Command below.
```

## Scope and evidence

A geometric decoder has Gram entries \(ρ^T M σ\). The selected complex side is
priced on a 112-port puncture of this shape: one coordinate frame is removed.
The masked model, excluded by the eight-term theorem, would keep the diagonal
and orthogonal equations and repair odd entries by cost-0 singletons.

The even equations already have unique solution \(M = 2I\). Odd entries then
equal \(2⟨ρ, σ⟩\) with no repair. An eight-column factorization is a dual basis
\(AB^T = 2I\), which is the all-pairs hypothesis the existing copy-cost theorem
already covers. This package does not re-prove that copy-cost inequality and
does not change a child histogram or \(κ\).

The proof is [PROOF.md](PROOF.md). The verifier replays the 108 coordinate
equations, the rank-62 gap left by deleting the last coupling, an inconsistent
right-hand side, the \(112^2\) live pairs, and a modular rank certificate for
all 6720 even rows.

Orientation in this session, not a dependency of the new proof:

```text
python3 -B scripts/research_baseline.py
PASS_RESEARCH_BASELINE_BINDINGS_ONLY
python3 -B research/complex-decoder-field-extension-seed44/verify.py
PASS_COMPLEX_DECODER_FIELD_EXTENSION_S44 p=0..24 examples=3 attaining=25 pairing=14400 controls=7
```

Python 3.12.3, assertions enabled, `PYTHONOPTIMIZE` unset. The C++ toolchain
was the repository default (`g++` 13.3.0 as `/usr/bin/c++`, `libboost-dev`
installed) and is not used here. NumPy 2.5.4, SymPy 1.14.0, and SciPy 1.18.1
were already installed from `research/e8-bit-p111-tuned/requirements.txt` and
are not used. `make frontier1094-verify` was not run.

Discussion writes were unavailable: this session's GitHub interface is
read-only and no discussion-write tool is configured. No discussion post was
attempted.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B research/geometric-masked-p112-redundancy/verify.py
python3 scripts/research_package.py --package research/geometric-masked-p112-redundancy --check-only
python3.12 scripts/research_package.py --package research/geometric-masked-p112-redundancy
```

Expected final line of the mathematical check:

```text
PASS_GEOMETRIC_MASKED_P112_REDUNDANCY proof_equations=108 proof_rank=64 live=112 even_live=6720 odd_live=5824 repairs=0 full_even_rank_mod=64 controls=2
```

## Open next questions

1. Can nine or more columns factoring this same \(M = 2I\) have total label-pairing cost below the eight-column floor on this P112 set? That is the overcomplete escape that this redundancy does not close. First step: price one explicit nine-column factorization of \(2I\) with exact supports, including every repeated column. Blocker: support cost is not a function of \(M\) alone, and the abstract nine-term floors in the discussion record are not this geometric factorization.

2. Which punctures make the even bilinear system have a positive-dimensional solution space? A nontrivial \(M\) would be the first geometric mask that is not an all-pairs decoder. First step: delete one further orbit of coordinate lines and rerun the 64-column rank. Blocker: a kernel matrix still needs supports, frames, and restoration before it is a budget.

## Credit

The root and label conventions follow the frame-pair exposition of
DreamingOfClouds' B14 model in `research/complex-frame-pair-decoders`, and the
masked-identity exclusion recorded again in
`research/complex-decoder-field-extension-seed44`. The eight-term copy floor is
their result; this note only shows that the geometric mask on this puncture
lands back inside that hypothesis. Abstract E-graph rigidity is parallel work
on a different matrix and is not an input.

Prepared by a research session with substantial AI assistance. No coding-agent
product is named. Apache-2.0. The selected frontier is unchanged.
