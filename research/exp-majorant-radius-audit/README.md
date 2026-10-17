# Exponential majorant radius for the degree-12 moment enclosure

**Exact interface audit; no new κ.** The selected conditional saving stays
`836330098538459/500000000000000000`. Nothing under `upstream/`, the selected
record, or `interval_moment.py` is edited.

The pinned moment engine in
[interval_moment.py](../coordinated-frames-and-entrance-banks/arithmetic/interval_moment.py)
rejects `exp_interval` unless the upper argument is strictly below `1/4`.
That guard is sufficient for the formula it evaluates, and it is stricter
than the formula's own radius. The same algebraic expression is a strict
exponential upper bound for every rational argument in `(0, 14)` and is not
an upper bound at `15`.

## Task card

```text
Task ID / proposed scope key: uniform-transfer-audit / ce7411fb7cf6f3460bfc
Base commit: ef5f39403610d231a0c27e8a6b4f08c10209bcd6
Selector nonce: 084da2492a0741f621cca81de43d935d
Track: adversarial-audit. The other suggested card, supplier-boundary-audit,
was not used.
Predecessor: research/coordinated-frames-and-entrance-banks/arithmetic/interval_moment.py
  blob c135d98d866b076959d1890f8622c49bd76cd1d7
  sha256 9d3d1d28bfb3375958995205179b171fb65c70a3792cf9f7a21ef5ee54f5460b
Concrete object: the degree-12 geometric tail inside exp_interval, on the
  rational arguments {0, 1/5, 1/4, 13, 1399/100, 14, 15}.
Scope status: refined. The card allows one precision implication. This
  session keeps that premise and narrows it to this enclosure's guard versus
  its majorant radius. It does not replace the obligation with an unrelated
  finite replay.
Existing restriction being audited: "argument below 1/4" as the condition
  under which this tail expression upper-bounds exp. The assembly-domain note
  already warns that enlarging the search needs a new enclosure argument;
  it does not give the radius or a false-accept bill.
Method: exact rational Taylor arithmetic, the geometric-series comparison,
  and direct calls to the pinned function. No floating point.
Nearest overlap and the added value: docs/research/assembly-domain-audit.md
  (the 1/32 assembly cap and a pointer at this 1/4 guard) and the a < D/E
  notes on discussion 1166. Those do not prove this tail's radius or exhibit
  the one-term bills below. Binomial geometric tails in the T21/T37 audits
  are a different series.
Optimistic budget: not applicable. This is an audit of an enclosure, not a
  supplier improvement. The required observable is a separated false accept.
Success evidence: PASS_EXP_MAJORANT_RADIUS_AUDIT. Falsification would be an
  argument in (0, 14) where the tail falls to the Taylor polynomial or below,
  or an argument >= 15 where the same expression still dominates the next
  Taylor term.
Stop rule: these rational witnesses and the inductive coefficient step; no
  selected-histogram reprice and no guard edit in the production engine.
```

The orientation command `python3 -B scripts/research_baseline.py` returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` on this base. The complex primitive
binds. That command is a source-bound control, not this audit.

## Proposition

Let `T_12` be the degree-12 Taylor polynomial of the exponential series at
zero, and for `x != 14` write

```text
U(x) = T_12(x) + x^13 / (13! (1 - x/14)).
```

Let `P_j = (14)(15)...(13+j)` for `j >= 1`, with `P_0 = 1`. Then
`P_j >= 14^j`, with equality exactly at `j = 0, 1`. The inductive step is
the identity `(14 + j) - 14 = j`: for every integer `j >= 1` the next factor
is an integer at least `15`. Consequently, for `0 <= x < 14`,

```text
exp(x) = T_12(x) + (x^13 / 13!) * sum_{j>=0} x^j / P_j
       <= T_12(x) + (x^13 / 13!) * sum_{j>=0} (x/14)^j
       = U(x).
```

For `x > 0` the `j = 2` coefficient is strict, so `exp(x) < U(x)`. Every
term after degree 12 is positive, so `exp(x) > T_12(x) + x^13/13!`. At
`x = 0` all three quantities equal `1`. At `x = 14` the displayed denominator
is zero, so `U` is not a real upper bound. For every rational `x > 14` the
denominator is negative, hence `U(x) < T_12(x) < exp(x)`.

The pinned implementation returns an outward `10^-45` rounding of
`[T_12(lo), U(hi)]` when `0 <= lo <= hi < 1/4`, and raises
`exp enclosure domain` otherwise. Rounding preserves the inequality inside
that smaller interval. It is not what creates the radius `14`.

## Exact adversarial bills

Normalize a one-term bill by `w(x) = 1 / (T_12(x) + x^13/13!)`. For `x > 0`
the true value `w(x) exp(x)` is strictly greater than one.

| Argument | What is true | Tail-free `w T_12` | Formula `w U` | Pinned `exp_interval` |
|---|---|---|---|---|
| `1/5` (inside the coded guard) | bill `> 1` | `< 1`, false accept | `> 1`, rejects | returns an interval whose weighted image overlaps `1`, so it does not accept |
| `1/4`, `13`, `1399/100` | `U` still lies strictly above `T_12 + x^13/13!` | not used | majorant still valid | rejects the call |
| `15` | bill `> 1` and `U < T_12` | `< 1` | `< 0`, false accept | rejects the call |

The inside overlap is expected. The excess of `exp(1/5)` over the degree-13
partial sum is far smaller than the gap between that partial sum and the
outward lower grid of `T_12`, so this particular weight is a false-accept
witness for the tail-free reading, not a separation certificate for the
guarded engine. The outside witness needs no grid: `U(15)` is already below
`T_12(15)`.

## What this changes downstream

A caller that treats `T_12` as an upper bound, or that evaluates this `U`
at an argument of `14` or more, can report a one-term bill as strictly below
one when the series lower bound is already one. Widening the coded guard from
`1/4` to any fixed rational cap strictly below `14` does not create that
false upper bound. It also does not by itself authorize a larger moment
search: `saving_grid` still stops at `denominator//32`, and the logarithm
reduction is a separate enclosure.

