#!/usr/bin/env python3
"""Exact three-role lengths in the generator-priced modular group of order 16.

M16 = <a, b | a^8 = e, b^2 = e, b a b = a^5>.
Elements are encoded as a^k = k and a^k b = 8+k for k = 0..7.
Paid calls are D_N([g]) = I + ([g] + [e]) N for g in {a, b} and every
rank-one idempotent N in M_3(F_2). Equality is in M_3(F_2[M16]).

Disjoint generator bills: diag([a^2]^3) costs 6, and both diag([a^3]^3)
and diag([a^5]^3) cost 9. All three minima equal those bills.
"""

from __future__ import annotations

A = 1
B = 8
A2, A3, A4, A5, A6, A7 = 2, 3, 4, 5, 6, 7


def fail(message: str) -> None:
    raise SystemExit("FAIL_M16_GENERATOR_TRIPLE " + message)


def mul_group(left: int, right: int) -> int:
    li, le = left & 7, left >> 3
    ri, re = right & 7, right >> 3
    if le == 0 and re == 0:
        return (li + ri) & 7
    if le == 0 and re == 1:
        return 8 | ((li + ri) & 7)
    if le == 1 and re == 0:
        return 8 | ((li + 5 * ri) & 7)
    return (li + 5 * ri) & 7


def mul_dihedral(left: int, right: int) -> int:
    """Control presentation: b^2 = e and b a b = a^{-1}, not a^5."""
    li, le = left & 7, left >> 3
    ri, re = right & 7, right >> 3
    if le == 0 and re == 0:
        return (li + ri) & 7
    if le == 0 and re == 1:
        return 8 | ((li + ri) & 7)
    if le == 1 and re == 0:
        return 8 | ((li - ri) & 7)
    return (li - ri) & 7


def invert_table(multiply) -> dict[int, int]:
    table = {}
    for element in range(16):
        hits = [other for other in range(16) if multiply(element, other) == 0]
        if len(hits) != 1:
            fail(f"element {element} does not have a unique right inverse")
        table[element] = hits[0]
    return table


def algebra(multiply):
    table = [[multiply(left, right) for right in range(16)] for left in range(16)]

    def amul(left: int, right: int) -> int:
        result = 0
        remaining = left
        while remaining:
            i = (remaining & -remaining).bit_length() - 1
            remaining ^= 1 << i
            row = table[i]
            scan = right
            while scan:
                j = (scan & -scan).bit_length() - 1
                scan ^= 1 << j
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
            row0 = left_entries[3 * i]
            row1 = left_entries[3 * i + 1]
            row2 = left_entries[3 * i + 2]
            for j in range(3):
                acc = amul(row0, right_entries[j])
                acc ^= amul(row1, right_entries[3 + j])
                acc ^= amul(row2, right_entries[6 + j])
                out[3 * i + j] = acc
        return pack(out)

    return matmul


def identity() -> int:
    return pack([1 if i == j else 0 for i in range(3) for j in range(3)])


def make_call(label: int, projector: int) -> int:
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


def check_group(multiply, inverses: dict[int, int]) -> None:
    for left in range(16):
        for right in range(16):
            for third in range(16):
                if multiply(multiply(left, right), third) != multiply(left, multiply(right, third)):
                    fail("multiplication is not associative")
    if any(multiply(0, element) != element or multiply(element, 0) != element for element in range(16)):
        fail("identity element is not e")
    power = 0
    for _ in range(8):
        power = multiply(power, A)
    if power != 0:
        fail("a^8 is not e")
    if multiply(B, B) != 0:
        fail("b^2 is not e")
    if multiply(A, B) == multiply(B, A):
        fail("the address group collapsed to an abelian group")


