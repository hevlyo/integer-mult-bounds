#!/usr/bin/env python3
"""Binomial enclosure of the selected conservative complex moment.

The selected assembly already records Mercator and base-two residuals. The
code-disjoint atanh pricer certifies the native endpoint and does not turn on
the inherited bad-residue surcharge. This script encloses the same frozen
profile with the positive series (1 - r/m)^(-a), imports neither engine, and
checks the conservative bracket, the native-with-surcharge rejection, and the
conservative kappa grid point.

Python 3.12 standard library only. Assertions must stay enabled.
"""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
ASSEMBLY = ROOT / "research/community-frontier1094-audit/ASSEMBLY.json"
PROFILE = ROOT / "research/complex-t16-rare-pattern-exchanges/PROFILE.json"
PLAN = ROOT / "research/complex-t16-rare-pattern-exchanges/data/PLAN.json"
SELECTED = ROOT / "certificates/selected-result.json"

D = 1 << 240
TAIL_LIMIT = 1 << 70
GRID = Q(1, 10**24)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def as_profile(raw):
    profile = {int(rank): int(count) for rank, count in raw.items()}
    require(profile and all(rank > 0 and count > 0 for rank, count in profile.items()),
            "profile ranks and counts must be positive")
    return profile


def ceil_div(numerator, denominator):
    return -(-numerator // denominator)


def power_interval(rank, modulus, saving, tail_limit=TAIL_LIMIT):
    """Enclose (modulus/rank)^saving for a rational saving in [0, 1].

    With x = 1 - rank/modulus, the positive binomial series is
    (1 - x)^(-saving) = sum_{k >= 0} t_k, t_0 = 1, and
    t_{k+1} = t_k * (saving + k) / (k + 1) * x.
    For 0 <= saving <= 1 the factor (saving + k)/(k + 1) is at most 1, so
    t_{k+j} <= t_{k+1} * x^{j-1}. The tail after t_k is therefore at most
    t_{k+1} / (1 - x) = t_{k+1} * modulus / rank. Partial sums are rounded
    outward onto multiples of 2^{-240}. The tail is added only to the upper end.
    """
    require(type(rank) is int and type(modulus) is int and 0 < rank <= modulus,
            "invalid rank or modulus")
    require(isinstance(saving, Q) and 0 <= saving <= 1, "saving must lie in [0, 1]")
    if saving == 0 or rank == modulus:
        return Q(1), Q(1), 0
    numerator_a, denominator_a = saving.numerator, saving.denominator
    term_lo = term_hi = sum_lo = sum_hi = D
    for k in range(20000):
        step_numerator = (numerator_a + k * denominator_a) * (modulus - rank)
        step_denominator = denominator_a * (k + 1) * modulus
        next_lo = term_lo * step_numerator // step_denominator
        next_hi = ceil_div(term_hi * step_numerator, step_denominator)
        tail = ceil_div(next_hi * modulus, rank)
        if tail <= tail_limit:
            return Q(sum_lo, D), Q(sum_hi + tail, D), k + 1
        term_lo, term_hi = next_lo, next_hi
        sum_lo += term_lo
        sum_hi += term_hi
    raise ValueError("series did not reach the prescribed tail bound")


def moment(profile, modulus, live, saving, surcharge=False, tail_limit=TAIL_LIMIT):
    require(type(modulus) is int and modulus > 1 and type(live) is int and live > 0,
            "invalid modulus or live stock")
    lower = upper = Q(0)
    steps = {}
    for rank, count in sorted(profile.items()):
        require(rank < modulus, "child rank must be strictly below the modulus")
        lo, hi, used = power_interval(rank, modulus, saving, tail_limit)
        weight = Q(rank * count, modulus * live)
        lower += weight * lo
        upper += weight * hi
        steps[str(rank)] = used
    if surcharge:
        lo, hi, used = power_interval(1, modulus, saving, tail_limit)
        weight = Q(32 * modulus * sum(profile.values()), 10**16 * live)
        lower += weight * lo
        upper += weight * hi
        steps["fallback"] = used
    return lower, upper, steps


def rows_for(assembly, side, surcharge):
    rows = [row for row in assembly["moments" if side != "conservative_complex" else "conservative_moments"]
            if row["side"] == side and row["surcharge"] is surcharge]
    require(len(rows) == 2, "expected an accept/reject pair")
    return rows


def overlap(residual_lo, residual_hi, recorded):
    recorded_lo, recorded_hi = map(Q, recorded)
    require(recorded_lo <= recorded_hi, "recorded residual is not ordered")
    require(max(residual_lo, recorded_lo) <= min(residual_hi, recorded_hi),
            "binomial residual does not meet the recorded residual")


def certify_bracket(profile, modulus, live, endpoint, surcharge, recorded_rows):
    accept = moment(profile, modulus, live, endpoint, surcharge)
    reject = moment(profile, modulus, live, endpoint + GRID, surcharge)
    require(accept[1] < 1, "acceptance enclosure is not strictly below one")
    require(reject[0] > 1, "rejection enclosure is not strictly above one")
    for row, (lo, hi, _), expected, accepted in (
        (recorded_rows[0], accept, endpoint, True),
        (recorded_rows[1], reject, endpoint + GRID, False),
    ):
        require(Q(row["endpoint"]) == expected and row["accept"] is accepted
                and row["surcharge"] is surcharge, "recorded moment row does not match this bracket")
        for engine in ("mercator", "base_two"):
            overlap(lo - 1, hi - 1, row[engine])
    return {
        "endpoint": str(endpoint),
        "successor": str(endpoint + GRID),
        "accept_below_one": True,
        "successor_above_one": True,
        "accept_residual": [str(accept[0] - 1), str(accept[1] - 1)],
        "successor_residual": [str(reject[0] - 1), str(reject[1] - 1)],
        "accept_terms": accept[2],
        "overlaps_recorded_mercator_and_base_two": True,
    }


def conservative_kappa(complex_endpoint, bit_endpoint):
    """Selected outer reduction, reimplemented from the stated rational recurrence.

    This is the arithmetic already recorded by the assembly. It is not a new
    derivation of the analytic transfer theorem.
    """
    eta = beta = GRID
    saving = min(bit_endpoint, (1 - beta) * complex_endpoint) - Q(1, 10**27)
    require(0 < saving < bit_endpoint and saving < (1 - beta) * complex_endpoint,
            "bootstrap input is outside the selected range")
    value = Q(384599, 10**10)
    for _ in range(7):
        previous = value
        value = (1 - saving) * saving + saving * previous
        gap = min(saving - value, 1 - value - saving, 1 - value - saving * (1 - previous), 1 - saving)
        require(previous < value < saving < 1 - value and gap > 0, "bootstrap step is not strictly ordered")
    balanced = value * (1 - 2 * eta)
    margin = (1 - eta) * balanced / (1 + balanced)
    ticks = margin * 10**18
    kappa = Q((ticks.numerator - 1) // ticks.denominator, 10**18)
    require(kappa < margin <= kappa + Q(1, 10**18), "kappa is not the grid point below the margin")
    require((1 - beta) * complex_endpoint < bit_endpoint, "complex side does not bind")
    return kappa


def expect_value_error(action, text):
    try:
        action()
    except ValueError as exc:
        require(text in str(exc), "unexpected failure: " + str(exc))
        return
    raise ValueError("control did not fail: " + text)


def main():
    require(not sys.flags.optimize, "assertions must stay enabled; leave PYTHONOPTIMIZE unset")
    assembly = load(ASSEMBLY)
    profile = as_profile(load(PROFILE))
    plan = load(PLAN)
    selected = load(SELECTED)
    require(as_profile(assembly["complex_profile"]) == profile == as_profile(plan["profile"]),
            "assembly, profile file and plan disagree")
    modulus, live, deficit = int(plan["M"]), int(plan["live"]), int(plan["deficit"])
    calls = int(plan["T"]) * int(plan["L"])
    mass = sum(rank * count for rank, count in profile.items())
    require(modulus * live - mass == deficit == live - 64 * calls,
            "rank-mass deficit is not the stated live-stock identity")
    require(modulus * modulus > 2 * max(profile) ** 2, "halving guard fails")
    require(selected["certificate"] == "research/community-frontier1094-audit/ASSEMBLY.json",
            "selected certificate path changed")
    require(selected["kappa"] == assembly["kappa"], "selected kappa and assembly kappa differ")

    conservative = Q(assembly["conservative_complex_lower"])
    native = Q(assembly["complex_lower"])
    bit = Q(assembly["bit_lower"])
    conservative_report = certify_bracket(
        profile, modulus, live, conservative, True,
        rows_for(assembly, "conservative_complex", True))
    native_report = certify_bracket(
        profile, modulus, live, native, False, rows_for(assembly, "complex", False))
    surcharged_native = moment(profile, modulus, live, native, True)
    require(surcharged_native[0] > 1, "native endpoint is not rejected when the old surcharge is restored")

    kappa = conservative_kappa(conservative, bit)
    require(kappa == Q(assembly["conservative_kappa"]), "conservative kappa grid point disagrees")
    require(Q(assembly["kappa"]) == Q(selected["kappa"]), "published native kappa was not left unchanged")

    for rank in sorted(profile):
        lo, hi, _ = power_interval(rank, modulus, Q(1))
        require(lo <= Q(modulus, rank) <= hi, "a=1 enclosure misses the exact integer power")
    zero_lo, zero_hi, _ = moment(profile, modulus, live, Q(0), False)
    require(zero_lo == zero_hi == Q(mass, modulus * live), "a=0 moment is not the exact rank mass")

    extra = dict(profile)
    extra[1] += 1
    extra_lo, _, _ = moment(extra, modulus, live, conservative, True)
    require(extra_lo > 1, "one extra rank-one child does not push the moment above one")
    wide_lo, wide_hi, wide_steps = moment(profile, modulus, live, conservative, True, tail_limit=1 << 300)
    require(wide_steps.get("1") == 1 and not wide_hi < 1,
            "a one-term tail does not fail closed")
    expect_value_error(
        lambda: certify_bracket(profile, modulus, live, conservative + GRID, True,
                                rows_for(assembly, "conservative_complex", True)),
        "acceptance enclosure is not strictly below one")

    report = {
        "status": "PASS_SELECTED_CONSERVATIVE_BINOMIAL",
        "scope": "Selected PR1094 conservative complex moment with the inherited surcharge; no new kappa",
        "modulus": modulus,
        "live": live,
        "calls": calls,
        "rank_mass": mass,
        "deficit": deficit,
        "selected_kappa": selected["kappa"],
        "conservative_kappa": str(kappa),
        "native_endpoint_with_surcharge_above_one": True,
        "native_surcharge_residual_lower": str(surcharged_native[0] - 1),
        "conservative": conservative_report,
        "native_without_surcharge_control": native_report,
        "one_term_tail_fails_closed": True,
        "one_extra_rank_one_child_rejected": True,
        "input_sha256": {
            "assembly": sha256(ASSEMBLY),
            "profile": sha256(PROFILE),
            "plan": sha256(PLAN),
            "selected_record": sha256(SELECTED),
        },
        "not_run": [
            "make frontier1094-verify",
            "owner and word replay",
            "PR589 bit-circuit rebuild",
            "bit surcharge omission at the next bit endpoint",
            "analytic transfer and bit H1-H5",
        ],
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    print(report["status"], report["conservative_kappa"])


if __name__ == "__main__":
    main()
