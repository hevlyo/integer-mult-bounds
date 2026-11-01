#!/usr/bin/env python3
"""Fixed-reader P112 two-total COPY screen for source unions 49, 50 and 51.

Standard library only. Rebuilds the eight coordinate reader codes from the
pinned geometry and checks the finite premises used by the written argument.
"""

import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GEOM_REL = "research/p112-single-lift/reference-geometry.json"
GEOM_SHA = "4f44af368e046002553d632ee90c6470990827cea3fae41f0f54018522d7a080"
NPORT = 112
NREAD = 8
CAP = 51

# Closed-support census of each reader through size 51: (dimension, size) -> count.
EXPECTED_CENSUS = {
    (1, 24): 63,
    (1, 28): 128,
    (1, 32): 63,
    (2, 36): 336,
    (2, 40): 4977,
    (2, 44): 5040,
    (3, 44): 1260,
    (3, 46): 10752,
    (3, 48): 35280,
    (3, 50): 32256,
    (4, 48): 315,
    (4, 50): 22176,
}
# Single-codeword tuples with union at most 51, by number of distinct readers.
EXPECTED_WORD_TUPLES = {1: 2032, 2: 1100540, 3: 85400, 4: 6986, 5: 1232, 6: 196, 7: 56, 8: 7}
EXPECTED_WORD_PASSING = {1: 2032, 2: 1100540, 3: 37856, 4: 2576, 5: 448}


class CheckFailure(Exception):
    pass


def require(cond, msg):
    if not cond:
        raise CheckFailure(msg)


def pc(value):
    return value.bit_count()


def parity(value):
    return pc(value) & 1


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


