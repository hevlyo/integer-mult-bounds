#!/usr/bin/env python3
"""P112 E-graph lift with fixed coordinate readers and one extra term.

Copy-rank sum is at least 64. Standard library only. Exact integer rank,
with rational kernels only on the 7-row bases that meet corank 1.
Assertions raise SystemExit, so python -O cannot skip a failed check.
"""
import hashlib
import itertools
import json
import math
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NPORTS = 112
FULL = (1 << NPORTS) - 1


def die(tag, detail=""):
    raise SystemExit("FAIL " + tag + ((" | " + detail) if detail else ""))


def check(tag, cond, detail=""):
    if not cond:
        die(tag, detail)
    print("PASS " + tag + ((" | " + detail) if detail else ""), flush=True)


def e8_lines():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                v = [0] * 8
                v[i], v[j] = 2 * si, 2 * sj
                roots.append(tuple(v))
    for s in itertools.product((1, -1), repeat=8):
        if s.count(-1) % 2 == 0:
            roots.append(tuple(s))
    lines, seen = [], set()
    for r in roots:
        key = r if r > tuple(-a for a in r) else tuple(-a for a in r)
        if key not in seen:
            seen.add(key)
            lines.append(r)
    return lines


def ip(x, y):
    d = sum(a * b for a, b in zip(x, y))
    if d % 4:
        die("model.ip-scale", str(d))
    return d // 4


# Entries of X are 0 or ±1, so every 8×8 minor has absolute value at most
# 8**(8/2) = 4096. Rank over Q therefore agrees with rank modulo any larger prime.
MOD = 65537


def rank_int(rows):
    basis = []
    for row in rows:
        v = [int(x) % MOD for x in row]
        for piv, b in basis:
            f = v[piv]
            if f:
                v = [(x - f * b[c]) % MOD for c, x in enumerate(v)]
        piv = next((c for c in range(8) if v[c]), None)
        if piv is None:
            continue
        inv = pow(v[piv], -1, MOD)
        basis.append((piv, [(x * inv) % MOD for x in v]))
        if len(basis) == 8:
            break
    return len(basis)


def independent_rows(rows, need):
    basis = []
    kept = []
    for row in rows:
        original = tuple(int(x) for x in row)
        v = [x % MOD for x in original]
        for piv, b in basis:
            f = v[piv]
            if f:
                v = [(x - f * b[c]) % MOD for c, x in enumerate(v)]
        piv = next((c for c in range(8) if v[c]), None)
        if piv is None:
            continue
        inv = pow(v[piv], -1, MOD)
        basis.append((piv, [(x * inv) % MOD for x in v]))
        kept.append(original)
        if len(kept) == need:
            break
    return kept


