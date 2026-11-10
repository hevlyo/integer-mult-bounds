# The selected artifact identity drops the scalar-frame audit

**Audit of one comparison. No new κ, no supplier edit, no selected-frontier change.**

`research/complex-sw4-frame8/code/generated_identity.py` is the selected
generated-artifact identity (Git blob `c8af22719c0f3097a991a3f6ccac8f090afd2faba554745733d9ea88f2c25708`,
the same bytes as the historical owner-repair copy). Its docstring says gzip
identity is the decompressed payload and that JSON identity keeps every field
except the root `seconds` value of `CLIFFORD-REVIEW.json`. The function's
`FILES` tuple never names `SCALAR-FRAME-AUDIT.json`.

On the committed #626 provider directories `ck` and `jp8`, that receipt still
holds a non-timing scalar-operation count. The count is not stored under that
key in the seven files the identity reads. Adding one to it changes the audit
file's SHA-256 and leaves every returned identity equal to the untouched
directory. The same invisibility holds for a `seconds` edit of that receipt.
A `frames` edit of `CLIFFORD-REVIEW.json` changes only that file's identity,
and deleting `CANONICAL-WORD.json.gz` is rejected. Phase `seconds` stays
excluded, which is the exclusion the identity actually implements.

`local_rank_mass` on these two receipts equals the weighted sum of
`local_profile`, so that integer is redundant with the profile. The profile
itself is also outside this identity map. This package's executed witness is
`scalar_operations`, because that key does not occur in the seven hashed files.

## Reproduce

From the repository root, with `PYTHONOPTIMIZE` unset:

```sh
python3 -B research/scalar-audit-identity-gap/verify.py
python3 scripts/research_package.py --package research/scalar-audit-identity-gap
```

Expected last line:

```text
PASS_SCALAR_AUDIT_IDENTITY_GAP providers=2 omitted_non_timing_fields=22
```

Observed environment: Linux, CPython 3.12.3, `PYTHONOPTIMIZE` unset,
g++ 13.3.0 and Boost 1.83 headers present and unused by this standard-library
check. The command copies the two provider
directories into temporary directories, mutates the copies, and deletes them.
It does not rewrite committed bytes and it does not run `make frontier1094-verify`
or `make frontier626-verify`.

## What this does not show

The invoice artifact map still stores a whole-file SHA-256 of
`SCALAR-FRAME-AUDIT.json`. A checker that requires that raw digest sees the
scalar-count edit, and it also sees a timing edit, because `seconds` is inside
the same file. This audit does not say the selected replay accepts a wrong
scalar count. It says the portable identity named above cannot see one.

Rohan Guliani's hash-substitution note
(`research/pr695-digest-audit`) and the frontier #799 review already record
that a non-timing edit of this file can follow a whole-file digest through
that substitution. The preserved #806 control adds a synthetic key. Adam Gall's
PR #1912 audits the seven files inside this same identity and finds that only
root phase `seconds` is dropped from those trees. That census does not open
`SCALAR-FRAME-AUDIT.json`. This package names the committed fields of that
sibling receipt and checks the selected identity on the committed `ck` and
`jp8` directories. It does not reproduce the historical CI payloads from run
38317651752, and it does not decide whether those missing payloads differed
only in timing.

The ancestral SW4 linker in `research/complex-sw4-frame8/verify.py` compares
this receipt after removing only `seconds`. That comparison would see
`scalar_operations`. The identity function audited here does not.

## Open next questions

`WRAPPER-CHECKS.json` is in the #626 invoice artifact map and is also absent
from `artifact_identities`. Its committed `ck` object carries
`hyperplane_end_pairs` and `cold_hyperplane_end_pairs`. The same one-field
mutation used here would tell whether those fields are invisible to the
identity. This package stops after the scalar-frame receipt. Adopting a
seconds-stripped digest of either file into the selected identity would change
pinned semantic hashes, so that adoption is a separate supplier change.

## Credit

The identity and the #626 provider receipts are the selected-source and
owner-repair lineage (Douglas Colkitt, Chafik Boukhalfa, and the predecessors
credited in the selected review). Joshua Snider preserved the three omitted
#626 assembly digests. Rohan Guliani traced their whole-file propagation.
Maxime Fleury and Antoine Olivier recorded the payload-versus-container
convention used to choose this comparison.

Prepared by hevlyo with substantial AI assistance. Apache-2.0. This is not
independent human peer review and not a multiplication theorem.

A finding post to the CrocSwap discussion board was refused with
`Resource not accessible by integration`. That refusal is recorded here and
was not retried.
