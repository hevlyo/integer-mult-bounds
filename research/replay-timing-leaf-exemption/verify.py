#!/usr/bin/env python3
"""Compare the pinned #741 replay comparator with the working timing exemption.

No kappa change and no selected-frontier replay. The predecessor module is loaded
from the pinned git blob. The working module is the file in this checkout.
"""
import gzip
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PREDECESSOR = 'research/complex741-parallel-replay/compare_replays.py'
MARKER = 'PASS_REPLAY_TIMING_LEAF_EXEMPTION'


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def load_blob(commit, path, name):
    source = subprocess.check_output(['git', 'show', f'{commit}:{path}'], cwd=ROOT)
    module = types.ModuleType(name)
    module.__file__ = f'{path}@{commit}'
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    return module


def load_live():
    path = ROOT / PREDECESSOR
    spec = importlib.util.spec_from_file_location('compare_replays_live', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_tree(root, files):
    root.mkdir(parents=True)
    for rel, kind, payload in files:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if kind == 'json':
            path.write_text(json.dumps(payload), encoding='utf-8')
        elif kind == 'gz':
            raw, mtime = payload
            path.write_bytes(gzip.compress(raw, mtime=mtime))
        else:
            raise SystemExit('unknown fixture kind')


def compare(module, left, right):
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        write_tree(base / 'a', left)
        write_tree(base / 'b', right)
        return module.compare(base / 'a', base / 'b')


def main():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text(encoding='utf-8'))
    row = next(item for item in sources['files'] if item['path'] == PREDECESSOR)
    blob = subprocess.check_output(
        ['git', 'rev-parse', f"{sources['base_commit']}:{PREDECESSOR}"], cwd=ROOT, text=True).strip()
    data = subprocess.check_output(['git', 'show', f"{sources['base_commit']}:{PREDECESSOR}"], cwd=ROOT)
    require(blob == row['git_blob'] and hashlib.sha256(data).hexdigest() == row['sha256'],
            'predecessor pin does not match the base commit')
    require(hashlib.sha256((ROOT / PREDECESSOR).read_bytes()).hexdigest() != row['sha256'],
            'working comparator is still the predecessor bytes')
    old = load_blob(sources['base_commit'], PREDECESSOR, 'compare_replays_predecessor')
    live = load_live()
    require(not hasattr(old, 'timing_leaf'), 'predecessor unexpectedly has the repaired predicate')
    require(live.timing_leaf('/seconds', 0, 2.5), 'root timing')
    require(live.timing_leaf('/stages/0/elapsed_seconds', 1, 4), 'stage timing')
    require(not live.timing_leaf('/seconds/kappa', '1/2', '1/3'), 'nested proof leaf')
    require(not live.timing_leaf('/additional_evidence/seconds', 1, 7), 'object-nested seconds')
    require(not live.timing_leaf('/seconds', True, False), 'boolean timing')
    require(not live.timing_leaf('/seconds', float('nan'), 1.0), 'non-finite timing')
    require(not live.timing_leaf('/seconds', -1, 1), 'negative timing')
    require(not live.timing_leaf('/seconds', None, 7), 'inserted timing key')

    hidden_left = [('R.json', 'json', {'seconds': {'kappa': '1/2', 'wall': 1.0}})]
    hidden_right = [('R.json', 'json', {'seconds': {'kappa': '1/3', 'wall': 2.0}})]
    old_hidden = compare(old, hidden_left, hidden_right)
    live_hidden = compare(live, hidden_left, hidden_right)
    require(old_hidden['other'] == {}, 'predecessor did not omit /seconds/kappa')
    require(live_hidden['other'] == {'R.json': ['/seconds/kappa', '/seconds/wall']},
            'working comparator did not reject the nested proof leaves')

    nested_left = [('R.json', 'json', {'additional_evidence': {'seconds': 1, 'rank': 4}})]
    nested_right = [('R.json', 'json', {'additional_evidence': {'seconds': 7, 'rank': 4}})]
    require(compare(old, nested_left, nested_right)['other'] == {},
            'predecessor did not omit additional_evidence.seconds')
    require(compare(live, nested_left, nested_right)['other'] ==
            {'R.json': ['/additional_evidence/seconds']},
            'working comparator did not reject object-nested seconds')

    for label, right_value in (('bool', True), ('string', '1'), ('nan', float('nan')),
                               ('negative', -1), ('object', {'kappa': '9/10'})):
        left = [('R.json', 'json', {'kappa': '1/2', 'seconds': 1.5})]
        right = [('R.json', 'json', {'kappa': '1/2', 'seconds': right_value})]
        require(compare(old, left, right)['other'] == {}, 'predecessor rejected ' + label)
        require(compare(live, left, right)['other'] == {'R.json': ['/seconds']},
                'working comparator accepted ' + label)

    timing_left = [('R.json', 'json', {'kappa': '1/2', 'seconds': 1, 'stages': [{'seconds': 0, 'exit_code': 0}]})]
    timing_right = [('R.json', 'json', {'kappa': '1/2', 'seconds': 2.5, 'stages': [{'seconds': 3, 'exit_code': 0}]})]
    timing = compare(live, timing_left, timing_right)
    require(timing['other'] == {} and timing['accepted']['R.json'] == ['/seconds', '/stages/0/seconds'],
            'legitimate timing was rejected')
    require(compare(live, [('R.json', 'json', [{'elapsed_seconds': 1, 'exit_code': 0}])],
                    [('R.json', 'json', [{'elapsed_seconds': 2, 'exit_code': 0}])])['other'] == {},
            'stage-list elapsed_seconds was rejected')
    require(compare(live, [('R.json', 'json', [{'seconds': 1, 'exit_code': 0}])],
                    [('R.json', 'json', [{'seconds': 2, 'exit_code': 1}])])['other'] ==
            {'R.json': ['/0/exit_code']}, 'exit_code change was exempted')

    raw = b'{"w": 1}'
    gzip_report = compare(live, [('W.json.gz', 'gz', (raw, 1))], [('W.json.gz', 'gz', (raw, 2))])
    require(gzip_report['other'] == {} and gzip_report['identical_payload'] == 1
            and gzip_report['identical_bytes'] == 0, 'gzip header difference was not payload-equal')

    def digest_case(module, left_obj, right_obj):
        left_raw = json.dumps(left_obj).encode()
        right_raw = json.dumps(right_obj).encode()
        left = [('R.json', 'json', left_obj),
                ('D.json', 'json', {'log_sha256': hashlib.sha256(left_raw).hexdigest()})]
        right = [('R.json', 'json', right_obj),
                 ('D.json', 'json', {'log_sha256': hashlib.sha256(right_raw).hexdigest()})]
        return compare(module, left, right)

    accepted_digest = digest_case(live, {'kappa': '1/2', 'seconds': 1}, {'kappa': '1/2', 'seconds': 2})
    require(accepted_digest['other'] == {} and set(accepted_digest['accepted']) == {'D.json', 'R.json'},
            'digest of a timing-only file was rejected')
    rejected_digest = digest_case(live, {'seconds': {'kappa': '1/2'}}, {'seconds': {'kappa': '1/3'}})
    require(set(rejected_digest['other']) == {'D.json', 'R.json'},
            'digest of a hidden kappa change was accepted')
    print(MARKER)


if __name__ == '__main__':
    main()
