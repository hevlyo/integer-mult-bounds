#!/usr/bin/env python3
"""Portable replay of the retained PR379 low-read candidate.

The packaged verifier stops on a missing CPython 3.11 bytecode file. This
command keeps that failure, then replays the proof-relevant sources that are
actually in the tree. It does not change the selected frontier.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from decimal import Decimal, ROUND_FLOOR
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('assertions must stay enabled')
if sys.version_info[:2] != (3, 12):
    raise SystemExit('replay uses Python 3.12')

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PIN = HERE / 'pinned'
EXPECTED = json.loads((PIN / 'EXPECTED.json').read_text())
PREDECESSOR = EXPECTED['predecessor_commit']
JSON_HPP = ROOT / 'research/e8-bit-carrier-skeleton/code/bit/checkers/json.hpp'
ABSENT = EXPECTED['absent_manifest_paths']


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(argv, cwd, env=None):
    return subprocess.run(argv, cwd=cwd, env=env, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def clean_env():
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env.pop('PYTHONOPTIMIZE', None)
    return env


def manifest_rows():
    rows = []
    for line in (PIN / 'manifest/MANIFEST.sha256').read_text().splitlines():
        digest, relative = line.split('  ', 1)
        rows.append((digest, relative))
    return rows


def git_available():
    found = run(['git', 'cat-file', '-e', PREDECESSOR + '^{commit}'], ROOT)
    return found.returncode == 0


def bind_predecessor_bytes():
    """When the archive commit is present, vendored bytes must match it."""
    if not git_available():
        print('SKIP_ARCHIVE_OBJECT_BINDING ' + PREDECESSOR)
        return
    binding = {
        'manifest/MANIFEST.sha256': 'MANIFEST.sha256',
        'manifest/verify.py': 'verify.py',
        'manifest/NOTICE.md': 'NOTICE.md',
        'manifest/README.md': 'README.md',
        'manifest/assemble.py': 'assemble.py',
        'manifest/FULL-REPLAY-RECEIPTS.json': 'provenance/FULL-REPLAY-RECEIPTS.json',
        'kappa.json': 'proof/price/kappa.json',
        'finite.json': 'proof/price/finite.json',
        'b3.json': 'complex/b3.json',
        'assembly.json': 'proof/assembly.json',
        'LOWERING-BANKS.json': 'geometry/lowering/LOWERING-BANKS.json',
        'col.json': 'proof/check/col.json',
        'outer.py': 'code/outer.py',
        'lower_and_bank.py': 'code/lower_and_bank.py',
        'all-charts.cpp': 'code/all-charts.cpp',
        'columns_h.cpp': 'code/columns_h.cpp',
        'records/249-records.bin': 'proof/records/249-records.bin',
        'records/249-states.json': 'proof/records/249-states.json',
        'records/frames.json': 'proof/records/frames.json',
        'candidate-certificate.tar.gz': 'source/candidate-certificate.tar.gz',
        'pr363-composition-source.tar.gz': 'source/pr363-composition-source.tar.gz',
    }
    prefix = 'research/e8-low-read-seven-complex/'
    for local, remote in binding.items():
        shown = subprocess.run(['git', 'show', PREDECESSOR + ':' + prefix + remote],
                               cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        require(shown.returncode == 0, 'missing predecessor blob ' + remote)
        require(shown.stdout == (PIN / local).read_bytes(), 'vendored bytes differ ' + local)
    header = subprocess.run(['git', 'show', PREDECESSOR + ':' + prefix + 'code/json.hpp'],
                            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    require(header.returncode == 0 and header.stdout == JSON_HPP.read_bytes(),
            'json.hpp differs from the predecessor header')
    listed = run(['git', 'ls-tree', '-r', '--name-only', PREDECESSOR, '--',
                  'research/e8-low-read-seven-complex'], ROOT)
    require(listed.returncode == 0, 'git ls-tree failed')
    require(listed.stdout == (PIN / 'GIT-TREE.txt').read_text(), 'predecessor tree list changed')
    print('PASS_ARCHIVE_OBJECT_BINDING ' + PREDECESSOR)


def reproduce_manifest_failure():
    rows = manifest_rows()
    names = [relative for _, relative in rows]
    tree = [line.split('research/e8-low-read-seven-complex/', 1)[1]
            for line in (PIN / 'GIT-TREE.txt').read_text().splitlines()]
    missing = [name for name in names if name not in tree]
    require(missing == ABSENT, 'absent manifest paths differ: ' + repr(missing))
    with tempfile.TemporaryDirectory(prefix='pr379-manifest-') as tmp:
        dest = Path(tmp)
        for name in ('MANIFEST.sha256', 'verify.py', 'NOTICE.md', 'README.md', 'assemble.py'):
            shutil.copyfile(PIN / 'manifest' / name, dest / name)
        env = clean_env()
        result = run([sys.executable, '-B', 'verify.py'], dest, env)
        detail = result.stdout + result.stderr
        require(result.returncode != 0, 'original verifier unexpectedly passed')
        require('outer.cpython-311.pyc' in detail,
                'original verifier did not stop on the missing bytecode')
        require('PASS E8 low-read' not in result.stdout, 'receipt check ran after the missing file')
    print('PASS_MANIFEST_STOPS_ON_MISSING_BYTECODE')


def replay_receipt_gap():
    full = json.loads((PIN / 'manifest/FULL-REPLAY-RECEIPTS.json').read_text())
    require(full['cp311']['kappa'] == full['cp312']['kappa'] == EXPECTED['pr370_replay_kappa'],
            'retained full-replay kappa changed')
    require(full['cp311']['kappa'] != EXPECTED['candidate_kappa'],
            'retained full-replay kappa is the candidate')
    print('PASS_FULL_REPLAY_RECEIPT_IS_PR370_BASELINE')


def replay_candidate(work):
    archive = PIN / 'candidate-certificate.tar.gz'
    with tarfile.open(archive) as packed:
        original = packed.extractfile('RESULT.json').read()
        packed.extractall(work)
    env = clean_env()
    result = run([sys.executable, '-B', 'verify.py'], work, env)
    require(result.returncode == 0, 'candidate certificate replay failed\n' + result.stdout + result.stderr)
    fresh = (work / 'RESULT.json').read_bytes()
    require(fresh == original, 'candidate RESULT.json is not the retained receipt')
    data = json.loads(fresh)
    kappa = json.loads((PIN / 'kappa.json').read_text())
    histogram = {str(rank): count for rank, count in data['candidate_five_stage_histogram'].items()}
    require(histogram == {str(rank): count for rank, count in kappa['normalized_histogram'].items()},
            'candidate five-stage histogram differs from kappa.json')
    require(data['calls'] == 22020 and data['rank_mass'] == 53680 and data['deficit'] == 120
            and data['W'] == 1345 and data['m'] == 40, 'candidate inventory differs')
    root = data['conditional_coarse_roots_with_inherited_bad_envelope']['candidate']
    floor = (Decimal(root['lower']) * Decimal(10 ** 18)).to_integral_value(ROUND_FLOOR)
    require(str(floor) + '/1000000000000000000' == kappa['bit_coarse'] == EXPECTED['candidate_bit_coarse'],
            'bit coarse is not the floored candidate root')
    require(Decimal(root['upper']) > Decimal(root['lower']), 'candidate root interval is empty')
    print('PASS_CANDIDATE_WORD_AND_MOMENT')


def compile_checker(source, output, extra):
    compiler = shutil.which('g++')
    require(compiler == '/usr/bin/g++', 'g++ is not /usr/bin/g++')
    linked = Path('/usr/bin/c++').resolve()
    require(linked == Path('/usr/bin/g++').resolve(), 'c++ alternative is not g++')
    command = [compiler, '-O2', '-std=c++17', '-I', str(JSON_HPP.parent), *extra, '-o', str(output), str(source)]
    result = run(command, ROOT, clean_env())
    require(result.returncode == 0, 'compile failed\n' + result.stdout + result.stderr)
    return output


def replay_geometry(work):
    charts = work / 'charts'
    charts.mkdir()
    binary = compile_checker(PIN / 'all-charts.cpp', work / 'all-charts', [])
    result = run([str(binary), str(PIN / 'records'), str(charts)], work, clean_env())
    require(result.returncode == 0, 'chart replay failed\n' + result.stdout + result.stderr)
    require(sha256(charts / 'ALL-CHARTS.json') == EXPECTED['all_charts_sha256'], 'ALL-CHARTS bytes differ')
    require(sha256(charts / 'CHART-RECEIPT.json') == EXPECTED['chart_receipt_sha256'], 'chart receipt differs')
    mutated = work / 'mutated-records'
    shutil.copytree(PIN / 'records', mutated)
    blob = mutated / '249-records.bin'
    raw = bytearray(blob.read_bytes())
    raw[len(raw) // 2] ^= 0x01
    blob.write_bytes(raw)
    bad_dir = work / 'bad-charts'
    bad_dir.mkdir()
    bad = run([str(binary), str(mutated), str(bad_dir)], work, clean_env())
    changed = bad.returncode != 0 or not (bad_dir / 'ALL-CHARTS.json').is_file() or sha256(bad_dir / 'ALL-CHARTS.json') != EXPECTED['all_charts_sha256']
    require(changed, 'mutated record stream reproduced the chart oracle')
    print('PASS_CHARTS_AND_MUTATION')
    return charts


def replay_columns(work):
    binary = compile_checker(PIN / 'columns_h.cpp', work / 'columns',
                             ['-DNCOPY=9', '-DVPORTS=120', '-DRHELP=865', '-DHDIM=8'])
    result = run([str(binary), str(PIN / 'records/249-records.bin'), str(work / 'columns-out')], work, clean_env())
    require(result.returncode == 0, 'column replay failed\n' + result.stdout + result.stderr)
    fresh = json.loads((work / 'columns-out').read_text())
    stored = json.loads((PIN / 'col.json').read_text())
    ignore = {'seconds', 'local_scalar_stream'}
    require({key: value for key, value in fresh.items() if key not in ignore}
            == {key: value for key, value in stored.items() if key not in ignore},
            'column receipt differs beyond path and elapsed time')
    require(fresh['formal_columns_checked'] == 1345 and fresh['independent_dirty_registers'] == 865,
            'column dimensions differ')
    print('PASS_FIVE_STAGE_COLUMNS')


def replay_lowering(work, charts):
    output = work / 'lowering'
    output.mkdir()
    result = run([sys.executable, '-B', str(PIN / 'lower_and_bank.py'),
                  '--records', str(PIN / 'records'), '--charts', str(charts), '--output', str(output)],
                 work, clean_env())
    require(result.returncode == 0, 'lowering failed\n' + result.stdout + result.stderr)
    require((output / 'LOWERING-BANKS.json').read_bytes() == (PIN / 'LOWERING-BANKS.json').read_bytes(),
            'lowering receipt differs')
    require(sha256(output / 'GLOBAL-PROGRAM.bin') == EXPECTED['program_sha256'], 'lowered program differs')
    print('PASS_LOWERING_PROGRAM')


def replay_assembly(work):
    dest = work / 'assembly'
    (dest / 'code').mkdir(parents=True)
    (dest / 'proof/price').mkdir(parents=True)
    (dest / 'complex').mkdir()
    shutil.copyfile(PIN / 'manifest/assemble.py', dest / 'assemble.py')
    shutil.copyfile(PIN / 'outer.py', dest / 'code/outer.py')
    shutil.copyfile(PIN / 'kappa.json', dest / 'proof/price/kappa.json')
    shutil.copyfile(PIN / 'finite.json', dest / 'proof/price/finite.json')
    shutil.copyfile(PIN / 'b3.json', dest / 'complex/b3.json')
    result = run([sys.executable, '-B', 'assemble.py'], dest, clean_env())
    require(result.returncode == 0, 'assembly failed\n' + result.stdout + result.stderr)
    require((dest / 'proof/assembly.json').read_bytes() == (PIN / 'assembly.json').read_bytes(),
            'assembly receipt differs')
    built = json.loads((dest / 'proof/assembly.json').read_text())
    require(built['kappa'] == EXPECTED['candidate_kappa'] and built['complex_coarse'] == EXPECTED['complex_b3'],
            'assembly kappa or complex saving differs')
    require(built['adjacent_grid_point_rejected'] is True and len(built['strict_constraints']) == 47,
            'assembly constraints differ')
    print('PASS_47_CONSTRAINT_ASSEMBLY')


def replay_complex(work):
    source = work / 'pr363'
    source.mkdir()
    extracted = run(['tar', '-xzf', str(PIN / 'pr363-composition-source.tar.gz'), '-C', str(source)], work, clean_env())
    require(extracted.returncode == 0, 'complex source extract failed\n' + extracted.stdout + extracted.stderr)
    for path in source.rglob('._*'):
        path.unlink()
    output = work / 'pr363-out'
    script = source / 'pr363-composition-source-v1/verify.sh'
    result = run(['bash', str(script), str(output)], work, clean_env())
    require(result.returncode == 0, 'seven-stage complex replay failed\n' + result.stdout + result.stderr)
    saved = json.loads((output / 'b3.json').read_text())
    require(saved['b'] == EXPECTED['complex_b3'] == json.loads((PIN / 'b3.json').read_text())['b'],
            'seven-stage complex saving differs')
    print('PASS_SEVEN_STAGE_COMPLEX')


def main():
    require(sha256(JSON_HPP) == EXPECTED['json_hpp_sha256'], 'json.hpp pin differs')
    bind_predecessor_bytes()
    reproduce_manifest_failure()
    replay_receipt_gap()
    with tempfile.TemporaryDirectory(prefix='pr379-replay-') as tmp:
        work = Path(tmp)
        replay_candidate(work / 'candidate')
        charts = replay_geometry(work)
        replay_columns(work)
        replay_lowering(work, charts)
        replay_assembly(work)
        replay_complex(work)
    print('PASS_PR379_PORTABLE_REPLAY candidate_kappa=' + EXPECTED['candidate_kappa']
          + ' selected_frontier_unchanged')


if __name__ == '__main__':
    main()
