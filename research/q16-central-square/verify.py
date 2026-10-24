#!/usr/bin/env python3
"""Exact three-role lengths in the generator-priced quaternion model.

Q16 = <x, y | x^8 = e, y^2 = x^4, y x y^{-1} = x^{-1}>.
Paid calls are D_N([g]) = I + ([g] + [e]) N for g in {x, y} and every
rank-one idempotent N in M_3(F_2). Equality is in M_3(F_2[Q16]).

The disjoint bills of diag([x^2]^3) and diag([x^4]^3) are both 6.
Both minima are exactly 6, so register mixing does not undercut them.
"""

from __future__ import annotations

X = 1
Y = 8
X2 = 2
X4 = 4
X6 = 6


def fail(message: str) -> None:
    raise SystemExit("FAIL_Q16_CENTRAL_SQUARE " + message)


def mul_group(a: int, b: int) -> int:
    ak, ae = a & 7, a >> 3
    bk, be = b & 7, b >> 3
    if ae == 0 and be == 0:
        return (ak + bk) & 7
    if ae == 0 and be == 1:
        return 8 | ((ak + bk) & 7)
    if ae == 1 and be == 0:
        return 8 | ((ak - bk) & 7)
    return (ak - bk + 4) & 7


def mul_group_square_trivial(a: int, b: int) -> int:
    """Same generators with the wrong relation y^2 = e."""
    ak, ae = a & 7, a >> 3
    bk, be = b & 7, b >> 3
    if ae == 0 and be == 0:
        return (ak + bk) & 7
    if ae == 0 and be == 1:
        return 8 | ((ak + bk) & 7)
    if ae == 1 and be == 0:
        return 8 | ((ak - bk) & 7)
    return (ak - bk) & 7


def invert_table(multiply) -> dict[int, int]:
    table = {}
    for g in range(16):
        hits = [h for h in range(16) if multiply(g, h) == 0]
        if len(hits) != 1:
            fail(f"element {g} does not have a unique right inverse")
        table[g] = hits[0]
    return table


def algebra(multiply):
    table = [[multiply(a, b) for b in range(16)] for a in range(16)]

    def amul(p: int, q: int) -> int:
        result = 0
        left = p
        while left:
            i = (left & -left).bit_length() - 1
            left ^= 1 << i
            right = q
            row = table[i]
            while right:
                j = (right & -right).bit_length() - 1
                right ^= 1 << j
                result ^= 1 << row[j]
        return result

    return amul


def pack(entries: list[int]) -> int:
    value = 0
    for index, entry in enumerate(entries):
        value |= (entry & 0xFFFF) << (16 * index)
    return value


def unpack(value: int) -> list[int]:
    return [(value >> (16 * index)) & 0xFFFF for index in range(9)]


def make_matmul(amul):
    def matmul(left: int, right: int) -> int:
        left_entries = unpack(left)
        right_entries = unpack(right)
        out = [0] * 9
        for i in range(3):
            row = left_entries[3 * i : 3 * i + 3]
            for j in range(3):
                acc = amul(row[0], right_entries[j])
                acc ^= amul(row[1], right_entries[3 + j])
                acc ^= amul(row[2], right_entries[6 + j])
                out[3 * i + j] = acc
        return pack(out)

    return matmul


def identity() -> int:
    return pack([1 if i == j else 0 for i in range(3) for j in range(3)])


def make_call(amul_unused, label: int, projector: int) -> int:
    del amul_unused
    alpha = (1 << label) ^ 1
    entries = [1 if i == j else 0 for i in range(3) for j in range(3)]
    for pos in range(9):
        if (projector >> pos) & 1:
            entries[pos] ^= alpha
    return pack(entries)


def f2_mul(left: int, right: int) -> int:
    out = 0
    for i in range(3):
        for j in range(3):
            bit = 0
            for k in range(3):
                bit ^= ((left >> (3 * i + k)) & 1) & ((right >> (3 * k + j)) & 1)
            out |= bit << (3 * i + j)
    return out


