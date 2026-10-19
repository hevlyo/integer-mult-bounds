#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One added total cannot lower one pinned P104 frame-pair copy sum below 56.

Standard library only. Exact integer, F2 and rational arithmetic. Checks use
explicit exceptions, so they stay active under python -O.

The finite premises of PROOF.md are checked here. The quantified real
statement is that written rank-nullity argument, not a search over z.
"""
import itertools
import sys
from fractions import Fraction


def fail(tag, info):
    raise SystemExit("FAIL %s | %s" % (tag, info))


def check(tag, cond, info):
    if not cond:
        fail(tag, info)
    print("PASS %s | %s" % (tag, info), flush=True)


def e8_roots():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                v = [0] * 8
                v[i], v[j] = 2 * si, 2 * sj
                roots.append(tuple(v))
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(tuple(signs))
    return roots


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def ip(x, y):
    value = dot(x, y)
    if value % 4 != 0:
        fail("geometry.ip", "doubled inner product is not divisible by 4")
    return value // 4


def neg(v):
    return tuple(-a for a in v)


def f2_insert(basis, vector):
    while vector:
        pivot = vector.bit_length() - 1
        if pivot in basis:
            vector ^= basis[pivot]
        else:
            basis[pivot] = vector
            return True
    return False


def f2_rank(rows):
    basis = {}
    for row in rows:
        f2_insert(basis, row)
    return len(basis)


def f2_reduce(basis):
    for pivot in list(basis):
        vector = basis[pivot]
        for other in basis:
            if other != pivot and (vector >> other) & 1:
                vector ^= basis[other]
        basis[pivot] = vector


def mask_of(indices):
    mask = 0
    for index in indices:
        mask |= 1 << index
    return mask


def bit(vector, index):
    return (vector >> index) & 1


ROOTS = e8_roots()
LINES = []
SEEN = set()
for root in ROOTS:
    key = root if root > neg(root) else neg(root)
    if key not in SEEN:
        SEEN.add(key)
        LINES.append(root)
NL = len(LINES)
IP = [[ip(LINES[i], LINES[j]) for j in range(NL)] for i in range(NL)]
NROW = [sum(((IP[i][j] + 1) & 1) << j for j in range(NL)) for i in range(NL)]

FRAME0 = []
for block in range(4):
    for sign in (1, -1):
        vector = [0] * 8
        vector[2 * block] = 2
        vector[2 * block + 1] = 2 * sign
        FRAME0.append(LINES.index(tuple(vector)))
P112 = [i for i in range(NL) if i not in set(FRAME0)]
ORTH = {i: mask_of(j for j in P112 if j != i and IP[i][j] == 0) for i in P112}

# First admissible frame and its first cross-frame decoder in this enumeration.
EXPECTED_F1 = (96, 95, 85, 74, 47, 38, 14, 13)
EXPECTED_PAIRS = (
    (1, 13), (26, 85), (27, 74), (44, 47),
    (96, 54), (95, 55), (38, 45), (14, 0),
)
SPECIALS = (
    (1, -1, -1, 0, 0, 0, 0, 2),
    (-1, 0, -1, -1, 2, 0, 0, 0),
    (-1, -1, 0, 1, 0, 2, 0, 0),
    (2, 0, 0, 0, -1, -1, 0, 1),
    (0, 0, 0, -2, 1, -1, 1, 0),
    (0, -1, 1, -1, 0, 0, 2, 0),
    (0, 0, -2, 0, 1, 0, -1, 1),
    (0, -2, 0, 0, 0, 1, 1, 1),
)


def one_solution(frame0, frame1):
    for split in range(256):
        rows = [frame0[j] for j in range(8) if (split >> j) & 1]
        partners = {
            row: [col for col in frame1 if [x for x in rows if IP[col][x]] == [row]]
            for row in rows
        }
        if any(not partners[row] for row in rows):
            continue
        for choice in itertools.product(*[partners[row] for row in rows]):
            if len(set(choice)) != len(rows):
                continue
            used = set(choice)
            rest_cols = [col for col in frame1 if col not in used]
            if len(rest_cols) != 8 - len(rows):
                continue
            rest_rows = [row for row in frame0 if row not in set(rows)]
            partners2 = {
                col: [row for row in rest_rows if [x for x in rest_cols if IP[row][x]] == [col]]
                for col in rest_cols
            }
            if any(not partners2[col] for col in rest_cols):
                continue
            for choice2 in itertools.product(*[partners2[col] for col in rest_cols]):
                if len(set(choice2)) != len(rest_cols):
                    continue
                return tuple(zip(rows, choice)) + tuple(zip(rest_cols, choice2))
    return None


def first_admissible():
    def search(clique, candidates):
        if len(clique) == 8:
            pairs = one_solution(FRAME0, clique)
            if pairs:
                return tuple(clique), pairs
            return None
        remaining = candidates
        while remaining:
            vertex = remaining.bit_length() - 1
            remaining &= ~(1 << vertex)
            found = search(clique + [vertex], candidates & ORTH[vertex] & ((1 << vertex) - 1))
            if found:
                return found
        return None

    for start in P112:
        found = search([start], ORTH[start] & ((1 << start) - 1))
        if found:
            return found
    return None


def rational_rank(rows):
    matrix = [[Fraction(entry) for entry in row] for row in rows]
    rank = 0
    if not matrix:
        return 0
    columns = len(matrix[0])
    for column in range(columns):
        pivot = None
        for row in range(rank, len(matrix)):
            if matrix[row][column] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        for row in range(len(matrix)):
            if row != rank and matrix[row][column] != 0:
                factor = matrix[row][column] / matrix[rank][column]
                matrix[row] = [entry - factor * src for entry, src in zip(matrix[row], matrix[rank])]
        rank += 1
    return rank


def nullspace(rows):
    width = 8
    matrix = [[Fraction(entry) for entry in row] for row in rows]
    pivot_of = {}
    rank = 0
    for column in range(width):
        pivot = None
        for row in range(rank, len(matrix)):
            if matrix[row][column] != 0:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        pivot_of[column] = rank
        for row in range(len(matrix)):
            if row != rank and matrix[row][column] != 0:
                factor = matrix[row][column] / matrix[rank][column]
                matrix[row] = [entry - factor * src for entry, src in zip(matrix[row], matrix[rank])]
        rank += 1
    vectors = []
    for free in [column for column in range(width) if column not in pivot_of]:
        vector = [Fraction(0)] * width
        vector[free] = Fraction(1)
        for column, row in pivot_of.items():
            vector[column] = -matrix[row][free] / matrix[row][column]
        denominator = 1
        for entry in vector:
            denominator = denominator * entry.denominator // __import__("math").gcd(denominator, entry.denominator)
        integers = [int(entry * denominator) for entry in vector]
        scale = 0
        for entry in integers:
            scale = __import__("math").gcd(scale, abs(entry))
        if scale == 0:
            fail("nullspace", "zero kernel vector")
        vectors.append(tuple(entry // scale for entry in integers))
    return vectors


def normalize(vector):
    for entry in vector:
        if entry:
            sign = 1 if entry > 0 else -1
            return tuple(sign * item for item in vector)
    return vector


def pair_rank(row_lines, col_lines):
    if not row_lines or not col_lines:
        return 0
    column_mask = mask_of(col_lines)
    return f2_rank(NROW[row] & column_mask for row in row_lines)


def support_dim(line_ids):
    if not line_ids:
        return 0
    return f2_rank(NROW[line] for line in line_ids)


def main():
    check("A.lines", NL == 120 and len(ROOTS) == 240 and f2_rank(NROW) == 9,
          "120 lines, 240 roots, label rank 9")
    check("A.frame0", len(FRAME0) == 8 and all(IP[a][b] == 0 for a in FRAME0 for b in FRAME0 if a != b),
          "coordinate frame has eight orthogonal lines")

    found = first_admissible()
    if found is None:
        fail("B.frame", "no admissible frame")
    frame1, pairs = found
    check("B.frame", frame1 == EXPECTED_F1 and pairs == EXPECTED_PAIRS,
          "first admissible frame %s and its first decoder" % (list(frame1),))
    check("B.odd-pairs", all(IP[row][col] in (1, -1) for row, col in pairs),
          "every decoder pair has odd inner product")
    live = [i for i in range(NL) if i not in set(FRAME0) and i not in set(frame1)]
    check("B.live", len(live) == 104, "P104 complement has 104 lines")

    readers = []
    sources = []
    signs = []
    for row, col in pairs:
        coupling = IP[row][col]
        readers.append([IP[line][row] for line in live])
        sources.append([2 * coupling * IP[line][col] for line in live])
        signs.append([coupling * IP[line][col] for line in live])
    check("B.entries", all(set(column) <= {-1, 0, 1} for column in readers)
          and all(set(column) <= {-2, 0, 2} for column in sources),
          "readers are in {-1,0,1} and sources are in {-2,0,2}")

    identity = True
    for left in range(104):
        for right in range(104):
            total = sum(readers[j][left] * sources[j][right] for j in range(8))
            if total != 2 * IP[live[left]][live[right]]:
                identity = False
                break
        if not identity:
            break
    check("B.identity", identity, "sum_j x_j y_j^T = 2G on all 104 x 104 live pairs")

    def beta(reader, source):
        row_lines = [live[port] for port, value in enumerate(reader) if value]
        col_lines = [live[port] for port, value in enumerate(source) if value]
        return pair_rank(row_lines, col_lines)

    base_costs = [beta(readers[j], sources[j]) for j in range(8)]
    spans = [support_dim(live[port] for port in range(104) if readers[j][port]) for j in range(8)]
    check("B.base-cost", base_costs == [7] * 8 and spans == [8] * 8 and sum(base_costs) == 56,
          "eight cost-7 terms, each reader label span dimension 8")

    bases = []
    fire = []
    kernel_coeff = []
    for j in range(8):
        basis = {}
        for port, value in enumerate(readers[j]):
            if value:
                f2_insert(basis, NROW[live[port]])
        f2_reduce(basis)
        ordered = [basis[pivot] for pivot in sorted(basis)]
        if len(ordered) != 8:
            fail("C.basis", "reader %d span is %d" % (j, len(ordered)))
        bases.append(ordered)
        masks = []
        for port in range(104):
            mask = 0
            for slot, vector in enumerate(ordered):
                if bit(vector, live[port]):
                    mask |= 1 << slot
            masks.append(mask)
        fire.append(masks)
        equations = [masks[port] for port in range(104) if signs[j][port]]
        reduced = {}
        for equation in equations:
            f2_insert(reduced, equation)
        pivots = set(reduced)
        free = [slot for slot in range(8) if slot not in pivots]
        if len(free) != 1 or len(pivots) != 7:
            fail("C.kernel", "reader %d kernel rank %d" % (j, len(pivots)))
        # One reduced pass is enough: pivots were inserted, then rebuild the vector.
        rows = []
        for equation in equations:
            for row in rows:
                head = row.bit_length() - 1
                if bit(equation, head):
                    equation ^= row
            if equation:
                head = equation.bit_length() - 1
                rows = [row ^ equation if bit(row, head) else row for row in rows]
                rows.append(equation)
        pivot_cols = [row.bit_length() - 1 for row in rows]
        slot = free[0]
        coeff = 1 << slot
        for row, pivot in zip(rows, pivot_cols):
            if bit(row, slot):
                coeff |= 1 << pivot
        kernel_coeff.append(coeff)
    check("C.kernels", len(kernel_coeff) == 8, "each original source has a one-dimensional reader kernel")

    def pattern_data(sign_pattern, sign_table):
        active = [j for j in range(8) if sign_pattern[j]]
        equations = []
        block = {j: slot for slot, j in enumerate(active)}
        for port in range(104):
            for epsilon in (1, -1):
                mask = 0
                for j in active:
                    if sign_table[j][port] * sign_pattern[j] == epsilon:
                        mask |= sign_table_fire(j, port) << (8 * block[j])
                if mask:
                    equations.append(mask)
        return active, equations

    def sign_table_fire(j, port):
        return fire[j][port]

    def rank_of(equations, width):
        basis = {}
        for equation in equations:
            f2_insert(basis, equation)
        return len(basis), width - len(basis)

    def satisfies(equations, coeff):
        for equation in equations:
            if bin(equation & coeff).count("1") % 2:
                return False
        return True

    corank_matches = 0
    patterns = 0
    for signs_a in itertools.product((-1, 0, 1), repeat=8):
        if sum(entry != 0 for entry in signs_a) < 2:
            continue
        if next(entry for entry in signs_a if entry) < 0:
            continue
        patterns += 1
        active, equations = pattern_data(signs_a, signs)
        width = 8 * len(active)
        _rank, corank = rank_of(equations, width)
        if corank != len(active):
            fail("D.corank", "pattern %s has corank %d" % (signs_a, corank))
        for slot, j in enumerate(active):
            coeff = kernel_coeff[j] << (8 * slot)
            if not satisfies(equations, coeff):
                fail("D.span", "original kernel %d misses pattern %s" % (j, signs_a))
        corank_matches += 1
    check("D.parity", patterns == 3272 and corank_matches == 3272,
          "all 3272 sign patterns with k>=2, up to global sign, have corank k spanned by the original kernels")

    # Label coordinates for the 511 functionals.
    basis_lines = []
    for line in range(NL):
        if f2_rank([NROW[item] for item in basis_lines] + [NROW[line]]) == len(basis_lines) + 1:
            basis_lines.append(line)
        if len(basis_lines) == 9:
            break
    phi = [sum(bit(NROW[line], basis_lines[slot]) << slot for slot in range(9)) for line in range(NL)]
    hit = []
    for functional in range(512):
        mask = 0
        for port, line in enumerate(live):
            if bin(functional & phi[line]).count("1") % 2:
                mask |= 1 << port
        hit.append(mask)

    kernels = []
    rank_hist = {7: 0, 8: 0}
    for functional in range(1, 512):
        rows = []
        mask = hit[functional]
        port = 0
        while mask:
            if mask & 1:
                rows.append([readers[j][port] for j in range(8)])
            mask >>= 1
            port += 1
        rank = rational_rank(rows)
        if rank not in (7, 8):
            fail("E.census", "functional %d has rank %d" % (functional, rank))
        rank_hist[rank] += 1
        if rank == 7:
            vectors = nullspace(rows)
            if len(vectors) != 1:
                fail("E.census", "functional %d kernel dimension %d" % (functional, len(vectors)))
            kernels.append(normalize(vectors[0]))
    expected = {normalize(vector) for vector in SPECIALS}
    expected |= {tuple(1 if slot == j else 0 for slot in range(8)) for j in range(8)}
    check("E.census", rank_hist == {7: 16, 8: 495} and set(kernels) == expected and len(kernels) == 16,
          "495 full supports and 16 rank-7 kernels: eight axes and eight weight-4 directions")

    def quotient_rank(sign_pattern, reader_column):
        active, equations = pattern_data(sign_pattern, signs)
        width = 8 * len(active)
        basis = {}
        rows = []
        for equation in equations:
            for row in rows:
                head = row.bit_length() - 1
                if bit(equation, head):
                    equation ^= row
            if not equation:
                continue
            head = equation.bit_length() - 1
            rows = [row ^ equation if bit(row, head) else row for row in rows]
            rows.append(equation)
        pivot_cols = [row.bit_length() - 1 for row in rows]
        free = [column for column in range(width) if column not in pivot_cols]
        sums = []
        for slot in free:
            coeff = 1 << slot
            for row, pivot in zip(rows, pivot_cols):
                if bit(row, slot):
                    coeff |= 1 << pivot
            total = 0
            for block, j in enumerate(active):
                piece = (coeff >> (8 * block)) & 255
                vector = 0
                for bit_index in range(8):
                    if (piece >> bit_index) & 1:
                        vector ^= bases[j][bit_index]
                total ^= vector
            sums.append(total)
        span = {}
        for port, value in enumerate(reader_column):
            if value:
                f2_insert(span, NROW[live[port]])
        f2_reduce(span)

        def residue(vector):
            for pivot in sorted(span, reverse=True):
                if bit(vector, pivot):
                    vector ^= span[pivot]
            return vector

        return len(free), f2_rank(residue(vector) for vector in sums), support_dim(
            live[port] for port, value in enumerate(reader_column) if value)

    special_ok = True
    for vector in SPECIALS:
        for scale in (1, -1):
            column_a = tuple(scale * entry for entry in vector)
            sign_pattern = tuple((1 if entry > 0 else -1 if entry < 0 else 0) for entry in column_a)
            combined = [sum(column_a[j] * readers[j][port] for j in range(8)) for port in range(104)]
            corank, qrank, dimension = quotient_rank(sign_pattern, combined)
            if not (corank == 4 and qrank == 1 and dimension == 8):
                special_ok = False
    check("F.specials", special_ok,
          "each weight-4 direction and its negative has reader span 8 and parity-sum quotient rank 1")

    def lift_cost(column_a, correction):
        parts = []
        for j in range(8):
            corrected = [sources[j][port] - column_a[j] * correction[port] for port in range(104)]
            parts.append(beta(readers[j], corrected))
        ninth = [sum(column_a[j] * readers[j][port] for j in range(8)) for port in range(104)]
        parts.append(beta(ninth, correction))
        return sum(parts), parts

    zero = [0] * 104
    cost_zero, parts_zero = lift_cost([0] * 8, zero)
    moves_ok = True
    move_parts = None
    for j in range(8):
        column_a = [1 if slot == j else 0 for slot in range(8)]
        cost_move, parts_move = lift_cost(column_a, sources[j])
        expected_parts = [0 if slot == j else 7 for slot in range(8)] + [7]
        if cost_move != 56 or parts_move != expected_parts:
            moves_ok = False
        if j == 0:
            move_parts = parts_move
    cost_special, _parts_special = lift_cost(SPECIALS[0], zero)
    dense = [1] * 104
    cost_dense, _parts_dense = lift_cost(SPECIALS[0], dense)
    check("G.sharp", cost_zero == 56 and parts_zero == [7] * 8 + [0]
          and moves_ok and move_parts == [0] + [7] * 7 + [7]
          and cost_special == 56 and cost_dense > 56,
          "z=0 and each one-term move attain 56; a dense correction is strictly above")

    # Failure controls.
    mutated = [column[:] for column in sources]
    mutated[0][0] += 1
    mutated_ok = True
    for right in range(104):
        total = sum(readers[j][0] * mutated[j][right] for j in range(8))
        if total != 2 * IP[live[0]][live[right]]:
            mutated_ok = False
            break
    check("H.identity-mutation", not mutated_ok, "changing one source entry breaks the Gram identity")

    reader_signs = [[1 if value > 0 else -1 if value < 0 else 0 for value in column] for column in readers]
    reader_coranks = set()
    for signs_a in itertools.product((-1, 0, 1), repeat=8):
        if sum(entry != 0 for entry in signs_a) < 2 or next(entry for entry in signs_a if entry) < 0:
            continue
        active, equations = pattern_data(signs_a, reader_signs)
        _rank, corank = rank_of(equations, 8 * len(active))
        reader_coranks.add(corank)
    check("H.reader-signs", reader_coranks == {0},
          "the same equations on reader signs have corank 0, so the source signs are essential")

    fake = normalize((1, 1, 1, 1, 1, 1, 1, 1))
    check("H.fake-kernel", fake not in set(kernels), "a weight-8 vector is not a deficient reader direction")
    check("H.empty-beta", beta(readers[0], zero) == 0 and beta(zero, sources[0]) == 0,
          "an empty reader or source support has pairing rank 0")
    axis_count = sum(sum(entry != 0 for entry in vector) == 1 for vector in kernels)
    check("H.axis-count", axis_count == 8, "exactly eight of the computed rank-7 kernels are coordinate axes")

    print("PASS_P104_FRAME_PAIR_SINGLE_LIFT frame=%s patterns=3272 census=495/16 "
          "specials=8 floor=56 no_new_kappa" % ",".join(str(line) for line in EXPECTED_F1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