This does not show a defect in the guarded function, a failing selected
moment, or a larger multiplication exponent. The selected frontier replay
`make frontier1094-verify` was not run.

## Reproduce

From the repository root, with Python 3.12 and `PYTHONOPTIMIZE` unset.
Both commands are also the registered package replay. The second forces
`python -O`; the checker does not use `assert`.

```sh
python3 -B research/exp-majorant-radius-audit/verify.py
python3 -O -B research/exp-majorant-radius-audit/verify.py
python3 -B scripts/research_package.py --package research/exp-majorant-radius-audit --check-only
python3.12 -B scripts/research_package.py --package research/exp-majorant-radius-audit
```

Expected final line: `PASS_EXP_MAJORANT_RADIUS_AUDIT`.

Environment used for the local run: CPython 3.12.3, `PYTHONOPTIMIZE` unset,
`g++` 13.3.0 at `/usr/bin/g++` with the `c++` alternative already pointing
there, and `libboost-dev` 1.83.0.1ubuntu2. No C++ or Boost code was executed.
`research/e8-bit-p111-tuned/requirements.txt` was already satisfied for
numpy, sympy and scipy; this package does not import them.

## Checks not run

- `make frontier1094-verify` and every other cold supplier replay.
- A reprice of the selected complex or bit histogram under a wider guard.
- The logarithm enclosure, the `10^-45` grid's separation power, and the
  assembly constraints outside this exponential call.
- Hosted CI, an independent human review, and a proof-assistant check.
- Discussion posting. Writes to the upstream discussion board are forbidden
  for this account (`FORBIDDEN` / resource not accessible by integration,
  previously observed 2026-10-16). That limitation is recorded here and was
  not retried.

## Open next questions

1. **Can a fixed cap `c` with `1/4 <= c < 14` be substituted for the coded
   guard and still separate the selected complex moment at its recorded
   endpoint?** It matters because the mathematical radius is larger than
   `1/4`, but only a joint replay with the logarithm reduction, surcharge
   and outward grid can say whether any selected child actually needs the
   extra room. First step: evaluate `a * log(m/r)` for the selected complex
   histogram at the recorded endpoint and compare the upper endpoint with
   `1/4` and with `c = 1`. Blocker: this package does not load that histogram
   or rerun the logarithm enclosure, and a wider guard is not a new supplier.

2. **For the inside bill at `x = 1/5`, how many extra Taylor terms make an
   outward enclosure prove `w exp(x) > 1` rather than only overlap one?**
   It matters because the guarded engine correctly refuses to accept this
   bill and still does not certify the rejection. First step: increase the
   partial sum until its weight-one threshold sits strictly below the outward
   lower bound of `T_12(1/5)`. Blocker: that is a different enclosure, and
   it should stay independent of the production moment engine.

## Credit

The enclosure implementation and its `1/4` domain check are the existing
`interval_moment.py` engine, prepared with AI assistance as stated in that
file. The assembly-domain note by Douglas Colkitt records why the separate
`b < 1/32` cap is not a multiplication barrier and points at this guard.
This package adds the radius proof, the exact false-accept bills, and the
distinction between widening the guard up to but not including `14` and
deleting it.

Prepared by an AI-assisted research session. Substantial AI assistance
drafted the statement, the rational checks and these notes. No agent product
is named. Apache-2.0. This is not an independent human review and not a
formal verification of integer multiplication.

## Coordination

Overlap was searched with `python3 scripts/find_overlap.py` for the assigned
card and, separately, for the enclosure phrases `exp enclosure domain`,
`degree-12 exponential`, `geometric tail` and `interval_moment guard`. The
phrase search was refreshed immediately before submission. Coverage was
complete: 280 open PRs including drafts at 2026-10-17T12:12:04Z, and 1924
discussion records at 2026-10-17T12:13:41Z. The only hits were this package
and the binomial tails in `research/t21-binomial-audit` and
`research/t37-binomial-endpoint-audit-seed78`. Those tails bound a different
series. No matches is not a novelty certificate. Upstream discussion writes
remain forbidden for this account and were not retried.
