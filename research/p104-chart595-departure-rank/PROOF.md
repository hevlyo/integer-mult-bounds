# Chart 595 cannot export a second protected-safe form

All scalars are rational. The finite facts below are checked by `verify.py`
from the pinned selected PR6030 word. Event indices are zero based.

## 1. Contract

Keep the selected word, its frames and its event order. After event 13637,
`COPY 778 <- 572` in chart 595, replace the value of field 572 by an
independent scalar `z`. Every original public input stays arbitrary.

Allow any finite sequence of homogeneous linear operations, with arbitrary
rational coefficients, on the fields that currently occupy chart 595. Do not
add, delete or retarget a MOVE, INIT or CLEAR, and do not edit any other
chart. COPY and CLEAR inside chart 595 are included. This is a relaxation of
reversible scalar programs: a noninvertible map is allowed, so failure here
also excludes every invertible program in the same region.

The anchor chart is `V = final(572)`. A public output is protected when its
final chart is not `V`. A correction is successful only when every protected
output equals its original unsplit value on all original inputs and on `z`,
and at least one public output has a nonzero coefficient on `z`.

## 2. Exports from chart 595

ADD, COPY and SCALE on this word are same-chart operations: the verifier
checks every scalar event against the chart occupation reconstructed from
INIT, MOVE and CLEAR. Therefore a value created in chart 595 reaches another
chart only when a field MOVEs out of chart 595, or when that value is
discarded by CLEAR.

After event 13637 the MOVE events whose source chart is 595 are exactly

```text
13652: 572 -> 603
13988: 134 -> 618
14001: 127 -> 637
14344: 450 -> 711
14458: 496 -> 729
14470: 731 -> 737
14684: 581 -> 766
14688: 582 -> 767
```

Fields 134, 450 and 496 enter chart 595 from chart 3 after the cut and then
leave again; those three leaves are included. Owned field 778 is cleared at
event 13656 while it is still in chart 595, so a value parked only in 778
does not leave the chart. The whole word moves a field into chart 603 on only
three occasions: 572 from 595, 709 from 597, and a fresh INIT of 778. No
later departure from chart 595 enters chart 603.

## 3. Departure columns

MOVE does not change a field's value. For each departure, place a unit
perturbation on that field immediately after its MOVE and apply every later
original event. Linearity gives the public image of an arbitrary perturbation
of the eight departure values, even if arbitrary chart-595 rewrites occur
between the departures: a rewrite immediately before a departure can set that
departure value to any form in the span then available, and can reset the
fields that remain. It cannot change a value that has already left the chart.

Let the eight images be columns. On the protected output rows

```text
(120, 134, 127, 136, 135, 144, 116, 176)
```

the 8 by 8 minor has determinant `1/2`. The same determinant is computed by
fraction-free elimination and by the Leibniz formula. The full set of
protected rows touched by these columns also has rank 8. Deleting any one
column drops the rank of those eight rows to 7, so each departure contributes
an independent protected constraint.

Thus the only perturbation of the eight departure values that preserves every
protected output is the zero perturbation. Each departure value is forced to
equal its value in the original unsplit word.

## 4. Conclusion

The original departure values are independent of `z`, because `z` is
introduced only by the post-cut overwrite inside chart 595 and the original
word does not contain it. A protected-preserving correction must therefore
export no `z` at any of the eight departures. Chart 595 is empty after event
14688, and the saved copy in field 778 has already been cleared. No remaining
field carries `z` out of the chart.

Every public output is a linear function of values that either never met
chart 595 after the cut or left through one of these eight departures. Both
kinds are independent of `z` under the forced exports. Every public
coefficient of `z` is zero.

In particular, granting the seven later chart-595 departures as possible
carriers does not create the second transported form left open by the local
two-bank argument. A nonzero public response to `z` requires an edit outside
chart 595, a new MOVE, or a pre-cut copy into a field that is not subject to
this census.

## 5. What remains out of scope

Edits in destination charts 603, 618, 637, 711, 729, 737, 766 and 767, or on
the chart-597 path of field 709, could in principle cancel a protected image
after a departure. That is a different contract. No such cancellation is
constructed or priced here. Pre-cut copies, changed routes, nonlinear
encodings, native maps, ownership, precision, the caller and the signed
invoice are untouched. There is no new supplier, no change to the paid or
productive profile, and no new kappa. The five selected framework assumptions
remain. This finite certificate is not a proof of the multiplication theorem.
