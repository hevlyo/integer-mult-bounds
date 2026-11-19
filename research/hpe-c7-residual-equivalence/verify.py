#!/usr/bin/env python3
"""Selected hyperplane residual C7 is a linear equivalence.

`factor_iff_pre` cancels a wrong pre-wrapper only when its residual is a
linear equivalence. The selected operator `C7` is defined as a linear map.
This checker proves, by exact Gaussian-rational arithmetic on all 128 basis
vectors, that the sign-flipped reverse of `fourierC 7` is a two-sided inverse.
It does not import the Lean development or `clifford_exact.py`.

Apache-2.0. The general gate-inverse theorems `gL_adj` and `cL_adjC` are
Jeremy Kothe's and are not reproved here.
"""
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXACT = ROOT / "research/hyperplane-end-lean/HyperplaneEnd/Exact.lean"
LABELS = ROOT / "research/hyperplane-end-lean/HyperplaneEnd/Labels.lean"
CLIFFORD = ROOT / "research/hyperplane-end-lean/HyperplaneEnd/Clifford.lean"
BINDING = ROOT / "scripts/verify_hpe_lean_binding.py"
PAIRS = ROOT / "research/hyperplane-end-lean/code/check_hpe_pairs.py"
N = 128
QUBITS = range(7)


class Reject(Exception):
    pass


def need(cond, message):
    if not cond:
        raise Reject(message)


