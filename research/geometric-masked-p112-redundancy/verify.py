#!/usr/bin/env python3
"""Odd-pair constraints are redundant for geometric decoders on P112.

A geometric decoder evaluates C^8 normals, so its Gram entries are ρ^T M σ
for one matrix M. On the complement of the coordinate frame
F = {e_{2a} ± e_{2a+1} : a = 0,1,2,3}, the even-inner-product equations
already force M = 2I. Odd pairs then match the all-pairs target, and no
cost-0 repair, extra frame, or restoration is created by the mask.

The argument is the coordinate calculation in PROOF.md. This program replays
that calculation in exact arithmetic, checks the two failure controls named
there, and audits every live pair of the independently built E8 model.
"""

from fractions import Fraction
import itertools

MODULI = (1_000_003, 1_000_033)
FRAME_PAIRS = ({0, 1}, {2, 3}, {4, 5}, {6, 7})
COUPLINGS = ((0, 2, 1, 3), (0, 4, 1, 5), (0, 6, 1, 7))


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def coordinate(i, j, sign):
    vector = [0] * 8
    vector[i] = 1
    vector[j] = sign
    return tuple(vector)


def stored_lines():
    """One stored representative of each root line. True root = stored / 2."""
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                vector = [0] * 8
                vector[i], vector[j] = 2 * si, 2 * sj
                roots.append(tuple(vector))
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(signs)
    lines = []
    seen = set()
    for root in roots:
        opposite = tuple(-entry for entry in root)
        key = root if root > opposite else opposite
        if key not in seen:
            seen.add(key)
            lines.append(root)
    return lines


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def equation(left, right, target):
    row = [Fraction(0)] * 64
    for a in range(8):
        for b in range(8):
            row[a * 8 + b] = Fraction(left[a] * right[b])
    return row, Fraction(target)


def proof_equations(omit_last_coupling=False):
    rows = []
    for i in range(8):
        for j in range(i + 1, 8):
            if {i, j} in FRAME_PAIRS:
                continue
            positive = coordinate(i, j, 1)
            negative = coordinate(i, j, -1)
            rows.append(equation(positive, positive, 4))
            rows.append(equation(negative, negative, 4))
            rows.append(equation(positive, negative, 0))
            rows.append(equation(negative, positive, 0))
    couplings = COUPLINGS[:-1] if omit_last_coupling else COUPLINGS
    for a, c, b, d in couplings:
        for sign_b, sign_d in ((1, 1), (1, -1)):
            left = coordinate(a, c, 1)
            right = [0] * 8
            right[b] = sign_b
            right[d] = sign_d
            rows.append(equation(left, tuple(right), 0))
            rows.append(equation(tuple(right), left, 0))
    return rows


def eliminate(rows):
    """Exact row reduction. Returns rank, a solution, and whether it is consistent."""
    matrix = [list(row) for row, _target in rows]
    targets = [target for _row, target in rows]
    pivot_of = [-1] * 64
    rank = 0
    for col in range(64):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][col] != 0), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        targets[rank], targets[pivot] = targets[pivot], targets[rank]
        scale = matrix[rank][col]
        for i in range(len(matrix)):
            if i == rank or matrix[i][col] == 0:
                continue
            factor = matrix[i][col] / scale
            for c in range(col, 64):
                matrix[i][c] -= factor * matrix[rank][c]
            targets[i] -= factor * targets[rank]
        pivot_of[col] = rank
        rank += 1
    if any(matrix[i] == [Fraction(0)] * 64 and targets[i] != 0 for i in range(len(matrix))):
        return rank, None, False
    solution = [Fraction(0)] * 64
    for col in range(63, -1, -1):
        if pivot_of[col] < 0:
            continue
        row = pivot_of[col]
        value = targets[row]
        for c in range(col + 1, 64):
            value -= matrix[row][c] * solution[c]
        solution[col] = value / matrix[row][col]
    return rank, solution, True


def rank_mod(rows, modulus):
    matrix = [[entry % modulus for entry in row] for row in rows]
    rank = 0
    for col in range(64):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][col] != 0), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = pow(matrix[rank][col], -1, modulus)
        for i in range(len(matrix)):
            factor = matrix[i][col] * inverse % modulus
            if i == rank or factor == 0:
                continue
            for c in range(col, 64):
                matrix[i][c] = (matrix[i][c] - factor * matrix[rank][c]) % modulus
        rank += 1
    return rank


def matrix_from_entries(pairs):
    matrix = [[0] * 8 for _ in range(8)]
    for (a, b), value in pairs:
        matrix[a][b] = value
    return matrix


def bilinear(matrix, left, right):
    return sum(left[a] * matrix[a][b] * right[b] for a in range(8) for b in range(8))


