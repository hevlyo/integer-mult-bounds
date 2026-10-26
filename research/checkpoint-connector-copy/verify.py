#!/usr/bin/env python3
"""Charge one auxiliary checkpoint on the universal dirty connector.

The new call is S: w += z. Source toggles touch only z. Output reads may use z
or w. Both roots and every source row stay arbitrarily dirty and must return
to their initial values. S is one complete root call, not a free copy.

The uniform all-31 five-source budget stays 74. Every covering schedule that
uses S costs at least 76. An explicit eight-checkpoint word covers at 80.
"""

from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "research" / "universal-connector-boundary" / "CERTIFICATE.json"
FULL5 = (1 << 32) - 1
PILOT = (0, 1, 2, 0, 3, 1, 4, 2, 3, 4)
# Cinna Davis, discussion 1412: S at B-count boundaries 1,2,3,3,4,6,8,9.
CLAIMED_COUNTS = (0, 1, 1, 2, 1, 0, 1, 0, 1, 1, 0)
# A second restoring eight-checkpoint placement found by direct search.
ALTERNATE_COUNTS = (0, 1, 1, 0, 1, 0, 1, 2, 1, 1, 0)
REPAIR = (2, 0, 2, 1, 2, 0, 3, 1, 4, 2, 3, 4)
THREE = (0, 1, 0, 1, 2, 2)
THREE_PAIRS = {
    1: (0, 1),
    2: (0, 3),
    3: (0, 2),
    4: (0, 5),
    5: (1, 5),
    6: (3, 5),
    7: (2, 5),
}


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def double_words(n, word=(), counts=()):
    """Restricted-growth double occurrences. Each label is used twice."""
    if len(word) == 2 * n:
        yield word
        return
    for label, count in enumerate(counts):
        if count == 1:
            after = counts[:label] + (2,) + counts[label + 1:]
            yield from double_words(n, word + (label,), after)
    if len(counts) < n:
        yield from double_words(n, word + (len(counts),), counts + (1,))


def prefixes(word):
    values = [0]
    for label in word:
        values.append(values[-1] ^ (1 << label))
    return values


def difference_mask(values):
    mask = 0
    for left in values:
        for right in values:
            mask |= 1 << (left ^ right)
    return mask


def compositions(bins, total):
    """Nonnegative integer solutions of length `bins` summing to `total`."""
    slots = total + bins - 1
    for bars in combinations(range(slots), bins - 1):
        previous = -1
        row = []
        for bar in bars:
            row.append(bar - previous - 1)
            previous = bar
        row.append(slots - 1 - previous)
        yield tuple(row)


def checkpoint_view(qs, counts):
    """Return (restored, z_mask, even_r_mask, odd_r_mask, after_each_s)."""
    even = 0
    odd = 0
    r = 0
    k = 0
    after = []
    for boundary, q in enumerate(qs):
        for _ in range(counts[boundary]):
            if k & 1:
                odd |= 1 << r
            else:
                even |= 1 << r
            r ^= q
            k += 1
            after.append(r)
        if k & 1:
            odd |= 1 << r
        else:
            even |= 1 << r
    restored = (k % 2 == 0) and r == 0
    return restored, difference_mask(qs), even, odd, after


def masks_of(bitmask):
    return [i for i in range(32) if bitmask >> i & 1]


def same_parity_masks(even, odd):
    out = 0
    for group in (even, odd):
        states = masks_of(group)
        for left in states:
            for right in states:
                out |= 1 << (left ^ right)
    return out


def adds_mask_outside(qs, counts):
    restored, zmask, even, odd, _after = checkpoint_view(qs, counts)
    if not restored:
        return False
    return bool(same_parity_masks(even, odd) & ~zmask)


def census(n):
    entries = sorted((list(word), difference_mask(prefixes(word))) for word in double_words(n))
    hist = Counter(mask.bit_count() for _, mask in entries)
    digest = sha256(json.dumps(entries, separators=(",", ":")).encode()).hexdigest()
    return entries, hist, digest


def no_new_masks(words, copies):
    checked = 0
    for word in words:
        qs = prefixes(word)
        width = len(qs)
        for counts in compositions(width, copies):
            checked += 1
            if adds_mask_outside(qs, counts):
                return False, checked, word, counts
    return True, checked, None, None


def compile_z_schedule(word, pairs):
    """pairs maps a positive mask to two boundary indices."""
    events = []
    pending = {boundary: [] for boundary in range(len(word) + 1)}
    for mask, (left, right) in pairs.items():
        pending[left].append(("Az", mask))
        pending[right].append(("Az", mask))
    for boundary, label in enumerate(word):
        events.extend(pending[boundary])
        events.append(("B", label))
    events.extend(pending[len(word)])
    return events


