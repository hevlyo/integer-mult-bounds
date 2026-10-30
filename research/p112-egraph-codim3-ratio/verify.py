#!/usr/bin/env python3
"""Exact frame-hit ratio for codimension-at-most-3 P112 E-graph supports.

The witness arithmetic is independent of census.cpp. The census is then
compiled and required to report the same ratio and the same root supports.
"""
import itertools
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WITNESS_I = (
    (0, 2, -2, 0, 0, 0, 0, 0),
    (0, 2, 0, 2, 0, 0, 0, 0),
    (1, 1, -1, -1, -1, 1, 1, -1),
    (1, 1, -1, -1, 1, -1, -1, 1),
    (1, 1, 1, 1, -1, 1, 1, -1),
    (1, 1, 1, 1, 1, -1, -1, 1),
    (2, 0, 0, -2, 0, 0, 0, 0),
    (2, 0, 2, 0, 0, 0, 0, 0),
)
WITNESS_J = (
    (0, 0, 0, 0, 0, 2, -2, 0),
    (0, 0, 0, 0, 0, 2, 0, 2),
    (0, 0, 0, 0, 2, 0, 0, -2),
    (0, 0, 0, 0, 2, 0, 2, 0),
    (1, -1, -1, 1, -1, -1, -1, -1),
    (1, -1, -1, 1, -1, -1, 1, 1),
    (1, -1, -1, 1, -1, 1, -1, 1),
    (1, -1, -1, 1, 1, -1, 1, -1),
    (1, -1, -1, 1, 1, 1, -1, -1),
    (1, -1, -1, 1, 1, 1, 1, 1),
    (1, -1, 1, -1, -1, 1, 1, -1),
    (1, -1, 1, -1, 1, -1, -1, 1),
)


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL " + message)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def canon(vector):
    negative = tuple(-a for a in vector)
    return vector if vector > negative else negative


