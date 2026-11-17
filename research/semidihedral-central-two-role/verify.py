#!/usr/bin/env python3
"""Exact two-register call minima for the semidihedral central translation.

The regular representation of F2[SD16] is faithful, so equality of the packed
operators is equality in M_2(F2[SD16]). Python 3.10+ standard library only.
"""

from __future__ import annotations

import sys

W = 2
ORDER = 16
DIM = W * ORDER
R = 1
S = 8
R4 = 4
R2 = 2
RINV = 7  # filled after inv() is available; checked below


def fail(message: str) -> None:
    raise SystemExit("FAIL_SEMIDIHEDRAL_CENTRAL_TWO_ROLE " + message)


def mul(a: int, b: int) -> int:
    """Multiplication in <r, s | r^8 = s^2 = 1, s r s = r^3>.

    Elements 0..7 are r^i and 8..15 are r^i s.
    """
    a_s, b_s = a >> 3, b >> 3
    ai, bi = a & 7, b & 7
    if a_s == 0 and b_s == 0:
        return (ai + bi) & 7
    if a_s == 0 and b_s == 1:
        return 8 | ((ai + bi) & 7)
    if a_s == 1 and b_s == 0:
        return 8 | ((ai + 3 * bi) & 7)
    return (ai + 3 * bi) & 7


def inv(a: int) -> int:
    for b in range(ORDER):
        if mul(a, b) == 0:
            return b
    fail("missing inverse")
    return 0


def check_group() -> None:
    for a in range(ORDER):
        for b in range(ORDER):
            for c in range(ORDER):
                if mul(mul(a, b), c) != mul(a, mul(b, c)):
                    fail("group law is not associative")
    for a in range(ORDER):
        if mul(a, inv(a)) != 0 or mul(inv(a), a) != 0:
            fail("inverse table")
    if mul(R, R) != R2 or inv(R) != RINV:
        fail("rotation naming")
    if mul(S, S) != 0:
        fail("reflection square")
    # s r s = r^3, the semidihedral relation. The dihedral relation s r s = r^{-1} is false.
    srs = mul(mul(S, R), S)
    if srs != 3:
        fail("semidihedral relation")
    if srs == inv(R):
        fail("presentation collapsed to the dihedral group of order 16")
    # r^4 is central of order 2.
    if mul(R4, R4) != 0:
        fail("r^4 order")
    for g in range(ORDER):
        if mul(R4, g) != mul(g, R4):
            fail("r^4 is not central")
    # Positive length of r^4 in the paid alphabet, by the group Cayley graph.
    dist = {0: 0}
    layer = [0]
    alphabet = (R, inv(R), S)
    for depth in range(1, 5):
        nxt = []
        for g in layer:
            for a in alphabet:
                h = mul(a, g)
                if h not in dist:
                    dist[h] = depth
                    nxt.append(h)
        layer = nxt
    if dist.get(R4) != 4:
        fail("group length of r^4")
    if any(dist.get(g) == 0 for g in (R2, R4) if g != 0):
        fail("length table")
    if dist.get(R2) != 2:
        fail("group length of r^2")


def rank_one_idempotents() -> list[tuple[int, int]]:
    found = []
    for x in range(1, 1 << W):
        for y in range(1 << W):
            if (bin(x & y).count("1") & 1) == 0:
                continue
            rows = tuple(y if (x >> i) & 1 else 0 for i in range(W))
            found.append(rows)
    found = sorted(set(found))
    if len(found) != 6:
        fail("expected 6 distinct rank-one idempotents")
    # Independent census of all 16 matrices.
    census = []
    for a in range(2):
        for b in range(2):
            for c in range(2):
                for d in range(2):
                    rows = (a | (b << 1), c | (d << 1))
                    n2 = (
                        (a * a + b * c) & 1 | (((a * b + b * d) & 1) << 1),
                        (c * a + d * c) & 1 | (((c * b + d * d) & 1) << 1),
                    )
                    det = (a * d + b * c) & 1
                    nonzero = rows != (0, 0)
                    if n2 == rows and nonzero and det == 0:
                        census.append(rows)
    if sorted(census) != found:
        fail("rank-one idempotent census disagrees with xy^T enumeration")
    # [[1, 1], [1, 0]] squares to [[0, 1], [1, 1]], so it is outside the alphabet.
    non_example = (1 | (1 << 1), 1)
    square = (
        (1 * 1 + 1 * 1) & 1 | (((1 * 1 + 1 * 0) & 1) << 1),
        (1 * 1 + 0 * 1) & 1 | (((1 * 1 + 0 * 0) & 1) << 1),
    )
    if non_example in found or square == non_example:
        fail("non-idempotent control was accepted")
    return found


