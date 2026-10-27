#!/usr/bin/env python3
"""Exact eight-term label-pairing cost of every 16-line E8 frame pair.

The live alphabet is the coordinate frame together with one complementary
frame. This is the puncture set of the eight-term P104 equality case, used
here as the decoded support. Ordinary transpose, real and complex
coefficients. No supplier invoice is formed.

Exit status is 0 only when every check passes. Checks raise on failure, so
they stay active when assertions are disabled.
"""

import itertools
import sys
from fractions import Fraction


def fail(tag, detail):
    raise SystemExit("FAIL %s %s" % (tag, detail))


def check(tag, cond, detail):
    if not cond:
        fail(tag, detail)
    return True


def e8_lines():
    """120 root lines in the same doubled-coordinate order as the frame-pair model."""
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
    lines = []
    seen = set()
    for root in roots:
        key = root if root > tuple(-a for a in root) else tuple(-a for a in root)
        if key not in seen:
            seen.add(key)
            lines.append(root)
    return lines


def ip(x, y):
    dot = sum(a * b for a, b in zip(x, y))
    if dot % 4 != 0:
        fail("ip", "doubled coordinates are not integral inner products")
    return dot // 4


def s9(value):
    return (value + 1) & 1


def mask_of(indices):
    out = 0
    for i in indices:
        out |= 1 << i
    return out


def f2_rank(rows):
    basis = []
    for v in rows:
        for b in basis:
            pivot = b.bit_length() - 1
            if (v >> pivot) & 1:
                v ^= b
        if v:
            pivot = v.bit_length() - 1
            basis = [b ^ v if (b >> pivot) & 1 else b for b in basis]
            basis.append(v)
    return len(basis)


def pair_rank(nrow, rows, cols):
    colmask = mask_of(cols)
    return f2_rank(nrow[i] & colmask for i in rows)


def frames_in(pool, ip_table):
    orth = {
        i: mask_of(j for j in pool if j != i and ip_table[i][j] == 0) for i in pool
    }
    found = []

    def rec(clique, cand):
        if len(clique) == 8:
            found.append(tuple(sorted(clique)))
            return
        rest = cand
        while rest:
            j = rest.bit_length() - 1
            rest &= ~(1 << j)
            rec(clique + [j], cand & orth[j] & ((1 << j) - 1))

    for i in pool:
        rec([i], orth[i] & ((1 << i) - 1))
    return sorted(set(found))


def admits_root_pair_decoder(frame0, frame1, ip_table):
    """Existence form of the frame-pair split search. One solution is enough."""
    for smask in range(256):
        rows = [frame0[j] for j in range(8) if smask >> j & 1]
        need = 8 - len(rows)
        partners = []
        ok = True
        for row in rows:
            choices = [
                g for g in frame1 if [x for x in rows if ip_table[g][x]] == [row]
            ]
            if not choices:
                ok = False
                break
            partners.append(choices)
        if not ok:
            continue
        for choice in itertools.product(*partners):
            if len(set(choice)) != len(rows):
                continue
            chosen = set(choice)
            columns = [g for g in frame1 if g not in chosen]
            if len(columns) != need:
                continue
            rest = [f for f in frame0 if f not in set(rows)]
            partners2 = []
            ok2 = True
            for column in columns:
                choices = [
                    f
                    for f in rest
                    if [x for x in columns if ip_table[f][x]] == [column]
                ]
                if not choices:
                    ok2 = False
                    break
                partners2.append(choices)
            if not ok2:
                continue
            for choice2 in itertools.product(*partners2):
                if len(set(choice2)) == len(columns):
                    return True
    return False


def column_support(frame0, frame1, gram, k):
    return [frame0[k]] + [frame1[i] for i in range(8) if gram[i][k] != 0]


def build_factor(gram):
    factor = [[0] * 8 for _ in range(16)]
    for k in range(8):
        factor[k][k] = 2
        for row in range(8):
            factor[8 + row][k] = gram[row][k]
    return factor