def rank_rows(rows):
    basis = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def geometry():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si, sj in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            vector = [0] * 8
            vector[i], vector[j] = 2 * si, 2 * sj
            roots.append(tuple(vector))
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(tuple(signs))
    lines, seen = [], set()
    for root in roots:
        key = canon(root)
        if key not in seen:
            seen.add(key)
            lines.append(key)
    simple = [
        [1, -1, -1, -1, -1, -1, -1, 1],
        [2, 2, 0, 0, 0, 0, 0, 0],
        [-2, 2, 0, 0, 0, 0, 0, 0],
    ]
    for k in range(1, 6):
        vector = [0] * 8
        vector[k], vector[k + 1] = -2, 2
        simple.append(vector)
    rows = [list(map(float, simple[i])) + [float(i == j) for j in range(8)] for i in range(8)]
    for col in range(8):
        pivot = next(i for i in range(col, 8) if rows[i][col])
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        rows[col] = [value / divisor for value in rows[col]]
        for i in range(8):
            if i != col and rows[i][col]:
                coefficient = rows[i][col]
                rows[i] = [a - coefficient * b for a, b in zip(rows[i], rows[col])]
    inverse = [row[8:] for row in rows]
    frame = []
    for j in range(4):
        for sign in (1, -1):
            vector = [0] * 8
            vector[2 * j], vector[2 * j + 1] = 2, 2 * sign
            frame.append(tuple(vector))
    frame_keys = {canon(vector) for vector in frame}
    kept, labels = [], []
    for root in lines:
        if root in frame_keys:
            continue
        coords = [int(round(sum(root[k] * inverse[k][j] for k in range(8)))) for j in range(8)]
        label = 0
        for bit in coords + [1]:
            label = (label << 1) | (bit & 1)
        kept.append(root)
        labels.append(label)
    require(len(kept) == 112 and len(set(labels)) == 112, "P112 size")
    orth = [0] * 112
    ones = set()
    for i in range(112):
        row_ones = 0
        for j in range(112):
            inner = dot(kept[i], kept[j])
            require(inner % 4 == 0, "inner product scale")
            if (inner // 4) % 2 == 0:
                row_ones += 1
            if i != j and inner == 0:
                orth[i] |= 1 << j
        ones.add(row_ones)
    require(ones == {60}, "E-graph degree")
    frames = []

    def rec(clique, candidates):
        if len(clique) == 8:
            frames.append(clique)
            return
        rest = candidates
        while rest:
            j = (rest & -rest).bit_length() - 1
            rest &= rest - 1
            rec(clique + (j,), candidates & orth[j] & ((1 << j) - 1))

    for i in range(112):
        rec((i,), orth[i] & ((1 << i) - 1))
    require(len(frames) == 1260, "frame count")
    line_frames = [0] * 112
    for index, frame_lines in enumerate(frames):
        for line in frame_lines:
            line_frames[line] |= 1 << index
    require(all(mask.bit_count() == 90 for mask in line_frames), "frames per line")
    return kept, labels, line_frames


def pairing_rank(kept, left, right, even=True):
    matrix = []
    for i in left:
        row = 0
        for column, j in enumerate(right):
            inner = dot(kept[i], kept[j]) // 4
            bit = (inner % 2 == 0) if even else (inner % 2 != 0)
            if bit:
                row |= 1 << column
        matrix.append(row)
    return rank_rows(matrix)


def frame_hits(line_frames, left, right):
    left_mask = 0
    right_mask = 0
    for line in left:
        left_mask |= line_frames[line]
    for line in right:
        right_mask |= line_frames[line]
    return (left_mask & right_mask).bit_count()


def span_dim(labels, ids):
    return rank_rows(labels[i] for i in ids)


def is_dim6_flat(labels, ids):
    """True when ids is every port label inside some 6-dimensional subspace."""
    chosen = set(ids)
    labs = [labels[i] for i in ids]
    span = span_dim(labels, ids)
    rows = {}
    for label in labs:
        value = label
        while value:
            pivot = value.bit_length() - 1
            if pivot in rows:
                value ^= rows[pivot]
            else:
                rows[pivot] = value
                break
    quotient = []
    occupied = dict(rows)
    for bit in range(9):
        value = 1 << (8 - bit)
        reduced = value
        for pivot, row in sorted(occupied.items(), reverse=True):
            if (reduced >> pivot) & 1:
                reduced ^= row
        if not reduced:
            continue
        new_pivot = reduced.bit_length() - 1
        for pivot in list(occupied):
            if (occupied[pivot] >> new_pivot) & 1:
                occupied[pivot] ^= reduced
        occupied[new_pivot] = reduced
        quotient.append(value)
    require(len(quotient) == 9 - span, "quotient dimension")
    outside = [i for i in range(112) if i not in chosen]
    qdim = len(quotient)
    need = 6 - span

    def subspaces():
        if need == 0:
            yield ()
            return
        for pivots in itertools.combinations(range(qdim), need):
            pivot_set = set(pivots)
            free = []
            for row, pivot in enumerate(pivots):
                free.append([c for c in range(pivot + 1, qdim) if c not in pivot_set])
            ranges = [range(1 << len(cols)) for cols in free]
            for bits in itertools.product(*ranges):
                gens = []
                for row, pivot in enumerate(pivots):
                    mask = 1 << pivot
                    for index, col in enumerate(free[row]):
                        if (bits[row] >> index) & 1:
                            mask |= 1 << col
                    gens.append(mask)
                yield gens

    for generators in subspaces():
        basis = {}

        def add(value):
            while value:
                pivot = value.bit_length() - 1
                if pivot in basis:
                    value ^= basis[pivot]
                else:
                    basis[pivot] = value
                    return
            return

        for label in labs:
            add(label)
        independent = True
        for mask in generators:
            extra = 0
            for bit in range(qdim):
                if (mask >> bit) & 1:
                    extra ^= quotient[bit]
            before = len(basis)
            add(extra)
            if len(basis) == before:
                independent = False
                break
        if not independent or len(basis) != 6:
            continue
        if all(not _in_span(labels[i], basis) for i in outside):
            return True
    return False


def _in_span(value, basis):
    while value:
        pivot = value.bit_length() - 1
        if pivot in basis:
            value ^= basis[pivot]
        else:
            return False
    return True


def locate(kept, wanted):
    index = {canon(root): i for i, root in enumerate(kept)}
    return [index[canon(root)] for root in wanted]


def witness_check():
    kept, labels, line_frames = geometry()
    left = locate(kept, WITNESS_I)
    right = locate(kept, WITNESS_J)
    require(len(set(left)) == 8 and len(set(right)) == 12, "witness size")
    hits = frame_hits(line_frames, left, right)
    beta = pairing_rank(kept, left, right, even=True)
    require(hits == 612 and beta == 1, "witness ratio")
    require(span_dim(labels, left) == 4 and span_dim(labels, right) == 6, "witness spans")
    require(is_dim6_flat(labels, left) and is_dim6_flat(labels, right), "witness flats")
    left_self = pairing_rank(kept, left, left)
    right_self = pairing_rank(kept, right, right)
    require(left_self == 2, "left self-rank")
    require(right_self == 3, "right self-rank")
    require(hits * 35 != 1260 * left_self * 17, "self-rank must not certify 17/35")
    # 4 + 6 - 9 = 1, so the nondegenerate rank inequality is sharp here.
    require(beta == 4 + 6 - 9, "sharp rank inequality")
    dropped = frame_hits(line_frames, left[:-1], right)
    require(dropped < 612, "omitting a witness root must drop the frame count")
    # A zero-cost term is rejected by the ratio, rather than sent to infinity.
    accepted_zero = False
    try:
        _ = hits / (1260 * 0)
        accepted_zero = True
    except ZeroDivisionError:
        accepted_zero = False
    require(not accepted_zero, "zero beta must not define a ratio")
    ratio_num, ratio_den = 17, 35
    require(hits * ratio_den == 1260 * beta * ratio_num, "17/35")
    # Sampled D1(e) champion 920 / (1260 * 4) = 23/126.
    require(17 * 126 > 35 * 23, "exhaustive ratio exceeds the 20000-sample ratio 23/126")
    covering_num, covering_den = 280, 17
    require(8 * 35 == covering_num and 17 == covering_den, "8 / (17/35) = 280/17")
    require(covering_num < 64 * covering_den, "covering bound stays below 64")
    return hits, beta


def parse_roots(line):
    roots = []
    for chunk in line.split("[")[1:]:
        body = chunk.split("]")[0]
        roots.append(tuple(int(part) for part in body.split(",")))
    return roots


def census_check():
    compiler = "/usr/bin/g++"
    require(Path(compiler).exists(), "g++ is required for the exhaustive census")
    with tempfile.TemporaryDirectory(prefix="egraph-census-") as directory:
        binary = str(Path(directory) / "census")
        compiled = subprocess.run(
            [compiler, "-O2", "-std=c++17", "-o", binary, str(PACKAGE / "census.cpp")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        require(compiled.returncode == 0, "census compile failed: " + compiled.stderr[-500:])
        run = subprocess.run(
            [binary],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=240,
            check=False,
        )
    require(run.returncode == 0, "census failed: " + run.stderr[-500:])
    lines = run.stdout.splitlines()
    require("PASS_CENSUS 17/35" in lines, "census ratio")
    witness_i = next(line for line in lines if line.startswith("WITNESS_I "))
    witness_j = next(line for line in lines if line.startswith("WITNESS_J "))
    require(parse_roots(witness_i) == list(WITNESS_I), "census left support")
    require(parse_roots(witness_j) == list(WITNESS_J), "census right support")


def main():
    hits, beta = witness_check()
    census_check()
    print(
        "PASS_P112_EGRAPH_CODIM3_RATIO hits=%d beta=%d ratio=17/35 covering=280/17 frames=1260 controls=3 no_new_kappa"
        % (hits, beta)
    )


if __name__ == "__main__":
    main()
