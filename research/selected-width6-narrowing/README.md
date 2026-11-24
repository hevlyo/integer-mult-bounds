# Width-6 narrowing of the selected gauge44 inventory

**Negative planning result. No new kappa.**

Replacing all 122 width-8 helpers on the selected gauge44 word by width-6
helpers, and giving the freed rank mass its most favorable legal shape, still
misses the primitive budget `1/99`. The selected frontier is unchanged.

## Scope and evidence

Task `complex-new-helper-inventory`, scope key `5868e5281a1e63d41a22`, chooser
seed `d544eefab4c9d29dff874e40d84221a1`, priority revision 2. Base
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Scope status: **refined** to one
helper width with explicit counts. This is the card's optimistic-histogram
test. It is not a mixture of the 25 frozen catalogue interfaces, and it does
not claim a physically realizable contract.

The selected T16 profile in
`research/complex-t16-rare-pattern-exchanges/data/SPEC.json` has 144 gauge44
calls. The width plan in `research/gauge44-slots/data/PLAN.json` gives every
call the inventory `{4:56, 5:32, 7:30, 8:122, 9:240}` (mass 3730, 480 helpers)
and local paid profile `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`. The paid
rank sum exceeds the helper mass by 1856. The frozen catalogue inventories use
only widths `{4, 5, 7, 8, 9}`; width 6 is absent there and on this word.
T16's published note keeps these role widths.

The edit replaces each width-8 helper by one width-6 helper. Helper mass falls
by 244 per call. Keeping excess 1856 deletes 244 rank-1 children per call and
leaves every larger paid child in place. Idle rank mass rises by `144 * 244`.
Under residual rank at most 48, the cheapest idle shape is 5670 children of
rank 48. That histogram is integral because the freed mass is divisible by 48.

For `0 < a < 1` and `r > 1`, one rank-`r` child is strictly cheaper than `r`
rank-1 children, since `(r/73)^(1-a) < r (1/73)^(1-a)`. Deleting rank-1
children is therefore the favorable way to shed a fixed rank mass, and
rank-48 pieces are the favorable residuals at this cap. The resulting root is
an upper bound for this edit only while those hypotheses hold. A bin larger
than 48, a different paid-profile change, or an added restoration charge is a
different contract.

The exact native roots, from the pinned Mercator moment engine with assertions
enabled, are

| Histogram | Root |
| --- | --- |
| Selected T16 profile | `1675462676808103522925/10^24` |
| Same mass, idle concentrated at rank 48 | `1682094870064815352349/10^24` |
| Width-6 narrowing, optimistic histogram | `1760855940405956673857/10^24` |

The selected numerator is the published complex endpoint
`67018507072324140917/40000000000000000000000`. The width-6 root is about
5.097% larger than that endpoint and about 17.43% of `1/99`. It is strictly
below `1/99`, so the ideal balanced cap `a/(1+a)` is strictly below `1/100`:

`1760855940405956673857/1001760855940405956673857 < 1/100`.

A same-mass introduction of width 6, trading one width-8 and one width-4 for
two width-6 helpers, does not change the concentrated histogram. Repacking
alone, with this mass and paid profile, cannot pass the width-6 root.

No supplier, owner map, scalar word, or selected record is changed. Kappa
remains `836330098538459/500000000000000000`.

## Reproduce

Python 3.12, standard library only, from the repository root. Leave
`PYTHONOPTIMIZE` unset so the moment engine's assertions stay enabled.

```sh
python3 -B research/selected-width6-narrowing/verify.py
python3 scripts/research_package.py --package research/selected-width6-narrowing
```

Expected final marker: `PASS_SELECTED_WIDTH6_NARROWING`.

The direct check recomputes the three roots, compares them with the published
endpoint and with `1/99`, and runs four failure controls: an extra rank-1
child is inadmissible at the width-6 root, deleting one rank-48 child moves
the root, a constant-mass width-6 swap does not move the optimistic histogram,
and narrowing without deleting paid rank breaks excess 1856. Catalogue
interfaces are checked to exclude width 6.

This session's environment was Python 3.12.3, `g++` 13.2.0 with `/usr/bin/c++`
pointing at `/usr/bin/g++`, and `libboost-dev` 1.83.0. Those compilers are not
used by this check. `research/e8-bit-p111-tuned/requirements.txt` was installed
with `python3 -m pip install --user`; this package does not import those
libraries.

## Not run

`make frontier1094-verify` was not run. The seven-step outer assembly, the bit
bad-residue surcharge, owner admission, and a width-6 gate were not run. The
capacity multiset `{8:672, 16:448, 32:448, 48:448}` per replica is the pinned
catalogue inventory; this check uses its total, which matches selected idle
mass plus helper mass, and the selected profile's maximum rank of 48. It does
not re-read `OWNERS.json.gz`.

One discussion comment on
[handoffs](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166)
returned `FORBIDDEN` (`Resource not accessible by integration`). No post was
sent, and the write was not retried.

## Open next questions

1. Can the scalar word narrow those 122 width-8 helpers to width 6 while
   deleting exactly 244 rank-1 children and no other paid rank? That is the
   gap between this upper bound and a realizable complex-root increase of
   about five percent. The first step is to locate one width-8 helper's gates
   in the k8 slots word and see whether two rank-1 children belong to it.
   The blocker is that the admitted width alphabet has no width-6 operation,
   and this package does not build one.

2. Does the selected T16 owner geometry contain a bin larger than 48? A larger
   bin would make residual concentration more favorable and could retire this
   upper bound. The first step is to read the pattern capacities from the T16
   owner certificate. The blocker is that this check does not parse
   `OWNERS.json.gz`.

## Credit

The selected profile and widths come from the T16 rare-pattern exchange on the
gauge44 slots word, and from the earlier k8 leaver and slot lineage recorded
in those packages. The moment engine is the pinned multicold engine used by
the gauge44 independent price check. The capacity total is the inventory in
`research/heterogeneous-owner-assembly`. Prepared by Riquelme Soares with
substantial AI assistance. New material is Apache-2.0. No coding-agent product
is named.
