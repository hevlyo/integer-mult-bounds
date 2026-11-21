#!/usr/bin/env python3
"""Independent ledger recount and first-order diagnostic for the selected histogram.

The paid rank histogram is rebuilt from the frozen T16 owner roles, window
capacities and the declared gauge44 local profile. The saved global aggregate
is a comparison target only. The first-order diagnostic a < D/E is enclosed
with rational logarithms. This file does not import a moment engine.

The selected moment sign, outer assembly and cold replay are not repeated.
"""

import gzip
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = "research/complex-t16-rare-pattern-exchanges/data/PLAN.json"
OWNERS_PATH = "research/complex-t16-rare-pattern-exchanges/OWNERS.json.gz"
ASSEMBLY_PATH = "research/community-frontier1094-audit/ASSEMBLY.json"
PINS = {
    PLAN_PATH: "7bd786ba8e66408f02aa9ef446eaf20c1bfe981ea2e4dd1e5a929f0aa7767bc0",
    OWNERS_PATH: "87902c528dfab7d503dcf8a784260e3ab6fb7424c418a1820f7261f25be7b6bc",
    ASSEMBLY_PATH: "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
}
V = 112
T = 16
M = 73
SERIES_TERMS = 24


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_bound_inputs():
    loaded = {}
    for name, pin in PINS.items():
        path = ROOT / name
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == pin, "source pin " + name)
        if name.endswith(".gz"):
            loaded[name] = json.loads(gzip.decompress(raw))
        else:
            loaded[name] = json.loads(raw)
    return loaded


class Interval:
    def __init__(self, lo, hi):
        require(lo <= hi, "empty interval")
        self.lo = lo
        self.hi = hi

    def __add__(self, other):
        return Interval(self.lo + other.lo, self.hi + other.hi)

    def __sub__(self, other):
        return Interval(self.lo - other.hi, self.hi - other.lo)

    def scale(self, factor):
        require(factor > 0, "positive scale")
        return Interval(self.lo * factor, self.hi * factor)


def ln1p_bounds(numerator, denominator, terms):
    """Rational bounds for ln(1 + numerator/denominator), both arguments positive."""
    require(numerator > 0 and denominator > 0 and terms >= 2, "log series domain")
    y_num = numerator
    y_den = 2 * denominator + numerator
    acc_num, acc_den = 0, 1
    power_num, power_den = y_num, y_den
    y2_num, y2_den = y_num * y_num, y_den * y_den
    for k in range(terms):
        term_num = 2 * power_num
        term_den = power_den * (2 * k + 1)
        acc_num = acc_num * term_den + term_num * acc_den
        acc_den *= term_den
        common = gcd(acc_num, acc_den)
        acc_num //= common
        acc_den //= common
        power_num *= y2_num
        power_den *= y2_den
        common = gcd(power_num, power_den)
        power_num //= common
        power_den //= common
    # After the loop, power is y**(2*terms+1). The positive tail is strictly
    # below the geometric majorant 2 y**(2N+1) / ((2N+1) (1-y*y)).
    gap_num = y_den * y_den - y_num * y_num
    require(gap_num > 0, "log contraction")
    rem_num = 2 * power_num * y_den * y_den
    rem_den = power_den * (2 * terms + 1) * gap_num
    lower = Fraction(acc_num, acc_den)
    upper = lower + Fraction(rem_num, rem_den)
    return Interval(lower, upper)


def gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)


def log_intervals():
    ln2 = ln1p_bounds(1, 1, SERIES_TERMS)
    ln3 = ln1p_bounds(2, 1, SERIES_TERMS)
    ln5_over_4 = ln1p_bounds(1, 4, SERIES_TERMS)
    ln73_over_64 = ln1p_bounds(9, 64, SERIES_TERMS)
    ln73_over_72 = ln1p_bounds(1, 72, SERIES_TERMS)
    ln73_over_70 = ln1p_bounds(3, 70, SERIES_TERMS)
    return {
        1: ln73_over_64 + ln2.scale(6),
        2: ln73_over_64 + ln2.scale(5),
        3: ln73_over_72 + ln2.scale(3) + ln3,
        4: ln73_over_64 + ln2.scale(4),
        5: ln73_over_64 + ln2.scale(4) - ln5_over_4,
        7: ln73_over_70 + ln2.scale(3) + ln5_over_4,
        8: ln73_over_64 + ln2.scale(3),
        48: ln73_over_64 + ln2.scale(2) - ln3,
    }


