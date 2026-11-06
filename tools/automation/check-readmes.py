#!/usr/bin/env python3
"""Check current README formatting, navigation and city publication scope."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

AUTOMATION_DIR = str(Path(__file__).resolve().parent)
if AUTOMATION_DIR not in sys.path:
    sys.path.insert(0, AUTOMATION_DIR)

from doc_index_policy import is_indexed_markdown

REPO_ROOT = Path(__file__).resolve().parents[2]
FLAGS = ('design_complete','physical_validation','manufacturing_release','physical_release')
SEALED_LEGACY_PACKET_READMES = {
    'docs/design-engine/sourcing/domestic-fabrication/regional-estimates-2026-september-v3/README.md',
    'docs/design-engine/sourcing/domestic-fabrication/regional-estimates-2026-september-v4/README.md',
}


def repository_markdown():
    values = []
    for arguments in (['git','ls-files','*.md'],['git','ls-files','--others','--exclude-standard','*.md']):
        values += subprocess.check_output(arguments,cwd=REPO_ROOT,text=True).splitlines()
    return sorted({REPO_ROOT/name for name in values if (REPO_ROOT/name).is_file()})


def tracked_readmes():
    # Keep these source-hashed historical packet bytes intact. Their former
    # writer serialized Markdown as a JSON string; the current v5 generator
    # writes a normal README and is included in this check.
    return [p for p in repository_markdown() if p.name=='README.md'
            and p.relative_to(REPO_ROOT).as_posix() not in SEALED_LEGACY_PACKET_READMES]


def normalized(text):
    return '\n'.join(line.rstrip() + ('  ' if line.endswith('  ') else '') for line in text.splitlines())+'\n'



def primary_city_readme(path,text):
    """Check that a city frontdoor routes to the candidate-bound planning hold."""
    package = path.parent/'engineering/current'
    if not (path.parent/'city.json').is_file():
        return text,None
    errors=[]
    try:
        current=(package/'README.md').read_text()
        summary=json.loads((package/'summary.json').read_text())
        manifest=json.loads((package/'manifest.json').read_text())
        if not current.startswith('# '):errors.append('city package README requires an H1')
        if '[Planning workspace]' not in current:errors.append('city package lacks the current planning workspace route')
        if summary.get('schema')!='osr-current-city-hold/1' or summary.get('execution')!='held':
            errors.append('city package must be a current v0.6 planning hold')
        if summary.get('performance_evaluated') is not False or summary.get('totals') is not None:
            errors.append('city package cannot publish route performance or totals')
        for flag in ('engineering_accepted','physical_accepted','installed_mass_complete','manufacturing_release','operating_release'):
            if summary.get(flag) is not False:errors.append('city cannot grant physical release: '+flag)
        if manifest.get('schema') not in ('osr-current-city-publication/2','osr-current-city-publication/3'):
            errors.append('city package manifest must identify the current v0.6 hold')
        if manifest.get('schema')=='osr-current-city-publication/3':
            presentation=manifest.get('presentation',{})
            dossier=REPO_ROOT/presentation.get('dossier_manifest_path','')
            value=json.loads(dossier.read_bytes())
            if (presentation.get('owner')!='engineering.city_reports.publication' or value.get('manifest_id')!=presentation.get('dossier_manifest_id')
                or value.get('city_frontdoor_sha256')!=manifest.get('city_frontdoor_sha256')):
                errors.append('city dossier presentation ownership differs')
        if manifest.get('files_sha256',{}).get('README.md')!=sha256((package/'README.md').read_bytes()).hexdigest():
            errors.append('city package README differs from its source-bound manifest')
        if manifest.get('files_sha256',{}).get('summary.json')!=sha256((package/'summary.json').read_bytes()).hexdigest():
            errors.append('city package summary differs from its source-bound manifest')
        if manifest.get('city_frontdoor_path')!=path.relative_to(REPO_ROOT).as_posix():
            errors.append('city frontdoor path differs from its source-bound manifest')
        if manifest.get('city_frontdoor_sha256')!=sha256(path.read_bytes()).hexdigest():
            errors.append('city frontdoor differs from its source-bound manifest')
        if 'engineering/current/' not in text or '[Planning workspace]' not in text:
            errors.append('city frontdoor needs current packet and planning workspace routes')
        for source in (text,current):
            if any(token in source.casefold() for token in ('engineering/maglev/readme.md','ferrite-maglev','v0.4','v0.5','legacy/')):
                errors.append('current city README must not route readers to superseded design pages')
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
        for marker in ('docs/design-engine/current/README.md','engineering/development-baseline.toml','crates/README.md','./osr readiness','./osr test','./osr build','OpenSourceRail-Book.pdf'):
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
            if not is_indexed_markdown(path.relative_to(REPO_ROOT)):
                continue
            relative=path.relative_to(REPO_ROOT).as_posix()
            if path!=inventory and f'`{relative}`' not in text:
                findings.append('docs/INDEX.md: missing Markdown inventory entry '+relative)
    for finding in findings:print(f'ERROR: {finding}')
    print(f'README check: {len(findings)} findings; {len(paths)} README files')
    return int(bool(findings))


if __name__=='__main__':
    raise SystemExit(main())
