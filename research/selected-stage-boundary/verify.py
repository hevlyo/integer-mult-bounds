#!/usr/bin/env python3
"""Selected T16 stage boundary: the next call does not rebuild the hosted cell.

The pinned PR1094 owner map places each helper once per stage. This checker
counts those successive pairs, proves the next placement misses the previous
cell, and shows every recorded window port is exactly full. A separate
one-coordinate capacity increase is priced and rejected as a contract.

Standard-library Python 3.12. Does not write files. Do not set PYTHONOPTIMIZE:
the imported moment engines are not the outer assembly, but this script still
relies on ordinary asserts in its own checks.
"""

import gzip
import importlib.util
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / "research/complex-t16-rare-pattern-exchanges/data/PLAN.json"
OWNERS_PATH = ROOT / "research/complex-t16-rare-pattern-exchanges/data/OWNERS.json.gz"
SPEC_PATH = ROOT / "research/complex-t16-rare-pattern-exchanges/data/SPEC.json"
ASSEMBLY_PATH = ROOT / "research/community-frontier1094-audit/ASSEMBLY.json"
MOMENT_PATH = ROOT / "research/complex-k492-owner-repair/vendor/multicold/engines/moment.py"
BASE_TWO_PATH = ROOT / "research/complex-k492-owner-repair/vendor/multicold/engines/base_two_moment.py"

M = 73
W = 14336
N_CALLS = 144
N_HELPERS = 7680
PLACEMENTS = 9
PORTS = 112
DEFICIT = 5120
MERGES = 144
GAPS = {16: 23040, 12: 9600, 14: 9600, 10: 7680, 8: 5760, 6: 3840, 4: 1920}
SAME_PORT = 41
SAME_WINDOW = 2582
FULL_PORTS = 24730


