#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Selected T16 family uniqueness does not follow from the spectator chart.

The pinned data-phase basis puts the port vector at frame index 0, and no
pending axis is that vector. Every width-at-most-8 greedy spectator list
therefore contains index 0. A width-9 route stores no spectators, so two
width-9 slices have disjoint spectator lists and still share a family.

Standard library only. Reads pinned inputs and writes nothing.
"""
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
H, M, V = 9, 73, 112
FAMILIES_PER_REPLICA = 896
PHASES = ROOT / "research/community-k492-audit/pr622/replay/baseline558/complex-global/base/work/complex-nine-native/DATA-PHASES.json"
CANON = ROOT / "research/community-k492-audit/pr622/replay/baseline558/complex-global/base/split-centres/CANONICAL-WORD.json.gz"
OWNERS = ROOT / "research/complex-t16-rare-pattern-exchanges/data/OWNERS.json.gz"
TEMPLATE = ROOT / "research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor535/inputs/ROUND20-PARENT-TEMPLATE.json.gz"
PROOF = ROOT / "research/complex-double-replica-owners/PROOF.md"

WITNESS = dict(child=8, port=0, width=9, offsets=(0, 9), owner=0)


class Gap(Exception):
    pass


def need(ok, message):
    if not ok:
        raise Gap(message)


def load(path):
    raw = path.read_bytes()
    if path.name.endswith(".gz"):
        raw = gzip.decompress(raw)
    return json.loads(raw)


def basis(q):
    zero = next(i for i in range(H) if (q >> i & 1) == 0)
    correction = q ^ (1 << zero)
    order = list(range(H))
    order[0], order[zero] = order[zero], order[0]
    frame = [(1 << i) ^ (correction if (correction >> i) & 1 else 0) for i in order]
    frame.extend(1 << i for i in range(H, M))
    return frame


def orthogonal(frame):
    return all((x & y).bit_count() % 2 == int(i == j)
               for i, x in enumerate(frame) for j, y in enumerate(frame))


def spectators(occupied, width):
    """Greedy complement prefix used by the width-w route. Width 9 stores none."""
    need(0 <= width <= H, "width")
    count = H - width
    if count == 0:
        return []
    out = []
    for i in range(M):
        if i not in occupied:
            out.append(i)
            if len(out) == count:
                break
    need(len(out) == count, "spectator prefix length")
    return out


def chart_ok(occupied, width):
    spec = spectators(set(occupied), width)
    if len(occupied) != width or len(set(occupied)) != width:
        return False
    if len(set(occupied).intersection(spec)) != 0:
        return False
    rest = [i for i in range(M) if i not in occupied and i not in spec]
    perm = list(occupied) + spec + rest
    return sorted(perm) == list(range(M))


def family_id(place, owner, child, port):
    pair, side = place[child]
    return owner * FAMILIES_PER_REPLICA + (2 * pair + side) * V + port


def unique_families(rows):
    seen = set()
    for row in rows:
        key = (row["stage"], row["replica"], row["family"])
        if key in seen:
            return False
        seen.add(key)
    return True


def avoids_port_vector(pending, query, locate):
    return all(vector in locate and locate[vector] != 0 and vector != query for vector in pending)


def pending_lists(phases):
    by_port = {recipe["port"]: recipe for recipe in phases["recipes"]}
    need(sorted(by_port) == list(range(V)), "phase ports")
    axes = {}
    for port, recipe in by_port.items():
        children = recipe["idle_children"]
        items = enumerate(children) if isinstance(children, list) else (
            (int(k), v) for k, v in children.items())
        for child, item in items:
            axes[port, child] = [int(x) for x in item["orthogonal_axes"]]
    return by_port, axes


def places(template):
    events = template["execution_schedule"]
    need([e["kind"] for e in events[30:]] == ["bank_padding_cover_sweep", "translate_every_live_family"],
         "template tail")
    place = {}
    for event in events[:30]:
        if event["kind"] != "idle_cover_sweep":
            continue
        need(len(event["child_indices"]) == 2, "two sides")
        for side, child in enumerate(event["child_indices"]):
            need(child not in place, "child swept twice")
            place[child] = (event["pair"], side)
    return place


def main():
    phases, canon, roles, template = load(PHASES), load(CANON), load(OWNERS), load(TEMPLATE)
    proof = PROOF.read_text()
    need("The whole-family uniqueness rule is necessary even for narrow slices:" in proof, "proof sentence")
    need("spectator coordinates can borrow other coordinates of that family during the" in proof,
         "proof sentence")
    need("supplies `9-width`" in proof, "proof spectator budget")

    by_port, axes = pending_lists(phases)
    queries = [by_port[port]["q"] for port in range(V)]
    need(canon["ports"] == queries, "canonical ports equal phase queries")
    frames = [basis(q) for q in queries]
    need(all(orthogonal(frame) and len(frame) == M and len(set(frame)) == M for frame in frames),
         "port bases")
    need(all(frame[0] == q for frame, q in zip(frames, queries)), "frame index 0 is the port vector")
    index_of = [{vector: i for i, vector in enumerate(frame)} for frame in frames]

    pending_count = sum(len(pending) for pending in axes.values())
    need(pending_count == 48384, "pending-axis count")
    need(all(avoids_port_vector(pending, queries[port], index_of[port])
             for (port, _child), pending in axes.items()),
         "pending axis meets the port vector")
    mutated = list(axes[0, 0])
    mutated[0] = queries[0]
    need(not avoids_port_vector(mutated, queries[0], index_of[0]),
         "port-vector insertion must fail the pending-axis test")

    place = places(template)
    need(WITNESS["child"] in place, "witness child")
    witness_axes = axes[WITNESS["port"], WITNESS["child"]]
    need(len(witness_axes) >= 18 and len(set(witness_axes[:18])) == 18, "witness room")
    slices = []
    for offset in WITNESS["offsets"]:
        occupied = [index_of[WITNESS["port"]][vector]
                    for vector in witness_axes[offset:offset + WITNESS["width"]]]
        spec = spectators(set(occupied), WITNESS["width"])
        need(spec == [] and chart_ok(occupied, WITNESS["width"]), "width-9 chart")
        slices.append(occupied)
    need(set(slices[0]).isdisjoint(slices[1]), "witness slices are disjoint")
    shared = family_id(place, WITNESS["owner"], WITNESS["child"], WITNESS["port"])
    pair = [
        dict(stage=0, replica=0, family=shared, width=9),
        dict(stage=0, replica=0, family=shared, width=9),
    ]
    need(not unique_families(pair), "same-family width-9 pair violates uniqueness")
    other = family_id(place, WITNESS["owner"], WITNESS["child"], WITNESS["port"] + 1)
    need(other != shared and unique_families([
        dict(stage=0, replica=0, family=shared, width=9),
        dict(stage=0, replica=0, family=other, width=9),
    ]), "different families stay unique")

    narrow = axes[WITNESS["port"], WITNESS["child"]]
    narrow_sets = []
    for offset in (0, 8):
        occupied = [index_of[WITNESS["port"]][vector] for vector in narrow[offset:offset + 8]]
        spec = spectators(set(occupied), 8)
        need(spec[0] == 0 and chart_ok(occupied, 8), "width-8 spectators contain index 0")
        narrow_sets.append(set(spec))
    need(not narrow_sets[0].isdisjoint(narrow_sets[1]), "width-8 spectators meet")

    mutated = list(axes[0, 0])
    mutated[0] = queries[0]
    need(any(vector == queries[0] for vector in mutated), "control can see a port-vector axis")

    need(len(roles) == 69120, "selected role count")
    width_counts = Counter()
    per_call = Counter()
    width9_per_call = Counter()
    for role in roles:
        width = role["width"]
        width_counts[width] += 1
        call = (role["stage"], role["replica"])
        per_call[call] += 1
        if width == 9:
            width9_per_call[call] += 1
        pending = axes[role["port"], role["child"]]
        occupied = [index_of[role["port"]][vector]
                    for vector in pending[role["offset"]:role["offset"] + width]]
        spec = spectators(set(occupied), width)
        need(chart_ok(occupied, width), "selected chart")
        if width < 9:
            need(spec[0] == 0, "selected narrow spectator")
        else:
            need(spec == [], "selected width-9 spectator")
        need(role["family"] == family_id(place, role["owner_replica"], role["child"], role["port"]),
             "selected family identity")
    need(unique_families(roles), "selected map repeats a family")
    need(dict(sorted(width_counts.items())) == {4: 8064, 5: 4608, 7: 4320, 8: 17568, 9: 34560},
         "selected widths")
    need(len(per_call) == 144 and set(per_call.values()) == {480}, "selected calls")
    need(set(width9_per_call.values()) == {240}, "width-9 helpers in every call")

    result = {
        "status": "PASS_SELECTED_WIDTH9_SPECTATOR_GAP",
        "base_commit": "ef5f39403610d231a0c27e8a6b4f08c10209bcd6",
        "pending_axes": pending_count,
        "port_bases": V,
        "frame_index_0": "port vector",
        "selected_roles": len(roles),
        "selected_width9_roles": width_counts[9],
        "selected_family_collisions": 0,
        "witness": {
            "child": WITNESS["child"],
            "port": WITNESS["port"],
            "owner": WITNESS["owner"],
            "pair_side": list(place[WITNESS["child"]]),
            "offsets": list(WITNESS["offsets"]),
            "width": 9,
            "family": shared,
            "spectator_lists": [[], []],
            "charts_accept": True,
            "family_uniqueness_accepts": False,
        },
        "scope": "Finite pinned phase geometry and selected PR1094 owner roles. No new kappa.",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print(result["status"])


if __name__ == "__main__":
    try:
        main()
    except (Gap, KeyError, IndexError, ValueError) as exc:
        print("FAIL", exc, file=sys.stderr)
        sys.exit(1)
