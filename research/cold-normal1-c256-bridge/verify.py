#!/usr/bin/env python3
"""Exact normal-1 cold chart: T_U = L (C8 tensor id) R on C^256 tensor C^2.

The identity is decided by an independent Gaussian gate interpreter. The pinned
compiler is used only to name the ordered circuit and monomials, not as the
equality oracle. Standard library only. Apache-2.0.
"""
import importlib.util
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
N = 9
DIM = 1 << N
U_BASIS = (2, 4, 8, 16, 32, 64, 128, 256)
ZERO_Q = (0, 0, 0, 0, 0, 0, 0, 0, 0)
LEFT = {
    "matrix_rows": (256, 1, 2, 4, 8, 16, 32, 64, 128),
    "offset": 0,
    "quadratic_rows": ZERO_Q,
    "linear_Z4": (2, 2, 2, 2, 2, 2, 2, 2, 0),
    "phase": 0,
}
RIGHT = {
    "matrix_rows": (2, 4, 8, 16, 32, 64, 128, 256, 1),
    "offset": 255,
    "quadratic_rows": ZERO_Q,
    "linear_Z4": (0, 2, 2, 2, 2, 2, 2, 2, 2),
    "phase": 0,
}


def parity(x):
    return x.bit_count() & 1


def rank(rows):
    pivots = {}
    for value in rows:
        x = value
        while x:
            bit = x.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = x
                break
            x ^= pivots[bit]
    return len(pivots)


def transpose(rows, n):
    return tuple(sum(((rows[j] >> i) & 1) << j for j in range(n)) for i in range(n))


def mv(rows, x):
    return sum(parity(row & x) << i for i, row in enumerate(rows))


def inv(rows, n):
    augmented = [row | (1 << (n + i)) for i, row in enumerate(rows)]
    for col in range(n):
        pivot = next(i for i in range(col, n) if (augmented[i] >> col) & 1)
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        for i in range(n):
            if i != col and (augmented[i] >> col) & 1:
                augmented[i] ^= augmented[col]
    assert [row & ((1 << n) - 1) for row in augmented] == [1 << i for i in range(n)]
    return tuple(row >> n for row in augmented)


def basis_extend(cols, n):
    out = []
    for x in list(cols) + [1 << i for i in range(n)]:
        if rank(out + [x]) > len(out):
            out.append(x)
    assert len(out) == n
    return tuple(out)


def canonical_circuit(n, frame):
    """Gate list of canonical_frame, definition-following and tableau-free."""
    width = len(frame)
    if width == 0:
        return []
    if width == n:
        return [("C", 1 << i, 1) for i in range(n)]
    matrix = transpose(basis_extend(frame, n), n)
    inverse = inv(matrix, n)
    dual = transpose(inverse, n)
    quadratic = tuple(
        (1 << i) ^ sum(parity(dual[i] & dual[j]) << j for j in range(n))
        for i in range(n)
    )
    alpha = tuple((quadratic[i] >> i) & 1 for i in range(n))
    fourier = [("C", 1 << i, 1) for i in range(width)]
    return [
        ("D", quadratic, tuple((-a) % 4 for a in alpha)),
        ("P", inverse),
        *fourier,
        ("P", matrix),
        ("D", quadratic, alpha),
    ]


def rho(x):
    return ((x >> 1) & 255) | ((x & 1) << 8)


def rho_inv(x):
    low = x & 255
    spectator = (x >> 8) & 1
    return spectator | (low << 1)


def q_diagonal(alpha, x):
    return sum(alpha[i] for i in range(N) if (x >> i) & 1) % 4


def mul_i(real, imag, power):
    power %= 4
    if power == 0:
        return real, imag
    if power == 1:
        return -imag, real
    if power == 2:
        return -real, -imag
    return imag, -real


def gauss(real, imag):
    return (real, imag)


def zero_vec():
    return [gauss(Fraction(0), Fraction(0)) for _ in range(DIM)]


def basis_vec(index):
    vec = zero_vec()
    vec[index] = gauss(Fraction(1), Fraction(0))
    return vec


def apply_gate(vec, gate):
    kind = gate[0]
    if kind == "P":
        out = [None] * DIM
        for x, amp in enumerate(vec):
            out[mv(gate[1], x)] = amp
        if any(amp is None for amp in out):
            raise AssertionError("permutation is not total")
        return out
    if kind == "X":
        offset = gate[1]
        return [vec[x ^ offset] for x in range(DIM)]
    if kind == "phase":
        return [gauss(*mul_i(real, imag, gate[1])) for real, imag in vec]
    if kind == "D":
        quadratic, alpha = gate[1], gate[2]
        if quadratic != ZERO_Q:
            raise AssertionError("this chart's diagonal is identically zero")
        out = []
        for x, (real, imag) in enumerate(vec):
            out.append(gauss(*mul_i(real, imag, q_diagonal(alpha, x))))
        return out
    if kind == "C":
        qubit, sign = gate[1], gate[2]
        out = []
        for x, (real, imag) in enumerate(vec):
            other_real, other_imag = vec[x ^ qubit]
            if sign == 1:
                next_real = real - imag + other_real + other_imag
                next_imag = real + imag - other_real + other_imag
            elif sign == -1:
                next_real = real + imag + other_real - other_imag
                next_imag = -real + imag + other_real + other_imag
            else:
                raise AssertionError(sign)
            out.append(gauss(next_real / 2, next_imag / 2))
        return out
    raise AssertionError(kind)


