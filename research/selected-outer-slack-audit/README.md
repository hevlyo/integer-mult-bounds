# Selected outer slacks versus the 47-positive receipt check

**Adversarial audit of one selected obligation. No new κ.** The selected
frontier #1094 certificate's 47 native outer slacks, its 47 conservative outer
slacks, and both published kappa floors equal an independent evaluation of the
retained balanced-assembly formulas. The receipt check used by
`scripts/verify_frontier1094.py` and `research/gauge44-slots-t16/verify_t16.py`
does not establish those identities: any 47 positive rationals satisfy it.

This is not a bug in the published certificate, and it is not the historical
PR626 timing-only bridge omission. A full honest replay still computes the
slacks inside the supplier assembly engine. The gap is the receipt predicate
that only counts positive values.

## Scope and evidence

Assignment `supplier-boundary-audit`, seed `0bc262c33a32b030f02e00e663b62ec1`,
base `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. The obligation is the selected
assembly's named outer map, a refinement of the card's "one current supplier
obligation."

| Object | Result |
| --- | --- |
| Native outer map | All 47 names and exact values match `ASSEMBLY.json` |
| Native kappa | `836330098538459/500000000000000000` |
| Conservative outer map and kappa | Same identities at the conservative complex endpoint |
| `next_grid`, `zero_eta`, `zero_beta`, `unit_beta` | Each makes at least one named slack nonpositive |
| 47 dummy positive keys | Passes the receipt predicate and fails the name binding |
| One genuine slack replaced by `1` | Passes the receipt predicate and fails the identity |
| One genuine slack set to `0` | Fails the receipt predicate |

The bootstrap uses the certificate bit lower bound and complex lower bound,
`eta = beta = 10^-24`, seven iterations from `384599/10^10`, and the `10^-18`
floor `(1-eta)q/(1+q)`. The engine argument historically named `bit_saving` is
that seventh iterate, not the PR589 bit lower bound. `bit_positive` equals the
iterate. The row gap is `10^6 - 51*20161/25` and the literal scalar guard is `1`.

The checker does not import `engines/outer.py`. It reads the selected
certificate and requires the two receipt predicates to remain the quoted
length-and-positivity lines.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3 -B research/selected-outer-slack-audit/verify.py
python3 scripts/research_package.py --package research/selected-outer-slack-audit
```

Expected status: `PASS_SELECTED_OUTER_SLACK_AUDIT`.

## Limitations

Not checked: the moment engines, owner emission, controller, invoice, native
circuit, or a cold `make frontier1094-verify`. All-size/compiler,
common-label/mutable-source realization, whole-call hosting, precision/tape,
exact recovery, analytic transfer and bit H1–H5 obligations remain inherited.
A dishonest generator could still write a positive dummy map if the replay
stopped trusting the assembly engine and trusted only the receipt predicate.
This package does not replace that engine.

Discussion posting was unavailable to this session, so the claim is recorded
here and in the pull request rather than on the discussion board.

## Credit

Zhihao Chen's PR23 outer constraints; icekylinx's structured-bulk assembly;
the RaD project's balanced prefix; the gauge44 T16 witness and Rohan Arun's
#1094 certificate. Prepared as an AI-assisted audit. Apache-2.0. No human peer
review is claimed.

## Open next questions

**Does any selected replay path accept `ASSEMBLY.json` without executing the assembly engine?**
That matters because the receipt predicate alone accepts a dummy map. The first
step is to trace every writer and reader of `outer` in `make frontier1094-verify`
and see whether a substituted map can pass after the engine call is skipped.
Blocked by the cost of a full cold replay and by not modifying the selected verifier in this package.