def pack_identity() -> tuple[int, ...]:
    return tuple(1 << j for j in range(DIM))


def apply_vec_fast(v: int, y: int, xbits: tuple[int, ...], left: tuple[int, ...]) -> int:
    scalar = 0
    kk = y
    while kk:
        bit = kk & -kk
        k = bit.bit_length() - 1
        scalar ^= (v >> (k * ORDER)) & 0xFFFF
        kk ^= bit
    if scalar == 0:
        return v
    mixed = 0
    ss = scalar
    while ss:
        bit = ss & -ss
        h = bit.bit_length() - 1
        mixed |= 1 << left[h]
        ss ^= bit
    delta = 0
    for i in xbits:
        delta |= (scalar ^ mixed) << (i * ORDER)
    return v ^ delta


def gates(idems: list[tuple[int, int]]) -> list[tuple[int, tuple[int, ...], tuple[int, ...]]]:
    labels = (R, inv(R), S)
    out = []
    for rows in idems:
        y = next(row for row in rows if row)
        xbits = tuple(i for i, row in enumerate(rows) if row)
        for g in labels:
            left = tuple(mul(g, h) for h in range(ORDER))
            out.append((y, xbits, left))
    if len(out) != 18:
        fail("gate count")
    return out


def apply_state(cols: tuple[int, ...], gate) -> tuple[int, ...]:
    y, xbits, left = gate
    return tuple(apply_vec_fast(c, y, xbits, left) for c in cols)


def target(mults: tuple[int, int]) -> tuple[int, ...]:
    cols = []
    for j in range(DIM):
        i, h = divmod(j, ORDER)
        cols.append(1 << (i * ORDER + mul(mults[i], h)))
    return tuple(cols)


def ball(start: tuple[int, ...], radius: int, alphabet) -> dict[tuple[int, ...], int]:
    dist = {start: 0}
    layer = [start]
    for depth in range(radius):
        nxt = []
        for state in layer:
            for gate in alphabet:
                nxt_state = apply_state(state, gate)
                if nxt_state not in dist:
                    dist[nxt_state] = depth + 1
                    nxt.append(nxt_state)
        layer = nxt
    return dist


def algebra_product(words: list[tuple[tuple[int, int], int]]) -> tuple[int, int, int, int]:
    """Left-to-right gate application as a 2x2 matrix over the group algebra."""
    # Identity matrix.
    mat = [1, 0, 0, 1]  # masks: 00, 01, 10, 11; bit 0 is the identity element
    for rows, g in words:
        gate = []
        for i in range(W):
            for j in range(W):
                n_ij = (rows[i] >> j) & 1
                # (I + N) + [g] N in characteristic 2. Off-diagonal N_ij contributes [e] + [g].
                if n_ij == 0:
                    gate.append(1 if i == j else 0)
                elif i == j:
                    gate.append(1 << g)
                else:
                    gate.append(1 | (1 << g))
        mat = multiply(gate, mat)
    return tuple(mat)  # type: ignore[return-value]


def multiply(a: list[int], b: list[int]) -> list[int]:
    out = [0, 0, 0, 0]
    for i in range(W):
        for j in range(W):
            mask = 0
            for k in range(W):
                mask ^= convolve(a[i * W + k], b[k * W + j])
            out[i * W + j] = mask
    return out


def convolve(p: int, q: int) -> int:
    out = 0
    pp = p
    while pp:
        bit = pp & -pp
        g = bit.bit_length() - 1
        qq = q
        while qq:
            bit2 = qq & -qq
            h = bit2.bit_length() - 1
            out ^= 1 << mul(g, h)
            qq ^= bit2
        pp ^= bit
    return out