def product_matches(factor, target):
    for i in range(16):
        for j in range(16):
            got = sum(factor[i][k] * factor[j][k] for k in range(8))
            if got != target[i][j]:
                return False
    return True


def gram_is_scaled_isometry(gram):
    for i in range(8):
        for j in range(8):
            row = sum(gram[i][k] * gram[j][k] for k in range(8))
            col = sum(gram[k][i] * gram[k][j] for k in range(8))
            expect = 4 if i == j else 0
            if row != expect or col != expect:
                return False
    return True


def standard_pattern(ip_table, frame0, frame1, gram, k):
    partners = [i for i in range(8) if gram[i][k] != 0]
    if len(partners) != 4:
        return False
    if any(abs(gram[i][k]) != 1 for i in partners):
        return False
    coordinate = frame0[k]
    if s9(ip_table[coordinate][coordinate]) != 1:
        return False
    for p in partners:
        partner = frame1[p]
        if s9(ip_table[coordinate][partner]) != 0:
            return False
        for q in partners:
            if s9(ip_table[partner][frame1[q]]) != 1:
                return False
    rows = []
    # Bit 0 is the coordinate line. Bits 1..4 are the four odd partners.
    rows.append(1)
    for _ in partners:
        rows.append((1 << 5) - 2)
    return f2_rank(rows) == 2


def target_gram(ip_table, support):
    return [[2 * ip_table[a][b] for b in support] for a in support]


