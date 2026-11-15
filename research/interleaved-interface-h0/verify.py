#!/usr/bin/env python3
"""Restoration implication for the interleaved scalar-interface lemma.

The quantified claim is the proof in README.md. This program checks that
claim's boundary on an explicit gate model: the five named hypotheses do not
imply cleanup inversion, the repaired hypotheses do, and the finite
enumerations agree with that split. It does not replay an E8 word.
"""

from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEMMA = ROOT / "research/e8-bit-r420/README.md"
XCHECK = ROOT / "research/e8-bit-p111-tuned/code/xcheck_p.py"


class Reject(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise Reject(msg)


def is_y(v, r):
    return v <= r < 2 * v


def is_z(v, r):
    return not is_y(v, r)


def is_helper(v, r):
    return r >= 2 * v


def apply_gate(vals, dest, srcs):
    acc = 0
    for s in srcs:
        acc ^= vals[s]
    vals[dest] ^= acc


def simulate(word, sections):
    v = word["v"]
    n = word["n"]
    vals = [1 << r for r in range(n)]
    for name in sections:
        if name == "scatter":
            copies = [vals[q] for q in word["helpers_snapshot"]]
            # scatter rows name indices into helpers_snapshot, matching the
            # pinned checker's copied-total semantics.
            for t, row in enumerate(word["scatter"]):
                for k in row:
                    vals[v + t] ^= copies[k]
        else:
            for dest, srcs in word[name]:
                apply_gate(vals, dest, srcs)
    return vals


def z_gates(word):
    v = word["v"]
    out = []
    for name in ("A", "B"):
        for dest, srcs in word[name]:
            if is_z(v, dest):
                out.append((dest, srcs))
    return out


def dest_outside_sources(gates):
    return all(dest not in srcs for dest, srcs in gates)


def hypotheses(word):
    """Named predicates. H0 is the missing operand hypothesis, not one of H1-H5."""
    v = word["v"]
    n = word["n"]
    sections = ("D", "A", "B", "C")
    all_gates = [g for name in sections for g in word[name]]
    forward = z_gates(word)
    # Load-bearing gap: z-gates only. H2 forces the same shape on D, and H5
    # forces it on target gates once these z-gates are involutions.
    h0 = dest_outside_sources(forward)
    h1 = all(
        (not is_z(v, dest)) or all(not is_y(v, s) for s in srcs)
        for dest, srcs in all_gates
    )
    h2 = all(
        is_y(v, dest) and all(is_helper(v, s) for s in srcs)
        for dest, srcs in word["D"]
    )
    h3 = (
        all(is_z(v, dest) for dest, _srcs in word["A"])
        and all(0 <= k < len(word["helpers_snapshot"]) for row in word["scatter"] for k in row)
        and all(is_helper(v, q) for q in word["helpers_snapshot"])
        and len(word["scatter"]) == v
        and all(
            is_y(v, dest) or all(is_z(v, s) for s in srcs)
            for dest, srcs in word["B"]
        )
    )
    h4 = list(word["C"]) == list(reversed(forward))
    raw = simulate(word, ("A", "scatter", "B"))
    ymask = ((1 << v) - 1) << v
    h5 = all((raw[v + t] & ymask) == (1 << (v + t)) for t in range(v))
    return {
        "H0_dest_not_source": h0,
        "H1": h1,
        "H2": h2,
        "H3": h3,
        "H4": h4,
        "H5": h5,
        "named_H1_through_H5": h1 and h2 and h3 and h4 and h5,
        "n": n,
    }


def z_mask(v, r_helpers):
    return ((1 << v) - 1) | (((1 << r_helpers) - 1) << (2 * v))


def invertible_z(raw, v, r_helpers):
    """Rows are z-register outputs, columns are initial z bits, over F2."""
    n = 2 * v + r_helpers
    cols = [i for i in range(n) if is_z(v, i)]
    rows = []
    for r in cols:
        mask = raw[r]
        rows.append([1 if mask & (1 << c) else 0 for c in cols])
    m = len(rows)
    mat = [row[:] for row in rows]
    rank = 0
    for col in range(m):
        pivot = next((i for i in range(rank, m) if mat[i][col]), None)
        if pivot is None:
            continue
        mat[rank], mat[pivot] = mat[pivot], mat[rank]
        for i in range(m):
            if i != rank and mat[i][col]:
                mat[i] = [a ^ b for a, b in zip(mat[i], mat[rank])]
        rank += 1
    return rank == m


def conclusions(word, flags):
    v = word["v"]
    r_helpers = word["n"] - 2 * v
    raw = simulate(word, ("A", "scatter", "B"))
    ymask = ((1 << v) - 1) << v
    xmask = (1 << v) - 1
    smask = z_mask(v, r_helpers) ^ xmask
    block = all((raw[r] & ymask) == 0 for r in range(word["n"]) if is_z(v, r))
    restored = simulate(word, ("A", "scatter", "B", "C"))
    c_inverse = all(restored[r] == (1 << r) for r in range(word["n"]) if is_z(v, r))
    y_fixed = all(restored[v + t] == raw[v + t] for t in range(v))
    invertible = invertible_z(raw, v, r_helpers) if block else False
    d_only = simulate(word, ("D",))
    full = simulate(word, ("D", "A", "scatter", "B", "C"))
    composed = True
    for t in range(v):
        n_mask = d_only[v + t] & smask
        j_mask = raw[v + t] & xmask
        k_mask = raw[v + t] & smask
        predicted = (1 << (v + t)) ^ j_mask ^ k_mask ^ n_mask
        if full[v + t] != predicted or any(full[r] != (1 << r) for r in range(word["n"]) if is_z(v, r)):
            composed = False
            break
    shear = all(
        full[v + t] == ((1 << (v + t)) ^ (1 << t)) and all(
            full[r] == (1 << r) for r in range(word["n"]) if is_z(v, r)
        )
        for t in range(v)
    )
    return {
        "block": block,
        "U_invertible": invertible,
        "C_is_U_inverse": c_inverse and y_fixed,
        "composed_map": composed,
        "shear_y_plus_x": shear,
        "repaired_implication": bool(
            flags["H0_dest_not_source"] and flags["named_H1_through_H5"]
            and block and invertible and c_inverse and y_fixed and composed
        ),
    }


def make_word(v, r_helpers, D=(), A=(), scatter=None, B=(), C=None, snapshot=None):
    if snapshot is None:
        snapshot = tuple(range(2 * v, 2 * v + r_helpers))
    if scatter is None:
        scatter = tuple(() for _ in range(v))
    if C is None:
        forward = []
        for name, gates in (("A", A), ("B", B)):
            for dest, srcs in gates:
                if is_z(v, dest):
                    forward.append((dest, srcs))
        C = tuple(reversed(forward))
    scatter = tuple(tuple(row) for row in scatter)
    need(len(scatter) == v, "scatter width")
    return {
        "v": v,
        "n": 2 * v + r_helpers,
        "D": tuple((d, tuple(s)) for d, s in D),
        "A": tuple((d, tuple(s)) for d, s in A),
        "scatter": scatter,
        "B": tuple((d, tuple(s)) for d, s in B),
        "C": tuple((d, tuple(s)) for d, s in C),
        "helpers_snapshot": tuple(snapshot),
    }


def gate_options(n, dest_excluded=True, unique=True, nonempty=True):
    options = []
    for dest in range(n):
        pool = [i for i in range(n) if i != dest] if dest_excluded else list(range(n))
        min_r = 1 if nonempty else 0
        max_r = len(pool)
        for r in range(min_r, max_r + 1):
            for srcs in combinations(pool, r):
                options.append((dest, srcs))
                if not unique and r >= 1:
                    options.append((dest, srcs + (srcs[0],)))
    return options


def enumerate_domain(v, r_helpers, max_len, dest_excluded=True):
    """Every section list of length <= max_len over the operand alphabet.

    Scatter rows are subsets of the single helper when R=1, and empty when R=0.
    This is a finite corroboration of the proof, not the proof.
    """
    n = 2 * v + r_helpers
    options = gate_options(n, dest_excluded=dest_excluded, unique=True, nonempty=True)
    sequences = [()]
    if max_len >= 1:
        sequences.extend((g,) for g in options)
    if max_len >= 2:
        sequences.extend((g1, g2) for g1 in options for g2 in options)
    if r_helpers == 0:
        scatters = (tuple(() for _ in range(v)),)
    elif r_helpers == 1:
        helper_rows = ((), (0,))
        scatters = tuple(product(helper_rows, repeat=v))
    else:
        raise Reject("enumeration only covers R=0 or R=1")
    passed = 0
    named = 0
    broken_inverse = 0
    for D, A, B, scatter in product(sequences, sequences, sequences, scatters):
        word = make_word(v, r_helpers, D, A, scatter, B)
        flags = hypotheses(word)
        cons = conclusions(word, flags)
        if flags["named_H1_through_H5"]:
            named += 1
        if flags["H0_dest_not_source"] and flags["named_H1_through_H5"]:
            if not cons["repaired_implication"]:
                raise Reject("repaired implication failed inside %s" % (word,))
            passed += 1
        elif flags["named_H1_through_H5"] and not cons["C_is_U_inverse"]:
            broken_inverse += 1
            if flags["H0_dest_not_source"]:
                raise Reject("inverse failed with destination excluded")
        if flags["named_H1_through_H5"] and flags["H0_dest_not_source"]:
            if not dest_outside_sources(word["B"]):
                raise Reject("H5 admitted a target gate that reads its destination")
    return {
        "v": v,
        "R": r_helpers,
        "max_gate_list_length": max_len,
        "dest_excluded_alphabet": dest_excluded,
        "words": len(sequences) ** 3 * len(scatters),
        "named_H1_through_H5": named,
        "repaired_implication_holds": passed,
        "named_but_cleanup_not_inverse": broken_inverse,
    }


def expect_hand_trace():
    """Independent integers for the noncommuting two-gate product. U is not an involution."""
    word = make_word(
        1, 1,
        A=((0, (2,)), (2, (0,))),
        B=((1, (0,)),),
    )
    raw = simulate(word, ("A", "scatter", "B"))
    need(raw == [5, 7, 1], "hand trace of W0 got %s" % raw)
    twice = [5, 0, 1]
    apply_gate(twice, 0, (2,))
    apply_gate(twice, 2, (0,))
    need(twice[0] == 4 and twice[2] == 5, "U squared was an involution")
    flags = hypotheses(word)
    cons = conclusions(word, flags)
    need(flags["H0_dest_not_source"] and flags["named_H1_through_H5"], flags)
    need(cons["U_invertible"] and cons["C_is_U_inverse"] and cons["composed_map"], cons)
    need(not cons["shear_y_plus_x"], "this fixture is not the y+x shear")


def expect_self_source_counterexample():
    word = make_word(1, 1, A=((2, (2,)),), B=((1, (0,)),), C=((2, (2,)),))
    flags = hypotheses(word)
    cons = conclusions(word, flags)
    need(flags["named_H1_through_H5"], flags)
    need(not flags["H0_dest_not_source"], "self-source was excluded")
    need(not cons["U_invertible"] and not cons["C_is_U_inverse"], cons)
    need(not cons["repaired_implication"], cons)
    raw = simulate(word, ("A", "scatter", "B"))
    need(raw[2] == 0 and raw[1] == 3 and raw[0] == 1, raw)


def expect_duplicate_sources_still_invert():
    word = make_word(1, 1, A=((2, (0, 0)),), B=((1, (0,)),))
    flags = hypotheses(word)
    cons = conclusions(word, flags)
    need(flags["H0_dest_not_source"] and flags["named_H1_through_H5"], flags)
    need(cons["repaired_implication"] and cons["shear_y_plus_x"], cons)
    # The executable operand guard is stricter than H0: it rejects repeated sources.
    regs = [2, 0, 0]
    need(len(set(regs)) != len(regs), "duplicate fixture must fail distinctness")


def expect_empty_sources_still_invert():
    word = make_word(1, 1, A=((2, ()),), B=((1, (0,)),))
    flags = hypotheses(word)
    cons = conclusions(word, flags)
    need(flags["named_H1_through_H5"] and cons["repaired_implication"], (flags, cons))


def expect_shear_gap():
    word = make_word(1, 1, B=((1, (2,)),))
    flags = hypotheses(word)
    cons = conclusions(word, flags)
    need(flags["H0_dest_not_source"] and flags["named_H1_through_H5"], flags)
    need(cons["repaired_implication"] and not cons["shear_y_plus_x"], cons)


def expect_read_then_rewrite():
    word = make_word(1, 1, scatter=((0,),), B=((2, (0,)),))
    flags = hypotheses(word)
    cons = conclusions(word, flags)
    raw = simulate(word, ("A", "scatter", "B"))
    need(raw == [1, 6, 5], raw)
    need(cons["repaired_implication"] and not cons["shear_y_plus_x"], cons)


def expect_self_target_fails_h5():
    word = make_word(1, 1, B=((1, (1,)),))
    flags = hypotheses(word)
    # The destination is a target, so the z-gate hypothesis does not see it.
    need(flags["H0_dest_not_source"] and not flags["H5"], flags)


def expect_no_h5_with_self_target():
    """Length <= 2 words whose B list contains a self-read, with H0 z-gates."""
    n = 3
    z_safe = gate_options(n, dest_excluded=True, unique=True, nonempty=True)
    a_seqs = [()] + [(g,) for g in z_safe] + [(g1, g2) for g1 in z_safe for g2 in z_safe]
    d_seqs = [()] + [(g,) for g in z_safe]
    self_targets = []
    for dest in (1,):
        pool = [0, 1, 2]
        for r in range(1, 4):
            for srcs in combinations(pool, r):
                if dest in srcs:
                    self_targets.append((dest, srcs))
    b_seqs = [(g,) for g in self_targets]
    for g1 in self_targets:
        for g2 in z_safe:
            b_seqs.append((g1, g2))
            b_seqs.append((g2, g1))
    for g1 in self_targets:
        for g2 in self_targets:
            b_seqs.append((g1, g2))
    seen = 0
    h5_blocked = 0
    for D, A, B, row in product(d_seqs, a_seqs, b_seqs, ((), (0,))):
        word = make_word(1, 1, D, A, (row,), B)
        flags = hypotheses(word)
        seen += 1
        if flags["H0_dest_not_source"] and flags["H1"] and flags["H2"] and flags["H3"] and flags["H4"]:
            need(not flags["H5"], "self-target word kept V = I")
            h5_blocked += 1
    need(seen > 0 and h5_blocked > 0, "self-target search was empty")
    return {"words": seen, "blocked_by_H5": h5_blocked}


def expect_target_feed_fails_h1():
    word = make_word(1, 1, A=((2, (1,)),), B=((1, (0,)),))
    flags = hypotheses(word)
    need(not flags["H1"] and not flags["named_H1_through_H5"], flags)


def expect_checker_text():
    readme = LEMMA.read_text(encoding="utf-8")
    xcheck = XCHECK.read_text(encoding="utf-8")
    need("destination is never among its own sources" in readme, "lemma parenthetical moved")
    need("so C = U" in readme.replace("⁻", "^"), "inverse wording moved")
    lines = xcheck.splitlines()
    guard = next(i for i, line in enumerate(lines, 1) if "len(set(regs)) == len(regs)" in line)
    h1 = next(i for i, line in enumerate(lines, 1) if 'H["H1_no_target_feeds_z"]' in line)
    h5 = next(i for i, line in enumerate(lines, 1) if 'H["H5_V_identity"]' in line)
    inv = next(i for i, line in enumerate(lines, 1) if 'C["C_is_U_inverse"]' in line)
    need(guard < h1 < h5 < inv, (guard, h1, h5, inv))
    # The operand guard is inside replay(), which interface() calls before the flags exist.
    need("def replay(" in xcheck and "def interface(" in xcheck, "checker shape changed")
    return {"operand_guard_line": guard, "H1_line": h1, "H5_line": h5, "C_inverse_line": inv}


def main():
    text = expect_checker_text()
    expect_hand_trace()
    expect_self_source_counterexample()
    expect_duplicate_sources_still_invert()
    expect_empty_sources_still_invert()
    expect_shear_gap()
    expect_read_then_rewrite()
    expect_self_target_fails_h5()
    self_target = expect_no_h5_with_self_target()
    expect_target_feed_fails_h1()
    domains = [
        enumerate_domain(1, 1, 2, dest_excluded=True),
        enumerate_domain(1, 0, 2, dest_excluded=True),
        enumerate_domain(2, 1, 1, dest_excluded=True),
        enumerate_domain(1, 1, 1, dest_excluded=False),
    ]
    need(domains[0]["repaired_implication_holds"] > 0, domains[0])
    need(domains[3]["named_but_cleanup_not_inverse"] > 0, domains[3])
    need(all(row["named_but_cleanup_not_inverse"] == 0 for row in domains[:3]), domains)
    print("PASS_INTERLEAVED_INTERFACE_H0")
    print("pinned_checker_lines", text)
    print("self_target_search", self_target)
    for row in domains:
        print("domain", row)


if __name__ == "__main__":
    try:
        main()
    except (Reject, StopIteration, KeyError, IndexError) as exc:
        print("REJECT", exc)
        raise SystemExit(1)