def diagnostic_gap(histogram, endpoint):
    """Return rational bounds on D/E - endpoint for natural-log D and E."""
    require(endpoint > 0, "endpoint")
    mass = sum(rank * count for rank, count in histogram.items())
    live = 8 * T * V
    deficit = M * live - mass
    require(deficit > 0, "nonpositive deficit")
    logs = log_intervals()
    require(set(histogram) <= set(logs), "log reduction missing a rank")
    energy = None
    for rank, count in histogram.items():
        require(count > 0 and rank > 0, "histogram entry")
        piece = logs[rank].scale(count * rank)
        energy = piece if energy is None else energy + piece
    # D/E decreases in E, so the lower diagnostic is D/E_hi.
    diagnostic_lo = Fraction(deficit) / energy.hi
    diagnostic_hi = Fraction(deficit) / energy.lo
    return {
        "deficit": deficit,
        "energy_lower": energy.lo,
        "energy_upper": energy.hi,
        "diagnostic_lower": diagnostic_lo,
        "diagnostic_upper": diagnostic_hi,
        "gap_lower": diagnostic_lo - endpoint,
        "gap_upper": diagnostic_hi - endpoint,
    }


def row_coefficient(physical):
    half = M // 2
    group = 1 << (half * half)
    for index in range(1, half + 1):
        group *= (1 << (2 * index)) - 1
    stock = group * physical
    return 2 * stock.bit_length() + 9909 + 252 + 1024, stock.bit_length()


def recount(plan, roles):
    registry = plan["provider_registry"]
    require(set(registry) == {"gauge44"}, "provider set")
    provider = registry["gauge44"]
    widths = provider["widths"]
    require(all(type(width) is int and width > 0 for width in widths), "helper widths")
    helpers = len(widths)
    centres = provider["centers"]
    require(type(centres) is list and centres, "centres")
    live = 8 * T * V
    require(plan["live"] == live, "live wires")
    physical = live + len(centres) + helpers + 2
    order = [tuple(call) for call in plan["order"]]
    require(len(order) == len(set(order)) == 144, "call order")
    position = {call: index for index, call in enumerate(order)}
    width_rows = plan["per_call_widths"]
    require(len(width_rows) == len(order), "per-call width rows")
    for row in width_rows:
        require(tuple((row["stage"], row["replica"])) in position, "per-call width key")
        require(row["widths"] == widths, "per-call widths")
    windows = {}
    for key, spec in plan["windows"].items():
        cap, times = spec
        replica, child = (int(part) for part in key.split(","))
        require(type(cap) is int and cap > 0, "window capacity")
        windows[(replica, child)] = (cap, set(times))
    pairs = {int(key): value for key, value in plan["pairs"].items()}
    sides = {int(key): value for key, value in plan["sides"].items()}
    seen_helpers = defaultdict(set)
    seen_families = defaultdict(set)
    slices = defaultdict(list)
    for role in roles:
        call = (role["stage"], role["replica"])
        require(call in position and role["time"] == position[call], "role invocation time")
        helper = role["helper"]
        require(helper not in seen_helpers[call] and 0 <= helper < helpers, "helper inventory")
        require(role["width"] == widths[helper], "whole-helper residual width")
        seen_helpers[call].add(helper)
        owner, child, port = role["owner_replica"], role["child"], role["port"]
        require(role["copy"] == owner * V + port, "copy identity")
        family = owner * (8 * V) + (2 * pairs[child] + sides[child]) * V + port
        require(role["family"] == family, "family identity")
        require(family not in seen_families[call], "duplicate family in one call")
        seen_families[call].add(family)
        cap, times = windows[(owner, child)]
        require(role["time"] in times, "idle window")
        require(0 <= role["offset"] and role["offset"] + role["width"] <= cap, "slice capacity")
        slices[(owner, child, port)].append((role["offset"], role["width"]))
    require(set(seen_helpers) == set(order), "complete call set")
    require(all(found == set(range(helpers)) for found in seen_helpers.values()), "complete helper inventory")
    require(len(roles) == len(order) * helpers, "role count")
    hosted = {}
    for key, parts in slices.items():
        cursor = 0
        for offset, width in sorted(parts):
            require(offset == cursor, "gap or overlap in owner prefix")
            cursor += width
        cap = windows[(key[0], key[1])][0]
        require(cursor <= cap, "slice capacity")
        hosted[key] = cursor
    idle = Counter()
    for (replica, child), (cap, _times) in windows.items():
        for port in range(V):
            used = hosted.get((replica, child, port), 0)
            left = cap - used
            require(left >= 0, "idle rank")
            if left:
                idle[left] += 1
    local = {int(rank): count for rank, count in provider["actual_paid_profile"].items()}
    require(all(rank > 0 and count > 0 for rank, count in local.items()), "local profile")
    paid = Counter()
    for rank, count in local.items():
        paid[rank] += len(order) * count
    paid.update(idle)
    mass = sum(rank * count for rank, count in paid.items())
    deficit = M * live - mass
    require(deficit == live - 64 * len(order) == 5120, "deficit identity")
    require(M * M > 2 * max(paid) ** 2, "halving guard")
    coefficient, stock_bits = row_coefficient(physical)
    require(coefficient == 16469 and stock_bits == 2642, "physical row coefficient")
    return {
        "helpers": helpers,
        "centres": len(centres),
        "live": live,
        "physical": physical,
        "calls": len(order),
        "roles": len(roles),
        "local_profile": dict(sorted(local.items())),
        "idle": dict(sorted(idle.items())),
        "histogram": dict(sorted(paid.items())),
        "rank_mass": mass,
        "deficit": deficit,
        "row_coefficient": coefficient,
        "stock_bits": stock_bits,
    }


