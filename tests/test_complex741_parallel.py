"""Concurrent scheduling of the pinned #741 complex replay.

The driver runs the unchanged stage commands of research/complex-sw4-frame8/verify.py.
These tests check the scheduler, the stage table against verify.py, and the
schedule against the recorded per-stage file accesses.
"""
from pathlib import Path
import json
import shutil
import sys
import tempfile
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import verify_complex741_parallel as par

VERIFY = ROOT / 'research/complex-sw4-frame8/verify.py'
ACCESS = ROOT / 'research/complex741-parallel-replay/ACCESS.json'


class Graph(unittest.TestCase):
    def timed(self, log, fail=()):
        lock = threading.Lock()
        def job(name):
            with lock:
                log[name] = [time.monotonic(), None]
            time.sleep(0.2)
            if name in fail:
                raise RuntimeError(name + ' failed')
            with lock:
                log[name][1] = time.monotonic()
            return name
        return job

    def test_dependent_starts_after_prerequisite_ends(self):
        log = {}
        out = par.run_graph(['a', 'b'], {'a': (), 'b': ('a',)}, self.timed(log), workers=4)
        self.assertEqual(out, {'a': 'a', 'b': 'b'})
        self.assertGreaterEqual(log['b'][0], log['a'][1])

    def test_independent_jobs_overlap(self):
        log = {}
        par.run_graph(['a', 'b'], {'a': (), 'b': ()}, self.timed(log), workers=2)
        self.assertLess(max(s for s, _ in log.values()), min(e for _, e in log.values()))

    def test_failure_stops_dependents_and_reraises(self):
        log = {}
        with self.assertRaisesRegex(RuntimeError, 'a failed'):
            par.run_graph(['a', 'b', 'c'], {'a': (), 'b': ('a',), 'c': ()},
                          self.timed(log, fail={'a'}), workers=2)
        self.assertNotIn('b', log)
        self.assertIsNotNone(log['c'][1])  # a running sibling finishes before the error propagates

    def test_unknown_or_later_dependency_rejected(self):
        with self.assertRaises(AssertionError):
            par.run_graph(['a', 'b'], {'a': ('b',), 'b': ()}, lambda n: n, workers=1)


class Schedule(unittest.TestCase):
    def test_stage_table_matches_verify_py(self):
        self.assertEqual(par.stage_names(VERIFY.read_text(encoding='utf-8')), list(par.STAGE_DEPS))

    def test_verify_py_is_the_pinned_file(self):
        par.check_pin(VERIFY)

    def test_changed_verify_py_refused(self):
        with tempfile.TemporaryDirectory() as d:
            copy = Path(d) / 'verify.py'
            copy.write_bytes(VERIFY.read_bytes() + b'\n')
            with self.assertRaises(SystemExit):
                par.check_pin(copy)

    def test_every_recorded_access_conflict_is_ordered(self):
        access = json.loads(ACCESS.read_text(encoding='utf-8'))
        self.assertEqual(access['verify_sha256'], par.VERIFY_SHA256)
        self.assertEqual(set(access['stages']), set(par.STAGE_DEPS) | set(par.DEFERRED_DEPS))
        self.assertEqual(access['outside_work_writes'], {})
        self.assertEqual(par.conflicts(dict(par.STAGE_DEPS, **par.DEFERRED_DEPS), access['stages']), [])

    def test_dropping_a_needed_edge_is_detected(self):
        access = json.loads(ACCESS.read_text(encoding='utf-8'))['stages']
        deps = dict(par.STAGE_DEPS)
        deps['inherited-cold-controls'] = ()
        found = par.conflicts(deps, access)
        self.assertTrue(any('inherited-cold-controls' in pair[:2] for pair in found), found)

    def test_listing_a_directory_conflicts_with_writes_inside_it(self):
        access = {'a': {'w': ['out/x.json']}, 'b': {'ls': ['out']}}
        self.assertEqual(par.conflicts({'a': (), 'b': ()}, access), [('a', 'b', 'out/x.json')])
        self.assertEqual(par.conflicts({'a': (), 'b': ('a',)}, access), [])

    def test_creating_a_directory_conflicts_only_with_listing_its_parent(self):
        both = {'a': {'mkdir': ['out/d']}, 'b': {'mkdir': ['out/d'], 'w': ['out/d/f']}}
        self.assertEqual(par.conflicts({'a': (), 'b': ()}, both), [])
        lister = {'a': {'mkdir': ['out/d']}, 'b': {'ls': ['out']}}
        self.assertEqual(par.conflicts({'a': (), 'b': ()}, lister), [('a', 'b', 'out/d')])

    def test_stage_commands_follow_verify_py(self):
        cmds = par.stage_commands(VERIFY.read_text(encoding='utf-8'), VERIFY.parent, Path('/w'))
        self.assertEqual(list(cmds), list(par.STAGE_DEPS))
        self.assertEqual(cmds['inherited-cold-controls'][1:],
                         [str(Path('/w/frames/FULL-WORD.json.gz')),
                          str(VERIFY.parent / 'vendor/main/research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'),
                          str(Path('/w/cold-controls'))])


