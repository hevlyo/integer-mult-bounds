#!/usr/bin/env python3
"""Masked rank and separated copy cost on every E8 double frame.

The 16-line alphabet is a coordinate frame F0 together with any of the 1260
frames in its complement. The masked E-graph equations keep diagonal 4 and
force a zero on every orthogonal pair; odd inner-product entries stay free.
This checker proves the finite census in PROOF.md. It does not build a
supplier or change kappa.

Standard library only. Exact integer and F2 arithmetic.
"""

from __future__ import annotations

import itertools
import sys
from collections import Counter, defaultdict


def fail(message):
    raise SystemExit("FAIL " + message)


def check(name, cond, detail):
    if not cond:
        fail(name + " | " + detail)
    print("PASS " + name + " | " + detail, flush=True)


def e8_roots():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                vector = [0] * 8
                vector[i], vector[j] = 2 * si, 2 * sj
                roots.append(tuple(vector))
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(tuple(signs))
    return roots


def inner(left, right):
    product = sum(a * b for a, b in zip(left, right))
    if product % 4:
        fail("inner product not divisible by 4")
    return product // 4


def opposite(vector):
    return tuple(-coordinate for coordinate in vector)


def f2_rank(rows):
    basis = {}
    rank = 0
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return rank


def mask_of(indices):
    value = 0
    for index in indices:
        value |= 1 << index
    return value


ROOTS = e8_roots()
LINES = []
SEEN = set()
for root in ROOTS:
    key = root if root > opposite(root) else opposite(root)
    if key not in SEEN:
        SEEN.add(key)
        LINES.append(root)
if len(ROOTS) != 240 or len(LINES) != 120:
    fail("E8 root geometry is not 240 roots and 120 lines")

IP = [[inner(LINES[i], LINES[j]) for j in range(120)] for i in range(120)]
FRAME0 = []
for plane in range(4):
    for sign in (1, -1):
        vector = [0] * 8
        vector[2 * plane] = 2
        vector[2 * plane + 1] = 2 * sign
        FRAME0.append(LINES.index(tuple(vector)))
if len(FRAME0) != 8 or len(set(FRAME0)) != 8:
    fail("coordinate frame is not eight distinct lines")
P112 = [i for i in range(120) if i not in set(FRAME0)]


def label_bit(i, j):
    return (IP[i][j] + 1) & 1


def frames_in(pool):
    orth = {
        i: mask_of(j for j in pool if j != i and IP[i][j] == 0)
        for i in pool
    }
    found = []

    def rec(clique, cand):
        if len(clique) == 8:
            found.append(tuple(clique))
            return
        rest = cand
        while rest:
            bit = rest & -rest
            rest ^= bit
            j = bit.bit_length() - 1
            rec(clique + [j], cand & orth[j] & ((1 << j) - 1))

    for i in pool:
        rec([i], orth[i] & ((1 << i) - 1))
    return found


def neighbor_columns(frame):
    return [[1 if IP[a][b] else 0 for b in frame] for a in FRAME0]


def cross_entries(frame):
    return [[IP[a][b] for b in frame] for a in FRAME0]


def gram_identity(frame):
    """Return True when the F0-coordinate matrix N of F1 satisfies N^T N = 4 I."""
    entries = cross_entries(frame)
    for i in range(8):
        for j in range(8):
            product = sum(entries[k][i] * entries[k][j] for k in range(8))
            if product != (4 if i == j else 0):
                return False
    return True


def relative_pairs(frame):
    counts = Counter()
    for left, right in itertools.combinations(frame, 2):
        shared = sum(
            1 for a in FRAME0 if IP[left][a] and IP[right][a]
        )
        counts[shared] += 1
    return tuple(sorted(counts.items()))