def f2_rank(matrix: int) -> int:
    rows = [((matrix >> (3 * i)) & 7) for i in range(3)]
    rank = 0
    for col in range(3):
        pivot = next((r for r in range(rank, 3) if (rows[r] >> col) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for r in range(3):
            if r != rank and (rows[r] >> col) & 1:
                rows[r] ^= rows[rank]
        rank += 1
    return rank


def f2_trace(matrix: int) -> int:
    return ((matrix >> 0) & 1) ^ ((matrix >> 4) & 1) ^ ((matrix >> 8) & 1)


def projector_bit(role: int) -> int:
    return 1 << (4 * role)


def rref(vectors: list[int]) -> list[int]:
    rows: list[int] = []
    for vector in vectors:
        reduced = vector
        for row in rows:
            pivot = row.bit_length() - 1
            if (reduced >> pivot) & 1:
                reduced ^= row
        if reduced:
            pivot = reduced.bit_length() - 1
            rows = [row ^ reduced if (row >> pivot) & 1 else row for row in rows]
            rows.append(reduced)
    return rows


def in_space(rows: list[int], vector: int) -> bool:
    reduced = vector
    for row in rows:
        pivot = row.bit_length() - 1
        if (reduced >> pivot) & 1:
            reduced ^= row
    return reduced == 0


def valuation(powers: list[list[int]], mask: int) -> int:
    level = 0
    for rows in powers:
        if in_space(rows, mask):
            level += 1
        else:
            break
    return level


def check_group() -> dict[int, int]:
    for a in range(16):
        for b in range(16):
            for c in range(16):
                if mul_group(mul_group(a, b), c) != mul_group(a, mul_group(b, c)):
                    fail("Q16 multiplication is not associative")
    if any(mul_group(0, g) != g or mul_group(g, 0) != g for g in range(16)):
        fail("identity element is not e")
    inverses = invert_table(mul_group)
    power = 0
    for _ in range(8):
        power = mul_group(power, X)
    if power != 0:
        fail("x^8 is not e")
    if mul_group(Y, Y) != X4:
        fail("y^2 is not x^4")
    if mul_group(mul_group(Y, X), inverses[Y]) != inverses[X]:
        fail("y x y^{-1} is not x^{-1}")
    if mul_group(Y, X) == mul_group(X, Y):
        fail("Q16 collapsed to an abelian group")
    orders = []
    for g in range(16):
        seen = 0
        order = 0
        while True:
            order += 1
            seen = mul_group(seen, g)
            if seen == 0:
                break
            if order > 16:
                fail("element order did not close")
        orders.append(order)
    if orders[X4] != 2 or orders.count(2) != 1:
        fail("x^4 is not the unique order-2 element")
    if orders[Y] != 4 or orders[X] != 8:
        fail("generator orders are not 8 and 4")
    reachable = {0}
    frontier = [0]
    while frontier:
        current = frontier.pop()
        for step in (X, Y):
            nxt = mul_group(current, step)
            if nxt not in reachable:
                reachable.add(nxt)
                frontier.append(nxt)
    if reachable != set(range(16)):
        fail("generators x and y do not exhaust Q16")
    return inverses


def group_lengths() -> dict[int, int]:
    lengths = {0: 0}
    frontier = [0]
    while frontier:
        current = frontier.pop(0)
        if lengths[current] >= 8:
            continue
        for step in (X, Y):
            nxt = mul_group(current, step)
            if nxt not in lengths:
                lengths[nxt] = lengths[current] + 1
                frontier.append(nxt)
    return lengths


def augmentation_powers(amul) -> list[list[int]]:
    delta = rref([(1 << g) ^ 1 for g in range(1, 16)])
    if len(delta) != 15:
        fail("augmentation ideal is not 15-dimensional")
    powers = [delta]
    current = delta
    for _ in range(8):
        products = [amul(left, right) for left in current for right in delta]
        current = rref(products)
        powers.append(current)
        if not current:
            break
    dims = [len(rows) for rows in powers]
    if dims != [15, 13, 11, 9, 7, 5, 3, 1, 0]:
        fail(f"unexpected augmentation dimensions {dims}")
    return powers


def idempotents() -> list[int]:
    found = []
    for column in range(1, 8):
        for row in range(1, 8):
            if bin(column & row).count("1") & 1:
                matrix = 0
                for i in range(3):
                    for j in range(3):
                        if (column >> i) & 1 and (row >> j) & 1:
                            matrix |= 1 << (3 * i + j)
                found.append(matrix)
    found = sorted(set(found))
    if len(found) != 28:
        fail(f"expected 28 rank-one idempotents, found {len(found)}")
    scanned = []
    for matrix in range(512):
        if f2_mul(matrix, matrix) == matrix and f2_rank(matrix) == 1:
            scanned.append(matrix)
    if scanned != found:
        fail("rank-one idempotent scan does not match the xy^T list")
    for matrix in found:
        if f2_trace(matrix) != 1:
            fail("a rank-one idempotent has trace other than 1")
    rank_two = projector_bit(0) | projector_bit(1)
    if f2_rank(rank_two) != 2 or rank_two in found:
        fail("rank-2 matrix E00+E11 was admitted as a rank-one idempotent")
    return found


def target_matrix(diags: tuple[int, int, int]) -> int:
    entries = [1 if i == j else 0 for i in range(3) for j in range(3)]
    for role, element in enumerate(diags):
        entries[3 * role + role] = 1 << element
    return pack(entries)


def apply_word(matmul, factors: list[int], state: int) -> int:
    for factor in factors:
        state = matmul(state, factor)
    return state


def invert_word(matmul, inverse_factors: list[int], word: tuple[int, ...], state: int) -> int:
    # A = C_i C_j means A^{-1} = C_j^{-1} C_i^{-1}. Left-multiplying the inverse
    # factors in forward word order composes to that product.
    for index in word:
        state = matmul(inverse_factors[index], state)
    return state


def build_layers(matmul, factors: list[int], inverse_factors: list[int], eye: int):
    for index, factor in enumerate(factors):
        if matmul(factor, inverse_factors[index]) != eye or matmul(inverse_factors[index], factor) != eye:
            fail("a paid call is not inverted by the inverse label")
    layer2: dict[int, tuple[int, int]] = {}
    for i, left in enumerate(factors):
        for j, right in enumerate(factors):
            product = matmul(left, right)
            layer2.setdefault(product, (i, j))
    for matrix, word in layer2.items():
        if invert_word(matmul, inverse_factors, word, matrix) != eye:
            fail("length-2 inverse word does not recover I")
        rebuilt = apply_word(matmul, [factors[index] for index in word], eye)
        if rebuilt != matrix:
            fail("stored length-2 word does not rebuild its matrix")
    layer3: dict[int, tuple[int, int, int]] = {}
    for prefix, (i, j) in layer2.items():
        for k, factor in enumerate(factors):
            product = matmul(prefix, factor)
            layer3.setdefault(product, (i, j, k))
    for matrix, word in layer3.items():
        if invert_word(matmul, inverse_factors, word, matrix) != eye:
            fail("length-3 inverse word does not recover I")
    return layer2, layer3


def shortest(matmul, factors, inverse_factors, layer2, layer3, diags: tuple[int, int, int], limit: int):
    eye = identity()
    target = target_matrix(diags)
    if target == eye:
        return 0
    for index, factor in enumerate(factors):
        if factor == target:
            return 1
    if limit >= 2 and target in layer2:
        return 2
    if limit >= 3 and target in layer3:
        return 3
    if limit >= 4:
        for matrix, word in layer2.items():
            if invert_word(matmul, inverse_factors, word, target) in layer2:
                return 4
    if limit >= 5:
        for matrix, word in layer2.items():
            if invert_word(matmul, inverse_factors, word, target) in layer3:
                return 5
    if limit >= 6:
        for matrix, word in layer3.items():
            if invert_word(matmul, inverse_factors, word, target) in layer3:
                return 6
    return None


def hit_count(matmul, inverse_factors, layer, diags: tuple[int, int, int]) -> int:
    target = target_matrix(diags)
    hits = 0
    for word in layer.values():
        if invert_word(matmul, inverse_factors, word, target) in layer:
            hits += 1
    return hits


def coordinate_word(label: int, repeats: int, roles: tuple[int, ...] = (0, 1, 2)) -> list[tuple[int, int]]:
    word = []
    for role in roles:
        word.extend((label, projector_bit(role)) for _ in range(repeats))
    return word


def realize(call_of, matmul, word: list[tuple[int, int]], eye: int) -> int:
    state = eye
    for label, projector in word:
        state = matmul(state, call_of(label, projector))
    return state


def apply_state(amul, matrix: int, vector: tuple[int, int, int]) -> tuple[int, int, int]:
    entries = unpack(matrix)
    out = []
    for row in range(3):
        acc = 0
        for col in range(3):
            acc ^= amul(entries[3 * row + col], vector[col])
        out.append(acc)
    return tuple(out)


def main() -> None:
    inverses = check_group()
    lengths = group_lengths()
    if (lengths[X2], lengths[X4], lengths[X6]) != (2, 2, 4):
        fail(f"unexpected generator lengths {lengths[X2], lengths[X4], lengths[X6]}")
    amul = algebra(mul_group)
    matmul = make_matmul(amul)
    powers = augmentation_powers(amul)
    expected_values = {X: 1, X2: 2, X4: 4, X6: 2, Y: 1}
    for element, expected in expected_values.items():
        got = valuation(powers, (1 << element) ^ 1)
        if got != expected:
            fail(f"valuation of element {element} is {got}, expected {expected}")
    quotient = powers[1]
    x_class = (1 << X) ^ 1
    y_class = (1 << Y) ^ 1
    if in_space(quotient, x_class) or in_space(quotient, y_class) or in_space(quotient, x_class ^ y_class):
        fail("[x]+1 and [y]+1 are not independent modulo Delta^2")
    if len(powers[0]) - len(powers[1]) != 2:
        fail("Delta/Delta^2 is not two-dimensional")
    for element in (X2, X4, X6):
        if not in_space(powers[1], (1 << element) ^ 1):
            fail(f"[{element}]+1 is outside Delta^2")
    projectors = idempotents()
    eye = identity()
    factors = []
    inverse_factors = []
    for label in (X, Y):
        for projector in projectors:
            factors.append(make_call(None, label, projector))
            inverse_factors.append(make_call(None, inverses[label], projector))
    if len(factors) != 56:
        fail("alphabet does not have 56 calls")
    layer2, layer3 = build_layers(matmul, factors, inverse_factors, eye)

    triple_x2 = (X2, X2, X2)
    triple_x4 = (X4, X4, X4)
    triple_x6 = (X6, X6, X6)
    minima = {
        "x": shortest(matmul, factors, inverse_factors, layer2, layer3, (X, X, X), 3),
        "y": shortest(matmul, factors, inverse_factors, layer2, layer3, (Y, Y, Y), 3),
        "x2": shortest(matmul, factors, inverse_factors, layer2, layer3, triple_x2, 6),
        "x4": shortest(matmul, factors, inverse_factors, layer2, layer3, triple_x4, 6),
        "x6": shortest(matmul, factors, inverse_factors, layer2, layer3, triple_x6, 6),
        "x2_pair": shortest(matmul, factors, inverse_factors, layer2, layer3, (X2, X2, 0), 4),
        "one_x4": shortest(matmul, factors, inverse_factors, layer2, layer3, (X4, 0, 0), 2),
    }
    if minima["x"] != 3 or minima["y"] != 3:
        fail(f"generator triples were not found at length 3: {minima['x']}, {minima['y']}")
    if minima["x2"] != 6 or minima["x4"] != 6:
        fail(f"square minima are {minima['x2']} and {minima['x4']}, not 6")
    if minima["x6"] is not None:
        fail(f"x^6 triple appeared at length {minima['x6']}")
    if minima["x2_pair"] != 4 or minima["one_x4"] != 2:
        fail("positive length controls did not meet the disjoint bill")

    len4_hits = hit_count(matmul, inverse_factors, layer2, triple_x4)
    len4_x2 = hit_count(matmul, inverse_factors, layer2, triple_x2)
    len6_x4 = hit_count(matmul, inverse_factors, layer3, triple_x4)
    len6_x2 = hit_count(matmul, inverse_factors, layer3, triple_x2)
    len6_x6 = hit_count(matmul, inverse_factors, layer3, triple_x6)
    if len4_hits != 0 or len4_x2 != 0 or len6_x6 != 0 or len6_x4 <= 0 or len6_x2 <= 0:
        fail(
            f"hit counts len4_x2={len4_x2} len4_x4={len4_hits} len6_x2={len6_x2} "
            f"len6_x4={len6_x4} len6_x6={len6_x6}"
        )
    diagonal = {projector_bit(role) for role in range(3)}
    pure_y = nondiagonal = 0
    central = target_matrix(triple_x4)
    for word in layer3.values():
        if invert_word(matmul, inverse_factors, word, central) not in layer3:
            continue
        if any(index // 28 != 1 for index in word):
            fail("central length-6 prefix used an x call")
        pure_y += 1
        if any(projectors[index % 28] not in diagonal for index in word):
            nondiagonal += 1
    if pure_y != len6_x4 or nondiagonal != 792:
        fail(f"central prefix profile pure_y={pure_y} nondiagonal={nondiagonal}")

    call_of = lambda label, projector: make_call(None, label, projector)
    x4_word = coordinate_word(Y, 2)
    x2_word = coordinate_word(X, 2)
    x6_word = []
    for role in (0, 1, 2):
        x6_word.extend((X, projector_bit(role)) for _ in range(2))
        x6_word.extend((Y, projector_bit(role)) for _ in range(2))
    if realize(call_of, matmul, x4_word, eye) != target_matrix(triple_x4):
        fail("doubled y coordinate word missed diag([x^4]^3)")
    if realize(call_of, matmul, x2_word, eye) != target_matrix(triple_x2):
        fail("doubled x coordinate word missed diag([x^2]^3)")
    if len(x6_word) != 12 or realize(call_of, matmul, x6_word, eye) != target_matrix(triple_x6):
        fail("length-12 xxyy word missed diag([x^6]^3)")

    dirty = ((1 << 5), (1 << Y), (1 << X2) ^ (1 << Y))
    image = apply_state(amul, target_matrix(triple_x4), dirty)
    if apply_state(amul, realize(call_of, matmul, x4_word, eye), dirty) != image:
        fail("operator witness disagrees on the dirty state")
    dropped = realize(call_of, matmul, x4_word[:-1], eye)
    if dropped == target_matrix(triple_x4) or apply_state(amul, dropped, dirty) == image:
        fail("dropped call still matched the central target")
    swapped = list(x4_word)
    swapped[0] = (X, swapped[0][1])
    if realize(call_of, matmul, swapped, eye) == target_matrix(triple_x4):
        fail("replacing a y call by x still matched the central target")

    broken_amul = algebra(mul_group_square_trivial)
    broken_matmul = make_matmul(broken_amul)
    if mul_group_square_trivial(Y, Y) != 0:
        fail("control relation y^2=e was not installed")
    broken_call = lambda label, projector: make_call(None, label, projector)
    if realize(broken_call, broken_matmul, x4_word, eye) == target_matrix(triple_x4):
        fail("breaking y^2=x^4 still produced the central target")

    controls = 7
    print(
        "PASS_Q16_CENTRAL_SQUARE "
        f"x2=6 x4=6 x6_through6=0 x6_upper=12 "
        f"idempotents=28 calls=56 frontier2={len(layer2)} frontier3={len(layer3)} "
        f"len4=0 len6_x2={len6_x2} len6_x4={len6_x4} len6_x6=0 "
        f"central_nondiagonal_prefixes={nondiagonal} "
        f"group_lengths=2,2,4 controls={controls} no_new_kappa"
    )


if __name__ == "__main__":
    main()
