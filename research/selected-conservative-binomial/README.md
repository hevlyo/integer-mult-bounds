# Selected conservative complex moment, by a positive binomial enclosure

**Independent verification. No new κ. The selected record is unchanged.**

The selected certificate is `836330098538459/500000000000000000`
(`0.001672660197076918`). Its complex side binds. This package does not move
that value. It checks the conservative pricing of the same frozen profile.

## Task card

- Task: `independent-moment` (scope key `c191650c0fa8d2fa514e`), track
  `independent-verification`.
- Selector nonce: `9c6b16e22a9fc1a2ac785130569f7d6a`. Kept; not redrawn.
- Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`.
- Priority revision 2. Selected-record SHA-256
  `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Scope status: **refined**. The native endpoint is already certified by the
  assembly's Mercator and base-two rows and by the code-disjoint atanh sweep.
  The claim checked here is the conservative bracket, with the inherited
  bad-residue surcharge turned on.

Orientation command, before the enclosure:

```sh
python3 -B scripts/research_baseline.py
```

It returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` with complex saving
`67018507072324140917/40000000000000000000000` and binding side `complex`.
That command is source-bound orientation, not this certificate.

## Result

The frozen plan gives modulus `M = 73`, live stock `14336`, `T = 16`, `L = 9`
and deficit `5120`. The profile shared by `PLAN.json`, `PROFILE.json` and the
selected assembly is

```text
{1: 349604, 2: 60192, 3: 62585, 4: 20448, 5: 11808, 7: 7, 8: 1152, 48: 4866}
```

Rank mass is `1041408`. The accounting identity
`73 * 14336 - 1041408 = 14336 - 64 * 144 = 5120` holds, and `73^2 > 2 * 48^2`.

For each child rank `r` the enclosure is the positive series

```text
(73/r)^a = (1 - x)^(-a),  x = 1 - r/73,
```

with outward rounding onto multiples of `2^{-240}` and a geometric tail of at
most `2^{-170}` on each power. No logarithm and no exponential are formed.
The surcharge term is the inherited rank-one charge

```text
32 * 73 * (total calls) / (10^16 * 14336) * 73^a.
```

That is the same charge the assembly adds when `bad` is true.

At the recorded conservative endpoint

`1675462673946628390003/1000000000000000000000000`

the binomial moment is strictly below one. At the next `10^{-24}` grid point,

`418865668486657097501/250000000000000000000000`,

it is strictly above one. Both residual intervals meet the recorded Mercator
interval and the recorded base-two interval. Displayed widths are about
`10^{-51}`; the signs used for acceptance are exact.

Restoring that surcharge at the native endpoint
`67018507072324140917/40000000000000000000000` makes the moment strictly
greater than one (displayed gap about `8.4 * 10^{-12}`). This is the assembly
model control `native_complex_endpoint_rejected_with_old_surcharge`, checked
without importing `moment.py`.

The seven-step outer reduction from this conservative endpoint and the cited
PR589 bit endpoint reproduces

`104541262139063/62500000000000000`.

That is the assembly's `conservative_kappa`. The complex side still binds.
The selected native κ is left as recorded.

The same series also agrees with the native, surcharge-off bracket already
stored in the assembly. That comparison is a control, not a second claim.

## Failure controls

- `a = 0` returns the exact rank-mass ratio `1041408 / (73 * 14336)`.
- `a = 1` encloses the exact integer `73/r` for every rank in the profile.
- One extra rank-one child makes the conservative moment strictly greater than one.
- A one-term tail is too wide to prove acceptance, so the check fails closed.
- Treating the successor grid point as an accepting endpoint fails.
- `PYTHONOPTIMIZE=1` is refused before any enclosure is built.

## Reproduce

Python 3.12, standard library only. Assertions must be enabled
(`PYTHONOPTIMIZE` unset). From the repository root:

```sh
python3 -B research/selected-conservative-binomial/verify.py
python3 scripts/research_package.py --package research/selected-conservative-binomial
```

Expected marker: `PASS_SELECTED_CONSERVATIVE_BINOMIAL`.

This run used CPython 3.12.3. `g++` 13 and `libboost-dev` were installed and
`c++` pointed at `/usr/bin/g++`. The pinned research requirements
(numpy 2.5.4, sympy 1.14.0, scipy 1.18.1) were already present. This package
does not import them.

## What was not run

`make frontier1094-verify` was not run. The owner map, scalar word, PR589 bit
circuit, bit-surcharge omission at the next bit endpoint, all-size/compiler
realization, precision/tape, analytic transfer and bit H1–H5 were not
rechecked. A passing arithmetic bracket does not admit the profile.

Overlap was refreshed on 2026-11-07 against 796 open PR bodies and 6904
discussion records, complete pagination, for the phrases `selected conservative
binomial`, `1675462673946628390003`, `native endpoint old surcharge` and
`binomial surcharge 14336`. The helper reported no matches. That is not a
novelty certificate. The predecessors below are the nearby work.

Discussion writes to the upstream discussion board are forbidden for this
account. The limitation is recorded here and was not retried.

## Open next questions

1. **Does omitting the PR589 bit surcharge fail to reject the next bit endpoint?**
   The selected model control says it does. Only the complex side is enclosed
   here, so the surcharge model is still half unchecked. First step: run this
   series on the cited PR589 profile at the recorded bit endpoint and one
   `10^{-24}` step later, with and without the surcharge. Blocker: that
   histogram and its live stock are not fields of the selected assembly and
   were not re-derived.

2. **Does the owner map actually produce this profile?** The three pinned JSON
   files agree with each other. They do not, by themselves, rebuild the word.
   First step: replay the owner half of
   `research/community-batch1099-audit/check_frontier1094.py` in a fresh work
   directory and compare the profile. Blocker: that replay needs the pinned
   T16 word, template and phases, and it was not run here.

## Credit

The profile and the conditional frontier are Rohan Arun's PR1094 rare-pattern
exchanges, on the T16 owner lineage. The assembly and the batch-1099 review
are the selected certificate. Mercator and base-two residuals are the retained
engines' recorded output. Sagar Thakrar's
`research/pending-claims-independent-pricing` certifies native endpoints,
including this profile through `check_frontier1094.py`, by a prime-chain atanh
expansion and does not enable the surcharge for that check. The positive
binomial series follows the method in David Breslauer's `t21-binomial-audit`
and `t37-binomial-endpoint-audit-seed78` by steph4n-gh, which certified the older
T37 profile at live stock 33152, not this 14336-stock bracket.

Prepared as an AI-assisted research session. Substantial AI assistance was
used. New material is Apache-2.0.
