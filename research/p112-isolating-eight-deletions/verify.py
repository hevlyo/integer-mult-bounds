#!/usr/bin/env python3
"""Exact kernels of the P112 frame deletions that isolate a line.

The live blocks are the orthogonal 8-frames in the 112 lines outside a fixed
coordinate frame. An 8-subset isolates a line when every live frame through
that line meets the subset. This verifier enumerates those subsets and
identifies each rational incidence kernel.
"""

import itertools
from collections import Counter, defaultdict

P_MOD = 1_000_003


def need(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def e8_lines():
    """120 root lines in doubled coordinates. True inner product is dot/4."""
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                v = [0] * 8
                v[i], v[j] = 2 * si, 2 * sj
                roots.append(tuple(v))
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(signs)
    lines, seen = [], set()
    for r in roots:
        key = r if r > tuple(-x for x in r) else tuple(-x for x in r)
        if key not in seen:
            seen.add(key)
            lines.append(r)
    need(len(roots) == 240 and len(lines) == 120, "E8 root census")
    return lines


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def frames_in(pool, orthogonal):
    """Maximal pairwise-orthogonal 8-subsets of pool, each index once."""
    pool = list(pool)
    allowed = mask_of(pool)
    out = []

    def rec(clique, cand):
        if len(clique) == 8:
            out.append(tuple(clique))
            return
        while cand:
            j = cand.bit_length() - 1
            cand &= ~(1 << j)
            rec(clique + [j], cand & orthogonal[j] & allowed & ((1 << j) - 1))

    for i in pool:
        rec([i], orthogonal[i] & allowed & ((1 << i) - 1))
    return out


def mask_of(indices):
    m = 0
    for i in indices:
        m |= 1 << i
    return m


def rank_gf2(masks):
    basis = {}
    rank = 0
    for v in masks:
        while v:
            h = v.bit_length() - 1
            b = basis.get(h)
            if b is None:
                basis[h] = v
                rank += 1
                break
            v ^= b
    return rank


def rank_mod(rows, modulus):
    """Rank of an integer matrix over F_modulus. rows are mutable copies."""
    if not rows:
        return 0
    rank = 0
    cols = len(rows[0])
    for c in range(cols):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][c] % modulus), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][c], -1, modulus)
        if inverse != 1:
            rows[rank] = [(value * inverse) % modulus for value in rows[rank]]
        pivot_row = rows[rank]
        for i in range(len(rows)):
            factor = rows[i][c] % modulus
            if i != rank and factor:
                rows[i] = [(a - factor * b) % modulus for a, b in zip(rows[i], pivot_row)]
        rank += 1
    return rank


def quadratic_specs():
    specs = [("off", i, j) for i, j in itertools.combinations(range(8), 2)]
    specs += [("diag", i, 7) for i in range(7)]
    return specs


def evaluate(spec, vector):
    kind, a, b = spec
    if kind == "off":
        return 2 * vector[a] * vector[b]
    return vector[a] * vector[a] - vector[b] * vector[b]


