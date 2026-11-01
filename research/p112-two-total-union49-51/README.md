# P112 fixed-reader two-total screen through source union 51

**Scoped negative result. No new kappa and no new supplier.**

For the pinned P112 coordinate matrix, every exact two-total correction that
keeps the eight coordinate readers and has source union at most 51 has
two-column retained pairing-rank loss at most **5**. Loss 5 is attained by a
union-48 witness whose separate-total bill is **74**. In the full-rank
on-column case the added-term price relaxation is at least 6, so the
copy-rank sum is at least **65**. There is no closed reader support of size
49 or 51; size 50 occurs and does not raise the loss bound.

This is the band left open after the union-48 screen. It does not improve
the binding complex moment. Frame changes, restoration, hosting and recursive
children are granted cost zero in this screen; a positive charge would not
lower the copy-rank sum proved here.

## Scope

Original card: `complex-masked-decoder`, scope **refined**. The card asks
whether one masked or overcomplete decoder can improve the complete moment.
The eight-term all-pairs theorem excludes nine or more terms. This note takes
that overcomplete side and narrows it to ten terms whose first eight readers
stay the P112 coordinate columns, with source union in {49, 50, 51}.

The selector was run once. Track `complex-mechanisms`, task
`complex-masked-decoder`, scope key `7acfe4d9cac04f7ba4cb`, nonce
`1f91c49e743429932b6e87b7267a09b9`, catalogue revision 2, base
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. The orientation command

```sh
python3 -B research/complex-decoder-field-extension-seed44/verify.py
```

ended with `PASS_COMPLEX_DECODER_FIELD_EXTENSION_S44`.

## What was checked

[verify.py](verify.py) rebuilds the eight reader codes from the pinned
geometry and does not import a predecessor checker.

| Cap | Closed-support geometric count | N-satisfying retained loss | Full-rank on-column floor |
|---|---:|---:|---:|
| 49 | 8 | 5 | 65 |
| 50 | 8 | 5 | 65 |
| 51 | 8 | 5 | 65 |

- Size-36 leads gain no companion supports when the outside budget grows from
  12 ports to 15.
- Every cut configuration with a conceivable loss of 6 or more fails the
  rank-at-most-2 minor test.
- Single-codeword tuples with union at most 51 include 196 six-reader tuples,
  56 seven-reader tuples and 7 eight-reader tuples. None of those satisfies
  the minor test. The largest passing tuple has five readers (448 tuples).
- The union-48 witness is checked on all 12,544 port pairs. Retained losses
  are `(4,1,0,0,0,0,0,0)` and the added ranks are `(8,7)`.

## Reproduce

Python 3.12, standard library only, from the repository root. Assertions are
not used; the checks are explicit exceptions and stay active under `-O`.

```sh
python3 -I -B research/p112-two-total-union49-51/verify.py
```

Expected final line:

```text
PASS_P112_TWO_TOTAL_UNION49_51 caps=49,50,51 two_column_loss=5 geometric_closed=8 full_rank_floor=65 witness_union=48 witness_bill=74 no_closed_sizes=49,51 no_new_kappa
```

Registered replay:

```sh
python3 scripts/research_package.py --package research/p112-two-total-union49-51
```

One local run of the direct verifier took 138 seconds on CPython 3.12.3,
Linux x86-64, one core. The registered timeout is 400 seconds.

## Environment

- Base commit `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`.
- Input `research/p112-single-lift/reference-geometry.json`, SHA-256
  `4f44af368e046002553d632ee90c6470990827cea3fae41f0f54018522d7a080`.
- Python 3.12.3. `PYTHONOPTIMIZE` was unset.
- `c++` resolved to `/usr/bin/g++`, g++ 13.3.0. `libboost-dev` 1.83.0.1ubuntu2
  was already installed. No native code is compiled by this package.
- `python3 -m pip install --user -r research/e8-bit-p111-tuned/requirements.txt`
  reported numpy 2.5.4, sympy 1.14.0 and scipy 1.18.1 already present. This
  package does not import them.
- Selected conditional kappa remains
  `836330098538459/500000000000000000`. The selected cold replay
  `make frontier1094-verify` was not run.

## Open next questions

1. **Source union 52.** The copy screen is still open there, and 52 is the
   next integer at which a size-40 lead has a 12-port outside budget. The
   twelve-port margin then no longer forces every companion to be a cut, so
   the cut-only branch in [PROOF.md](PROOF.md) stops applying to those leads.
   First step: enumerate closed supports of size 52 and test condition N on
   every lead whose outside budget is still below 12. Blocker: the size-40
   leads need the widened companion enumeration, which this package only
   settled for size-36 leads.

2. **Is the full-rank floor 65 attained?** The relaxation allows one added
   source to carry a single active label. The explicit loss-5 witness costs
   74, so a matching lower-price witness, or a proof that every loss-5 shape
   costs at least 66, is still open. First step: classify the column space of
   each N-satisfying loss-5 shape at union 48 and apply the cut sign balance
   to its support sizes. Blocker: shapes other than one lead plus a single
   cut have free entries, and this package does not solve them.

## Limits and obligations not checked

- Rank-one corrections, sources outside the column space, changed readers and
  masked exactness are not given a new proof here. Earlier notes reduce some
  of those cases to the full-rank on-column screen; those reductions were not
  replayed.
- Helper access, frame changes, restoration, hosting, precision, tape, the
  all-size compiler obligations and bit hypotheses H1–H5 are inherited and
  were not rechecked. They were priced at zero before the copy screen.
- The finite enumeration plus [PROOF.md](PROOF.md) is not a proof-assistant
  formalization.
- Discussion writes were not retried. Earlier sessions on this account
  received a forbidden response from the discussion API, and this session did
  not call it again.

## Credit

The geometry and the single-lift theorem are Mihir Srivastava's PR845, using
DreamingOfClouds' PR717 model. The two-total support screen through 43 is
Josie Elliston's PR1787. Philipp (mightyOil) sharpened the joint-loss screen
through 43 and supplied the complementary reductions in PR1197. Sricharan
Vagvala (@theon199) extended the exclusion through 47 in PR2382. The union-48
band, including the loss-5 witness shape used here, is @thakrarsagar's
PR2581. This package recomputes bands 49–51 independently and does not import
those checkers.

The selected frontier is unchanged. Upstream trees and frozen inputs are
unchanged.

Prepared with substantial AI assistance in the mathematics, implementation,
verification and writing. No coding-agent product is named here. No
independent human review is claimed. Apache-2.0.
