#!/usr/bin/env python3
"""Audit the retained PR309 retiming51 predecessor pin for 249-states.json.

The inherited-base replay already stopped on this raw file hash. This checker
does not rerun that native replay. It recomputes newline and key-order
variants of the retained states, and compares them with the retained
rank-modular cohort files whose pins do match after LF-to-CRLF conversion.
"""
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "research/community-reconciliation-third100-audit"
FINAL = AUDIT / "regenerated/pr309-disk-retry-outputs/base-replay/rank-modular-replay/final"
TARGET_STATES = "208cc9aba1401423ca31a3305a2d2bc9e1778d78323c000bed425f0bf21518d4"
ACTUAL_STATES = "3348648d9f659ed8c842f9b573ca7da66108a7966268e44d29caebd71bc32781"
SEMANTIC = "7ad5dc8fe4a0d415b4a332381f1391c5bdaecd1ae92e95a1bae9b879b8251163"


def need(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_gz(path):
    return gzip.decompress(path.read_bytes())


def crlf(data):
    need(b"\r" not in data, "input already contains CR: " + str(data[:20]))
    return data.replace(b"\n", b"\r\n")


def pretty(obj):
    return (json.dumps(obj, indent=2) + "\n").encode()


def norm_replay(document):
    """Same normalization as retiming51/compose.py at PR309 head aeb4808."""
    need("inherited_receipt" not in document, "conflicting inherited receipt key")
    document = dict(document)
    document.pop("scope", None)
    document.pop("source_initial_scope", None)
    keys = [key for key in ("inherited_admitted_receipt", "inherited_predecessor_receipt") if key in document]
    need(len(keys) == 1, "expected one inherited receipt alias")
    document["inherited_receipt"] = document.pop(keys[0])
    return document


def nonlexical_dicts(value, path=""):
    found = []
    if isinstance(value, dict):
        if list(value) != sorted(value):
            found.append(path or "<root>")
        for key, child in value.items():
            found.extend(nonlexical_dicts(child, (path + "." + key) if path else key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            if isinstance(child, (dict, list)):
                found.extend(nonlexical_dicts(child, "%s[%d]" % (path, index)))
    return found


def main():
    need(sys.version_info >= (3, 11), "Python 3.11+ required")
    diagnostic = json.loads((AUDIT / "PR309-DIAGNOSTIC.json").read_text())
    pin = json.loads(load_gz(AUDIT / "PR309-RETIMING51-PIN.json.gz"))
    raw = load_gz(AUDIT / "PR309-ACTUAL-STATES.json.gz")
    states = json.loads(raw)
    need(sha256(raw) == ACTUAL_STATES == diagnostic["actual_states_sha256"], "actual states pin drifted")
    need(pin["predecessor"]["249-states.json"] == TARGET_STATES, "expected states pin drifted")
    need(TARGET_STATES != ACTUAL_STATES, "mismatch fixture collapsed")
    need(sha256(crlf(raw)) != TARGET_STATES, "CRLF of the retained states unexpectedly matches the pin")
    need(pretty(states) == raw, "retained states are not indent-2 JSON with one trailing LF")

    lexical = json.loads(raw)
    lexical["initial"] = dict(sorted(lexical["initial"].items()))
    need(sha256(pretty(lexical)) != TARGET_STATES, "lexical initial unexpectedly matches")
    need(sha256(crlf(pretty(lexical))) != TARGET_STATES, "CRLF lexical initial unexpectedly matches")
    numeric = json.loads(json.dumps(states, sort_keys=True))
    need(sha256(pretty(numeric)) != TARGET_STATES, "sort_keys states unexpectedly match")
    need(sha256(crlf(pretty(numeric))) != TARGET_STATES, "CRLF sort_keys states unexpectedly match")
    need(nonlexical_dicts(states) == ["initial"], "unexpected non-lexical object")

    cohort = {}
    for name in ("COHORT249-FINAL.json", "COHORT249-INITIAL.json", "COHORT249-FRAMES.json"):
        payload = load_gz(FINAL / (name + ".gz"))
        need(payload.count(b"\n") == 1 and b"\r" not in payload, name + " is not one-line LF JSON")
        need(sha256(payload) != pin["predecessor"][name], name + " LF unexpectedly equals the Windows pin")
        need(sha256(crlf(payload)) == pin["predecessor"][name], name + " is not the pin after LF-to-CRLF")
        mutated = bytearray(payload)
        mutated[10] ^= 1
        need(sha256(crlf(bytes(mutated))) != pin["predecessor"][name], "mutated " + name + " still matched")
        cohort[name] = json.loads(payload)
    need(states["final"] == cohort["COHORT249-FINAL.json"], "embedded final differs from the matching cohort file")

    initial = cohort["COHORT249-INITIAL.json"]
    need(list(initial) == sorted(initial), "cohort initial is not lexical")
    need(list(states["initial"]) == sorted(states["initial"], key=int), "states initial is not numeric")
    diffs = [key for key in states["initial"] if states["initial"][key] != initial[key]]
    zero = states["ZERO"]
    need(len(diffs) == 1915, "expected 1915 initial disagreements, got %d" % len(diffs))
    need(all(states["initial"][key] == zero for key in diffs), "a disagreement is not ZERO on the states side")
    need(all(initial[key] != zero for key in diffs), "a disagreement is ZERO on the cohort side")
    need(len({initial[key] for key in diffs}) == 1915, "cohort replacement frames are not unique")
    spliced = json.loads(raw)
    spliced["initial"] = dict(sorted(initial.items(), key=lambda item: int(item[0])))
    need(sha256(pretty(spliced)) != TARGET_STATES, "numeric cohort initial unexpectedly matches the pin")
    need(sha256(crlf(pretty(spliced))) != TARGET_STATES, "CRLF numeric cohort initial unexpectedly matches")
    broken = json.loads(raw)
    broken["initial"][diffs[0]] = initial[diffs[0]]
    broken_diffs = [key for key in broken["initial"] if broken["initial"][key] != initial[key]]
    need(len(broken_diffs) == 1914, "single-value failure control did not change the count")

    replay_raw = load_gz(FINAL / "COHORT249-REPLAY.json.gz")
    replay = json.loads(replay_raw)
    semantic = sha256(json.dumps(norm_replay(replay), sort_keys=True, separators=(",", ":")).encode())
    need(semantic == SEMANTIC == pin["predecessor_replay_semantic_sha256"], "semantic replay digest drifted")
    need(replay["new_gauges"] == 1915 == replay["actual_kernel_gauges"], "gauge count is not 1915")
    need(sha256(replay_raw) != pin["predecessor"].get("COHORT249-REPLAY.json", semantic), "replay file was raw-pinned")

    rows = json.loads((AUDIT / "FILESYSTEM-COMPRESSION.json").read_text())
    by_path = {row["path"]: row for row in rows}
    retimed = by_path["base-replay/kernel-replay/retimed/249-states.json"]
    final = by_path["base-replay/kernel-replay/final/249-states.json"]
    need(retimed["sha256"] == ACTUAL_STATES and retimed["bytes"] == len(raw) == 5825276, "retimed states record differs")
    need(final["sha256"] != ACTUAL_STATES and final["bytes"] == len(raw), "final states record is not an equal-length different digest")
    need(diagnostic["binary_word_matches"] is True, "diagnostic binary agreement changed")
    for row in diagnostic["comparison"]:
        if row["path"] == "249-states.json":
            need(row["lf_to_crlf_matches"] is False and row["expected"] == TARGET_STATES, "diagnostic states row changed")
        elif row["path"] in ("COHORT249-FINAL.json", "COHORT249-INITIAL.json", "COHORT249-FRAMES.json"):
            need(row["lf_to_crlf_matches"] is True, "diagnostic cohort row changed")

    print(json.dumps({
        "status": "PASS_PR309_STATES_PIN_NEWLINE_AND_INITIAL_AUDIT",
        "actual_states_sha256": ACTUAL_STATES,
        "pinned_states_sha256": TARGET_STATES,
        "states_crlf_matches_pin": False,
        "lexical_and_sort_keys_match_pin": False,
        "cohort_files_match_pin_after_crlf": ["COHORT249-FINAL.json", "COHORT249-INITIAL.json", "COHORT249-FRAMES.json"],
        "initial_disagreements": 1915,
        "states_side_of_each_disagreement": "ZERO",
        "semantic_replay_sha256": semantic,
        "new_gauges": 1915,
        "kernel_retimed_states_sha256": retimed["sha256"],
        "kernel_final_states_sha256": final["sha256"],
        "kappa_change": None,
        "native_replay_rerun": False,
    }, indent=2))


if __name__ == "__main__":
    main()
