#!/usr/bin/env python3
"""Finite discharge of the cold hyperplane-end operator hypotheses on F_2^9.

The statement is the one in HyperplaneEnd/Multi.lean: exact_cold assumes
T_E is the identity and T_U = L (C ⊗ id) R, and cold_hyperplane_width assumes
a frame of rank 8. PROOF.md records that the rank-8 case was checked locally
for all 511 hyperplanes and that the script was not shipped. This verifier
recomputes that finite instance. It does not import the predecessor Clifford
compiler, and it does not replay the three non-cold Lean pairs.

Operator equality is the packed probe from the hyperplane-end proof note.
Both circuits are applied to sum_x B^x |x> with the 1/2 of each C gate kept
in a common denominator. Matrix numerators produced by c such gates are
bounded by 4^c. Their difference is therefore strictly inside one digit of
base B = 2 * 4^(c+1), so equal packed images are equal operators, global
phase included.
"""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
EXACT = ROOT / "research/hyperplane-end-lean/HyperplaneEnd/Exact.lean"
MULTI = ROOT / "research/hyperplane-end-lean/HyperplaneEnd/Multi.lean"
N = 9
DIMENSION = 1 << N


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def parity(x):
    return x.bit_count() & 1


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = row
                break
            row ^= pivots[bit]
    return len(pivots)


def transpose(rows, n):
    return tuple(sum(((rows[j] >> i) & 1) << j for j in range(n)) for i in range(n))


def mv(rows, x):
    return sum(parity(row & x) << i for i, row in enumerate(rows))


def invert(rows, n):
    augmented = [row | (1 << (n + i)) for i, row in enumerate(rows)]
    for col in range(n):
        pivot = next(i for i in range(col, n) if (augmented[i] >> col) & 1)
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        for i in range(n):
            if i != col and (augmented[i] >> col) & 1:
                augmented[i] ^= augmented[col]
    require([row & ((1 << n) - 1) for row in augmented] == [1 << i for i in range(n)],
            "matrix inverse failed")
    return tuple(row >> n for row in augmented)


def basis_extend(columns, n):
    out = []
    for vector in list(columns) + [1 << i for i in range(n)]:
        if rank(out + [vector]) > len(out):
            out.append(vector)
    require(len(out) == n, "basis extension did not span")
    return tuple(out)


def nullspace(rows, n):
    work = list(rows)
    pivots = []
    height = 0
    for col in range(n):
        pivot = next((i for i in range(height, len(work)) if (work[i] >> col) & 1), None)
        if pivot is None:
            continue
        work[pivot], work[height] = work[height], work[pivot]
        for i in range(len(work)):
            if i != height and (work[i] >> col) & 1:
                work[i] ^= work[height]
        pivots.append(col)
        height += 1
    return tuple(
        (1 << col) | sum(((work[i] >> col) & 1) << pivot for i, pivot in enumerate(pivots))
        for col in range(n) if col not in pivots)


def pauli_mul(left, right):
    x, z, p = left
    y, w, q = right
    return x ^ y, z ^ w, (p + q + 2 * parity(z & y)) % 4


def identity_tableau(n):
    return tuple([(1 << i, 0, 0) for i in range(n)] + [(0, 1 << i, 0) for i in range(n)])


def apply_tableau(tableau, pauli):
    n = len(tableau) // 2
    x, z, phase = pauli
    out = (0, 0, phase)
    for i in range(n):
        if (x >> i) & 1:
            out = pauli_mul(out, tableau[i])
    for i in range(n):
        if (z >> i) & 1:
            out = pauli_mul(out, tableau[n + i])
    return out


def compose(second, first):
    return tuple(apply_tableau(second, pauli) for pauli in first)


