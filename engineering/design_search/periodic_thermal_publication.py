"""Publish the externally pinned synthetic periodic-thermal worker evidence."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile

from engineering.station_rail.common import digest, encoded, identity
from . import periodic_thermal_research as study
from . import installed_mass_cg_publication as support
from .installed_mass_cg_publication import _file, _ordinary, _publication_payload, _remove_staging, _rename_noreplace

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path('docs/design-engine/periodic-thermal-research')
PRODUCER = 'engineering/design_search/periodic_thermal_publication.py'
HELPER = 'engineering/design_search/installed_mass_cg_publication.py'
HANDOFF = 'handoff-v10.json'
RESULT = 'result-v10-py313.json'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False)


def _payload(folder):
    folder=_ordinary(folder);count=0;total=0;files=set();directories=set()
    for path in folder.rglob('*'):
        mode=path.lstat().st_mode
        if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            raise ValueError('Only regular files and directories are permitted')
        count+=1
        if count>512:raise ValueError('Bounded publication inventory required')
        if stat.S_ISREG(mode):
            files.add(path.relative_to(folder));size=path.stat().st_size;total+=size
            if size>16*1024*1024 or total>64*1024*1024:
                raise ValueError('Bounded publication inventory required')
        else:directories.add(path.relative_to(folder))
    implied={parent for name in files for parent in name.parents if parent!=Path('.')}
    if directories!=implied:raise ValueError('Undeclared or empty directories are not permitted')
    return _publication_payload(folder)


def _worker(folder, *, expected_handoff_id, expected_request_id, expected_evaluation_id):
    folder = _ordinary(folder)
    if (folder/'manifest.json').exists() or (folder/'manifest.json').is_symlink():
        raise ValueError('Unexpected root manifest in worker evidence')
    handoff_path = _file(folder/HANDOFF)
    if handoff_path.stat().st_size>16*1024*1024:raise ValueError('Worker handoff exceeds byte limit')
    handoff_bytes = handoff_path.read_bytes()
    handoff = study._json(handoff_bytes)
    if (handoff.get('schema') != 'osr-periodic-thermal-worker-handoff/1'
            or handoff.get('handoff_id') != expected_handoff_id
            or identity({k:v for k,v in handoff.items() if k != 'handoff_id'}) != expected_handoff_id
            or handoff.get('request_id') != expected_request_id
            or handoff.get('evaluation_id') != expected_evaluation_id
            or any(handoff.get(k) is not v for k,v in FLAGS.items())):
        raise ValueError('Externally pinned worker identity or disposition differs')
    inventory = _payload(folder)
    inventory.pop(HANDOFF, None)
    if inventory != handoff.get('files_sha256'):
        raise ValueError('Worker evidence inventory differs')
    request = study._json(_file(folder/'request.json').read_bytes())
    if identity(request) != expected_request_id:
        raise ValueError('Worker request differs')
    raw = _file(folder/RESULT).read_bytes()
    if raw != _file(folder/'result-v10-py312.json').read_bytes():
        raise ValueError('Recorded runtime outputs differ')
    result = study._json(raw)
    if (result.get('evaluation_id') != expected_evaluation_id
            or identity({k:v for k,v in result.items() if k != 'evaluation_id'}) != expected_evaluation_id
            or result.get('request_id') != expected_request_id
            or result.get('producer_sha256') != handoff.get('producer_sha256')
            or digest(_file(folder/'producer-v10.py')) != handoff.get('producer_sha256')
            or any(result.get(k) is not v for k,v in FLAGS.items())
            or any(result.get(k) is not False for k in ('configuration_adopted','selected_reference_changed','physical_journey_completed'))
            or result.get('available_motor_map_id') is not None):
        raise ValueError('Worker output, producer or disposition differs')
    if _file(handoff_path).read_bytes() != handoff_bytes or _payload(folder) != {**inventory, HANDOFF:digest(handoff_path)}:
        raise ValueError('Worker evidence changed during inspection')
    return request, result, handoff


def _sources(root):
    root = _ordinary(root)
    manifest = study._json(study._read(root,study.MANIFEST))
    source = manifest.get('source_sha256')
    if not isinstance(source, dict) or not source or len(source)>study.MAX_SOURCE_FILES:
        raise ValueError('Explicit retained study source map required')
    names = set(source) | {study.MANIFEST, study.ARTIFACT, study.PRODUCER, PRODUCER, HELPER}
    for name in names: study._relative(name)
    for value in source.values(): study._hex(value)
    result={};total=0
    for name in sorted(names):
        raw=study._read(root,name);total+=len(raw)
        if total>study.MAX_SOURCE_BYTES:raise ValueError('Bounded source byte inventory required')
        result[name]=study._sha(raw)
    if any(result[k] != v for k,v in source.items()):
        raise ValueError('Retained study source epoch differs')
    if (digest(_file(__file__)) != result[PRODUCER]
            or digest(_file(study.__file__)) != result[study.PRODUCER]
            or digest(_file(support.__file__)) != result[HELPER]):
        raise ValueError('Executing producer differs from declared source tree')
    return result


def _readme(result):
    rows=[]
    for case in result['cases']:
        p=case['periodic']
        if p['status']=='held-incomplete-trajectory':
            rows.append(f"| {case['case']} | Held: {p['reason']} | Held: {p['reason']} |")
        else:
            cells=[]
            for name in ('continuous_cooling','prelaunch_cooling_suppressed'):
                disposition=p['branch_dispositions'][name];steady=p[name]['steady_cycle']
                cells.append(f"{steady['peak_C']:.3f} °C" if disposition=='conditional-periodic-solution' and steady is not None else f"Held: {disposition}")
            rows.append(f"| {case['case']} | {cells[0]} | {cells[1]} |")
    period=result['assumptions']['headway_s']
    return ('# Conditional repeated-duty thermal sensitivity\n\n'
        'This study reconstructs synthetic train-aggregate loss from the retained selected-vehicle P1 '
        f'journey trace, with its 0–500 m command window and {period:g} s departure period. '
        'It is not a stationary-bank motor model or a result for the selected 900 m winding.\n\n'
        '| Case | Peak, continuous cooling | Peak, cooling suppressed for prelaunch |\n'
        '|---|---|---|\n'+'\n'.join(rows)+'\n\n'
        'The first hypothesis adds the prelaunch energy as an adiabatic impulse and '
        'cools continuously for the full departure period. The second suppresses all aggregate cooling during '
        'the prelaunch interval within that same period. Both repeat the recorded synthetic '
        'loss pulse unchanged with temperature and use exact exponential cooling for piecewise '
        'constant power; this is a separate assumption from the journey forward-Euler update.\n\n'
        'Incomplete cases are held and are not repeated. These calculations '
        'do not establish actual thrust, fixed-bank current or cooling, station occupancy, train-tail '
        'clearance, a physical journey or thermal qualification. Overlap, zero cooling and temperature '
        'domain limitations are recorded in the complete result. Earlier superseded attempts and '
        'failed tests are retained; some early producer bytes were not retained and their outputs '
        'are not claimed to be replayable. The original runtime is not independently attested and '
        'no filesystem or network sandbox was enforced.\n')


def publish(state, output=OUTPUT, *, root=ROOT, expected_handoff_id, expected_request_id, expected_evaluation_id):
    root=_ordinary(root); state=_ordinary(state); output=_ordinary(root/output, directory=False)
    if output.exists(): raise ValueError('Publish to a fresh output directory')
    sources=_sources(root)
    request, original, handoff=_worker(state, expected_handoff_id=expected_handoff_id,
        expected_request_id=expected_request_id, expected_evaluation_id=expected_evaluation_id)
    result=study.evaluate(root,request,expected_request_id=expected_request_id)
    if result != original: raise ValueError('Current analytical replay differs from worker')
    output.parent.mkdir(parents=True,exist_ok=True)
    temporary=Path(tempfile.mkdtemp(prefix='.thermal-study-',dir=output.parent))
    try:
        shutil.copytree(state,temporary/'original')
        (temporary/'result.json').write_bytes(encoded(result))
        (temporary/'README.md').write_text(_readme(result))
        payload=_payload(temporary)
        manifest=dict(schema='osr-periodic-thermal-publication/1',source_sha256=sources,
            files_sha256=payload,request_id=expected_request_id,worker_handoff_id=expected_handoff_id,
            evaluation_id=expected_evaluation_id,reference_candidate_id=study.REFERENCE,
            bundle_id=study.BUNDLE,configuration_adopted=False,**FLAGS)
        manifest['manifest_id']=identity(manifest)
        (temporary/'manifest.json').write_bytes(encoded(manifest))
        verify(temporary,root=root,expected_manifest_id=manifest['manifest_id'],
            expected_handoff_id=expected_handoff_id,expected_request_id=expected_request_id,
            expected_evaluation_id=expected_evaluation_id)
        if (_sources(root)!=sources or _worker(state,expected_handoff_id=expected_handoff_id,
                expected_request_id=expected_request_id,expected_evaluation_id=expected_evaluation_id)[2]!=handoff
                or _payload(temporary)!=payload
                or _file(temporary/'manifest.json').read_bytes()!=encoded(manifest)):
            raise ValueError('Sources or worker evidence changed during publication')
        _rename_noreplace(temporary,output)
    finally:
        if temporary.exists(): _remove_staging(temporary)
    return manifest['manifest_id']


def verify(folder=OUTPUT, *, root=ROOT, expected_manifest_id, expected_handoff_id,
           expected_request_id, expected_evaluation_id):
    root=_ordinary(root);folder=_ordinary(root/folder)
    manifest_path=_file(folder/'manifest.json');manifest_bytes=manifest_path.read_bytes()
    manifest=study._json(manifest_bytes)
    if (manifest.get('schema')!='osr-periodic-thermal-publication/1'
            or manifest.get('manifest_id')!=expected_manifest_id
            or identity({k:v for k,v in manifest.items() if k!='manifest_id'})!=expected_manifest_id
            or manifest.get('worker_handoff_id')!=expected_handoff_id
            or manifest.get('request_id')!=expected_request_id
            or manifest.get('evaluation_id')!=expected_evaluation_id
            or manifest.get('reference_candidate_id')!=study.REFERENCE
            or manifest.get('bundle_id')!=study.BUNDLE
            or manifest.get('configuration_adopted') is not False
            or any(manifest.get(k) is not v for k,v in FLAGS.items())
            or manifest.get('source_sha256')!=_sources(root)):
        raise ValueError('Pinned publication identity, sources or disposition differs')
    payload=_payload(folder)
    if payload!=manifest.get('files_sha256'):raise ValueError('Publication payload differs')
    request,original,_=_worker(folder/'original',expected_handoff_id=expected_handoff_id,
        expected_request_id=expected_request_id,expected_evaluation_id=expected_evaluation_id)
    result=study.evaluate(root,request,expected_request_id=expected_request_id)
    if (result!=original or result!=study._json(_file(folder/'result.json').read_bytes())
            or _readme(result)!=_file(folder/'README.md').read_text()
            or _sources(root)!=manifest['source_sha256']
            or _file(manifest_path).read_bytes()!=manifest_bytes
            or _payload(folder)!=payload):
        raise ValueError('Publication replay or source epoch differs')
    return dict(verified=True,manifest_id=expected_manifest_id,evaluation_id=expected_evaluation_id,**FLAGS)


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    create=sub.add_parser('publish');create.add_argument('--state',required=True,type=Path)
    check=sub.add_parser('verify');check.add_argument('--expected-manifest-id',required=True)
    for parser in (create,check):
        parser.add_argument('--expected-handoff-id',required=True)
        parser.add_argument('--expected-request-id',required=True)
        parser.add_argument('--expected-evaluation-id',required=True)
    args=p.parse_args();pins=dict(expected_handoff_id=args.expected_handoff_id,
        expected_request_id=args.expected_request_id,expected_evaluation_id=args.expected_evaluation_id)
    result=publish(args.state,**pins) if args.action=='publish' else verify(expected_manifest_id=args.expected_manifest_id,**pins)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':main()