def share4_components(frame):
    parent = {line: line for line in frame}

    def find(line):
        while parent[line] != line:
            parent[line] = parent[parent[line]]
            line = parent[line]
        return line

    def unite(left, right):
        left, right = find(left), find(right)
        if left != right:
            parent[right] = left

    edges = []
    for left, right in itertools.combinations(frame, 2):
        shared = sum(1 for a in FRAME0 if IP[left][a] and IP[right][a])
        if shared == 4:
            edges.append((left, right))
            unite(left, right)
    groups = defaultdict(list)
    for line in frame:
        groups[find(line)].append(line)
    return edges, list(groups.values())


def label_rows(frame):
    indices = list(FRAME0) + list(frame)
    return [
        sum(label_bit(indices[i], indices[j]) << j for j in range(16))
        for i in range(16)
    ], indices


def pair_rank(indices, left, right):
    rows = []
    for i in left:
        value = 0
        for column, j in enumerate(right):
            value |= label_bit(indices[i], indices[j]) << column
        rows.append(value)
    return f2_rank(rows)


def perfect_matchings(adjacency):
    matchings = []

    def rec(row, used, assignment):
        if row == 8:
            matchings.append(tuple(assignment))
            return
        rest = adjacency[row] & ~used
        while rest:
            bit = rest & -rest
            rest ^= bit
            assignment[row] = bit.bit_length() - 1
            rec(row + 1, used | bit, assignment)

    rec(0, 0, [-1] * 8)
    return matchings


def masked_zero_pattern(indices, matrix):
    for i, left in enumerate(indices):
        for j, right in enumerate(indices):
            if i == j:
                if matrix[i][j] != 4:
                    return False
            elif IP[left][right] == 0 and matrix[i][j] != 0:
                return False
    return True


def matching_matrix(indices, assignment):
    """Integer matrix 4 * sum_a u_a u_a^T for one perfect matching."""
    matrix = [[0] * 16 for _ in range(16)]
    for row, column in enumerate(assignment):
        support = (row, 8 + column)
        for i in support:
            for j in support:
                matrix[i][j] += 4
    return matrix


def block_multiply_ok(assignment):
    """Unsigned permutation B and C = B^T satisfy C B = I."""
    matrix_b = [[1 if assignment[i] == j else 0 for j in range(8)] for i in range(8)]
    product = [
        [sum(matrix_b[k][a] * matrix_b[k][b] for k in range(8)) for b in range(8)]
        for a in range(8)
    ]
    return product == [[1 if a == b else 0 for b in range(8)] for a in range(8)]


EXPECTED = {
    ((0, 4), (2, 24)): {"frames": 896, "rank": 8, "distinct": 16, "share": "none"},
    ((0, 8), (2, 16), (4, 4)): {
        "frames": 336,
        "rank": 6,
        "distinct": 8,
        "share": "matching",
    },
    ((0, 16), (4, 12)): {
        "frames": 28,
        "rank": 4,
        "distinct": 4,
        "share": "two-cliques",
    },
}


def component_kind(groups, edges):
    sizes = tuple(sorted(len(group) for group in groups))
    if edges == [] and sizes == (1,) * 8:
        return "none"
    if sizes == (2,) * 4 and len(edges) == 4:
        return "matching"
    if sizes == (4, 4) and len(edges) == 12:
        cliques = True
        for group in groups:
            present = {
                tuple(sorted(pair))
                for pair in itertools.combinations(group, 2)
                if tuple(sorted(pair)) in {tuple(sorted(edge)) for edge in edges}
            }
            cliques = cliques and len(present) == 6
        if cliques:
            return "two-cliques"
    return "other:" + str(sizes)