def invert_tableau(tableau):
    n = len(tableau) // 2
    columns = [x | (z << n) for x, z, _phase in tableau]
    inverse_columns = transpose(invert(transpose(columns, 2 * n), 2 * n), 2 * n)
    identity = identity_tableau(n)
    out = []
    for j, word in enumerate(inverse_columns):
        x = word & ((1 << n) - 1)
        z = word >> n
        u, v, phase = apply_tableau(tableau, (x, z, 0))
        require((u, v) == identity[j][:2], "tableau inverse mismatch")
        out.append((x, z, (-phase) % 4))
    return tuple(out)


def quadratic_value(form, alpha, x, n):
    diagonal = sum(alpha[i] for i in range(n) if (x >> i) & 1)
    cross = sum(
        parity((form[i] >> (i + 1)) & (x >> (i + 1)))
        for i in range(n) if (x >> i) & 1)
    return (diagonal + 2 * cross) % 4


def mul_i(value, phase):
    real, imag = value
    return [(real, imag), (-imag, real), (-real, -imag), (imag, -real)][phase % 4]


class Op:
    def __init__(self, n, tableau, circuit):
        self.n = n
        self.tab = tableau
        self.circuit = circuit

    def then(self, later):
        require(self.n == later.n, "qubit mismatch")
        return Op(self.n, compose(later.tab, self.tab), self.circuit + later.circuit)

    def adjoint(self):
        reversed_gates = []
        for gate in reversed(self.circuit):
            kind = gate[0]
            if kind == "P":
                reversed_gates.append(("P", invert(gate[1], self.n)))
            elif kind == "D":
                reversed_gates.append(("D", gate[1], tuple((-entry) % 4 for entry in gate[2])))
            elif kind == "C":
                reversed_gates.append(("C", gate[1], -gate[2]))
            elif kind == "phase":
                reversed_gates.append(("phase", (-gate[1]) % 4))
            else:
                reversed_gates.append(gate)
        return Op(self.n, invert_tableau(self.tab), reversed_gates)


def ident(n):
    return Op(n, identity_tableau(n), [])


def perm(n, matrix):
    columns = transpose(matrix, n)
    inverse = invert(matrix, n)
    tableau = tuple([(column, 0, 0) for column in columns] + [(0, column, 0) for column in inverse])
    return Op(n, tableau, [("P", tuple(matrix))])


def diag(n, form, alpha=None):
    form = tuple(form)
    require(transpose(form, n) == form, "quadratic form is not symmetric")
    if alpha is None:
        alpha = tuple((form[i] >> i) & 1 for i in range(n))
    else:
        alpha = tuple(alpha)
    require(all(alpha[i] % 2 == (form[i] >> i) & 1 for i in range(n)), "diagonal phase mismatch")
    tableau = tuple([(1 << i, form[i], alpha[i]) for i in range(n)] + [(0, 1 << i, 0) for i in range(n)])
    return Op(n, tableau, [("D", form, alpha)])


def cgate(n, target, sign=1):
    tableau = tuple(
        [(1 << i, 0, 0) for i in range(n)]
        + [(target if (target >> i) & 1 else 0, 1 << i, (3 * sign) % 4 if (target >> i) & 1 else 0)
           for i in range(n)])
    return Op(n, tableau, [("C", target, sign)])


def xgate(n, shift):
    tableau = tuple(
        [(1 << i, 0, 0) for i in range(n)]
        + [(0, 1 << i, 2 * ((shift >> i) & 1)) for i in range(n)])
    return Op(n, tableau, [("X", shift)])


def fourier(n, axes):
    out = ident(n)
    for axis in axes:
        out = out.then(cgate(n, 1 << axis))
    return out


def canonical_frame(n, subspace):
    width = len(subspace)
    if width == 0:
        return ident(n)
    if width == n:
        return fourier(n, range(n))
    matrix = transpose(basis_extend(subspace, n), n)
    inverse_rows = transpose(invert(matrix, n), n)
    form = tuple(
        (1 << i) ^ sum(parity(row & other) << j for j, other in enumerate(inverse_rows))
        for i, row in enumerate(inverse_rows))
    change = perm(n, matrix).then(diag(n, form))
    return change.adjoint().then(fourier(n, range(width))).then(change)


