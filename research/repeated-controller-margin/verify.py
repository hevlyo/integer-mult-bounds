#!/usr/bin/env python3
"""Exact repeated-evaluation rank margins for the idle-deleted controller model.

The arithmetic is independent of research/controller-border-interface/budget.py.
It rebuilds the local invoices from the vendored predecessor bytes, then checks
the K>=2 rank-mass claim in that package's BUDGET.md. No kappa is computed.
"""
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SEPARATOR = {"complex": Fraction(6), "BIT": Fraction(15, 2)}
LANE = {"complex": (8, 112), "BIT": (7, 111)}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(name):
    return json.loads((PACKAGE / "inputs" / name).read_text())


def rank_mass(profile):
    return sum(rank * count for rank, count in profile.items())


def signed_counts(helpers, paid):
    ranks = set(helpers) | set(paid)
    signed = {rank: helpers.get(rank, 0) - paid.get(rank, 0) for rank in ranks}
    return {rank: count for rank, count in signed.items() if count}


def local_invoices():
    complex_result = load("joint-helper-lattice-RESULT.json")
    invoice = load("BIT-CONTROLLER.json")["invoice"]
    helpers = {int(rank): count for rank, count in complex_result["local_helpers"].items()}
    paid = {int(rank): count for rank, count in complex_result["local_paid"].items()}
    need(all(count > 0 for count in (*helpers.values(), *paid.values())),
         "complex invoice counts")
    full = invoice["thick_calls"]
    need(isinstance(full, int) and full > 0, "thick call count")
    target = Counter({int(rank): count for rank, count in invoice["targets"].items()})
    cost = Counter({int(rank): count for rank, count in invoice["paid"].items()})
    target.subtract({int(rank): count for rank, count in invoice["main"].items()})
    cost.subtract({int(rank): count for rank, count in invoice["whole_idle"].items()})
    cost[1] -= invoice["thin_queries"]
    pieces = [*target.values(), *cost.values()]
    need(all(count >= 0 and count % full == 0 for count in pieces),
         "BIT local profile does not divide evenly")
    bit_helpers = {rank: count // full for rank, count in target.items() if count}
    bit_paid = {rank: count // full for rank, count in cost.items() if count}
    return {
        "complex": {"helpers": helpers, "paid": paid},
        "BIT": {"helpers": bit_helpers, "paid": bit_paid},
    }


def separation(signed, separator):
    positive = [rank for rank, count in signed.items() if count > 0]
    negative = [rank for rank, count in signed.items() if count < 0]
    need(positive and negative, "both sides of the local invoice are present")
    need(all(rank > separator for rank in positive), "positive term at or below separator")
    need(all(rank < separator for rank in negative), "negative term at or above separator")
    return positive, negative


def main_mass(port_count, stage_factor, pairs):
    return 2 * port_count * (pairs + stage_factor * (pairs + 2))


def evaluation_step(pairs, helper_minus_paid, port_count):
    """One extra whole-controller evaluation at t=1, after one main credit."""
    return (pairs + 2) * helper_minus_paid - port_count * (pairs - 1)


def repeated_margin(pairs, evaluations, helper_minus_paid, port_count, stage_factor):
    return (main_mass(port_count, stage_factor, pairs)
            + evaluations * evaluation_step(pairs, helper_minus_paid, port_count))


def doubled_main(pairs, evaluations, helper_minus_paid, port_count, stage_factor):
    """Ownership fault: credit the same main outputs twice."""
    return (repeated_margin(pairs, evaluations, helper_minus_paid, port_count, stage_factor)
            + main_mass(port_count, stage_factor, pairs))


def monotone_hypothesis(signed, separator, stage_factor):
    separation(signed, separator)
    # For every positive integer pair count the Jensen base is 1+b+2b/p > 1+b.
    floor_base = 1 + stage_factor
    need(floor_base > separator > 1, "Jensen base or thin query misses the separator")
    return floor_base


def separated_implication_fails_without_hypothesis():
    """Positive mass below the separator can rise while t falls.

    F(t) = 5*2^t - 3*4^t. Then F(1) < 0 < F(0), so negativity at t=1 does
    not imply negativity at every smaller t.
    """
    def value(t):
        return 5 * (2 ** t) - 3 * (4 ** t)
    need(value(1) < 0 < value(0), "synthetic separated-implication control")
    return {"t0": value(0), "t1": value(1)}


def reject(name, callback):
    try:
        callback()
    except ValueError:
        return name
    raise ValueError("accepted control: " + name)


def controls(invoices):
    rejected = []
    complex_helpers = dict(invoices["complex"]["helpers"])
    complex_helpers[9] += 1
    signed = signed_counts(complex_helpers, invoices["complex"]["paid"])
    rejected.append(reject(
        "extra_rank9_changes_complex_mass",
        lambda: need(rank_mass(signed) == -1856, "mass changed"),
    ))
    bad = {4: 1, 8: -1}
    rejected.append(reject(
        "positive_term_below_separator",
        lambda: separation(bad, Fraction(6)),
    ))
    rejected.append(reject(
        "indivisible_bit_target",
        lambda: bit_profile_or_fail({"targets": {"8": 1}, "paid": {"1": 18},
                                     "main": {}, "whole_idle": {},
                                     "thin_queries": 0, "thick_calls": 18}),
    ))
    return rejected


def bit_profile_or_fail(invoice):
    full = invoice["thick_calls"]
    target = Counter({int(rank): count for rank, count in invoice["targets"].items()})
    cost = Counter({int(rank): count for rank, count in invoice["paid"].items()})
    target.subtract({int(rank): count for rank, count in invoice["main"].items()})
    cost.subtract({int(rank): count for rank, count in invoice["whole_idle"].items()})
    cost[1] -= invoice["thin_queries"]
    need(all(count >= 0 and count % full == 0 for count in (*target.values(), *cost.values())),
         "BIT local profile does not divide evenly")


def lane_report(name, invoice):
    stage_factor, port_count = LANE[name]
    signed = signed_counts(invoice["helpers"], invoice["paid"])
    helper_minus_paid = rank_mass(signed)
    floor_base = monotone_hypothesis(signed, SEPARATOR[name], stage_factor)
    step_slope = evaluation_step(1, helper_minus_paid, port_count) - evaluation_step(0, helper_minus_paid, port_count)
    # evaluation_step(p) = (p+2)*h - v*(p-1) = (h-v)*p + (2h+v)
    step_constant = evaluation_step(0, helper_minus_paid, port_count)
    need(step_slope < 0 and step_constant < 0, "each added evaluation is a negative affine form")
    margin_slope = 2 * port_count * (1 + stage_factor) + 2 * step_slope
    margin_constant = 4 * port_count * stage_factor + 2 * step_constant
    need(margin_slope < 0 and margin_constant < 0, "K=2 margin is negative for every positive pair count")
    for pairs in range(1, 9):
        for evaluations in range(2, 5):
            margin = repeated_margin(pairs, evaluations, helper_minus_paid, port_count, stage_factor)
            need(margin == main_mass(port_count, stage_factor, pairs) + evaluations * evaluation_step(
                pairs, helper_minus_paid, port_count), "margin expansion")
            need(margin < 0, "finite repeated margin")
            need(margin == (margin_slope * pairs + margin_constant)
                 + (evaluations - 2) * evaluation_step(pairs, helper_minus_paid, port_count),
                 "closed form")
    fault = doubled_main(2, 2, helper_minus_paid, port_count, stage_factor)
    correct = repeated_margin(2, 2, helper_minus_paid, port_count, stage_factor)
    need(fault > 0 > correct, "doubled main credit hides the loss")
    return {
        "helper_minus_paid_at_t1": helper_minus_paid,
        "evaluation_step": {"slope": step_slope, "constant": step_constant},
        "two_evaluation_margin": {"slope": margin_slope, "constant": margin_constant},
        "p2_k2_margin": correct,
        "p2_k2_doubled_main": fault,
        "separator": str(SEPARATOR[name]),
        "jensen_base_floor": str(floor_base),
    }


def main():
    invoices = local_invoices()
    need(invoices["complex"]["helpers"] == {4: 28, 7: 7, 8: 47, 9: 326}, "complex helpers")
    need(invoices["complex"]["paid"] == {1: 2237, 2: 388, 3: 494, 4: 147, 5: 36, 8: 8},
         "complex paid")
    need(invoices["BIT"]["helpers"] == {8: 439}, "BIT helpers")
    need(invoices["BIT"]["paid"] == {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19},
         "BIT paid")
    report = {name: lane_report(name, invoice) for name, invoice in invoices.items()}
    need(report["complex"]["helper_minus_paid_at_t1"] == -1856, "complex h(1)")
    need(report["BIT"]["helper_minus_paid_at_t1"] == -1617, "BIT h(1)")
    need(report["complex"]["two_evaluation_margin"] == {"slope": -1920, "constant": -3616},
         "complex K=2 form")
    need(report["BIT"]["two_evaluation_margin"] == {"slope": -1680, "constant": -3138},
         "BIT K=2 form")
    need(report["complex"]["p2_k2_margin"] == -7456, "complex p=2 witness")
    need(report["BIT"]["p2_k2_margin"] == -6498, "BIT p=2 witness")
    need(report["complex"]["p2_k2_doubled_main"] == 160, "complex ownership fault")
    need(report["BIT"]["p2_k2_doubled_main"] == 162, "BIT ownership fault")
    synthetic = separated_implication_fails_without_hypothesis()
    rejected = controls(invoices)
    need(rejected == [
        "extra_rank9_changes_complex_mass",
        "positive_term_below_separator",
        "indivisible_bit_target",
    ], "failure controls")
    print(json.dumps({
        "status": "PASS_REPEATED_CONTROLLER_RANK_MARGINS",
        "lanes": report,
        "synthetic_implication_failure": synthetic,
        "rejected_controls": rejected,
        "kappa_claimed": False,
        "calculus_derivative_formalized": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
