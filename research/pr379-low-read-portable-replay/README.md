# PR379 low-read portable replay

**No selected-κ change.** This is a portable replay of one retained historical
package, `research/e8-low-read-seven-complex` at
`e01bcc51ca7ee93cec54350afae8f163aafc8f93`. The candidate assembly remains
κ = 3618278388573/4000000000000000. The selected record stays
836330098538459/500000000000000000.

## Scope and evidence

Task `portable-replay` (scope key `831cc1a3c8f9ff01b197`), selector nonce
`422625a332abd11aacf8242a9b996258`, priority revision 2, base
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Scope status: **refined**. The card
asks for one environment failure whose repair keeps proof-relevant content. The
object is the verifier stop recorded in
`research/community-reconciliation-third100-audit/logs/pr379-native.txt.gz`,
not a gzip-container comparison and not the earlier states-pin audit of #309.

The retained manifest lists 74 paths. The tree has 71 files. The five absent
paths are:

- `code/__pycache__/outer.cpython-311.pyc`
- `proof/signed-source/run.log`
- `provenance/full-replay-cp311.log`
- `provenance/full-replay-cp312.log`
- `source/signed-source/run.log`

Running the original `verify.py` on Python 3.12 stops in `FileNotFoundError`
on the bytecode path, before any receipt assertion. The retained
`FULL-REPLAY-RECEIPTS.json` then asks both interpreter runs for κ =
875481145306751/10^18, which is the PR370 baseline named in the package
README, not this candidate.

The replay below uses vendored copies of the predecessor bytes. When that
commit is present locally, `verify.py` also checks those copies against
`git show`. It does not delete or rewrite the manifest pins.

| Check | Evidence |
|---|---|
| Candidate certificate `verify.py` | Retained `RESULT.json` reproduced, including histogram and calls 22020, mass 53680, deficit 120 |
| Bit coarse | 905388584776183/10^18 is the floor of the replayed candidate root at 10^−18 |
| `all-charts.cpp` | `ALL-CHARTS.json` and `CHART-RECEIPT.json` byte-identical; a flipped record bit does not reproduce that oracle |
| `columns_h.cpp` | `col.json` matches except `seconds` and `local_scalar_stream`; 1345 formal columns and 865 dirty registers |
| `lower_and_bank.py` | `LOWERING-BANKS.json` byte-identical; program sha256 `b702c84c6d10e7445e5d3401377391048289193fde01765488cff1fde748efc4` |
| `assemble.py` | `assembly.json` byte-identical: 47 strict constraints, adjacent 10^−18 grid rejected |
| Bundled PR363 `verify.sh` | Seven-stage complex coarse saving `b = 932783231884153/10^18` |

## Reproduce

From the repository root, with Python 3.12, SymPy 1.14.0, g++ as `/usr/bin/c++`,
and Boost headers:

```sh
python3 scripts/research_package.py --package research/pr379-low-read-portable-replay --check-only
python3 scripts/research_package.py --package research/pr379-low-read-portable-replay
```

`PYTHONOPTIMIZE` must be unset. The command writes only under a temporary
directory. Observed environment for the recorded run: CPython 3.12.3, g++
13.3.0, Boost headers 1.83.0, NumPy 2.5.4, SymPy 1.14.0, SciPy 1.18.1.

## Open next questions

- **Can legality and the signed defining-source checker be rerun from their producers?**
  The retained review still lists those obligations. The first step is to compile
  `legality_h.cpp` against the retained cohort and run the signed-source checker.
  This is blocked as a source-complete claim because those inputs are already
  produced receipts and were not pinned here.
- **Can a fresh two-interpreter replay replace `FULL-REPLAY-RECEIPTS.json`?**
  That receipt witnesses the PR370 baseline, and both logs are absent. The first
  step is a candidate-source run at CPython 3.11 and 3.12. It is blocked because
  `provenance/lowread-full-replay-source.tar.gz` is the PR370 tree.

## Credit and assistance

The low-read candidate, charts, columns, lowering, and seven-stage composition
are the retained work of the PR379 and PR363 authors, including Dylan Crow,
Jacob Sussman, eumemic, and the notices inside those sources. The third-100
reconciliation recorded the verifier stop and left #379 open. This package adds
the portable replay and the separation between the missing environment files
and the PR370 replay kappa.

Substantial AI assistance was used for task selection, the harness, and
execution. No coding-agent product is named. Apache-2.0.

Discussion writes to `CrocSwap/integer-mult-bounds` are forbidden for this
account (`FORBIDDEN` / resource not accessible). No discussion post was
attempted on this run, and the write was not retried.
