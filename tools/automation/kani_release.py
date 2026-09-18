"""Validate all declared Kani artifacts before exporting a software release."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tomllib

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('controlled_assurance', ROOT / 'tools/automation/assurance-evidence.py')
ASSURANCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ASSURANCE)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(directory, commit, run_id):
    expected = ASSURANCE.declared()
    inputs = ASSURANCE.scope()
    runner = f'github:modernecotech/OpenSourceRail/actions/runs/{run_id}'
    packages = sorted({row['path'].split('/')[1] for row in expected})
    inventory = []
    for package in packages:
        folder = directory / ('safety-execution-' + package)
        if folder.is_symlink() or not folder.is_dir() or any(p.is_symlink() or not p.is_file() for p in folder.iterdir()):
            raise ValueError(f'Unsafe Kani artifact membership: {package}')
        manifest_path, results_path = folder / 'execution.json', folder / 'results.toml'
        manifest = json.loads(manifest_path.read_text())
        results = tomllib.loads(results_path.read_text())
        declarations = {row['solution']: row for row in expected if row['path'].split('/')[1] == package}
        if (manifest.get('schema') != 'osr-controlled-execution/1' or manifest.get('commit') != commit
                or manifest.get('runner') != runner or manifest.get('passed') is not True
                or manifest.get('inputs') != inputs or manifest.get('results_sha256') != digest(results_path)):
            raise ValueError(f'Stale, failed or mismatched Kani execution: {package}')
        records = results.get('result', [])
        solutions = [row.get('solution') for row in records]
        if (results.get('schema') != 'osr-evidence-results/1' or len(solutions) != len(set(solutions))
                or set(solutions) != set(declarations) or manifest.get('solutions') != solutions):
            raise ValueError(f'Incomplete or duplicate declared Kani evidence: {package}')
        allowed = {'execution.json', 'results.toml'}
        for row in records:
            declaration = declarations[row['solution']]
            report_name = row['solution'] + '.log'
            report = folder / report_name
            expected_path = f'build/assurance/{package}/{report_name}'
            if (any(row.get(key) != declaration[key] for key in ('kind', 'path', 'anchor'))
                    or row.get('inputs') != inputs or row.get('status') != 'passed'
                    or row.get('exit_code') != 0 or row.get('tool') != 'cargo-kani'
                    or row.get('tool_version') != 'cargo-kani 0.67.0' or not row.get('bounds')
                    or row.get('executed_by') != runner or row.get('report') != expected_path
                    or row.get('report_sha256') != digest(report)):
                raise ValueError(f'Invalid Kani result: {row["solution"]}')
            lines = report.read_text().splitlines()
            header = json.loads(lines[0])
            if (header.get('source_commit') != commit or header.get('tool_version') != row['tool_version']
                    or header.get('command') != ['cargo', 'kani', '-p', package, '--harness', 'kani_proofs::' + row['anchor'], '--exact']
                    or not any(line.strip() in ('VERIFICATION:- SUCCESSFUL', 'VERIFICATION: SUCCESSFUL') for line in lines)):
                raise ValueError(f'Kani report does not confirm the execution: {row["solution"]}')
            allowed.add(report_name)
            inventory.append(dict(solution=row['solution'], package=package, anchor=row['anchor'],
                                  report=expected_path, report_sha256=row['report_sha256']))
        if any(path.is_symlink() or not path.is_file() for path in folder.iterdir()) or {p.name for p in folder.iterdir()} != allowed:
            raise ValueError(f'Unexpected Kani artifact membership: {package}')
    return dict(schema='osr-kani-release-evidence/1', commit=commit, workflow_run=run_id,
                packages=packages, harnesses=inventory, independently_accepted=False,
                scope='Executed declared harnesses within recorded assumptions and unwind bounds; no independent safety acceptance.')


def export(directory, destination, commit, run_id):
    summary = validate(directory, commit, run_id)
    for package in summary['packages']:
        shutil.copytree(directory / ('safety-execution-' + package), destination / 'build/assurance' / package)
    (destination / 'kani-evidence.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary
