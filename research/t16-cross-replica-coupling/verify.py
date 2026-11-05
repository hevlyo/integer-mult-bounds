#!/usr/bin/env python3
"""Restoration and non-interleaving are separately necessary for no coupling.

The selected T16 owner audit admits a pinned cross-replica role. Four exact
add schedules, in the seven-slot word's gate encoding, separate the two
hypotheses in the inherited cross-group hosting sentence. The owner record
does not contain those schedules, and narrowing the role's width is still
rejected. No new kappa is claimed.

Standard library only. Reads pinned inputs and writes nothing.
"""
import gzip
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent

CLAIM = (
    "A hosted helper may use a family belonging to the other group. This relies on\n"
    "the existing whole-invocation interface: the hash-bound local supplier and its\n"
    "normalization wrappers restore arbitrary initial helper contents after each\n"
    "complete invocation. The scheduler does not interleave operations inside a\n"
    "local invocation. At its boundaries, the borrowed family therefore has the\n"
    "same contents it had before the borrow. This is why a cross-group helper\n"
    "assignment does not introduce a new scalar coupling between the two data\n"
    "controllers.\n"
)

# Registers in the scalar projection: borrowed family coordinate, helper
# scratch, and the lender's later accumulator. These ids are local to the
# projection. They are not helper 0's registers in the seven-slot word.
X, H, Y = 0, 1, 2

NO_BORROW = [["add", Y, X, 1, 1, []]]
WORK = [
    ["add", H, X, 1, 1, []],
    ["add", X, H, 1, 1, []],
]
RESTORE = [
    ["add", X, H, -1, 1, []],
    ["add", H, X, -1, 1, []],
]
ATOMIC = WORK + RESTORE + NO_BORROW
OMIT_RESTORE = WORK + NO_BORROW
INTERLEAVE = WORK + NO_BORROW + RESTORE
PRIVATE = [
    ["add", H, X, 1, 1, []],
    ["add", H, X, -1, 1, []],
] + NO_BORROW

# Hand images of (x, h, y) = (3, -5, 7). The executor must match these
# literals; they were expanded from the gate list, not from the executor.
HAND = {
    "no_borrow": (3, -5, 10),
    "atomic": (3, -5, 10),
    "omit_restore": (1, -2, 8),
    "interleave": (3, -5, 8),
    "private": (3, -5, 10),
}


def fail(message):
    raise SystemExit("FAIL_T16_CROSS_REPLICA_COUPLING: " + message)


def read_bytes(path):
    return (ROOT / path).read_bytes()


def read_json(path):
    raw = read_bytes(path)
    if path.endswith(".gz"):
        raw = gzip.decompress(raw)
    return json.loads(raw)