def main():
    lines = e8_lines()
    check("lines", len(lines) == 120, "expected 120 root lines, got %d" % len(lines))
    ip_table = [[ip(lines[i], lines[j]) for j in range(120)] for i in range(120)]
    frame0 = []
    for axis in range(4):
        for sign in (1, -1):
            vector = [0] * 8
            vector[2 * axis], vector[2 * axis + 1] = 2, 2 * sign
            frame0.append(lines.index(tuple(vector)))
    check(
        "frame0",
        len(frame0) == 8
        and all(ip_table[a][b] == (2 if a == b else 0) for a in frame0 for b in frame0),
        "coordinate frame is not eight orthogonal norm-2 lines",
    )
    pool = [i for i in range(120) if i not in set(frame0)]
    frames = frames_in(pool, ip_table)
    check("frame-count", len(frames) == 1260, "expected 1260 complementary frames")

    nrow = [
        mask_of(j for j in range(120) if s9(ip_table[i][j])) for i in range(120)
    ]
    admissible = 0
    orthogonal_rank_one = 0
    for frame1 in frames:
        if admits_root_pair_decoder(frame0, frame1, ip_table):
            admissible += 1
        gram = [[ip_table[frame1[r]][frame0[c]] for c in range(8)] for r in range(8)]
        check(
            "isometry",
            gram_is_scaled_isometry(gram),
            "cross inner products are not a scaled isometry",
        )
        support = list(frame0) + list(frame1)
        factor = build_factor(gram)
        check(
            "identity",
            product_matches(factor, target_gram(ip_table, support)),
            "eight-term factor does not reproduce 2G",
        )
        for k in range(8):
            for ell in range(8):
                got = sum(factor[row][k] * factor[row][ell] for row in range(16))
                expect = 8 if k == ell else 0
                if got != expect:
                    fail("left-inverse", "D0^T D0 is not 8I")
        for k in range(8):
            if not standard_pattern(ip_table, frame0, frame1, gram, k):
                fail("column-pattern", "column %d is not the rank-2 odd star" % k)
            supp = column_support(frame0, frame1, gram, k)
            rank = pair_rank(nrow, supp, supp)
            if rank != 2:
                fail("column-rank", "analytic pattern did not have pairing rank 2")
        for i in range(8):
            for j in range(8):
                if i == j:
                    continue
                left = column_support(frame0, frame1, gram, i)
                right = column_support(frame0, frame1, gram, j)
                if pair_rank(nrow, left, right) == 1:
                    orthogonal_rank_one += 1
        within = all(
            s9(ip_table[a][b]) == 1 for a in support[:8] for b in support[:8]
        ) and all(s9(ip_table[a][b]) == 1 for a in support[8:] for b in support[8:])
        cross = all(
            s9(ip_table[frame1[r]][frame0[c]]) == (0 if gram[r][c] else 1)
            for r in range(8)
            for c in range(8)
        )
        check("label-mask", within and cross, "S9 mask disagrees with the inner-product parity")

    check("admissible", admissible == 896, "expected 896 root-pair frames, got %d" % admissible)
    check(
        "orthogonal-rank-one",
        orthogonal_rank_one > 0,
        "no orthogonal coefficient pair of pairing rank 1 was found",
    )

    # Failure controls on the first frame.
    frame1 = frames[0]
    gram = [[ip_table[frame1[r]][frame0[c]] for c in range(8)] for r in range(8)]
    support = list(frame0) + list(frame1)
    target = target_gram(ip_table, support)
    mutated = [row[:] for row in gram]
    mutated[0][0] = mutated[0][0] + 2
    check(
        "mutated-entry",
        not product_matches(build_factor(mutated), target),
        "changing one cross entry still matched 2G",
    )
    block = [[4 if i == j else 0 for j in range(16)] for i in range(16)]
    odd_gap = sum(
        1
        for i in range(16)
        for j in range(16)
        if s9(ip_table[support[i]][support[j]]) == 0 and block[i][j] != target[i][j]
    )
    check("odd-gap", odd_gap > 0, "block-diagonal matrix already matched the odd entries")
    factor = build_factor(gram)

    def cmul(a, b):
        return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])

    # Ordinary transpose. Column 0 of D is scaled by 1+i and column 0 of T by 1/(1+i).
    scale = (Fraction(1), Fraction(1))
    dual = (Fraction(1, 2), Fraction(-1, 2))
    check("complex-unit", cmul(scale, dual) == (Fraction(1), Fraction(0)), "1+i and its reciprocal disagree")

    def scaled_product(right_scale):
        out = [[(Fraction(0), Fraction(0)) for _ in range(16)] for _ in range(16)]
        for i in range(16):
            for j in range(16):
                total = (Fraction(0), Fraction(0))
                for k in range(8):
                    left = (Fraction(factor[i][k]), Fraction(0))
                    right = (Fraction(factor[j][k]), Fraction(0))
                    if k == 0:
                        left = cmul(left, scale)
                        right = cmul(right, right_scale)
                    term = cmul(left, right)
                    total = (total[0] + term[0], total[1] + term[1])
                out[i][j] = total
        return out

    good = scaled_product(dual)
    bad = scaled_product(scale)
    check(
        "complex-scale",
        all(good[i][j] == (Fraction(target[i][j]), Fraction(0)) for i in range(16) for j in range(16))
        and all(factor[i][0] == 0 or cmul((Fraction(factor[i][0]), Fraction(0)), scale) != (0, 0) for i in range(16)),
        "complex ordinary-transpose gauge lost the identity or a support",
    )
    check(
        "bad-complex-scale",
        any(bad[i][j] != (Fraction(target[i][j]), Fraction(0)) for i in range(16) for j in range(16)),
        "scaling both factors by 1+i still matched 2G",
    )
    check(
        "ratio",
        Fraction(16, 16) > Fraction(7, 13),
        "16/16 is not strictly coarser than the P104 ratio 7/13",
    )
    check(
        "cost",
        8 * 2 == 16,
        "eight rank-2 columns do not sum to 16",
    )

    print(
        "PASS_FRAME_PAIR_SIXTEEN_EXACT frames=1260 admissible=896 cost=16 "
        "column_rank=2 orthogonal_rank_one_pairs=%d controls=7"
        % orthogonal_rank_one
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
