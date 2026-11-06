#!/usr/bin/env python3
"""Exact endpoint screen for two gauge44 histogram edits.

The selected complex moment uses research/frame-domain-ceiling/engines/moment.py
with surcharge off. This checker does not admit a supplier.
"""
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MOMENT_PATH = ROOT / "research/frame-domain-ceiling/engines/moment.py"
SPEC_PATH = ROOT / "research/complex-t16-rare-pattern-exchanges/data/SPEC.json"
ASSEMBLY_PATH = ROOT / "research/community-frontier1094-audit/ASSEMBLY.json"
MOMENT_SHA256 = "81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482"

CALLS = 144
M_WIDTH = 73
LIVE = 14336
LOCAL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
IDLE = {1: 2276, 3: 377, 7: 7, 48: 4866}
WIDTHS = {4: 56, 5: 32, 7: 30, 8: 122, 9: 240}
HELPER_WIDTH_SUM = 3730
NONHELPER_MASS = 1856
LOCAL_RANKS = (1, 2, 3, 4, 5, 8)
SUPPORT = (1, 2, 3, 4, 5, 7, 8, 48)


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def load_moment():
    body = MOMENT_PATH.read_bytes()
    require(hashlib.sha256(body).hexdigest() == MOMENT_SHA256, "moment engine hash")
    spec = importlib.util.spec_from_file_location("selected_moment_engine", MOMENT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ints(mapping):
    return {int(rank): int(count) for rank, count in mapping.items()}


def histogram(local):
    combined = {rank: CALLS * count for rank, count in local.items() if count}
    for rank, count in IDLE.items():
        combined[rank] = combined.get(rank, 0) + count
    return {rank: count for rank, count in combined.items() if count}


def mass(profile):
    return sum(rank * count for rank, count in profile.items())


def pure_deletions(total):
    found = []

    def walk(index, left, choice):
        if index == len(LOCAL_RANKS):
            if left == 0 and any(choice.values()):
                found.append({rank: count for rank, count in choice.items() if count})
            return
        rank = LOCAL_RANKS[index]
        for count in range(min(LOCAL[rank], left // rank) + 1):
            choice[rank] = count
            walk(index + 1, left - count * rank, choice)
        choice[rank] = 0

    walk(0, total, {})
    return found


def apply_removal(removal):
    local = dict(LOCAL)
    for rank, count in removal.items():
        local[rank] -= count
        require(local[rank] >= 0, "removal exceeds local count")
    return local


def coalesce(count):
    local = dict(LOCAL)
    local[1] -= 8 * count
    local[8] += count
    require(local[1] >= 0, "coalescence exceeds rank-1 count")
    return local


def bounds(engine, profile, exponent):
    lower, upper = engine.moment(profile, M_WIDTH, LIVE, exponent, False)
    require(lower <= upper, "moment interval reversed")
    if upper < 1:
        side = "below"
    elif lower > 1:
        side = "above"
    else:
        side = "straddle"
    return side, lower, upper


def main():
    require(not sys.flags.optimize, "assertions must stay enabled; leave PYTHONOPTIMIZE unset")
    engine = load_moment()
    spec = json.loads(SPEC_PATH.read_text())
    assembly = json.loads(ASSEMBLY_PATH.read_text())
    expected = spec["expected"]
    provider = spec["providers"]["gauge44"]
    contract = provider["complete_contract"]

    require(expected["live"] == LIVE, "live width")
    require(expected["provider_counts"] == {"gauge44": CALLS}, "call count")
    require(ints(expected["global_profile"]) == histogram(LOCAL), "global histogram")
    require(ints(expected["idle_remainder_profile"]) == IDLE, "idle histogram")
    require(ints(provider["expected_profile"]) == LOCAL, "local profile")
    require(ints(contract["width_inventory"]) == WIDTHS, "width inventory")
    require(ints(assembly["complex_profile"]) == histogram(LOCAL), "assembly histogram")
    require(assembly["provider_counts"] == {"gauge44": CALLS}, "assembly calls")
    require(sum(rank * count for rank, count in WIDTHS.items()) == HELPER_WIDTH_SUM, "width sum")
    require(mass(LOCAL) == HELPER_WIDTH_SUM + NONHELPER_MASS, "local mass identity")
    require(M_WIDTH * LIVE - mass(histogram(LOCAL)) == 5120, "global deficit")
    require(assembly["surcharge_model"]["complex"] is False, "complex surcharge flag")

    bit = next(
        Fraction(row["endpoint"])
        for row in assembly["moments"]
        if row["side"] == "bit" and row["accept"] is True and row["surcharge"] is True
    )
    complex_accept = next(
        Fraction(row["endpoint"])
        for row in assembly["moments"]
        if row["side"] == "complex" and row["accept"] is True and row["surcharge"] is False
    )
    complex_reject = next(
        Fraction(row["endpoint"])
        for row in assembly["moments"]
        if row["side"] == "complex" and row["accept"] is False and row["surcharge"] is False
    )
    require(complex_accept == Fraction(expected["complex_lower"]), "complex endpoint pin")
    require(bit == Fraction("1733427039589844234749/1000000000000000000000000"), "bit endpoint")

    baseline = histogram(LOCAL)
    require(bounds(engine, baseline, complex_accept)[0] == "below", "published complex acceptance")
    require(bounds(engine, baseline, complex_reject)[0] == "above", "published complex rejection")
    require(bounds(engine, baseline, bit)[0] == "above", "baseline still above the bit endpoint")
    try:
        engine.moment({M_WIDTH: 1}, M_WIDTH, LIVE, bit, False)
    except AssertionError:
        pass
    else:
        require(False, "rank m must be rejected")

    previous_upper = None
    for rank in reversed(SUPPORT):
        lower, upper = engine.moment({rank: 1}, M_WIDTH, LIVE, bit, False)
        unit_lower, unit_upper = lower / rank, upper / rank
        if previous_upper is not None:
            require(unit_lower > previous_upper, "per-mass cost decreased at rank " + str(rank))
        previous_upper = unit_upper

    mass_one = pure_deletions(1)
    mass_two = pure_deletions(2)
    require(mass_one == [{1: 1}], "unique mass-1 deletion")
    require(sorted(mass_two, key=lambda item: sorted(item)) == [{1: 2}, {2: 1}], "mass-2 deletions")

    deletion_sides = {}
    for removal in mass_one + mass_two:
        label = ",".join(f"{rank}:{count}" for rank, count in sorted(removal.items()))
        side, lower, upper = bounds(engine, histogram(apply_removal(removal)), bit)
        deletion_sides[label] = (side, lower, upper)
    require(deletion_sides["1:1"][0] == "above", "one rank-1 deletion stays above 1")
    require(deletion_sides["1:2"][0] == "below", "two rank-1 deletions fall below 1")
    require(deletion_sides["2:1"][0] == "below", "one rank-2 deletion falls below 1")
    require(deletion_sides["1:2"][2] < deletion_sides["2:1"][1], "two rank-1 deletions are strictly cheaper")

    coalesced = {}
    for count in (42, 43):
        side, lower, upper = bounds(engine, histogram(coalesce(count)), bit)
        coalesced[count] = (side, lower, upper)
        require(mass(coalesce(count)) == mass(LOCAL), "coalescence preserves local mass")
    require(coalesced[42][0] == "above", "42 coalescences stay above 1")
    require(coalesced[43][0] == "below", "43 coalescences fall below 1")

    print(
        "PASS_GAUGE44_HELPER_ENDPOINT_SCREEN "
        "deletion=1:above,2:below coalescence=42:above,43:below "
        "ordering=strict controls=5"
    )


if __name__ == "__main__":
    main()
