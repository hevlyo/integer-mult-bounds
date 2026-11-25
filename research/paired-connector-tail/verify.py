#!/usr/bin/env python3
"""Paired omission of the unread final source toggle in three pinned connector schedules.

The schedules are Ross Richardson's certificate in
research/universal-connector-boundary/CERTIFICATE.json. This checker imports
none of that package. It uses the standard library only.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "research/universal-connector-boundary/CERTIFICATE.json"
NAMES = ("four_all", "five_extra_source", "five_extra_output")
PUBLISHED_QUERIES = {
    "four_all": 38,
    "five_extra_source": 74,
    "five_extra_output": 74,
}


def need(condition, message):
    if not condition:
        raise SystemExit(message)


def load_certificate():
    data = json.loads(CERTIFICATE.read_text())
    need(data.get("schema") == "universal-connector-boundary-v1", "unexpected certificate schema")
    need(data.get("base") == "91a2094f2e022930069e8cfdc810a3ea1b81cd09", "unexpected certificate base")
    schedules = data["schedules"]
    need(set(NAMES) <= set(schedules), "missing pinned schedule")
    return {name: schedules[name] for name in NAMES}


def fresh(sources, rows, offset):
    state = {f"x{j}": {(f"x{j}",)} for j in range(sources)}
    state["z"] = {("z",)}
    for i in range(rows):
        state[f"y{offset + i}"] = {(f"y{offset + i}",)}
    return state


def apply_word(state, word, offset):
    for kind, index in word:
        if kind == "B":
            coefficient, source, target = f"B{index}", f"x{index}", "z"
        else:
            coefficient = f"A{offset + index}"
            source, target = "z", f"y{offset + index}"
        state[target].symmetric_difference_update(
            {(coefficient,) + term for term in state[source]}
        )
    return state


def outputs_match(state, masks, offset):
    for i, mask in enumerate(masks):
        terms = {(f"y{offset + i}",)}
        for j in range(mask.bit_length()):
            if mask >> j & 1:
                terms.add((f"A{offset + i}", f"B{j}", f"x{j}"))
        if state[f"y{offset + i}"] != terms:
            return False
    return True


def sources_fixed(state, sources):
    return all(state[f"x{j}"] == {(f"x{j}",)} for j in range(sources))


def connector_extra(state):
    return state["z"] - {("z",)}


def readout_slots(word):
    slots = []
    seen = 0
    for kind, index in word:
        if kind == "B":
            seen += 1
        else:
            slots.append(seen)
    return slots


def prepare(item):
    word = item["word"]
    source_word = item["source_word"]
    sources = item["sources"]
    masks = item["rows"]
    need(item["queries"] == PUBLISHED_QUERIES[item["name"]] == len(word), "published query count moved")
    need(word[-1][0] == "B", "schedule does not end on a source toggle")
    need([index for kind, index in word if kind == "B"] == source_word, "source projection mismatch")
    recorded = sorted(slot for group in item["readout_slots"] for slot in group)
    need(sorted(readout_slots(word)) == recorded, "readout slots do not match the word")
    used = {slot for group in item["readout_slots"] for slot in group}
    need(len(source_word) not in used, "final boundary is a readout; it is not a pure restoration")
    last = word[-1][1]
    need(source_word.count(last) % 2 == 0, "final source label is not an even restoration")
    need(all(0 <= mask < (1 << sources) and mask != 0 for mask in masks), "mask out of range")
    short = word[:-1]
    return word, short, last


def run_batch(sources, masks, word, offset):
    state = fresh(sources, len(masks), offset)
    apply_word(state, word, offset)
    return state


def check_schedule(item):
    word, short, last = prepare(item)
    sources, masks = item["sources"], item["rows"]
    full = run_batch(sources, masks, word, 0)
    need(outputs_match(full, masks, 0), "published word misses an output")
    need(sources_fixed(full, sources) and not connector_extra(full), "published word does not restore")
    one = run_batch(sources, masks, short, 0)
    leftover = {(f"B{last}", f"x{last}")}
    need(outputs_match(one, masks, 0), "dropping the final toggle changes outputs")
    need(sources_fixed(one, sources) and connector_extra(one) == leftover, "final toggle is not exactly one connector term")
    # Two shortened batches, disjoint outputs, one shared connector.
    pair = fresh(sources, len(masks), 0)
    for i in range(len(masks)):
        pair[f"y{100 + i}"] = {(f"y{100 + i}",)}
    apply_word(pair, short, 0)
    need(connector_extra(pair) == leftover, "first short exit is not the named leftover")
    apply_word(pair, short, 100)
    need(outputs_match(pair, masks, 0) and outputs_match(pair, masks, 100), "paired outputs failed")
    need(sources_fixed(pair, sources) and not connector_extra(pair), "paired shorts do not restore the connector")
    # Reversal of the successful pair must restore the initial state.
    backward = {role: set(terms) for role, terms in pair.items()}
    apply_word(backward, list(reversed(short)), 100)
    apply_word(backward, list(reversed(short)), 0)
    initial = fresh(sources, len(masks), 0)
    for i in range(len(masks)):
        initial[f"y{100 + i}"] = {(f"y{100 + i}",)}
    need(backward == initial, "paired word is not invertible by reversal")
    # The next restored batch preserves the leftover; it does not clear it.
    kept = fresh(sources, len(masks), 0)
    for i in range(len(masks)):
        kept[f"y{100 + i}"] = {(f"y{100 + i}",)}
    apply_word(kept, short, 0)
    apply_word(kept, word, 100)
    need(outputs_match(kept, masks, 100), "restored successor outputs failed")
    need(connector_extra(kept) == leftover, "a restored successor cleared the leftover")
    # Three shorts have odd total parity, so the connector stays dirty.
    triple = run_batch(sources, masks, short, 0)
    apply_word(triple, short, 0)
    apply_word(triple, short, 0)
    need(connector_extra(triple) == leftover, "three shorts unexpectedly restored the connector")
    # Deleting an earlier call is not the same omission.
    broken = run_batch(sources, masks, word[1:], 0)
    need(not outputs_match(broken, masks, 0), "dropping the first call still covered every mask")
    return {
        "last_source": last,
        "published_queries": len(word),
        "pair_queries": 2 * len(short),
        "saved_queries": 2,
    }


def check_cross(schedules):
    four = schedules["four_all"]
    five = schedules["five_extra_source"]
    _, four_short, four_last = prepare(four)
    _, five_short, five_last = prepare(five)
    need(four_last != five_last, "the two tails are the same source; the cross control is vacuous")
    state = fresh(5, len(four["rows"]), 0)
    for i in range(len(five["rows"])):
        state[f"y{100 + i}"] = {(f"y{100 + i}",)}
    apply_word(state, four_short, 0)
    apply_word(state, five_short, 100)
    need(connector_extra(state) == {(f"B{four_last}", f"x{four_last}"), (f"B{five_last}", f"x{five_last}")},
         "unlike tails cancelled each other")


def main():
    schedules = load_certificate()
    for name, item in schedules.items():
        item["name"] = name
    reports = {name: check_schedule(item) for name, item in schedules.items()}
    check_cross(schedules)
    need(all(row["saved_queries"] == 2 for row in reports.values()), "saving is not two queries")
    need(reports["four_all"]["pair_queries"] == 74, "four-source pair cost moved")
    need(reports["five_extra_source"]["pair_queries"] == 146, "five-source pair cost moved")
    need(reports["five_extra_output"]["pair_queries"] == 146, "five-source output-repair pair cost moved")
    print(
        "PASS_PAIRED_CONNECTOR_TAIL"
        f" schedules=3 saved_per_pair=2"
        f" four_pair_queries={reports['four_all']['pair_queries']}"
        f" five_pair_queries={reports['five_extra_source']['pair_queries']}"
        f" tails={[reports[name]['last_source'] for name in NAMES]}"
    )


if __name__ == "__main__":
    main()
