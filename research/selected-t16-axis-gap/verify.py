#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Selected PR1094 pending-axis disjointness does not follow from role or chart checks.

The published sixteen-replica owner map and pinned phase file do satisfy the
obligation. A one-axis transplant between two idle children of one physical
family keeps every rebuilt port-basis chart legal and leaves the role audit
unchanged, while the separate X2 scan rejects it. This is not a claim that the
published map fails, and it is not the historical PR626 bridge-omission example.
"""
import gzip
import hashlib
import importlib.util
import json
import tarfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
H, M, V, T = 9, 73, 112, 16
MARKER = "PASS_SELECTED_T16_AXIS_DISJOINTNESS_GAP"

TEMPLATE = (
    "research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/"
    "vendor/pr552/complex-global/vendor535/inputs/ROUND20-PARENT-TEMPLATE.json.gz"
)
PHASES = (
    "research/community-k492-audit/pr622/replay/baseline558/complex-global/"
    "base/work/complex-nine-native/DATA-PHASES.json"
)
WORD = "research/t16-owner-audit-seed67/inputs/k8-seven-slot-word.json.gz"
OWNERS = "research/complex-t16-rare-pattern-exchanges/data/OWNERS.json.gz"
PLAN = "research/complex-t16-rare-pattern-exchanges/data/PLAN.json"
SPEC = "research/complex-t16-rare-pattern-exchanges/data/SPEC.json"
PROFILE = "research/complex-t16-rare-pattern-exchanges/PROFILE.json"
ARCHIVE = "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz"
INDEP = "research/gauge44-slots-t16/t16/indep16.py"
AUDIT = "research/gauge44-slots-t16/code/audit_allcold.py"
PINS = "research/gauge44-slots-t16/data/UPSTREAM-PINS.json"
OWNER_AUDIT = "research/t16-owner-audit-seed67/verify.py"

ARCHIVE_MEMBERS = {
    "t16/indep16.py": INDEP,
    "code/audit_allcold.py": AUDIT,
    "data/UPSTREAM-PINS.json": PINS,
}


class Gap(Exception):
    pass


def need(ok, message):
    if not ok:
        raise Gap(message)


def load_bytes(path):
    raw = path.read_bytes()
    if path.name.endswith(".gz"):
        return json.loads(gzip.decompress(raw))
    return json.loads(raw)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_pins():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    checked = 0
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        need(sha256(path) == row["sha256"], "input hash drift: " + row["path"])
        checked += 1
    need(checked == 12, "unexpected input count")
    with tarfile.open(ROOT / ARCHIVE) as archive:
        for member, loose in ARCHIVE_MEMBERS.items():
            blob = archive.extractfile(member).read()
            need(blob == (ROOT / loose).read_bytes(), "archive member drifted: " + member)
    pins = json.loads((ROOT / PINS).read_text())
    need(pins[PHASES] == sha256(ROOT / PHASES), "upstream pin is not the phase file")


def port_frame(q):
    zero = next(i for i in range(H) if (q >> i & 1) == 0)
    correction = q ^ (1 << zero)
    order = list(range(H))
    order[0], order[zero] = order[zero], order[0]
    frame = [(1 << i) ^ (correction if (correction >> i) & 1 else 0) for i in order]
    frame.extend(1 << i for i in range(H, M))
    need(len(frame) == M, "port frame width")
    for i, x in enumerate(frame):
        for j, y in enumerate(frame):
            need((x & y).bit_count() % 2 == int(i == j), "port frame is not an orthogonal basis")
    return frame


def chart(frame, pending, offset, width):
    """Predicate shared by indep16.check_roles and audit_allcold.audit.

    Both rebuild the occupied indices from the phase axes, take the first
    9-width complementary spectators, and require a permutation of all 73
    axes whose initial block is exactly that slice. Neither compares axes
    across children.
    """
    try:
        occupied = [frame.index(x) for x in pending[offset:offset + width]]
    except ValueError:
        return None
    if len(occupied) != width:
        return None
    spectators = [i for i in range(M) if i not in set(occupied)][:H - width]
    rest = [i for i in range(M) if i not in set(occupied) and i not in set(spectators)]
    permutation = occupied + spectators + rest
    if len(set(occupied + spectators)) != H or sorted(permutation) != list(range(M)):
        return None
    if [frame[i] for i in permutation[:width]] != list(pending[offset:offset + width]):
        return None
    return spectators


def axis_table(phases):
    table = []
    for port, recipe in enumerate(phases["recipes"]):
        need(recipe["port"] == port, "phase port order")
        children = []
        for child, item in enumerate(recipe["idle_children"]):
            children.append([int(x) for x in item["orthogonal_axes"]])
        table.append(children)
    return table


def occupied_cells(roles):
    cells = defaultdict(set)
    for role in roles:
        cells[(role["owner_replica"], role["child"], role["port"])].update(
            range(role["offset"], role["offset"] + role["width"]))
    return cells


def family_children(place, rank):
    grouped = defaultdict(list)
    for child, where in place.items():
        if child in rank:
            grouped[where].append(child)
    return {where: sorted(children) for where, children in grouped.items()}


def x2_failures(table, grouped, rank):
    failures = []
    checks = 0
    for where, children in sorted(grouped.items()):
        for port in range(V):
            seen = {}
            for child in children:
                checks += 1
                axes = table[port][child]
                need(len(axes) == rank[child], "axis list length")
                if len(set(axes)) != len(axes):
                    failures.append(dict(pair=where[0], side=where[1], port=port,
                                         child=child, kind="duplicate"))
                for axis in axes:
                    if axis in seen:
                        failures.append(dict(pair=where[0], side=where[1], port=port,
                                             children=[seen[axis], child], axis=axis,
                                             kind="shared"))
                    else:
                        seen[axis] = child
    return checks, failures


def collisions(table, grouped, rank, cells):
    found = []
    for owner in range(T):
        for where, children in sorted(grouped.items()):
            for port in range(V):
                seen = {}
                for child in children:
                    if child not in rank:
                        continue
                    axes = table[port][child]
                    for index in sorted(cells[(owner, child, port)]):
                        axis = axes[index]
                        if axis in seen:
                            previous = seen[axis]
                            found.append(dict(owner=owner, pair=where[0], side=where[1],
                                               port=port, axis=axis,
                                               first=dict(child=previous[0], index=previous[1]),
                                               second=dict(child=child, index=index)))
                        else:
                            seen[axis] = (child, index)
    return found


def union_occupied(cells, child, port):
    used = set()
    for owner in range(T):
        used |= cells[(owner, child, port)]
    return used


def first_transplant(table, grouped, rank, cells):
    """Copy a hosted axis into a sibling's unoccupied pending suffix.

    The target index is outside every hosted slice, so every rebuilt chart,
    spectator list and sigma is unchanged. The source index is hosted.
    """
    for where, children in sorted(grouped.items()):
        for port in range(V):
            for left in range(len(children)):
                for right in range(len(children)):
                    if left == right:
                        continue
                    child_a, child_b = children[left], children[right]
                    used_a = union_occupied(cells, child_a, port)
                    used_b = union_occupied(cells, child_b, port)
                    if not used_a or len(used_b) >= rank[child_b]:
                        continue
                    index_b = max(used_b) + 1 if used_b else 0
                    if index_b in used_b or index_b >= rank[child_b]:
                        continue
                    index_a = min(used_a)
                    donor = table[port][child_a][index_a]
                    if donor in table[port][child_b]:
                        continue
                    owners = [owner for owner in range(T) if index_a in cells[(owner, child_a, port)]]
                    return dict(pair=where[0], side=where[1], port=port,
                                source_child=child_a, source_index=index_a, axis=donor,
                                source_owners=owners, target_child=child_b,
                                target_index=index_b, replaced=table[port][child_b][index_b],
                                target_occupied_length=len(used_b), target_rank=rank[child_b])
    raise Gap("no idle-suffix transplant")


def apply_transplant(table, witness):
    mutant = [list(map(list, children)) for children in table]
    mutant[witness["port"]][witness["target_child"]][witness["target_index"]] = witness["axis"]
    return mutant


def chart_census(table, frames, roles):
    accepted = 0
    charts = {}
    for role in roles:
        pending = table[role["port"]][role["child"]]
        frame = frames[role["port"]]
        spectators = chart(frame, pending, role["offset"], role["width"])
        if spectators is None:
            continue
        occupied = tuple(frame.index(x) for x in pending[role["offset"]:role["offset"] + role["width"]])
        accepted += 1
        charts[(role["stage"], role["replica"], role["helper"])] = (occupied, tuple(spectators))
    return accepted, charts


def load_owner_audit():
    spec = importlib.util.spec_from_file_location("t16_owner_audit", ROOT / OWNER_AUDIT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    check_pins()
    phases = load_bytes(ROOT / PHASES)
    plan = load_bytes(ROOT / PLAN)
    spec = load_bytes(ROOT / SPEC)
    profile = load_bytes(ROOT / PROFILE)
    roles = load_bytes(ROOT / OWNERS)
    table = axis_table(phases)
    plan_ports = plan["provider_registry"]["gauge44"]["ports"]
    recipe_q = [recipe["q"] for recipe in phases["recipes"]]
    need(plan_ports == recipe_q, "selected plan ports differ from phase labels")
    frames = [port_frame(q) for q in recipe_q]

    audit = load_owner_audit()
    template = audit.load((ROOT / TEMPLATE).read_bytes(), TEMPLATE)
    word = audit.load((ROOT / WORD).read_bytes(), "word.json.gz")
    geometry = audit.geometry(template, phases)
    widths = audit.word_widths(word)
    local = audit.as_profile(spec["providers"]["gauge44"]["expected_profile"])
    idle = audit.as_profile(spec["expected"]["idle_remainder_profile"])
    owned = audit.audit(geometry, widths, local, roles, plan, idle, T)
    need(audit.as_profile(profile) == Counter(owned["profile"]), "profile mismatch")
    need(owned["roles"] == 69120 and owned["deficit"] == 5120 and owned["calls"] == 144,
         "selected role inventory")
    need(geometry["x2_child_ports"] == 2016, "published X2 coverage")

    grouped = family_children(geometry["place"], geometry["rank"])
    cells = occupied_cells(roles)
    checks, failures = x2_failures(table, grouped, geometry["rank"])
    need(checks == geometry["x2_child_ports"], "X2 coverage " + str(checks))
    need(failures == [], "published axes are not disjoint: " + json.dumps(failures[:3]))
    legal_hits = collisions(table, grouped, geometry["rank"], cells)
    need(legal_hits == [], "published hosted slices already share an axis")
    legal_charts, legal_routes = chart_census(table, frames, roles)
    need(legal_charts == len(roles), "published chart predicate rejected a selected role")

    witness = first_transplant(table, grouped, geometry["rank"], cells)
    need(witness == dict(pair=3, side=1, port=0, source_child=11, source_index=0,
                         axis=1 << 49, source_owners=list(range(T)), target_child=10,
                         target_index=0, replaced=13, target_occupied_length=0,
                         target_rank=48), "transplant witness moved: " + json.dumps(witness))
    mutant = apply_transplant(table, witness)
    mutant_phases = json.loads(json.dumps(phases))
    target = mutant_phases["recipes"][witness["port"]]["idle_children"][witness["target_child"]]
    target["orthogonal_axes"][witness["target_index"]] = witness["axis"]
    try:
        audit.geometry(template, mutant_phases)
    except audit.Reject as exc:
        need(str(exc).startswith("X2:"), "predecessor rejected the transplant for " + str(exc))
    else:
        raise Gap("predecessor geometry accepted the transplant")

    mutant_checks, mutant_failures = x2_failures(mutant, grouped, geometry["rank"])
    need(mutant_checks == checks, "transplant changed X2 coverage")
    need(len(mutant_failures) == 1 and mutant_failures[0]["kind"] == "shared"
         and mutant_failures[0]["axis"] == witness["axis"], "transplant failure is not the one shared axis")
    mutant_hits = collisions(mutant, grouped, geometry["rank"], cells)
    need(mutant_hits == [], "idle-suffix transplant collided inside hosted slices")
    target_used = union_occupied(cells, witness["target_child"], witness["port"])
    need(witness["target_index"] not in target_used, "target index is hosted")
    need(witness["source_index"] in union_occupied(cells, witness["source_child"], witness["port"]),
         "source index is not hosted")
    mutant_charts, mutant_routes = chart_census(mutant, frames, roles)
    need(mutant_charts == len(roles), "rebuilt chart predicate rejected the transplant")
    changed_routes = [key for key, route in mutant_routes.items() if legal_routes[key] != route]
    need(changed_routes == [], "transplant changed " + str(len(changed_routes)) + " charts")
    # The same roles still satisfy the predecessor role audit: it never reads axes.
    again = audit.audit(geometry, widths, local, roles, plan, idle, T)
    need(again == owned, "role audit changed without an axis argument")

    duplicate = [list(map(list, children)) for children in table]
    sample = next(role for role in roles if role["width"] >= 2 and role["port"] == 0 and role["child"] == 0)
    duplicate[0][0][sample["offset"] + 1] = duplicate[0][0][sample["offset"]]
    need(chart(frames[0], duplicate[0][0], sample["offset"], sample["width"]) is None,
         "duplicate-inside-slice control was accepted")
    duplicate_accepted, _ = chart_census(duplicate, frames, roles)
    need(duplicate_accepted == 69104, "duplicate control rejected an unexpected set")

    receipt = dict(
        status=MARKER,
        obligation=("Distinct positive-rank idle children of one physical family "
                    "have disjoint pending axes at every port."),
        selected_pr=1094,
        base_commit=json.loads((HERE / "SOURCES.json").read_text())["base_commit"],
        published=dict(x2_checks=checks, x2="pass", chart_roles=legal_charts,
                       occupied_axis_collisions=0, roles=owned["roles"], calls=owned["calls"],
                       deficit=owned["deficit"], cross_replica_roles=owned["cross_replica_roles"],
                       idle=owned["idle"]),
        transplant=witness,
        transplant_result=dict(x2="reject", shared_axis_failures=1,
                               occupied_axis_collisions=0,
                               rebuilt_charts_accepted=mutant_charts,
                               charts_changed=len(changed_routes),
                               source_roles_hosting_axis=len(witness["source_owners"]),
                               role_audit="accept"),
        duplicate_slice_control=dict(rejected=True, charts_still_accepted=duplicate_accepted),
        archive_chart_sources_byte_identical=True,
        not_a_published_acceptance_bug=True,
        cold_replay="not run",
        kappa_change=None,
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    try:
        main()
    except Gap as exc:
        raise SystemExit("FAIL: " + str(exc))
