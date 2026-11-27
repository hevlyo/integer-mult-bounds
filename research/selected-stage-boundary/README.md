# Selected stage boundary on the PR1094 owner map

**Scoped obstruction and an out-of-contract price. No new κ.**

The selected record stays `836330098538459/500000000000000000`. This package
does not change a supplier, an owner map, or a window capacity.

## Scope and evidence

Track `recursive-interfaces`, card `persistent-boundary`, scope key
`026be4b6e61971d51838`. Assignment seed `2508a270168c05f74943560d58871b31`.
Priority revision 2. Base `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`.
Scope status: **refined**. The pair is fixed as the two successive stage
placements of one helper on the selected 144-call gauge44 map, rather than an
abstract multitype recurrence.

Two call types, taken from `provider_calls` in the pinned plan:

- Type F: a forward gauge44 call.
- Type B: a backward gauge44 call.

Each of the 7,680 helpers (16 replicas, 480 helpers) is hosted once in every
stage `0..8`. The next placement is always the opposite orientation. The
hosted-cell contract is the half-open offset interval on
`(owner_replica, child, port)`.

Across all 61,440 successive pairs:

- the schedule gap is one of 4, 6, 8, 10, 12, 14, 16, never 1;
- 0 pairs share a coordinate cell;
- 41 pairs reuse the same port, and those offsets are disjoint;
- 2,582 pairs reuse the same window child.

The next typed call does not rewrite the previous hosted interval, so it does
not reconstruct that restoration. Dropping the exit restoration of those cells
is not a legal composition on this map.

Every one of the 32,256 window ports is exactly full: hosted cells are a
prefix, and the idle remainder rank is `capacity - used`. There are 24,730
full ports and 7,526 idle remainders, matching the published idle profile
`{1:2276, 3:377, 7:7, 48:4866}`. The aggregate identity
`deficit = W - 64N = 5120` holds. A per-family form of that identity is not
rederived here.

### Out-of-contract relaxation

The most favorable one-unit merge at the selected complex endpoint sends one
rank-1 child from each of the 144 calls into an empty capacity-48 remainder
(there are 4,866 such ports). The histogram change is `-144` at rank 1,
`-144` at rank 48, and `+144` at rank 49. Rank mass stays `1,041,408`.
Concavity of `x^(1-a)` makes a rank-48 target cheaper than a rank-1 target;
the verifier checks that one-merge comparison directly.

Each of those ports has used `0` and capacity `48`, so a rank-49 remainder
needs capacity 49. The recorded contract rejects the move.

If that capacity increase were free, both pinned moment engines would still
put the moment strictly below one at the published complex endpoint and at
the next `10^-24` endpoint. A 40-step Mercator bracket of the relaxed root is

```text
140580340963215187719634009/83886080000000000000000000000
< root <
281160681926430528027158643/167772160000000000000000000000
```

which is about `0.0016758482571031`, roughly `3.8558e-7` above the selected
complex endpoint `67018507072324140917/40000000000000000000000`. The upper
end stays below the selected bit endpoint, so the complex side would still
bind. This is not an admitted root and not a new κ. The outer 47-constraint
assembly was not run.

Sagar Thakrar's PR1012 priced restoration deferral on the earlier T37 payload
and found a mass-neutral consolidation there. That package is not in this
checkout. The heterogeneous-owner bound states that this deferral model is
outside its catalogue. The present census is the selected T16 map's cell and
capacity obstruction, not a replay of either result.

An earlier note on this same card studied unread source toggles on three
connector schedules. That question is not this owner-map census.

Cinna Davis's merged PR1829 censuses direct owner and chart identity on all
143 adjacent call pairs and explicitly leaves nonadjacent calls alone.
Discussion
[#1986](https://github.com/CrocSwap/integer-mult-bounds/discussions/1986)
reports intersection dimension 0 for one forward/backward data-frame pair on
112 ports, and says that does not rule out changed schedules. This package
counts a different pair: the same helper's next stage placement, which is
never the next call. It does not replay those packages.

## Reproduce

Python 3.12, standard library. From the repository root, with
`PYTHONOPTIMIZE` unset:

```sh
python3 -B research/selected-stage-boundary/verify.py
python3 -B scripts/research_package.py --package research/selected-stage-boundary
```

Expected first line:

```text
PASS_SELECTED_STAGE_BOUNDARY helpers=7680 pairs=61440 same_port=41 shared_cells=0 full_ports=24730 idle_ports=7526 merges=144 capacity_increase=1 controls=7
```

The verifier reads the pinned plan, owners, SPEC, assembly and the two moment
engines. It writes nothing. Seven controls reject an overlapping cell, an
adjacent successive pair, a same-orientation pair, a capacity claim on a
recorded donor, a mass-dropping deletion posed as deferral, and they keep the
rank-48 merge strictly cheaper than a rank-1 merge. A capacity-49 window is
accepted by the fit predicate so the rejection is not a constant false.

`python3 -B scripts/research_baseline.py` was run first and returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. `make frontier1094-verify` was not run.

## What was not checked

- The outer 47-constraint map and any κ for the relaxation.
- The selected canonical word. SPEC records
  `CANONICAL-WORD.json.gz` as `4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c`.
  The file at `research/gauge44-slots/evidence/local/CANONICAL-WORD.json.gz`
  hashes to `92941c2b718b533f1d3addb710d261a6e2b9ec5d19f0051d79775b08cb2571ed`
  and was not used.
- Per-family coverage `8k_f + 1 + hosted_f + idle_f = 73`.
- Phases, cones, cleanup gates, native replay, and Lean.
- A second moment engine's bracket. Base-two signs are checked at the
  published endpoint and the next `10^-24` point only.

Discussion writes were not available in this session's GitHub interface.
No discussion post was sent, and the write was not retried.

## Open next questions

- Does one FULL-cleanup gate in the selected local word already name
  coordinates that sit in the successor stage's recorded pending set? That
  would be a restoration the next stage could advance without growing a
  window. Bind `CANONICAL-WORD.json.gz` at the SPEC hash above and compare
  one forward call's final cleanup with the next stage's pending axes. The
  matching word bytes are not the local evidence file in this checkout.
- For the 41 same-port successive pairs, is the shared idle remainder already
  charging a coordinate that both local cleanups also charge? List those 41
  `(owner_replica, child, port, offset, width)` rows against the local
  cleanup. The same missing word blocks the comparison.

## Credit

The owner map is Rohan Arun's PR1094, on Jeremy Kothe's T16 packing lineage
and Hao Yan's window geometry. The moment engines are the pinned multicold
engines used by the selected assembly. PR1012 (Sagar Thakrar) and
`research/heterogeneous-owner-assembly` (Ali Romman) are the deferral
predecessors named above. New material is Apache-2.0.

Prepared by an AI-assisted research session. Substantial AI assistance was
used for the census, the verifier and this note. No independent human review
is claimed.