def compile_checkpoint_schedule(word, counts):
    """Place two reads per nonzero mask, using w only when z has no pair."""
    qs = prefixes(word)
    restored, zmask, even, odd, after = checkpoint_view(qs, counts)
    require(restored, "checkpoint schedule does not restore")
    states = []
    r = 0
    k = 0
    plan = []
    for boundary, q in enumerate(qs):
        for _ in range(counts[boundary]):
            plan.append(("S", len(states)))
            states.append((q, r, k & 1))
            plan.append(("K",))
            r ^= q
            k += 1
        plan.append(("S", len(states)))
        states.append((q, r, k & 1))
        if boundary < len(word):
            plan.append(("B", word[boundary]))
    by_q = {}
    by_r = {0: {}, 1: {}}
    for index, (q, rv, parity) in enumerate(states):
        by_q.setdefault(q, []).append(index)
        by_r[parity].setdefault(rv, []).append(index)
    reads = {index: [] for index in range(len(states))}
    width = 1 << (max(word) + 1 if word else 0)
    # Five-source callers pass masks 1..31. Smaller pilots pass their own width.
    limit = width
    for mask in range(1, limit):
        placed = False
        for q, slots in by_q.items():
            other = q ^ mask
            if other in by_q and (q != other or len(slots) >= 2):
                left = by_q[q][0]
                right = by_q[other][0] if q != other else by_q[q][1]
                reads[left].append(("Az", mask))
                reads[right].append(("Az", mask))
                placed = True
                break
        if placed:
            continue
        for parity in (0, 1):
            for rv, slots in by_r[parity].items():
                other = rv ^ mask
                group = by_r[parity]
                if other in group and (rv != other or len(slots) >= 2):
                    left = group[rv][0]
                    right = group[other][0] if rv != other else group[rv][1]
                    reads[left].append(("Aw", mask))
                    reads[right].append(("Aw", mask))
                    placed = True
                    break
            if placed:
                break
        require(placed, f"no pair for mask {mask}")
    events = []
    for item in plan:
        if item[0] == "S":
            events.extend(reads[item[1]])
        else:
            events.append(item)
    return events, after, zmask


def run_bits(events, x, y, z, w):
    x = list(x)
    y = list(y)
    for kind, *payload in events:
        if kind == "B":
            z ^= x[payload[0]]
        elif kind == "K":
            w ^= z
        elif kind == "Az":
            y[payload[0]] ^= z
        elif kind == "Aw":
            y[payload[0]] ^= w
        else:
            raise SystemExit("unknown event")
    return x, y, z, w


def dot(mask, x):
    total = 0
    for bit, value in enumerate(x):
        if mask >> bit & 1:
            total ^= value
    return total


def accepts_identity(events, sources, masks, dirty_w=True):
    """Finite L=1 identity checks, including arbitrary one-bit dirt."""
    basis = []
    for j in range(sources):
        row = [0] * sources
        row[j] = 1
        basis.append(row)
    basis.append([0] * sources)
    dirts = [(0, 0), (1, 0)]
    if dirty_w:
        dirts.extend(((0, 1), (1, 1)))
    span = max(masks) + 1
    y0_choices = ([0] * span, [1] * span)
    for x in basis:
        for z0, w0 in dirts:
            for y0 in y0_choices:
                x1, y1, z1, w1 = run_bits(events, x, y0, z0, w0)
                if x1 != x or z1 != z0 or w1 != w0:
                    return False
                for mask in masks:
                    if y1[mask] != (y0[mask] ^ dot(mask, x)):
                        return False
    return True


def three_source_pilot():
    words = list(double_words(3))
    require(len(words) == 15, "three-source domain")
    hist = Counter(difference_mask(prefixes(word)).bit_count() for word in words)
    require(hist == Counter({8: 10, 7: 5}), "three-source coverage")
    for copies in (2, 4, 6):
        clear, checked, _word, _counts = no_new_masks(words, copies)
        require(clear, f"three-source {copies} checkpoints created a mask")
        require(checked > 0, "empty three-source search")
    events = compile_z_schedule(THREE, THREE_PAIRS)
    require(sum(1 for kind, *_ in events if kind == "B") == 6, "three-source B count")
    require(sum(1 for kind, *_ in events if kind == "Az") == 14, "three-source A count")
    require(len(events) == 20, "three-source uniform optimum witness")
    masks = list(range(1, 8))
    passed = 0
    for x0 in range(8):
        x = [(x0 >> j) & 1 for j in range(3)]
        for y0 in range(128):
            y = [0] + [(y0 >> j) & 1 for j in range(7)]
            for z0 in (0, 1):
                for w0 in (0, 1):
                    x1, y1, z1, w1 = run_bits(events, x, y, z0, w0)
                    require(x1 == x and z1 == z0 and w1 == w0, "three-source restoration")
                    for mask in masks:
                        require(y1[mask] == (y[mask] ^ dot(mask, x)), "three-source mask")
                    passed += 1
    require(passed == 4096, "three-source dirty sweep")
    # Failure controls: one omitted readout, and one unrestored checkpoint.
    removed = False
    trimmed = []
    for event in events:
        if event == ("Az", 7) and not removed:
            removed = True
            continue
        trimmed.append(event)
    require(removed, "mask 7 readout missing from the pilot")
    detected = False
    for x0 in range(8):
        x = [(x0 >> bit) & 1 for bit in range(3)]
        _x1, y1, z1, _w1 = run_bits(trimmed, x, [0] * 8, 0, 0)
        if z1 != 0 or y1[7] != dot(7, x):
            detected = True
            break
    require(detected, "omitted readout was not detected")
    odd = [("K",), ("B", 0), ("B", 0)]
    _x1, _y1, z1, w1 = run_bits(odd, [0, 0, 0], [], 1, 0)
    require(w1 == 1 and z1 == 1, "odd checkpoint failed to keep z-dirt")
    return passed


