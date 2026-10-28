#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Optimistic no-arbitrage screen for one U8 width-6 helper inventory.

The frozen catalogue uses helper widths {4, 5, 7, 8, 9} only. This checker
prices one extension that is not a mixture of those 25 interfaces: replace
every width-8 helper in the U8 call by a width-6 helper, delete two rank-1
children per replacement, and give width 6 the most favorable signed price
that does not beat every old six-unit fill marginal. It is a dual relaxation,
not a scalar program or a kappa improvement.
"""

from fractions import Fraction as Q
import hashlib
import importlib.util
import itertools
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WIDTHS = (4, 5, 7, 8, 9)
PRICES = (-1, -20, -8, -2, 4)
BONUSES = {8: 2, 16: 4, 32: 8, 48: -13}
CAPACITIES = (8, 16, 32, 48)
P6 = -39
UNIFORM = Q(1, 500)
U8_LOWER = Q(1664727258740678855772, 10**24)
U8_UPPER = U8_LOWER + Q(1, 10**24)
SCREEN_LOWER = Q(1821649025053055110577, 10**24)
SCREEN_UPPER = SCREEN_LOWER + Q(1, 10**24)
TARGET = Q(1, 99)
ENGINES = {
    "moment.py": "81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482",
    "base_two_moment.py": "aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_engine(name):
    path = ROOT / "research/complex-k492-owner-repair/vendor/multicold/engines" / name
    need(sha256(path) == ENGINES[name], "engine drift: " + name)
    spec = importlib.util.spec_from_file_location(name.replace(".", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def add_form(form, other, factor=Q(1)):
    for rank, coefficient in other.items():
        form[rank] = form.get(rank, Q(0)) + factor * coefficient
        if form[rank] == 0:
            del form[rank]
    return form


def cost_forms():
    multiplier = {1: Q(48, 925), 48: Q(-1, 925)}
    slope = add_form({48: Q(1, 48)}, multiplier, Q(13, 48))
    return slope, multiplier


def bin_form(rank, price):
    slope, multiplier = cost_forms()
    form = {rank: Q(1)} if rank else {}
    add_form(form, slope, -Q(rank))
    add_form(form, multiplier, -Q(price))
    return form


def interval(form, values):
    lower = upper = Q(0)
    for rank, coefficient in form.items():
        lo, hi = values[rank]
        if coefficient < 0:
            lo, hi = hi, lo
        lower += coefficient * lo
        upper += coefficient * hi
    return lower, upper


def fill_best(widths, prices, limit=48):
    best = {0: 0}
    for used in range(1, limit + 1):
        choices = [best[used - width] + price
                   for width, price in zip(widths, prices) if used - width in best]
        if choices:
            best[used] = max(choices)
    return best


def bin_rows(widths, prices):
    best = fill_best(widths, prices)
    rows = []
    maxima = {}
    for capacity, bonus in BONUSES.items():
        for counts in itertools.product(*(range(capacity // width + 1) for width in widths)):
            used = sum(width * count for width, count in zip(widths, counts))
            if used <= capacity:
                price = bonus + sum(p * count for p, count in zip(prices, counts))
                remainder = capacity - used
                rows.append((capacity, remainder, price, counts))
                key = (capacity, remainder)
                maxima[key] = max(maxima.get(key, price), price)
    recurrence = {}
    for capacity, bonus in BONUSES.items():
        for used, score in best.items():
            if used <= capacity:
                key = (capacity, capacity - used)
                recurrence[key] = max(recurrence.get(key, bonus + score), bonus + score)
    need(maxima == recurrence, "bin enumeration and fill recurrence disagree")
    return rows, maxima, best


def derivative_values(engine, kind, right, ranks):
    values = {}
    for rank in ranks:
        if kind == "mercator":
            lo, hi = engine.logarithm(Q(73, rank))
            upper = engine.exponential(Q(0), right * hi)[1]
        else:
            lo, hi = engine.log_bounds(Q(73, rank))
            upper = engine.exp_bounds(right * hi)[1]
        values[rank] = (rank * lo, rank * hi * upper)
    return values


def support_margin(form, derivatives):
    need(sum(rank * coefficient for rank, coefficient in form.items()) == 0,
         "bin dual is not zero at b=0")
    if not form:
        return None
    lower, _upper = interval(form, derivatives)
    return lower


def certify_support(rows, derivatives):
    equalities = set()
    margins = []
    seen = set()
    for _capacity, remainder, price, _counts in rows:
        key = (remainder, price)
        if key in seen:
            continue
        seen.add(key)
        margin = support_margin(bin_form(remainder, price), derivatives)
        if margin is None:
            equalities.add(remainder)
        else:
            need(margin > 0, "bin support derivative failed for remainder " + str(remainder))
            margins.append(margin)
    return equalities, min(margins)


def no_arbitrage_price(best):
    marginals = [(start, best[start + 6] - best[start])
                 for start in range(0, 43) if start in best and start + 6 in best]
    need(marginals, "no six-unit marginal")
    price = min(value for _start, value in marginals)
    places = [start for start, value in marginals if value == price]
    return price, places, marginals


def u8_inventory():
    inventory = {4: 80, 5: 32, 7: 54, 8: 122, 9: 216}
    profile = {1: 2548, 2: 338, 3: 446, 4: 162, 5: 72, 8: 8}
    return inventory, profile


def signed_price(inventory, prices):
    return sum(prices[width] * count for width, count in inventory.items())


def screen_call():
    inventory, profile = u8_inventory()
    need(inventory[8] == 122 and 2 * 122 <= profile[1], "U8 width-8 bill changed")
    inventory = dict(inventory)
    profile = dict(profile)
    inventory[6] = inventory.pop(8)
    profile[1] -= 2 * 122
    mass = sum(rank * count for rank, count in profile.items())
    width = sum(w * count for w, count in inventory.items())
    need(mass - width == 1856, "screen breaks the U8 mass contract")
    prices = dict(zip(WIDTHS, PRICES))
    prices[6] = P6
    return inventory, profile, signed_price(inventory, prices)


def idle_form(width_sum, price_sum):
    """Per-replica idle dual A*R + lambda*S as coefficients of phi(1) and phi(48)."""
    capacity = sum(cap * {8: 672, 16: 448, 32: 448, 48: 448}[cap] for cap in CAPACITIES)
    bonus = sum(BONUSES[cap] * {8: 672, 16: 448, 32: 448, 48: 448}[cap] for cap in CAPACITIES)
    need((capacity, bonus) == (48384, 896), "capacity inventory changed")
    residual = capacity - 9 * width_sum
    signed = bonus + 9 * price_sum
    coefficient_1 = Q(13 * residual + 48 * signed, 925)
    coefficient_48 = Q(19 * residual - signed, 925)
    return coefficient_1, coefficient_48, residual, signed


def replica_histogram(profile, coefficient_1, coefficient_48, replicas=37):
    scale = 9 * replicas
    histogram = {rank: scale * count for rank, count in profile.items()}
    histogram[1] += coefficient_1 * replicas
    histogram[48] = histogram.get(48, 0) + coefficient_48 * replicas
    exact = {rank: Q(value) for rank, value in histogram.items()}
    need(all(value.denominator == 1 and value > 0 for value in exact.values()),
         "screen histogram is not a positive integer profile")
    return {rank: int(value) for rank, value in exact.items()}


def moment_both(mercator, atanh, histogram, saving):
    merc = mercator.moment(histogram, 73, 33152, saving)
    atan = atanh.moment(73, 33152, list(histogram.items()), saving)
    return merc, atan


def run():
    need(not sys.flags.optimize, "exact support checks require assertions")
    mercator = load_engine("moment.py")
    atanh = load_engine("base_two_moment.py")
    old_rows, old_maxima, old_best = bin_rows(WIDTHS, PRICES)
    need(len(old_rows) == 1163, "old bin pattern count changed")
    need(old_best[4] == -1 and old_best[10] == -40, "inherited fill values changed")
    price, places, _marginals = no_arbitrage_price(old_best)
    need(price == P6 and places == [4], "no-arbitrage price is not D(10)-D(4)")
    ranks = list(range(1, 49))
    _slope, multiplier = cost_forms()
    for engine, kind in ((mercator, "mercator"), (atanh, "atanh")):
        derivatives = derivative_values(engine, kind, UNIFORM, ranks)
        need(interval(multiplier, derivatives)[0] > 0, "packing multiplier derivative failed")
        equalities, _margin = certify_support(old_rows, derivatives)
        need(equalities == {0, 1, 48}, "unexpected old support equality")

    _new_rows, new_maxima, _new_best = bin_rows(WIDTHS + (6,), PRICES + (P6,))
    fresh = []
    for key, new_price in new_maxima.items():
        if key not in old_maxima or new_price > old_maxima[key]:
            fresh.append((key[0], key[1], new_price))
    fresh.sort()
    expected_fresh = [(8, 2, -37), (16, 10, -35), (32, 26, -31), (48, 42, -52)]
    need(fresh == expected_fresh, "unexpected new bin maxima: " + str(fresh))
    for engine, kind in ((mercator, "mercator"), (atanh, "atanh")):
        derivatives = derivative_values(engine, kind, UNIFORM, ranks)
        for capacity, remainder, bin_price in expected_fresh:
            margin = support_margin(bin_form(remainder, bin_price), derivatives)
            need(margin is not None and margin > 0,
                 "new width-6 bin loses support at capacity " + str(capacity))

    inventory, profile, price_sum = screen_call()
    width_sum = sum(width * count for width, count in inventory.items())
    need((width_sum, price_sum) == (3534, -5046), "screen width or credit changed")
    coefficient_1, coefficient_48, residual, signed = idle_form(width_sum, price_sum)
    need((residual, signed) == (16578, -44518), "idle residual or credit changed")
    need(coefficient_1 == Q(-76854, 37) and coefficient_48 == Q(14380, 37),
         "idle dual coefficients changed")
    histogram = replica_histogram(profile, coefficient_1, coefficient_48)
    expected = {1: 690378, 2: 112554, 3: 148518, 4: 53946, 5: 23976, 8: 2664, 48: 14380}
    need(histogram == expected, "screen histogram changed")
    paid = sum(rank * count for rank, count in histogram.items())
    need(73 * 33152 - paid == 11840, "screen deficit changed")

    u8_histogram = {1: 848490, 2: 112554, 3: 148518, 4: 53946, 5: 23976, 8: 2664, 48: 11086}
    for saving, screen_below, u8_below in (
            (U8_LOWER, True, True),
            (U8_UPPER, True, False),
            (SCREEN_LOWER, True, False),
            (SCREEN_UPPER, False, False),
            (UNIFORM, False, False),
            (TARGET, False, False)):
        for label, bounds in zip(("mercator", "atanh"), moment_both(mercator, atanh, histogram, saving)):
            upper_below = bounds[1] < 1
            lower_above = bounds[0] > 1
            need(upper_below if screen_below else lower_above,
                 label + " screen sign failed at " + str(saving))
        if saving in (U8_LOWER, U8_UPPER):
            for label, bounds in zip(("mercator", "atanh"),
                                     moment_both(mercator, atanh, u8_histogram, saving)):
                need((bounds[1] < 1) if u8_below else (bounds[0] > 1),
                     label + " U8 wiring check failed at " + str(saving))

    root = mercator.certify(histogram, 73, 33152)
    need(root["lower"] == "0.001821649025053055110577"
         and root["upper"] == "0.001821649025053055110578",
         "mercator root bracket changed")
    need(SCREEN_UPPER < UNIFORM < TARGET, "screen root is not inside the support interval and below 1/99")

    # Equal-mass rank-2 deletion is strictly costlier at the accepting tick.
    rank_two = dict(histogram)
    rank_two[1] += 244 * 9 * 37
    rank_two[2] -= 122 * 9 * 37
    need(rank_two[2] > 0, "rank-2 alternative is not available in U8")
    for label, screen_bounds, other_bounds in zip(
            ("mercator", "atanh"),
            moment_both(mercator, atanh, histogram, SCREEN_LOWER),
            moment_both(mercator, atanh, rank_two, SCREEN_LOWER)):
        need(other_bounds[0] > screen_bounds[1],
             label + " does not separate the rank-2 deletion")

    controls = run_controls(old_best, derivative_values(mercator, "mercator", UNIFORM, ranks))
    controls.append("rank_two_deletion_strictly_costlier")
    return {"status": "PASS_U8_WIDTH6_NA_SCREEN",
            "histogram": histogram,
            "root": [str(SCREEN_LOWER), str(SCREEN_UPPER)],
            "planning_kappa_upper": str(SCREEN_UPPER / (1 + SCREEN_UPPER)),
            "controls": controls}


def run_controls(old_best, derivatives):
    # Seventy units above the accepted cap-8 width-6 price -37.
    excessive = support_margin(bin_form(2, 33), derivatives)
    need(excessive is not None and excessive < 0, "excessive remainder-2 credit passed")
    subsidized = old_best[4] + (P6 - 1)
    need(subsidized < old_best[10], "price -40 does not beat the old width-10 fill")
    _inventory, profile = u8_inventory()
    short = dict(profile)
    short[1] -= 243
    need(sum(rank * count for rank, count in short.items()) - 3534 != 1856,
         "a one-unit-short deletion still met the mass contract")
    return ["excessive_remainder_2_credit_rejected",
            "price_minus_40_beats_old_ten_fill",
            "short_rank_deletion_rejected"]


def main():
    result = run()
    print(result["status"],
            "root=0.001821649025053055110577..0.001821649025053055110578",
          "kappa_cap=" + result["planning_kappa_upper"],
          "controls=" + str(len(result["controls"])))


if __name__ == "__main__":
    main()
