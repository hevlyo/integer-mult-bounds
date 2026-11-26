# Historical status headings for #1042 and #942

**Navigation repair. No new κ and no change to the selected frontier.**

## Scope and evidence

Assignment: consolidation track, card `scope-navigation`, scope key
`b18e0e173a4430a9564b`, chooser seed `e8f3628db3d5d6359a14412e3ff25ea8`.
Base `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Priority revision 2.
Scope status: **refined**. The card asks whether one misleading
historical-current claim can be corrected. This package corrects the only two
blocks in [docs/research/current-status.md](../../docs/research/current-status.md)
that remain titled `Current reviewed status` after a historical divider.

Preserved notes send readers to that file for the authoritative bound. Before
this repair, a search for the current heading found three sections:

| Heading before this repair | Stated decimal | Record link target |
|---|---|---|
| Opening `Current reviewed status` | `0.001672660197076918` | live `certificates/selected-result.json` (#1094) |
| Block after `Historical status through #1042` | `0.001672188119205421` | the same live file |
| Block after `Historical status through #942` | `0.001661960547713947` | the same live file |

The #1042 decimal equals [certificates/checkpoints/frontier1042.json](../../certificates/checkpoints/frontier1042.json).
The #942 decimal equals [certificates/checkpoints/frontier942.json](../../certificates/checkpoints/frontier942.json).
Both differ from the live selected decimal. The historical kappa sentences,
reviews and replay commands are unchanged. Each repaired block is now titled
`Historical reviewed status at #1042` or `Historical reviewed status at #942`
and its record link names the matching checkpoint. Frozen copies of the status
note under `research/community-frontier741-audit/snapshots/` and
`research/community-batch970-audit/pr943-context/` were not edited.

The predecessor bytes of `docs/research/current-status.md` at the base commit
are provenance blob `aa3cf49715cd367ad8c4e63ab28856fc0d19794f`, SHA256
`1f59d648763c77d574d18dc59ea8bf62d2ee74aaed3c202c9c8cfa4f901badbd`.
Pins for the live selected record and the two checkpoints are in
[SOURCES.json](SOURCES.json).

A refreshed overlap search on 2026-11-26, with complete open-PR pagination of
1387 records fetched at 2026-11-26T12:11:01Z and 7979 discussion records fetched
at 2026-11-26T12:14:32Z, matched `Historical reviewed status` only in this
package. It did not show another change that retitles these two headings.
The nearest public neighbor is
[PR #3903](https://github.com/CrocSwap/integer-mult-bounds/pull/3903) at
`ad56ff7b100601d68bf9693cf53a4b3a18c47ca1`, which links the glossary to this
status note and does not edit the repeated headings. Package pin repairs that
mention `frontier1042.json` address verifier inputs, not this onboarding path.

`python3 -B scripts/research_baseline.py` printed
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. The checker below prints
`PASS_HISTORICAL_CURRENT_STATUS_HEADINGS`. It rejects an in-memory copy that
restores the two `Current reviewed status` headings, a copy that points the
repaired blocks back at the live selected record, a copy that swaps the two
checkpoint links, and a copy that replaces the #1042 prose decimal with the
live selected decimal.

## Reproduce

From the repository root, with Python 3.12 and `PYTHONOPTIMIZE` unset:

```sh
python3 -B scripts/research_baseline.py
python3 scripts/research_package.py --package research/historical-status-headings --check-only
python3 scripts/research_package.py --package research/historical-status-headings
```

No native compiler, Boost, or `research/e8-bit-p111-tuned` dependency is used.
`make frontier1094-verify` was not run. This check does not certify a
multiplication theorem.

Discussion writes are not available in this session's GitHub interface. No
discussion post was sent, and the write was not retried.

## Open next questions

Can the #890 block, which states decimal `0.001661957774647029` and still
links `certificates/selected-result.json`, be pointed at
`certificates/checkpoints/frontier890.json` without rewriting its historical
review prose?

That matters because the link now opens the #1094 record. The same live link
remains in the #799, #626, #617, #596 and #588 blocks, whose stated decimals
match `frontier799.json`, `k492626.json`, `cold617.json`, `hyperplane596.json`
and `family588.json`.

The smallest next edit is the #890 link alone, after confirming the prose
decimal equals that checkpoint. This package does not make that edit. Sections
below #588 do not all have a matching checkpoint file.

## Credit

The status note and both checkpoints are predecessor maintainer records.
Prepared by Riquelme Soares (hevlyo). Substantial AI assistance drafted the
heading repair, the checker, and these notes. New work is Apache-2.0.