def apply_circuit(n, circuit, state):
    size = 1 << n
    denominator = 0
    for gate in circuit:
        kind = gate[0]
        if kind == "P":
            moved = [(0, 0)] * size
            for x, amplitude in enumerate(state):
                moved[mv(gate[1], x)] = amplitude
            state = moved
        elif kind == "X":
            shift = gate[1]
            state = [state[x ^ shift] for x in range(size)]
        elif kind == "D":
            form, alpha = gate[1], gate[2]
            state = [mul_i(amplitude, quadratic_value(form, alpha, x, n))
                     for x, amplitude in enumerate(state)]
        elif kind == "phase":
            state = [mul_i(amplitude, gate[1]) for amplitude in state]
        elif kind == "C":
            target, sign = gate[1], gate[2]
            updated = [None] * size
            for x, (real, imag) in enumerate(state):
                other_real, other_imag = state[x ^ target]
                updated[x] = (
                    real - sign * imag + other_real + sign * other_imag,
                    imag + sign * real + other_imag - sign * other_real)
            state = updated
            denominator += 1
        else:
            raise AssertionError(kind)
    return state, denominator


def fully_reduce(state, denominator):
    while denominator and all((real & 1) == (imag & 1) == 0 for real, imag in state):
        state = [(real // 2, imag // 2) for real, imag in state]
        denominator -= 1
    return state, denominator


def packed_image(n, circuit):
    """Image of sum_x B^x |x> under the integer numerator of the circuit."""
    controlled = sum(gate[0] == "C" for gate in circuit)
    # Strict digit room: a difference of two 4^c-bounded numerators has absolute
    # value at most 2 * 4^c, and B/2 = 4^(c+1) is strictly larger.
    base = 2 * 4 ** (controlled + 1)
    require(4 * 4 ** controlled < base, "digit base is not strict")
    state = [(pow(base, x), 0) for x in range(1 << n)]
    image, denominator = apply_circuit(n, circuit, state)
    require(denominator == controlled, "controlled-phase count drifted")
    return image


def circuits_agree(n, left, right):
    if sum(gate[0] == "C" for gate in left) != sum(gate[0] == "C" for gate in right):
        return False
    return packed_image(n, left) == packed_image(n, right)


def monomial(op):
    n = op.n
    tableau = op.tab
    require(all(x == 0 and phase % 2 == 0 for x, _z, phase in tableau[n:]),
            "operator is not a monomial")
    matrix = transpose([x for x, _z, _phase in tableau[:n]], n)
    offset = mv(matrix, sum((phase // 2) << i for i, (_x, _z, phase) in enumerate(tableau[n:])))
    columns = [mv(transpose(matrix, n), z) for _x, z, _phase in tableau[:n]]
    form = transpose(columns, n)
    alpha = [(phase - 2 * parity(offset & z)) % 4 for _x, z, phase in tableau[:n]]
    extracted = diag(n, form, alpha).then(perm(n, matrix)).then(xgate(n, offset))
    require(extracted.tab == tableau, "monomial tableau mismatch")
    vacuum = [(1, 0)] + [(0, 0)] * ((1 << n) - 1)
    state, denominator = fully_reduce(*apply_circuit(n, op.circuit, vacuum))
    require(denominator == 0, "monomial vacuum has a residual denominator")
    require(all(amplitude == (0, 0) for i, amplitude in enumerate(state) if i != offset),
            "monomial vacuum is not a phase times one basis vector")
    phase = [(1, 0), (0, 1), (-1, 0), (0, -1)].index(state[offset])
    extracted = extracted.then(Op(n, identity_tableau(n), [("phase", phase)]))
    record = {
        "matrix_rows": list(matrix),
        "offset": offset,
        "quadratic_rows": list(form),
        "linear_Z4": list(alpha),
        "phase": phase,
    }
    return extracted, record


def factor_operator(op):
    n = op.n
    z_block = [x for x, _z, _phase in op.tab[n:]]
    width = rank(z_block)
    if width == 0:
        extracted, record = monomial(op)
        return {"rank": 0, "left": record, "right": None}, extracted, None, extracted
    matrix = transpose(basis_extend(z_block, n), n)
    permutation = perm(n, invert(matrix, n))
    moved = op.then(permutation)
    moved_z = [x for x, _z, _phase in moved.tab[n:]]
    moved_x = [z for _x, z, _phase in moved.tab[n:]]
    picks = []
    selected = []
    for index, vector in enumerate(moved_z):
        if rank(selected + [vector]) > len(selected):
            picks.append(index)
            selected.append(vector)
    require(len(picks) == width and all(vector >> width == 0 for vector in moved_z),
            "residual support is not the first qubits")
    small = transpose(selected, width)
    small_inverse = invert(small, width)
    residual_form_rows = transpose([moved_x[index] & ((1 << width) - 1) for index in picks], width)
    small_form = tuple(
        sum(parity(row & column) << j for j, column in enumerate(transpose(small_inverse, width)))
        for row in residual_form_rows)
    quadratic = diag(n, small_form + (0,) * (n - width))
    axes = range(width)
    phase_form = tuple(1 << i if i < width else 0 for i in range(n))
    hadamard = diag(n, phase_form).then(fourier(n, axes)).then(diag(n, phase_form))
    cleared = moved.then(quadratic).then(hadamard)
    require(all(x == 0 for x, _z, _phase in cleared.tab[n:]), "residual Z block did not clear")
    cleared_monomial, _record = monomial(cleared)
    spectator = diag(n, phase_form)
    left = spectator.adjoint().then(quadratic.adjoint()).then(permutation.adjoint())
    right = cleared_monomial.then(spectator.adjoint()).then(xgate(n, (1 << width) - 1))
    left_op, left_record = monomial(left)
    right_op, right_record = monomial(right)
    compiled = right_op.then(fourier(n, axes)).then(left_op)
    require(compiled.tab == op.tab, "factored tableau differs")
    return {"rank": width, "left": left_record, "right": right_record}, compiled, right_op, left_op


def lean_entrances():
    text = EXACT.read_text()
    entrances = []
    for index in (1, 2, 3):
        match = re.search(r"def pair%d : Pair := ⟨(\[[0-9]+\])," % index, text)
        require(match is not None, "missing Lean pair entrance")
        entrances.append(ast_list(match.group(1)))
    require(len(entrances) == 3 and len({tuple(item) for item in entrances}) == 3,
            "Lean entrances are not three distinct frames")
    return entrances


def ast_list(text):
    value = json.loads(text)
    require(isinstance(value, list) and all(isinstance(item, int) for item in value),
            "Lean frame is not an integer list")
    return value


def bind_statements():
    multi = MULTI.read_text()
    require("theorem exact_cold" in multi, "exact_cold is not the named Multi.lean theorem")
    require("theorem cold_hyperplane_width" in multi, "cold_hyperplane_width is missing")
    require("frameRank U = 8" in multi, "cold width hypothesis is missing")
    require("(T E).symm v = v" in multi, "cold identity hypothesis is missing")
    entrances = lean_entrances()
    for entrance in entrances:
        require(rank(entrance) == 1, "a certified non-cold entrance does not have rank 1")
    return entrances


def census():
    rows = []
    samples = {}
    for functional in range(1, DIMENSION):
        basis = nullspace([functional], N)
        require(len(basis) == 8 and rank(basis) == 8, "kernel is not a hyperplane")
        require(all(parity(functional & vector) == 0 for vector in basis), "kernel vector misses the functional")
        outside = 1 << (functional.bit_length() - 1)
        require(parity(functional & outside) == 1 and rank(basis + (outside,)) == 9,
                "kernel is not a hyperplane")
        operator = canonical_frame(N, basis)
        record, compiled, right, left = factor_operator(operator)
        require(record["rank"] == 8 and record["right"] is not None, "factorization rank is not 8")
        require(circuits_agree(N, operator.circuit, compiled.circuit),
                "packed images differ for functional %d" % functional)
        require(sum(gate[0] == "C" for gate in operator.circuit) == 8, "cold frame does not have width 8")
        require(N - record["rank"] == 1, "a rank-8 cold frame does not have one spectator")
        rows.append({
            "functional": functional,
            "basis": list(basis),
            "left": record["left"],
            "right": record["right"],
        })
        if functional in (1, 256, 511):
            samples[str(functional)] = {
                "basis": list(basis),
                "right_offset": record["right"]["offset"],
                "right_phase": record["right"]["phase"],
                "left_phase": record["left"]["phase"],
            }
        if functional == 1:
            require(not circuits_agree(N, operator.circuit, compiled.circuit + [("phase", 1)]),
                    "a global-phase mutant was accepted")
            deleted = False
            trimmed = []
            for gate in compiled.circuit:
                if gate[0] == "C" and not deleted:
                    deleted = True
                    continue
                trimmed.append(gate)
            require(deleted and not circuits_agree(N, operator.circuit, trimmed),
                    "a deleted C gate was accepted")
            swapped = left.then(fourier(N, range(8))).then(right)
            require(not circuits_agree(N, operator.circuit, swapped.circuit),
                    "swapped monomials were accepted")
            require(not circuits_agree(N, operator.circuit, []),
                    "the identity circuit was accepted for a hyperplane")
    empty = canonical_frame(N, ())
    require(empty.circuit == [], "the empty frame is not the empty circuit")
    probe = [(1, 0) for _ in range(DIMENSION)]
    image, denominator = apply_circuit(N, empty.circuit, probe)
    require(denominator == 0 and image == probe, "the empty frame moves the standard probe")
    require(not circuits_agree(N, empty.circuit, xgate(N, 1).circuit),
            "a translation of the identity was accepted")
    full = nullspace([0], N)
    require(rank(full) == 9, "the zero functional is not the full space")
    encoded = json.dumps(rows, separators=(",", ":"), sort_keys=True).encode()
    return {
        "hyperplanes": len(rows),
        "digest_sha256": hashlib.sha256(encoded).hexdigest(),
        "samples": samples,
    }


def main():
    entrances = bind_statements()
    result = census()
    report = {
        "status": "PASS_COLD_HYPERPLANE_FACTOR_CENSUS",
        "proposition": (
            "For every nonzero linear functional on F_2^9, the canonical cold frame "
            "of its kernel equals the extracted monomial factorization "
            "L then Fourier on qubits 0..7 then R, as operators on C^512, global phase "
            "included. The empty frame is the identity. Each such kernel has rank 8, "
            "residual width 8 and one spectator, and is not the full space."
        ),
        "n": N,
        "hyperplanes": result["hyperplanes"],
        "residual_width": 8,
        "spectators": 1,
        "digest_sha256": result["digest_sha256"],
        "samples": result["samples"],
        "lean_entrances_rank": [rank(entrance) for entrance in entrances],
        "controls_rejected": [
            "global_phase",
            "deleted_C_gate",
            "swapped_monomials",
            "identity_circuit",
            "identity_translation",
        ],
        "not_discharged": [
            "Lean kernel acceptance of this census",
            "the three non-cold pair1-pair3 factorizations",
            "unit rows, wrapper recipes on an emitted word, footprints and hosting",
            "selected kappa",
        ],
    }
    require(report["hyperplanes"] == 511, "hyperplane count")
    require(report["lean_entrances_rank"] == [1, 1, 1], "non-cold entrances entered the census")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    main()
