#!/usr/bin/env python3
"""Exact minimum length of one semidihedral triple-square register word.

Model: G = SD16 = <r, s | r^8 = s^2 = e, s r s = r^3>, three roles, and paid
calls D_N([g]) = I + ([g] + [e]) N for g in {r, s} and every binary rank-one
idempotent N on F2^3. Equality is in M_3(F2[G]), so it is an identity on
arbitrary dirty register states.

The doubled coordinate word has length 6 and equals diag([r^2], [r^2], [r^2]).
No shorter word does. Reflections are in the alphabet and do not reduce it.
"""

from array import array
import sys


def mul(a, b):
    """Group law. Codes 0..7 are r^i and 8..15 are r^i s."""
    ai, bi = a & 7, b & 7
    if a < 8 and b < 8:
        return (ai + bi) & 7
    if a < 8:
        return 8 + ((ai + bi) & 7)
    if b < 8:
        return 8 + ((ai + 3 * bi) & 7)
    return (ai + 3 * bi) & 7


MUL = [[mul(a, b) for b in range(16)] for a in range(16)]
LEFT = []
RIGHT = []
for g in range(16):
    left = array("H")
    right = array("H")
    for mask in range(1 << 16):
        out_left = 0
        out_right = 0
        rest = mask
        while rest:
            bit = (rest & -rest).bit_length() - 1
            out_left ^= 1 << MUL[g][bit]
            out_right ^= 1 << MUL[bit][g]
            rest &= rest - 1
        left.append(out_left)
        right.append(out_right)
    LEFT.append(left)
    RIGHT.append(right)


def times_generator_plus_one(mask, g):
    return mask ^ LEFT[g][mask]


def dot(x, y):
    return bin(x & y).count("1") % 2


IDEMS = [(x, y) for x in range(1, 8) for y in range(8) if dot(x, y) == 1]
EXCLUDED = [(x, y) for x in range(1, 8) for y in range(8) if dot(x, y) == 0]
R = 1
S = 8
OPS = [(label, x, y) for label in (R, S) for x, y in IDEMS]
E11 = (1, 1)
E22 = (2, 2)
E33 = (4, 4)


def identity():
    cols = array("H", [0] * 9)
    cols[0] = cols[4] = cols[8] = 1
    return cols


def apply(cols, op):
    label, x, y = op
    acc = [0, 0, 0]
    for j in range(3):
        if (x >> j) & 1:
            acc[0] ^= cols[j]
            acc[1] ^= cols[3 + j]
            acc[2] ^= cols[6 + j]
    acc = [times_generator_plus_one(entry, label) for entry in acc]
    out = array("H", cols)
    for j in range(3):
        if (y >> j) & 1:
            out[j] ^= acc[0]
            out[3 + j] ^= acc[1]
            out[6 + j] ^= acc[2]
    return out


def word_matrix(word):
    cols = identity()
    for op in word:
        cols = apply(cols, op)
    return cols


def diagonal(mask_a, mask_b, mask_c):
    cols = array("H", [0] * 9)
    cols[0] = mask_a
    cols[4] = mask_b
    cols[8] = mask_c
    return cols


def bit(element):
    return 1 << element


def matmul(left, right):
    out = array("H", [0] * 9)
    for i in range(3):
        for j in range(3):
            acc = 0
            for k in range(3):
                factor = right[3 * k + j]
                entry = left[3 * i + k]
                while factor:
                    g = (factor & -factor).bit_length() - 1
                    acc ^= RIGHT[g][entry]
                    factor &= factor - 1
            out[3 * i + j] = acc
    return out


def linear_rows(cols):
    rows = [0] * 48
    for j in range(3):
        for h in range(16):
            column = j * 16 + h
            for i in range(3):
                rest = cols[3 * i + j]
                while rest:
                    q = (rest & -rest).bit_length() - 1
                    rows[i * 16 + MUL[q][h]] |= 1 << column
                    rest &= rest - 1
    return rows


def invert_rows(rows):
    augmented = [rows[r] | (1 << (48 + r)) for r in range(48)]
    for col in range(48):
        pivot = next((r for r in range(col, 48) if (augmented[r] >> col) & 1), None)
        if pivot is None:
            return None
        if pivot != col:
            augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        pivot_row = augmented[col]
        for r in range(48):
            if r != col and (augmented[r] >> col) & 1:
                augmented[r] ^= pivot_row
    return [augmented[r] >> 48 for r in range(48)]


