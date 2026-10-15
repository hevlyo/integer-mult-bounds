#!/usr/bin/env python3
"""Named outer slacks of the selected frontier, independent of the receipt count.

The selected replay accepts an outer map when it has 47 positive values. This
checker recomputes the 47 named slacks and the published kappa floor from the
certificate endpoints. It does not import the supplier outer engine, replay a
circuit, or change kappa.

The formulas are the retained balanced assembly: Zhihao Chen's PR23, icekylinx's
structured-bulk constraints, and the RaD balanced prefix, as used by the gauge44
outer witness with eta = beta = 10^-24. The engine's first argument is the
seventh bootstrap iterate, historically called bit_saving; it is not the PR589
bit lower bound.
"""
from fractions import Fraction
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
ASSEMBLY = ROOT / "research/community-frontier1094-audit/ASSEMBLY.json"
FRONTIER = ROOT / "scripts/verify_frontier1094.py"
T16 = ROOT / "research/gauge44-slots-t16/verify_t16.py"

ETA = Fraction(1, 10**24)
BETA = Fraction(1, 10**24)
ROW_GAP = Fraction(10**6) - Fraction(51 * 20161, 25)
FRONTIER_PREDICATE = (
    "require(len(assembly['outer']) == 47 and all(Fraction(v)>0 "
    "for v in assembly['outer'].values()), 'Strict outer assembly')"
)
T16_PREDICATE = (
    "assert len(asm['outer']) == 47 and all(Fraction(v) > 0 "
    "for v in asm['outer'].values()), 'all 47 strict outer margins'"
)
CONTROLS = (
    ("next_grid", "kappa_step"),
    ("zero_eta", "eta"),
    ("zero_beta", "beta"),
    ("unit_beta", "beta"),
)


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def production_predicate(outer):
    """The receipt check in the selected frontier wrapper and the T16 verifier."""
    return len(outer) == 47 and all(Fraction(value) > 0 for value in outer.values())


def named_slacks(iterate, complex_saving, kappa, eta, beta):
    """Forty base slacks plus seven margin-above-kappa slacks."""
    bit_saving = iterate
    tau, sigma = 1 - bit_saving, 1 - complex_saving
    q = bit_saving * (1 - 2 * eta)
    lambda_prime = 1 - q
    lam = (tau + lambda_prime) / 2
    c_param = q + eta / 4
    eps = (1 - eta) / (1 + q)
    minimum = eps * q
    alpha = (minimum + 1 - eps) / 2
    delta = eta / 8
    internal = tau + (1 - beta) * max(sigma - tau, Fraction(0))
    leaf = sigma + beta * (1 - sigma)
    margins = {
        "balanced_prefix": 1 - eps,
        "coordinate_movement": bit_saving,
        "compact_phase_layer": minimum,
        "bulk_exposure": bit_saving,
        "Gaussian_arithmetic": min(1 - eps - delta, alpha - delta),
        "scalar_work": 1 - eps - delta,
        "dimension": eps,
    }
    slacks = {
        "bit_positive": bit_saving,
        "complex_above_bit": complex_saving - bit_saving,
        "complex_below_one_over32": Fraction(1, 32) - complex_saving,
        "beta_positive": beta,
        "beta_below_one": 1 - beta,
        "leaf_saving_above_bit": (1 - beta) * complex_saving - bit_saving,
        "q_positive": q,
        "q_below_internal": 1 - internal - q,
        "q_below_leaf": 1 - leaf - q,
        "c_positive": c_param,
        "c_below_one": 1 - c_param,
        "q_below_reservations": c_param - q,
        "lambda_above_tau": lam - tau,
        "lambda_above_sigma": lam - sigma,
        "lambda_above_internal": lam - internal,
        "lambda_prime_above_lambda": lambda_prime - lam,
        "compact_leaf": lambda_prime - leaf,
        "compact_reservations": lambda_prime - (1 - c_param),
        "lambda_prime_below_one": q,
        "epsilon_positive": eps,
        "epsilon_below_one": 1 - eps,
        "guard_width": 1 - eps,
        "K_geometry": 1 - eps * (1 + c_param),
        "K_dominates_log": eps * c_param,
        "record_suffix": 1 - eps,
        "phase_local": 1 - eps - delta,
        "phase_boundary": alpha - delta,
        "gamma_sublinear": 1 - eps - alpha,
        "cell_above_band": eps - (1 - alpha) / 2,
        "prime_interval_packing": 1 - eps,
        "alpha_positive": alpha,
        "alpha_below_one": 1 - alpha,
        "alpha_below_one_fourth": Fraction(1, 4) - alpha,
        "delta_positive": delta,
        "delta_below_one_eighth": Fraction(1, 8) - delta,
        "short_record_fallback": eps - bit_saving,
        "small_field_exposure": 1 - eps - minimum,
        "artificial_boundary": 8 - eps + alpha - delta - minimum,
        "literal_scalar_guard": Fraction(1),
        "row_product_gap": ROW_GAP,
    }
    slacks.update({name + "_above_kappa": value - kappa for name, value in margins.items()})
    require(len(slacks) == 47 and len(margins) == 7, "slack census")
    return slacks


