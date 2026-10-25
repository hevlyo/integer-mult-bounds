#!/usr/bin/env python3
"""Exact dirty-handoff certificate for two five-source connector batches.

The singleton alphabet and paired-readout rule are Ross Richardson's,
from research/universal-connector-boundary. This checker does not import
that package. It rechecks the published four-source prefixes and the
published ten- and twelve-toggle five-source words, then certifies the
two-batch handoff.

Standard library only. Apache-2.0.
Substantial AI assistance was used for the enumeration, the witness check,
and the notes. No product name is recorded here.
"""

from math import comb, factorial
import sys

NBITS = 5
SPACE = 1 << NBITS
FULL = (1 << SPACE) - 1
WITNESS = (0, 1, 0, 2, 0, 1, 0, 3, 4, 3)
CLOSED12 = (2, 0, 2, 1, 2, 0, 3, 1, 4, 2, 3, 4)
OPEN10_MISSING = (0, 1, 2, 0, 3, 1, 4, 2, 3, 4)
FOUR_SOURCE = (0, 1, 0, 1, 2, 3, 2, 3)
FOUR_PREFIXES = (0, 1, 3, 2, 0, 4, 12, 8, 0)

# Restricted-growth census, frozen after the exhaustive count below.
EXPECTED = {
    9: {"leaves": 18002, "covers": 0, "zero_end": 0, "min_leaf": None},
    10: {"leaves": 86472, "covers": 188, "zero_end": 0, "min_leaf": 76},
    11: {"leaves": 422005, "covers": 4716, "zero_end": 0, "min_leaf": 77},
    12: {"leaves": 2079475, "covers": 68328, "zero_end": 1116, "min_leaf": 78},
}


class CheckError(Exception):
    pass


def require(ok, message):
    if not ok:
        raise CheckError(message)


def ell(depth):
    """Balanced complete-leaf recurrence from the predecessor interface."""
    require(depth >= 1, "leaf depth must be positive")
    if depth == 1:
        return 1
    left = depth // 2
    return 2 * ell(left) + 2 * ell(depth - left)


def prices():
    return tuple(ell(depth) for depth in range(1, NBITS + 1))


def stirling2(size, parts):
    if parts < 0 or size < 0 or parts > size:
        return 0
    if parts == 0:
        return 1 if size == 0 else 0
    signed = 0
    for term in range(parts + 1):
        signed += (-1) ** (parts - term) * comb(parts, term) * term**size
    return signed // factorial(parts)


def restricted_growth_total(length):
    return sum(stirling2(length, parts) for parts in range(NBITS + 1))


def prefixes_of(word):
    state = 0
    points = [0]
    for label in word:
        require(0 <= label < NBITS, "toggle label out of range")
        state ^= 1 << label
        points.append(state)
    return points


def coverage_mask(points):
    mask = 0
    seen = []
    present = 0
    for point in points:
        bit = 1 << point
        if present & bit:
            continue
        for earlier in seen:
            mask |= 1 << (point ^ earlier)
        mask |= 1  # point XOR point
        seen.append(point)
        present |= bit
        if mask == FULL:
            return mask
    return mask


def assignment_cost(counts, leaf_prices):
    if any(count <= 0 for count in counts):
        return None
    ordered = sorted(counts)
    expensive = sorted(leaf_prices, reverse=True)
    return sum(count * price for count, price in zip(ordered, expensive))


def census(length, leaf_prices):
    """Enumerate every restricted-growth toggle word of this length once."""
    leaves = 0
    covers = 0
    zero_end = 0
    min_leaf = None

    def walk(state, seen, distinct, covered, max_label, steps, counts):
        nonlocal leaves, covers, zero_end, min_leaf
        if steps == length:
            leaves += 1
            if covered == FULL:
                covers += 1
                if state == 0:
                    zero_end += 1
                cost = assignment_cost(counts, leaf_prices)
                require(cost is not None, "a full cover used fewer than five labels")
                if min_leaf is None or cost < min_leaf:
                    min_leaf = cost
            return
        upper = min(NBITS - 1, max_label + 1)
        for label in range(upper + 1):
            nxt = state ^ (1 << label)
            bit = 1 << nxt
            counts[label] += 1
            if seen & bit:
                walk(nxt, seen, distinct, covered, max(max_label, label), steps + 1, counts)
            else:
                added = covered
                for earlier in distinct:
                    added |= 1 << (nxt ^ earlier)
                distinct.append(nxt)
                walk(nxt, seen | bit, distinct, added, max(max_label, label), steps + 1, counts)
                distinct.pop()
            counts[label] -= 1

    walk(0, 1, [0], 1, -1, 0, [0] * NBITS)
    return {
        "leaves": leaves,
        "covers": covers,
        "zero_end": zero_end,
        "min_leaf": min_leaf,
    }


