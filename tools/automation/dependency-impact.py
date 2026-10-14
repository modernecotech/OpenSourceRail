#!/usr/bin/env python3
"""Find downstream provenance records invalidated by changed source bytes.

Reads declared dependencies, never rewrites hashes or acceptance records. Current
owners have explicit regeneration commands; historical evidence stays retained.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
OWNERS={
 'engineering/assurance/baghdad-test-inputs/manifest.json':
  ['tools/automation/osr-python','tools/automation/pack-baghdad-test-inputs.py'],
 'cities/catalogue/west-asia/Iraq/Baghdad/engineering/connected-build/manifest.json':
  ['tools/automation/osr-python','tools/automation/connected-build-study.py','--city','baghdad','--refresh-cad'],
 'engineering/models/digital-twins/best-practice/review.json':
  ['tools/automation/osr-python','tools/automation/design-best-practice-twin.py','generate','--output','<fresh-directory>','--publish'],
 'engineering/best_practice/coverage.json':
  ['python3','tools/automation/best-practice.py','generate','--as-of','2026-10-11'],
 'engineering/industrialisation/modernisation/review.json':
  ['tools/automation/osr-python','tools/automation/factory-modernisation.py','generate','--output','<fresh-directory>'],
 'engineering/civil_exploration/examples/automated-parts-current-review.json':
  ['tools/automation/osr-python','tools/automation/compile-reference-parts.py','generate','--output','<fresh-directory>','--review','<fresh-review>'],
 'docs/certification/digital-assurance-report.json':['python3','tools/automation/digital-assurance.py'],
}
HISTORICAL={'engineering/civil_exploration/examples/automated-parts-review.json'}
KEYS={'source_sha256','sources_sha256','source_hashes','sources'}


def dependency_maps(value):
    if isinstance(value,dict):
        for key,child in value.items():
            if key in KEYS and isinstance(child,dict):
                for name,digest in child.items():
                    if isinstance(name,str) and isinstance(digest,str) and len(digest)==64 and ('/' in name or Path(name).suffix):
                        yield name,digest
            yield from dependency_maps(child)
    elif isinstance(value,list):
        for child in value:yield from dependency_maps(child)


def impact(paths=None,root=ROOT):
    if paths is None:
        paths=subprocess.check_output(['git','ls-files','-z','*.json'],cwd=root).decode().split('\0')
    cache={};rows=[]
    for name in paths:
        if not name:continue
        path=root/name
        if not path.is_file():continue
        raw=path.read_bytes()
        if not any(('"'+key+'"').encode() in raw for key in KEYS):continue
        try:record=json.loads(raw)
        except (ValueError,UnicodeDecodeError):continue
        changes=[]
        for source,expected in sorted(set(dependency_maps(record))):
            target=(root/source).resolve()
            if not target.is_relative_to(root.resolve()):raise ValueError('dependency escapes repository: '+source)
            if source not in cache:cache[source]=hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None
            if cache[source]!=expected:changes.append(dict(source=source,recorded_sha256=expected,current_sha256=cache[source]))
        if changes:
            state='stale-current' if name in OWNERS else 'historical' if name in HISTORICAL else 'scope-review-required'
            rows.append(dict(artifact=name,state=state,changed_sources=changes,regenerate_command=OWNERS.get(name)))
    return dict(schema='osr-dependency-impact/1',invalidated=rows,current_regeneration_required=[r['artifact'] for r in rows if r['state']=='stale-current'],
        acceptance_changed=False,source_hashes_rewritten=False)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);p.add_argument('--check-current',action='store_true');a=p.parse_args()
    report=impact()
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(invalidated_artifacts=len(report['invalidated']),current_regeneration_required=report['current_regeneration_required'])))
    if a.check_current and report['current_regeneration_required']:raise SystemExit(1)


if __name__=='__main__':main()
