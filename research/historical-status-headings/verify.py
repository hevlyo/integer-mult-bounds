#!/usr/bin/env python3
"""Check the two repaired historical headings in docs/research/current-status.md.

The opening section stays the live selected record. The blocks after the #1042
and #942 historical dividers must cite the checkpoint whose decimal equals the
stated kappa. Superseded sections later in the file are outside this check.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "docs/research/current-status.md"
SELECTED = ROOT / "certificates/selected-result.json"
CHECKPOINTS = {
    "1042": ROOT / "certificates/checkpoints/frontier1042.json",
    "942": ROOT / "certificates/checkpoints/frontier942.json",
}
LIVE_LINK = "../../certificates/selected-result.json"
CHECKPOINT_LINK = {
    "1042": "../../certificates/checkpoints/frontier1042.json",
    "942": "../../certificates/checkpoints/frontier942.json",
}
HEADING = re.compile(r"^# (.+)$", re.M)
DECIMAL = re.compile(r"\*\*(?:κ=)?([0-9]+\.[0-9]+)\*\*")


def sections(text):
    matches = list(HEADING.finditer(text))
    parsed = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        parsed.append((match.group(1).strip(), text[match.end():end]))
    return parsed


def first_decimal(body):
    match = DECIMAL.search(body)
    return None if match is None else match.group(1)


def check(text, selected_decimal, checkpoint_decimals):
    errors = []
    parsed = sections(text)
    titles = [title for title, _ in parsed]
    current = [title for title in titles if title == "Current reviewed status"]
    if current != ["Current reviewed status"] or not titles or titles[0] != "Current reviewed status":
        errors.append(
            "expected the first heading, and only that heading, to be Current reviewed status; found %s"
            % current
        )
    else:
        opening = parsed[0][1]
        got = first_decimal(opening)
        if got != selected_decimal:
            errors.append("opening decimal %s != selected %s" % (got, selected_decimal))
        if LIVE_LINK not in opening:
            errors.append("opening section missing the live selected-record link")
    for label, divider, title in (
        ("1042", "Historical status through #1042", "Historical reviewed status at #1042"),
        ("942", "Historical status through #942", "Historical reviewed status at #942"),
    ):
        if titles.count(divider) != 1 or titles.count(title) != 1:
            errors.append("expected one %s divider and one %s heading" % (divider, title))
            continue
        if titles[titles.index(divider) + 1] != title:
            errors.append("the section after %s is not %s" % (divider, title))
        body = parsed[titles.index(title)][1]
        expected = checkpoint_decimals[label]
        got = first_decimal(body)
        if got != expected:
            errors.append("%s decimal %s != checkpoint %s" % (label, got, expected))
        if expected == selected_decimal:
            errors.append("%s checkpoint decimal equals the live selected decimal" % label)
        if CHECKPOINT_LINK[label] not in body:
            errors.append("%s section missing %s" % (label, CHECKPOINT_LINK[label]))
        if LIVE_LINK in body:
            errors.append("%s section still links the live selected record" % label)
    return errors


def main():
    text = STATUS.read_text()
    selected_decimal = json.loads(SELECTED.read_text())["decimal"]
    checkpoint_decimals = {
        label: json.loads(path.read_text())["decimal"] for label, path in CHECKPOINTS.items()
    }
    errors = check(text, selected_decimal, checkpoint_decimals)
    if errors:
        print("FAIL")
        print("\n".join(errors))
        return 1

    restored_headings = text.replace(
        "# Historical reviewed status at #1042", "# Current reviewed status", 1
    ).replace("# Historical reviewed status at #942", "# Current reviewed status", 1)
    heading_errors = check(restored_headings, selected_decimal, checkpoint_decimals)
    if not any("only that heading" in item for item in heading_errors):
        print("FAIL restored current headings were accepted")
        print(heading_errors)
        return 1

    restored_links = text.replace(CHECKPOINT_LINK["1042"], LIVE_LINK, 1).replace(
        CHECKPOINT_LINK["942"], LIVE_LINK, 1
    )
    link_errors = check(restored_links, selected_decimal, checkpoint_decimals)
    if not any("still links the live selected record" in item for item in link_errors):
        print("FAIL restored live selected-record links were accepted")
        print(link_errors)
        return 1

    swapped = (
        text.replace(CHECKPOINT_LINK["1042"], "TEMP_LINK", 1)
        .replace(CHECKPOINT_LINK["942"], CHECKPOINT_LINK["1042"], 1)
        .replace("TEMP_LINK", CHECKPOINT_LINK["942"], 1)
    )
    if not check(swapped, selected_decimal, checkpoint_decimals):
        print("FAIL swapped checkpoint links were accepted")
        return 1

    mutated = text.replace(checkpoint_decimals["1042"], selected_decimal, 1)
    mutation_errors = check(mutated, selected_decimal, checkpoint_decimals)
    if not any(item.startswith("1042 decimal") for item in mutation_errors):
        print("FAIL #1042 prose-decimal mutation was accepted")
        print(mutation_errors)
        return 1

    print("PASS_HISTORICAL_CURRENT_STATUS_HEADINGS")
    print("selected_decimal=%s" % selected_decimal)
    print("checkpoint_1042=%s" % checkpoint_decimals["1042"])
    print("checkpoint_942=%s" % checkpoint_decimals["942"])
    print("heading_rejections=%d" % len(heading_errors))
    print("link_rejections=%d" % len(link_errors))
    print("decimal_mutation_rejections=%d" % len(mutation_errors))
    return 0


if __name__ == "__main__":
    sys.exit(main())
