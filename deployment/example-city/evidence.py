"""Commit-bound public city acceptance artifacts used by the software release gate."""
import hashlib
import json
from pathlib import Path
import subprocess

REQUIRED=('report.json','expansion-report.json','contract-report.json','business-report.json','disposition-report.json','ui-report.json','full-network/report.json')


def validate(folder,commit=None):
    folder=Path(folder);manifest=json.loads((folder/'city-evidence.json').read_text())
    if manifest.get('schema')!='osr-city-release-evidence/1' or manifest.get('passed') is not True:
        raise ValueError('Invalid city release manifest')
    if not manifest.get('clean_source') or (commit is not None and manifest.get('commit')!=commit):
        raise ValueError('City evidence must bind the clean release commit')
    if manifest.get('scenario_source',{}).get('commit')!=manifest.get('commit') or manifest.get('scenario_source',{}).get('clean_source') is not True:
        raise ValueError('Scenario did not start on the clean release commit')
    if not set(REQUIRED)<=set(manifest.get('reports',{})):raise ValueError('City release reports missing')
    for name,expected in manifest['reports'].items():
        path=(folder/name).resolve()
        if not path.is_relative_to(folder.resolve()) or not path.is_file():raise ValueError('Invalid report path')
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('City report checksum mismatch: '+name)
        data=json.loads(raw)
        if data.get('passed') is not True:raise ValueError('City report failed/incomplete: '+name)
        checks=data.get('checks')
        if name!='full-network/report.json' and (not checks or any(not (c.get('passed') is True if isinstance(c,dict) else isinstance(c,str) and bool(c)) for c in checks)):
            raise ValueError('City checks failed/empty: '+name)
    return manifest


def record(h):
    def git(*args):return subprocess.check_output(['git',*args],cwd=h.ROOT,text=True).strip()
    files={}
    for name in REQUIRED:
        path=h.OUTPUT/name
        if not path.is_file():raise ValueError('Run the required city scenario first: '+name)
        files[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    origin=json.loads((h.OUTPUT/'run-started.json').read_text())
    manifest=dict(schema='osr-city-release-evidence/1',commit=git('rev-parse','HEAD'),source_tree=git('rev-parse','HEAD^{tree}'),
        clean_source=not bool(git('status','--porcelain','--untracked-files=normal')),passed=True,reports=files,scenario_source=origin,
        scope='Representative integrated software lifecycle; explicit coverage gaps remain',physical_acceptance=False)
    h.write(h.OUTPUT/'city-evidence.json',manifest)
    try:validate(h.OUTPUT,manifest['commit'])
    except (ValueError,KeyError,TypeError) as error:
        manifest.update(passed=False,error=str(error));h.write(h.OUTPUT/'city-evidence.json',manifest)
        raise
    print('PASS commit-bound example-city release evidence:',manifest['commit'])
