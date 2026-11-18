#!/usr/bin/env python3
"""Exact four-address floor in the elementary abelian group of order 8.

The proof is in README.md. This program checks its finite content and the
explicit words. It does not import predecessor packages.
"""

from itertools import combinations

NONZERO = tuple(range(1, 8))


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def popcount(value):
    return bin(value).count("1")


def rank_bits(rows):
    """Rank of 4-bit row vectors over F2."""
    span = []
    for row in rows:
        value = row
        for pivot in span:
            if value & -value == pivot & -pivot:
                value ^= pivot
        if value:
            span.append(value)
            span.sort(key=lambda item: item & -item)
    return len(span)


def convolution(left, right):
    out = 0
    for i in range(8):
        if (left >> i) & 1:
            for j in range(8):
                if (right >> j) & 1:
                    out ^= 1 << (i ^ j)
    return out


def set_convolution(left, right):
    return frozenset(i ^ j for i in left for j in right)


class MaskAlgebra:
    @staticmethod
    def zero():
        return 0

    @staticmethod
    def one():
        return 1  # group identity, vector 0

    @staticmethod
    def basis(vector):
        return 1 << vector

    @staticmethod
    def mul(left, right):
        return convolution(left, right)

    @staticmethod
    def add(left, right):
        return left ^ right


class SetAlgebra:
    @staticmethod
    def zero():
        return frozenset()

    @staticmethod
    def one():
        return frozenset({0})

    @staticmethod
    def basis(vector):
        return frozenset({vector})

    @staticmethod
    def mul(left, right):
        return set_convolution(left, right)

    @staticmethod
    def add(left, right):
        return left.symmetric_difference(right)


class IntAlgebra:
    """Nonnegative integer coefficients. Used to see that the direct words
    do not cancel, so the same words are valid over every field."""

    @staticmethod
    def zero():
        return (0, 0, 0, 0, 0, 0, 0, 0)

    @staticmethod
    def one():
        return (1, 0, 0, 0, 0, 0, 0, 0)

    @staticmethod
    def basis(vector):
        values = [0] * 8
        values[vector] = 1
        return tuple(values)

    @staticmethod
    def mul(left, right):
        out = [0] * 8
        for i, coeff in enumerate(left):
            if not coeff:
                continue
            for j, other in enumerate(right):
                if other:
                    out[i ^ j] += coeff * other
        return tuple(out)

    @staticmethod
    def add(left, right):
        return tuple(a + b for a, b in zip(left, right))


def eye(algebra, size=4):
    zero = algebra.zero()
    return tuple(
        tuple(algebra.one() if i == j else zero for j in range(size))
        for i in range(size)
    )


def matmul(algebra, left, right):
    size = len(left)
    zero = algebra.zero()
    out = []
    for i in range(size):
        row = []
        for j in range(size):
            acc = zero
            for k in range(size):
                acc = algebra.add(acc, algebra.mul(left[i][k], right[k][j]))
            row.append(acc)
        out.append(tuple(row))
    return tuple(out)


def gate(algebra, projector, label):
    """D(N, label) = (I-N)[0] + N[label] for a diagonal 0-1 projector."""
    size = len(projector)
    one = algebra.one()
    step = algebra.basis(label)
    zero = algebra.zero()
    rows = []
    for i in range(size):
        row = []
        for j in range(size):
            if i != j:
                row.append(zero)
            elif projector[i]:
                row.append(step)
            else:
                row.append(one)
        rows.append(tuple(row))
    return tuple(rows)


def target_matrix(algebra, labels):
    size = len(labels)
    one = algebra.one()
    zero = algebra.zero()
    return tuple(
        tuple(algebra.basis(labels[i]) if i == j else zero for j in range(size))
        for i in range(size)
    )


def word_for(algebra, projectors, labels):
    acc = eye(algebra)
    for projector, label in zip(projectors, labels):
        acc = matmul(algebra, acc, gate(algebra, projector, label))
    return acc