def packed_from_algebra(mat: tuple[int, int, int, int]) -> tuple[int, ...]:
    cols = []
    for j in range(DIM):
        i, h = divmod(j, ORDER)
        # Input basis vector has [h] in register i.
        image = 0
        for row in range(W):
            mask = mat[row * W + i]
            # Coefficient of input [h] is the mask evaluated by right? 
            # (entry * [h]) contributes the left translate of each support element.
            pp = mask
            while pp:
                bit = pp & -pp
                g = bit.bit_length() - 1
                image |= 1 << (row * ORDER + mul(g, h))
                pp ^= bit
        cols.append(image)
    return tuple(cols)


def conjugation_closed(idems: list[tuple[int, int]]) -> None:
    group = []
    for a in range(2):
        for b in range(2):
            for c in range(2):
                for d in range(2):
                    det = (a * d + b * c) & 1
                    if det == 1:
                        group.append((a | (b << 1), c | (d << 1)))
    if len(group) != 6:
        fail("GL2(F2) order")
    idem_set = set(idems)
    for s0, s1 in group:
        # Columns of S are the two rows we stored as bit pairs (row-major bits).
        # S = [[a, b], [c, d]] with row0 = a|b<<1.
        for rows in idems:
            # M = S^{-1} N S. Over F2, GL2 elements satisfy S^{-1} = det-adjusted adjugate.
            # det=1 so S^{-1} = [[d, b], [c, a]] for [[a,b],[c,d]] in char 2? 
            # adjugate [[d, -b], [-c, a]] = [[d, b], [c, a]] in char 2.
            a = s0 & 1
            b = (s0 >> 1) & 1
            c = s1 & 1
            d = (s1 >> 1) & 1
            invs = (d | (b << 1), c | (a << 1))
            conjugated = conjugate(rows, (s0, s1), invs)
            if conjugated not in idem_set:
                fail("conjugation left the idempotent set")
            # S^{-1} D_N(r) S = D_{S^{-1} N S}(r), as packed regular operators.
            g = R
            left = algebra_product([(rows, g)])
            mid = algebra_product([(conjugated, g)])
            # Compare S^{-1} D S with D_conj by acting on the four group-algebra basis inputs
            # is done in packed form below for every pair, on the identity element only? 
            # Full packed equality:
            packed_left = sandwich(left, (s0, s1), invs)
            packed_mid = packed_from_algebra(mid)  # type: ignore[arg-type]
            if packed_left != packed_mid:
                fail("scalar conjugation does not preserve the paid alphabet")


def conjugate(rows: tuple[int, int], s_rows: tuple[int, int], inv_rows: tuple[int, int]) -> tuple[int, int]:
    def matmul(p, q):
        out = [0, 0]
        for i in range(2):
            val = 0
            for j in range(2):
                bit = 0
                for k in range(2):
                    bit ^= ((p[i] >> k) & 1) & ((q[k] >> j) & 1)
                val |= bit << j
            out[i] = val
        return tuple(out)

    return matmul(matmul(inv_rows, rows), s_rows)  # type: ignore[return-value]


def sandwich(mat: tuple[int, int, int, int], s_rows: tuple[int, int], inv_rows: tuple[int, int]) -> tuple[int, ...]:
    # Build scalar matrices as group-algebra matrices supported at e, then multiply.
    def scalar(rows: tuple[int, int]) -> list[int]:
        out = []
        for i in range(2):
            for j in range(2):
                out.append(1 if (rows[i] >> j) & 1 else 0)
        return out

    sm = scalar(s_rows)
    invm = scalar(inv_rows)
    # inv * mat * s
    mid = multiply(list(mat), sm)
    full = multiply(invm, mid)
    return packed_from_algebra(tuple(full))  # type: ignore[arg-type]


