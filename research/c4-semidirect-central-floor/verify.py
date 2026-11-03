#!/usr/bin/env python3
"""Exact three-role central bills in F2[C4 rtimes C4].

G = <a, b | a^4 = b^4 = e, b a b^{-1} = a^{-1}>.
Elements are a^i b^j = i + 4j for i, j in {0,1,2,3}.
Paid calls are D_N([g]) = I + ([g] + [e]) N for g in {a, b} and every
rank-one idempotent N in M_3(F_2). Equality is in M_3(F_2[G]).

Coordinate bills and proved minima:

    diag([a^2]^3)                         6
    diag([b^2]^3)                         6
    diag([a^2], [b^2], [a^2 b^2])         8
    diag([a^2 b^2], [a^2 b^2], [e])       8

diag([a^2 b^2]^3) has no word of length at most 6. The coordinate word
has length 12, and the symbol lemma excludes every odd length, so its
minimum lies in {8, 10, 12}.
"""

from __future__ import annotations


def fail(message: str) -> None:
    raise SystemExit("FAIL_C4_SEMIDIRECT_CENTRAL " + message)


def mul_semidirect(left: int, right: int) -> int:
    li, lj = left & 3, left >> 2
    ri, rj = right & 3, right >> 2
    sign = 1 if (lj & 1) == 0 else -1
    ni = (li + sign * ri) & 3
    nj = (lj + rj) & 3
    return ni | (nj << 2)


def mul_direct(left: int, right: int) -> int:
    """Control law: the same encoding with trivial action, so ab = ba."""
    li, lj = left & 3, left >> 2
    ri, rj = right & 3, right >> 2
    return ((li + ri) & 3) | (((lj + rj) & 3) << 2)


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
    coeff = (1 << label) ^ 1
    entries = [1 if i == j else 0 for i in range(3) for j in range(3)]
    for pos in range(9):
        if (projector >> pos) & 1:
            entries[pos] ^= coeff
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
    rows = [(matrix >> (3 * i)) & 7 for i in range(3)]
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


def reduce_mod(rows: list[int], mask: int) -> int:
    reduced = mask
    for row in rows:
        pivot = row.bit_length() - 1
        if (reduced >> pivot) & 1:
            reduced ^= row
    return reduced


def element_order(multiply, element: int) -> int:
    seen = 0
    for order in range(1, 17):
        seen = multiply(seen, element)
        if seen == 0:
            return order
    fail("an element order did not close")
    return 0


def chain(multiply, labels: tuple[int, ...]) -> int:
    acc = 0
    for label in labels:
        acc = multiply(acc, label)
    return acc


def target_matrix(diags: tuple[int, int, int]) -> int:
    entries = [1 if i == j else 0 for i in range(3) for j in range(3)]
    for role, element in enumerate(diags):
        entries[3 * role + role] = 1 << element
    return pack(entries)


def coordinate_word(spec: tuple[tuple[int, tuple[int, ...]], ...]) -> list[tuple[int, int]]:
    word = []
    for role, labels in spec:
        projector = projector_bit(role)
        word.extend((label, projector) for label in labels)
    return word


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
    if dims != [15, 13, 10, 6, 3, 1, 0]:
        fail(f"unexpected augmentation dimensions {dims}")
    return powers


def check_group(multiply, inverses: dict[int, int]) -> None:
    for left in range(16):
        for right in range(16):
            for third in range(16):
                if multiply(multiply(left, right), third) != multiply(left, multiply(right, third)):
                    fail("multiplication is not associative")
            if multiply(0, left) != left or multiply(left, 0) != left:
                fail("identity element is not e")
            if multiply(left, inverses[left]) != 0 or multiply(inverses[left], left) != 0:
                fail("recorded inverse is not two-sided")


def shortest(matmul, inverse_factors, factors, layer2, layer3, target: int, limit: int):
    if target in factors:
        return 1
    if limit >= 2 and target in layer2:
        return 2
    if limit >= 3 and target in layer3:
        return 3

    def hit(words, pool) -> bool:
        for word in words:
            state = target
            for index in word:
                state = matmul(inverse_factors[index], state)
            if state in pool:
                return True
        return False

    if limit >= 4 and hit(layer2.values(), layer2):
        return 4
    if limit >= 5 and hit(layer2.values(), layer3):
        return 5
    if limit >= 6 and hit(layer3.values(), layer3):
        return 6
    return None