def bits_of(vector):
    return ((vector >> 0) & 1, (vector >> 1) & 1, (vector >> 2) & 1)


def projectors_for(labels):
    columns = list(zip(*(bits_of(label) for label in labels)))
    return tuple(columns)


def weight(vector):
    return popcount(vector)


def all_idempotent_rank_one():
    found = []
    for mask in range(1 << 16):
        rows = [(mask >> (4 * i)) & 15 for i in range(4)]
        product = [0, 0, 0, 0]
        for i, row in enumerate(rows):
            for j in range(4):
                if (row >> j) & 1:
                    product[i] ^= rows[j]
        if product == rows and rank_bits(rows) == 1:
            found.append(tuple(rows))
    return found


def outer_factorization_count():
    count = 0
    seen = set()
    for x in range(1, 16):
        for y in range(16):
            if bin(x & y).count("1") % 2 != 1:
                continue
            rows = tuple(((x >> i) & 1) * y for i in range(4))
            seen.add(rows)
            count += 1
    return count, len(seen)


def main():
    quadruples = list(combinations(NONZERO, 4))
    require(len(quadruples) == 35, "expected C(7,4)=35 quadruples")
    algebras = (MaskAlgebra, SetAlgebra, IntAlgebra)
    omitted = 0
    cleared = 0
    min_weight = 99
    max_weight = 0

    for labels in quadruples:
        # At most three weight-1 vectors exist in any basis of F2^3, and
        # every nonzero vector has weight at least 1, so four of them weigh
        # at least 5 in every basis. Checked here on the standard basis and
        # on every image under GL3 by recomputing weights after all ordered
        # bases below.
        standard_weight = sum(weight(label) for label in labels)
        min_weight = min(min_weight, standard_weight)
        max_weight = max(max_weight, standard_weight)
        require(standard_weight >= 5, "standard weight dropped below 5")
        projectors = projectors_for(labels)
        ranks = tuple(sum(column) for column in projectors)
        require(sum(ranks) == standard_weight, "rank sum is the Hamming weight")
        require(max(ranks) >= 2 and min(ranks) >= 1, "a basis word is uneven and uses all three labels")
        for algebra in algebras:
            built = word_for(algebra, projectors, (1, 2, 4))
            require(built == target_matrix(algebra, labels), "unit-gate basis word missed its target")
        # Direct rank-one word: gate i multiplies register i by labels[i].
        for algebra in algebras:
            acc = eye(algebra)
            for index, label in enumerate(labels):
                projector = tuple(1 if i == index else 0 for i in range(4))
                acc = matmul(algebra, acc, gate(algebra, projector, label))
            require(acc == target_matrix(algebra, labels), "direct rank-one word missed its target")
        # Omitting any one basis gate misses the target.
        for drop in range(3):
            kept = [(projectors[j], (1, 2, 4)[j]) for j in range(3) if j != drop]
            missed = word_for(MaskAlgebra, [item[0] for item in kept], [item[1] for item in kept])
            require(missed != target_matrix(MaskAlgebra, labels), "omitted gate still hit the target")
            omitted += 1
        # Clearing any single 1 in a projector misses the target.
        for column, bit_row in enumerate(projectors):
            for row, bit in enumerate(bit_row):
                if not bit:
                    continue
                damaged = [list(col) for col in projectors]
                damaged[column][row] = 0
                missed = word_for(MaskAlgebra, damaged, (1, 2, 4))
                require(missed != target_matrix(MaskAlgebra, labels), "cleared bit still hit the target")
                cleared += 1

    # Every ordered basis: four distinct nonzero vectors still weigh at least 5.
    bases = 0
    for first, second, third in ((a, b, c) for a in NONZERO for b in NONZERO for c in NONZERO):
        if rank_bits((first, second, third)) < 3:
            continue
        bases += 1
        # Express every nonzero vector in this basis and weigh each quadruple
        # by summing those coordinates. The change-of-basis matrix sends the
        # standard basis to (first, second, third).
        decode = {}
        for mask in range(8):
            image = 0
            for shift, vector in enumerate((first, second, third)):
                if (mask >> shift) & 1:
                    image ^= vector
            decode[image] = mask
        require(len(decode) == 8, "basis did not enumerate the group")
        for labels in quadruples:
            total = sum(weight(decode[label]) for label in labels)
            require(total >= 5, "some basis gives four addresses total weight below 5")
    require(bases == 168, "GL3(F2) has 168 ordered bases")

    # Every ordered label triple: dependent labels cover at most 3 nonzero
    # addresses; independent labels are a basis.
    dependent_cover = 0
    independent = 0
    for labels in ((a, b, c) for a in range(8) for b in range(8) for c in range(8)):
        generated = {0}
        for mask in range(8):
            acc = 0
            for shift, label in enumerate(labels):
                if (mask >> shift) & 1:
                    acc ^= label
            generated.add(acc)
        nonzero = generated - {0}
        if rank_bits(labels) < 3:
            require(len(nonzero) <= 3, "dependent triple covered four addresses")
            dependent_cover += 1
        else:
            require(len(nonzero) == 7, "independent triple missed an address")
            independent += 1
    require(dependent_cover + independent == 512, "label triple census incomplete")

    idempotents = all_idempotent_rank_one()
    factorizations, distinct = outer_factorization_count()
    require(len(idempotents) == 120, "F2 rank-one idempotent count")
    require(distinct == 120 and factorizations == 120, "outer-product parametrization missed an idempotent")
    for rows in idempotents:
        require(rank_bits(rows) == 1, "census rank drifted")

    # Three-label control: {1,2,3} = {e1, e2, e1+e2} has a two-gate unit word
    # and is not realized by one gate. This is the predecessor shape inside
    # this group, checked directly rather than imported.
    triple = (1, 2, 3)
    acc = eye(MaskAlgebra, 3)
    acc = matmul(MaskAlgebra, acc, gate(MaskAlgebra, (1, 0, 1), 1))
    acc = matmul(MaskAlgebra, acc, gate(MaskAlgebra, (0, 1, 1), 2))
    expected = target_matrix(MaskAlgebra, triple)
    # target_matrix uses len(labels); good.
    require(acc == expected, "two-gate triple control failed")
    one = gate(MaskAlgebra, (1, 1, 1), 1)
    require(one != expected, "one gate must not realize three distinct addresses")
    # No single rank-one diagonal pattern realizes the triple: every diagonal
    # rank-one gate writes one label on one register.
    for index in range(3):
        projector = tuple(1 if i == index else 0 for i in range(3))
        for label in NONZERO:
            require(gate(MaskAlgebra, projector, label) != expected, "rank-one gate realized the triple")

    # Integer-coefficient witness that a representative quadruple has
    # coefficient 1 on the target address and 0 elsewhere, with no carries.
    sample = (1, 2, 4, 7)
    built = word_for(IntAlgebra, projectors_for(sample), (1, 2, 4))
    for i, label in enumerate(sample):
        for j in range(4):
            coeffs = built[i][j]
            require(all(coeff in (0, 1) for coeff in coeffs), "construction used a nontrivial integer coefficient")
            require(sum(coeffs) == (1 if i == j else 0), "integer support is not a pure address")
            if i == j:
                require(coeffs[label] == 1, "integer target coefficient")

    print(
        "PASS_ELEMENTARY_ABELIAN_FOUR_LABEL_FLOOR"
        f" quadruples=35 bases={bases} label_triples=512"
        f" unit_gates=3 rank_one_gates=4 total_rank_at_least=5"
        f" standard_weight_range={min_weight}..{max_weight}"
        f" omissions={omitted} cleared_bits={cleared}"
        f" idempotents={len(idempotents)} engines=3"
        " no_new_kappa"
    )


if __name__ == "__main__":
    main()