def load_auditor():
    path = ROOT / "research/t16-owner-audit-seed67/verify.py"
    spec = importlib.util.spec_from_file_location("t16_owner_audit", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_pins():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    pinned = [row for row in sources["files"] if row["usage"] == "input"]
    if len(pinned) != 8:
        fail("expected eight live inputs")
    for row in pinned:
        digest = hashlib.sha256(read_bytes(row["path"])).hexdigest()
        if digest != row["sha256"]:
            fail("working input drift: " + row["path"])
    proof = read_bytes("research/complex-double-replica-owners/PROOF.md").decode()
    if proof.count(CLAIM) != 1:
        fail("cross-group no-coupling sentence is not the pinned paragraph")
    return sources["base_commit"]


def apply_gate(state, gate):
    if not isinstance(gate, list) or not gate or not isinstance(gate[-1], list):
        fail("gate encoding")
    op = gate[0]
    if op == "add":
        if len(gate) != 6:
            fail("add encoding")
        _, target, source, numerator, denominator, _frame = gate
        if source == target or numerator == 0:
            raise ValueError("add operands")
    elif op == "scale":
        if len(gate) != 5:
            fail("scale encoding")
        _, target, numerator, denominator, _frame = gate
        source = None
        if numerator == 0:
            raise ValueError("scale operands")
    else:
        raise ValueError("opcode")
    if not isinstance(denominator, int) or denominator <= 0 or denominator & (denominator - 1):
        raise ValueError("denominator")
    if not isinstance(numerator, int):
        raise ValueError("numerator")
    image = list(state)
    if op == "add":
        image[target] += Fraction(numerator, denominator) * state[source]
    else:
        image[target] *= Fraction(numerator, denominator)
    return tuple(image)


def run(gates, state):
    for gate in gates:
        state = apply_gate(state, gate)
    return state


def matrix(gates):
    columns = []
    for index in range(3):
        basis = tuple(Fraction(int(i == index)) for i in range(3))
        columns.append(run(gates, basis))
    return columns


def image(columns, state):
    return tuple(sum(state[i] * columns[i][row] for i in range(3)) for row in range(3))


def as_ints(values):
    out = []
    for value in values:
        if value.denominator != 1:
            fail("non-integral reported image")
        out.append(int(value))
    return out


def check_schedules():
    schedules = {
        "no_borrow": NO_BORROW,
        "atomic": ATOMIC,
        "omit_restore": OMIT_RESTORE,
        "interleave": INTERLEAVE,
        "private": PRIVATE,
    }
    columns = {name: matrix(gates) for name, gates in schedules.items()}
    dirty = (Fraction(3), Fraction(-5), Fraction(7))
    for name, expected in HAND.items():
        direct = run(schedules[name], dirty)
        linear = image(columns[name], dirty)
        if direct != linear or direct != tuple(Fraction(v) for v in expected):
            fail(name + " image")
    if columns["atomic"] != columns["no_borrow"] or columns["private"] != columns["no_borrow"]:
        fail("atomic or private round-trip coupled")
    if columns["omit_restore"] == columns["no_borrow"]:
        fail("omitted cleanup was invisible")
    if columns["interleave"] == columns["no_borrow"]:
        fail("mid-borrow read was invisible")
    # Final borrowed coordinate and helper scratch match the input on every
    # basis vector. The lender accumulator does not.
    for vector in columns["interleave"]:
        if (vector[X], vector[H]) not in ((1, 0), (0, 1), (0, 0)):
            fail("interleaving did not restore the borrowed state")
    if (columns["interleave"][X][Y], columns["interleave"][H][Y]) == (1, 0):
        fail("interleaving left the lender image unchanged")
    framed = [list(gate) for gate in ATOMIC]
    framed[0][-1] = [256]
    if matrix(framed) != columns["atomic"]:
        fail("frame annotation changed the scalar projection")
    half = [list(gate) for gate in ATOMIC]
    half[2][3] = -1
    half[2][4] = 2
    if matrix(half) == columns["no_borrow"]:
        fail("half-coefficient cleanup compared equal")
    for bad in (["add", X, H, 1, 3, []], ["add", X, X, 1, 1, []], ["add", X, H, 0, 1, []], ["scale", X, -1, 6, []]):
        try:
            apply_gate((Fraction(1), Fraction(1), Fraction(0)), bad)
        except ValueError:
            continue
        fail("illegal gate was accepted: " + str(bad))
    scale_restore = [["scale", X, -1, 2, []], ["scale", X, -2, 1, []]] + NO_BORROW
    scale_once = [["scale", X, -1, 2, []]] + NO_BORROW
    if matrix(scale_restore) != columns["no_borrow"] or matrix(scale_once) == columns["no_borrow"]:
        fail("scale round-trip control")
    word = read_json("research/t16-owner-audit-seed67/inputs/k8-seven-slot-word.json.gz")
    if word["A"][0] != ["add", 499, 498, 1, 1, []]:
        fail("add encoding pin")
    if word["precondition"][0] != ["scale", 174, -1, 2, []]:
        fail("scale encoding pin")
    restoring = 0
    for section in ("A", "B", "cleanup"):
        restoring += sum(gate[0] == "add" and gate[3] < 0 and gate[4] == 1 for gate in word[section])
    if restoring <= 0:
        fail("the pinned word has no attested restoring add")
    return {
        "hand_image": {name: list(value) for name, value in HAND.items()},
        "omit_basis_image": [as_ints(column) for column in columns["omit_restore"]],
        "interleave_basis_image": [as_ints(column) for column in columns["interleave"]],
        "attested_negative_unit_adds": restoring,
    }


def check_owner(auditor):
    template = read_json(auditor.TEMPLATE)
    phases = read_json(auditor.PHASES)
    word = read_json("research/t16-owner-audit-seed67/inputs/k8-seven-slot-word.json.gz")
    geometry = auditor.geometry(template, phases)
    widths = auditor.word_widths(word)
    local = auditor.as_profile(word["report"]["local_profile"])
    spec = read_json("research/complex-t16-rare-pattern-exchanges/data/SPEC.json")
    plan = read_json("research/complex-t16-rare-pattern-exchanges/data/PLAN.json")
    roles = read_json("research/complex-t16-rare-pattern-exchanges/data/OWNERS.json.gz")
    expected = spec["expected"]
    idle = auditor.as_profile(expected["idle_remainder_profile"])
    owned = auditor.audit(geometry, widths, local, roles, plan, idle, 16)
    if owned["roles"] != 69120 or owned["cross_replica_roles"] != 57480:
        fail("owner census")
    if owned["deficit"] != 5120 or owned["rank_mass"] != 1041408 or owned["calls"] != 144:
        fail("owner price inputs")
    if owned["profile"] != {int(k): v for k, v in expected["global_profile"].items()}:
        fail("owner profile")
    if widths[0] != 9:
        fail("helper 0 width")
    role = roles[0]
    expected_role = {
        "child": 4,
        "copy": 1582,
        "family": 13006,
        "helper": 0,
        "offset": 0,
        "owner_replica": 14,
        "port": 14,
        "replica": 0,
        "stage": 0,
        "time": 0,
        "width": 9,
    }
    if role != expected_role:
        fail("pinned cross-replica role")
    window = plan["windows"]["14,4"]
    if window[0] != 32 or role["time"] not in window[1] or len(window[1]) != 92:
        fail("pinned role window")
    source = Path(auditor.__file__).read_text()
    audit_source = source.split("def audit(", 1)[1].split("\ndef as_profile(", 1)[0]
    if any(token in audit_source for token in ("'add'", '"add"', "numerator", "cleanup", "precondition")):
        fail("owner audit started reading scalar gates")
    mutant = [dict(item) for item in roles]
    mutant[0]["width"] = 8
    try:
        auditor.audit(geometry, widths, local, mutant, plan, idle, 16)
    except auditor.Reject as exc:
        if not str(exc).startswith("R2:"):
            fail("narrowed width rejected by " + str(exc))
    else:
        fail("narrowed width was admitted")
    return {
        "role": expected_role,
        "window_rank": 32,
        "window_times": 92,
        "owner": {key: owned[key] for key in ("roles", "cross_replica_roles", "calls", "windows", "deficit", "rank_mass")},
        "idle": owned["idle"],
    }


def main():
    if sys.flags.optimize:
        fail("run with PYTHONOPTIMIZE unset")
    base = check_pins()
    schedules = check_schedules()
    owner = check_owner(load_auditor())
    result = {
        "status": "PASS_T16_CROSS_REPLICA_COUPLING",
        "base_commit": base,
        "proposition": "atomic restoration and no internal lender read imply the no-borrow image; each hypothesis is necessary",
        "kappa": "unchanged",
        "schedules": schedules,
        "owner": owner,
        "not_checked": [
            "selected frontier cold replay",
            "helper 0's real cleanup on family 13006",
            "all-size compiler, precision, tape and analytic transfer",
            "fifteen production controller mutations",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print(result["status"])


if __name__ == "__main__":
    main()
