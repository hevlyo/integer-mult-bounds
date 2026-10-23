# pr309-states-pin-audit

**No κ change and no selected-frontier change.** This is a retained-artifact audit of one raw JSON pin. It does not repair that pin and does not rerun the native replay.

## Scope and evidence

Original card: `portable-replay` (chooser scope key `831cc1a3c8f9ff01b197`, nonce `3daf0bf1789ebe2bd57e80e3ca0127cd`, priority revision 2). Scope is **refined** to the open PR309 retiming51 predecessor hash of `249-states.json`. The card's payload-comparison premise is unchanged: newline-equivalent files are not treated as mathematical mismatches, and immutable pins are not removed.

Base commit `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. PR309 head recorded by the diagnostic is `aeb4808af1392e565e7071cbeb2c29608201cf24`. The predecessor pin names upstream PR299 head `7a30fddac2c413c9792a401e50a7e72bfbbb28f9`.

The third-100 reconciliation left PR309 open because `retiming51/compose.py` rejects the regenerated `249-states.json` hash. Four other JSON pins match after LF-to-CRLF conversion, the records word matches, and the semantic replay digest is checked before the raw states hash. See [PR309-DIAGNOSTIC.json](../community-reconciliation-third100-audit/PR309-DIAGNOSTIC.json). This package recomputes that split on the retained files.

Checked result:

- Retained states sha256 `3348648d9f659ed8c842f9b573ca7da66108a7966268e44d29caebd71bc32781` (5,825,276 bytes) is exactly `json.dumps(..., indent=2)` plus one LF. The pin is `208cc9aba1401423ca31a3305a2d2bc9e1778d78323c000bed425f0bf21518d4`.
- CRLF conversion of those bytes does not equal the pin. Lexicographic order of `initial`, and a full `sort_keys` dump, also fail in both LF and CRLF. `initial` is the only object in the file whose keys are not already lexicographic; its keys are numeric.
- `COHORT249-FINAL.json`, `COHORT249-INITIAL.json`, and `COHORT249-FRAMES.json` from the retained rank-modular final directory are one-line LF JSON. Each equals its predecessor pin after LF-to-CRLF and fails that check after a one-byte mutation. The embedded `final` map equals the cohort final file.
- `states.initial` and that newline-matching cohort initial have the same 18,943 keys and disagree in exactly 1,915 entries. Every disagreement is `ZERO` (`146904`) on the states side and a unique non-ZERO frame id on the cohort side. The retained replay receipt has `new_gauges` and `actual_kernel_gauges` equal to 1,915.
- Replacing those 1,915 states entries with the cohort frame ids, in numeric key order, still does not reproduce the pin.
- The replay receipt's normalization (drop `scope` and `source_initial_scope`; rename the single inherited-receipt alias) hashes to the pin's `predecessor_replay_semantic_sha256`. The replay file itself is not a raw predecessor pin.
- The compression record gives kernel-replay `retimed/249-states.json` the same digest and length as the failing states file, and `final/249-states.json` a different digest of the same length. Those two files are not retained here; only the recorded digests are checked.

The upstream `kernels159/replay159.py` in PR309's `vendor/base.zip` → `vendor/round5.zip` restores `source_initial` into `249-states.json` after the cohort files are emitted. That source was read from head `aeb4808af1392e565e7071cbeb2c29608201cf24` and is not re-executed by this package. The 1,915 ZERO entries are the retained-file counterpart of that restoration. They do not, by themselves, explain the unreproduced pin.

## Reproduce

From the repository root, with `PYTHONOPTIMIZE` unset:

```sh
python3 -B scripts/research_baseline.py
python3 scripts/research_package.py --package research/pr309-states-pin-audit --check-only
python3 -B scripts/research_package.py --package research/pr309-states-pin-audit
```

The baseline command is source-bound orientation only. This package's checker is standard-library Python 3.12 and does not compile C++ or regenerate artifacts. Environment for the recorded run: Linux, CPython 3.12, g++ 13.2.0 and Boost headers installed, `PYTHONOPTIMIZE` unset. `make frontier1094-verify` was not run.

## Open next questions

The author's `249-states.json` bytes are not in the retained artifacts, so the exact field diff against pin `208cc9ab…` is still open. It matters because the inherited-base replay stops before the TI extension. The smallest next step is to recover those bytes, or to compare a semantic states digest while still rejecting a changed ZERO or frame id. The blocker is the missing expected file and the decision not to rerun the native replay in this session.

## Credit

Predecessor evidence is the third-100 reconciliation audit of Dugongue's PR309 (`research/ti-local-response-schedules`), including the retained states file, pin, cohort outputs, and the decision to leave PR309 open. The newline convention follows `research/gzip-container-reproducibility`. No selected supplier or certificate is changed.

Discussion writes to the upstream discussion board are not available for this account (previously forbidden). This limitation is recorded here and was not retried.

Prepared with substantial AI assistance. New work is Apache-2.0.

## Not checked

- A fresh native replay of the PR309 inherited base, retiming51, or the TI extension.
- Byte recomputation of `frames.json` or `COHORT249-RECORDS.bin`; the diagnostic already records CRLF agreement and binary agreement, and those large files are not inputs of this checker.
- A value-level diff against the unreproduced states pin.
- Any claim that the 1,915 ZERO entries are the complete cause of the hash mismatch. Splicing the cohort values back does not reproduce the pin.
