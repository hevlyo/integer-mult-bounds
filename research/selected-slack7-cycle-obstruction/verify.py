#!/usr/bin/env python3
"""Exact window obstruction for slack-7 three-bin cycles on the selected map.

The selected PR1094 owner map is read from the pinned PLAN and OWNERS files.
No supplier, controller, invoice, or selected record is modified.
"""

import gzip
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "research/complex-t16-rare-pattern-exchanges/data/PLAN.json"
OWNERS = ROOT / "research/complex-t16-rare-pattern-exchanges/data/OWNERS.json.gz"
ANCHORS = ((7, 4), (7, 8), (7, 9))
KNOWN = {
    ((7, 8), (0, 8), (1, 7)): 17567,
    ((7, 8), (1, 7), (0, 7)): 4319,
}


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def load():
    plan = json.loads(PLAN.read_text())
    with gzip.open(OWNERS, "rt") as handle:
        owners = json.load(handle)
    capmap = {}
    windows = {}
    for key, (cap, times) in plan["windows"].items():
        replica, child = map(int, key.split(","))
        windows[(replica, child)] = set(times)
        for port in range(112):
            capmap[(replica, child, port)] = cap
    used = defaultdict(int)
    for role in owners:
        used[(role["owner_replica"], role["child"], role["port"])] += role["width"]
    count = len(owners)
    slack = [0] * count
    width = [0] * count
    owner = [0] * count
    child = [0] * count
    port = [0] * count
    moment = [0] * count
    stage = [0] * count
    replica = [0] * count
    groups = defaultdict(list)
    for index, role in enumerate(owners):
        bin_id = (role["owner_replica"], role["child"], role["port"])
        slack[index] = capmap[bin_id] - used[bin_id]
        require(slack[index] >= 0, "overfull selected bin")
        width[index] = role["width"]
        owner[index], child[index], port[index] = bin_id
        moment[index] = role["time"]
        stage[index] = role["stage"]
        replica[index] = role["replica"]
        require(moment[index] in windows[(bin_id[0], bin_id[1])], "selected role outside its window")
        groups[(slack[index], width[index])].append(index)
    bins = [(owner[i], child[i], port[i]) for i in range(count)]
    return {
        "windows": windows,
        "slack": slack,
        "groups": groups,
        "bins": bins,
        "time": moment,
        "stage": stage,
        "replica": replica,
        "roles": count,
    }


def sign(old, new):
    """Return improve, worsen, neutral, incomparable, or infeasible."""
    if any(value < 0 for value in new) or sum(old) != sum(new):
        return "infeasible"
    old_sorted = tuple(sorted(old, reverse=True))
    new_sorted = tuple(sorted(new, reverse=True))
    if old_sorted == new_sorted:
        return "neutral"

    def majorizes(left, right):
        return left[0] >= right[0] and left[0] + left[1] >= right[0] + right[1]

    if majorizes(new_sorted, old_sorted):
        return "improve"
    if majorizes(old_sorted, new_sorted):
        return "worsen"
    return "incomparable"


def patterns_for(groups, kind):
    classes = list(groups)
    found = []
    for anchor in ANCHORS:
        for second in classes:
            for third in classes:
                old = (anchor[0], second[0], third[0])
                new = (
                    anchor[0] + anchor[1] - third[1],
                    second[0] + second[1] - anchor[1],
                    third[0] + third[1] - second[1],
                )
                if sign(old, new) == kind:
                    found.append((anchor, second, third, old, new))
    return found


def census(data, patterns):
    windows = data["windows"]
    slack = data["slack"]
    groups = data["groups"]
    bins = data["bins"]
    moment = data["time"]
    stage = data["stage"]
    replica = data["replica"]
    capacity = 0
    window = 0
    same_call = 0
    known = {key: 0 for key in KNOWN}
    known_window = {key: 0 for key in KNOWN}
    for anchor, second, third, _old, _new in patterns:
        key = (anchor, second, third)
        for first_index in groups[anchor]:
            first_bin = bins[first_index]
            first_time = moment[first_index]
            first_window = windows[(first_bin[0], first_bin[1])]
            first_call = (stage[first_index], replica[first_index])
            for second_index in groups[second]:
                second_bin = bins[second_index]
                if second_bin == first_bin:
                    continue
                if slack[second_index] == 7 and second_index < first_index:
                    continue
                first_lands = first_time in windows[(second_bin[0], second_bin[1])]
                second_time = moment[second_index]
                second_call = (stage[second_index], replica[second_index])
                for third_index in groups[third]:
                    third_bin = bins[third_index]
                    if third_bin == first_bin or third_bin == second_bin:
                        continue
                    if slack[third_index] == 7 and third_index < first_index:
                        continue
                    capacity += 1
                    same = first_call == second_call == (stage[third_index], replica[third_index])
                    if same:
                        same_call += 1
                    if key in known:
                        known[key] += 1
                    legal = (
                        first_lands
                        and moment[third_index] in first_window
                        and second_time in windows[(third_bin[0], third_bin[1])]
                    )
                    if legal:
                        window += 1
                        if key in known_window:
                            known_window[key] += 1
    return {
        "capacity": capacity,
        "window": window,
        "same_call": same_call,
        "known": known,
        "known_window": known_window,
    }


