#!/usr/bin/env python3
"""P112 coordinate-row span and the three-port two-total copy-rank bound.

The predecessor geometry and its pairing-rank function are the pinned input.
An independent builder and a column-wise F2 rank live in independent_check.py
and must agree on the matrix, the census and the invoices. Explicit exceptions
are used so python -O does not strip the checks.

Apache-2.0. Riquelme Soares (@hevlyo), with substantial AI assistance.
"""

import importlib.util
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
geometry = load('pinned_p112_geometry', ROOT / 'research/p112-single-lift/geometry.py')
independent = load('p112_two_total_independent', HERE / 'independent_check.py')


def predecessor_split_histogram(data):
    labels, duals, columns = data['labels'], data['duals'], data['X']
    histogram = {}
    for column in range(8):
        readers = [row[column] for row in columns]
        support = [i for i in range(112) if readers[i]]
        space = geometry.reader_space(readers, duals)
        require(len(space) == 8, 'predecessor reader span')
        coords = {i: geometry.evaluate(space, labels[i]) for i in support}
        require(len(set(coords.values())) == len(support) == 56, 'predecessor support')
        local = {}
        for form in range(1, 256):
            deleted = {i for i in support if geometry.parity(coords[i] & form)}
            deleted_source = [readers[i] if i in deleted else 0 for i in range(112)]
            remaining = [readers[i] if i not in deleted else 0 for i in range(112)]
            key = (len(deleted),
                   geometry.term_cost(readers, deleted_source, data),
                   geometry.term_cost(readers, remaining, data))
            local[key] = local.get(key, 0) + 1
        histogram[column] = local
    return histogram


def predecessor_invoice(data, coefficient_a, coefficient_b, source_z, source_w):
    columns = data['X']
    costs = []
    for column in range(8):
        readers = [row[column] for row in columns]
        sources = [readers[i] - coefficient_a[column] * source_z[i]
                   - coefficient_b[column] * source_w[i] for i in range(112)]
        costs.append(geometry.term_cost(readers, sources, data))
    extra_a = [sum(row[j] * coefficient_a[j] for j in range(8)) for row in columns]
    extra_b = [sum(row[j] * coefficient_b[j] for j in range(8)) for row in columns]
    return costs, [geometry.term_cost(extra_a, source_z, data),
                   geometry.term_cost(extra_b, source_w, data)]


def run():
    pinned = geometry.build()
    geometry.check_geometry(pinned)
    other = independent.build()
    require(other['X'] == pinned['X'], 'coordinate matrix drift')
    require(other['labels'] == pinned['labels'], 'label drift')
    require(other['duals'] == pinned['duals'], 'dual drift')
    require(other['roots'] == pinned['roots'], 'root drift')
    rows = [tuple(row) for row in pinned['X']]
    planes = independent.plane_census(rows)
    require(planes['parallel'] == 0 and planes['independent'] == 6216, 'pair census')
    require(planes['max_extra'] == 1 and planes['planes'] == 896, 'plane census')
    pinned_histogram = predecessor_split_histogram(pinned)
    other_histogram, _witness = independent.cocircuit_census(other)
    expected = {(24, 7, 7): 63, (28, 7, 7): 128, (32, 7, 7): 63, (56, 8, 0): 1}
    require(pinned_histogram == other_histogram, 'rank implementations disagree')
    require(all(column == expected for column in pinned_histogram.values()), 'cocircuit census')
    # Every dropping set contains a positive form-section, and those have size >= 24.
    minimum = min(size for size, _deleted, _remaining in expected)
    require(minimum == 24, 'minimum cocircuit')
    indices = independent.locate_sharp_triple(rows)
    zero = [0] * 112
    zero_readers, zero_extra = predecessor_invoice(pinned, [0] * 8, [0] * 8, zero, zero)
    other_zero = independent.correction_cost(other, [0] * 8, [0] * 8, zero, zero)
    require((zero_readers, zero_extra) == other_zero == ([8] * 8, [0, 0]), 'zero invoice')
    coefficient_a = list(rows[indices[0]])
    coefficient_b = list(rows[indices[1]])
    source_z, source_w = zero[:], zero[:]
    source_z[indices[0]] = 1
    source_w[indices[1]] = 1
    source_z[indices[2]] = 1
    source_w[indices[2]] = -1
    sharp = predecessor_invoice(pinned, coefficient_a, coefficient_b, source_z, source_w)
    other_sharp = independent.correction_cost(other, coefficient_a, coefficient_b, source_z, source_w)
    require(sharp == other_sharp == ([8] * 8, [2, 2]), 'sharp invoice')
    require(sum(sharp[0]) + sum(sharp[1]) == 68, 'sharp total')
    require(sum(1 for i in range(112) if source_z[i] or source_w[i]) == 3, 'support size')
    for port in indices:
        residual = [pinned['X'][port][j] - coefficient_a[j] * source_z[port]
                    - coefficient_b[j] * source_w[port] for j in range(8)]
        require(residual == [0] * 8, 'incomplete absorption')
    # A 23-port subset of an explicit 24-port cocircuit does not drop rank.
    readers = [row[0] for row in pinned['X']]
    support = [i for i in range(112) if readers[i]]
    space = geometry.reader_space(readers, pinned['duals'])
    coords = {i: geometry.evaluate(space, pinned['labels'][i]) for i in support}
    deleted = next(tuple(i for i in support if geometry.parity(coords[i] & form))
                   for form in range(1, 256)
                   if sum(geometry.parity(coords[i] & form) for i in support) == 24)
    near = set(deleted[:-1])
    remaining = [readers[i] if i not in near else 0 for i in range(112)]
    require(len(near) == 23 and geometry.term_cost(readers, remaining, pinned) == 8,
            '23-port near-cocircuit dropped the reader rank')
    synthetic = tuple(a + b for a, b in zip(rows[indices[0]], rows[indices[1]]))
    require(independent.in_span(rows[indices[0]], rows[indices[1]], synthetic)
            and synthetic not in rows, 'dependence control')
    require(not independent.in_span(rows[indices[0]], rows[indices[1]],
                                    (1, 0, 0, 0, 0, 0, 0, 0)),
            'independence control')
    mutated = {key: ( [list(row) for row in value] if key == 'X' else value)
               for key, value in pinned.items()}
    mutated['X'][0][0] = 0 if mutated['X'][0][0] else 1
    rejected = False
    try:
        geometry.check_geometry(mutated)
    except ValueError:
        rejected = True
    require(rejected, 'mutated geometry was accepted')
    # The three-port corollary is the cocircuit threshold applied to this support.
    require(minimum > 3, 'three-port deletions could drop a reader')
    print('PASS planes: 6216 pairs, 0 parallel rows, 896 three-point planes, no four coplanar')
    print('PASS cocircuits: 8 readers, 255 forms, minimum deletion 24, '
          'splits (24,7,7)x63 (28,7,7)x128 (32,7,7)x63 (56,8,0)x1')
    print('PASS invoices: zero correction 64; sharp three-port absorption 68 with readers 8')
    print('PASS controls: implementations agree; 23-port rank 8; dependence and Gram controls')
    print('PASS_P112_TWO_TOTAL_ROW_SPAN')


if __name__ == '__main__':
    try:
        run()
    except ValueError as exc:
        raise SystemExit('FAIL: ' + str(exc)) from exc
