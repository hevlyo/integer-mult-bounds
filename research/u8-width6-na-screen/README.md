# U8 width-6 no-arbitrage screen

**Negative for primitive saving `1/99`. No new κ.** One optimistic helper
inventory outside the frozen 25-interface catalogue still cannot reach the
planning threshold, and its dual root is certified exactly.

## Task card

```text
Task ID / proposed scope key:
  complex-new-helper-inventory / 5868e5281a1e63d41a22, refined
Base commit; exact predecessor and dependency heads:
  ef5f39403610d231a0c27e8a6b4f08c10209bcd6
  Chooser nonce 0c810412be6378dd4423b59d92247de3, track complex-mechanisms,
  priority revision 2.
  Predecessor dual: research/heterogeneous-owner-assembly (PR942 prices and
  the U8/T37 reference). Moment engines pinned in SOURCES.json.
Concrete object and question:
  Replace all 122 width-8 helpers in one U8 call by width-6 helpers, delete
  two rank-1 children for each, and set the width-6 signed price to the most
  negative six-unit fill marginal that old widths {4,5,7,8,9} attain in a
  bin of capacity at most 48. Does the resulting dual relaxation reach
  saving 1/99?
Scope status: refined. Width 6 occurs in none of the 25 frozen interfaces.
  The screen is one uniform count and one price, not a catalogue mixture.
Existing restriction being changed:
  The frozen helper alphabet W={4,5,7,8,9}. The shared-pool dual, the mass
  identity paid rank - helper width = 1856, and the PR795 prices on W stay.
Method; parameter domain:
  Exact rational fill recurrence, both pinned moment engines, saving interval
  (0, 1/500] for support and the single histogram below.
Nearest overlap:
  The catalogue mixture bound does not price width 6. R489/R480 change
  widths 4 and 7 into width 9. This file does not repeat those inventories.
Optimistic budget:
  Price -39, every width-8 helper shrunk, and the 244 freed rank units taken
  from rank 1, which is the most expensive equal-mass rank.
Success / falsification:
  A root at or above 1/99 would be headroom for the planning target. A root
  below 1/500 falsifies that target for this relaxation.
Predecessor authors:
  Chafik Boukhalfa's PR795 prices and PR942 dual, as retained by
  research/heterogeneous-owner-assembly. The moment engines keep their own
  notices.
```

## Result

Let `D` be the usual unbounded-fill maximum for prices `(-1,-20,-8,-2,4)` at
widths `(4,5,7,8,9)`. On attainable used-widths up to 48, the unique most
negative six-unit marginal is

```text
D(10) - D(4) = -40 - (-1) = -39,
```

attained only at start width 4. Call this price `p_6`. A price `-40` beats
the old width-10 fill, so it is outside the screen.

At `p_6 = -39` the extended alphabet does not raise any old bin maximum. It
adds exactly four maximum-price bins, each a single width-6 helper:

| Capacity | Remainder | Signed price |
| ---: | ---: | ---: |
| 8 | 2 | -37 |
| 16 | 10 | -35 |
| 32 | 26 | -31 |
| 48 | 42 | -52 |

All 1,163 old patterns, and these four new maxima, have support forms that
vanish at saving 0. Except for the old equality remainders `{0,1,48}`, both
retained engines give a positive derivative lower bound throughout
`[0, 1/500]`. The packing multiplier's derivative is positive there too, so
the inherited `(A, λ)` dual still lower-bounds the idle moment on
`(0, 1/500]`.

The screened call keeps the U8 mass identity. Width sum drops by
`122 * 2 = 244`, and 244 rank-1 children are deleted. Nine calls and the
`T = 37` clearing of the idle dual produce the net coefficient histogram

```text
{1:690378, 2:112554, 3:148518, 4:53946, 5:23976, 8:2664, 48:14380}
```

with live stock `33,152` and deficit `11,840`. The rank-1 entry mixes the
local children with the idle dual; it is the net coefficient of `φ(1)`, not
a claim that a scalar program contains 690,378 rank-1 calls.

Both engines put this moment strictly below 1 at

```text
1821649025053055110577 / 10^24
```

and strictly above 1 at the next `10^-24` tick. That upper tick is less than
`1/500`, which is less than `1/99`. Any realization whose moment is at least
this dual lower bound therefore misses primitive saving `1/99`.

At the published U8 successor tick `1664727258740678855773/10^24`, the same
lower bound is still strictly below 1, while the published U8/T37 histogram
is already above 1. The screen does not forbid every improvement over U8.
Under the retained planning map `κ = a/(1+a)`, the upper tick has image

```text
910824512526527555289 / 500910824512526527555289
≈ 0.001818336653860332
```

which is above the selected `κ` and far below `1/100`. This package does not
change the selected frontier.

Deleting 122 rank-2 children instead of 244 rank-1 children, with the same
inventory and price, has a strictly higher moment at the accepting tick in
both engines. Rank 1 is the favorable equal-mass choice because two rank-1
units are available (`2,548 ≥ 244`) and `(73/r)^b` decreases in `r`.

## Reproduce

Python 3.12, standard library only, assertions enabled. `PYTHONOPTIMIZE` must
be unset. From the repository root:

```sh
python3 -B research/u8-width6-na-screen/verify.py
```

Expected line:

```text
PASS_U8_WIDTH6_NA_SCREEN root=0.001821649025053055110577..0.001821649025053055110578 kappa_cap=910824512526527555289/500910824512526527555289 controls=4
```

The same command is the registered replay. Optimized execution (`-O`) is
rejected before any certificate is issued. The four controls reject remainder
2 at signed price 33, a price of `-40`, a deletion of only 243 rank-1
children, and they separate the rank-2 alternative.

Checked here: the fill recurrence, all old legal bins, the four new maxima,
the mass identity, and the moment signs above. Not checked: a scalar program,
dirty restoration, an owner map, hosted invoice, native replay, and
`make frontier1094-verify`. Discussion writes for this account were already
forbidden and were not retried.

## Open next questions

Can a proper subset of the 122 width-8 helpers be shrunk inside the pinned U8
scalar program so a hosted invoice, not only this dual lower bound, sits
strictly below 1 at `1664727258740678855773/10^24`?

That gap is the only room this screen leaves below its root. A hosted point
inside it would be a real complex-side improvement; the full rewrite still
cannot reach `1/99` under these hypotheses. The first step is to shrink one
width-8 helper, delete exactly two rank-1 children, restore arbitrary dirty
inputs, and price that single call with this dual. The blocker is that no
such scalar program is constructed here. A price below `-39` would also need
a new credit rule.

## Credit

The signed prices, capacity bonuses, U8 profile, and shared-pool dual are
inherited from Chafik Boukhalfa's PR795 and PR942, as recorded in
[the heterogeneous-owner proof](../heterogeneous-owner-assembly/PROOF.md).
The two moment engines are the pinned multicold sources and keep their
notices. R489 and R480 are different inventory changes and are not reused.

Prepared by a donated research session with substantial AI assistance.
No independent human review is claimed. New work is Apache-2.0.
