#!/usr/bin/env python3
"""Build versioned release assets only from a clean, workflow-verified Git tag."""
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    version = tomllib.loads((ROOT / 'Cargo.toml').read_text())['workspace']['package']['version']
    if args.tag != 'v' + version:
        raise SystemExit('Tag must match the workspace software version')
    commit = run('git', 'rev-parse', '--verify', args.tag + '^{commit}')
    if commit != run('git', 'rev-parse', 'HEAD') or run('git', 'status', '--porcelain', '--untracked-files=normal'):
        raise SystemExit('Check out the release tag with a clean working tree, including untracked source')
    gh = shutil.which('gh') or str(Path.home() / '.local/bin/gh')
    rows = json.loads(run(gh, 'run', 'list', '--repo', 'modernecotech/OpenSourceRail',
                          '--commit', commit, '--limit', '100', '--json',
                          'databaseId,workflowName,status,conclusion,headSha,url,createdAt'))
    workflows = successful_runs(rows, commit)
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    book = out / f'OpenSourceRail-Book-{args.tag}.pdf'
    subprocess.run([str(ROOT / 'tools/automation/osr-python'),
                    'tools/automation/build-doc-book.py', '--out', str(book), '--source-ref', args.tag], cwd=ROOT, check=True)
    exported = [book]
    city_run = next(row for row in workflows if row['workflowName'] == 'example-city')
    spec = importlib.util.spec_from_file_location('city_release_evidence', ROOT / 'deployment/example-city/evidence.py')
    city_evidence = importlib.util.module_from_spec(spec); spec.loader.exec_module(city_evidence)
    with tempfile.TemporaryDirectory(prefix='osr-release-city-') as directory:
        subprocess.run([gh, 'run', 'download', str(city_run['databaseId']), '--repo',
                        'modernecotech/OpenSourceRail', '--name', 'samawah-city-acceptance', '--dir', directory], check=True)
        city_manifest = city_evidence.validate(Path(directory), commit)
        # Publish the exact reports validated above, not a locally rerun substitute.
        archive_root = Path(directory) / 'release-public'; archive_root.mkdir()
        for relative in ['city-evidence.json', *city_manifest['reports']]:
            destination = archive_root / relative; destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(Path(directory) / relative, destination)
        archive = Path(shutil.make_archive(str(out / f'OpenSourceRail-City-Acceptance-{args.tag}'), 'zip', archive_root))
        exported.append(archive)
    from kani_release import export as export_kani
    kani_run = next(row for row in workflows if row['workflowName'] == 'kani')
    with tempfile.TemporaryDirectory(prefix='osr-release-kani-') as directory:
        subprocess.run([gh, 'run', 'download', str(kani_run['databaseId']), '--repo',
                        'modernecotech/OpenSourceRail', '--pattern', 'safety-execution-*', '--dir', directory], check=True)
        archive_root = Path(directory) / 'release-public'
        archive_root.mkdir()
        kani_manifest = export_kani(Path(directory), archive_root, commit, kani_run['databaseId'])
        archive = Path(shutil.make_archive(str(out / f'OpenSourceRail-Kani-Evidence-{args.tag}'), 'zip', archive_root))
        exported.append(archive)
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
        'workflows': workflows,
        'example_city': dict(run_id=city_run['databaseId'], manifest=city_manifest),
        'kani_release_properties': [row['anchor'] for row in kani_manifest['harnesses']],
        'kani_evidence': kani_manifest,
        'kani_additional_checks': ['kani_p5_time_bounded_arithmetic', 'kani_a2_expired_ma_trips'],
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