def main() -> None:
    A, B = 1, 4
    A2, A3 = 2, 3
    B2, B3 = 8, 12
    Z = 10  # a^2 b^2
    inverses = invert_table(mul_semidirect)
    check_group(mul_semidirect, inverses)
    if mul_semidirect(mul_semidirect(B, A), inverses[B]) != A3:
        fail("b a b^{-1} is not a^{-1}")
    if mul_semidirect(A, B) == mul_semidirect(B, A):
        fail("the address group collapsed to an abelian group")
    if B2 == A2 or mul_semidirect(B, B) != B2:
        fail("b^2 collapsed onto a^2")
    orders = [element_order(mul_semidirect, element) for element in range(16)]
    histogram: dict[int, int] = {}
    for order in orders:
        histogram[order] = histogram.get(order, 0) + 1
    if histogram != {1: 1, 2: 3, 4: 12}:
        fail(f"order histogram is {histogram}, not exponent 4 with three involutions")
    if orders[A] != 4 or orders[B] != 4 or orders[A2] != 2 or orders[B2] != 2 or orders[Z] != 2:
        fail("generator or central orders do not match C4 rtimes C4")
    center = [
        element
        for element in range(16)
        if all(mul_semidirect(element, other) == mul_semidirect(other, element) for other in range(16))
    ]
    if center != [0, A2, B2, Z]:
        fail(f"center is {center}, not {{e, a^2, b^2, a^2 b^2}}")
    commutators = {
        mul_semidirect(mul_semidirect(mul_semidirect(left, right), inverses[left]), inverses[right])
        for left in range(16)
        for right in range(16)
    }
    if commutators != {0, A2}:
        fail(f"derived subgroup is {sorted(commutators)}, not {{e, a^2}}")
    if B2 in commutators:
        fail("b^2 lies in the derived subgroup, so this is not the stated semidirect product")
    reachable = {0}
    frontier = [0]
    while frontier:
        current = frontier.pop()
        for step in (A, B):
            nxt = mul_semidirect(current, step)
            if nxt not in reachable:
                reachable.add(nxt)
                frontier.append(nxt)
    if reachable != set(range(16)):
        fail("generators a and b do not exhaust the encoded group")
    lengths = {0: 0}
    queue = [0]
    while queue:
        current = queue.pop(0)
        for step in (A, B):
            nxt = mul_semidirect(current, step)
            if nxt not in lengths:
                lengths[nxt] = lengths[current] + 1
                queue.append(nxt)
    if (lengths[A], lengths[B], lengths[A2], lengths[B2], lengths[Z]) != (1, 1, 2, 2, 4):
        fail(
            "generator lengths are "
            f"{lengths[A], lengths[B], lengths[A2], lengths[B2], lengths[Z]}"
        )
    if chain(mul_semidirect, (A, A)) != A2 or chain(mul_semidirect, (B, B)) != B2:
        fail("aa or bb missed its square")
    if chain(mul_semidirect, (A, A, B, B)) != Z:
        fail("aabb is not a^2 b^2")
    if chain(mul_semidirect, (A, B, A, B)) != B2:
        fail("abab is not b^2 in the semidirect product")
    if chain(mul_direct, (A, B, A, B)) == B2:
        fail("direct-product control still sends abab to b^2")

    amul = algebra(mul_semidirect)
    matmul = make_matmul(amul)
    powers = augmentation_powers(amul)
    delta2 = powers[1]
    if len(powers[0]) - len(delta2) != 2:
        fail("Delta/Delta^2 is not two-dimensional")
    alpha = reduce_mod(delta2, (1 << A) ^ 1)
    beta = reduce_mod(delta2, (1 << B) ^ 1)
    if alpha == 0 or beta == 0 or alpha == beta:
        fail("[a]+1 and [b]+1 are not independent modulo Delta^2")
    for element in range(16):
        i, j = element & 3, element >> 2
        expected = 0
        if i & 1:
            expected ^= alpha
        if j & 1:
            expected ^= beta
        if reduce_mod(delta2, (1 << element) ^ 1) != expected:
            fail(f"class of a^{i} b^{j} is not {i % 2} alpha + {j % 2} beta")

    projectors = idempotents()
    eye = identity()
    call_of = make_call
    factors = []
    inverse_factors = []
    for label in (A, B):
        for projector in projectors:
            factors.append(call_of(label, projector))
            inverse_factors.append(call_of(inverses[label], projector))
    factor_set = set(factors)
    if len(factors) != 56 or len(factor_set) != 56:
        fail("alphabet does not have 56 distinct calls")
    for index, factor in enumerate(factors):
        if matmul(factor, inverse_factors[index]) != eye or matmul(inverse_factors[index], factor) != eye:
            fail("a paid call is not inverted by the inverse label")
    for left in factors:
        left_row = [matmul(left, middle) for middle in factors]
        for middle_index, left_middle in enumerate(left_row):
            for right_index, right in enumerate(factors):
                if matmul(left_middle, right) != matmul(left, matmul(factors[middle_index], right)):
                    fail("paid-call multiplication is not associative")

    layer2: dict[int, tuple[int, int]] = {}
    for i, left in enumerate(factors):
        deviation_left = left ^ eye
        for entry in unpack(deviation_left):
            if not in_space(powers[0], entry):
                fail("a paid deviation leaves the augmentation ideal")
        for j, right in enumerate(factors):
            product = matmul(left, right)
            residue = product ^ eye ^ deviation_left ^ (right ^ eye)
            for entry in unpack(residue):
                if not in_space(delta2, entry):
                    fail("a two-call symbol residue leaves Delta^2")
            layer2.setdefault(product, (i, j))
    layer3: dict[int, tuple[int, int, int]] = {}
    for prefix, (i, j) in layer2.items():
        for k, factor in enumerate(factors):
            layer3.setdefault(matmul(prefix, factor), (i, j, k))
    if (len(layer2), len(layer3)) != (2352, 92374):
        fail(f"unexpected frontier sizes {len(layer2)}, {len(layer3)}")
    for matrix, (i, j, k) in layer3.items():
        residue = matrix ^ eye ^ (factors[i] ^ eye) ^ (factors[j] ^ eye) ^ (factors[k] ^ eye)
        for entry in unpack(residue):
            if not in_space(delta2, entry):
                fail("a three-call symbol residue leaves Delta^2")

    def length_of(diags: tuple[int, int, int], limit: int = 6):
        return shortest(
            matmul,
            inverse_factors,
            factor_set,
            layer2,
            layer3,
            target_matrix(diags),
            limit,
        )

    expected = {
        "a": ((A, A, A), 3),
        "b": ((B, B, B), 3),
        "a2": ((A2, A2, A2), 6),
        "b2": ((B2, B2, B2), 6),
        "one_a2": ((A2, 0, 0), 2),
        "one_b2": ((B2, 0, 0), 2),
        "one_z": ((Z, 0, 0), 4),
        "two_a2": ((A2, A2, 0), 4),
        "mixed": ((A2, B2, Z), 8),
        "two_z": ((Z, Z, 0), 8),
        "z": ((Z, Z, Z), 12),
    }
    found = {}
    for name, (diags, _upper) in expected.items():
        found[name] = length_of(diags)
    for name in ("a", "b", "a2", "b2", "one_a2", "one_b2", "one_z", "two_a2"):
        if found[name] != expected[name][1]:
            fail(f"{name} minimum is {found[name]}, not {expected[name][1]}")
    for name in ("mixed", "two_z", "z"):
        if found[name] is not None:
            fail(f"{name} appeared by length 6 at length {found[name]}")
        residue_ok = True
        matrix = target_matrix(expected[name][0])
        for entry in unpack(matrix ^ eye):
            if not in_space(delta2, entry):
                residue_ok = False
        if not residue_ok:
            fail(f"{name} is not congruent to I modulo Delta^2, so odd lengths remain possible")

    words = {
        "a2": coordinate_word(((0, (A, A)), (1, (A, A)), (2, (A, A)))),
        "b2": coordinate_word(((0, (B, B)), (1, (B, B)), (2, (B, B)))),
        "mixed": coordinate_word(((0, (A, A)), (1, (B, B)), (2, (A, A, B, B)))),
        "two_z": coordinate_word(((0, (A, A, B, B)), (1, (A, A, B, B)))),
        "z": coordinate_word(((0, (A, A, B, B)), (1, (A, A, B, B)), (2, (A, A, B, B)))),
        "abab": coordinate_word(((0, (A, B, A, B)), (1, (A, B, A, B)), (2, (A, B, A, B)))),
    }
    if len(words["a2"]) != 6 or realize(matmul, call_of, words["a2"], eye) != target_matrix((A2, A2, A2)):
        fail("coordinate aa word missed diag([a^2]^3)")
    if len(words["b2"]) != 6 or realize(matmul, call_of, words["b2"], eye) != target_matrix((B2, B2, B2)):
        fail("coordinate bb word missed diag([b^2]^3)")
    if len(words["mixed"]) != 8 or realize(matmul, call_of, words["mixed"], eye) != target_matrix((A2, B2, Z)):
        fail("coordinate mixed word missed diag([a^2],[b^2],[a^2 b^2])")
    if len(words["two_z"]) != 8 or realize(matmul, call_of, words["two_z"], eye) != target_matrix((Z, Z, 0)):
        fail("coordinate two-role word missed diag([a^2 b^2],[a^2 b^2],[e])")
    if len(words["z"]) != 12 or realize(matmul, call_of, words["z"], eye) != target_matrix((Z, Z, Z)):
        fail("coordinate aabb word missed diag([a^2 b^2]^3)")
    if realize(matmul, call_of, words["abab"], eye) != target_matrix((B2, B2, B2)):
        fail("semidirect abab word missed diag([b^2]^3)")

    direct_matmul = make_matmul(algebra(mul_direct))
    if realize(direct_matmul, call_of, words["abab"], eye) == target_matrix((B2, B2, B2)):
        fail("direct-product multiplication still produced diag([b^2]^3)")

    dirty = ((1 << 5) ^ (1 << B), 1 << A2, (1 << Z) ^ (1 << A3))
    triple = target_matrix((A2, A2, A2))
    witnessed = realize(matmul, call_of, words["a2"], eye)
    image = apply_state(amul, triple, dirty)
    if apply_state(amul, witnessed, dirty) != image:
        fail("a^2 witness disagrees on the dirty state")
    expected_coordinates = tuple(amul(1 << A2, coordinate) for coordinate in dirty)
    if image != expected_coordinates:
        fail("diagonal a^2 action does not match left multiplication")
    dropped = realize(matmul, call_of, words["a2"][:-1], eye)
    if dropped == triple or apply_state(amul, dropped, dirty) == image:
        fail("dropped call still matched diag([a^2]^3)")
    swapped = list(words["a2"])
    swapped[0] = (B, swapped[0][1])
    if realize(matmul, call_of, swapped, eye) == triple:
        fail("replacing the first a call by b still matched diag([a^2]^3)")

    synthetic = [(B, 3), (A, 24), (B, 65), (A, 146), (B, 260)]
    if any(projector not in projectors for _, projector in synthetic):
        fail("synthetic word uses a projector outside the alphabet")
    synthetic_matrix = realize(matmul, call_of, synthetic, eye)
    synthetic_length = shortest(
        matmul, inverse_factors, factor_set, layer2, layer3, synthetic_matrix, 6
    )
    if synthetic_length != 5:
        fail(f"synthetic five-call matrix was found at length {synthetic_length}")

    controls = 8
    print(
        "PASS_C4_SEMIDIRECT_CENTRAL "
        "a2=6 b2=6 mixed=8 two_z=8 z_through6=0 z_upper=12 "
        "one_z=4 idempotents=28 calls=56 "
        f"frontier2={len(layer2)} frontier3={len(layer3)} "
        "center=4 derived=2 involutions=3 "
        "aug=15,13,10,6,3,1,0 "
        f"controls={controls} no_new_kappa"
    )


if __name__ == "__main__":
    main()