def main():
    lines = stored_lines()
    require(len(lines) == 120, "expected 120 root lines")
    frame = []
    for block in range(4):
        for sign in (1, -1):
            stored = [0] * 8
            stored[2 * block] = 2
            stored[2 * block + 1] = 2 * sign
            representative = tuple(stored)
            opposite = tuple(-entry for entry in representative)
            key = representative if representative > opposite else opposite
            frame.append(lines.index(key))
    require(len(set(frame)) == 8, "coordinate frame is not eight distinct lines")
    live = [i for i in range(120) if i not in set(frame)]
    require(len(live) == 112, "P112 should retain 112 lines")
    require(all(dot(lines[i], lines[i]) == 8 for i in range(120)), "stored roots should have dot 8")
    require(
        all(dot(lines[a], lines[b]) == 0 for a in frame for b in frame if a != b),
        "the deleted frame should be pairwise orthogonal",
    )

    full = proof_equations(False)
    reduced = proof_equations(True)
    require(len(full) == 108 and len(reduced) == 104, "unexpected proof-equation count")
    for left, right in (
        (coordinate(0, 2, 1), coordinate(1, 3, 1)),
        (coordinate(0, 2, 1), coordinate(1, 3, -1)),
        (coordinate(0, 4, 1), coordinate(1, 5, 1)),
        (coordinate(0, 6, 1), coordinate(1, 7, 1)),
    ):
        require({i for i, value in enumerate(left) if value} not in FRAME_PAIRS, "proof root was punctured")
        require({i for i, value in enumerate(right) if value} not in FRAME_PAIRS, "proof root was punctured")

    # Raw expansions in PROOF.md, before non-frame entries are set to zero.
    u = coordinate(0, 2, 1)
    v_plus = tuple(1 if index in (1, 3) else 0 for index in range(8))
    v_minus = tuple(1 if index == 1 else -1 if index == 3 else 0 for index in range(8))
    plus_coeffs = {(0, 1): 1, (0, 3): 1, (2, 1): 1, (2, 3): 1}
    minus_coeffs = {(0, 1): 1, (0, 3): -1, (2, 1): 1, (2, 3): -1}
    for a, b in itertools.product(range(8), repeat=2):
        basis = matrix_from_entries([((a, b), 1)])
        require(bilinear(basis, u, v_plus) == plus_coeffs.get((a, b), 0),
                "expansion of e0+e2 against e1+e3")
        require(bilinear(basis, u, v_minus) == minus_coeffs.get((a, b), 0),
                "expansion of e0+e2 against e1-e3")
    require(all({p, q} not in FRAME_PAIRS for p, q in ((0, 3), (2, 1))),
            "entries discarded by the proof are not non-frame")

    rank, solution, consistent = eliminate(full)
    identity = [Fraction(2 if index % 9 == 0 else 0) for index in range(64)]
    require(consistent and rank == 64 and solution == identity, "proof equations do not force M = 2I")

    reduced_rank, _reduced_solution, reduced_ok = eliminate(reduced)
    require(reduced_ok and reduced_rank == 62, "dropping the last coupling should leave nullity 2")
    symmetric = matrix_from_entries([((6, 7), 1), ((7, 6), 1)])
    skew = matrix_from_entries([((6, 7), 1), ((7, 6), -1)])
    for witness in (symmetric, skew):
        for row, _target in reduced:
            value = sum(row[index] * witness[index // 8][index % 8] for index in range(64))
            require(value == 0, "reduced system rejected a nullity witness")
        require(bilinear(witness, coordinate(0, 6, 1), coordinate(1, 7, 1)) != 0,
                "last coupling did not see the witness")

    broken = list(full)
    row, _target = broken[0]
    broken[0] = (row, Fraction(1))
    _rank, _solution, broken_ok = eliminate(broken)
    require(not broken_ok, "an altered right-hand side was still solved")

    even_rows = []
    even_live = odd_live = 0
    for i in live:
        for j in live:
            inner = dot(lines[i], lines[j])
            require(inner in (-4, 0, 4, 8), "unexpected stored inner product")
            gram = sum(2 * lines[i][a] * lines[j][a] for a in range(8))
            require(gram == 2 * inner, "2I missed the stored all-pairs value")
            if inner % 8 == 0:
                even_live += 1
                row = [0] * 64
                for a in range(8):
                    for b in range(8):
                        row[a * 8 + b] = lines[i][a] * lines[j][b]
                even_rows.append(row)
                require(sum(2 * row[a * 8 + a] for a in range(8)) == gram,
                        "even row disagrees with 2I")
            else:
                odd_live += 1
                require(inner in (-4, 4) and gram in (-8, 8), "odd live pair is not a cost-0 site")
    require(even_live == 6720 and odd_live == 5824, "unexpected live even/odd counts")
    for modulus in MODULI:
        require(rank_mod(even_rows, modulus) == 64, "full even system lost rank modulo %s" % modulus)

    # Odd stored pairs are exactly the historical cost-0 singleton sites:
    # (<ρ,σ> + 1) is even precisely when the stored dot is ±4.
    require(all((inner // 4 + 1) % 2 == 0 for inner in (-4, 4)), "odd pairs should have pairing bit 0")
    require(all((inner // 4 + 1) % 2 == 1 for inner in (0, 8)), "even pairs should have pairing bit 1")

    print(
        "PASS_GEOMETRIC_MASKED_P112_REDUNDANCY "
        "proof_equations=108 proof_rank=64 "
        "live=112 even_live=6720 odd_live=5824 repairs=0 "
        "full_even_rank_mod=64 controls=2"
    )


if __name__ == "__main__":
    main()
