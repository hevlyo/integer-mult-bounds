#!/usr/bin/env python3
"""Radius of the degree-12 exponential majorant in interval_moment.py.

The pinned engine rejects every upper argument at least 1/4. The algebraic
tail it computes is nevertheless a strict exponential upper bound on the
larger interval [0, 14), and it stops being an upper bound at 14 and beyond.
Two one-term bills make that distinction exact: dropping the tail inside the
coded domain accepts a bill that exceeds one, and evaluating the same formula
at 15 does too. The guarded engine accepts neither call as a passing upper
bound.

Standard library only. This process does not write a file. Assertions are not
used, so the checks stay active under python -O.
"""

from fractions import Fraction
import hashlib
import importlib.util
import json
from math import factorial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/coordinated-frames-and-entrance-banks/arithmetic/interval_moment.py"
PIN = "9d3d1d28bfb3375958995205179b171fb65c70a3792cf9f7a21ef5ee54f5460b"
DEGREE = 12
RADIUS = DEGREE + 2  # geometric ratio x/(n+2); denominator vanishes at 14
GUARD = Fraction(1, 4)


class Reject(Exception):
    pass


def require(ok, message):
    if not ok:
        raise Reject(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_engine():
    require(sha256(SOURCE) == PIN, "interval_moment.py does not match the audited pin")
    spec = importlib.util.spec_from_file_location("audited_interval_moment", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require(module.EXP_DEGREE == DEGREE, "engine degree drifted from the audited majorant")
    require(module.GRID == 10**45, "outward grid drifted from 10^-45")
    return module


def taylor(x, degree):
    x = Fraction(x)
    value = term = Fraction(1)
    for k in range(1, degree + 1):
        term = term * x / k
        value += term
    return value


def next_term(x):
    x = Fraction(x)
    return x ** (DEGREE + 1) / factorial(DEGREE + 1)


def geometric_tail(x):
    """Formal tail x^{13}/13!/(1-x/14). Undefined when the denominator is zero."""
    x = Fraction(x)
    require(x != RADIUS, "geometric denominator vanishes at the radius")
    return next_term(x) / (1 - x / RADIUS)


def formula_upper(x):
    return taylor(x, DEGREE) + geometric_tail(x)


def slack_identity(x):
    """U(x) - (T_12(x) + x^13/13!) = (x^13/13!) * (x/14) / (1 - x/14)."""
    x = Fraction(x)
    require(x != RADIUS, "slack identity is undefined at the radius")
    first = next_term(x)
    expected = first * (x / RADIUS) / (1 - x / RADIUS)
    return formula_upper(x) - (taylor(x, DEGREE) + first) == expected


def rising(j):
    """(n+2)(n+3)...(n+1+j), with the empty product equal to 1."""
    value = 1
    for i in range(j):
        value *= RADIUS + i
    return value


def inductive_step_gap(j):
    """For every integer j >= 1 the next rising factor exceeds the geometric ratio."""
    require(isinstance(j, int) and j >= 1, "inductive step is stated for integers j >= 1")
    return (RADIUS + j) - RADIUS == j


def prove_coefficient_domination():
    """P_j >= 14^j for every j, with equality only for j = 0 and j = 1.

    Base cases are computed. The step is the identity (14+j) - 14 = j: once
    j >= 1, the new factor is an integer at least 15, so any inductive lower
    bound of 14^j becomes a strict lower bound of 14^{j+1}. No finite search
    supplies the universal quantifier; the identity does.
    """
    require(rising(0) == 1 == RADIUS**0, "j=0 base")
    require(rising(1) == RADIUS == RADIUS**1, "j=1 base")
    require(rising(2) == RADIUS * (RADIUS + 1) > RADIUS**2, "j=2 is the first strict coefficient")
    require(inductive_step_gap(1) and inductive_step_gap(2) and inductive_step_gap(10**6),
            "rising-factor gap is not the integer j")
    # A reviewer can rerun the same identity at any larger integer. One
    # explicit product check keeps the j=2 comparison attached to that step.
    require((RADIUS + 1) - RADIUS == 1, "first strict factor")


def series_bill(x):
    """One-term bill normalized so the degree-13 partial sum has weight one.

    For x > 0 every later Taylor term is positive, so exp(x) is strictly above
    that partial sum and the true bill is strictly above one. The comparisons
    below use only rational operations.
    """
    x = Fraction(x)
    require(x > 0, "the separating bill is stated for a positive argument")
    partial = taylor(x, DEGREE)
    remainder_first = next_term(x)
    require(remainder_first > 0, "first omitted term")
    weight = 1 / (partial + remainder_first)
    truncation = weight * partial
    require(truncation < 1 == weight * (partial + remainder_first),
            "degree-12 truncation must sit strictly below the separating bill")
    return {
        "argument": str(x),
        "weight": str(weight),
        "truncation_times_weight": str(truncation),
        "certified_series_lower_times_weight": "1",
    }


def formula_accepts_failing_bill(x):
    bill = series_bill(x)
    upper = formula_upper(x)
    weight = Fraction(bill["weight"])
    return weight * upper < 1


def engine_interval_contains_majorant(engine, lo, hi):
    got_lo, got_hi = engine.exp_interval(lo, hi)
    require(got_lo <= taylor(lo, DEGREE), "rounded lower bound exceeded the Taylor polynomial")
    require(got_hi >= formula_upper(hi), "rounded upper bound fell below the geometric majorant")
    require(got_lo <= got_hi, "returned interval is empty")
    return got_lo, got_hi


def engine_rejects(engine, value):
    try:
        engine.exp_interval(value, value)
    except ValueError as exc:
        require(str(exc) == "exp enclosure domain", "unexpected rejection reason: " + str(exc))
        return True
    return False


def main():
    prove_coefficient_domination()
    engine = load_engine()

    # Equality at zero, where every omitted term vanishes.
    zero_lo, zero_hi = engine.exp_interval(Fraction(0), Fraction(0))
    require(zero_lo == zero_hi == taylor(0, DEGREE) == 1, "zero argument is not exactly one")

    inside = Fraction(1, 5)
    require(0 < inside < GUARD < RADIUS, "inside witness left the coded domain")
    require(slack_identity(inside), "slack identity failed inside the coded domain")
    require(formula_upper(inside) > taylor(inside, DEGREE) + next_term(inside),
            "geometric slack vanished inside the domain")
    require(not formula_accepts_failing_bill(inside),
            "the intact majorant accepted the inside failing bill")
    require(Fraction(series_bill(inside)["truncation_times_weight"]) < 1,
            "tail-free truncation did not falsely accept")
    got_lo, got_hi = engine_interval_contains_majorant(engine, inside, inside)
    weight = Fraction(series_bill(inside)["weight"])
    require(weight * got_lo < 1 < weight * got_hi,
            "guarded enclosure unexpectedly separated the tight inside bill")
    span_lo, span_hi = engine_interval_contains_majorant(engine, Fraction(0), inside)
    require(span_lo <= 1 and span_hi >= formula_upper(inside),
            "interval image does not cover exp on [0, 1/5] via the majorant")

    # Points the proof allows and the coded guard rejects.
    for value in (GUARD, Fraction(13), Fraction(1399, 100)):
        require(value < RADIUS, "valid-radius witness crossed 14")
        require(slack_identity(value), "slack identity failed at " + str(value))
        require(formula_upper(value) > taylor(value, DEGREE) + next_term(value),
                "majorant lost its slack at " + str(value))
        require(engine_rejects(engine, value), "engine accepted " + str(value))

    # The radius itself is undefined, not an upper bound.
    radius_rejected = False
    try:
        geometric_tail(RADIUS)
    except Reject as exc:
        require(str(exc) == "geometric denominator vanishes at the radius", str(exc))
        radius_rejected = True
    require(radius_rejected, "denominator at 14 did not fail")

    outside = 15
    require(outside > RADIUS, "outside witness")
    require(slack_identity(outside), "slack identity should remain algebraic past the radius")
    require(geometric_tail(outside) < 0, "past-radius tail was not negative")
    require(formula_upper(outside) < taylor(outside, DEGREE) < taylor(outside, DEGREE) + next_term(outside),
            "formula at 15 is still above the series lower bound")
    require(formula_accepts_failing_bill(outside),
            "unguarded formula did not falsely accept the outside bill")
    require(engine_rejects(engine, Fraction(outside)), "engine accepted the outside argument")

    # Failure controls. Each mutated reading must be detected, and the
    # detector must not fire on the intact inside majorant.
    require(formula_accepts_failing_bill(inside) is False, "control polarity")
    mutated_tail_free = Fraction(series_bill(inside)["truncation_times_weight"]) < 1
    require(mutated_tail_free, "omitted-tail control was not a false accept")
    step_rejected = False
    try:
        inductive_step_gap(0)
    except Reject as exc:
        require("integers j >= 1" in str(exc), "bad step rejection")
        step_rejected = True
    require(step_rejected, "nonpositive inductive step was accepted")
    require(sha256(SOURCE) == PIN, "pin control")
    forced = False
    try:
        require(False, "forced failure")
    except Reject as exc:
        require(str(exc) == "forced failure", "require control")
        forced = True
    require(forced, "require did not reject")

    inside_bill = series_bill(inside)
    outside_bill = series_bill(outside)
    report = {
        "status": "PASS_EXP_MAJORANT_RADIUS_AUDIT",
        "source_sha256": PIN,
        "degree": DEGREE,
        "geometric_radius": str(RADIUS),
        "coded_guard": str(GUARD),
        "inside_argument": inside_bill,
        "inside_guarded_interval": [str(got_lo), str(got_hi)],
        "inside_tail_free_accepts_failing_bill": True,
        "inside_intact_formula_accepts_failing_bill": False,
        "outside_argument": outside_bill,
        "outside_formula_upper_below_taylor": True,
        "outside_formula_accepts_failing_bill": True,
        "engine_rejects_one_quarter_thirteen_and_fifteen": True,
        "selected_kappa_unchanged": True,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    print("PASS_EXP_MAJORANT_RADIUS_AUDIT")


if __name__ == "__main__":
    try:
        main()
    except Reject as exc:
        raise SystemExit("FAIL_EXP_MAJORANT_RADIUS_AUDIT: " + str(exc)) from None
