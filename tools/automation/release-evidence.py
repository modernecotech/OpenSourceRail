#!/usr/bin/env python3
"""Build versioned release assets from a clean tag with complete local or historical validation."""
import argparse
import base64
import mimetypes
import re
import hashlib
import importlib.util
import tempfile
import json
from pathlib import Path
import shutil
import subprocess
import tomllib
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = {'ci', 'kani', 'integrated-stack', 'example-city'}


def run(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def successful_runs(rows, commit):
    latest = {}
    for row in sorted(rows, key=lambda r: (r['createdAt'], r['databaseId']), reverse=True):
        if row['headSha'] == commit and row['workflowName'] in WORKFLOWS:
            latest.setdefault(row['workflowName'], row)
    missing = WORKFLOWS - latest.keys()
    incomplete = [name for name, row in latest.items()
                  if row['status'] != 'completed' or row['conclusion'] != 'success']
    if missing or incomplete:
        raise ValueError(f'Release checks incomplete: missing={sorted(missing)}, unsuccessful={incomplete}')
    return [latest[name] for name in sorted(latest)]


@contextmanager
def release_inputs(backend, folders, commit):
    """Require the same four release gates before assembling any assets."""
    if backend == 'local':
        from local_validation import release_receipts
        receipts = release_receipts(folders, commit)
        paths = {json.loads((folder / 'receipt.json').read_text())['profile']: folder.resolve() for folder in folders}
        checks = [dict(profile=name, execution_location='local', receipt=receipts[name],
                       receipt_sha256=hashlib.sha256((paths[name] / 'receipt.json').read_bytes()).hexdigest())
                  for name in sorted(receipts)]
        yield checks, paths['example-city'] / 'city', paths['kani'], None, None
        return
    if folders:
        raise ValueError('Local validation directories cannot substitute for historical GitHub runs')
    gh = shutil.which('gh') or str(Path.home() / '.local/bin/gh')
    rows = json.loads(run(gh, 'run', 'list', '--repo', 'modernecotech/OpenSourceRail',
                          '--commit', commit, '--limit', '100', '--json',
                          'databaseId,workflowName,status,conclusion,headSha,url,createdAt'))
    checks = successful_runs(rows, commit)
    city_id = next(row['databaseId'] for row in checks if row['workflowName'] == 'example-city')
    kani_id = next(row['databaseId'] for row in checks if row['workflowName'] == 'kani')
    with tempfile.TemporaryDirectory(prefix='osr-release-inputs-') as directory:
        city = Path(directory) / 'city'; kani = Path(directory) / 'kani'
        for run_id, folder, selection in [(city_id, city, ['--name', 'samawah-city-acceptance']),
                                         (kani_id, kani, ['--pattern', 'safety-execution-*'])]:
            subprocess.run([gh, 'run', 'download', str(run_id), '--repo',
                            'modernecotech/OpenSourceRail', *selection, '--dir', str(folder)], check=True)
        yield checks, city, kani, city_id, kani_id


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--backend', choices=['local', 'github'], default='local',
                        help='Local execution by default; github reads historical runs without starting jobs')
    parser.add_argument('--local-validation', action='append', type=Path, default=[],
                        help='Repeat for passing ci, kani, integrated-stack and example-city receipt directories')
    args = parser.parse_args()
    version = tomllib.loads((ROOT / 'Cargo.toml').read_text())['workspace']['package']['version']
    if args.tag != 'v' + version:
        raise SystemExit('Tag must match the workspace software version')
    commit = run('git', 'rev-parse', '--verify', args.tag + '^{commit}')
    if commit != run('git', 'rev-parse', 'HEAD') or run('git', 'status', '--porcelain', '--untracked-files=normal'):
        raise SystemExit('Check out the release tag with a clean working tree, including untracked source')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    book = out / f'OpenSourceRail-Book-{args.tag}.pdf'
    exported = []
    spec = importlib.util.spec_from_file_location('city_release_evidence', ROOT / 'deployment/example-city/evidence.py')
    city_evidence = importlib.util.module_from_spec(spec); spec.loader.exec_module(city_evidence)
    with release_inputs(args.backend, args.local_validation, commit) as (checks, city_folder, kani_folder, city_id, kani_id), tempfile.TemporaryDirectory(prefix='osr-release-export-') as directory:
        city_manifest = city_evidence.validate(city_folder, commit)
        # Publish the exact reports validated above, not a locally rerun substitute.
        archive_root = Path(directory) / 'release-public'; archive_root.mkdir()
        for relative in ['city-evidence.json', *city_manifest['reports']]:
            destination = archive_root / relative; destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(city_folder / relative, destination)
        archive = Path(shutil.make_archive(str(out / f'OpenSourceRail-City-Acceptance-{args.tag}'), 'zip', archive_root))
        exported.append(archive)
        from kani_release import export as export_kani, export_local
        archive_root = Path(directory) / 'release-kani'
        archive_root.mkdir()
        kani_manifest = export_local(kani_folder, archive_root, commit) if args.backend == 'local' else export_kani(kani_folder, archive_root, commit, kani_id)
        archive = Path(shutil.make_archive(str(out / f'OpenSourceRail-Kani-Evidence-{args.tag}'), 'zip', archive_root))
        exported.append(archive)
    subprocess.run([str(ROOT / 'tools/automation/osr-python'),
                    'tools/automation/build-doc-book.py', '--out', str(book), '--source-ref', args.tag], cwd=ROOT, check=True)
    exported.append(book)
    for source, name in [
        ('docs/open-source-rail-overview.html', f'OpenSourceRail-Overview-{args.tag}.html'),
        ('docs/open-source-rail-overview.md', f'OpenSourceRail-Overview-{args.tag}.md'),
        ('docs/operating/readiness.json', f'OpenSourceRail-Readiness-{args.tag}.json'),
        ('docs/release-v0.4.md', f'OpenSourceRail-Release-{args.tag}.md'),
    ]:
        destination = out / name
        destination.write_bytes(subprocess.check_output(['git', 'show', args.tag + ':' + source], cwd=ROOT))
        if destination.suffix == '.html':
            def embed_image(match):
                image = (ROOT / 'docs' / match.group(1)).resolve()
                if not image.is_relative_to(ROOT / 'docs') or not image.is_file():
                    raise ValueError('Overview image is outside the documented source tree')
                mime = mimetypes.guess_type(image.name)[0]
                return 'src="data:' + mime + ';base64,' + base64.b64encode(image.read_bytes()).decode() + '"'
            destination.write_text(re.sub(r'src="([^":]+)"', embed_image, destination.read_text()))
        if destination.suffix == '.md':
            destination.write_text(re.sub(r'(!?\[[^]]+\])\((?!https?:|#)([^)]+)\)',
                lambda m: m[1] + ('(https://raw.githubusercontent.com/modernecotech/OpenSourceRail/' if m[1].startswith('!') else '(https://github.com/modernecotech/OpenSourceRail/blob/') + args.tag + '/docs/' + m[2] + ')',
                destination.read_text()))
        exported.append(destination)
    evidence = {
        'schema': 'osr-software-release/1', 'version': version, 'tag': args.tag,
        'commit': commit, 'source_tree': run('git', 'rev-parse', args.tag + '^{tree}'),
        'execution_location': args.backend,
        'workflows': checks if args.backend == 'github' else [],
        'local_validation': checks if args.backend == 'local' else [],
        'example_city': dict(run_id=city_id, execution_location=args.backend, manifest=city_manifest),
        'kani_release_properties': [row['anchor'] for row in kani_manifest['harnesses']],
        'kani_evidence': kani_manifest,
        'kani_additional_checks': ['kani_p5_time_bounded_arithmetic', 'tacs_timestamped_output_rejects_invalid_source_age', 'kani_a2_expired_ma_trips'],
        'scope': 'ERPNext/FUXA/OSR software integration and simulation baseline',
        'independent_safety_acceptance': False,
        'physical_deployment_approval': False,
        'open_work_register': 'docs/ROADMAP.md',
        'assets': {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in exported},
    }
    manifest = out / f'OpenSourceRail-Evidence-{args.tag}.json'
    manifest.write_text(json.dumps(evidence, indent=2, sort_keys=True) + '\n')
    exported.append(manifest)
    checksums = out / 'SHA256SUMS'
    checksums.write_text(''.join(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n'
                                 for path in sorted(exported)))
    print(json.dumps({'tag': args.tag, 'commit': commit, 'assets': [str(p) for p in exported + [checksums]]}, indent=2))


if __name__ == '__main__':
    main()
