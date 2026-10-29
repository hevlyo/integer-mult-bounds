#!/usr/bin/env python3
"""Exact diagonal tariff for the 21 transvections of GL(3, F2).

Standard library only. Assertions must stay enabled.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREDECESSOR = ROOT / "research" / "bit-three-register-lower-bound" / "README.md"
PREDECESSOR_SHA256 = (
    "c12b33ef388deece0cbf891505a2ce2c0779a0c3a6cf1f0f7f7039bab59cbebd"
)

# Named matrices, row-major. Group law is matrix multiplication over F2.
T1 = (0, 0, 1, 0, 1, 0, 1, 0, 0)  # non-coordinate transvection
R2 = (0, 0, 1, 0, 1, 0, 1, 0, 1)  # rank 2
S = (0, 0, 1, 0, 1, 1, 1, 1, 0)  # order 7, rank 3
R2_FACTORS = (
    T1,
    (1, 0, 1, 0, 1, 0, 0, 0, 1),
)
S_FACTORS = (
    T1,
    (1, 0, 0, 0, 1, 1, 0, 0, 1),
    (1, 1, 0, 0, 1, 0, 0, 0, 1),
)
CYCLE = (0, 0, 1, 1, 0, 0, 0, 1, 0)  # (123) on the standard basis
CYCLE_INV = (0, 1, 0, 0, 0, 1, 1, 0, 0)  # (132)


def demand(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def mat_mul(a, b):
    out = [0] * 9
    for i in range(3):
        for j in range(3):
            acc = 0
            for k in range(3):
                acc ^= a[3 * i + k] & b[3 * k + j]
            out[3 * i + j] = acc
    return tuple(out)


def mat_det(a):
    a0, b, c, d, e, f, g, h, i = a
    return (a0 * (e * i ^ f * h) ^ b * (d * i ^ f * g) ^ c * (d * h ^ e * g)) & 1


def mat_add(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def eye(n=3):
    return tuple(1 if i == j else 0 for i in range(n) for j in range(n))


I3 = eye(3)


def rows_of(flat, width=3):
    return [list(flat[i * width : (i + 1) * width]) for i in range(len(flat) // width)]


def rank_of(flat, width=3):
    rows = rows_of(flat, width)
    height = len(rows)
    rank = 0
    for col in range(width):
        pivot = None
        for row in range(rank, height):
            if rows[row][col]:
                pivot = row
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for row in range(height):
            if row != rank and rows[row][col]:
                rows[row] = [x ^ y for x, y in zip(rows[row], rows[rank])]
        rank += 1
    return rank


def rect_rank(matrix):
    rows = [list(row) for row in matrix]
    if not rows:
        return 0
    height = len(rows)
    width = len(rows[0])
    rank = 0
    for col in range(width):
        pivot = None
        for row in range(rank, height):
            if rows[row][col]:
                pivot = row
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for row in range(height):
            if row != rank and rows[row][col]:
                rows[row] = [x ^ y for x, y in zip(rows[row], rows[rank])]
        rank += 1
    return rank


def displaced_rank(element):
    return rank_of(mat_add(element, I3))


def all_matrices():
    for mask in range(1 << 9):
        yield tuple((mask >> (8 - bit)) & 1 for bit in range(9))


def f2_mul(left, right):
    n = len(left)
    mid = len(right)
    width = len(right[0])
    out = [[0] * width for _ in range(n)]
    for i in range(n):
        for k in range(mid):
            if left[i][k]:
                for j in range(width):
                    out[i][j] ^= right[k][j]
    return out


def add_identity(update):
    size = len(update)
    return [
        [update[i][j] ^ (1 if i == j else 0) for j in range(size)] for i in range(size)
    ]


def kron_update(projector, displacement):
    """Block matrix of N ⊗ (g+I), role index slow."""
    width = len(projector)
    dim = 3
    big = [[0] * (width * dim) for _ in range(width * dim)]
    for i in range(width):
        for j in range(width):
            if not projector[i][j]:
                continue
            for a in range(dim):
                for b in range(dim):
                    big[i * dim + a][j * dim + b] = displacement[3 * a + b]
    return big


def block_diag(elements):
    width = len(elements)
    dim = 3
    size = width * dim
    big = [[0] * size for _ in range(size)]
    for index, element in enumerate(elements):
        for a in range(dim):
            for b in range(dim):
                big[index * dim + a][index * dim + b] = element[3 * a + b]
    return big


def idempotents(width):
    found = []
    for x_mask in range(1 << width):
        x = [(x_mask >> bit) & 1 for bit in range(width)]
        if not any(x):
            continue
        for y_mask in range(1 << width):
            y = [(y_mask >> bit) & 1 for bit in range(width)]
            dot = 0
            for bit in range(width):
                dot ^= x[bit] & y[bit]
            if dot != 1:
                continue
            matrix = tuple(
                tuple(x[i] & y[j] for j in range(width)) for i in range(width)
            )
            found.append(matrix)
    return found


def coordinate_generators():
    gens = []
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            entries = list(I3)
            entries[3 * i + j] = 1
            gens.append(tuple(entries))
    return gens


def cayley_distances(elements, generators, mul_index):
    start = elements.index(I3)
    dist = [-1] * len(elements)
    dist[start] = 0
    queue = [start]
    head = 0
    while head < len(queue):
        current = queue[head]
        head += 1
        for gen in generators:
            nxt = mul_index[gen][current]
            if dist[nxt] < 0:
                dist[nxt] = dist[current] + 1
                queue.append(nxt)
    return dist


def ga_mul(left, right, mul_index):
    if left == 0 or right == 0:
        return 0
    out = 0
    a = left
    while a:
        bit = a & -a
        i = bit.bit_length() - 1
        a ^= bit
        b = right
        while b:
            rbit = b & -b
            j = rbit.bit_length() - 1
            b ^= rbit
            out ^= 1 << mul_index[i][j]
    return out


def call_matrix(projector, label, identity_index, mul_index):
    width = len(projector)
    ge = (1 << label) ^ (1 << identity_index)
    matrix = [[0] * width for _ in range(width)]
    for i in range(width):
        matrix[i][i] = 1 << identity_index
        for j in range(width):
            if projector[i][j]:
                matrix[i][j] ^= ge
    return matrix


def call_identity(width, identity_index):
    return [
        [1 << identity_index if i == j else 0 for j in range(width)]
        for i in range(width)
    ]


def multiply_from(factors, identity_index, mul_index, width):
    """Right-multiply calls. Each factor is (projector, label index)."""
    acc = call_identity(width, identity_index)
    if not factors:
        return acc
    for projector, label in factors:
        step = call_matrix(projector, label, identity_index, mul_index)
        acc = mmul(acc, step, mul_index)
    return acc


def mmul(left, right, mul_index):
    width = len(left)
    out = [[0] * width for _ in range(width)]
    for i in range(width):
        for k in range(width):
            acc = 0
            for j in range(width):
                acc ^= ga_mul(left[i][j], right[j][k], mul_index)
            out[i][k] = acc
    return out


def diagonal_target(labels, identity_index, width):
    target = call_identity(width, identity_index)
    for i, label in enumerate(labels):
        target[i][i] = 1 << label
    for i in range(len(labels), width):
        target[i][i] = 1 << identity_index
    return target


def axis(width, index):
    rows = [[0] * width for _ in range(width)]
    rows[index][index] = 1
    return tuple(tuple(row) for row in rows)


def find_factorization(target_index, rank, trans_indices, mul_index):
    if rank == 0:
        return []
    if rank == 1:
        if target_index not in trans_indices:
            return None
        return [target_index]
    trans = list(trans_indices)
    if rank == 2:
        for first in trans:
            rest = mul_index[first][target_index]
            # first is an involution, so first * rest = target iff rest = first * target.
            if rest in trans_indices and mul_index[first][rest] == target_index:
                return [first, rest]
        return None
    if rank == 3:
        # prod = first*second need not be an involution, so search the third factor.
        for first in trans:
            for second in trans:
                prod = mul_index[first][second]
                for third in trans:
                    if mul_index[prod][third] == target_index:
                        return [first, second, third]
        return None
    raise RuntimeError("unexpected rank")


def represented_product(calls):
    acc = None
    for update in calls:
        step = add_identity(update)
        acc = step if acc is None else f2_mul(acc, step)
    return acc


def main():
    demand(not os.environ.get("PYTHONOPTIMIZE"), "PYTHONOPTIMIZE must be unset")
    demand(__debug__, "assertions disabled; refuse an optimized run")
    digest = hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest()
    demand(digest == PREDECESSOR_SHA256, "predecessor README hash drifted")

    elements = [mat for mat in all_matrices() if mat_det(mat) == 1]
    demand(len(elements) == 168, "GL(3,F2) count")
    index = {mat: i for i, mat in enumerate(elements)}
    identity_index = index[I3]
    mul_index = [
        [index[mat_mul(elements[i], elements[j])] for j in range(168)]
        for i in range(168)
    ]
    ranks = [displaced_rank(mat) for mat in elements]
    trans = [i for i, rank in enumerate(ranks) if rank == 1]
    trans_set = set(trans)
    demand(len(trans) == 21, "transvection count")

    order_hist = {1: 0, 2: 0, 3: 0, 4: 0, 7: 0}
    for i, mat in enumerate(elements):
        power = mat
        order = None
        for step in range(1, 8):
            if power == I3:
                order = step
                break
            power = mat_mul(power, mat)
        demand(order in order_hist, "unexpected element order " + str(order))
        order_hist[order] += 1
        if order == 1:
            demand(ranks[i] == 0, "identity rank")
        elif order == 2:
            demand(ranks[i] == 1, "involution rank")
            demand(mat_mul(mat, mat) == I3, "involution square")
        elif order in (3, 4):
            demand(ranks[i] == 2, "order 3 or 4 rank")
        else:
            demand(ranks[i] == 3, "order 7 rank")
    demand(order_hist == {1: 1, 2: 21, 3: 56, 4: 42, 7: 48}, "order census")

    factorizations = []
    for i, rank in enumerate(ranks):
        found = find_factorization(i, rank, trans_set, mul_index)
        demand(found is not None and len(found) == rank, "missing transvection factorization")
        product = identity_index
        for factor in found:
            demand(factor in trans_set, "factor leaves the alphabet")
            product = mul_index[product][factor]
        demand(product == i, "factorization multiplies to the element")
        if rank >= 2:
            shorter = find_factorization(i, rank - 1, trans_set, mul_index)
            # rank-1 search returns the element itself only when it is a transvection.
            if rank - 1 == 1:
                demand(i not in trans_set, "higher rank element listed as a transvection")
            elif rank - 1 == 2:
                demand(shorter is None, "rank-3 element is a product of two transvections")
        factorizations.append(found)

    # Hardcoded witness factors are one legal factorization, not a unique word.
    for element, factors in (
        (T1, (T1,)),
        (R2, R2_FACTORS),
        (S, S_FACTORS),
    ):
        product = I3
        for factor in factors:
            demand(displaced_rank(factor) == 1, "hardcoded factor rank")
            product = mat_mul(product, factor)
        demand(product == element, "hardcoded factorization")
        demand(len(factors) == displaced_rank(element), "hardcoded length")

    generators = coordinate_generators()
    demand(len(generators) == 6, "coordinate alphabet size")
    gen_index = [index[gen] for gen in generators]
    demand(all(i in trans_set for i in gen_index), "coordinate generators are transvections")
    distances = cayley_distances(elements, gen_index, mul_index)
    hist = {}
    for value in distances:
        hist[value] = hist.get(value, 0) + 1
    demand(
        hist == {0: 1, 1: 6, 2: 24, 3: 51, 4: 60, 5: 24, 6: 2},
        "coordinate distance histogram " + str(hist),
    )
    controls = 0
    demand(distances[index[T1]] == 3, "T1 coordinate length")
    controls += 1
    demand(distances[index[S]] == 4, "S coordinate length")
    controls += 1
    demand(distances[index[CYCLE]] == 6, "3-cycle coordinate length")
    demand(distances[index[CYCLE_INV]] == 6, "inverse 3-cycle coordinate length")
    controls += 1
    demand(displaced_rank(CYCLE) == 2 and displaced_rank(CYCLE_INV) == 2, "3-cycle rank")

    projectors = idempotents(3)
    demand(len(projectors) == 28, "three-register idempotent count")
    for projector in projectors:
        flat = tuple(bit for row in projector for bit in row)
        demand(rank_of(flat) == 1, "idempotent rank")
        square = f2_mul(projector, projector)
        demand(square == [list(row) for row in projector], "idempotent square")
    rank_two = [[1, 0, 0], [0, 1, 0], [0, 0, 0]]
    demand(f2_mul(rank_two, rank_two) == rank_two, "rank-two control square")
    demand(rect_rank(rank_two) == 2, "rank-two control rank")
    demand(
        tuple(tuple(row) for row in rank_two) not in set(projectors),
        "rank-two idempotent excluded",
    )
    controls += 1

    for label in trans:
        displacement = mat_add(elements[label], I3)
        demand(rank_of(displacement) == 1, "label displacement")
        for projector in projectors:
            update = kron_update(projector, displacement)
            demand(rect_rank(update) == 1, "paid call image rank")

    labels = [index[T1], index[R2], index[S]]
    roles = []
    represented_steps = []
    for role, label in enumerate(labels):
        projector = axis(3, role)
        for factor in factorizations[label]:
            roles.append((projector, factor))
            represented_steps.append(
                kron_update(projector, mat_add(elements[factor], I3))
            )
    demand(len(roles) == 6, "witness length")
    word = multiply_from(roles, identity_index, mul_index, 3)
    target = diagonal_target(labels, identity_index, 3)
    demand(word == target, "three-register witness")
    image = represented_product(represented_steps)
    demand(image == block_diag([T1, R2, S]), "representation sends the witness to the blocks")
    demand(rect_rank([[image[i][j] ^ (1 if i == j else 0) for j in range(9)] for i in range(9)]) == 6,
           "target image rank")

    short = multiply_from(roles[:-1], identity_index, mul_index, 3)
    demand(short != target, "omitted last factor")
    controls += 1
    prefix_image = represented_product(represented_steps[:-1])
    prefix_rank = rect_rank(
        [[prefix_image[i][j] ^ (1 if i == j else 0) for j in range(9)] for i in range(9)]
    )
    demand(prefix_rank <= 5, "five-call image rank")
    controls += 1

    replacement = list(roles)
    other = next(item for item in trans if item != roles[-1][1])
    replacement[-1] = (roles[-1][0], other)
    demand(
        multiply_from(replacement, identity_index, mul_index, 3) != target,
        "replaced last factor",
    )
    controls += 1

    reversed_s = I3
    for factor in reversed(S_FACTORS):
        reversed_s = mat_mul(reversed_s, factor)
    demand(reversed_s != S, "opposite factor order is a different product")
    controls += 1

    # Every width-2 diagonal target: monomial concatenation agrees with the
    # general group-algebra product, and the length equals the rank sum.
    checked_pairs = 0
    for left in range(168):
        for right in range(168):
            factors = []
            for role, element in enumerate((left, right)):
                projector = axis(2, role)
                for factor in factorizations[element]:
                    factors.append((projector, factor))
            got = multiply_from(factors, identity_index, mul_index, 2)
            expect = diagonal_target([left, right], identity_index, 2)
            demand(got == expect, "width-2 diagonal identity")
            demand(len(factors) == ranks[left] + ranks[right], "width-2 length")
            checked_pairs += 1
    demand(checked_pairs == 168 * 168, "pair census count")

    # Both distance-6 coordinate 3-cycles have transvection length 2.
    for cycle in (CYCLE, CYCLE_INV):
        demand(len(factorizations[index[cycle]]) == 2, "3-cycle transvection length")

    demand(controls == 8, "control count")
    print(
        "PASS_GL3_TRANSVECTION_DIAGONAL_FLOOR "
        f"elements=168 transvections=21 witness_calls=6 target_rank=6 "
        f"coordinate_length_S=4 coordinate_length_3cycle=6 "
        f"width2_pairs={checked_pairs} controls={controls} no_new_kappa"
    )


if __name__ == "__main__":
    main()