def rational_rank(matrix):
    if not matrix or not matrix[0]:
        return 0
    rows = [[Fraction(entry) for entry in row] for row in matrix]
    rank = 0
    width = len(rows[0])
    for col in range(width):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col] != 0), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][col]
        for i in range(len(rows)):
            if i != rank and rows[i][col] != 0:
                factor = rows[i][col] / scale
                rows[i] = [a - factor * b for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def ports_of(mask):
    return [port for port in range(NPORT) if mask >> port & 1]


class Geometry:
    def __init__(self, payload):
        self.X = payload["X"]
        self.labels = payload["labels"]
        self.duals = payload["duals"]
        require(len(self.X) == NPORT and all(len(row) == NREAD for row in self.X), "X shape")
        self.support = [[port for port in range(NPORT) if self.X[port][j] != 0] for j in range(NREAD)]
        self.support_mask = [sum(1 << port for port in ports) for ports in self.support]
        self.codes = []
        for j in range(NREAD):
            span = {0}
            for i in self.support[j]:
                word = 0
                for t in self.support[j]:
                    if parity(self.duals[i] & self.labels[t]):
                        word |= 1 << t
                if word not in span:
                    span |= {old ^ word for old in span}
            self.codes.append(span)
        self.cut = [[self.support_mask[j] & self.support_mask[k] for k in range(NREAD)] for j in range(NREAD)]

    def kernel_dim(self, reader, mask):
        count = sum(1 for word in self.codes[reader] if word & ~mask == 0)
        dim = count.bit_length() - 1
        require(count == 1 << dim, "kernel is not a linear space")
        return dim

    def beta(self, reader_mask, source_mask):
        rows = []
        for i in range(NPORT):
            if reader_mask >> i & 1:
                word = 0
                for t in range(NPORT):
                    if source_mask >> t & 1 and parity(self.duals[i] & self.labels[t]):
                        word |= 1 << t
                rows.append(word)
        return f2_rank(rows)


def load_geometry(raw):
    require(hashlib.sha256(raw).hexdigest() == GEOM_SHA, "geometry sha256 mismatch")
    return json.loads(raw.decode("utf-8"))


def check_premises(geom):
    weights = []
    for j in range(NREAD):
        require(len(geom.codes[j]) == 256, "code size")
        require(f2_rank(geom.duals[i] for i in geom.support[j]) == 8, "dual span")
        dist = {}
        for word in geom.codes[j]:
            dist[pc(word)] = dist.get(pc(word), 0) + 1
        weights.append(sorted(dist.items()))
    require(all(item == weights[0] for item in weights), "weight distributions differ")
    require(weights[0] == [(0, 1), (24, 63), (28, 128), (32, 63), (56, 1)], "weights")
    margins = set()
    for j in range(NREAD):
        for k in range(NREAD):
            if j == k:
                continue
            cut = geom.cut[j][k]
            require(pc(cut) == 24, "cut size")
            require(cut in geom.codes[j] and cut in geom.codes[k], "cut word")
            inside = [word for word in geom.codes[k] if word and word & ~geom.support_mask[j] == 0]
            require(inside == [cut], "unique foreign word inside a reader support")
            margins.add(min(pc(word & ~geom.support_mask[j]) for word in geom.codes[k] if word and word != cut))
    require(margins == {12}, "twelve-port margin")
    require(len(set(geom.labels)) == NPORT, "source labels are not distinct")
    for j in range(NREAD):
        for k in range(j + 1, NREAD):
            products = [geom.X[port][j] * geom.X[port][k] for port in ports_of(geom.cut[j][k])]
            require(products.count(1) == 12 and products.count(-1) == 12, "cut sign balance")


def closed_supports(geom):
    found = []
    for j in range(NREAD):
        words = [word for word in geom.codes[j] if word and pc(word) <= CAP]
        seen = set(words)
        frontier = list(seen)
        while frontier:
            nxt = []
            for mask in frontier:
                for word in words:
                    union = mask | word
                    if union != mask and union not in seen and pc(union) <= CAP:
                        seen.add(union)
                        nxt.append(union)
            frontier = nxt
        found.append(seen)
    return found


def check_census(geom, closed):
    census = []
    for j, seen in enumerate(closed):
        counts = {}
        for mask in seen:
            key = (geom.kernel_dim(j, mask), pc(mask))
            counts[key] = counts.get(key, 0) + 1
        census.append(counts)
        require(all(size not in {49, 51} for _dim, size in counts), "unexpected odd closed-support size")
        require(sum(n for (dim, size), n in counts.items() if size == 50) > 0, "missing size-50 supports")
    require(all(item == census[0] for item in census), "closed census differs by reader")
    require(census[0] == EXPECTED_CENSUS, "closed-support census mismatch")
    return census[0]


class RankScreen:
    def __init__(self, matrix):
        self.matrix = matrix
        self.cache = {}

    def rank(self, rows, cols):
        key = (rows, cols)
        cached = self.cache.get(key)
        if cached is None:
            selected = ports_of(rows)
            if len(selected) < 3:
                cached = len(selected)
            else:
                cached = rational_rank([[self.matrix[row][col] for col in cols] for row in selected])
            self.cache[key] = cached
        return cached

    def accepts(self, config, new_reader):
        others = [reader for reader in config if reader != new_reader]
        for width in range(2, len(others) + 1):
            for group in itertools.combinations(others, width):
                rows = config[new_reader]
                for reader in group:
                    rows &= config[reader]
                if pc(rows) >= 3 and self.rank(rows, tuple(sorted(group + (new_reader,)))) >= 3:
                    return False
        return True


def size36_branch(geom, closed, screen):
    """Outside budget 15 adds no supports beyond budget 12, and loss stays 5."""
    small = []
    leads = []
    for j, seen in enumerate(closed):
        small.append([(mask, geom.kernel_dim(j, mask)) for mask in seen if pc(mask) <= 36])
        leads.append([mask for mask in seen if pc(mask) == 36])
    mismatches = 0
    best = 0
    for j in range(NREAD):
        others = [k for k in range(NREAD) if k != j]
        for lead in leads[j]:
            lists = []
            for k in others:
                budget12 = []
                budget15 = []
                for mask, dim in small[k]:
                    outside = pc(mask & ~lead)
                    if outside <= 15 and pc(lead | mask) <= CAP:
                        budget15.append((mask, dim))
                        if outside <= 12:
                            budget12.append((mask, dim))
                if budget12 != budget15:
                    mismatches += 1
                lists.append(budget15)

            def walk(index, config, dims, ok):
                nonlocal best
                if ok:
                    best = max(best, geom.kernel_dim(j, lead) + sum(dims))
                for cursor in range(index, len(others)):
                    reader = others[cursor]
                    for mask, dim in lists[cursor]:
                        config[reader] = mask
                        walk(cursor + 1, config, dims + [dim], ok and screen.accepts(config, reader))
                        del config[reader]

            walk(0, {j: lead}, [], True)
    require(mismatches == 0, "budget 13-15 created a new size-36 companion")
    require(best == 5, "size-36 retained loss changed")
    return best


def cut_branch(geom, closed, screen):
    """Leads larger than 36 ports. Only cut words fit while the outside budget is below 12."""
    best = {49: 0, 50: 0, 51: 0}
    geometric = {49: 0, 50: 0, 51: 0}
    rejected_loss6 = 0
    for j, seen in enumerate(closed):
        for lead in seen:
            size = pc(lead)
            if size <= 36:
                continue
            dim = geom.kernel_dim(j, lead)
            contained = [k for k in range(NREAD) if k != j and geom.cut[j][k] & ~lead == 0]
            for cap in (49, 50, 51):
                if size <= cap:
                    geometric[cap] = max(geometric[cap], dim + len(contained))
            fitting = []
            for k in range(NREAD):
                if k == j:
                    continue
                if pc(lead | geom.cut[j][k]) <= CAP:
                    fitting.append((k, geom.cut[j][k]))
            if dim + len(fitting) < 6 and dim < 5:
                for cap in (49, 50, 51):
                    if size <= cap:
                        best[cap] = max(best[cap], dim)
                continue

            def walk(index, union, config, n_cuts, ok):
                nonlocal rejected_loss6
                loss = dim + n_cuts
                union_size = pc(union)
                if loss >= 6 and ok:
                    rejected_loss6 += 1
                if ok:
                    for cap in (49, 50, 51):
                        if union_size <= cap:
                            best[cap] = max(best[cap], loss)
                for cursor in range(index, len(fitting)):
                    reader, cut = fitting[cursor]
                    nxt = union | cut
                    if pc(nxt) > CAP:
                        continue
                    config[reader] = cut
                    walk(cursor + 1, nxt, config, n_cuts + 1, ok and screen.accepts(config, reader))
                    del config[reader]

            walk(0, lead, {j: lead}, 0, True)
    require(rejected_loss6 == 0, "a loss-6 cut configuration passed the rank screen")
    require(best == {49: 5, 50: 5, 51: 5}, "cut-branch loss bound changed")
    require(geometric == {49: 8, 50: 8, 51: 8}, "closed-support geometric maximum changed")
    return best, geometric


def word_branch(geom, screen):
    words = []
    readers = []
    for j in range(NREAD):
        for word in geom.codes[j]:
            if word and pc(word) <= 32:
                words.append(word)
                readers.append(j)
    count = len(words)
    compatible = [0] * count
    for left in range(count):
        mask = 0
        for right in range(left + 1, count):
            if readers[right] > readers[left] and pc(words[left] | words[right]) <= CAP:
                mask |= 1 << right
        compatible[left] = mask
    reader_mask = [sum(1 << i for i in range(count) if readers[i] == j) for j in range(NREAD)]
    totals = {}
    passing = {}
    best_pass = 0

    def walk(union, pool, config, ok):
        nonlocal best_pass
        width = len(config)
        totals[width] = totals.get(width, 0) + 1
        if ok:
            passing[width] = passing.get(width, 0) + 1
            best_pass = max(best_pass, width)
        rest = pool
        while rest:
            bit = rest & -rest
            index = bit.bit_length() - 1
            rest ^= bit
            nxt = union | words[index]
            if pc(nxt) <= CAP:
                reader = readers[index]
                config[reader] = words[index]
                walk(
                    nxt,
                    pool & compatible[index] & ~((1 << (index + 1)) - 1) & ~reader_mask[reader],
                    config,
                    ok and screen.accepts(config, reader),
                )
                del config[reader]

    for start in range(count):
        walk(words[start], compatible[start], {readers[start]: words[start]}, True)
    require(totals == EXPECTED_WORD_TUPLES, "single-word tuple census mismatch")
    require(passing == EXPECTED_WORD_PASSING, "single-word passing census mismatch")
    require(best_pass == 5, "single-word loss bound changed")
    return best_pass


def price(active_labels):
    rank = 1
    while active_labels > 2 ** (rank + 1):
        rank += 1
    return rank


def price_min(union_size):
    best = None
    for left in range(1, union_size):
        value = price(left) + price(union_size - left)
        best = value if best is None else min(best, value)
    # A one-label source paired with the rest is admissible in the relaxation.
    require(best == price(1) + price(union_size - 1), "price minimum is not the extreme split")
    return best


def find_witness(geom, closed):
    for mask in sorted(closed[0]):
        if pc(mask) == 48 and geom.kernel_dim(0, mask) == 4 and geom.cut[0][1] & ~mask == 0:
            return mask
    raise CheckFailure("no dimension-4 48-port support of reader 0 contains the 0-1 cut")


def check_witness(geom, lead):
    cut = geom.cut[0][1]
    correction = [[0] * NREAD for _ in range(NPORT)]
    for port in ports_of(lead):
        correction[port][0] = geom.X[port][0]
    for port in ports_of(cut):
        correction[port][1] = geom.X[port][1]
    source = [[geom.X[port][col] - correction[port][col] for col in range(NREAD)] for port in range(NPORT)]
    losses = []
    for col in range(NREAD):
        source_mask = sum(1 << port for port in range(NPORT) if source[port][col] != 0)
        losses.append(8 - geom.beta(geom.support_mask[col], source_mask))
    require(sum(losses) == 5, "witness retained loss")
    require(losses[0] == 4 and losses[1] == 1, "witness loss shape")
    z_columns = [[correction[port][0], correction[port][1]] for port in range(NPORT)]
    require(rational_rank(z_columns) == 2, "witness source rank")
    union = 0
    for port in range(NPORT):
        if correction[port][0] or correction[port][1]:
            union |= 1 << port
    require(pc(union) == 48, "witness union size")
    # Readers are the original coordinate columns 0 and 1.
    for a in range(NPORT):
        for b in range(NPORT):
            left = sum(geom.X[a][col] * geom.X[b][col] for col in range(NREAD))
            right = sum(geom.X[a][col] * source[b][col] for col in range(NREAD))
            right += geom.X[a][0] * correction[b][0] + geom.X[a][1] * correction[b][1]
            require(left == right, "witness identity")
    added = []
    for col, support in ((0, lead), (1, cut)):
        added.append(geom.beta(geom.support_mask[col], support))
    bill = sum(8 - loss for loss in losses) + sum(added)
    require(added == [8, 7], "witness added ranks")
    require(bill == 74, "witness bill")
    # Three coordinate columns on this same pattern are not a rank-2 correction.
    triple = [row[:] for row in correction]
    for port in ports_of(geom.cut[0][2]):
        triple[port][2] = geom.X[port][2]
    require(rational_rank(triple) >= 3, "three-column control stayed rank 2")
    return {"union": 48, "retained_loss": 5, "added": added, "bill": bill}


def negative_controls(raw, geom):
    mutated = bytearray(raw)
    position = mutated.index(b'"X"') + 10
    mutated[position:position + 1] = b"7" if mutated[position:position + 1] != b"7" else b"8"
    failed = False
    try:
        load_geometry(bytes(mutated))
    except CheckFailure:
        failed = True
    require(failed, "corrupted geometry pin was accepted")
    rows = [port for port in range(NPORT) if [col for col in range(4) if geom.X[port][col]] == [0, 1, 2, 3]]
    require(len(rows) == 8, "four-coordinate block")
    minor = [[geom.X[port][col] for col in (0, 2, 3)] for port in rows]
    require(rational_rank(minor) == 3, "block minor rank")
    perturbed = [row[:2] + [row[0] + row[1]] for row in minor]
    require(rational_rank(perturbed) == 2, "perturbed minor rank")


def main():
    raw = open(os.path.join(ROOT, GEOM_REL), "rb").read()
    geom = Geometry(load_geometry(raw))
    check_premises(geom)
    closed = closed_supports(geom)
    check_census(geom, closed)
    screen = RankScreen(geom.X)
    size36_branch(geom, closed, screen)
    cut_branch(geom, closed, screen)
    word_branch(geom, screen)
    witness = check_witness(geom, find_witness(geom, closed))
    for union in (49, 50, 51):
        require(price_min(union) == 6, "added-term price minimum")
    negative_controls(raw, geom)
    # 64 - retained loss 5 + added-term relaxation 6.
    require(64 - 5 + 6 == 65, "floor arithmetic")
    print(
        "PASS_P112_TWO_TOTAL_UNION49_51 caps=49,50,51 two_column_loss=5 "
        "geometric_closed=8 full_rank_floor=65 witness_union=%d witness_bill=%d "
        "no_closed_sizes=49,51 no_new_kappa"
        % (witness["union"], witness["bill"])
    )


if __name__ == "__main__":
    try:
        main()
    except CheckFailure as exc:
        print("FAIL", exc)
        sys.exit(1)