def witness(bit_lower, complex_lower, eta=ETA, beta=BETA):
    """Seven-step bootstrap and the 10^-18 floor used by the gauge44 outer witness."""
    common = min(bit_lower, (1 - beta) * complex_lower) - Fraction(1, 10**27)
    require(0 < common < bit_lower and common < (1 - beta) * complex_lower, "strict common saving")
    iterate = Fraction(384599, 10**10)
    for _ in range(7):
        previous = iterate
        iterate = (1 - common) * common + common * previous
        gap = min(common - iterate, 1 - iterate - common, 1 - iterate - common * (1 - previous), 1 - common)
        require(previous < iterate < common < 1 - iterate and gap > 0, "bootstrap gap")
    q = iterate * (1 - 2 * eta)
    margin = (1 - eta) * q / (1 + q)
    ticks = margin * 10**18
    kappa = Fraction((ticks.numerator - 1) // ticks.denominator, 10**18)
    return iterate, kappa


def nonpositive(slacks):
    return sorted(name for name, value in slacks.items() if value <= 0)


def bind(certificate, key, complex_key, kappa_key):
    bit_lower = Fraction(certificate["bit_lower"])
    complex_lower = Fraction(certificate[complex_key])
    iterate, kappa = witness(bit_lower, complex_lower)
    require(kappa == Fraction(certificate[kappa_key]), key + " kappa floor")
    expected = named_slacks(iterate, complex_lower, kappa, ETA, BETA)
    actual = {name: Fraction(value) for name, value in certificate[key].items()}
    require(set(actual) == set(expected), key + " names")
    require(all(actual[name] == expected[name] for name in expected), key + " values")
    require(all(value > 0 for value in actual.values()), key + " positivity")
    return iterate, kappa, actual


def main():
    frontier = FRONTIER.read_text()
    t16 = T16.read_text()
    require(FRONTIER_PREDICATE in frontier, "frontier predicate drifted")
    require(T16_PREDICATE in t16, "T16 predicate drifted")
    certificate = json.loads(ASSEMBLY.read_text())
    require(certificate["kappa"] == "836330098538459/500000000000000000", "selected kappa")
    _, kappa, native = bind(certificate, "outer", "complex_lower", "kappa")
    _, conservative, _ = bind(
        certificate, "conservative_outer", "conservative_complex_lower", "conservative_kappa"
    )
    require(certificate["controls"] == ["next_grid", "zero_eta", "zero_beta", "unit_beta"], "control names")

    bit_lower = Fraction(certificate["bit_lower"])
    complex_lower = Fraction(certificate["complex_lower"])
    iterate, _ = witness(bit_lower, complex_lower)
    rejected = []
    for name, mode in CONTROLS:
        if mode == "kappa_step":
            slacks = named_slacks(iterate, complex_lower, kappa + Fraction(1, 10**18), ETA, BETA)
        elif name == "zero_eta":
            slacks = named_slacks(iterate, complex_lower, kappa, Fraction(0), BETA)
        elif name == "zero_beta":
            slacks = named_slacks(iterate, complex_lower, kappa, ETA, Fraction(0))
        else:
            slacks = named_slacks(iterate, complex_lower, kappa, ETA, Fraction(1))
        failed = nonpositive(slacks)
        require(failed, "control stayed feasible: " + name)
        rejected.append(name)

    dummy = {f"dummy_{index}": Fraction(1) for index in range(47)}
    require(production_predicate(dummy), "dummy fixture should pass the receipt check")
    require(set(dummy) != set(native), "dummy fixture must not match the named slacks")
    swapped = dict(native)
    swapped["bit_positive"] = Fraction(1)
    require(swapped["bit_positive"] != native["bit_positive"], "swap must change a slack")
    require(production_predicate(swapped), "positive swap should pass the receipt check")
    zeroed = dict(native)
    zeroed["literal_scalar_guard"] = Fraction(0)
    require(not production_predicate(zeroed), "a zero slack must fail the receipt check")

    print(
        "PASS_SELECTED_OUTER_SLACK_AUDIT "
        f"native={kappa} conservative={conservative} "
        f"named=47 controls={','.join(rejected)} "
        "dummy_passes_receipt=1 swapped_positive_passes_receipt=1"
    )


if __name__ == "__main__":
    main()
