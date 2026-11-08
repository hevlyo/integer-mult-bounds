# Cold hyperplane factor census

**Finite discharge of the cold frame hypotheses. No new κ.**

## Scope and evidence

Original card: `formal-interface-lemma`, scope key `e3ffea67887eeb4c396c`, selector nonce `c0cdcab4e0310c8deaddcf545df3e0e0`, priority revision 2. Base commit `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Scope status: **refined**. The card allows one interface lemma. This package keeps that premise and narrows it to the cold specialization in `HyperplaneEnd/Multi.lean`.

`exact_cold` assumes two operator hypotheses: the entrance frame `E = ⊥` acts as the identity, and `T_U = L (C ⊗ id) R`. `cold_hyperplane_width` assumes a frame of rank 8 and concludes that the residual width is 8, there is one spectator, and the frame is not full. `research/hyperplane-end-lean/PROOF.md` says the rank-8 factorization was checked locally on all 511 hyperplanes of `F_2^9` and that the script was not shipped. The three non-cold pairs already have a Lean proof in `Exact.lean`; they are not recomputed.

For every nonzero linear functional on `F_2^9`, let `U` be its kernel. The verifier builds the canonical cold frame of `U` and an extracted monomial factorization `R`, then Fourier on qubits `0..7`, then `L`. Both circuits have eight `C` gates. Their images on `sum_x B^x |x>`, with `B = 2 * 4^(c+1)`, agree. Numerators of a `c`-gate circuit are bounded by `4^c`, so a difference of two such numerators is strictly inside one base-`B` digit. Equal packed images are equal operators on `C^512`, global phase included. The empty frame's circuit is empty, so it is the identity. Each kernel has rank 8, residual width 8 and one spectator.

The registered run prints `PASS_COLD_HYPERPLANE_FACTOR_CENSUS`, hyperplane count 511, and digest `4fd58c1106311ef12bb46f744bc7629d583b0539081238feedb808e5f40515ed`. The digest is the SHA256 of the 511 basis-and-monomial records. Samples for functionals 1, 256 and 511 are in the receipt. The three Lean entrances `[45]`, `[51]` and `[30]` each have rank 1, so they are outside this census.

Rejected controls, all on the same comparison: an extra global phase, deletion of one `C` gate, swapping `L` and `R` around the Fourier, the identity circuit in place of a hyperplane, and a nonzero translation of the identity.

Selected κ stays `836330098538459/500000000000000000`. This does not discharge unit rows, emitted wrapper recipes, footprints, hosting, or a Lean kernel check of the census.

A separate session comparison, not part of `verify.py`, showed that these canonical-frame circuits and tableaus match `research/direct-delivery504-global/vendor/clifford/clifford_exact.py` on all 511 kernels and the empty frame. The registered proof does not import that module.

## Reproduce

From the repository root, with Python 3.12 and `PYTHONOPTIMIZE` unset:

```sh
python3 -B scripts/research_package.py --package research/cold-hyperplane-factor-census --check-only
python3 -B scripts/research_package.py --package research/cold-hyperplane-factor-census
```

This session used Python 3.12.3. The direct verifier finished in about 20 seconds. `g++` 13.3.0 is installed and `c++` already pointed at `/usr/bin/g++`; `libboost-dev` 1.83.0.1ubuntu2 is installed. `research/e8-bit-p111-tuned/requirements.txt` is installed for the user (numpy 2.5.4, sympy 1.14.0, scipy 1.18.1) and is not used here. Source pins are in [SOURCES.json](SOURCES.json).

Not run: `lake build`, `make frontier1094-verify`, and any artifact-regenerating frontier suite. Discussion writes were not retried. This account previously received a forbidden response on discussion writes to `CrocSwap/integer-mult-bounds`, and that restriction is still treated as in force.

## Open next questions

Does one emitted cold helper, with its actual dirty entrance and cleanup tail, satisfy the unit-row and wrapper-recipe hypotheses that `exact_cold` does not touch? The operator identity is now checked for every abstract hyperplane, but an emitted word can still fail those physical hypotheses. A useful first step is to pin one shipped cold helper whose entrance is empty and whose terminal is a hyperplane, then compare its named recipe with the monomials in this digest. The blocker is that this package contains no emitted cold word, and the physical hyperplane-end replay was not run.

## Credit

The cold statements are DreamingOfClouds' extension in the hyperplane-end package, alongside Jeremy Kothe's non-cold Lean proofs. The frame definition follows the Clifford compiler vendored from icekylinx's direct-delivery work; this package reimplements the finite check and does not import that compiler. The packed digit comparison follows the argument recorded in the hyperplane-end proof note. Nearest other uses of the 511 hyperplanes are the W(E8) flat census in `research/complex-frame-pair-decoders` and the P112 copy optimum in discussion 1691. Both are different questions. The width-4 cold packages check 14 pairs and leave the rank-8 lemma to this specialization.

Prepared by an AI-assisted research session. Substantial AI assistance drafted the verifier and these notes. No independent human review is claimed. Apache-2.0.