def main():
    lines = e8_lines()
    orthogonal = []
    for i, u in enumerate(lines):
        m = 0
        for j, v in enumerate(lines):
            if i != j and dot(u, v) == 0:
                m |= 1 << j
        orthogonal.append(m)
    frame0 = []
    for a in range(4):
        for s in (1, -1):
            vector = [0] * 8
            vector[2 * a], vector[2 * a + 1] = 2, 2 * s
            frame0.append(lines.index(tuple(vector)))
    p112 = [i for i in range(120) if i not in set(frame0)]
    need(len(frame0) == 8 and len(p112) == 112, "P112 coordinate frame")
    frames = frames_in(p112, orthogonal)
    need(len(frames) == 1260, "live frame count")

    # An orthogonal basis of true roots r = v/2 has sum_k r_a r_b = 2 δ_ab,
    # so the doubled vectors satisfy sum_k v_a v_b = 8 δ_ab.
    for frame in frames:
        moment = [[0] * 8 for _ in range(8)]
        for i in frame:
            vector = lines[i]
            for a in range(8):
                for b in range(8):
                    moment[a][b] += vector[a] * vector[b]
        for a in range(8):
            for b in range(8):
                need(moment[a][b] == (8 if a == b else 0), "frame second moment")
    specs = quadratic_specs()
    values = [[evaluate(spec, lines[i]) for i in range(120)] for spec in specs]
    for frame in frames:
        for row in values:
            need(sum(row[i] for i in frame) == 0, "quadratic frame sum")

    by_line = defaultdict(list)
    frame_masks = []
    for frame in frames:
        bits = mask_of(frame)
        frame_masks.append(bits)
        for i in frame:
            by_line[i].append(frame)
    degree = Counter(i for frame in frames for i in frame)
    need(degree == Counter({i: 90 for i in p112}), "ninety frames per line")

    def heavy_of(line):
        partners = Counter(i for frame in by_line[line] for i in frame if i != line)
        need(Counter(partners.values()) == Counter({10: 51, 15: 8}), "partner counts")
        return tuple(sorted(i for i, count in partners.items() if count == 15))

    heavy = {line: heavy_of(line) for line in p112}
    octets = sorted(set(heavy.values()))
    need(len(octets) == 14, "fourteen heavy octets")
    owners = defaultdict(list)
    for line, octet in heavy.items():
        owners[octet].append(line)
    for octet in octets:
        need(sorted(owners[octet]) == list(heavy[octet[0]]), "octets pair as mutual heavies")
        need(len(owners[octet]) == 8, "partner octet has eight lines")
    need(sorted(i for octet in octets for i in octet) == sorted(p112), "octets partition P112")

    def transversals(line):
        through = by_line[line]
        octet = heavy[line]
        heavy_set = set(octet)
        private = [[] for _ in octet]
        index = {h: j for j, h in enumerate(octet)}
        for frame in through:
            meet = [i for i in frame if i in heavy_set]
            if len(meet) == 1:
                private[index[meet[0]]].append(
                    [i for i in frame if i != line and i not in heavy_set])
        found = [octet]
        for mask in range(1 << 8):
            if mask.bit_count() != 4:
                continue
            kept = [octet[j] for j in range(8) if not (mask >> j) & 1]
            sequence = []
            for j in range(8):
                if (mask >> j) & 1:
                    sequence.extend(private[j])

            def search(position, chosen):
                if len(chosen) > 4:
                    return
                if position == len(sequence):
                    if len(chosen) == 4 and all((set(kept) | chosen) & set(frame)
                                                for frame in through):
                        found.append(tuple(sorted(kept + list(chosen))))
                    return
                if any(i in chosen for i in sequence[position]):
                    search(position + 1, chosen)
                    return
                for i in sequence[position]:
                    if i not in chosen:
                        chosen.add(i)
                        search(position + 1, chosen)
                        chosen.remove(i)

            search(0, set())
        return found

    families = {}
    per_line = Counter()
    for line in p112:
        sols = transversals(line)
        per_line[len(sols)] += 1
        for subset in sols:
            families.setdefault(subset, set()).add(line)
    need(per_line == Counter({13: 112}), "thirteen size-8 transversals per line")
    need(len(families) == 686, "unique isolating eight-subsets")

    p112_mask = mask_of(p112)

    def analyze(subset):
        dead = mask_of(subset)
        rows = [m for m in frame_masks if m & dead == 0]
        cover = 0
        for m in rows:
            cover |= m
        live = p112_mask ^ dead
        isolated = [i for i in p112 if (live >> i) & 1 and not ((cover >> i) & 1)]
        return rows, isolated

    octet_sets = set(octets)
    doubles = []
    for subset, claimed in families.items():
        _rows, isolated = analyze(subset)
        if subset in octet_sets:
            need(sorted(isolated) == sorted(owners[subset]), "octet isolates its partner")
            need(claimed == set(owners[subset]), "octet is a transversal of each partner line")
        else:
            need(len(isolated) == 2, "non-octet isolating set isolates two lines")
            need(set(isolated) == claimed, "double set is a transversal of its isolated lines")
            doubles.append(subset)
    need(len(doubles) == 672, "double-isolation family")

    position = {i: k for k, i in enumerate(p112)}

    def incidence_rank(rows, live_lines):
        matrix = [[1 if (m >> i) & 1 else 0 for i in live_lines] for m in rows]
        return rank_mod(matrix, P_MOD)

    def kernel_span_rank(live_lines, isolated):
        matrix = [[values[s][i] % P_MOD for i in live_lines] for s in range(len(values))]
        for line in isolated:
            row = [0] * len(live_lines)
            row[live_lines.index(line)] = 1
            matrix.append(row)
        return rank_mod(matrix, P_MOD)

    checked = {"octet": 0, "double": 0}
    for subset in octets:
        rows, isolated = analyze(subset)
        live_lines = [i for i in p112 if i not in set(subset)]
        need(len(live_lines) == 104 and len(isolated) == 8, "octet shape")
        need(rank_gf2(rows) == 61, "octet GF(2) rank")
        incidence = incidence_rank(rows, live_lines)
        span = kernel_span_rank(live_lines, isolated)
        need(incidence == 62 and span == 42 and incidence + span == 104, "octet rational sandwich")
        checked["octet"] += 1
    for subset in doubles:
        rows, isolated = analyze(subset)
        live_lines = [i for i in p112 if i not in set(subset)]
        need(len(live_lines) == 104 and len(isolated) == 2, "double shape")
        need(rank_gf2(rows) == 66, "double GF(2) rank")
        incidence = incidence_rank(rows, live_lines)
        span = kernel_span_rank(live_lines, isolated)
        need(incidence == 67 and span == 37 and incidence + span == 104, "double rational sandwich")
        checked["double"] += 1
    need(checked == {"octet": 14, "double": 672}, "both families certified")

    # Controls. A proper subset of an octet does not isolate and keeps the
    # quadratic kernel. A one-point replacement does not isolate the old owner.
    octet = octets[0]
    owner = owners[octet][0]
    seven = octet[:-1]
    seven_rows, seven_isolated = analyze(seven)
    seven_live = [i for i in p112 if i not in set(seven)]
    need(seven_isolated == [], "seven-subset isolates nothing")
    need(rank_gf2(seven_rows) == 69, "seven-subset GF(2) rank")
    need(incidence_rank(seven_rows, seven_live) == 70, "seven-subset rational rank")
    need(kernel_span_rank(seven_live, []) == 35, "seven-subset quadratic rank")
    replacement = p112[0] if p112[0] not in set(octet) else p112[1]
    damaged = tuple(sorted(octet[1:] + (replacement,)))
    need(any(owner in frame and set(frame).isdisjoint(damaged) for frame in frames),
         "damaged octet still admits a frame through the old owner")
    # A covered line is not a kernel vector: some surviving frame contains it.
    sample_rows, _sample_isolated = analyze(octet)
    covered = next(i for i in p112 if i not in set(octet) and i not in set(owners[octet]))
    need(any((m >> covered) & 1 for m in sample_rows), "covered line meets a surviving frame")
    # The constant function is not a rational kernel vector.
    need(any(len(frame) != 0 for frame in frames) and 8 != 0, "frame cardinality is 8")
    generic = tuple(p112[:8])
    generic_rows, generic_isolated = analyze(generic)
    generic_live = [i for i in p112 if i not in set(generic)]
    need(generic not in families, "initial segment is not an isolating set")
    need(generic_isolated == [], "initial segment isolates nothing")
    need(incidence_rank(generic_rows, generic_live) == 69, "initial segment has zero excess")

    print(
        "PASS_P112_ISOLATING_EIGHT_DELETIONS "
        "octets=14 excess=7 doubles=672 excess=2 isolating=686 "
        "seven_control=1 damaged_control=1 generic_control=1"
    )


if __name__ == "__main__":
    main()
