#!/usr/bin/env python3
"""Independent enclosure of the selected complex moment and outer grid.

The retained Mercator engine, the artanh base-two engine and outer.py are not
imported. Logarithms use the alternating series of ln(1+z) after exact
power-of-two reduction and, when needed, factors (1+1/k) for k >= 64.
Exponentials use a Taylor polynomial with a geometric remainder. Both bounds
are exact rationals. Integer rounding is outward.

This checks the pinned aggregate histogram. It does not rebuild that histogram
from the scalar word and it does not rerun the selected cold replay.
"""

import hashlib
import json
import sys
from fractions import Fraction
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SELECTED = ROOT / "certificates/selected-result.json"
ASSEMBLY = ROOT / "research/community-frontier1094-audit/ASSEMBLY.json"
PLAN = ROOT / "research/complex-t16-rare-pattern-exchanges/data/PLAN.json"
SCALE = 10**60
Q = Fraction


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def div_floor(num, den):
    return num // den


def div_ceil(num, den):
    return -((-num) // den)


def series_terms(p, q):
    """Smallest even N >= 2 whose next omitted term is below 1/SCALE."""
    if p == 0:
        return 2
    n = 2
    pp = p * p
    qq = q * q
    while n <= 4000:
        num = SCALE * pp * p
        den = qq * q * (n + 1)
        if num <= den:
            return n
        n += 2
        pp *= p * p
        qq *= q * q
    raise SystemExit("log series did not reach the requested scale")


def ln1p_bounds(p, q):
    """Integer bounds on SCALE*ln(1+p/q) for 0 <= p < q.

    For 0 <= z < 1 the series ln(1+z) = sum_{n>=1} (-1)^{n+1} z^n/n alternates,
    and its terms decrease. After an even number of terms the partial sum is
    below the sum and the positive remainder is smaller than the next term.
    Each included term is rounded outward, so the returned integers enclose
    SCALE*ln(1+p/q).
    """
    require(0 <= p < q, "logarithm argument")
    terms = series_terms(p, q)
    if p == 0:
        return 0, 0
    lo = hi = 0
    pp = p
    qq = q
    for n in range(1, terms + 1):
        num = SCALE * pp
        den = qq * n
        if n % 2:
            lo += div_floor(num, den)
            hi += div_ceil(num, den)
        else:
            lo -= div_ceil(num, den)
            hi -= div_floor(num, den)
        pp *= p
        qq *= q
    tail = div_ceil(SCALE * pp, qq * (terms + 1))
    return lo, hi + tail


def ln2_bounds():
    lo = hi = 0
    for k in range(64, 128):
        a, b = ln1p_bounds(1, k)
        lo += a
        hi += b
    return lo, hi


LN2_LO, LN2_HI = ln2_bounds()
_LN = {}


def ln_ratio(num, den):
    """Integer bounds on SCALE*ln(num/den), num and den positive."""
    key = (num, den)
    if key in _LN:
        return _LN[key]
    require(num > 0 and den > 0, "logarithm of a nonpositive ratio")
    twos = 0
    while num >= 2 * den:
        den *= 2
        twos += 1
    while num < den:
        num *= 2
        twos -= 1
    factors = []
    while True:
        gap = num - den
        if gap <= 0:
            z_p = 0
            z_q = 1
            break
        k = den // gap
        if k >= 64:
            factors.append(k)
            num, den = num * k, den * (k + 1)
            g = gcd(num, den)
            num //= g
            den //= g
            continue
        z_p, z_q = gap, den
        g = gcd(z_p, z_q)
        z_p //= g
        z_q //= g
        break
    lo, hi = ln1p_bounds(z_p, z_q)
    for k in factors:
        a, b = ln1p_bounds(1, k)
        lo += a
        hi += b
    if twos >= 0:
        lo += twos * LN2_LO
        hi += twos * LN2_HI
    else:
        lo += twos * LN2_HI
        hi += twos * LN2_LO
    require(lo <= hi, "log bounds crossed")
    _LN[key] = (lo, hi)
    return lo, hi


def exp_bounds(lower, upper, degree=30):
    """Bounds on exp(x) for 0 <= lower <= upper < 1/10.

    The degree-truncated Taylor sum at the lower endpoint is a lower bound.
    At the upper endpoint the omitted tail is smaller than the next term
    divided by 1 - x/(degree+1).
    """
    require(0 <= lower <= upper < Q(1, 10), "exponential range")

    def partial(x):
        term = total = Q(1)
        for j in range(1, degree):
            term *= x / j
            total += term
        return total, term

    lo, _ = partial(lower)
    hi, last = partial(upper)
    tail = last * upper / degree / (1 - upper / (degree + 1))
    return lo, hi + tail


def moment_bounds(histogram, width, roles, saving, surcharge):
    lo = hi = Q(0)
    for rank, count in histogram.items():
        require(0 < rank < width and count > 0, "improper child")
        left, right = ln_ratio(width, rank)
        lower, upper = exp_bounds(saving * Q(left, SCALE), saving * Q(right, SCALE))
        weight = Q(rank * count, width * roles)
        lo += weight * lower
        hi += weight * upper
    if surcharge:
        calls = sum(histogram.values())
        left, right = ln_ratio(width, 1)
        lower, upper = exp_bounds(saving * Q(left, SCALE), saving * Q(right, SCALE))
        weight = Q(32 * width * calls, 10**16 * roles)
        lo += weight * lower
        hi += weight * upper
    require(lo <= hi, "moment bounds crossed")
    return lo, hi


def overlap(left, right):
    return left[0] <= right[1] and right[0] <= left[1]


def enclosure_controls():
    bare = ln_ratio(2, 1)
    doubled = ln_ratio(4, 1)
    require(overlap(doubled, (2 * bare[0], 2 * bare[1])), "ln(4) missed 2 ln(2)")
    shifted = ln_ratio(73, 1)
    pieces = ln_ratio(73, 2)
    require(
        overlap(shifted, (pieces[0] + bare[0], pieces[1] + bare[1])),
        "ln(73) missed ln(73/2)+ln(2)",
    )
    exact_low = moment_bounds({1: 1}, 2, 1, Q(0), False)
    require(exact_low[0] == exact_low[1] == Q(1, 2), "a=0 one-child moment")
    require(exact_low[1] < 1, "unit child should be accepted at a=0")
    exact_high = moment_bounds({1: 3}, 2, 1, Q(0), False)
    require(exact_high[0] == exact_high[1] == Q(3, 2) and exact_high[0] > 1,
            "three unit children should be rejected at a=0")
    zero = exp_bounds(Q(0), Q(0))
    require(zero == (Q(1), Q(1)), "exp(0)")


def endpoint_pair(rows):
    accepted = [row for row in rows if row["accept"] is True]
    rejected = [row for row in rows if row["accept"] is False]
    require(len(accepted) == 1 and len(rejected) == 1, "endpoint inventory")
    low = Q(accepted[0]["endpoint"])
    high = Q(rejected[0]["endpoint"])
    require(high == low + Q(1, 10**24), "rejected endpoint is not the next 10^-24 grid point")
    return low, high


def signed_decimal(value, digits=40):
    """Truncation toward zero of a rational, with an explicit digit count."""
    sign = "-" if value < 0 else ""
    value = abs(value)
    scaled = (value.numerator * 10**digits) // value.denominator
    text = f"{scaled:0{digits}d}"
    return sign + "0." + text


def check_moment(histogram, width, roles, rows, surcharge):
    low, high = endpoint_pair(rows)
    left = moment_bounds(histogram, width, roles, low, surcharge)
    right = moment_bounds(histogram, width, roles, high, surcharge)
    require(left[1] < 1 < right[0], "published endpoint signs")
    return {
        "accepted": str(low),
        "rejected": str(high),
        "accepted_upper_minus_one_40_digits": signed_decimal(left[1] - 1),
        "rejected_lower_minus_one_40_digits": signed_decimal(right[0] - 1),
    }


def ceil_div(value):
    return -((-value.numerator) // value.denominator)


def bootstrap(bit_saving, complex_saving):
    eta = beta = Q(1, 10**24)
    common = min(bit_saving, (1 - beta) * complex_saving) - Q(1, 10**27)
    require(0 < common < bit_saving and common < (1 - beta) * complex_saving, "common saving")
    exponent = Q(384599, 10**10)
    rows = []
    for _ in range(7):
        previous = exponent
        exponent = (1 - common) * common + common * previous
        gap = min(common - exponent, 1 - exponent - common,
                  1 - exponent - common * (1 - previous), 1 - common)
        require(previous < exponent < common < 1 - exponent and gap > 0, "bootstrap gap")
        cutoff = max(ceil_div(Q(36, 1) / gap**2), ceil_div(Q(2 * (4 + 512), 1) / gap))
        require(cutoff * gap**2 >= 36 and cutoff * gap >= 2 * (4 + 512), "bootstrap cutoff")
        rows.append({"exponent": exponent, "gap": gap, "cutoff_log2": cutoff})
    rate = exponent * (1 - 2 * eta)
    margin = (1 - eta) * rate / (1 + rate)
    ticks = margin * 10**18
    kappa = Q((ticks.numerator - 1) // ticks.denominator, 10**18)
    return common, exponent, rows, kappa, eta, beta


def outer_slacks(common, complex_saving, kappa, eta, beta):
    """The 47 strict slacks. The first assembly argument is the bootstrapped
    common rate, not the bit-supplier endpoint."""
    bit_slot = common
    tau, sigma = 1 - bit_slot, 1 - complex_saving
    q = bit_slot * (1 - 2 * eta)
    lam_prime = 1 - q
    lam = (tau + lam_prime) / 2
    c = q + eta / 4
    eps = (1 - eta) / (1 + q)
    minimum = eps * q
    alpha = (minimum + 1 - eps) / 2
    delta = eta / 8
    internal = tau + (1 - beta) * max(sigma - tau, Q(0))
    leaf = sigma + beta * (1 - sigma)
    degree_gap = Q(10**6) - Q(51 * 20161, 25)
    margins = {
        "balanced_prefix": 1 - eps,
        "coordinate_movement": bit_slot,
        "compact_phase_layer": minimum,
        "bulk_exposure": bit_slot,
        "Gaussian_arithmetic": min(1 - eps - delta, alpha - delta),
        "scalar_work": 1 - eps - delta,
        "dimension": eps,
    }
    slacks = {
        "bit_positive": bit_slot,
        "complex_above_bit": complex_saving - bit_slot,
        "complex_below_one_over32": Q(1, 32) - complex_saving,
        "beta_positive": beta,
        "beta_below_one": 1 - beta,
        "leaf_saving_above_bit": (1 - beta) * complex_saving - bit_slot,
        "q_positive": q,
        "q_below_internal": 1 - internal - q,
        "q_below_leaf": 1 - leaf - q,
        "c_positive": c,
        "c_below_one": 1 - c,
        "q_below_reservations": c - q,
        "lambda_above_tau": lam - tau,
        "lambda_above_sigma": lam - sigma,
        "lambda_above_internal": lam - internal,
        "lambda_prime_above_lambda": lam_prime - lam,
        "compact_leaf": lam_prime - leaf,
        "compact_reservations": lam_prime - (1 - c),
        "lambda_prime_below_one": q,
        "epsilon_positive": eps,
        "epsilon_below_one": 1 - eps,
        "guard_width": 1 - eps,
        "K_geometry": 1 - eps * (1 + c),
        "K_dominates_log": eps * c,
        "record_suffix": 1 - eps,
        "phase_local": 1 - eps - delta,
        "phase_boundary": alpha - delta,
        "gamma_sublinear": 1 - eps - alpha,
        "cell_above_band": eps - (1 - alpha) / 2,
        "prime_interval_packing": 1 - eps,
        "alpha_positive": alpha,
        "alpha_below_one": 1 - alpha,
        "alpha_below_one_fourth": Q(1, 4) - alpha,
        "delta_positive": delta,
        "delta_below_one_eighth": Q(1, 8) - delta,
        "short_record_fallback": eps - bit_slot,
        "small_field_exposure": 1 - eps - minimum,
        "artificial_boundary": 8 - eps + alpha - delta - minimum,
        "literal_scalar_guard": Q(1),
        "row_product_gap": degree_gap,
    }
    slacks.update({name + "_above_kappa": value - kappa for name, value in margins.items()})
    require(len(slacks) == 47 and len(margins) == 7, "slack inventory")
    require(min(margins.values()) == minimum, "minimum margin")
    require(margins["balanced_prefix"] - minimum == eta, "prefix gap")
    require(1 - eps - alpha == eta / 2, "alpha gap")
    require(1 - eps * (1 + c) == eta - eps * eta / 4, "geometry identity")
    return slacks


def load_histogram(plan, assembly):
    profile = {int(rank): count for rank, count in plan["profile"].items()}
    recorded = {int(rank): count for rank, count in assembly["complex_profile"].items()}
    require(profile == recorded, "PLAN profile differs from the selected assembly")
    width = int(plan["M"])
    roles = int(plan["live"])
    deficit = int(plan["deficit"])
    replicas = int(plan["T"])
    require(width == 73 and replicas == 16 and deficit == 5120, "T16 parameter pin")
    require(roles == replicas * 8 * 112, "live role count T*8*112")
    mass = sum(rank * count for rank, count in profile.items())
    require(width * roles - mass == deficit, "rank-mass deficit")
    require(width * width > 2 * max(profile) ** 2, "recorded halving guard")
    require(assembly["surcharge_model"] == {"complex": False, "bit": True}, "surcharge model")
    require(assembly["binding"] == "complex", "binding side")
    return profile, width, roles


def match_bootstrap(published, rows):
    require(len(published) == len(rows) == 7, "bootstrap length")
    for expected, got in zip(published, rows):
        require(Q(expected["exponent"]) == got["exponent"], "bootstrap exponent")
        require(Q(expected["gap"]) == got["gap"], "bootstrap gap")
        require(int(expected["cutoff_log2"]) == got["cutoff_log2"], "bootstrap cutoff")


def match_slacks(published, slacks):
    require(set(published) == set(slacks), "outer slack names")
    for name, value in slacks.items():
        require(Q(published[name]) == value, "outer slack " + name)
        require(value > 0, "nonpositive published slack")


def negative_outer(common, complex_saving, kappa, eta, beta):
    trials = {
        "next_grid": (common, complex_saving, kappa + Q(1, 10**18), eta, beta),
        "zero_eta": (common, complex_saving, kappa, Q(0), beta),
        "zero_beta": (common, complex_saving, kappa, eta, Q(0)),
        "unit_beta": (common, complex_saving, kappa, eta, Q(1)),
    }
    rejected = []
    for name, args in trials.items():
        slacks = outer_slacks(*args)
        if min(slacks.values()) <= 0:
            rejected.append(name)
    require(rejected == ["next_grid", "zero_eta", "zero_beta", "unit_beta"],
            "outer negative controls")


def main():
    require(not sys.flags.optimize, "PYTHONOPTIMIZE must be unset")
    require(sys.version_info[:2] == (3, 12), "Python 3.12")
    record = json.loads(SELECTED.read_text())
    require(sha256(ASSEMBLY) == record["certificate_sha256"], "assembly hash")
    require(record["certificate"] == "research/community-frontier1094-audit/ASSEMBLY.json",
            "selected certificate path")
    require(record["kappa"] == "836330098538459/500000000000000000", "selected kappa pin")
    assembly = json.loads(ASSEMBLY.read_text())
    plan = json.loads(PLAN.read_text())
    require(Q(assembly["kappa"]) == Q(record["kappa"]), "assembly kappa")
    histogram, width, roles = load_histogram(plan, assembly)
    enclosure_controls()

    native_rows = [row for row in assembly["moments"]
                   if row["side"] == "complex" and row["surcharge"] is False]
    native = check_moment(histogram, width, roles, native_rows, False)
    conservative = check_moment(histogram, width, roles,
                                assembly["conservative_moments"], True)
    native_low = Q(native["accepted"])
    surcharged = moment_bounds(histogram, width, roles, native_low, True)
    require(surcharged[0] > 1, "native endpoint must fail once the old surcharge is added")
    inflated = dict(histogram)
    inflated[48] += 1
    bumped = moment_bounds(inflated, width, roles, native_low, False)
    require(bumped[0] > 1, "an extra rank-48 child must exceed one")
    require(width * roles - sum(rank * count for rank, count in inflated.items()) != 5120,
            "inflation control did not change the deficit")

    bit = Q(assembly["bit_lower"])
    complex_saving = Q(assembly["complex_lower"])
    require(complex_saving == native_low, "complex endpoint binding")
    _common, exponent, rows, kappa, eta, beta = bootstrap(bit, complex_saving)
    require(kappa == Q(assembly["kappa"]), "native kappa grid")
    match_bootstrap(assembly["bootstrap"], rows)
    slacks = outer_slacks(exponent, complex_saving, kappa, eta, beta)
    match_slacks(assembly["outer"], slacks)
    negative_outer(exponent, complex_saving, kappa, eta, beta)

    conservative_saving = Q(assembly["conservative_complex_lower"])
    require(conservative_saving == Q(conservative["accepted"]), "conservative endpoint")
    _ccommon, cexponent, crows, ckappa, ceta, cbeta = bootstrap(bit, conservative_saving)
    require(ckappa == Q(assembly["conservative_kappa"]), "conservative kappa grid")
    match_bootstrap(assembly["conservative_bootstrap"], crows)
    cslacks = outer_slacks(cexponent, conservative_saving, ckappa, ceta, cbeta)
    match_slacks(assembly["conservative_outer"], cslacks)
    negative_outer(cexponent, conservative_saving, ckappa, ceta, cbeta)

    ideal = complex_saving / (1 + complex_saving)
    require(kappa < ideal, "grid kappa is below the unsafeguarded balanced image")
    report = {
        "width": width,
        "roles": roles,
        "calls": sum(histogram.values()),
        "kappa": str(kappa),
        "native": native,
        "conservative": conservative,
        "conservative_kappa": str(ckappa),
        "log_scale": str(SCALE),
        "ln2_width": str(Q(LN2_HI - LN2_LO, SCALE)),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    print("PASS_SELECTED_COMPLEX_ENDPOINT_ENCLOSURE")


if __name__ == "__main__":
    main()
