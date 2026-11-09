#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Protected rank of every post-cut chart-595 departure on the selected word."""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import permutations
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/p104-helper470-twin-rung-removal/WORD.json.gz"
CUT = 13637
WORD_SHA = "7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f"
DEPARTURES = (
    (13652, 572, 603),
    (13988, 134, 618),
    (14001, 127, 637),
    (14344, 450, 711),
    (14458, 496, 729),
    (14470, 731, 737),
    (14684, 581, 766),
    (14688, 582, 767),
)
MINOR_ROWS = (120, 134, 127, 136, 135, 144, 116, 176)
MINOR_DET = Q(1, 2)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(row, other, scale):
    result = row.copy()
    for column, value in other.items():
        updated = result.get(column, Q(0)) + scale * value
        if updated:
            result[column] = updated
        else:
            result.pop(column, None)
    return result


def apply(rows, event):
    operation, target = event[:2]
    if operation in ("ADD", "COPY"):
        old = rows[target] if operation == "ADD" else {}
        rows[target] = add(old, rows[event[2]], Q(event[3]))
    elif operation == "SCALE":
        factor = Q(event[2])
        rows[target] = {i: factor * value for i, value in rows[target].items() if factor * value}
    elif operation in ("INIT", "CLEAR"):
        rows[target] = {}
    else:
        need(operation == "MOVE", "known scalar opcode")


def load_word():
    pin = next(row for row in json.loads((HERE / "SOURCES.json").read_text())["files"]
               if row["path"] == WORD)
    raw = (ROOT / WORD).read_bytes()
    need(sha256(raw).hexdigest() == pin["sha256"] == WORD_SHA, "selected word SHA256")
    word = json.loads(gzip.decompress(raw))
    need(word["public"] == 770 and word["owned_fields"] == 29, "word dimensions")
    need(len(word["program"]) == 22803, "word length")
    need(word["program"][CUT] == ["COPY", 778, 572, "1", 595], "helper-572 cut")
    return word


def charts_at(word):
    charts = word["initial"] + [None] * word["owned_fields"]
    illegal = 0
    departures = []
    entries_603 = []
    clears_595 = []
    for index, event in enumerate(word["program"]):
        operation = event[0]
        if operation in ("ADD", "COPY", "SCALE"):
            if charts[event[1]] != event[-1]:
                illegal += 1
            if operation in ("ADD", "COPY") and charts[event[2]] != event[-1]:
                illegal += 1
        if index > CUT and operation == "MOVE" and event[2] == 595:
            departures.append((index, event[1], event[3]))
        if operation == "MOVE" and event[3] == 603:
            entries_603.append((index, event[1], event[2]))
        elif operation == "INIT" and event[2] == 603:
            entries_603.append((index, event[1], None))
        if operation == "INIT":
            charts[event[1]] = event[2]
        elif operation == "MOVE":
            charts[event[1]] = event[3]
        elif operation == "CLEAR":
            if index > CUT and charts[event[1]] == 595:
                clears_595.append((index, event[1]))
            charts[event[1]] = None
    occupied = tuple(i for i, chart in enumerate(charts) if chart == 595)
    return illegal, tuple(departures), tuple(entries_603), tuple(clears_595), occupied


def suffix_columns(word):
    size = word["public"] + word["owned_fields"]
    columns = []
    for index, field, _destination in DEPARTURES:
        rows = [{} for _ in range(size)]
        rows[field] = {0: Q(1)}
        for event in word["program"][index + 1:]:
            apply(rows, event)
        columns.append({row: rows[row][0] for row in range(word["public"]) if 0 in rows[row]})
    return columns


def elimination_rank(matrix, width):
    rows = [list(row) for row in matrix]
    rank = 0
    for column in range(width):
        pivot = next((row for row in range(rank, len(rows)) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for row in range(len(rows)):
            if row != rank and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [left - factor * right for left, right in zip(rows[row], rows[rank])]
        rank += 1
    return rank


def gaussian_det(matrix):
    rows = [list(row) for row in matrix]
    sign, determinant = 1, Q(1)
    for column in range(len(rows)):
        pivot = next(row for row in range(column, len(rows)) if rows[row][column])
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            sign = -sign
        determinant *= rows[column][column]
        for row in range(column + 1, len(rows)):
            if rows[row][column]:
                factor = rows[row][column] / rows[column][column]
                rows[row] = [left - factor * right for left, right in zip(rows[row], rows[column])]
    return sign * determinant


def leibniz_det(matrix):
    size = len(matrix)
    total = Q(0)
    for order in permutations(range(size)):
        value = Q(1)
        for row, column in enumerate(order):
            value *= matrix[row][column]
        inversions = sum(order[i] > order[j] for i in range(size) for j in range(i + 1, size))
        total += (-1 if inversions % 2 else 1) * value
    return total


def certify(word):
    illegal, departures, entries, clears, occupied = charts_at(word)
    need(illegal == 0, "every scalar operation stays inside one chart")
    need(departures == DEPARTURES, "eight post-cut departures from chart 595")
    need(clears == ((13656, 778),), "the only post-cut chart-595 clear is field 778")
    need(occupied == (), "chart 595 is empty at the end of the word")
    need(entries == ((13652, 572, 595), (13655, 709, 597), (13658, 778, None)),
         "chart 603 has one chart-595 entrant")
    need(word["program"][13656] == ["CLEAR", 778, 595], "owned 778 is cleared inside chart 595")
    anchor = word["final"][572]
    columns = suffix_columns(word)
    protected = sorted({row for column in columns for row in column if word["final"][row] != anchor})
    minor = [[columns[j].get(row, Q(0)) for j in range(8)] for row in MINOR_ROWS]
    need(all(word["final"][row] != anchor for row in MINOR_ROWS), "minor rows are protected")
    gaussian = gaussian_det(minor)
    leibniz = leibniz_det(minor)
    need(gaussian == leibniz == MINOR_DET, "independent determinants agree")
    full = [[columns[j].get(row, Q(0)) for j in range(8)] for row in protected]
    need(elimination_rank(full, 8) == 8, "all protected rows have rank 8")
    return {"departures": [list(item) for item in DEPARTURES],
            "protected_outputs": len(protected), "minor_rows": list(MINOR_ROWS),
            "minor_det": str(MINOR_DET), "chart_603_entries": 3,
            "scalar_chart_mismatches": illegal}


def controls(word):
    columns = suffix_columns(word)
    minor = [[columns[j].get(row, Q(0)) for j in range(8)] for row in MINOR_ROWS]
    changed = [row[:] for row in minor]
    changed[0][0] = -changed[0][0]
    need(gaussian_det(changed) != MINOR_DET, "sign flip changes the minor")
    for dropped in range(8):
        reduced = [[columns[j].get(row, Q(0)) for j in range(8) if j != dropped] for row in MINOR_ROWS]
        need(elimination_rank(reduced, 7) == 7, "each departure is necessary for rank 8")
    mutated = json.loads(json.dumps(word))
    mutated["program"][14688][3] = 603
    _illegal, departures, _entries, _clears, _occupied = charts_at(mutated)
    need(departures != DEPARTURES, "a second move into chart 603 is rejected")
    return {"sign_flip": True, "leave_one_out_rank_7": 8, "mutated_route_rejected": True}


def main():
    word = load_word()
    result = certify(word)
    result["controls"] = controls(word)
    result["status"] = "PASS_P104_CHART595_DEPARTURE_RANK"
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