def first_pairs(points):
    """Lexicographically first boundary pair for every nonzero mask."""
    locations = {}
    for index, point in enumerate(points):
        locations.setdefault(point, []).append(index)
    pairs = {}
    for mask in range(1, SPACE):
        found = None
        for left, left_times in locations.items():
            right = left ^ mask
            right_times = locations.get(right)
            if not right_times:
                continue
            for i in left_times:
                for j in right_times:
                    if i == j:
                        continue
                    pair = (i, j) if i < j else (j, i)
                    if found is None or pair < found:
                        found = pair
        if found is None:
            return None
        pairs[mask] = found
    return pairs


def run_batches(word, spans):
    """Symbolic F2 coefficient replay.

    spans are inclusive prefix-index intervals. Reads at a boundary see the
    source parity before any later toggle. Returns final source parity,
    each batch's mask coefficients, and each batch's initial-dirt parity.
    """
    points = prefixes_of(word)
    batches = []
    for start, end in spans:
        local = first_pairs(points[start:end + 1])
        if local is None:
            return None
        batches.append({mask: (start + a, start + b) for mask, (a, b) in local.items()})
    parity = [0] * NBITS
    rows = [[[0] * NBITS for _ in range(SPACE)] for _ in batches]
    dirt = [[0] * SPACE for _ in batches]
    for time, _point in enumerate(points):
        for batch, pairs in enumerate(batches):
            for mask, (left, right) in pairs.items():
                if time != left and time != right:
                    continue
                for source in range(NBITS):
                    rows[batch][mask][source] ^= parity[source]
                dirt[batch][mask] ^= 1
        if time < len(word):
            parity[word[time]] ^= 1
    return parity, rows, dirt


def masks_match(parity, rows, dirt):
    if parity != [0] * NBITS:
        return False
    for batch_rows, batch_dirt in zip(rows, dirt):
        for mask in range(1, SPACE):
            bits = [(mask >> source) & 1 for source in range(NBITS)]
            if batch_rows[mask] != bits or batch_dirt[mask] != 0:
                return False
    return True


def published_fixtures(leaf_prices):
    four = prefixes_of(FOUR_SOURCE)
    require(tuple(four) == FOUR_PREFIXES, "four-source prefixes drifted from the published word")
    require(coverage_mask(four) == (1 << 16) - 1, "published four-source word is not universal on F2^4")

    missing_points = prefixes_of(OPEN10_MISSING)
    missing = coverage_mask(missing_points)
    require(missing.bit_count() == 31, "published ten-toggle word should miss one mask")
    require((missing & (1 << 21)) == 0, "published ten-toggle word should miss mask 21")
    require(missing_points[-1] == 0, "published ten-toggle word should restore the connector")

    closed_points = prefixes_of(CLOSED12)
    require(coverage_mask(closed_points) == FULL, "published twelve-toggle repair is not universal")
    require(closed_points[-1] == 0, "published twelve-toggle repair should restore the connector")
    closed_counts = [CLOSED12.count(label) for label in range(NBITS)]
    require(sorted(closed_counts) == [2, 2, 2, 2, 4], "closed minimum multiplicity changed")
    require(assignment_cost(closed_counts, leaf_prices) == 120, "restored batch leaf cost is not 120")


