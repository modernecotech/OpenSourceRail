#!/usr/bin/env python3
"""Check current README formatting, navigation and city publication scope."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess

REPO_ROOT = Path(__file__).resolve().parents[2]
FLAGS = ('design_complete','physical_validation','manufacturing_release','physical_release')


def repository_markdown():
    values = []
    for arguments in (['git','ls-files','*.md'],['git','ls-files','--others','--exclude-standard','*.md']):
        values += subprocess.check_output(arguments,cwd=REPO_ROOT,text=True).splitlines()
    return sorted({REPO_ROOT/name for name in values if (REPO_ROOT/name).is_file()})


def tracked_readmes():
    return [p for p in repository_markdown() if p.name=='README.md']


def normalized(text):
    return '\n'.join(line.rstrip() + ('  ' if line.endswith('  ') else '') for line in text.splitlines())+'\n'


def primary_city_readme(path,text):
    """Check the generated current city package without accepting physical release."""
    package = path.parent/'engineering/current'
    if not (path.parent/'city.json').is_file():
        return text,None
    errors=[]
    try:
        current=(package/'README.md').read_text()
        summary=json.loads((package/'summary.json').read_text())
        if not current.startswith('# '):errors.append('city package README requires an H1')
        if '[Primary planning method]' not in current:errors.append('city package lacks a current common-method link')
        if summary.get('development_default') is not True:errors.append('city is not the selected development default')
        for flag in ('engineering_accepted','physical_accepted','installed_mass_complete','manufacturing_release','operating_release'):
            if summary.get(flag) is not False:errors.append('city cannot grant physical release: '+flag)
        if summary['vehicle']['cars']!=6 or summary['vehicle']['normal_passengers_per_car']!=46:
            errors.append('city comfort formation differs')
        if 'engineering/current/' not in text or 'engineering/maglev/README.md' not in text:
            errors.append('city front requires current and historical planning routes')
    except (OSError,ValueError,KeyError) as exc:
        errors.append('city package missing/invalid: '+str(exc))
    return text,errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fix',action='store_true',help='normalize whitespace and final newlines')
    args=parser.parse_args()
    findings=[]
    root=REPO_ROOT/'README.md'
    if not root.is_file():
        findings.append('README.md: missing repository front door')
    else:
        text=root.read_text()
        for marker in ('docs/design-engine/current/README.md','engineering/development-baseline.toml','osr-maglev-control','./osr readiness','./osr test','./osr build','OpenSourceRail-Book.pdf'):
            if marker not in text:
                findings.append('README.md: missing current architecture/command reference '+marker)
    if not (REPO_ROOT/'OpenSourceRail-Book.pdf').is_file():
        findings.append('OpenSourceRail-Book.pdf: missing current reader book')
    paths=tracked_readmes()
    for path in paths:
        text=path.read_text()
        expected=normalized(text)
        if args.fix and text!=expected:
            path.write_text(expected)
            text=expected
        relative=path.relative_to(REPO_ROOT)
        heading=text.removeprefix('<!-- osr-maglev-primary:start -->\n')
        if not heading.startswith('# '):
            findings.append(f'{relative}: README must start with an H1')
        if text!=normalized(text):
            findings.append(f'{relative}: trailing whitespace or missing final newline')
        _,errors=primary_city_readme(path,text)
        findings.extend(f'{relative}: {error}' for error in errors or [])
    inventory=REPO_ROOT/'docs/INDEX.md'
    if not inventory.is_file():
        findings.append('docs/INDEX.md: missing Markdown inventory')
    else:
        text=inventory.read_text()
        for path in repository_markdown():
            relative=path.relative_to(REPO_ROOT).as_posix()
            if path!=inventory and f'`{relative}`' not in text:
                findings.append('docs/INDEX.md: missing Markdown inventory entry '+relative)
    for finding in findings:print(f'ERROR: {finding}')
    print(f'README check: {len(findings)} findings; {len(paths)} README files')
    return int(bool(findings))


if __name__=='__main__':
    raise SystemExit(main())