def synthetic_known_window(data):
    """Repair both blocked legs of one recorded rank-8 triple and expect one hit.

    On the real windows, the (7,8)->(0,8) landings and the (0,8)->(1,7)
    landings are disjoint, and the (1,7) role never lands in the slack-7 bin.
    Opening only one of those facts leaves the pattern empty. The control
    therefore adds the slack-7 call time to that one middle bin's complement
    and adds the unique middle time that already accepts the slack-7 role.
    """
    windows = {key: set(value) for key, value in data["windows"].items()}
    groups = data["groups"]
    bins = data["bins"]
    moment = data["time"]
    anchor = groups[(7, 8)]
    destination = groups[(1, 7)]
    require(len(anchor) == 1 and len(destination) == 1, "unique rank-8 endpoint roles moved")
    anchor_index = anchor[0]
    destination_index = destination[0]
    anchor_bin = bins[anchor_index]
    destination_bin = bins[destination_index]
    by_time = {}
    for second_index in groups[(0, 8)]:
        second_bin = bins[second_index]
        if second_bin == anchor_bin or second_bin == destination_bin:
            continue
        if moment[anchor_index] not in windows[(second_bin[0], second_bin[1])]:
            continue
        by_time.setdefault(moment[second_index], []).append(second_index)
    singletons = [indexes[0] for indexes in by_time.values() if len(indexes) == 1]
    require(len(singletons) == 1, "expected one unique repairable middle time")
    windows[(anchor_bin[0], anchor_bin[1])].add(moment[destination_index])
    windows[(destination_bin[0], destination_bin[1])].add(moment[singletons[0]])
    hits = 0
    for second_index in groups[(0, 8)]:
        second_bin = bins[second_index]
        if second_bin == anchor_bin or second_bin == destination_bin:
            continue
        if moment[anchor_index] not in windows[(second_bin[0], second_bin[1])]:
            continue
        if moment[destination_index] not in windows[(anchor_bin[0], anchor_bin[1])]:
            continue
        if moment[second_index] not in windows[(destination_bin[0], destination_bin[1])]:
            continue
        hits += 1
    return hits


def main():
    require(sign((7, 0, 1), (8, 0, 0)) == "improve", "rank-8 sign control")
    require(sign((8, 0, 0), (7, 0, 1)) == "worsen", "reverse rank-8 sign control")
    require(sign((7, 1, 7), (3, 4, 8)) == "incomparable", "nonuniform sign control")
    require(sign((1, 1, 1), (3, 0, -1)) == "infeasible", "negative-slack sign control")
    data = load()
    require(data["roles"] == 69120, "role count")
    improving = patterns_for(data["groups"], "improve")
    incomparable = patterns_for(data["groups"], "incomparable")
    require(len(improving) == 77, "improving pattern count")
    require(len(patterns_for(data["groups"], "worsen")) == 96, "worsening pattern count")
    require(len(patterns_for(data["groups"], "neutral")) == 39, "neutral pattern count")
    require(len(patterns_for(data["groups"], "infeasible")) == 275, "infeasible pattern count")
    require(len(incomparable) == 20, "incomparable pattern count")
    require(3 * len(data["groups"]) ** 2 == 77 + 96 + 39 + 275 + 20, "pattern partition")
    result = census(data, improving)
    other = census(data, incomparable)
    synthetic = synthetic_known_window(data)
    require(result["known"] == KNOWN, "known capacity counts drifted: " + str(result["known"]))
    require(result["known_window"] == {key: 0 for key in KNOWN}, "known patterns became window-legal")
    require(result["capacity"] == 32981939, "capacity total drifted")
    require(result["window"] == 0, "a uniformly improving cycle passed every window")
    require(result["same_call"] == 0, "same-call improving cycle appeared")
    require(other["capacity"] == 325142, "incomparable capacity total drifted: " + str(other["capacity"]))
    require(other["window"] == 0, "an incomparable cycle passed every window")
    require(synthetic == 1, "synthetic window control drifted: " + str(synthetic))
    print(
        "PASS_SELECTED_SLACK7_CYCLE_OBSTRUCTION "
        f"improving_patterns=77 capacity={result['capacity']} window=0 "
        f"same_call=0 known=17567+4319 incomparable_patterns=20 "
        f"incomparable_capacity={other['capacity']} incomparable_window=0 "
        f"synthetic_window_hits={synthetic} roles=69120 no_new_kappa"
    )


if __name__ == "__main__":
    main()