def certify_witness(leaf_prices):
    points = prefixes_of(WITNESS)
    require(points == [0, 1, 3, 2, 6, 7, 5, 4, 12, 28, 20], "witness prefixes changed")
    require(coverage_mask(points) == FULL, "witness segment is not a difference basis")
    require(points[-1] == 20, "witness endpoint changed")
    counts = [WITNESS.count(label) for label in range(NBITS)]
    require(sorted(counts) == [1, 1, 2, 2, 4], "witness multiplicity changed")
    require(assignment_cost(counts, leaf_prices) == 76, "witness segment leaf cost is not 76")

    doubled = WITNESS + WITNESS
    doubled_points = prefixes_of(doubled)
    require(doubled_points[-1] == 0, "doubled witness does not restore the connector")
    require(coverage_mask(doubled_points[:11]) == FULL, "first handoff segment lost coverage")
    second = doubled_points[10:]
    relative = [point ^ second[0] for point in second]
    require(coverage_mask(relative) == FULL, "second handoff segment lost coverage")

    replay = run_batches(doubled, ((0, 10), (10, 20)))
    require(replay is not None and masks_match(*replay), "symbolic doubled schedule failed")
    parity, rows, dirt = replay
    require(parity == [0] * NBITS, "final source parity is dirty")
    require(all(batch[mask] == 0 for batch in dirt for mask in range(1, SPACE)), "entry dirt survived")
    require(len(rows) == 2 and len(dirt) == 2, "expected two batches")

    # The same word is not a legal restored one-batch schedule.
    alone = run_batches(WITNESS, ((0, 10),))
    require(alone is not None, "witness unexpectedly lost its own readouts")
    alone_parity, alone_rows, alone_dirt = alone
    require(alone_parity != [0] * NBITS, "open witness restored the connector by itself")
    require(alone_dirt[0][1] == 0 and alone_rows[0][1] == [1, 0, 0, 0, 0],
            "open witness lost mask 1 before the exit check")
    require(masks_match(*alone) is False, "dirty exit was accepted as a restored batch")
    require(dropped_read_accepted(doubled) is False, "dropping one readout was still accepted")

    truncated = WITNESS[:-1]
    require(coverage_mask(prefixes_of(truncated)) != FULL, "length-9 truncation still covers")
    mutated = WITNESS[:-1] + (0,)
    require(not masks_match_word(mutated + mutated), "mutated doubled word was accepted")


def masks_match_word(word):
    if len(word) != 20:
        return False
    replay = run_batches(word, ((0, 10), (10, 20)))
    return replay is not None and masks_match(*replay)


def dropped_read_accepted(word):
    points = prefixes_of(word)
    first = first_pairs(points[:11])
    second = first_pairs(points[10:])
    require(first is not None and second is not None, "pair finder failed on the witness")
    batches = [
        dict(first),
        {mask: (10 + left, 10 + right) for mask, (left, right) in second.items()},
    ]
    later = max(batches[0][1])
    parity = [0] * NBITS
    rows = [[[0] * NBITS for _ in range(SPACE)] for _ in batches]
    dirt = [[0] * SPACE for _ in batches]
    skipped = 0
    for time in range(len(points)):
        for batch, pairs in enumerate(batches):
            for mask, (left, right) in pairs.items():
                if time != left and time != right:
                    continue
                if batch == 0 and mask == 1 and time == later:
                    skipped += 1
                    continue
                for source in range(NBITS):
                    rows[batch][mask][source] ^= parity[source]
                dirt[batch][mask] ^= 1
        if time < len(word):
            parity[word[time]] ^= 1
    require(skipped == 1, "omitted readout was not a single boundary")
    require(dirt[0][1] == 1, "omitted readout cancelled dirt anyway")
    return masks_match(parity, rows, dirt)


def main():
    leaf_prices = prices()
    require(leaf_prices == (1, 4, 10, 16, 28), "leaf recurrence drifted from 1,4,10,16,28")
    published_fixtures(leaf_prices)

    for length, expected in EXPECTED.items():
        require(restricted_growth_total(length) == expected["leaves"],
                "Stirling total mismatch at length %s" % length)
        found = census(length, leaf_prices)
        require(found == expected, "census mismatch at length %s: %s" % (length, found))

    certify_witness(leaf_prices)

    # Exact unit-cost comparison. Each full batch needs 62 paired readouts.
    handoff_sources = 20
    restored_sources = 24
    readouts = 124
    require(EXPECTED[9]["covers"] == 0, "length 9 is not empty")
    require(EXPECTED[10]["covers"] > 0 and EXPECTED[10]["zero_end"] == 0,
            "length-10 covers are not all dirty")
    require(handoff_sources + readouts == 144, "handoff query bill changed")
    require(restored_sources + readouts == 148, "restored query bill changed")
    # Separate restored leaf minimum: no closed cover below length 12, and
    # every closed five-label walk has even positive counts. The cheapest
    # such composition of length at least 12 is (4,2,2,2,2) at cost 120.
    require(assignment_cost([4, 2, 2, 2, 2], leaf_prices) == 120, "closed leaf formula drifted")
    print(
        "PASS_FIVE_SOURCE_DIRTY_HANDOFF"
        " length9_covers=0 length10_covers=188 length10_zero_end=0"
        " handoff_queries=144 restored_queries=148"
        " witness_b_leaves=152 restored_b_leaves=240"
        " leaf_screen_through=12 min_segment_leaf_through_12=76"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CheckError as exc:
        print("FAIL_FIVE_SOURCE_DIRTY_HANDOFF " + str(exc), file=sys.stderr)
        sys.exit(1)
