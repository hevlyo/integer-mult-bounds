#!/usr/bin/env python3
"""Check the joint-reclaim parse copy: pins, unchanged kappa, and the test module.

The module's mutation matrix is the retained coverage. A shared-list write is
the negative control, and it lives in the module so this replay executes it.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if sys.flags.optimize:
        raise SystemExit('Assertions must remain enabled')
    test_path = ROOT / 'tests/test_joint_reclaim.py'
    test = test_path.read_text()
    if 'deepcopy(' in test:
        raise SystemExit('test_joint_reclaim.py still calls deepcopy')
    if 'def independent_word' not in test or 'test_parsed_copy_does_not_alias_pinned_words' not in test:
        raise SystemExit('cached parse copy or alias control is missing')
    source = json.loads((ROOT / 'research/joint-dual/SOURCE.json').read_text())
    for name in (
            'tests/test_joint_reclaim.py',
            'certificates/joint-dual-word-23.json.gz',
            'certificates/joint-dual-word-25.json.gz'):
        if source['files'][name] != digest(ROOT / name):
            raise SystemExit('joint-dual source pin mismatch: ' + name)
    kappa = json.loads((ROOT / 'certificates/joint-dual-kappa.json').read_text())
    if kappa['source_manifest_sha256'] != digest(ROOT / 'research/joint-dual/SOURCE.json'):
        raise SystemExit('kappa manifest hash does not match SOURCE.json')
    if str(kappa['kappa']) != '4764513337/100000000000000':
        raise SystemExit('conditional kappa changed')
    command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests',
               '-p', 'test_joint_reclaim.py', '-v']
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit('joint-reclaim tests failed')
    print('PASS_JOINT_RECLAIM_PARSE_COPY')


if __name__ == '__main__':
    main()