class G:
    """Gaussian rational a + b i."""

    def __init__(self, real=0, imag=0):
        self.real = Fraction(real)
        self.imag = Fraction(imag)

    def __add__(self, other):
        return G(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other):
        return G(self.real - other.real, self.imag - other.imag)

    def __neg__(self):
        return G(-self.real, -self.imag)

    def __mul__(self, other):
        if isinstance(other, G):
            return G(
                self.real * other.real - self.imag * other.imag,
                self.real * other.imag + self.imag * other.real,
            )
        return G(self.real * other, self.imag * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return G(self.real / other, self.imag / other)

    def __eq__(self, other):
        return isinstance(other, G) and self.real == other.real and self.imag == other.imag

    def __repr__(self):
        return f"{self.real}+{self.imag}i"


ZERO = G(0)
ONE = G(1)


def coeff(sign):
    """Coefficients of `.cg q s` for s = true (sign +1) or false (sign -1).

    Lean `sg true = 1` and `sg false = -1`, and
    `((1 + sg s * I) * v(x) + (1 - sg s * I) * v(x XOR q)) / 2`.
    """
    need(sign in (1, -1), "sign")
    return (ONE + G(0, sign)) / 2, (ONE - G(0, sign)) / 2


def apply_gate(vector, qubit, sign):
    shift = 1 << qubit
    left, right = coeff(sign)
    return [left * vector[x] + right * vector[x ^ shift] for x in range(N)]


def apply_circuit(vector, circuit):
    for qubit, sign in circuit:
        vector = apply_gate(vector, qubit, sign)
    return vector


def basis(index):
    vector = [ZERO] * N
    vector[index] = ONE
    return vector


def forward():
    """`fourierC 7`: qubit 0 first, matching `cL` on a cons-list."""
    return [(qubit, 1) for qubit in QUBITS]


def reverse_adjoint():
    """`adjC (fourierC 7)`: sign flip, then reverse, so qubit 6 runs first."""
    return [(qubit, -1) for qubit in range(6, -1, -1)]


def same_order_adjoint():
    return [(qubit, -1) for qubit in QUBITS]


def is_identity(circuit, inverse):
    for index in range(N):
        vector = basis(index)
        if apply_circuit(apply_circuit(vector, circuit), inverse) != vector:
            return False
        if apply_circuit(apply_circuit(vector, inverse), circuit) != vector:
            return False
    return True


def folded_xor_involves(modulus, shift):
    """Lean `Gate.ok` for `.cg`: `((x XOR q) % N XOR q) % N = x` for every x."""
    return all((((x ^ shift) % modulus ^ shift) % modulus) == x for x in range(modulus))


def require_source_text():
    exact = EXACT.read_text()
    labels = LABELS.read_text()
    clifford = CLIFFORD.read_text()
    binding = BINDING.read_text()
    pairs = PAIRS.read_text()
    need(
        "noncomputable def C7 : A →ₗ[ℂ] A := cL 128 (fourierC 7)" in exact,
        "C7 is no longer the selected linear map",
    )
    need("C7 : A ≃ₗ" not in exact, "a C7 equivalence is already declared")
    need(
        "def fourierC (r : ℕ) : List Gate := (List.range r).map fun i => .cg (2 ^ i) true"
        in exact,
        "fourierC formula changed",
    )
    need("(C : A ≃ₗ[K] A)" in labels, "factor_iff_pre no longer requires an equivalence")
    need(
        "((1 + sg s * I) * v x + (1 - sg s * I) * v (fx N (x.val ^^^ q))) / 2" in clifford,
        "C-gate formula changed",
    )
    need("| .cg q s => .cg q (!s)" in clifford, "C-gate adjoint changed")
    need(
        "((x ^^^ q) % N ^^^ q) % N == x" in clifford,
        "Gate.ok involution test changed",
    )
    need("theorem cL_adjC" in clifford and "theorem gL_adj" in clifford,
         "inherited inverse theorems missing")
    need("C7" not in binding and "fourier" not in binding, "binding script now mentions C7")
    need("C7" not in pairs and "fourier" not in pairs, "instance checker now mentions C7")


def single_gate_coefficients():
    """One gate inverts by the sign flip, before any addressing check."""
    alpha, beta = coeff(1)
    need(coeff(-1) == (beta, alpha), "sign flip does not swap coefficients")
    need(2 * alpha * beta == ONE, "diagonal coefficient is not 1")
    need(alpha * alpha + beta * beta == ZERO, "cross term does not cancel")


def main():
    require_source_text()
    single_gate_coefficients()
    for qubit in QUBITS:
        shift = 1 << qubit
        need(shift < N, "qubit leaves the 7-qubit space")
        need(folded_xor_involves(N, shift), f"qubit {qubit} is not an involution on Z/128")
        need(all((x ^ shift) < N for x in range(N)), f"qubit {qubit} overflows 7 bits")
    need(not folded_xor_involves(6, 4), "non-involution control was accepted")
    need(is_identity(forward(), reverse_adjoint()), "reverse adjoint is not a two-sided inverse")
    need(is_identity(forward(), same_order_adjoint()),
         "same-order sign flip is not a two-sided inverse")
    need(not is_identity([(0, 1)], [(0, 1)]), "same-sign square was accepted")
    need(not is_identity(forward(), [(qubit, -1) for qubit in range(6, 0, -1)]),
         "inverse missing qubit 0 was accepted")
    image = apply_circuit(basis(0), forward())
    need(image != basis(0), "C7 fixes e_0, so the inverse check is vacuous")
    total = apply_circuit([basis(0)[i] + basis(1)[i] for i in range(N)], forward())
    separate = [apply_circuit(basis(0), forward())[i] + apply_circuit(basis(1), forward())[i]
                for i in range(N)]
    need(total == separate, "C7 failed the e_0 + e_1 linearity witness")
    witness = {"real": str(image[0].real), "imag": str(image[0].imag)}
    print(json.dumps({
        "status": "PASS_HPE_C7_RESIDUAL_EQUIVALENCE",
        "dimension": N,
        "qubits": 7,
        "basis_vectors": N,
        "two_sided": ["adjC reverse order", "sign flip in fourierC order"],
        "rejected": ["same-sign square of qubit 0", "adjoint missing qubit 0",
                     "folded XOR on Z/6 with shift 4"],
        "c7_e0_coordinate_0": witness,
        "lean_kernel": "not run",
    }, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Reject as exc:
        raise SystemExit("FAIL_HPE_C7_RESIDUAL_EQUIVALENCE: " + str(exc)) from exc