def check_modular(inverses: dict[int, int]) -> None:
    if mul_group(mul_group(B, A), B) != A5:
        fail("b a b is not a^5")
    orders = []
    for element in range(16):
        seen = 0
        order = 0
        while True:
            order += 1
            seen = mul_group(seen, element)
            if seen == 0:
                break
            if order > 16:
                fail("element order did not close")
        orders.append(order)
    if orders[A] != 8 or orders[B] != 2 or orders[A4] != 2 or orders[A5] != 8:
        fail("generator or power orders do not match M16")
    involutions = [element for element, order in enumerate(orders) if order == 2]
    if involutions != [A4, B, 12]:
        fail(f"involutions are {involutions}, not a^4, b, a^4 b")
    center = [
        element
        for element in range(16)
        if all(mul_group(element, other) == mul_group(other, element) for other in range(16))
    ]
    if center != [0, A2, A4, A6]:
        fail(f"center is {center}, not the cyclic order-4 subgroup")
    commutators = {
        mul_group(mul_group(mul_group(left, right), inverses[left]), inverses[right])
        for left in range(16)
        for right in range(16)
    }
    if commutators != {0, A4}:
        fail(f"derived subgroup is {sorted(commutators)}, not {{e, a^4}}")
    reachable = {0}
    frontier = [0]
    while frontier:
        current = frontier.pop()
        for step in (A, B):
            nxt = mul_group(current, step)
            if nxt not in reachable:
                reachable.add(nxt)
                frontier.append(nxt)
    if reachable != set(range(16)):
        fail("generators a and b do not exhaust the encoded group")


def group_lengths() -> dict[int, int]:
    lengths = {0: 0}
    frontier = [0]
    while frontier:
        current = frontier.pop(0)
        for step in (A, B):
            nxt = mul_group(current, step)
            if nxt not in lengths:
                lengths[nxt] = lengths[current] + 1
                frontier.append(nxt)
    return lengths


def augmentation_powers(amul) -> list[list[int]]:
    delta = rref([(1 << element) ^ 1 for element in range(1, 16)])
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


def reduce_mod_delta2(delta2: list[int], mask: int) -> int:
    reduced = mask
    for row in delta2:
        pivot = row.bit_length() - 1
        if (reduced >> pivot) & 1:
            reduced ^= row
    return reduced


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


def invert_word(matmul, inverse_factors: list[int], word: tuple[int, ...], state: int) -> int:
    for index in word:
        state = matmul(inverse_factors[index], state)
    return state


def realize(matmul, factors_of, word: list[tuple[int, int]], eye: int) -> int:
    state = eye
    for label, projector in word:
        state = matmul(state, factors_of(label, projector))
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


def coordinate_word(labels: tuple[int, ...], roles: tuple[int, ...] = (0, 1, 2)) -> list[tuple[int, int]]:
    word = []
    for role in roles:
        projector = projector_bit(role)
        word.extend((label, projector) for label in labels)
    return word


def check_associativity(matmul, matrices: list[int]) -> None:
    for left in matrices:
        for middle in matrices:
            left_middle = matmul(left, middle)
            for right in matrices:
                if matmul(left_middle, right) != matmul(left, matmul(middle, right)):
                    fail("matrix multiplication of paid or inverse calls is not associative")


def minimal_length(matmul, inverse_factors, sets, layers, target: int, limit: int):
    set1, set2, set3, set4 = sets
    layer2, layer3 = layers
    if target in set1:
        return 1
    if limit >= 2 and target in set2:
        return 2
    if limit >= 3 and target in set3:
        return 3
    if limit >= 4:
        for word in layer2.values():
            if invert_word(matmul, inverse_factors, word, target) in set2:
                return 4
    if limit >= 5:
        for word in layer2.values():
            if invert_word(matmul, inverse_factors, word, target) in set3:
                return 5
    if limit >= 6:
        for word in layer3.values():
            if invert_word(matmul, inverse_factors, word, target) in set3:
                return 6
    if limit >= 7:
        for word in layer3.values():
            if invert_word(matmul, inverse_factors, word, target) in set4:
                return 7
    return None