class Compare(unittest.TestCase):
    def tree(self, root, seconds, value):
        import gzip, hashlib
        (root / 'local').mkdir(parents=True)
        (root / 'local/W.json.gz').write_bytes(gzip.compress(b'{"w": 1}', mtime=seconds))
        stages = json.dumps([{'name': 's', 'seconds': seconds}]).encode()
        (root / 'STAGES.json').write_bytes(stages)
        (root / 'RESULT.json').write_text(json.dumps({'kappa': value, 'seconds': seconds}))
        (root / 'RECEIPT.json').write_text(json.dumps({'artifacts': {
            'STAGES.json': hashlib.sha256(stages).hexdigest(),
            'RESULT.json': hashlib.sha256((root / 'RESULT.json').read_bytes()).hexdigest()}}))

    def compare(self, value_b):
        sys.path.insert(0, str(ROOT / 'research/complex741-parallel-replay'))
        import compare_replays
        with tempfile.TemporaryDirectory() as d:
            self.tree(Path(d, 'a'), 1, '1/2')
            self.tree(Path(d, 'b'), 2, value_b)
            return compare_replays.compare(Path(d, 'a'), Path(d, 'b'))

    def test_timing_and_gzip_header_differences_are_accepted(self):
        r = self.compare('1/2')
        self.assertEqual(r['other'], {})
        self.assertEqual(r['identical_payload'], 1)
        self.assertEqual(sorted(r['accepted']), ['RECEIPT.json', 'RESULT.json', 'STAGES.json'])

    def test_value_change_and_its_digest_are_rejected(self):
        r = self.compare('1/3')
        self.assertEqual(r['other'], {'RECEIPT.json': ['/artifacts/RESULT.json'], 'RESULT.json': ['/kappa']})

    def pair(self, left, right):
        import json
        sys.path.insert(0, str(ROOT / 'research/complex741-parallel-replay'))
        import compare_replays
        with tempfile.TemporaryDirectory() as d:
            for name, value in (('a', left), ('b', right)):
                Path(d, name).mkdir()
                Path(d, name, 'R.json').write_text(json.dumps(value), encoding='utf-8')
            return compare_replays.compare(Path(d, 'a'), Path(d, 'b'))

    def test_numeric_root_and_stage_timing_stay_accepted(self):
        self.assertEqual(self.pair({'kappa': '1/2', 'seconds': 1},
                                   {'kappa': '1/2', 'seconds': 2.5})['other'], {})
        self.assertEqual(self.pair({'stages': [{'seconds': 0, 'exit_code': 0}]},
                                   {'stages': [{'seconds': 3, 'exit_code': 0}]})['other'], {})
        self.assertEqual(self.pair([{'name': 's', 'elapsed_seconds': 1}],
                                   [{'name': 's', 'elapsed_seconds': 2}])['other'], {})

    def test_nested_proof_and_non_numeric_timing_are_rejected(self):
        hidden = self.pair({'seconds': {'kappa': '1/2', 'wall': 1.0}},
                           {'seconds': {'kappa': '1/3', 'wall': 2.0}})
        self.assertEqual(hidden['other'], {'R.json': ['/seconds/kappa', '/seconds/wall']})
        replaced = self.pair({'kappa': '1/2', 'seconds': 1.0},
                             {'kappa': '1/2', 'seconds': {'kappa': '9/10'}})
        self.assertEqual(replaced['other'], {'R.json': ['/seconds']})
        nested = self.pair({'additional_evidence': {'seconds': 1, 'rank': 4}},
                           {'additional_evidence': {'seconds': 7, 'rank': 4}})
        self.assertEqual(nested['other'], {'R.json': ['/additional_evidence/seconds']})
        inserted = self.pair({'rank': 4}, {'rank': 4, 'seconds': 7})
        self.assertEqual(inserted['other'], {'R.json': ['/seconds']})
        for bad in (True, False, '1', float('nan'), -1):
            report = self.pair({'seconds': 1.5}, {'seconds': bad})
            self.assertEqual(report['other'], {'R.json': ['/seconds']}, bad)

    def test_timing_only_digest_is_accepted_and_hidden_kappa_digest_is_not(self):
        import hashlib
        import json
        sys.path.insert(0, str(ROOT / 'research/complex741-parallel-replay'))
        import compare_replays

        def trees(left_obj, right_obj):
            left_raw = json.dumps(left_obj).encode()
            right_raw = json.dumps(right_obj).encode()
            with tempfile.TemporaryDirectory() as d:
                for name, obj, raw in (('a', left_obj, left_raw), ('b', right_obj, right_raw)):
                    root = Path(d, name)
                    root.mkdir()
                    (root / 'R.json').write_bytes(raw)
                    (root / 'D.json').write_text(json.dumps({
                        'log_sha256': hashlib.sha256(raw).hexdigest()}), encoding='utf-8')
                return compare_replays.compare(Path(d, 'a'), Path(d, 'b'))

        timing = trees({'kappa': '1/2', 'seconds': 1}, {'kappa': '1/2', 'seconds': 2})
        self.assertEqual(timing['other'], {})
        self.assertEqual(sorted(timing['accepted']), ['D.json', 'R.json'])
        hidden = trees({'seconds': {'kappa': '1/2'}}, {'seconds': {'kappa': '1/3'}})
        self.assertEqual(set(hidden['other']), {'D.json', 'R.json'})
        self.assertIn('/seconds/kappa', hidden['other']['R.json'])

    def logs(self, a, b):
        import compare_replays
        with tempfile.TemporaryDirectory() as d:
            for name, text in (('a', a), ('b', b)):
                Path(d, name).mkdir()
                Path(d, name, 's.log').write_text(text)
            return compare_replays.compare(Path(d, 'a'), Path(d, 'b'))

    def test_log_elapsed_time_accepted_but_integer_change_rejected(self):
        sys.path.insert(0, str(ROOT / 'research/complex741-parallel-replay'))
        self.assertEqual(self.logs('PASS emit 2.922\nrows 504\n', 'PASS emit 3.219\nrows 504\n')['logs'], {'s.log': 1})
        self.assertEqual(self.logs('rows 504 0.1\n', 'rows 505 0.2\n')['other'], {'s.log': ['rows 504 0.1 | rows 505 0.2']})
        self.assertEqual(self.logs('a\n', 'a\nb\n')['other'], {'s.log': 'line counts differ'})
        self.assertEqual(self.logs('h ' + 'a' * 64 + '\n', 'h ' + 'b' * 64 + '\n')['other'], {'s.log': ['h ' + 'a' * 64 + ' | h ' + 'b' * 64]})


if __name__ == '__main__':
    unittest.main()
