#!/usr/bin/env python3
"""Audit one canonical identity for fields it never reads.

The selected generated-artifact identity hashes seven provider files. It
excludes only the root ``seconds`` field of ``CLIFFORD-REVIEW.json``. The
sibling receipt ``SCALAR-FRAME-AUDIT.json`` is not in that map, so a change
to its scalar-operation count leaves every returned identity unchanged.

This does not edit the identity, rerun a supplier, or change kappa.
Standard library only. Refuses to run with assertions disabled.
"""
import gzip
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IDENTITY_PATH = ROOT / 'research/complex-sw4-frame8/code/generated_identity.py'
REPLAY = ROOT / 'research/community-k492-audit/pr626/replay/mixed-global/base/providers'
PROVIDERS = ('ck', 'jp8')
PROOF_FIELDS = (
    'scalar_operations',
    'local_profile',
    'local_rank_mass',
    'widths',
    'hyperplane_ended_helpers',
    'canonical_content_sha256',
)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_identity():
    spec = importlib.util.spec_from_file_location('selected_generated_identity', IDENTITY_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path):
    raw = path.read_bytes()
    if path.suffix == '.gz':
        raw = gzip.decompress(raw)
    return json.loads(raw)


def contains_key(value, key):
    if isinstance(value, dict):
        return key in value or any(contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(contains_key(item, key) for item in value)
    return False


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def copy_provider(source):
    temporary = Path(tempfile.mkdtemp(prefix='scalar-audit-identity-'))
    destination = temporary / source.name
    shutil.copytree(source, destination)
    return temporary, destination


def identities_of(module, directory):
    return module.artifact_identities(directory)


def main():
    require(sys.flags.optimize == 0 and __debug__, 'PYTHONOPTIMIZE must be unset so identity assertions stay enabled')
    module = load_identity()
    require(module.FILES == (
        'CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json',
        'INDEPENDENT-LOCAL-REPLAY.json', 'CLIFFORD-RECIPES.json',
        'CLIFFORD-REVIEW.json', 'RESIDUAL-ADAPTERS.json'),
        'Selected identity file list changed')
    require('SCALAR-FRAME-AUDIT.json' not in module.FILES, 'Scalar audit unexpectedly entered the identity list')

    reports = []
    for name in PROVIDERS:
        directory = REPLAY / name
        audit_path = directory / 'SCALAR-FRAME-AUDIT.json'
        audit = read_json(audit_path)
        require(set(PROOF_FIELDS) <= set(audit) and 'seconds' in audit, name + ' scalar audit is missing a named field')
        require(isinstance(audit['scalar_operations'], int), name + ' scalar_operations is not an integer')
        mass = sum(int(rank) * count for rank, count in audit['local_profile'].items())
        require(mass == audit['local_rank_mass'], name + ' local_rank_mass is not the profile mass')
        for sibling in directory.iterdir():
            if sibling.name == 'SCALAR-FRAME-AUDIT.json' or sibling.suffix not in {'.json', '.gz'}:
                continue
            require(not contains_key(read_json(sibling), 'scalar_operations'),
                    name + ' stores scalar_operations outside the scalar audit: ' + sibling.name)

        baseline = identities_of(module, directory)
        require(set(baseline) == set(module.FILES), name + ' identity map has unexpected keys')
        require('SCALAR-FRAME-AUDIT.json' not in baseline, name + ' identity reads the scalar audit')

        scratch, copied = copy_provider(directory)
        try:
            changed = read_json(copied / 'SCALAR-FRAME-AUDIT.json')
            changed['scalar_operations'] += 1
            write_json(copied / 'SCALAR-FRAME-AUDIT.json', changed)
            require(digest((copied / 'SCALAR-FRAME-AUDIT.json').read_bytes()) != digest(audit_path.read_bytes()),
                    name + ' scalar mutation did not change the file')
            require(identities_of(module, copied) == baseline,
                    name + ' scalar_operations change moved a canonical identity')
        finally:
            shutil.rmtree(scratch)

        scratch, copied = copy_provider(directory)
        try:
            changed = read_json(copied / 'SCALAR-FRAME-AUDIT.json')
            changed['seconds'] = float(changed['seconds']) + 1.0
            write_json(copied / 'SCALAR-FRAME-AUDIT.json', changed)
            require(identities_of(module, copied) == baseline,
                    name + ' scalar-audit seconds change moved a canonical identity')
        finally:
            shutil.rmtree(scratch)

        scratch, copied = copy_provider(directory)
        try:
            phase = read_json(copied / 'CLIFFORD-REVIEW.json')
            phase['seconds'] = float(phase['seconds']) + 1.0
            write_json(copied / 'CLIFFORD-REVIEW.json', phase)
            require(identities_of(module, copied) == baseline,
                    name + ' phase seconds change moved a canonical identity')
        finally:
            shutil.rmtree(scratch)

        scratch, copied = copy_provider(directory)
        try:
            phase = read_json(copied / 'CLIFFORD-REVIEW.json')
            phase['frames'] = int(phase['frames']) + 1
            write_json(copied / 'CLIFFORD-REVIEW.json', phase)
            shifted = identities_of(module, copied)
            require(shifted['CLIFFORD-REVIEW.json'] != baseline['CLIFFORD-REVIEW.json'],
                    name + ' phase frame count was invisible')
            require(all(shifted[key] == baseline[key] for key in baseline if key != 'CLIFFORD-REVIEW.json'),
                    name + ' phase frame count moved an unrelated identity')
        finally:
            shutil.rmtree(scratch)

        scratch, copied = copy_provider(directory)
        try:
            (copied / 'CANONICAL-WORD.json.gz').unlink()
            try:
                identities_of(module, copied)
            except (AssertionError, FileNotFoundError, OSError):
                pass
            else:
                raise ValueError(name + ' identity accepted a provider with no canonical word')
        finally:
            shutil.rmtree(scratch)

        omitted = sorted(key for key in audit if key != 'seconds')
        reports.append({
            'provider': name,
            'scalar_operations': audit['scalar_operations'],
            'local_rank_mass': audit['local_rank_mass'],
            'omitted_non_timing_fields': omitted,
            'identity_files': list(module.FILES),
        })

    require(reports[0]['omitted_non_timing_fields'] == reports[1]['omitted_non_timing_fields'],
            'ck and jp8 omit different scalar-audit fields')
    report = {
        'status': 'PASS_SCALAR_AUDIT_IDENTITY_GAP',
        'providers': [row['provider'] for row in reports],
        'omitted_non_timing_field_count': len(reports[0]['omitted_non_timing_fields']),
        'omitted_non_timing_fields': reports[0]['omitted_non_timing_fields'],
        'scalar_operations_invisible': True,
        'phase_seconds_excluded': True,
        'phase_frames_visible': True,
        'missing_canonical_word_rejected': True,
        'providers_detail': reports,
    }
    print(json.dumps(report, indent=2))
    print(report['status'],
          'providers=%d' % len(reports),
          'omitted_non_timing_fields=%d' % report['omitted_non_timing_field_count'])


if __name__ == '__main__':
    main()
