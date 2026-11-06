# Gauge44 helper-endpoint moment screen

**Scoped exact screen. No new κ and no supplier admission.**

On the pinned PR1094 gauge44 histogram, two explicit endpoint edits are priced
with the selected complex moment engine, surcharge off. The complex side binds
the selected construction. These edits are the smallest histogram changes, in
the two families below, that make that moment drop strictly below one at the
selected bit endpoint. They are not a scalar word, a width alphabet, or a
change to the selected frontier.

## Scope and evidence

Original card: `complex-new-helper-inventory`, scope key `5868e5281a1e63d41a22`,
chooser seed `ef87d06bc5be1f65ff317cc1c45c907b`, priority revision 2.
Scope status: **refined**. The card asks for a new realizable cost interface.
This package keeps the pinned call count, idle remainder, width multiset and
observed mass identity, and certifies two endpoint edits before any circuit
search. It does not mix providers from the frozen heterogeneous catalogue.

Base commit `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. The selected conditional
κ remains `836330098538459/500000000000000000`.

The checked object is one gauge44 call, repeated across all 144 calls, plus the
recorded idle remainder:

| Quantity | Value |
| --- | --- |
| Width `m`, live roles `W` | 73, 14336 |
| Local paid profile | `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` |
| Idle remainder | `{1:2276, 3:377, 7:7, 48:4866}` |
| Global paid profile | `{1:349604, 2:60192, 3:62585, 4:20448, 5:11808, 7:7, 8:1152, 48:4866}` |
| Width inventory | `{4:56, 5:32, 7:30, 8:122, 9:240}`, sum `M = 3730` |
| Local rank mass | `5586 = M + 1856` |
| Global deficit | `73·14336 − 1041408 = 5120` |

The moment is `Σ n_r (r/m)^(1-a) / W`, bounded by the selected assembly engine
`research/frame-domain-ceiling/engines/moment.py`
(SHA256 `81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482`),
with the bad-envelope surcharge off. A histogram is strictly below one when the
engine's upper bound is below one, and strictly above one when its lower bound
is above one. The comparison exponent is the accepting bit endpoint in
`ASSEMBLY.json`,

`1733427039589844234749/1000000000000000000000000`.

**Pure deletion.** Children are removed and none are added. On the local support
`{1,2,3,4,5,8}` the only deletions of rank mass 1 or 2 are one rank-1 child,
two rank-1 children, and one rank-2 child. Applied uniformly to all 144 calls,
at the bit endpoint:

- mass 1 stays strictly above 1;
- both mass-2 deletions fall strictly below 1;
- two rank-1 deletions are strictly cheaper than one rank-2 deletion.

The same engine separates per-unit-mass costs on `{1,2,3,4,5,7,8,48}`: the
outward intervals decrease strictly with rank. That orders the deletions. The
mass-1 and mass-2 lists are exhaustive enumerations, not samples.

**Rank-8 coalescence.** Replace eight rank-1 children by one additional rank-8
child, `k` times in every call. Local rank mass is unchanged, so this edit does
not by itself reduce `M`. At the bit endpoint, `k = 42` stays strictly above 1
and `k = 43` falls strictly below 1. Rank 1 remains positive (`2412 − 8·43 = 2068`).

The published complex bracket is a control on the same engine: the accepting
endpoint stays below one and the rejecting endpoint stays above one. A child of
rank `m` is rejected. The baseline histogram itself stays above one at the bit
endpoint, which is the gap these edits close.

## What was not proved

This is not a physically realizable contract. No canonical-word search, frame
schedule, dirty restoration, owner assignment, prefix, finite invoice, outer
assembly, or `make frontier1094-verify` cold replay was run. Meeting the bit
endpoint in this relaxation does not reprice κ. Other constant-mass edits,
including a move onto rank 48 or the ideal cell `{8:698, 2:1}`, are outside the
certificate. The identity `local mass = M + 1856` is checked for this pinned
profile. The heterogeneous-owner theorem proves that identity for a frozen
catalogue and a different outer word; it is not re-proved here for a new width.

A targeted overlap search on 2026-11-06T12:17:07Z covered 733 open PR bodies,
including drafts, and 6835 discussion records, with complete pagination.
The terms `pure deletion`, `rank-8 coalescence`, `gauge44 endpoint screen`, and
`eight rank-1 children` matched one unrelated local note,
`research/punctured112-global/README.md`, whose profile is different. No match
is not a novelty certificate. Upstream PR 3896 screens a rank-2 block rewrite
with a different child delta. The frozen catalogue bound in
`research/heterogeneous-owner-assembly/` prices mixtures of recorded providers;
this package does not add one of those mixtures.

## Reproduce

Python 3.12, standard library only, from the repository root. Leave
`PYTHONOPTIMIZE` unset. The checker refuses optimized mode because the moment
engine uses assertions.

```sh
python3 -B research/gauge44-helper-endpoint-screen/verify.py
python3 scripts/research_package.py --package research/gauge44-helper-endpoint-screen --check-only
python3 scripts/research_package.py --package research/gauge44-helper-endpoint-screen
```

Expected final line:

```text
PASS_GAUGE44_HELPER_ENDPOINT_SCREEN deletion=1:above,2:below coalescence=42:above,43:below ordering=strict controls=5
```

The registered replay also prints `PASS_REGISTERED_RESEARCH_PACKAGE`.
Source pins are in [SOURCES.json](SOURCES.json). The catalogue and selected
record are provenance. The three live inputs must match their pins.

Environment used for the author run: Python 3.12.3; `PYTHONOPTIMIZE` unset;
`c++` alternative `/usr/bin/g++` (g++ 13.3.0); `libboost-dev` installed. The
e8 requirements file was already satisfied and is not imported here. No native
replay was required.

## Open next questions

1. Does the pinned gauge44 word contain either a pure deletion of two rank
   units in every call, or 43 disjoint replacements of eight rank-1 children by
   one rank-8 child, with an empty restoration and frame bill?
   Either edit is the first histogram in this screen that meets the bit
   endpoint, and every smaller copy of the same edit is excluded. The first
   step is to count disjoint candidate events in the canonical local word.
   The histogram does not identify which children can move, and extraction,
   routing, and dirty restoration are not priced here.

2. If a width outside `{4,5,7,8,9}` is added, does paid mass remain
   `M + 1856`, or does the new helper add a child that consumes the two-unit
   surplus?
   The mass-2 deletion meets the bit endpoint only when those two units are not
   replaced by a new positive-rank child. The first step is one explicit
   width-6 endpoint law and its child delta, rerun through this screen.
   No such endpoint law is proved in this package.

## Credit

The histogram, idle remainder, and endpoints come from the selected PR1094
assembly of Rohan Arun's rare-pattern exchanges on Jeremy Kothe's gauge44/T16
packing, as recorded by the selected review. The moment engine is the engine
named by that assembly. The mass split `1856` is the contract stated for the
frozen catalogue in `research/heterogeneous-owner-assembly/PROOF.md`; this
package only checks that the pinned gauge44 profile satisfies the same numeric
split. Apache-2.0.

Prepared with substantial AI assistance. This is not an independent human
review or a formal verification of integer multiplication.

A finding comment on the handoff discussion was rejected with
`Resource not accessible by integration`. That write was not retried.