def main():
    pilot_states = three_source_pilot()
    cert = json.loads(CERTIFICATE.read_text())
    reported = {row["sources"]: row for row in cert["censuses"]}
    summaries = {}
    five_words = None
    for sources in (4, 5):
        entries, hist, digest = census(sources)
        row = reported[sources]
        require(row["canonical_entries_sha256"] == digest, f"{sources}-source digest")
        require(row["pairings"] == len(entries), f"{sources}-source pairing count")
        require(row["max_coverage"] == max(hist), f"{sources}-source max coverage")
        expect = {int(key): value for key, value in row["histogram"].items()}
        require(dict(hist) == expect, f"{sources}-source histogram")
        summaries[sources] = {"pairings": len(entries), "max": max(hist), "sha256": digest}
        if sources == 5:
            five_words = [tuple(word) for word, _mask in entries]
    require(len(five_words) == 945, "five-source domain")
    require(PILOT in five_words, "pilot left the canonical domain")

    for copies in (2, 4, 6):
        clear, checked, word, counts = no_new_masks(five_words, copies)
        require(clear, f"{copies} checkpoints added a mask on {word} {counts}")
        require(checked == 945 * len(list(compositions(11, copies))), f"{copies} search domain")

    events, after, _zmask = compile_checkpoint_schedule(PILOT, CLAIMED_COUNTS)
    require(after[2] == 5 and after[6] == 16, "third and seventh checkpoint states")
    require(after[2] ^ after[6] == 21, "mask 21 is not the claimed checkpoint difference")
    require(sum(1 for kind, *_ in events if kind == "B") == 10, "claimed B count")
    require(sum(1 for kind, *_ in events if kind == "K") == 8, "claimed S count")
    require(sum(1 for kind, *_ in events if kind in ("Az", "Aw")) == 62, "claimed A count")
    require(len(events) == 80, "claimed uniform cost")
    require(any(event[0] == "Aw" and event[1] == 21 for event in events),
            "mask 21 was not read from w")
    masks = list(range(1, 32))
    require(accepts_identity(events, 5, masks), "claimed witness L=1 identity")

    alt_events, alt_after, _zmask = compile_checkpoint_schedule(PILOT, ALTERNATE_COUNTS)
    require(len(alt_events) == 80, "alternate uniform cost")
    require(21 in {alt_after[i] ^ alt_after[j]
                   for i in range(8) for j in range(8) if (i % 2) == (j % 2)},
            "alternate placement missed mask 21")
    require(accepts_identity(alt_events, 5, masks), "alternate witness L=1 identity")

    # Two cancelling checkpoints on the twelve-toggle repair are legal and cost 76.
    repair_qs = prefixes(REPAIR)
    require(difference_mask(repair_qs) == FULL5, "twelve-toggle repair is not universal")
    pad = (2,) + (0,) * len(REPAIR)
    restored, zmask, even, odd, _after = checkpoint_view(repair_qs, pad)
    require(restored and zmask == FULL5, "padded repair failed")
    require(same_parity_masks(even, odd) & ~zmask == 0, "padding invented a mask")
    repair_events = compile_z_schedule(REPAIR, {
        mask: next((pair for pair in combinations(range(len(repair_qs)), 2)
                    if repair_qs[pair[0]] ^ repair_qs[pair[1]] == mask))
        for mask in range(1, 32)
    })
    require(len(repair_events) == 74, "singleton repair cost")
    require(len(repair_events) + 2 == 76, "cancelling checkpoint pair costs 76")
    require(accepts_identity(repair_events, 5, masks, dirty_w=False), "repair L=1 identity")

    # The pilot's own four-checkpoint placements do not cover. This is the
    # failure control for treating a short checkpoint list as enough.
    qs = prefixes(PILOT)
    four_hits = sum(1 for counts in compositions(11, 4) if adds_mask_outside(qs, counts))
    require(four_hits == 0, "four checkpoints on the pilot added a mask")
    broken = list(CLAIMED_COUNTS)
    broken[9] -= 1
    restored, _zmask, even, odd, _after = checkpoint_view(qs, tuple(broken))
    covered = restored and (zmask | same_parity_masks(even, odd)) == FULL5
    require(not covered, "dropping one claimed checkpoint still covered")

    print(
        "PASS_CHECKPOINT_CONNECTOR_COPY "
        f"pairings=945 max_coverage=31 queries_without_s=74 "
        f"min_queries_using_s=76 witness_queries=80 "
        f"checkpoint_states=5,16 mask21=21 "
        f"three_dirty={pilot_states} "
        f"sha5={summaries[5]['sha256']}"
    )


if __name__ == "__main__":
    main()