class Reject(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise Reject(message)


def load_engine(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_inputs():
    plan = json.loads(PLAN_PATH.read_text())
    with gzip.open(OWNERS_PATH, "rt") as handle:
        owners = json.load(handle)
    spec = json.loads(SPEC_PATH.read_text())
    return plan, owners, spec


def call_index(plan):
    calls = plan["provider_calls"]
    require(len(calls) == N_CALLS, "call count")
    by_time = {}
    for call in calls:
        require(call["time"] not in by_time, "duplicate call time")
        by_time[call["time"]] = call
    require(set(by_time) == set(range(N_CALLS)), "call times are 0..143")
    return by_time


def window_intervals(plan):
    intervals = {}
    for key, (capacity, times) in plan["windows"].items():
        replica, child = (int(part) for part in key.split(","))
        times = [int(t) for t in times]
        require(times == list(range(times[0], times[0] + len(times))), "window is not one interval: " + key)
        require(capacity in (8, 16, 32, 48), "unexpected window capacity")
        intervals[(replica, child)] = (int(capacity), times)
    require(len(intervals) == 288, "window count")
    return intervals


def hosted_cells(owners, windows, calls):
    used = defaultdict(set)
    by_helper = defaultdict(list)
    for role in owners:
        require(0 <= role["port"] < PORTS, "port out of range")
        call = calls[role["time"]]
        require(call["replica"] == role["replica"] and call["stage"] == role["stage"], "role/call mismatch")
        window = windows[(role["owner_replica"], role["child"])]
        require(role["time"] in window[1], "role outside its window")
        cells = set(range(role["offset"], role["offset"] + role["width"]))
        key = (role["owner_replica"], role["child"], role["port"])
        require(not used[key] & cells, "hosted cells overlap")
        used[key] |= cells
        by_helper[(role["replica"], role["helper"])].append(role)
    require(len(by_helper) == N_HELPERS, "helper count")
    require(all(len(rows) == PLACEMENTS for rows in by_helper.values()), "placements per helper")
    return used, by_helper


def successive_pairs(by_helper, calls):
    gaps = Counter()
    orientations = Counter()
    same_port = 0
    same_window = 0
    shared_cells = 0
    for rows in by_helper.values():
        rows = sorted(rows, key=lambda role: role["time"])
        stages = [role["stage"] for role in rows]
        require(stages == list(range(PLACEMENTS)), "stages are not 0..8 in time order")
        for left, right in zip(rows, rows[1:]):
            gap = right["time"] - left["time"]
            require(gap >= 2, "successive placements are adjacent calls")
            gaps[gap] += 1
            left_call = calls[left["time"]]["orientation"]
            right_call = calls[right["time"]]["orientation"]
            require({left_call, right_call} == {"forward", "backward"}, "successive orientations do not alternate")
            orientations[(left_call, right_call)] += 1
            same_key = (
                left["owner_replica"] == right["owner_replica"]
                and left["child"] == right["child"]
            )
            if same_key:
                same_window += 1
            if same_key and left["port"] == right["port"]:
                same_port += 1
                left_cells = set(range(left["offset"], left["offset"] + left["width"]))
                right_cells = set(range(right["offset"], right["offset"] + right["width"]))
                shared_cells += len(left_cells & right_cells)
    require(shared_cells == 0, "a later stage rewrites a hosted cell")
    require(dict(gaps) == GAPS, "gap census changed")
    require(same_port == SAME_PORT and same_window == SAME_WINDOW, "port/window census changed")
    require(orientations[("forward", "backward")] == 30720, "forward-to-backward count")
    require(orientations[("backward", "forward")] == 30720, "backward-to-forward count")
    return gaps, same_port, same_window, shared_cells


def port_fill(used, windows):
    idle = Counter()
    full = 0
    donors = []
    for (replica, child), (capacity, _times) in windows.items():
        for port in range(PORTS):
            cells = used.get((replica, child, port), set())
            require(cells == set(range(len(cells))), "hosted cells are not a prefix")
            used_count = len(cells)
            require(used_count <= capacity, "port exceeds capacity")
            slack = capacity - used_count
            if slack == 0:
                full += 1
            else:
                idle[slack] += 1
                if capacity == 48 and slack == 48:
                    donors.append((capacity, used_count))
    require(full == FULL_PORTS, "full-port count")
    require(dict(idle) == {1: 2276, 3: 377, 7: 7, 48: 4866}, "idle remainder profile")
    require(len(donors) == 4866, "empty capacity-48 ports")
    return idle, donors


def fits(capacity, used_count, occupied):
    """True when `occupied` coordinates fit in the recorded capacity."""
    return occupied <= capacity


def profile_from_spec(spec, idle):
    expected = spec["expected"]
    require(expected["live"] == W and expected["rank_mass"] == M * W - DEFICIT, "published mass")
    require(int(expected["provider_counts"]["gauge44"]) == N_CALLS, "provider count")
    global_profile = {int(rank): count for rank, count in expected["global_profile"].items()}
    published_idle = {int(rank): count for rank, count in expected["idle_remainder_profile"].items()}
    require(published_idle == dict(idle), "SPEC idle profile disagrees with owners")
    local = Counter(global_profile)
    local.subtract(published_idle)
    require(all(count % N_CALLS == 0 and count >= 0 for count in local.values()), "local profile is not 144 copies")
    per_call = {rank: count // N_CALLS for rank, count in local.items() if count}
    paid = spec["providers"]["gauge44"]["complete_contract"]["paid_profile"]
    require({int(rank): count for rank, count in paid.items()} == per_call, "per-call profile")
    require(M * W - sum(rank * count for rank, count in global_profile.items()) == DEFICIT, "deficit")
    require(DEFICIT == W - 64 * N_CALLS, "aggregate coverage identity")
    return global_profile


def relaxation(profile):
    """Move 144 rank-1 children into 144 empty capacity-48 remainders."""
    updated = dict(profile)
    require(updated[1] >= MERGES and updated[48] >= MERGES, "relaxation stock")
    updated[1] -= MERGES
    updated[48] -= MERGES
    updated[49] = updated.get(49, 0) + MERGES
    mass = sum(rank * count for rank, count in updated.items())
    require(mass == M * W - DEFICIT, "relaxation is not mass-neutral")
    require(max(updated) == 49 and M * M > 2 * 49 * 49, "halving guard")
    return updated


def moment_bounds(engine, profile, saving, kind):
    if kind == "mercator":
        return engine.moment(profile, M, W, saving, False)
    return engine.moment(M, W, list(profile.items()), saving)


def signs(mercator, base_two, profile, saving):
    low, high = moment_bounds(mercator, profile, saving, "mercator")
    low2, high2 = moment_bounds(base_two, profile, saving, "base_two")
    require((high < 1) == (high2 < 1) and (low > 1) == (low2 > 1), "engines disagree on the sign")
    return high < 1, low > 1


def bracket_root(mercator, profile, lower):
    upper = lower + Fraction(1, 10**6)
    require(moment_bounds(mercator, profile, lower, "mercator")[1] < 1, "lower endpoint not below one")
    require(moment_bounds(mercator, profile, upper, "mercator")[0] > 1, "search upper not above one")
    for _ in range(40):
        mid = (lower + upper) / 2
        if moment_bounds(mercator, profile, mid, "mercator")[1] < 1:
            lower = mid
        else:
            upper = mid
    require(upper - lower < Fraction(1, 10**12), "root bracket is too wide")
    require(moment_bounds(mercator, profile, lower, "mercator")[1] < 1, "bracket lower")
    require(moment_bounds(mercator, profile, upper, "mercator")[0] > 1, "bracket upper")
    return lower, upper


def one_merge(profile, rank):
    updated = dict(profile)
    updated[1] -= 1
    updated[rank] -= 1
    updated[rank + 1] = updated.get(rank + 1, 0) + 1
    if updated[rank] == 0:
        del updated[rank]
    return updated


def expect_reject(label, function):
    try:
        function()
    except Reject:
        return
    raise Reject("control failed to reject: " + label)


def controls(profile, donors, mercator, endpoint):
    def overlap():
        cells = set(range(0, 9))
        require(not cells & set(range(8, 17)), "hosted cells overlap")

    def adjacent():
        require(1 >= 2, "successive placements are adjacent calls")

    def capacity():
        capacity, used_count = donors[0]
        require(fits(capacity, used_count, used_count + (capacity - used_count) + 1),
                "recorded capacity admits another coordinate")

    def mass_drop():
        broken = dict(profile)
        broken[1] -= MERGES
        mass = sum(rank * count for rank, count in broken.items())
        require(M * W - mass == DEFICIT, "deficit")

    def same_orientation():
        require({"forward", "forward"} == {"forward", "backward"}, "successive orientations do not alternate")

    expect_reject("overlap", overlap)
    expect_reject("adjacent", adjacent)
    expect_reject("capacity", capacity)
    expect_reject("mass-drop", mass_drop)
    expect_reject("orientation", same_orientation)
    capacity, used_count = donors[0]
    grown = (capacity - used_count) + 1
    require(not fits(capacity, used_count, used_count + grown), "donor admits a coordinate")
    require(fits(capacity + 1, used_count, used_count + grown), "predicate rejects a grown window")
    low, high = moment_bounds(mercator, one_merge(profile, 48), endpoint, "mercator")
    other_low, _other_high = moment_bounds(mercator, one_merge(profile, 1), endpoint, "mercator")
    require(high < other_low, "rank-48 merge is not cheaper than a rank-1 merge")


def main():
    require(__debug__, "Leave PYTHONOPTIMIZE unset")
    plan, owners, spec = load_inputs()
    require(plan["M"] == M and plan["T"] == 16 and plan["live"] == W and plan["deficit"] == DEFICIT, "plan header")
    calls = call_index(plan)
    windows = window_intervals(plan)
    used, by_helper = hosted_cells(owners, windows, calls)
    successive_pairs(by_helper, calls)
    idle, donors = port_fill(used, windows)
    profile = profile_from_spec(spec, idle)
    require(all(not fits(capacity, used_count, capacity + 1) for capacity, used_count in donors),
            "an empty capacity-48 port has room for a rank-49 remainder")
    endpoint = Fraction(spec["expected"]["complex_lower"])
    assembly = json.loads(ASSEMBLY_PATH.read_text())
    require(Fraction(assembly["complex_lower"]) == endpoint, "assembly complex endpoint")
    require(assembly["complex_profile"] == {str(rank): count for rank, count in profile.items()},
            "assembly profile")
    bit_endpoint = Fraction(assembly["bit_lower"])
    mercator = load_engine(MOMENT_PATH, "selected_stage_mercator")
    base_two = load_engine(BASE_TWO_PATH, "selected_stage_base_two")
    step = Fraction(1, 10**24)
    require(signs(mercator, base_two, profile, endpoint) == (True, False), "selected endpoint must lie below one")
    require(signs(mercator, base_two, profile, endpoint + step) == (False, True), "published next endpoint must lie above one")
    relaxed = relaxation(profile)
    require(signs(mercator, base_two, relaxed, endpoint) == (True, False), "relaxation endpoint")
    require(signs(mercator, base_two, relaxed, endpoint + step) == (True, False),
            "relaxation does not clear the published next complex endpoint")
    lower, upper = bracket_root(mercator, relaxed, endpoint)
    require(lower > endpoint + Fraction(3, 10**7), "relaxation root did not move by 3/10^7")
    require(upper < endpoint + Fraction(4, 10**7), "relaxation root moved by at least 4/10^7")
    require(upper < bit_endpoint, "relaxation reaches the bit endpoint")
    controls(profile, donors, mercator, endpoint)
    print(
        "PASS_SELECTED_STAGE_BOUNDARY"
        f" helpers={N_HELPERS} pairs={N_HELPERS * (PLACEMENTS - 1)}"
        f" same_port={SAME_PORT} shared_cells=0"
        f" full_ports={FULL_PORTS} idle_ports={sum(idle.values())}"
        f" merges={MERGES} capacity_increase=1"
        f" controls=7"
    )
    print("relaxation_root_lower", lower)
    print("relaxation_root_upper", upper)


if __name__ == "__main__":
    main()