def audit():
    if any(IP[i][i] != 2 for i in range(120)):
        fail("a root line is not length-squared 2")
    off = {
        IP[i][j]
        for i in range(120)
        for j in range(120)
        if i != j
    }
    check(
        "geometry",
        off == {-1, 0, 1}
        and all(IP[a][b] == (2 if a == b else 0) for a in FRAME0 for b in FRAME0),
        "120 lines, off-diagonal inner products {-1,0,1}, F0 orthogonal of length 2",
    )
    # F0 spans the ambient 8 coordinates: each plane pair inverts to the two axes.
    spans = True
    for plane in range(4):
        plus = LINES[FRAME0[2 * plane]]
        minus = LINES[FRAME0[2 * plane + 1]]
        axis_even = tuple((p + m) // 4 for p, m in zip(plus, minus))
        axis_odd = tuple((p - m) // 4 for p, m in zip(plus, minus))
        expect_even = tuple(1 if k == 2 * plane else 0 for k in range(8))
        expect_odd = tuple(1 if k == 2 * plane + 1 else 0 for k in range(8))
        spans = spans and axis_even == expect_even and axis_odd == expect_odd
    check(
        "frame-basis",
        spans,
        "the four orthogonal pairs of F0 span all eight coordinates",
    )

    frames = frames_in(P112)
    type_counts = Counter()
    rank_counts = Counter()
    matching_total = 0
    term_checks = 0
    share_ok = True
    gram_ok = True
    masked_ok = True
    separated_ok = True
    identical_iff_share4 = True

    for frame in frames:
        kind = relative_pairs(frame)
        type_counts[kind] += 1
        rows, indices = label_rows(frame)
        rank = f2_rank(rows)
        distinct = len(set(rows))
        rank_counts[(kind, rank, distinct)] += 1
        edges, groups = share4_components(frame)
        share_ok = share_ok and component_kind(groups, edges) == EXPECTED[kind]["share"]
        adjacency_bits = []
        for row in neighbor_columns(frame):
            bits = 0
            for column, bit in enumerate(row):
                bits |= bit << column
            adjacency_bits.append(bits)
        gram_ok = gram_ok and gram_identity(frame)
        # Degree 4 is the diagonal of N^T N = 4 I, checked inside gram_identity.
        matchings = perfect_matchings(adjacency_bits)
        if not matchings:
            separated_ok = False
        matching_total += len(matchings)
        for assignment in matchings:
            for row, column in enumerate(assignment):
                left = FRAME0[row]
                right = frame[column]
                block = [
                    [label_bit(left, left), label_bit(left, right)],
                    [label_bit(right, left), label_bit(right, right)],
                ]
                separated_ok = (
                    separated_ok
                    and IP[left][right] in (1, -1)
                    and block == [[1, 0], [0, 1]]
                    and pair_rank(indices, [row, 8 + column], [row, 8 + column]) == 2
                )
                term_checks += 1
        assignment = matchings[0]
        matrix = matching_matrix(indices, assignment)
        masked_ok = masked_ok and masked_zero_pattern(indices, matrix)
        separated_ok = separated_ok and block_multiply_ok(assignment)
        # Equal F1 label rows are exactly the share-4 classes.
        by_row = defaultdict(set)
        for local, line in enumerate(frame):
            by_row[rows[8 + local]].add(line)
        share_classes = [set(group) for group in groups]
        identical_iff_share4 = identical_iff_share4 and sorted(
            by_row.values(), key=lambda group: min(group)
        ) == sorted(share_classes, key=min)

    check(
        "census",
        len(frames) == 1260 and type_counts == Counter(
            {kind: data["frames"] for kind, data in EXPECTED.items()}
        ),
        "1260 frames; types 896, 336, 28",
    )
    check(
        "label-rank",
        rank_counts
        == Counter(
            {
                (kind, data["rank"], data["distinct"]): data["frames"]
                for kind, data in EXPECTED.items()
            }
        ),
        "label rank/distinct rows are 8/16, 6/8, 4/4 on the three types",
    )
    check(
        "share4-graph",
        share_ok and identical_iff_share4,
        "share-4 graph is empty, a perfect matching, or two 4-cliques, and equals equal F1 label rows",
    )
    check(
        "cross-gram",
        gram_ok,
        "every second frame has cross-Gram N^T N = 4 I with entries in {-1,0,1}",
    )
    check(
        "separated-cost",
        separated_ok and masked_ok and term_checks == 8 * matching_total and matching_total > 1260,
        "every perfect matching gives eight label blocks I_2 and a masked matrix; matchings=%d"
        % matching_total,
    )
    return matching_total


def histogram_matches(counts):
    return counts == {kind: data["frames"] for kind, data in EXPECTED.items()}


def negative_controls():
    # An orthogonal pair does not give the cost-2 block.
    frame = next(iter(frames_in(P112)))
    orthogonal = next(
        line for line in frame if IP[FRAME0[0]][line] == 0
    )
    block = [
        [label_bit(FRAME0[0], FRAME0[0]), label_bit(FRAME0[0], orthogonal)],
        [label_bit(orthogonal, FRAME0[0]), label_bit(orthogonal, orthogonal)],
    ]
    check(
        "control-orthogonal-pair",
        block == [[1, 1], [1, 1]] and f2_rank([0b11, 0b11]) == 1,
        "an orthogonal pair has label block J_2 of rank 1, so it is not a cost-2 matching term",
    )
    # A zero cross block fails C B = I and has Schur rank 8, total rank 16.
    zero = [[0] * 8 for _ in range(8)]
    product = [
        [sum(zero[i][k] * zero[k][j] for k in range(8)) for j in range(8)]
        for i in range(8)
    ]
    schur = [
        [(1 if i == j else 0) - product[i][j] for j in range(8)]
        for i in range(8)
    ]
    check(
        "control-zero-cross",
        schur == [[1 if i == j else 0 for j in range(8)] for i in range(8)]
        and f2_rank([1 << i for i in range(8)]) == 8,
        "B = C = 0 has Schur complement I, so the block rank is 16 rather than 8",
    )
    # Corrupting an orthogonal entry leaves the masked pattern.
    indices = list(FRAME0) + list(frame)
    matrix = [[4 if i == j else 0 for j in range(16)] for i in range(16)]
    intact = masked_zero_pattern(indices, matrix)
    for i, left in enumerate(indices):
        for j, right in enumerate(indices):
            if i != j and IP[left][right] == 0:
                matrix[i][j] = 1
                broken = not masked_zero_pattern(indices, matrix)
                matrix[i][j] = 0
                break
        else:
            continue
        break
    check(
        "control-mask-corruption",
        intact and broken,
        "diagonal 4 with orthogonal zeros passes, and one corrupted orthogonal entry fails",
    )
    # Zeroing one row of a real cross-Gram destroys N^T N = 4 I.
    entries = cross_entries(frame)
    original = gram_identity(frame)
    saved = entries[0][:]
    entries[0] = [0] * 8
    # gram_identity reads IP, so test the mutated matrix directly.
    mutated = all(
        sum(entries[k][i] * entries[k][j] for k in range(8)) == (4 if i == j else 0)
        for i in range(8)
        for j in range(8)
    )
    entries[0] = saved
    check(
        "control-singular-cross",
        original and not mutated,
        "zeroing one row of a real cross-Gram makes N^T N differ from 4 I",
    )
    observed = {kind: data["frames"] for kind, data in EXPECTED.items()}
    drifted = dict(observed)
    drifted[((0, 4), (2, 24))] = 895
    check(
        "control-census-drift",
        histogram_matches(observed) and not histogram_matches(drifted),
        "the type histogram accepts 896+336+28 and rejects a one-frame drift",
    )


def main():
    if not __debug__:
        sys.exit("assertions must be enabled")
    matching_total = audit()
    negative_controls()
    print(
        "PASS_DOUBLE_FRAME_MASKED_RANK frames=1260 types=896+336+28 "
        "label-ranks=8/6/4 matchings=%d controls=5" % matching_total
    )


if __name__ == "__main__":
    main()
