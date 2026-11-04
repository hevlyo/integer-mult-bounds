# Reconciliation tree-OID reuse

**Tooling result. No kappa change and no new multiplication bound.**

Git tree authentication in the three reconciliation verifiers was the slow
stage of `scripts/verify_pr_reconciliation.py`. The same listing is now reused
only when every path, mode and blob matches. Each caller still requires the
OID to equal the pinned tree SHA. The selected exponent stays
`836330098538459/500000000000000000`.

## Scope and evidence

Selector seed `26c8c6ab1efbcf9b944761ccba07fe17`, track `verifier-engineering`,
card `replay-runtime`, catalogue scope key `a76657a85478d269d19f`. Base
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Priority revision 2. Scope is
**refined**: the card allows one source-bound cache boundary, and this boundary
is the tree walk shared by the 92-PR, next-100 and third-100 audits.

The pinned archives are unchanged. The working verifiers and their manifest
self-pins now call `scripts/git_tree_oid.py`. Predecessor verifier bytes, read
back from the base commit, are:

| Audit | Base-commit `verify.py` SHA256 |
|---|---|
| `research/community-reconciliation92-audit` | `883b190529c1cd786d0f29cae0a9d55f3499df8916c474c49c2b3c6418d6f20c` |
| `research/community-reconciliation-next100-audit` | `8c4cd88abb5cf541bff66e42b0e32c3b3ab5cbdd58b35082b831af0dc8dff521` |
| `research/community-reconciliation-third100-audit` | `c23e644bc13809e007b920a81f4af7e6dcd1e4c6e54bd4b1d94ec001353f01b7` |

On this machine the unprofiled verifiers, before the cache and after it, were:

| Verifier | Before (s) | After, two runs (s) |
|---|---:|---:|
| 92-PR | 1.201 | 0.841, 0.888 |
| next-100 | 2.550 | 1.745, 1.684 |
| third-100 | 7.176 | 4.629, 4.790 |

A cProfile run was used only to find the stage. It inflated `PurePosixPath`
and is not the speedup measurement. The registered package replay times the
predecessor function from the base commit and the cached walk on the same 459
listings (298 distinct keys): 5.350s versus 1.542s, ratio 3.47. The three
integrated verifiers then passed in 6.847s. A direct run immediately before
that replay was 5.331s versus 1.546s, ratio 3.45, with the verifiers in 7.329s.

Failure controls: a one-blob edit is a cache miss and disagrees with the pin;
a poisoned cache value fails `audit=True`. Unsafe paths, duplicate paths and
unexpected modes are rejected. A path that is both a file and a directory
still fails closed; the predecessor raises `TypeError` there, and the new walk
raises `ValueError`. No pinned listing has that collision.

Overlap search for `tree oid`, `git tree authentication` and
`reconciliation tree_oid` against the cached complete open-PR and discussion
snapshot returned no matches. That is not a novelty certificate. Broader
`replay-runtime` discussion matches name other stages.

Discussion writes to `CrocSwap/integer-mult-bounds` are forbidden for this
account. The limitation is recorded here and in the pull request. It was not
retried.

## Reproduce

From the repository root, with `PYTHONOPTIMIZE` unset:

```sh
python3 -B -m unittest tests.test_git_tree_oid
python3 scripts/research_package.py --package research/reconciliation-tree-oid-reuse --check-only
python3 scripts/research_package.py --package research/reconciliation-tree-oid-reuse
```

Environment for the timings above: Linux, CPython 3.12.3, g++ 13.3.0 and
`libboost-dev` 1.83 installed but not used, `c++` alternative pointing at
`/usr/bin/g++`. `research/e8-bit-p111-tuned/requirements.txt` was already
satisfied (NumPy 2.5.4, SymPy 1.14.0, SciPy 1.18.1, mpmath 1.3.0).
`python3 -B scripts/research_baseline.py` printed
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`.

## What was not run

`make frontier1094-verify` was not run. `verify.py --git-blobs` was not run,
so original source objects were not fetched or re-hashed. This does not change
the selected frontier, discharge analytic or all-size assumptions, or certify
a multiplication theorem.

## Open next questions

The residual cost is gzip decompression and JSON parsing of the same archives.
A useful next step is one unprofiled third-100 profile that separates those two
calls, then one reuse keyed by the compressed bytes. It is blocked here because
a parsed cache must miss when those bytes change, and the manifest already
hashes them.

The historical manifests pin `verify.py` and not `scripts/git_tree_oid.py`.
A later helper edit can change authentication while the self-pin still matches.
Pinning the helper from those manifests would close that gap; their inventories
currently list only files inside each audit directory, so that format change
was left for a separate review.

## Credit

The pinned trees, reviews and evidence checks belong to the three
reconciliation archives and the contributors recorded in their reviews. The
digest definition is the Git tree OID those verifiers already required. New
packaging is Apache-2.0.

Prepared by a research session. Substantial AI assistance was used to profile
the verifier, implement the cache and write this package. No coding-agent
product is named.
