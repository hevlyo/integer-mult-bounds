"""Differential checks for content-addressed reconciliation tree OIDs."""
import hashlib
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import git_tree_oid as trees


def blob_id(payload):
    return trees.git_oid('blob', payload)


class TreeOidTests(unittest.TestCase):
    def test_empty_tree_matches_the_git_constant(self):
        empty = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
        self.assertEqual(trees.predecessor_tree_oid([]), empty)
        self.assertEqual(trees.compute_tree_oid([]), empty)

    def test_file_and_directory_order_matches_predecessor(self):
        first = blob_id(b'one')
        second = blob_id(b'two')
        nested = blob_id(b'nested')
        files = [
            {'path': 'z.txt', 'mode': '100644', 'blob': first},
            {'path': 'dir/a.txt', 'mode': '100755', 'blob': nested},
            {'path': 'a.txt', 'mode': '100644', 'blob': second},
        ]
        self.assertEqual(trees.compute_tree_oid(files), trees.predecessor_tree_oid(files))

    def test_cache_hit_reuses_the_oid_and_a_dependency_change_misses(self):
        files = [
            {'path': 'src/a.py', 'mode': '100644', 'blob': blob_id(b'a')},
            {'path': 'src/b.py', 'mode': '100644', 'blob': blob_id(b'b')},
        ]
        cache = {}
        original = trees.tree_oid(files, cache)
        self.assertEqual(trees.tree_oid(files, cache), original)
        self.assertEqual(len(cache), 1)
        changed = [dict(files[0], blob=blob_id(b'a-changed')), files[1]]
        self.assertNotIn(trees.listing_key(changed), cache)
        updated = trees.tree_oid(changed, cache)
        self.assertNotEqual(updated, original)
        self.assertEqual(updated, trees.predecessor_tree_oid(changed))
        mode_changed = [dict(files[0], mode='100755'), files[1]]
        self.assertNotEqual(trees.tree_oid(mode_changed, {}), original)

    def test_poisoned_cache_fails_audit_and_disagrees_with_the_fresh_oid(self):
        files = [{'path': 'a.txt', 'mode': '100644', 'blob': blob_id(b'a')}]
        cache = {trees.listing_key(files): '0' * 40}
        self.assertEqual(trees.tree_oid(files, cache), '0' * 40)
        with self.assertRaisesRegex(ValueError, 'Stale tree cache'):
            trees.tree_oid(files, cache, audit=True)
        self.assertNotEqual(trees.compute_tree_oid(files), '0' * 40)

    def test_unsafe_duplicate_and_mode_inputs_are_rejected(self):
        good = {'path': 'a.txt', 'mode': '100644', 'blob': blob_id(b'a')}
        for path in ('/etc/passwd', 'a/../b', 'a//b', 'a/./b', 'a/', '..', ''):
            bad = dict(good, path=path)
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    trees.predecessor_tree_oid([bad])
                with self.assertRaises(ValueError):
                    trees.compute_tree_oid([bad])
        with self.assertRaisesRegex(ValueError, 'Duplicate source path'):
            trees.compute_tree_oid([good, dict(good)])
        with self.assertRaisesRegex(ValueError, 'Duplicate source path'):
            trees.predecessor_tree_oid([good, dict(good)])
        with self.assertRaisesRegex(ValueError, 'Unexpected source mode'):
            trees.compute_tree_oid([dict(good, mode='120000')])
        with self.assertRaisesRegex(ValueError, 'Unexpected source mode'):
            trees.predecessor_tree_oid([dict(good, mode='120000')])

    def test_file_and_directory_collision_fails_closed(self):
        blob = blob_id(b'x')
        files = [
            {'path': 'a', 'mode': '100644', 'blob': blob},
            {'path': 'a/b', 'mode': '100644', 'blob': blob},
        ]
        with self.assertRaises(TypeError):
            trees.predecessor_tree_oid(files)
        with self.assertRaisesRegex(ValueError, 'Unsafe source path'):
            trees.compute_tree_oid(files)

    def test_repeated_listing_is_faster_than_the_predecessor(self):
        files = [
            {'path': f'dir{i // 20}/file{i}.txt', 'mode': '100644', 'blob': format(i, '040x')}
            for i in range(2000)
        ]
        self.assertEqual(trees.compute_tree_oid(files), trees.predecessor_tree_oid(files))
        cache = {}
        started = time.perf_counter()
        for _ in range(12):
            trees.predecessor_tree_oid(files)
        predecessor = time.perf_counter() - started
        started = time.perf_counter()
        for _ in range(12):
            trees.tree_oid(files, cache)
        cached = time.perf_counter() - started
        self.assertLess(cached * 2, predecessor, f'cached {cached:.4f}s predecessor {predecessor:.4f}s')

    def test_backslash_component_matches_predecessor(self):
        files = [{'path': 'a\\b', 'mode': '100644', 'blob': blob_id(b'q')}]
        self.assertEqual(trees.compute_tree_oid(files), trees.predecessor_tree_oid(files))


if __name__ == '__main__':
    unittest.main()