def kernel_vector(rows):
    """One integer right-kernel vector of a rank-7 integer system."""
    kept = independent_rows(rows, 7)
    if len(kept) != 7:
        die("kernel.rank", str(len(kept)))
    A = [[Q(x) for x in row] for row in kept]
    pivots = []
    r = 0
    for c in range(8):
        p = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        piv = A[r][c]
        A[r] = [x / piv for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        pivots.append(c)
        r += 1
    free = [c for c in range(8) if c not in pivots]
    if len(free) != 1:
        die("kernel.corank", str(free))
    fcol = free[0]
    vec = [Q(0)] * 8
    vec[fcol] = Q(1)
    for i, c in enumerate(pivots):
        vec[c] = -A[i][fcol]
    den = 1
    for x in vec:
        den = math.lcm(den, x.denominator)
    return [int(x * den) for x in vec]


def parallel_int(vec, row):
    seen = None
    for c in range(8):
        if row[c] == 0:
            if vec[c] != 0:
                return False
            continue
        ratio = (vec[c], row[c])
        g = math.gcd(ratio[0], ratio[1])
        ratio = (ratio[0] // g, ratio[1] // g)
        if ratio[1] < 0:
            ratio = (-ratio[0], -ratio[1])
        if seen is None:
            seen = ratio
        elif seen != ratio:
            return False
    return seen is not None


def f2_rank(masks):
    basis = {}
    rank = 0
    for v in masks:
        x = v
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                basis[h] = x
                rank += 1
                break
    return rank


def f2_basis(masks):
    basis = {}
    for v in masks:
        x = v
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                basis[h] = x
                break
    return list(basis.values())


def span_from_basis(basis):
    out = [0]
    for b in basis:
        # Snapshot the current block. A generator would see the items it appends.
        out.extend([z ^ b for z in out])
    return out


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def pair_rank(lab, rows, cols):
    if rows == 0 or cols == 0:
        return 0
    return f2_rank(lab[i] & cols for i in bits(rows))


def component_sizes(mask, lab):
    left = mask
    sizes = []
    while left:
        seen = 0
        stack = left & -left
        while stack:
            bit = stack & -stack
            stack ^= bit
            if seen & bit:
                continue
            seen |= bit
            i = bit.bit_length() - 1
            stack |= lab[i] & mask & ~seen
        sizes.append(seen.bit_count())
        left &= ~seen
    sizes.sort()
    return tuple(sizes)


def common_odd_mask(mask, lab):
    out = 0
    for i in range(NPORTS):
        if ((mask >> i) & 1) == 0 and (lab[i] & mask) == 0:
            out |= 1 << i
    return out


def build():
    lines = e8_lines()
    if len(lines) != 120:
        die("model.lines", str(len(lines)))
    ipm = [[ip(lines[i], lines[j]) for j in range(120)] for i in range(120)]
    frame = []
    for a in range(4):
        for s in (1, -1):
            v = [0] * 8
            v[2 * a], v[2 * a + 1] = 2, 2 * s
            frame.append(lines.index(tuple(v)))
    frame_set = set(frame)
    ports = [i for i in range(120) if i not in frame_set]
    if len(frame) != 8 or len(ports) != NPORTS:
        die("model.frame")
    X = [tuple(ipm[ports[p]][frame[k]] for k in range(8)) for p in range(NPORTS)]
    lab = [0] * NPORTS
    for i in range(NPORTS):
        m = 0
        for j in range(NPORTS):
            if ((ipm[ports[i]][ports[j]] + 1) & 1) == 1:
                m |= 1 << j
        lab[i] = m
    stars = [0] * 8
    for k in range(8):
        m = 0
        for i in range(NPORTS):
            if X[i][k] != 0:
                m |= 1 << i
        stars[k] = m
    return X, lab, stars


def star_code_masks(star, lab):
    ports = list(bits(star))
    pos = {p: i for i, p in enumerate(ports)}
    rows = []
    for i in ports:
        m = 0
        for j in bits(lab[i] & star):
            m |= 1 << pos[j]
        rows.append(m)
    basis = f2_basis(rows)
    if len(basis) != 8:
        die("code.dimension", str(len(basis)))
    space = span_from_basis(basis)
    out = []
    for vec in space:
        if vec == 0:
            continue
        g = 0
        for i in range(len(ports)):
            if (vec >> i) & 1:
                g |= 1 << ports[i]
        out.append(g)
    return out


def gram(X, i, j):
    return sum(X[i][k] * X[j][k] for k in range(8))


def main():
    pin = json.loads((HERE / "SOURCES.json").read_text())
    proof_row = next(r for r in pin["files"] if r["path"] == "research/p112-single-lift/PROOF.md")
    proof = (ROOT / proof_row["path"]).read_bytes()
    check("pin.pr845-proof", hashlib.sha256(proof).hexdigest() == proof_row["sha256"], proof_row["sha256"][:16])
    check(
        "pin.pr845-states-floor",
        b">= 64" in proof and b"masked completion" in proof,
        "inherited classical floor; masked completions stay outside that proof",
    )

    X, lab, stars = build()
    check("model.lines-frame", True, "120 lines, P112 = 112, coordinate frame 8")
    check(
        "model.row-weight",
        all(sum(x != 0 for x in row) == 4 and all(x in (-1, 0, 1) for x in row) for row in X),
        "four nonzeros per row, entries in {-1,0,1}; modular rank uses this Hadamard bound",
    )
    check("model.star-size", [m.bit_count() for m in stars] == [56] * 8, "eight stars of size 56")
    e_off = diag = odd_nz = True
    ones = 0
    for i in range(NPORTS):
        if lab[i].bit_count() != 60 or gram(X, i, i) != 4:
            diag = False
        for j in bits(lab[i]):
            ones += 1
            if i != j and gram(X, i, j) != 0:
                e_off = False
            if (lab[i] >> j) & 1 != (lab[j] >> i) & 1:
                die("model.dot-symmetry")
        for j in bits(FULL ^ lab[i]):
            if gram(X, i, j) == 0:
                odd_nz = False
    check("model.e-graph-target", e_off and diag and odd_nz and ones == 112 * 60,
          "M4 is 4I on the E-graph and nonzero off it")
    check("model.label-rank", f2_rank(lab) == 9, "label pairing has F2 rank 9")

    e_pairs = odd_pairs = 0
    for j in range(NPORTS):
        for jp in range(j + 1, NPORTS):
            inter = lab[j] & lab[jp]
            rk = rank_int(X[i] for i in bits(inter))
            if (lab[j] >> jp) & 1:
                e_pairs += 1
                if rk != 8:
                    die("nbhd.e-intersection-rank-8", "pair %d %d rank %d" % (j, jp, rk))
            else:
                odd_pairs += 1
                if rk != 6:
                    die("nbhd.odd-intersection-rank-6", "pair %d %d rank %d" % (j, jp, rk))
    check("nbhd.e-intersection-rank-8", e_pairs == 3304, "all %d E-pairs" % e_pairs)
    check("nbhd.odd-intersection-rank-6", odd_pairs == 2912, "sharpness: odd pairs are rank 6")
    for v in range(NPORTS):
        rows = [X[i] for i in bits(lab[v] ^ (1 << v))]
        if rank_int(rows) != 7 or any(gram(X, i, v) != 0 for i in bits(lab[v] ^ (1 << v))):
            die("nbhd.off-diagonal-rank-7", "v %d" % v)
    check("nbhd.off-diagonal-rank-7", True, "N(v) without v is an X[v]-perp of rank 7")

    signature = {}
    fixture = None
    active_closure = inactive_closure = 0
    for k, star in enumerate(stars):
        masks = star_code_masks(star, lab)
        if len(masks) != 255:
            die("code.count", "star %d has %d" % (k, len(masks)))
        for supp in masks:
            comp = component_sizes(supp, lab)
            odd = common_odd_mask(supp, lab)
            signature[(supp.bit_count(), comp, odd.bit_count())] = (
                signature.get((supp.bit_count(), comp, odd.bit_count()), 0) + 1
            )
            if odd.bit_count() == 1 and (supp & odd) == 0:
                v = odd.bit_length() - 1
                odd_v = common_odd_mask(1 << v, lab)
                if supp & ~odd_v:
                    die("normal.not-in-odd-neighborhood", "star %d weight %d" % (k, supp.bit_count()))
                union = 0
                for w in bits(supp):
                    union |= lab[w]
                cover = lab[v] & union
                if rank_int(X[i] for i in bits(cover)) != 7:
                    die("normal.joint-kernel", "star %d v %d" % (k, v))
                if any(gram(X, i, v) != 0 for i in bits(cover)):
                    die("normal.joint-orth", "star %d v %d" % (k, v))
                if pair_rank(lab, odd_v, supp) != 7:
                    die("closure.odd-reader-rank", "star %d v %d" % (k, v))
                if X[v][k] != 0:
                    if supp.bit_count() != 28:
                        die("closure.active-weight", str(supp.bit_count()))
                    if odd_v & ~union:
                        die("closure.odd-uncovered", "star %d v %d" % (k, v))
                    if any(gram(X, i, v) == 0 for i in bits(odd_v)):
                        die("closure.odd-gram", "v %d" % v)
                    active_closure += 1
                    if fixture is None:
                        fixture = (k, supp, v)
                else:
                    if supp.bit_count() != 24:
                        die("closure.inactive-weight", str(supp.bit_count()))
                    inactive_closure += 1
    expected = {
        (28, (28,), 0): 576,
        (32, (32,), 0): 504,
        (28, (28,), 1): 448,
        (24, (24,), 1): 448,
        (24, (24,), 0): 56,
        (56, (56,), 0): 8,
    }
    check("code.signature", signature == expected and sum(signature.values()) == 2040,
          "2040 supports, all E-connected, at most one odd neighbor")
    check(
        "normal.joint-kernel",
        active_closure == 448 and inactive_closure == 448 and fixture is not None,
        "896 odd-neighbor codewords, joint corank 1; 448 active weight-28 and 448 inactive weight-24",
    )

    redundant = 0
    for k, star in enumerate(stars):
        for v in bits(star):
            en = star & lab[v] & ~(1 << v)
            if en.bit_count() != 27:
                die("redundancy.degree", "star %d v %d" % (k, v))
            alone = pair_rank(lab, star, 1 << v)
            base = pair_rank(lab, star, en)
            both = pair_rank(lab, star, en | (1 << v))
            if not (alone == 1 and base == 7 and both == 7):
                die("redundancy.column", "star %d v %d" % (k, v))
            odd = common_odd_mask(1 << v, lab)
            if en & odd:
                die("redundancy.odd-disjoint")
            redundant += 1
    check("redundancy.e-neighbor-columns", redundant == 448,
          "each star point is redundant beside its 27 E-neighbors")

    basis = f2_basis(lab)
    if len(basis) != 9:
        die("critical.basis")
    parallel_meet = skew_orth = high = 0
    for mask in range(1, 512):
        q = 0
        for b in range(9):
            if (mask >> b) & 1:
                q ^= basis[b]
        active = [i for i in bits(q)]
        active_mask = q
        for v in active:
            corank = 8 - rank_int(X[i] for i in bits(active_mask ^ (1 << v)))
            if corank > 1:
                high += 1
            elif corank == 1:
                vec = kernel_vector(X[i] for i in bits(active_mask ^ (1 << v)))
                meet = sum(vec[c] * X[v][c] for c in range(8)) != 0
                if meet:
                    if not parallel_int(vec, X[v]):
                        die("critical.skew-meet", "v %d" % v)
                    parallel_meet += 1
                else:
                    skew_orth += 1
            elif corank < 0:
                die("critical.rank")
    check("critical.only-row-parallel", high == 0 and parallel_meet == 112 and skew_orth == 448,
          "112 row-parallel witnesses; 448 skew kernels miss the port")

    k0, supp, v = fixture
    odd = common_odd_mask(1 << v, lab)
    if supp & ~odd:
        die("fixture.selection")
    reader = odd
    for k in range(8):
        if pair_rank(lab, stars[k], stars[k]) != 8:
            die("fixture.coordinate-beta")
    extra = pair_rank(lab, reader, 1 << v)
    check("fixture.masked-cost-64", extra == 0, "eight stars at 8 and a cost-free odd reader")
    # d[i] = 0 on N(v) and d[i] = M4[i,v] on the odd neighborhood. Column v of
    # XX^T + d e_v^T therefore matches M4 on the E-graph and doubles off it.
    e_ok = True
    full_fail = False
    for i in range(NPORTS):
        on_edge = ((lab[v] >> i) & 1) == 1
        d_i = 0 if on_edge else gram(X, i, v)
        value = gram(X, i, v) + d_i
        if on_edge:
            if d_i != 0 or value != gram(X, i, v):
                e_ok = False
        elif d_i == 0 or value == gram(X, i, v):
            e_ok = False
        else:
            full_fail = True
    check("fixture.e-graph-exact", e_ok, "d vanishes on N(v), so column v matches M4 there")
    check("fixture.not-all-pairs", full_fail, "every odd entry of column v is nonzero and doubles")

    a = X[v]
    if a[k0] == 0:
        die("fixture.deformation-coordinate")
    t = {j: Q(X[j][k0], a[k0]) for j in bits(supp)}
    t[v] = Q(1)
    lam = Q(1)
    betas = []
    for k in range(8):
        column = 0
        for j in range(NPORTS):
            if j == v:
                coeff = a[k] + lam * X[v][k]
                val = X[j][k] - t[v] * coeff
            elif j in t:
                val = X[j][k] - t[j] * a[k]
            else:
                val = X[j][k]
            if val != 0:
                column |= 1 << j
        betas.append(pair_rank(lab, stars[k], column))
    drow = [0] * NPORTS
    for i in range(NPORTS):
        coeff = [a[c] + (lam * X[v][c] if i == v else 0) for c in range(8)]
        drow[i] = sum(X[i][c] * coeff[c] for c in range(8))
    dsupp = 0
    for i in range(NPORTS):
        if drow[i] != 0:
            dsupp |= 1 << i
    J = 0
    for j, val in t.items():
        if val != 0:
            J |= 1 << j
    extra = pair_rank(lab, dsupp, J)
    total = sum(betas) + extra
    e_identity = True
    for j in range(NPORTS):
        tj = t[j] if j in t else Q(0)
        for i in bits(lab[j]):
            acc = 0
            for k in range(8):
                if j == v:
                    sk = X[j][k] - tj * (a[k] + lam * X[v][k])
                elif j in t:
                    sk = X[j][k] - tj * a[k]
                else:
                    sk = X[j][k]
                acc += X[i][k] * sk
            if tj != 0:
                if i == v:
                    di = sum(X[v][c] * (a[c] + lam * X[v][c]) for c in range(8))
                else:
                    di = sum(X[i][c] * a[c] for c in range(8))
                acc += di * tj
            if acc != gram(X, i, j):
                e_identity = False
                break
        if not e_identity:
            break
    check("fixture.deformation-e-exact", e_identity and total >= 64,
          "betas %s extra %d total %d" % (betas, extra, total))

    anchor = next(j for j in range(1, NPORTS) if (lab[0] >> j) & 1)
    truncated = [X[i] for i in bits(lab[0] & lab[anchor])][:4]
    controls = [
        rank_int(truncated) < 8,
        pair_rank(lab, stars[0], 1 << (stars[0] & -stars[0]).bit_length() - 1) < 8,
        pair_rank(lab, reader, 1 << v) == 0,
        signature.get((23, (23,), 0), 0) == 0,
        any(gram(X, i, v) != 0 for i in bits(odd)),
    ]
    check("controls.reject-mutations", all(controls) and len(controls) == 5,
          "truncated intersection, one-point column, free odd reader, no weight-23 word, odd Gram")
    print(
        "PASS_P112_MASKED_FIXED_READER_LIFT "
        "floor=64 readers=coordinate extra-terms=1 mask=E-graph "
        "e-pairs=3304 codewords=2040 critical=112 active-closure=448 inactive-closure=448 controls=5"
    )


if __name__ == "__main__":
    main()