def apply_circuit(vec, gates):
    for gate in gates:
        vec = apply_gate(vec, gate)
    return vec


def mono_gates(record):
    return [
        ("D", record["quadratic_rows"], record["linear_Z4"]),
        ("P", record["matrix_rows"]),
        ("X", record["offset"]),
        ("phase", record["phase"]),
    ]


def c8_closed(target, source):
    """Product of eight disjoint sign-+1 C gates, denominator 256."""
    distance = (target ^ source).bit_count()
    real, imag = mul_i(16, 0, (3 * distance) % 4)
    return gauss(Fraction(real, 256), Fraction(imag, 256))


def load_compiler():
    path = ROOT / "research/split-centres-global/vendor/clifford_exact.py"
    spec = importlib.util.spec_from_file_location("pinned_clifford_exact", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_record(record):
    return {
        "matrix_rows": tuple(record["matrix_rows"]),
        "offset": record["offset"],
        "quadratic_rows": tuple(record["quadratic_rows"]),
        "linear_Z4": tuple(record["linear_Z4"]),
        "phase": record["phase"],
    }


def vectors_equal(left, right):
    return all(a == b for a, b in zip(left, right, strict=True))


def column_image(gates, index):
    return apply_circuit(basis_vec(index), gates)


def composed_column(left, right, c_gates, index):
    after_right = apply_circuit(basis_vec(index), mono_gates(right))
    after_c = apply_circuit(after_right, c_gates)
    return apply_circuit(after_c, mono_gates(left))


def assert_width():
    if rank(U_BASIS) != 8:
        raise AssertionError("normal-1 basis is not rank 8")
    if any(vector & 1 for vector in U_BASIS):
        raise AssertionError("basis vector meets the transverse bit")
    if rank(U_BASIS + (1,)) != 9:
        raise AssertionError("transverse bit does not complete the space")
    if basis_extend(U_BASIS, N) != U_BASIS + (1,):
        raise AssertionError("ordered basis extension drifted")


def assert_permutations():
    forward, inverse = RIGHT["matrix_rows"], LEFT["matrix_rows"]
    for x in range(DIM):
        if mv(forward, x) != rho(x) or mv(inverse, x) != rho_inv(x):
            raise AssertionError(("permutation", x))
        if rho_inv(rho(x)) != x or rho(rho_inv(x)) != x:
            raise AssertionError(("rotation", x))


def assert_algebraic_steps():
    real, imag = 1, 0
    for _ in range(8):
        # (1+i) * (real + i imag) = (real - imag) + i(real + imag)
        real, imag = real - imag, real + imag
    if (real, imag) != (16, 0):
        raise AssertionError("(1+i)^8")
    # (1-i)/(1+i) = -i. Cross-multiply: (1-i) = -i(1+i) = 1 - i.
    if (1 - 1j) != (-1j) * (1 + 1j):
        raise AssertionError("(1-i)/(1+i)")
    for distance in range(9):
        left = mul_i(1, 0, (3 * (8 - distance)) % 4)  # (-i)^(8-d)
        right = mul_i(1, 0, distance % 4)  # i^d
        if left != right:
            raise AssertionError(("phase reduction", distance))
    for y in range(256):
        for z in range(256):
            if (y.bit_count() + z.bit_count() + (y ^ z).bit_count()) % 2:
                raise AssertionError(("weight parity", y, z))


def assert_closed_form(c_gates):
    for source in range(256):
        image = column_image(c_gates, source)
        for target, amp in enumerate(image):
            if target >= 256:
                if amp != gauss(Fraction(0), Fraction(0)):
                    raise AssertionError("C8 leaked into the spectator")
            elif amp != c8_closed(target, source):
                raise AssertionError(("closed form", source, target))
        spectator = column_image(c_gates, source | 256)
        for target, amp in enumerate(spectator):
            if target < 256:
                if amp != gauss(Fraction(0), Fraction(0)):
                    raise AssertionError("spectator input leaked downward")
            elif amp != c8_closed(target ^ 256, source):
                raise AssertionError(("spectator closed form", source, target))


def assert_identity(circuit, c_gates):
    for index in range(DIM):
        direct = column_image(circuit, index)
        wrapped = composed_column(LEFT, RIGHT, c_gates, index)
        if not vectors_equal(direct, wrapped):
            raise AssertionError(("column", index))
    superposed = apply_circuit(
        [gauss(Fraction(1), Fraction(0)), gauss(Fraction(1), Fraction(0))] + zero_vec()[2:],
        circuit,
    )
    total = [
        gauss(a + c, b + d)
        for (a, b), (c, d) in zip(column_image(circuit, 0), column_image(circuit, 1), strict=True)
    ]
    if not vectors_equal(superposed, total):
        raise AssertionError("interpreter is not additive on e0+e1")


def assert_monomial_action():
    for record in (LEFT, RIGHT):
        gates = mono_gates(record)
        for index in range(DIM):
            image = column_image(gates, index)
            phase = (q_diagonal(record["linear_Z4"], index) + record["phase"]) % 4
            destination = mv(record["matrix_rows"], index) ^ record["offset"]
            expected = zero_vec()
            expected[destination] = gauss(*mul_i(Fraction(1), Fraction(0), phase))
            if not vectors_equal(image, expected):
                raise AssertionError(("monomial", destination))


def assert_coordinate_formula(circuit, c_gates):
    """T leaves bit 0 fixed and Fouriers bits 1..8."""
    for index in range(DIM):
        spectator = index & 1
        high = (index >> 1) & 255
        image = column_image(circuit, index)
        for target, amp in enumerate(image):
            if (target & 1) != spectator:
                if amp != gauss(Fraction(0), Fraction(0)):
                    raise AssertionError("transverse bit moved")
                continue
            source_byte = (target >> 1) & 255
            if amp != c8_closed(source_byte, high):
                raise AssertionError(("transverse formula", index, target))
    del c_gates


def assert_mutations(circuit, c_gates):
    accepted = []

    def require_reject(name, left, right, gates):
        same = all(
            vectors_equal(column_image(circuit, index), composed_column(left, right, gates, index))
            for index in (0, 1, 255, 256, 511)
        )
        if same:
            raise AssertionError("mutated chart accepted: " + name)
        accepted.append(name)

    phased = dict(LEFT)
    phased["phase"] = 1
    require_reject("left global phase", phased, RIGHT, c_gates)

    shifted = dict(RIGHT)
    shifted["offset"] = RIGHT["offset"] ^ 256
    require_reject("right spectator translation", LEFT, shifted, c_gates)

    flipped = [("C", 1, -1 if qubit == 1 else 1) for _, qubit, _ in c_gates]
    require_reject("reversed C direction", LEFT, RIGHT, flipped)

    spectator_c = [("C", 1 << i, 1) for i in range(7)] + [("C", 256, 1)]
    require_reject("C on the spectator", LEFT, RIGHT, spectator_c)

    omitted = c_gates[:-1]
    require_reject("omitted C gate", LEFT, RIGHT, omitted)
    if accepted != [
        "left global phase",
        "right spectator translation",
        "reversed C direction",
        "C on the spectator",
        "omitted C gate",
    ]:
        raise AssertionError(accepted)


def assert_source_binding(circuit):
    lean = (ROOT / "research/hyperplane-end-lean/HyperplaneEnd/Multi.lean").read_text()
    for fragment in (
        "theorem exact_cold",
        "(hE : ∀ v, (T E).symm v = v)",
        "(hU : ∀ v, T U v = L (C.rTensor B (R v)))",
        "theorem cold_hyperplane_width",
        "frameRank U - frameRank ⊥ = 8",
        "9 - (frameRank U - frameRank ⊥) = 1",
    ):
        if fragment not in lean:
            raise AssertionError("Lean hypothesis drifted: " + fragment)
    compiler = load_compiler()
    if list(compiler.canonical_frame(N, ()).circuit) != []:
        raise AssertionError("empty entrance is not the identity circuit")
    vendor_circuit = list(compiler.canonical_frame(N, U_BASIS).circuit)
    if vendor_circuit != circuit:
        raise AssertionError("local canonical circuit differs from the pinned compiler")
    record, _compiled = compiler.lower_child(compiler.canonical_frame(N, U_BASIS))
    if record["rank"] != 8:
        raise AssertionError(record["rank"])
    if normalize_record(record["left"]) != LEFT or normalize_record(record["right"]) != RIGHT:
        raise AssertionError("pinned monomials differ from the stated chart")


def main():
    assert_width()
    assert_permutations()
    assert_algebraic_steps()
    circuit = canonical_circuit(N, U_BASIS)
    c_gates = [("C", 1 << i, 1) for i in range(8)]
    if [gate for gate in circuit if gate[0] == "C"] != c_gates:
        raise AssertionError("Fourier support is not qubits 0..7")
    assert_source_binding(circuit)
    assert_closed_form(c_gates)
    assert_monomial_action()
    assert_coordinate_formula(circuit, c_gates)
    assert_identity(circuit, c_gates)
    assert_mutations(circuit, c_gates)
    print(
        "PASS_COLD_NORMAL1_C256_BRIDGE columns=512 full_operator_checks=2 "
        "controls=5 rank=8 spectators=1 global_phase no_lean no_new_kappa"
    )


if __name__ == "__main__":
    main()
