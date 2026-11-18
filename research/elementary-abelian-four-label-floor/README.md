# Three-gate words for four addresses in `(Z/2)^3` have total rank at least 5

**Scoped sharpening; no new κ.** The selected conditional result, the
selected suppliers and `upstream/` are unchanged. The complex side binds,
and this finite address model is not a bit-supplier admission.

The rank-one count for these targets is already 4. Over `F2`, Wentao Li's
`research/elementary-abelian-diagonal-minimum` gives one rank-one call per
non-identity diagonal entry of `F2[(C2)^k]`. Over every field, the
prime-exponent theorem recorded in discussion
[#1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19227902)
(PR #6008) gives total projector rank at least `d` for `d` non-identity
entries. Neither statement is in this checkout. Both allow a three-gate
word of ranks `(2,1,1)`, total rank 4. The argument below rules that shape
out.

Let `V=(Z/2)^3` and let `K` be any field. A paid gate on finitely many
registers is

```text
D(N,g) = (I-N)[0] + N[g],    N^2 = N,   g in V.
```

It costs one at every rank. A free operation is a matrix over `K`, of any
shape, acting as the identity address `[0]`. It may add or drop workspace,
copy, or be singular. It cannot apply an address. The target is
`diag([t1],[t2],[t3],[t4])` with four distinct nonzero `ti`. Dirty workspace
may change arbitrarily, but it may not affect the data output.

## Theorem

For every such quadruple, in any characteristic, with finite workspace and
free scalar maps:

1. Two paid gates are impossible at every rank. Three gates suffice, so the
   unit-gate count is 3.
2. Every three-gate realization uses a basis of labels and has total
   projector rank at least 5. Ranks `(2,1,1)` do not occur.
3. Four rank-one coordinate gates realize the target at total rank 4.

A unit-minimum word therefore costs at least one rank unit more than the
general floor of 4. Rank charging prefers the longer rank-one word.

This replaces the rational three-register model
(`research/bit-three-register-lower-bound`: three registers, frames in
`M_3(Q)`, nine calls) by four data registers and the finite group
`(Z/2)^3`. The dependent triple `{g,h,g+h}` already has unit cost 2 and
rank-one cost 3. The new constant is for four addresses: the general floor
allows total rank 4, and every three-gate word needs at least 5.

## Proof

**Support.** Expand each gate into the branches `I-N` and `N`. Free scalar
matrices contribute only `[0]`. Every data-output entry is a `K`-linear
combination of subset sums of the three labels. Cancellation can remove an
address, not create one outside their span. A subspace of dimension at most
2 contains at most three nonzero vectors, so two gates, or three dependent
labels, cannot produce four distinct nonzero addresses.

**Unit upper bound.** The quadruple spans `V`. In the standard basis
`(e1,e2,e3)`, let `N_j` be the diagonal projector whose `i`-th entry is the
`j`-th bit of `ti`. Then `D(N_1,e1) D(N_2,e2) D(N_3,e3)` equals the target.
In any basis a nonzero vector has weight at least 1, and at most three
vectors have weight 1, so four distinct nonzero vectors have total weight
at least 5. Thus some `N_j` has rank at least 2, every `N_j` is nonzero,
and the total rank of this word is at least 5.

**Rank lower bound for every three-gate word.** A successful three-gate
word cannot have dependent labels, so its labels `g,h,k` are a basis.
Let `χ` be the dual coordinate that is 1 on `g` and 0 on `h` and `k`.
Exactly one gate has `χ=1`. The algebra map `K[V] → K[Z/2]` sends that
gate to `(I-N)+N[σ]` and sends the other two gates to `I`. Free maps stay
scalar. The coefficient of `[σ]` from data inputs to data outputs is
therefore `B N A` for scalar matrices `A,B`, and its rank is at most
`rank N`. On the target, that coefficient is the diagonal matrix with a 1
in each position whose address has `χ=1`, and 0 elsewhere.

In the label basis, those addresses are four distinct nonzero vectors.
Their total weight is at least 5, so some dual coordinate is 1 on at least
two of them. The corresponding gate has rank at least 2. Summing the three
coordinates, the total rank is at least 5. In particular the three gates
cannot all have rank one.

**Rank-one upper bound.** `D(E_ii, ti)` multiplies register `i` by `[ti]`
and fixes the others. Four such gates give the target and total rank 4.
One or two gates are already excluded by the support bound, so four is the
rank-one minimum.

The identity `K^n = im N ⊕ ker N` for a projector is the reason a rank-one
gate is similar to `E_11`, but the rank bound above does not need that
similarity: it uses only `rank(BNA) ≤ rank N`.

## What was checked

`verify.py` uses the standard library only. It exhausts all 35 quadruples,
all 168 ordered bases and all 512 ordered label triples. For every
quadruple it rebuilds both words in three independent algebras: bit masks,
frozensets of vectors, and nonnegative integer coefficients. The integer
engine checks that every construction coefficient is 0 or 1, so the words
are not using characteristic-2 cancellation. It also checks that omitting
any basis gate, or clearing any single 1 in a projector, misses the target;
that every `F2` rank-one idempotent on four coordinates is one of the 120
outer products `xy^T` with `y^T x=1`; and that the dependent triple
`(e1,e2,e1+e2)` has an explicit two-gate unit word while no one-register
rank-one gate realizes it.

## Reproduce

From the repository root, with CPython 3.12:

```sh
python3 -B research/elementary-abelian-four-label-floor/verify.py
python3 -I -O -B research/elementary-abelian-four-label-floor/verify.py
python3 -B scripts/research_package.py --package research/elementary-abelian-four-label-floor --check-only
```

Expected final line:

```text
PASS_ELEMENTARY_ABELIAN_FOUR_LABEL_FLOOR quadruples=35 bases=168 label_triples=512 unit_gates=3 rank_one_gates=4 total_rank_at_least=5 standard_weight_range=5..9 omissions=105 cleared_bits=240 idempotents=120 engines=3 no_new_kappa
```

`standard_weight_range` is the Hamming weight in the standard basis. The
lower bound of 5 is checked again in every ordered basis.

## Limits

The theorem is for this address group and for diagonal targets whose
entries are distinct and nonzero. It does not cover repeated addresses,
groups with trivial homomorphism onto `(Z/2)^3`, restricted label sets,
data-dependent control, or a nonfaithful representation. No native gate,
frame, hosting, precision, tape, or recursive child is priced. The selected
cold replay `make frontier1094-verify` was not run, and neither was any
Lean or predecessor suite. One attempt to post this finding on discussion
#1166 returned `Resource not accessible by integration`. That write was
not retried.

## Open next questions

1. **Does `A4` still force rank-one cost four for four distinct non-identity
   addresses?** `A4` is the smallest nonabelian group with no homomorphism
   onto `Z/2`, so the character cut above is blind there. A length-three
   rank-one word would be genuine compression. The first step is to fix
   four 3-cycles inside one ordered three-label subproduct set and either
   find a `C3` coefficient cut of rank at least 2, or test the coordinate
   normal form over `F2` against a finite scalar generating set. Free
   scalar maps are infinite, so that search becomes a proof only with a
   normal form or a new quotient identity.

## Credit

The rational three-register model and its nine-call theorem are Ali
Romman's `research/bit-three-register-lower-bound`, from the pinned
argument in eumemic's PR #288. The three-label separation between unit
cost and rank-one cost is Ali Romman's `research/group-subproduct-cover`
(PR #5394). Wentao Li's `research/elementary-abelian-diagonal-minimum`
already gives the `F2` rank-one count, and the prime-exponent theorem in
PR #6008 gives total rank at least 4 over every field. Those packages are
not in this checkout and were not replayed. The new comparison is the
exclusion of total rank 4 for every three-gate word. The calculation, both
explicit words, and this verifier were prepared in an AI-assisted research
session. Substantial AI assistance was used for the argument and the
checks. Apache-2.0.
