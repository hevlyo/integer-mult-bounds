#!/usr/bin/env python3
"""Optimistic moment of one width-6 narrowing of the selected gauge44 inventory.

The selected T16 word uses helper widths in {4, 5, 7, 8, 9}. This check prices
the edit that replaces each of the 122 width-8 helpers by one width-6 helper,
preserves the paid-rank excess 1856 by deleting 244 rank-1 children, and places
every freed width unit into rank-48 residuals. It is an upper bound under those
hypotheses, not a circuit, an owner map, or a new kappa.
"""

import hashlib
import importlib.util
import json
from collections import Counter
from decimal import Decimal, ROUND_FLOOR, localcontext
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent

SPEC = "research/complex-t16-rare-pattern-exchanges/data/SPEC.json"
PLAN = "research/gauge44-slots/data/PLAN.json"
CATALOGUE = "research/heterogeneous-owner-assembly/CATALOGUE.json"
MOMENT = "research/complex-k492-owner-repair/vendor/multicold/engines/moment.py"

PINS = {
    SPEC: "8cb51f25a5da4a29d3783853025b73ff1f452429d4fdb30c599e598bcab0e71d",
    PLAN: "1dec4ca3af6d45d82286005cae4c5e56e7253adefb117d797da55c55c891af08",
    CATALOGUE: "8650a35d8292cf08711aac2d5d39e6e700010e6c7ce273b215e577c984b2ad07",
    MOMENT: "81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482",
}

CALLS = 144
REPLICAS = 16
M_AMBIENT = 73
LIVE = 14336
EXCESS = 1856
CAPACITY = {8: 672, 16: 448, 32: 448, 48: 448}
OLD_WIDTHS = {4: 56, 5: 32, 7: 30, 8: 122, 9: 240}
LOCAL_PAID = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
NARROWED = 122
WIDTH_DROP = 2 * NARROWED
SELECTED_ROOT = 1675462676808103522925
CONCENTRATED_ROOT = 1682094870064815352349
WIDTH6_ROOT = 1760855940405956673857


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(condition, message):
    if not condition:
        fail(message)


def load_json(rel):
    path = ROOT / rel
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PINS[rel], "sha256 drift: " + rel)
    return json.loads(raw)


