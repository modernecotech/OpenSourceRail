"""Verify one unchanged thermal packet under its already retained source epoch.

Byte verification grants no current-evaluator admission. Optional replay uses a
fresh private source context; it never refreshes the original packet or pins.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded,identity,digest
from . import retained_service_energy_epoch as extra
from . import retained_service_energy_materialize as materializer
from . import retained_source_epoch as retained
from . import retained_packet_materialize as prior

PRODUCER='engineering/design_search/retained_periodic_thermal.py'
PACKET='docs/design-engine/periodic-thermal-research'
NAME='periodic-thermal-research/manifest.json'
ARCHIVE='docs/design-engine/retained-service-energy-extra/original/worker-v7/archive'
PINS='docs/design-engine/retained-service-energy-extra/original/worker-v7/pins.json'
HELPERS=(PRODUCER,materializer.PRODUCER,'engineering/design_search/retained_service_energy_epoch.py',
    'engineering/design_search/retained_source_epoch.py','engineering/design_search/retained_packet_materialize.py')
MODULE_FILES=dict(zip(HELPERS,(__file__,materializer.__file__,extra.__file__,retained.__file__,prior.__file__)))
LOADED={name:digest(path) for name,path in MODULE_FILES.items()}
TESTS=('engineering/design_search/tests/test_periodic_thermal_research.py',
       'engineering/design_search/tests/test_periodic_thermal_publication.py')
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
    manufacturing_release=False,operating_release=False,current_evaluator_admission=False,
    physical_equivalence_proven=False,selected_reference_changed=False)


def _helpers(root):
    values={}
    for name,path in MODULE_FILES.items():
        actual=extra._file_data(retained._ordinary(Path(root)/name))[0]
        if actual!=LOADED[name] or digest(path)!=LOADED[name]:raise ValueError('Retained verifier source epoch changed: '+name)
        values[name]=actual
    return values


def _inspect(root):
    root=retained._ordinary(Path(root).absolute(),directory=True);helpers=_helpers(root)
    pins,pin_sha,_=extra._read_json(root/PINS)
    meta,_,_,hashes=materializer._preflight(root/ARCHIVE,pins,materializer.PINS_ID,materializer.ARCHIVE_ID)
    manifest,msha,_=extra._read_json(root/PACKET/'manifest.json');record=meta['records'][NAME]
    if (msha!=pins['manifest_sha256'][NAME] or msha!=record['manifest_sha256']
            or manifest.get('schema')!=extra.CATALOG[NAME][0]
            or manifest.get('manifest_id')!=pins['manifest_ids'][NAME]
            or manifest.get('manifest_id')!=retained._id({k:v for k,v in manifest.items() if k!='manifest_id'})
            or manifest.get('reference_candidate_id')!=extra.REFERENCE):
        raise ValueError('Externally pinned original periodic manifest differs')
    extra._held(manifest)
    sources=retained._checked_map(manifest.get('source_sha256'))
    if any(meta['original_source_sha256'].get(k)!=v for k,v in sources.items()):
        raise ValueError('Thermal source bytes are outside the authenticated original epoch')
    inventory=extra._inventory(root/PACKET)
    if inventory!=meta['folders'][PACKET]:raise ValueError('Original periodic packet inventory differs')
    payload=retained._checked_map(manifest.get('files_sha256'))
    if payload!=record['declared_payload_sha256'] or any(inventory['files_sha256'].get(k)!=v for k,v in payload.items()):
        raise ValueError('Original periodic declared payload differs')
    result,_,_=extra._read_json(root/PACKET/'result.json')
    if (result.get('schema')!='osr-periodic-thermal-research/1'
            or result.get('evaluation_id')!=manifest.get('evaluation_id')
            or result.get('evaluation_id')!=retained._id({k:v for k,v in result.items() if k!='evaluation_id'})):
        raise ValueError('Original periodic result identity differs')
    extra._held(result)
    dependencies={str(Path(PACKET)/name):sha for name,sha in inventory['files_sha256'].items()}
    dependencies.update({PINS:pin_sha,str(Path(ARCHIVE)/'manifest.json'):hashes[0],
        str(Path(ARCHIVE)/'sources.tar.gz'):hashes[1],**helpers})
    proof=dict(verified=True,scope='original-periodic-packet-and-authenticated-producer-bytes-only',
        original_manifest_id=manifest['manifest_id'],original_manifest_sha256=msha,
        archive_id=materializer.ARCHIVE_ID,pins_id=materializer.PINS_ID,git_commit=extra.GIT_COMMIT,
        original_source_count=len(sources),authenticated_epoch_source_count=len(meta['original_source_sha256']),
        packet_file_count=inventory['file_count'],packet_bytes=inventory['bytes'],
        numerical_reexecuted=False,dependency_sha256=dict(sorted(dependencies.items())),**FLAGS)
    proof['verification_id']=identity(proof)
    return proof,meta,manifest


def verify(root=ROOT):
    """No numerical execution, current-source substitution or packet writes."""
    proof,_,_=_inspect(root)
    if any(extra._file_data(Path(root)/name)[0]!=sha for name,sha in proof['dependency_sha256'].items()):
        raise ValueError('Retained periodic evidence changed during verification')
    if _inspect(root)[0]!=proof:raise ValueError('Retained periodic inventories changed during verification')
    _helpers(root)
    return proof


def _destination(output,root):
    output=Path(output).absolute();root=Path(root).resolve()
    if output.exists() or output.is_symlink():raise FileExistsError('Fresh private context required')
    for path in (output.parent,*output.parent.parents):
        if path.is_symlink():raise ValueError('Ordinary private context parents required')
        manifest=path/'manifest.json'
        if manifest.is_file() and not manifest.is_symlink() and manifest.stat().st_size<=extra.MAX_JSON:
            try:schema=retained._json(manifest.read_bytes()).get('schema')
            except ValueError:schema=None
            if schema in ('osr-service-energy-packet-materialization/1','osr-retained-service-energy-extra-epoch/1'):
                raise ValueError('Context must be separate from sealed historical trees')
    if output==root or root.is_relative_to(output) or (output.is_relative_to(root) and not output.is_relative_to(root/'build')):
        raise ValueError('Use a separate private context, or this checkout build directory')
    retained._ordinary(output.parent,directory=True)
    return output


def _write_file(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if extra._file_data(path,retained.MAX_SOURCE_BYTES,materialize=True)[1]!=raw:raise ValueError('Conflicting original context file')
        return
    with path.open('xb') as stream:stream.write(raw)


def _test_inputs(root):
    values={name:extra._git_bytes(Path(root),name) for name in TESTS}
    # Current publication regressions must not silently disappear merely because
    # the replay executes an older producer. Hold when the test contract differs.
    current_tests={}
    for name in TESTS:
        current_sha,current,_=extra._file_data(Path(root)/name,extra.MAX_JSON,materialize=True)
        if current!=values[name]:raise ValueError('Current periodic test contract differs from the pinned original; declare and run the changed tests explicitly')
        current_tests[name]=current_sha
    return values,current_tests


def _expected_context(meta,test_values):
    expected=dict(meta['original_source_sha256'])
    for name,sha in meta['folders'][PACKET]['files_sha256'].items():
        target=str(Path(PACKET)/name)
        if target in expected and expected[target]!=sha:raise ValueError('Conflicting source and packet context')
        expected[target]=sha
    for name,raw in test_values.items():
        sha=sha256(raw).hexdigest()
        if name in expected and expected[name]!=sha:raise ValueError('Pinned test conflicts with source archive')
        expected[name]=sha
    return dict(sorted(expected.items()))


def _context_inventory(context,expected):
    actual=extra._inventory(context)
    directories=sorted({str(parent) for name in expected for parent in Path(name).parents if str(parent)!='.'})
    if actual['files_sha256']!=expected or actual['directories']!=directories:
        raise ValueError('Prepared original source coverage or directory inventory differs')
    return actual


def prepare_context(output,*,root=ROOT):
    """Copy authenticated original sources and packet; offline Git supplies tests.

    The extra materializer's sealed tree is never modified or reused as a work
    tree. A failed private destination is retained rather than auto-cleaned.
    """
    proof,meta,manifest=_inspect(root);out=_destination(output,root)
    if shutil.disk_usage(out.parent).free<256*1024**2:raise ValueError('At least256MiB free for one bounded context required')
    out.mkdir(mode=0o700);context=out/'root';context.mkdir(mode=0o700)
    expected=dict(meta['original_source_sha256'])
    try:
        with tarfile.open(Path(root)/ARCHIVE/'sources.tar.gz','r:gz') as archive:
            for member in archive:
                if member.name not in expected or not member.isfile():raise ValueError('Unexpected retained source member')
                raw=archive.extractfile(member).read(retained.MAX_SOURCE_BYTES+1)
                if len(raw)>retained.MAX_SOURCE_BYTES or sha256(raw).hexdigest()!=expected[member.name]:raise ValueError('Retained source member changed')
                _write_file(context/member.name,raw)
        for name,sha in meta['folders'][PACKET]['files_sha256'].items():
            _,raw,_=extra._file_data(Path(root)/PACKET/name,extra.MAX_FOLDER_BYTES,materialize=True)
            if sha256(raw).hexdigest()!=sha:raise ValueError('Original packet changed before copying')
            target=str(Path(PACKET)/name)
            if target in expected and expected[target]!=sha:raise ValueError('Conflicting source and packet context')
            expected[target]=sha;_write_file(context/target,raw)
        test_sources={};test_values,current_tests=_test_inputs(root)
        for name,raw in test_values.items():
            sha=sha256(raw).hexdigest()
            if name in expected and expected[name]!=sha:raise ValueError('Pinned test conflicts with source archive')
            expected[name]=sha;test_sources[name]=sha;_write_file(context/name,raw)
        if verify(root)['verification_id']!=proof['verification_id']:raise ValueError('Original inputs changed during context preparation')
        expected=_expected_context(meta,test_values);_context_inventory(context,expected)
        value=dict(schema='osr-retained-periodic-source-context/1',context_root=str(context),
            retained_verification_id=proof['verification_id'],git_commit=extra.GIT_COMMIT,
            archive_id=materializer.ARCHIVE_ID,pins_id=materializer.PINS_ID,
            source_sha256=expected,test_source_sha256=test_sources,current_test_source_sha256=current_tests,
            test_source_origin='Offline exact Git blob at the already pinned original commit',
            original_manifest_id=manifest['manifest_id'],worker_handoff_id=manifest['worker_handoff_id'],
            request_id=manifest['request_id'],evaluation_id=manifest['evaluation_id'],
            numerical_reexecuted=False,**FLAGS)
        value['context_id']=identity(value)
        _write_file(out/'context.json',encoded(value));return value
    except BaseException as exc:
        raise RuntimeError('Failed private source context retained at '+str(out)) from exc


def _context(output,root):
    output=retained._ordinary(Path(output).absolute(),directory=True)
    value,_,_=extra._read_json(output/'context.json');context=output/'root'
    proof,meta,manifest=_inspect(root);test_values,current_tests=_test_inputs(root)
    expected=_expected_context(meta,test_values)
    keys={'schema','context_root','retained_verification_id','git_commit','archive_id','pins_id',
        'source_sha256','test_source_sha256','current_test_source_sha256','test_source_origin',
        'original_manifest_id','worker_handoff_id','request_id','evaluation_id','numerical_reexecuted','context_id',*FLAGS}
    if (value.get('schema')!='osr-retained-periodic-source-context/1'
            or set(value)!=keys
            or value.get('context_id')!=identity({k:v for k,v in value.items() if k!='context_id'})
            or value.get('context_root')!=str(context)
            or any(value.get(k) is not False for k in FLAGS)
            or value.get('numerical_reexecuted') is not False
            or value.get('git_commit')!=extra.GIT_COMMIT
            or value.get('archive_id')!=materializer.ARCHIVE_ID
            or value.get('pins_id')!=materializer.PINS_ID
            or proof['verification_id']!=value.get('retained_verification_id')
            or value.get('source_sha256')!=expected
            or value.get('test_source_sha256')!={name:sha256(raw).hexdigest() for name,raw in test_values.items()}
            or value.get('current_test_source_sha256')!=current_tests
            or value.get('test_source_origin')!='Offline exact Git blob at the already pinned original commit'
            or any(value.get(key)!=manifest[key] for key in ('worker_handoff_id','request_id','evaluation_id'))
            or value.get('original_manifest_id')!=manifest['manifest_id']):
        raise ValueError('Private original source context identity, input bytes or scope differs')
    _context_inventory(context,expected)
    if _inspect(root)[0]!=proof:raise ValueError('Original evidence changed during context checking')
    return output,context,value


BOOTSTRAP=r'''
import importlib.abc,importlib.machinery,json,os,pathlib,resource,runpy,socket,subprocess,sys
resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3));resource.setrlimit(resource.RLIMIT_CPU,(90,90))
resource.setrlimit(resource.RLIMIT_FSIZE,(8*1024**2,8*1024**2))
context=pathlib.Path(sys.argv[1]).resolve();result_path=pathlib.Path(sys.argv[2]);pins=json.loads(pathlib.Path(sys.argv[3]).read_bytes())
def blocked(*args,**kwargs):raise RuntimeError('External process/network access is not permitted by this replay harness')
socket.socket.connect=blocked;socket.socket.connect_ex=blocked;socket.create_connection=blocked;socket.getaddrinfo=blocked
subprocess.Popen=blocked;os.system=blocked
class ArchivedEngineering(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname!='engineering' and not fullname.startswith('engineering.'):return None
        spec=importlib.machinery.PathFinder.find_spec(fullname,[str(context)] if fullname=='engineering' else path)
        if spec is None:raise ModuleNotFoundError('Source absent from original context: '+fullname)
        locations=([spec.origin] if spec.origin not in (None,'namespace') else list(spec.submodule_search_locations or []))
        if any(not pathlib.Path(p).resolve().is_relative_to(context) for p in locations):raise ImportError('Current source fallback refused')
        return spec
sys.meta_path.insert(0,ArchivedEngineering())
import pytest
code=pytest.main(['-q','-p','no:cacheprovider','--import-mode=importlib',
    'engineering/design_search/tests/test_periodic_thermal_research.py',
    'engineering/design_search/tests/test_periodic_thermal_publication.py'])
if code:raise SystemExit(code)
from engineering.design_search import periodic_thermal_publication as publication
result=publication.verify(expected_manifest_id=pins['original_manifest_id'],expected_handoff_id=pins['worker_handoff_id'],
    expected_request_id=pins['request_id'],expected_evaluation_id=pins['evaluation_id'])
origins={name:str(pathlib.Path(module.__file__).resolve().relative_to(context)) for name,module in sys.modules.items()
    if name.startswith('engineering.') and getattr(module,'__file__',None)}
result.update(original_source_replay=True,loaded_engineering_modules=origins,tests_passed=True)
with result_path.open('x') as stream:json.dump(result,stream,sort_keys=True)
'''


def replay(output,*,root=ROOT):
    """Prepare and replay the original tests/publication in one bounded child."""
    prepare_context(output,root=root);out,context,value=_context(output,root)
    temporary=out/'tmp';temporary.mkdir(mode=0o700)
    environment=dict(os.environ,PYTHONPATH=str(context),PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1',TMPDIR=str(temporary),
        PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
        GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0')
    for name in ('PYTHONHOME','PYTHONSTARTUP','PYTEST_ADDOPTS'):environment.pop(name,None)
    logs=out/'logs';logs.mkdir();child_result=out/'child-result.json'
    with (logs/'stdout.log').open('xb') as stdout,(logs/'stderr.log').open('xb') as stderr:
        try:child=subprocess.run([sys.executable,'-c',BOOTSTRAP,str(context),str(child_result),str(out/'context.json')],
            cwd=context,env=environment,stdout=stdout,stderr=stderr,timeout=120,check=False)
        except subprocess.TimeoutExpired as exc:raise RuntimeError('Original replay timed out; private context retained at '+str(out)) from exc
    if child.returncode:raise RuntimeError('Original replay failed; private context retained at '+str(out))
    _context(out,root)
    result,_,_=extra._read_json(child_result)
    if (result.get('verified') is not True or result.get('manifest_id')!=value['original_manifest_id']
            or result.get('tests_passed') is not True or result.get('original_source_replay') is not True
            or any(result.get(k) is not False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release'))):
        raise ValueError('Original replay result or non-promotion disposition differs')
    report=dict(schema='osr-retained-periodic-replay/1',verified=True,context_id=value['context_id'],
        original_manifest_id=value['original_manifest_id'],original_epoch_numerical_reexecuted=True,
        current_evaluator_numerical_reexecuted=False,source_context=str(context),
        stdout_sha256=digest(logs/'stdout.log'),stderr_sha256=digest(logs/'stderr.log'),
        result_sha256=digest(child_result),python_executable_sha256=digest(Path(sys.executable).resolve()),
        budgets=dict(wall_s=120,CPU_s=90,address_space_bytes=1024**3,threads=1),
        isolation='Separate private source root and subprocess with resource limits; engineering import-origin and Python network/process guards; no OS sandbox',**FLAGS)
    report['replay_id']=identity(report);_write_file(out/'replay.json',encoded(report));return report


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('verify','prepare-context','replay'))
    parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--output',type=Path);args=parser.parse_args(argv)
    if args.action=='verify':result=verify(args.root)
    else:
        if args.output is None:parser.error('--output is required')
        result=(prepare_context if args.action=='prepare-context' else replay)(args.output,root=args.root)
    print(json.dumps(result,sort_keys=True));return 0


if __name__=='__main__':raise SystemExit(main())
