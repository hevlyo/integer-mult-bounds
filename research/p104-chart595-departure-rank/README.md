# Chart 595's eight departures are protected-independent

**Scoped negative result; no new kappa.** On the selected PR6030 word, after
the helper-572 overwrite at event 13637, arbitrary rational linear edits on
chart 595 do not produce a nonzero public response to the new input while
preserving every protected output. The eight later departures from chart 595
have protected rank 8. Their explicit 8 by 8 minor has determinant `1/2`.

The local two-bank theorem in
[p104-unrestricted-572-seam](../p104-unrestricted-572-seam/README.md) allows
edits only through event 13655 and one transported row into chart 603. This
note extends the editable region to the whole remaining life of chart 595,
including fields 134, 450 and 496, which enter from chart 3 after the cut.
Those extra carriers still cannot hide the new input. The proof is in
[PROOF.md](PROOF.md).

## Reproduce

From the repository root, CPython 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/p104-chart595-departure-rank
```

Direct replay, normally and with `-O`:

```sh
python3 -I -W error -B research/p104-chart595-departure-rank/verify.py
python3 -I -O -W error -B research/p104-chart595-departure-rank/verify.py
```

Expected marker: `PASS_P104_CHART595_DEPARTURE_RANK`. The checker authenticates
the word hash, reconstructs chart occupation, lists the eight departures and
the three entries into chart 603, and computes the protected minor by both
Gaussian elimination and the Leibniz formula. Failure controls flip one minor
sign, drop each departure column, and retarget the last MOVE into chart 603.
No file is written.

## Scope

The task card is `p104-side-correction` at priority revision 8. The scope is
**refined** to one selected-word chart and one cut. A full helper split would
need a legal second route and a complete signed invoice; this certificate
shows that chart-595 edits alone do not supply that route. The selected
frontier is unchanged.

The one chooser run on the stale fork main assigned the retired
`complex-masked-decoder` card. Canonical main is 7,895 commits ahead of that
fork main and no longer contains the card. The complex-mechanisms track was
kept and the question was taken from the current card, then narrowed to this
cut. Discussion comments could not be posted from this environment, so no claim
was created and the finding is recorded here. A refreshed overlap search at
2026-11-09T12:15:37Z covered 881 open PRs and 6,922 discussion records with
complete pagination, plus the local notes at `7c49fe32`. The nearest results
are the local helper-572 seam, the two-ADD census and the combination-carrier
classification. None gives this eight-departure minor. The search does not
read every code diff, so it is not a novelty certificate.

## Validation limits

Not run: `make frontier6030-verify`, native maps, caller replay, Lean, Docker,
and any edit outside chart 595. Same-chart scalar checks and the rank
certificate do not price MOVE, ownership or precision. Unknown costs are not
treated as zero. Finite exact arithmetic supports the written rank argument;
it is not an all-size multiplication proof.

## Open next questions

1. Can an edit in one destination chart cancel that departure's protected
   image and still leave a final output that depends on the new input? Start
   with field 134's chart 618 and outputs 134 and 221. The blocker is a legal
   chart-local inverse together with the signed invoice for every added gate.
2. Can a pre-cut copy into a field that never occupies chart 595 after event
   13637 evade the departure census? Pin one such field and its owned
   lifetime before changing the word. The present census does not apply to a
   value that has already left.

## Credit

The selected word is DreamingOfClouds' PR6030, retained at
`research/p104-helper470-twin-rung-removal/WORD.json.gz`. Nick Petalas's
unrestricted chart-595/603 seam posed the second-transport question and proved
the local one-channel case. JoyboyBrian, apoursh, Jonathan Capalbo and
JosieElliston supplied the earlier helper-572 exclusions and combination-carrier
census; this note does not rerun those classifications. Ali Romman and the
P104, native and caller lineage remain the construction predecessors.

Prepared by hevlyo with substantial AI assistance in the route census, the
exact minor, the verifier and the notes. Apache-2.0. No independent human or
proof-kernel review is claimed.