def matrix_from_rows(rows):
    cols = array("H", [0] * 9)
    for j in range(3):
        column = j * 16
        for i in range(3):
            mask = 0
            for q in range(16):
                if (rows[i * 16 + q] >> column) & 1:
                    mask |= 1 << q
            cols[3 * i + j] = mask
    return cols


def projector_ok(x, y):
    rows = [[((x >> i) & 1) & ((y >> j) & 1) for j in range(3)] for i in range(3)]
    square = [[0] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            square[i][j] = sum(rows[i][k] & rows[k][j] for k in range(3)) & 1
    return rows == square and dot(x, y) == 1


def diagonal_group_word(indexed_calls):
    """Product of diagonal calls (label, role). Independent of the matrix update."""
    acc = [0, 0, 0]
    for label, role in indexed_calls:
        acc[role] = mul(acc[role], label)
    return tuple(acc)


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL " + message)


def shortest_frontiers():
    start = identity()
    parent = {start.tobytes(): (None, None)}
    levels = [ {start.tobytes()} ]
    for _depth in range(3):
        current = set()
        for key in levels[-1]:
            cols = array("H")
            cols.frombytes(key)
            for index, op in enumerate(OPS):
                nxt = apply(cols, op).tobytes()
                if nxt not in parent:
                    parent[nxt] = (key, index)
                    current.add(nxt)
        levels.append(current)
    return levels


def inverses(keys):
    found = {}
    singular = 0
    for key in keys:
        cols = array("H")
        cols.frombytes(key)
        rows = invert_rows(linear_rows(cols))
        if rows is None:
            singular += 1
            continue
        found[key] = matrix_from_rows(rows).tobytes()
    return found, singular


def factor_hits(target, left_keys, right_inverses):
    hits = 0
    for inverse_key in right_inverses.values():
        right = array("H")
        right.frombytes(inverse_key)
        if matmul(target, right).tobytes() in left_keys:
            hits += 1
    return hits


def main():
    require(mul(mul(mul(S, R), R), S) == 6, "conjugation s r^2 s = r^6")
    require(mul(mul(S, R), S) == 3, "semidihedral relation s r s = r^3")
    require(mul(mul(S, R), S) != 7, "this is not the dihedral relation s r s = r^{-1}")
    require(len({mul(a, b) for a in range(16) for b in range(16)}) == 16, "order")
    require(len(IDEMS) == 28 and len(EXCLUDED) == 28, "idempotent count")
    require(all(projector_ok(x, y) for x, y in IDEMS), "idempotent algebra")
    require(not any(projector_ok(x, y) for x, y in EXCLUDED), "trace-zero exclusion")
    require(len(OPS) == 56, "alphabet size")

    triple = [
        (R, *E11), (R, *E11),
        (R, *E22), (R, *E22),
        (R, *E33), (R, *E33),
    ]
    target = diagonal(bit(2), bit(2), bit(2))
    witness = word_matrix(triple)
    require(list(witness) == list(target), "length-6 matrix identity")
    require(
        diagonal_group_word([(R, 0), (R, 0), (R, 1), (R, 1), (R, 2), (R, 2)]) == (2, 2, 2),
        "length-6 diagonal group word",
    )
    square = word_matrix([(R, *E11), (R, *E11)])
    require(list(square) == list(diagonal(bit(2), 1, 1)), "single-coordinate square")
    require(list(word_matrix([(S, *E11), (S, *E11)])) == list(identity()), "reflection square is I")

    conjugation = [(S, *E11), (R, *E11), (R, *E11), (S, *E11)]
    require(
        list(word_matrix(conjugation)) == list(diagonal(bit(6), 1, 1)),
        "reflection realizes r^6",
    )
    require(diagonal_group_word([(S, 0), (R, 0), (R, 0), (S, 0)]) == (6, 0, 0), "group conjugation")
    r4_one = [(R, *E11), (R, *E11), (R, *E11), (R, *E11)]
    require(list(word_matrix(r4_one)) == list(diagonal(bit(4), 1, 1)), "four rotations give r^4")

    dropped = word_matrix(triple[:-1])
    relabeled = word_matrix([(S, *E11), *triple[1:]])
    moved = word_matrix(triple[:-1] + [(R, *E11)])
    require(list(dropped) != list(target), "dropped call")
    require(list(relabeled) != list(target), "reflection substitution")
    require(list(moved) != list(target), "moved projector")

    # Abelianization sums: image in F2[C2 x C2] is I only if both label-sums vanish.
    sum_r = [0] * 9
    for label, x, y in triple:
        require(label == R, "witness uses only rotations")
        for i in range(3):
            for j in range(3):
                sum_r[3 * i + j] ^= ((x >> i) & 1) & ((y >> j) & 1)
    require(sum_r == [0] * 9, "rotation projectors sum to 0")

    dirty = array("H", [bit(5), bit(8), bit(2) ^ bit(8)])
    dirty_matrix = array("H", [0] * 9)
    for i in range(3):
        dirty_matrix[3 * i] = dirty[i]
    require(
        list(matmul(witness, dirty_matrix)) == list(matmul(target, dirty_matrix)),
        "dirty state follows the identity",
    )
    require(
        list(matmul(dropped, dirty_matrix)) != list(matmul(target, dirty_matrix)),
        "dirty state rejects the dropped word",
    )

    levels = shortest_frontiers()
    require([len(level) for level in levels] == [1, 56, 2051, 68899], "shortest frontier sizes")
    exact_two = set()
    for key in levels[1]:
        cols = array("H")
        cols.frombytes(key)
        for op in OPS:
            exact_two.add(apply(cols, op).tobytes())
    require(len(exact_two) == 2052 and identity().tobytes() in exact_two, "exact length-two collapse")
    require(target.tobytes() not in levels[1] | levels[2] | levels[3], "target absent through length 3")
    require(diagonal(bit(6), 1, 1).tobytes() not in levels[1] | levels[2] | levels[3], "r^6 absent through length 3")
    require(diagonal(bit(4), 1, 1).tobytes() not in levels[1] | levels[2] | levels[3], "r^4 absent through length 3")
    triple_r = diagonal(bit(1), bit(1), bit(1))
    require(triple_r.tobytes() in levels[3] and triple_r.tobytes() not in levels[2], "generator triple has length 3")

    inverse_two, singular_two = inverses(levels[2])
    require(singular_two == 0 and len(inverse_two) == 2051, "length-two factors invert")
    sample_key = next(iter(levels[2]))
    sample = array("H")
    sample.frombytes(sample_key)
    sample_inverse = array("H")
    sample_inverse.frombytes(inverse_two[sample_key])
    require(list(matmul(sample, sample_inverse)) == list(identity()), "inverse roundtrip")

    hits4 = factor_hits(target, levels[2], inverse_two)
    hits5 = factor_hits(target, levels[3], inverse_two)
    generator_hits5 = factor_hits(triple_r, levels[3], inverse_two)
    require(hits4 == 0 and hits5 == 0, "no length-4 or length-5 factorization")
    require(generator_hits5 == 196, "length-five sieve sees the generator triple")

    inverse_three, singular_three = inverses(levels[3])
    require(singular_three == 0 and len(inverse_three) == 68899, "length-three factors invert")
    hits6 = factor_hits(target, levels[3], inverse_three)
    r4_hits6 = factor_hits(diagonal(bit(4), bit(4), bit(4)), levels[3], inverse_three)
    r6_hits6 = factor_hits(diagonal(bit(6), bit(6), bit(6)), levels[3], inverse_three)
    require(hits6 == 799, "length-six factorizations of the triple square")
    require(r4_hits6 == 0 and r6_hits6 == 0, "r^4 and r^6 triples absent through length 6")

    r4_triple = []
    r6_triple = []
    for projector in (E11, E22, E33):
        r4_triple.extend((R, *projector) for _ in range(4))
        r6_triple.extend((S, *projector) for _ in range(1))
        r6_triple.extend((R, *projector) for _ in range(2))
        r6_triple.extend((S, *projector) for _ in range(1))
    require(list(word_matrix(r4_triple)) == list(diagonal(bit(4), bit(4), bit(4))), "length-12 r^4 upper bound")
    require(list(word_matrix(r6_triple)) == list(diagonal(bit(6), bit(6), bit(6))), "length-12 r^6 upper bound")

    print(
        "PASS_SD16_TRIPLE_SQUARE length=6 frontier=1,56,2051,68899 "
        "exact2=2052 len4=0 len5=0 len6=799 r4_through6=0 r6_through6=0 "
        "generator_len5_hits=196 rejected=6 no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