def selected_endpoint(assembly, histogram):
    profile = {int(rank): count for rank, count in assembly["complex_profile"].items()}
    require(profile == histogram, "recounted histogram differs from selected profile")
    endpoint = Fraction(assembly["complex_lower"])
    require(assembly["complex_lower"] == "67018507072324140917/40000000000000000000000", "selected endpoint literal")
    require(assembly["binding"] == "complex", "binding side")
    return endpoint


def failure_controls(plan, roles, endpoint, gap):
    truncated = [dict(role) for role in roles]
    truncated[0]["width"] = truncated[0]["width"] - 1
    expect_reject("truncated width", lambda: recount(plan, truncated), "whole-helper residual width")

    groups = defaultdict(list)
    for index, role in enumerate(roles):
        groups[(role["owner_replica"], role["child"], role["port"])].append(index)
    pair = next(indexes for indexes in groups.values() if len(indexes) >= 2)
    overlapped = [dict(role) for role in roles]
    overlapped[pair[1]]["offset"] = overlapped[pair[0]]["offset"]
    expect_reject("overlapped slices", lambda: recount(plan, overlapped), "gap or overlap in owner prefix")

    overclaim = gap["diagnostic_upper"]
    expect_reject(
        "diagnostic overclaim",
        lambda: require_below(overclaim, gap),
        "endpoint is not strictly below the diagnostic",
    )
    saturated = {1: M * 8 * T * V}
    expect_reject(
        "nonpositive deficit",
        lambda: diagnostic_gap(saturated, endpoint),
        "nonpositive deficit",
    )


def require_below(endpoint, gap):
    require(gap["gap_lower"] > 0 and endpoint < gap["diagnostic_lower"], "endpoint is not strictly below the diagnostic")


def expect_reject(name, function, fragment):
    try:
        function()
    except ValueError as exc:
        require(fragment in str(exc), "control " + name + " failed differently: " + str(exc))
    else:
        raise ValueError("control accepted: " + name)


def main():
    loaded = load_bound_inputs()
    plan = loaded[PLAN_PATH]
    roles = loaded[OWNERS_PATH]
    assembly = loaded[ASSEMBLY_PATH]
    # The saved aggregate is not an input to the sum. Read it only after recount.
    ledger = recount(plan, roles)
    saved = {int(rank): count for rank, count in plan["profile"].items()}
    require(saved == ledger["histogram"], "recounted histogram differs from saved plan aggregate")
    require(plan["deficit"] == ledger["deficit"], "saved deficit field")
    endpoint = selected_endpoint(assembly, ledger["histogram"])
    gap = diagnostic_gap(ledger["histogram"], endpoint)
    # These are consequences of the series enclosure, not inputs to it.
    require(gap["gap_lower"] > Fraction(5128032946218, 10**18), "diagnostic gap lower bound")
    require(gap["gap_upper"] < Fraction(5128032946219, 10**18), "diagnostic gap upper bound")
    require(gap["diagnostic_lower"] > endpoint, "endpoint is not strictly below the diagnostic")
    failure_controls(plan, roles, endpoint, gap)
    report = {
        "status": "PASS_SELECTED_LINEAR_DIAGNOSTIC_GAP",
        "calls": ledger["calls"],
        "roles": ledger["roles"],
        "helpers": ledger["helpers"],
        "centres": ledger["centres"],
        "live": ledger["live"],
        "physical": ledger["physical"],
        "local_profile": ledger["local_profile"],
        "idle": ledger["idle"],
        "histogram": ledger["histogram"],
        "rank_mass": ledger["rank_mass"],
        "deficit": ledger["deficit"],
        "row_coefficient": ledger["row_coefficient"],
        "stock_bits": ledger["stock_bits"],
        "endpoint": str(endpoint),
        "diagnostic_lower": str(gap["diagnostic_lower"]),
        "diagnostic_upper": str(gap["diagnostic_upper"]),
        "gap_lower": str(gap["gap_lower"]),
        "gap_upper": str(gap["gap_upper"]),
        "series_terms": SERIES_TERMS,
        "controls_rejected": [
            "truncated width",
            "overlapped slices",
            "diagnostic overclaim",
            "nonpositive deficit",
        ],
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    print(report["status"])


if __name__ == "__main__":
    main()
