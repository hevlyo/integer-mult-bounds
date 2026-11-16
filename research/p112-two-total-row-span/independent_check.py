#!/usr/bin/env python3
"""Independent census of P112 coordinate-row planes and reader cocircuits.

This file does not import research/p112-single-lift/geometry.py or verify.py.
The E8/P112 builder follows DreamingOfClouds' PR717 model as recorded by
Mihir Srivastava in research/p112-single-lift/geometry.py. Pairing rank is
reimplemented by column-wise elimination over F2.

Apache-2.0. Riquelme Soares (@hevlyo), with substantial AI assistance.
"""

from fractions import Fraction
from itertools import combinations, product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def mask(values):
    out = 0
    for value in values:
        out = (out << 1) | (value & 1)
    return out


def parity(value):
    return value.bit_count() & 1


def inverse(matrix):
    size = len(matrix)
    rows = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(size)]
            for i, row in enumerate(matrix)]
    for col in range(size):
        pivot = next(i for i in range(col, size) if rows[i][col])
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        rows[col] = [x / divisor for x in rows[col]]
        for i in range(size):
            if i != col:
                coefficient = rows[i][col]
                rows[i] = [x - coefficient * y for x, y in zip(rows[i], rows[col])]
    return [row[size:] for row in rows]


def build():
    """Pinned P112 coordinate model. Row order is part of the predecessor builder."""
    roots = []
    for i, j in combinations(range(8), 2):
        for si, sj in product((1, -1), repeat=2):
            vector = [0] * 8
            vector[i], vector[j] = 2 * si, 2 * sj
            roots.append(vector)
    roots.extend(list(signs) for signs in product((1, -1), repeat=8)
                 if signs.count(-1) % 2 == 0)
    simple = [[1, -1, -1, -1, -1, -1, -1, 1],
              [2, 2, 0, 0, 0, 0, 0, 0],
              [-2, 2, 0, 0, 0, 0, 0, 0]]
    for k in range(1, 6):
        vector = [0] * 8
        vector[k], vector[k + 1] = -2, 2
        simple.append(vector)
    change = inverse(simple)
    gram = [[dot(a, b) // 4 for b in simple] for a in simple]
    frame = []
    for j in range(4):
        for sign in (1, -1):
            vector = [0] * 8
            vector[2 * j], vector[2 * j + 1] = 2, 2 * sign
            frame.append(vector)
    lines, seen = [], set()
    for root in roots:
        key = max(tuple(root), tuple(-v for v in root))
        if key not in seen:
            seen.add(key)
            lines.append(root)
    frame_keys = {tuple(vector) for vector in frame}
    kept = [root for root in lines
            if tuple(root) not in frame_keys and tuple(-v for v in root) not in frame_keys]
    labels, duals, columns = [], [], []
    for root in kept:
        coordinates = [sum(root[k] * change[k][j] for k in range(8)) for j in range(8)]
        require(all(value.denominator == 1 for value in coordinates), 'nonintegral coordinates')
        coordinates = [int(value) for value in coordinates]
        require([sum(coordinates[k] * simple[k][j] for k in range(8)) for j in range(8)] == root,
                'root reconstruction')
        labels.append(mask(coordinates + [1]))
        duals.append(mask([sum(coordinates[k] * gram[k][j] for k in range(8))
                           for j in range(8)] + [1]))
        columns.append([dot(root, vector) // 4 for vector in frame])
    return {'roots': kept, 'labels': labels, 'duals': duals, 'X': columns}


def check_model(data):
    roots, labels, duals, columns = data['roots'], data['labels'], data['duals'], data['X']
    require(len(columns) == len(labels) == len(duals) == len(roots) == 112, 'P112 size')
    require(len({tuple(row) for row in columns}) == 112, 'duplicate coordinate rows')
    for row in columns:
        require(set(row) <= {-1, 0, 1} and dot(row, row) == 4, 'coordinate alphabet')
    for i, j in combinations(range(112), 2):
        gram = dot(roots[i], roots[j])
        require(gram % 4 == 0, 'integral Gram')
        require(dot(columns[i], columns[j]) == gram // 2, 'XX^T = 2G')
        require(parity(duals[i] & labels[j]) == (1 + gram // 4) % 2, 'label pairing')
    for i in range(112):
        gram = dot(roots[i], roots[i])
        require(dot(columns[i], columns[i]) == gram // 2, 'diagonal Gram')
        require(parity(duals[i] & labels[i]) == (1 + gram // 4) % 2, 'diagonal pairing')


def two_minor(left, right):
    for i, j in combinations(range(8), 2):
        minor = left[i] * right[j] - left[j] * right[i]
        if minor:
            return minor
    return 0


def in_span(left, right, vector):
    for i, j, k in combinations(range(8), 3):
        minor = (left[i] * (right[j] * vector[k] - right[k] * vector[j])
                 - left[j] * (right[i] * vector[k] - right[k] * vector[i])
                 + left[k] * (right[i] * vector[j] - right[j] * vector[i]))
        if minor:
            return False
    return True


def plane_census(rows):
    max_extra = 0
    extra_sum = 0
    parallel = 0
    independent = 0
    for i, j in combinations(range(len(rows)), 2):
        if two_minor(rows[i], rows[j]) == 0:
            parallel += 1
            continue
        independent += 1
        extra = sum(1 for k in range(len(rows))
                    if k != i and k != j and in_span(rows[i], rows[j], rows[k]))
        max_extra = max(max_extra, extra)
        extra_sum += extra
    require(max_extra == 1 and extra_sum % 3 == 0, 'plane census is not a disjoint triple cover')
    return {'pairs': independent + parallel, 'parallel': parallel,
            'independent': independent, 'max_extra': max_extra,
            'planes': extra_sum // 3}


def dual_basis(duals, active):
    pivots = {}
    for flag, dual in zip(active, duals):
        if not flag:
            continue
        value = dual
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return [pivots[bit] for bit in sorted(pivots, reverse=True)]


def evaluate(space, label):
    return sum(parity(vector & label) << index for index, vector in enumerate(space))


def rank_columns(vectors, width):
    """Rank of an n-by-width F2 matrix given as row masks, eliminating by columns."""
    pivot_at = {}
    rank = 0
    for bit in range(width):
        column = 0
        for index, vector in enumerate(vectors):
            if (vector >> bit) & 1:
                column |= 1 << index
        while column:
            row = column.bit_length() - 1
            if row in pivot_at:
                column ^= pivot_at[row]
            else:
                pivot_at[row] = column
                rank += 1
                break
    return rank


def source_rank(duals, labels, readers, sources):
    space = dual_basis(duals, readers)
    rows = [evaluate(space, label) for flag, label in zip(sources, labels) if flag]
    return rank_columns(rows, len(space))


def cocircuit_census(data):
    labels, duals, columns = data['labels'], data['duals'], data['X']
    histogram = {}
    minimum = None
    for column in range(8):
        readers = [row[column] for row in columns]
        support = [i for i in range(112) if readers[i]]
        space = dual_basis(duals, readers)
        require(len(space) == 8, 'reader span')
        coords = {i: evaluate(space, labels[i]) for i in support}
        require(len(set(coords.values())) == 56, 'evaluation vectors are not distinct')
        local = {}
        for form in range(1, 256):
            deleted = [i for i in support if parity(coords[i] & form)]
            sources = [1 if i in set(deleted) else 0 for i in range(112)]
            remaining = [1 if readers[i] and i not in set(deleted) else 0 for i in range(112)]
            key = (len(deleted),
                   source_rank(duals, labels, readers, sources),
                   source_rank(duals, labels, readers, remaining))
            local[key] = local.get(key, 0) + 1
            if len(deleted) == 24 and minimum is None:
                minimum = (column, form, tuple(deleted), readers)
        histogram[column] = local
    require(minimum is not None, 'no 24-port form')
    return histogram, minimum


def correction_cost(data, coefficient_a, coefficient_b, source_z, source_w):
    columns, labels, duals = data['X'], data['labels'], data['duals']
    reader_costs = []
    for column in range(8):
        readers = [row[column] for row in columns]
        sources = [readers[i] - coefficient_a[column] * source_z[i]
                   - coefficient_b[column] * source_w[i] for i in range(112)]
        reader_costs.append(source_rank(duals, labels, [1 if value else 0 for value in readers],
                                         [1 if value else 0 for value in sources]))
    extra_a = [sum(row[j] * coefficient_a[j] for j in range(8)) for row in columns]
    extra_b = [sum(row[j] * coefficient_b[j] for j in range(8)) for row in columns]
    extra_cost = [
        source_rank(duals, labels, [1 if value else 0 for value in extra_a],
                    [1 if value else 0 for value in source_z]),
        source_rank(duals, labels, [1 if value else 0 for value in extra_b],
                    [1 if value else 0 for value in source_w])]
    return reader_costs, extra_cost


def locate_sharp_triple(rows):
    first = (1, 1, 1, 1, 0, 0, 0, 0)
    second = (1, 1, 0, 0, 1, 1, 0, 0)
    third = tuple(a - b for a, b in zip(first, second))
    indices = []
    for vector in (first, second, third):
        require(vector in rows, 'sharp plane vector missing')
        indices.append(rows.index(vector))
    require(in_span(rows[indices[0]], rows[indices[1]], rows[indices[2]]), 'sharp triple')
    members = [k for k in range(len(rows))
               if in_span(rows[indices[0]], rows[indices[1]], rows[k])]
    require(members == sorted(indices), 'sharp plane is not exactly these three rows')
    return indices


def run():
    data = build()
    check_model(data)
    rows = [tuple(row) for row in data['X']]
    planes = plane_census(rows)
    require(planes == {'pairs': 6216, 'parallel': 0, 'independent': 6216,
                       'max_extra': 1, 'planes': 896}, 'unexpected plane census')
    histogram, witness = cocircuit_census(data)
    expected = {(24, 7, 7): 63, (28, 7, 7): 128, (32, 7, 7): 63, (56, 8, 0): 1}
    require(all(column == expected for column in histogram.values()), 'unexpected cocircuit census')
    _column, _form, deleted, readers = witness
    near = deleted[:-1]
    near_sources = [1 if readers[i] and i not in set(near) else 0 for i in range(112)]
    # The near-cocircuit keeps one positive port, so the reader must stay full rank.
    near_rank = source_rank(data['duals'], data['labels'], readers, near_sources)
    require(len(near) == 23 and near_rank == 8, '23-port deletion changed rank')
    indices = locate_sharp_triple(rows)
    zero = [0] * 112
    zero_readers, zero_extra = correction_cost(data, [0] * 8, [0] * 8, zero, zero)
    require(zero_readers == [8] * 8 and zero_extra == [0, 0], 'zero correction')
    coefficient_a = list(rows[indices[0]])
    coefficient_b = list(rows[indices[1]])
    source_z, source_w = zero[:], zero[:]
    source_z[indices[0]] = 1
    source_w[indices[1]] = 1
    source_z[indices[2]] = 1
    source_w[indices[2]] = -1
    sharp_readers, sharp_extra = correction_cost(data, coefficient_a, coefficient_b, source_z, source_w)
    require(sharp_readers == [8] * 8 and sharp_extra == [2, 2], 'sharp absorption invoice')
    for port in indices:
        residual = [data['X'][port][j] - coefficient_a[j] * source_z[port]
                    - coefficient_b[j] * source_w[port] for j in range(8)]
        require(residual == [0] * 8, 'sharp port was not fully absorbed')
    synthetic = tuple(a + b for a, b in zip(rows[indices[0]], rows[indices[1]]))
    require(in_span(rows[indices[0]], rows[indices[1]], synthetic), 'predicate missed a dependence')
    require(synthetic not in rows, 'synthetic row collided with X')
    require(not in_span(rows[indices[0]], rows[indices[1]], (1, 0, 0, 0, 0, 0, 0, 0)),
            'predicate accepted an independent vector')
    mutated = {'roots': data['roots'], 'labels': data['labels'], 'duals': data['duals'],
               'X': [list(row) for row in data['X']]}
    mutated['X'][0][0] = 0 if mutated['X'][0][0] else 1
    rejected = False
    try:
        check_model(mutated)
    except ValueError:
        rejected = True
    require(rejected, 'mutated coordinate row passed the Gram check')
    support = sum(1 for i in range(112) if source_z[i] or source_w[i])
    require(support == 3, 'sharp absorption support')
    print('PASS independent plane census: 6216 pairs, 0 parallel, 896 three-point planes')
    print('PASS independent cocircuits: min deletion 24; each reader '
          '(24,7,7)x63 (28,7,7)x128 (32,7,7)x63 (56,8,0)x1')
    print('PASS independent invoices: zero correction 64; sharp triple 68 on 3 ports')
    print('PASS independent controls: 23-port rank 8; synthetic dependence; mutated Gram rejected')
    print('PASS_P112_TWO_TOTAL_ROW_SPAN_INDEPENDENT')


if __name__ == '__main__':
    try:
        run()
    except ValueError as exc:
        raise SystemExit('FAIL: ' + str(exc)) from exc