def main() -> None:
    inverses = invert_table(mul_group)
    check_group(mul_group, inverses)
    check_modular(inverses)
    dihedral_inverses = invert_table(mul_dihedral)
    check_group(mul_dihedral, dihedral_inverses)
    if mul_dihedral(mul_dihedral(B, A), B) != A7:
        fail("dihedral control does not send b a b to a^7")
    lengths = group_lengths()
    expected_lengths = {A: 1, A2: 2, A3: 3, A4: 4, A5: 3, A6: 4, A7: 5, B: 1}
    for element, expected in expected_lengths.items():
        if lengths[element] != expected:
            fail(f"generator length of {element} is {lengths[element]}, expected {expected}")
    if mul_group(mul_group(A, B), mul_group(A, B)) != A6:
        fail("(a b)^2 is not a^6")

    amul = algebra(mul_group)
    matmul = make_matmul(amul)
    powers = augmentation_powers(amul)
    delta2 = powers[1]
    alpha = reduce_mod_delta2(delta2, (1 << A) ^ 1)
    beta = reduce_mod_delta2(delta2, (1 << B) ^ 1)
    if alpha == 0 or beta == 0 or alpha == beta:
        fail("[a]+1 and [b]+1 are not independent modulo Delta^2")
    classes = {
        A: alpha,
        A3: alpha,
        A5: alpha,
        A7: alpha,
        A2: 0,
        A4: 0,
        A6: 0,
        B: beta,
    }
    for element, expected in classes.items():
        got = reduce_mod_delta2(delta2, (1 << element) ^ 1)
        if got != expected:
            fail(f"class of element {element} is {got}, expected {expected}")

    projectors = idempotents()
    eye = identity()
    factors = []
    inverse_factors = []
    for label in (A, B):
        for projector in projectors:
            factors.append(make_call(label, projector))
            inverse_factors.append(make_call(inverses[label], projector))
    if len(factors) != 56:
        fail("alphabet does not have 56 calls")
    for index, factor in enumerate(factors):
        if matmul(factor, inverse_factors[index]) != eye or matmul(inverse_factors[index], factor) != eye:
            fail("a paid call is not inverted by the inverse label")
    check_associativity(matmul, factors)
    check_associativity(matmul, inverse_factors)

    layer2: dict[int, tuple[int, int]] = {}
    for i, left in enumerate(factors):
        for j, right in enumerate(factors):
            product = matmul(left, right)
            cross = product ^ eye ^ (left ^ eye) ^ (right ^ eye)
            for entry in unpack(cross):
                if not in_space(delta2, entry):
                    fail("a two-call cross term leaves Delta^2")
            layer2.setdefault(product, (i, j))
    for matrix, word in layer2.items():
        if invert_word(matmul, inverse_factors, word, matrix) != eye:
            fail("length-2 inverse word does not recover I")
    layer3: dict[int, tuple[int, int, int]] = {}
    for prefix, (i, j) in layer2.items():
        for k, factor in enumerate(factors):
            layer3.setdefault(matmul(prefix, factor), (i, j, k))
    for matrix, word in layer3.items():
        if invert_word(matmul, inverse_factors, word, matrix) != eye:
            fail("length-3 inverse word does not recover I")
    layer4: set[int] = set()
    for prefix in layer3:
        for factor in factors:
            layer4.add(matmul(prefix, factor))
    if (len(layer2), len(layer3), len(layer4)) != (2052, 68955, 2199152):
        fail(
            "unexpected frontier sizes "
            f"{len(layer2)}, {len(layer3)}, {len(layer4)}"
        )

    sets = (set(factors), set(layer2), set(layer3), layer4)
    layers = (layer2, layer3)

    def length_of(diags: tuple[int, int, int], limit: int):
        return minimal_length(matmul, inverse_factors, sets, layers, target_matrix(diags), limit)

    minima = {
        "a": length_of((A, A, A), 3),
        "b": length_of((B, B, B), 3),
        "a2": length_of((A2, A2, A2), 7),
        "a3": length_of((A3, A3, A3), 7),
        "a4": length_of((A4, A4, A4), 7),
        "a5": length_of((A5, A5, A5), 7),
        "a6": length_of((A6, A6, A6), 7),
        "a2_pair": length_of((A2, A2, 0), 4),
        "one_a4": length_of((A4, 0, 0), 4),
        "one_a5": length_of((A5, 0, 0), 3),
    }
    if minima["a"] != 3 or minima["b"] != 3:
        fail(f"generator triples were not found at length 3: {minima['a']}, {minima['b']}")
    if minima["a2"] != 6:
        fail(f"a^2 triple minimum is {minima['a2']}, not 6")
    if minima["a3"] is not None or minima["a5"] is not None:
        fail(f"odd triples appeared by length 7: a3={minima['a3']} a5={minima['a5']}")
    if minima["a4"] is not None or minima["a6"] is not None:
        fail(f"a^4 or a^6 triple appeared by length 7: {minima['a4']}, {minima['a6']}")
    if minima["a2_pair"] != 4 or minima["one_a4"] != 4 or minima["one_a5"] != 3:
        fail("positive length controls did not meet the disjoint bill")

    call_of = make_call
    a2_word = coordinate_word((A, A))
    a3_word = coordinate_word((A, A, A))
    a4_word = coordinate_word((A, A, A, A))
    a5_word = coordinate_word((B, A, B))
    a6_word = coordinate_word((B, A, B, A))
    if len(a2_word) != 6 or realize(matmul, call_of, a2_word, eye) != target_matrix((A2, A2, A2)):
        fail("doubled a coordinate word missed diag([a^2]^3)")
    if len(a3_word) != 9 or realize(matmul, call_of, a3_word, eye) != target_matrix((A3, A3, A3)):
        fail("tripled a coordinate word missed diag([a^3]^3)")
    if len(a4_word) != 12 or realize(matmul, call_of, a4_word, eye) != target_matrix((A4, A4, A4)):
        fail("length-12 aaaa word missed diag([a^4]^3)")
    if len(a5_word) != 9 or realize(matmul, call_of, a5_word, eye) != target_matrix((A5, A5, A5)):
        fail("bab coordinate word missed diag([a^5]^3)")
    if len(a6_word) != 12 or realize(matmul, call_of, a6_word, eye) != target_matrix((A6, A6, A6)):
        fail("length-12 (ab)^2 word missed diag([a^6]^3)")

    dirty = ((1 << A5) ^ (1 << B), 1 << A2, (1 << A4) ^ (1 << 11))
    image = apply_state(amul, target_matrix((A5, A5, A5)), dirty)
    witnessed = apply_state(amul, realize(matmul, call_of, a5_word, eye), dirty)
    if witnessed != image:
        fail("a^5 witness disagrees on the dirty state")
    expected_coordinates = tuple(amul(1 << A5, coordinate) for coordinate in dirty)
    if image != expected_coordinates:
        fail("diagonal a^5 action does not match left multiplication")
    dropped = realize(matmul, call_of, a5_word[:-1], eye)
    if dropped == target_matrix((A5, A5, A5)) or apply_state(amul, dropped, dirty) == image:
        fail("dropped call still matched diag([a^5]^3)")
    swapped = list(a5_word)
    swapped[0] = (A, swapped[0][1])
    if realize(matmul, call_of, swapped, eye) == target_matrix((A5, A5, A5)):
        fail("replacing the first b call by a still matched diag([a^5]^3)")

    broken_amul = algebra(mul_dihedral)
    broken_matmul = make_matmul(broken_amul)
    if realize(broken_matmul, call_of, a5_word, eye) == target_matrix((A5, A5, A5)):
        fail("the dihedral relation still produced diag([a^5]^3)")

    synthetic = [
        (B, 3),
        (A, 24),
        (B, 65),
        (A, 146),
        (B, 260),
        (A, 320),
        (B, 390),
    ]
    if any(projector not in projectors for _, projector in synthetic):
        fail("synthetic word uses a projector outside the alphabet")
    synthetic_matrix = realize(matmul, call_of, synthetic, eye)
    synthetic_length = minimal_length(matmul, inverse_factors, sets, layers, synthetic_matrix, 7)
    if synthetic_length != 7:
        fail(f"synthetic seven-call matrix was found at length {synthetic_length}")

    controls = 7
    print(
        "PASS_M16_GENERATOR_TRIPLE "
        "a2=6 a3=9 a5=9 a4_through7=0 a6_through7=0 "
        "a4_upper=12 a6_upper=12 "
        f"idempotents=28 calls=56 frontier2={len(layer2)} frontier3={len(layer3)} "
        f"frontier4={len(layer4)} center=4 derived=2 "
        f"controls={controls} no_new_kappa"
    )


if __name__ == "__main__":
    main()