def main() -> None:
    check_group()
    idems = rank_one_idempotents()
    alphabet = gates(idems)
    e00 = (1, 0)
    e11 = (0, 2)
    if e00 not in idems or e11 not in idems:
        fail("coordinate projectors missing")

    one = target((R4, 0))
    two = target((R4, R4))
    square = target((R2, 0))
    ident = pack_identity()

    one_word = [(e00, R)] * 4
    two_word = [(e00, R)] * 4 + [(e11, R)] * 4
    reflection_word = [(e00, R), (e00, S), (e00, R), (e00, S)]
    one_alg = algebra_product(one_word)
    two_alg = algebra_product(two_word)
    reflection_alg = algebra_product(reflection_word)
    if packed_from_algebra(one_alg) != one:
        fail("four rotation calls missed diag([r^4], 1)")
    if packed_from_algebra(two_alg) != two:
        fail("eight rotation calls missed diag([r^4], [r^4])")
    if packed_from_algebra(reflection_alg) != one:
        fail("reflection witness s-side word missed diag([r^4], 1)")
    # The reflection word really uses s: the length-3 prefix must differ.
    if packed_from_algebra(algebra_product(reflection_word[:3])) == one:
        fail("reflection witness does not depend on its last call")

    # Cross-check the packed gate action against the algebra matrix on the witness.
    state = ident
    for rows, g in one_word:
        y = rows[0]
        xbits = tuple(i for i, row in enumerate(rows) if row)
        left = tuple(mul(g, h) for h in range(ORDER))
        state = apply_state(state, (y, xbits, left))
    if state != packed_from_algebra(one_alg):
        fail("packed action disagrees with the group-algebra matrix")
    for rows in idems:
        for g in (R, inv(R), S):
            algebraic = packed_from_algebra(algebra_product([(rows, g)]))
            y = next(row for row in rows if row)
            xbits = tuple(i for i, row in enumerate(rows) if row)
            left = tuple(mul(g, h) for h in range(ORDER))
            if apply_state(ident, (y, xbits, left)) != algebraic:
                fail("packed action disagrees on a non-coordinate gate")

    forward = ball(ident, 4, alphabet)
    if forward.get(square) != 2:
        fail("r^2 target distance")
    if forward.get(one) != 4:
        fail("one-copy distance")
    if two in forward:
        fail("two-copy target appeared by radius 4")
    counts = [sum(1 for d in forward.values() if d == k) for k in range(5)]
    if counts != [1, 18, 213, 2276, 22641]:
        fail("forward ball layer counts " + str(counts))

    backward = ball(two, 4, alphabet)
    back_counts = [sum(1 for d in backward.values() if d == k) for k in range(5)]
    if back_counts != counts:
        fail("inverse symmetry of the ball failed")
    best = None
    for state, dist_f in forward.items():
        dist_b = backward.get(state)
        if dist_b is None:
            continue
        length = dist_f + dist_b
        if best is None or length < best:
            best = length
    if best != 8:
        fail("two-copy minimum " + str(best))

    # Failure controls. These must be rejected.
    controls = 0
    if packed_from_algebra(algebra_product(one_word[:3])) == one:
        fail("deleted call was accepted")
    controls += 1
    mutated = one_word[:-1] + [(e00, S)]
    if packed_from_algebra(algebra_product(mutated)) == one:
        fail("mutated label was accepted")
    controls += 1
    if packed_from_algebra(algebra_product(two_word[:-1])) == two:
        fail("deleted two-copy call was accepted")
    controls += 1
    if (1 | (1 << 1), 1) in idems:
        fail("non-idempotent entered the alphabet")
    controls += 1
    if mul(mul(S, R), S) == inv(R):
        fail("dihedral relation was accepted")
    controls += 1
    if forward.get(square) != 2:
        fail("short positive control missing")
    controls += 1

    conjugation_closed(idems)

    if controls != 6:
        fail("control count")
    print(
        "PASS_SEMIDIHEDRAL_CENTRAL_TWO_ROLE"
        f" one=4 two=8 ball4={len(forward)} gates=18"
        f" layers=1,18,213,2276,22641 controls={controls} no_new_kappa"
    )


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # surface unexpected arithmetic errors as failures
        fail(type(exc).__name__ + ": " + str(exc))
