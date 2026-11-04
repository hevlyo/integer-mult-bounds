#!/usr/bin/env python3
"""Replay content-addressed Git tree OIDs against the pinned reconciliation trees.

The predecessor algorithm is taken from the base commit, not from the working
tree. Every pinned commit tree, and every CI checkout tree in the next-100 and
third-100 audits, must match both that predecessor and the cached walk. A
one-blob change and a poisoned cache must fail. The three integrated verifiers
are then run unchanged, which keeps their other evidence checks.
"""
import ast
import gzip
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import git_tree_oid as trees

PACKAGE = Path(__file__).resolve().parent
BASE = json.loads((PACKAGE / 'SOURCES.json').read_text())['base_commit']
PREDECESSORS = {
    'research/community-reconciliation92-audit/verify.py':
        '883b190529c1cd786d0f29cae0a9d55f3499df8916c474c49c2b3c6418d6f20c',
    'research/community-reconciliation-next100-audit/verify.py':
        '8c4cd88abb5cf541bff66e42b0e32c3b3ab5cbdd58b35082b831af0dc8dff521',
    'research/community-reconciliation-third100-audit/verify.py':
        'c23e644bc13809e007b920a81f4af7e6dcd1e4c6e54bd4b1d94ec001353f01b7',
}
AUDITS = (
    ('research/community-reconciliation92-audit', False),
    ('research/community-reconciliation-next100-audit', True),
    ('research/community-reconciliation-third100-audit', True),
)


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def git_show(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)


def predecessor_tree_oid():
    segments = []
    signature = None
    for path, digest in PREDECESSORS.items():
        source = git_show(path)
        require(hashlib.sha256(source).hexdigest() == digest, 'predecessor verifier bytes changed: ' + path)
        text = source.decode()
        module = ast.parse(text)
        found = [node for node in module.body
                 if isinstance(node, ast.FunctionDef) and node.name in ('require', 'oid', 'tree_oid')]
        require([node.name for node in found] == ['require', 'oid', 'tree_oid'],
                'predecessor tree functions moved: ' + path)
        body = '\n\n'.join(ast.get_source_segment(text, node) for node in found)
        current = hashlib.sha256(body.encode()).hexdigest()
        if signature is None:
            signature = current
        require(current == signature, 'predecessor tree_oid differs across audits: ' + path)
        segments.append(body)
    namespace = {}
    exec('import hashlib\nfrom pathlib import PurePosixPath\n\n' + segments[0], namespace)
    return namespace['tree_oid']


def load_gz(path):
    return json.loads(gzip.decompress((ROOT / path).read_bytes()))


def listings():
    rows = []
    for folder, include_ci in AUDITS:
        source = load_gz(folder + '/SOURCES.json.gz')
        for pull in source['pull_requests']:
            rows.append((folder, pull['number'], pull['files'], pull['tree']))
        if not include_ci:
            continue
        for row in load_gz(folder + '/CI-SOURCE-CONTEXT.json.gz'):
            require(not row.get('error'), f'{folder} CI row {row.get("number")} has an error')
            tree = row['checkout_tree']
            require(not tree.get('truncated'), f'{folder} CI tree truncated')
            files = [{'path': item['path'], 'mode': item['mode'], 'blob': item['sha']}
                     for item in tree['tree'] if item['type'] == 'blob']
            rows.append((folder, row['number'], files, tree['sha']))
    return rows


def stage_times(rows, original):
    started = time.perf_counter()
    for _folder, _number, files, pinned in rows:
        require(original(files) == pinned, 'predecessor disagrees with pinned tree')
    predecessor = time.perf_counter() - started
    cache = {}
    started = time.perf_counter()
    for _folder, _number, files, pinned in rows:
        require(trees.tree_oid(files, cache) == pinned, 'cached tree OID disagrees with pin')
    cached = time.perf_counter() - started
    return predecessor, cached, len(cache)


def failure_controls(rows):
    _folder, _number, files, pinned = rows[0]
    cache = {}
    original = trees.tree_oid(files, cache)
    require(original == pinned, 'control listing does not match its pin')
    mutated = [dict(item) for item in files]
    mutated[0] = dict(mutated[0], blob='0' * 40 if mutated[0]['blob'] != '0' * 40 else '1' * 40)
    require(trees.listing_key(mutated) not in cache, 'changed blob reused the old cache key')
    changed = trees.tree_oid(mutated, cache)
    require(changed != original and changed != pinned, 'changed blob kept the pinned tree OID')
    poison = {trees.listing_key(files): '0' * 40}
    require(trees.tree_oid(files, poison) != pinned, 'poisoned cache still matched the pin')
    try:
        trees.tree_oid(files, poison, audit=True)
    except ValueError as exc:
        require('Stale tree cache' in str(exc), 'audit rejected the cache for a different reason')
    else:
        raise SystemExit('poisoned cache survived audit')


def integrated_verifiers():
    started = time.perf_counter()
    for folder, _include_ci in AUDITS:
        manifest = json.loads((ROOT / folder / 'MANIFEST.json').read_text())
        verify = ROOT / folder / 'verify.py'
        digest = hashlib.sha256(verify.read_bytes()).hexdigest()
        require(manifest['files']['verify.py'] == digest, 'integrated verifier is not the manifest pin: ' + folder)
        result = subprocess.run([sys.executable, '-B', str(verify)], cwd=ROOT, capture_output=True, text=True)
        require(result.returncode == 0, result.stderr[-500:] or result.stdout[-500:])
        require(result.stdout.strip().endswith('no theorem claim'), 'integrated verifier lost its scope line')
    return time.perf_counter() - started


def main():
    require(not sys.flags.optimize, 'assertions and explicit checks must stay enabled')
    original = predecessor_tree_oid()
    rows = listings()
    predecessor, cached, unique = stage_times(rows, original)
    require(predecessor > 0 and cached * 2 < predecessor,
            f'stage speedup below 2x: predecessor {predecessor:.3f}s cached {cached:.3f}s')
    failure_controls(rows)
    full = integrated_verifiers()
    print(
        'PASS_TREE_OID_REUSE '
        f'listings={len(rows)} unique={unique} '
        f'predecessor_s={predecessor:.3f} cached_s={cached:.3f} '
        f'ratio={predecessor / cached:.2f} integrated_verifiers_s={full:.3f}'
    )


if __name__ == '__main__':
    main()
