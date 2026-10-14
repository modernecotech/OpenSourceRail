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
 'engineering/operations/pilot-review.json':
  ['tools/automation/osr-python','tools/automation/operations-pilot.py','--review'],
 'cities/catalogue/west-asia/Iraq/Baghdad/publication-manifest.json':
  ['tools/automation/osr-python','tools/automation/publish-city-summary.py'],
 'engineering/assurance/baghdad-test-inputs/manifest.json':
  ['tools/automation/osr-python','tools/automation/pack-baghdad-test-inputs.py'],
 'cities/catalogue/west-asia/Iraq/Baghdad/engineering/coupled-programme/manifest.json':
  ['tools/automation/osr-python','tools/automation/coupled-programme-study.py'],
 'cities/catalogue/west-asia/Iraq/Baghdad/engineering/civil-works/manifest.json':
  ['tools/automation/osr-python','tools/automation/civil-works-plan.py'],
 'engineering/network-planning/baghdad/manifest.json':
  ['tools/automation/osr-python','tools/automation/integrated-network-plan.py'],
 'docs/certification/connected-engineering-report.json':
  ['tools/automation/osr-python','tools/automation/connected_assurance.py'],
 'engineering/assurance/battery-cooling/qualification-report.json':
  ['tools/automation/osr-python','tools/automation/subsystem_qualification.py'],
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
 'docs/component-rfc-readiness.json':['tools/automation/osr-python','tools/automation/component_rfc_readiness.py'],
 # Aggregate source digests require their own canonical checker, not a file-hash guess.
 'docs/operating/readiness.json':['tools/automation/osr-python','tools/automation/operating-readiness.py'],
 # These numerical reports have no source fingerprint: freshness needs the real native --check.
 'docs/certification/software-soak-report.json':['cargo','run','--quiet','--release','-p','osr-sim','--bin','osr-soak-evidence'],
 'docs/certification/software-soak-report.md':['cargo','run','--quiet','--release','-p','osr-sim','--bin','osr-soak-evidence'],
}
HISTORICAL={'engineering/civil_exploration/examples/automated-parts-review.json'}
KEYS={'source_sha256','source_sha256s','sources_sha256','source_hashes','sources'}
# Only these owner/schema pairs declare these maps as repository-root input byte hashes.
# Output/artifact-relative and context-free body hashes must not be generalized.
OWNER_INPUT_MAPS={
 'docs/certification/digital-assurance-report.json':
  ('osr-digital-standards-thread/2', {'dependency_hashes','evidence_hashes','input_hashes'}),
 'docs/component-rfc-readiness.json':
  ('osr-component-rfc-packages/1', {'inventory_hashes','evidence_hashes'}),
}

# This producer's scalar is the exact bytes of one fixed repository input.
OWNER_SCALAR_INPUTS={
 'docs/component-rfc-readiness.json':
  ('osr-component-rfc-packages/1', {'source_sha256':'lib/templates/component-rfc-packages.toml'}),
}

# These schemas cannot establish freshness from repository-file maps alone.
OWNER_CHECK_REQUIREMENTS={
 'docs/certification/software-soak-report.json':dict(
  schema='osr-software-soak/1',
  command=['cargo','run','--quiet','--release','-p','osr-sim','--bin','osr-soak-evidence','--','--check'],
  reason='No source fingerprint: numerical freshness requires the actual native simulation check.'),
 'docs/operating/readiness.json':dict(
  schema='osr-operating-readiness/2',
  command=['tools/automation/osr-python','tools/automation/operating-readiness.py','--check'],
  reason='Aggregate source digest: freshness requires the canonical owner checker.'),
}


def dependency_maps(value, *, publication_outputs=False, extra_keys=frozenset()):
    if isinstance(value,dict):
        for key,child in value.items():
            if (key in KEYS or key in extra_keys or publication_outputs and key=='outputs_sha256') and isinstance(child,dict):
                for name,digest in child.items():
                    if isinstance(name,str) and isinstance(digest,str) and len(digest)==64 and ('/' in name or Path(name).suffix):
                        yield name,digest
            yield from dependency_maps(child,publication_outputs=publication_outputs,extra_keys=extra_keys)
    elif isinstance(value,list):
        for child in value:yield from dependency_maps(child,publication_outputs=publication_outputs,extra_keys=extra_keys)


def impact(paths=None,root=ROOT):
    if paths is None:
        paths=subprocess.check_output(['git','ls-files','-z','*.json'],cwd=root).decode().split('\0')
    cache={};rows=[];owner_checks=[]
    for name in paths:
        if not name:continue
        path=root/name
        if not path.is_file():continue
        raw=path.read_bytes()
        owner_schema,owner_keys=OWNER_INPUT_MAPS.get(name,(None,frozenset()))
        if name not in OWNER_CHECK_REQUIREMENTS and not any(('"'+key+'"').encode() in raw for key in KEYS|owner_keys):continue
        try:record=json.loads(raw)
        except (ValueError,UnicodeDecodeError):continue
        required_check=OWNER_CHECK_REQUIREMENTS.get(name)
        if required_check and isinstance(record,dict) and record.get('schema')==required_check['schema']:
            owner_checks.append(dict(artifact=name,command=required_check['command'],reason=required_check['reason'],
                executed=False,freshness='not-assessed-by-hash-scan'))
        extra_keys=owner_keys if isinstance(record,dict) and record.get('schema')==owner_schema else frozenset()
        scalar_schema,scalar_inputs=OWNER_SCALAR_INPUTS.get(name,(None,{}))
        dependencies=set(dependency_maps(record,publication_outputs=path.name=='publication-manifest.json',extra_keys=extra_keys))
        if isinstance(record,dict) and record.get('schema')==scalar_schema:
            for key,source in scalar_inputs.items():
                expected=record.get(key)
                if isinstance(expected,str) and len(expected)==64:dependencies.add((source,expected))
        changes=[]
        for source,expected in sorted(dependencies):
            target=(root/source).resolve()
            if not target.is_relative_to(root.resolve()):raise ValueError('dependency escapes repository: '+source)
            if source not in cache:cache[source]=hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None
            if cache[source]!=expected:changes.append(dict(source=source,recorded_sha256=expected,current_sha256=cache[source]))
        if changes:
            state='stale-current' if name in OWNERS else 'historical' if name in HISTORICAL else 'scope-review-required'
            rows.append(dict(artifact=name,state=state,changed_sources=changes,regenerate_command=OWNERS.get(name)))
    return dict(schema='osr-dependency-impact/1',invalidated=rows,current_regeneration_required=[r['artifact'] for r in rows if r['state']=='stale-current'],
        canonical_owner_checks_required=owner_checks,canonical_owner_checks_executed=False,hash_scan_only=True,
        acceptance_changed=False,source_hashes_rewritten=False)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);p.add_argument('--check-current',action='store_true',help='fail on stale current declared file hashes; canonical owner checks remain separate');a=p.parse_args()
    report=impact()
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(invalidated_artifacts=len(report['invalidated']),current_regeneration_required=report['current_regeneration_required'],
        canonical_owner_checks_required=report['canonical_owner_checks_required'],hash_scan_only=report['hash_scan_only'],
        canonical_owner_checks_executed=report['canonical_owner_checks_executed'])))
    if a.check_current and report['current_regeneration_required']:raise SystemExit(1)


if __name__=='__main__':main()