def load_moment():
    path = ROOT / MOMENT
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PINS[MOMENT], "moment engine drift")
    spec = importlib.util.spec_from_file_location("selected_width6_moment", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def histogram(counter):
    return {int(rank): int(count) for rank, count in sorted(counter.items()) if count}


def mass(counter):
    return sum(rank * count for rank, count in counter.items())


def scale(profile, factor):
    return Counter({rank: count * factor for rank, count in profile.items()})


def proposed_endpoint(profile, moment):
    """Same Decimal proposal as moment.certify, without the bad-residue envelope."""
    items = histogram(profile)
    with localcontext() as ctx:
        ctx.prec = 70
        terms = [
            (Decimal(rank * count) / Decimal(M_AMBIENT * LIVE),
             (Decimal(M_AMBIENT) / Decimal(rank)).ln())
            for rank, count in items.items()
        ]
        low = Decimal(0)
        high = Decimal(".003")
        for _ in range(210):
            midpoint = (low + high) / 2
            bill = sum(weight * (midpoint * log_term).exp() for weight, log_term in terms)
            if bill < 1:
                low = midpoint
            else:
                high = midpoint
        numerator = int(((low + high) / 2 * 10**24).to_integral_value(rounding=ROUND_FLOOR))
    root = Fraction(numerator, 10**24)
    below = moment.moment(items, M_AMBIENT, LIVE, root, False)
    above = moment.moment(items, M_AMBIENT, LIVE, root + Fraction(1, 10**24), False)
    require(below[1] < 1 < above[0], "endpoint signs failed for " + str(items))
    return numerator


def optimistic(local_paid, helper_mass):
    """Paid children, plus idle rank mass concentrated at rank 48."""
    paid = scale(local_paid, CALLS)
    capacity = REPLICAS * sum(size * count for size, count in CAPACITY.items())
    idle_mass = capacity - CALLS * helper_mass
    require(idle_mass > 0 and idle_mass % 48 == 0, "idle mass is not a positive multiple of 48")
    paid[48] += idle_mass // 48
    require(max(paid) <= 48, "histogram left the admitted rank cap")
    return paid


def main():
    require(__debug__, "assertions must stay enabled; do not run under PYTHONOPTIMIZE or python -O")
    moment = load_moment()
    spec = load_json(SPEC)
    plan = load_json(PLAN)
    catalogue = load_json(CATALOGUE)

    selected = Counter({int(rank): count for rank, count in spec["expected"]["global_profile"].items()})
    require(spec["expected"]["provider_counts"] == {"gauge44": CALLS}, "provider count")
    require(spec["expected"]["live"] == LIVE, "live width")
    require(spec["expected"]["rank_mass"] == mass(selected), "published rank mass")
    require(M_AMBIENT * LIVE - mass(selected) == 5120, "selected deficit")
    require(int(spec["expected"]["complex_lower"].split("/")[0]) * 25 == SELECTED_ROOT,
            "published complex endpoint")

    registry = plan["provider_registry"]["gauge44"]
    local = Counter({int(rank): count for rank, count in registry["actual_paid_profile"].items()})
    require(dict(local) == LOCAL_PAID, "local paid profile")
    widths = Counter(registry["widths"])
    require(dict(widths) == OLD_WIDTHS, "registry width inventory")
    require(len(registry["widths"]) == 480, "helper count")
    helper_mass = mass(widths)
    require(helper_mass == 3730, "helper mass")
    require(mass(local) - helper_mass == EXCESS, "paid-rank excess")
    calls = plan["per_call_widths"]
    require(len(calls) == 72, "T8 call count in the width plan")
    require(all(Counter(call["widths"]) == widths for call in calls), "call widths differ")

    idle = selected - scale(local, CALLS)
    require(all(count > 0 for count in idle.values()), "selected idle is not the global remainder")
    require(mass(idle) == REPLICAS * sum(size * count for size, count in CAPACITY.items())
            - CALLS * helper_mass, "capacity total does not match selected idle")
    require(max(selected) == 48, "selected profile already uses a rank above 48")

    for interface in catalogue["interfaces"]:
        inventory = {int(width): count for width, count in interface["inventory"].items()}
        require(set(inventory) <= {4, 5, 7, 8, 9}, "catalogue width outside {4,5,7,8,9}")
        require(6 not in inventory, "catalogue already contains width 6")
        require(inventory != {4: 56, 5: 32, 6: 122, 7: 30, 9: 240}, "catalogue contains this edit")

    concentrated = optimistic(local, helper_mass)
    narrowed_local = Counter(local)
    narrowed_local[1] -= WIDTH_DROP
    require(narrowed_local[1] > 0, "rank-1 deletion exceeds the local profile")
    narrowed_mass = helper_mass - WIDTH_DROP
    require(mass(narrowed_local) - narrowed_mass == EXCESS, "narrowed excess")
    narrowed = optimistic(narrowed_local, narrowed_mass)
    require(histogram(narrowed)[1] == CALLS * narrowed_local[1], "paid rank-1 count")
    require(narrowed[48] == 5670, "concentrated rank-48 count")
    require(6 not in narrowed, "width 6 is not a paid child rank in this edit")

    same_mass = Counter(OLD_WIDTHS)
    same_mass[4] -= 1
    same_mass[8] -= 1
    same_mass[6] = 2
    require(mass(same_mass) == helper_mass, "constant-mass width-6 swap")
    require(optimistic(local, mass(same_mass)) == concentrated,
            "constant-mass width change moved the optimistic histogram")

    selected_root = proposed_endpoint(selected, moment)
    concentrated_root = proposed_endpoint(concentrated, moment)
    narrowed_root = proposed_endpoint(narrowed, moment)
    require(selected_root == SELECTED_ROOT, "selected root changed")
    require(concentrated_root == CONCENTRATED_ROOT, "concentrated root changed")
    require(narrowed_root == WIDTH6_ROOT, "width-6 root changed")
    require(SELECTED_ROOT < CONCENTRATED_ROOT < WIDTH6_ROOT, "root order")
    require(99 * WIDTH6_ROOT < 10**24, "width-6 relaxation reached 1/99")
    require(Fraction(WIDTH6_ROOT, 10**24 + WIDTH6_ROOT) < Fraction(1, 100),
            "ideal balanced cap reached 1/100")

    # A forged extra rank-1 child makes the width-6 endpoint inadmissible.
    forged = Counter(narrowed)
    forged[1] += 1
    forged_at_root = moment.moment(histogram(forged), M_AMBIENT, LIVE,
                                   Fraction(WIDTH6_ROOT, 10**24), False)
    require(forged_at_root[0] > 1, "extra rank-1 was still admissible at the width-6 root")

    # Deleting one rank-48 child must not keep the same certified numerator.
    depleted = Counter(narrowed)
    depleted[48] -= 1
    require(proposed_endpoint(depleted, moment) != WIDTH6_ROOT,
            "depleted histogram kept the width-6 root")

    # Breaking the excess while narrowing is outside the priced contract.
    broken = mass(local) - narrowed_mass
    require(broken != EXCESS, "unchanged paid profile accidentally preserved the excess")

    print("PASS_SELECTED_WIDTH6_NARROWING")
    print("selected_root", f"{SELECTED_ROOT}/10^24")
    print("same_mass_concentrated_root", f"{CONCENTRATED_ROOT}/10^24")
    print("width6_root", f"{WIDTH6_ROOT}/10^24")
    print("width6_below_1/99", True)
    print("ideal_kappa_cap", f"{WIDTH6_ROOT}/{10**24 + WIDTH6_ROOT}")
    print("controls", 4)


if __name__ == "__main__":
    main()
