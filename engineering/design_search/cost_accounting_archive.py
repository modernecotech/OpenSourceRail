"""Preserve the exact pre-partition accounting record and its declared producers.

This is byte archival verification, not numerical replay. The original producers
are never imported or executed. Verification needs neither Git nor host-current
producer equality; the pinned original record authenticates its own 17 declared
source hashes. Recursive dependency completeness and physical evidence are not
claimed. The archive is separate from all current cost publications.
"""
import argparse
import gzip
from hashlib import sha256
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
import tempfile

from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded, identity
from . import portable_gzip

PRODUCER='engineering/design_search/cost_accounting_archive.py'
COMMIT='5b9b943e198dd22bdabc57d705e7cc1f1462bd7f'
RECORD='docs/design-engine/current/exports/selected-system-cost.json'
RECORD_SHA256='e779d5faac7f58c518376ac2bf52a3df30be45637ccbd7f40239aed7cae2d5c9'
ESTIMATE_ID='9dc8679953032252e03217c5821ce0d17bfc78b4d053647c0cabb43e31d00f34'
OUTPUT='docs/archives/cost-accounting-pre-partition'
ARCHIVE='original-accounting.tar.gz'
MAX_MEMBER=32*1024**2
MAX_TAR=64*1024**2
MAX_ARCHIVE=16*1024**2
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
    operating_release=False,configuration_adopted=False,selected_reference_changed=False)
CORRECTIONS=[
    dict(code='fastener-account-partition',reason='Overlapping material and complete-fastener-set accounts require a disjoint accounting boundary.'),
    dict(code='disjoint-renewal-bases',reason='Generic renewal bases and explicitly scheduled equipment replacements require disjoint scope.'),
    dict(code='fractional-life-and-horizon',reason='Replacement schedules must preserve fractional service lives and the declared economic horizon.')]


def _hash(raw):return sha256(raw).hexdigest()


def _name(name):
    if (not isinstance(name,str) or not name or '\\' in name or ':' in name
            or name!=PurePosixPath(name).as_posix() or name.startswith('/')
            or any(part in ('','.','..') for part in name.split('/'))):
        raise ValueError('Canonical repository-relative archive path required')
    return name


def _digest(value):
    return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)


def _json(raw):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError('Duplicate JSON key: '+key)
            result[key]=value
        return result
    def constant(_value):raise ValueError('Nonfinite JSON constant')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=constant)


def _record(raw):
    if _hash(raw)!=RECORD_SHA256:raise ValueError('Pinned original accounting record bytes differ')
    value=_json(raw)
    if (value.get('schema')!='osr-selected-v06-whole-system-class-c-cost/1'
            or value.get('cost_estimate_id')!=ESTIMATE_ID
            or value['cost_estimate_id']!=identity({k:v for k,v in value.items() if k!='cost_estimate_id'})
            or any(value.get(k) is not False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release'))):
        raise ValueError('Original accounting identity or non-promoting disposition differs')
    sources=value.get('source_sha256')
    if not isinstance(sources,dict) or len(sources)!=17:
        raise ValueError('Exactly 17 original declared producers required')
    for name,wanted in sources.items():
        _name(name)
        if name==RECORD or not _digest(wanted):raise ValueError('Invalid original producer binding')
    lines=value.get('cost_line_items')
    if (not isinstance(lines,list) or not lines or any(not isinstance(line,dict) or not _digest(line.get('line_id')) for line in lines)
            or len({line['line_id'] for line in lines})!=len(lines)):
        raise ValueError('Original unique line identities required')
    return value


def _summary(record):
    return {key:record[key] for key in ('cost_estimate_id','candidate_id','selection_id','vehicle_evaluation_id',
        'vehicle_cost_estimate_id','scenario_id','currency','estimate_class','required_cost_scopes',
        'factory_gate_cost_iqd','delivered_cost_iqd','model_based_installed_CAPEX_iqd',
        'model_based_whole_life_NPV_iqd','scope_totals_iqd')} | {
        'cost_line_ids':[line['line_id'] for line in record['cost_line_items']]}


def _git_file(root,name):
    _name(name)
    environment={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
    environment.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GIT_OPTIONAL_LOCKS='0',GIT_TERMINAL_PROMPT='0')
    def git(*arguments):
        result=subprocess.run(['git','--no-optional-locks','-c','core.fsmonitor=false',
            '-c','core.packedGitWindowSize=16m','-c','core.packedGitLimit=64m',*arguments],
            cwd=root,env=environment,capture_output=True,timeout=30)
        if result.returncode:raise ValueError('Pinned offline Git object unavailable: '+name)
        return result.stdout
    entry=git('ls-tree','-z',COMMIT,'--',name).split(b'\0')
    if len(entry)!=2 or entry[-1]!=b'' or b'\t' not in entry[0]:
        raise ValueError('Expected one original ordinary Git file: '+name)
    metadata,filename=entry[0].split(b'\t',1)
    if filename.decode()!=name or metadata.split()[:2] not in ([b'100644',b'blob'],[b'100755',b'blob']):
        raise ValueError('Original producer must be an ordinary Git blob')
    size=int(git('cat-file','-s',metadata.split()[2]))
    if not 0<=size<=MAX_MEMBER:raise ValueError('Original producer exceeds archive member budget')
    raw=git('show',COMMIT+':'+name)
    if len(raw)>MAX_MEMBER:raise ValueError('Original producer exceeds archive member budget')
    return raw


def _tar(files):
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w',format=tarfile.USTAR_FORMAT) as archive:
        for name,raw in sorted(files.items()):
            _name(name)
            info=tarfile.TarInfo(name);info.size=len(raw);info.mode=0o644;info.mtime=0
            archive.addfile(info,io.BytesIO(raw))
    raw=stream.getvalue()
    if len(raw)>MAX_TAR:raise ValueError('Original accounting package exceeds decompressed budget')
    return raw


def _manifest(files,archive_raw,tools):
    record=_record(files[RECORD]);sources=record['source_sha256']
    if set(files)!={RECORD,*sources}:raise ValueError('Exact original record and producer coverage required')
    if any(_hash(files[name])!=wanted for name,wanted in sources.items()):
        raise ValueError('Original producer bytes differ from recorded source hashes')
    if (not isinstance(tools,dict) or set(tools)!={PRODUCER,'engineering/design_search/portable_gzip.py'}
            or any(not _digest(value) for value in tools.values())):
        raise ValueError('Explicit archiving-tool digests required')
    value=dict(schema='osr-original-cost-accounting-archive/1',original_git_commit=COMMIT,
        original_record_path=RECORD,original_record_sha256=RECORD_SHA256,
        original_declared_source_sha256=sources,original_summary=_summary(record),
        archive=ARCHIVE,archive_sha256=_hash(archive_raw),
        files_sha256={name:_hash(raw) for name,raw in sorted(files.items())},
        archiving_tools_sha256=tools,known_correction_reasons=[dict(item) for item in CORRECTIONS],
        scope='Exact original cost record and its 17 top-level declared producer bytes. Stored prior calculation only; referenced assets and recursive dependency closure are not asserted.',
        prior_calculation_preserved=True,original_declared_source_coverage_complete=True,
        recursive_dependency_coverage_complete=False,current_cost_result=False,
        numerical_reexecuted=False,current_evaluator_admission=False,physical_comparison_proven=False,
        archived_producers_imported_or_executed=False,**FLAGS)
    value['manifest_id']=identity(value)
    return value


def _ordinary(path):
    path=Path(path).absolute()
    if '..' in path.parts:raise ValueError('Ordinary archive location required')
    if any(item.is_symlink() for item in (path,*path.parents)):
        raise ValueError('Archive paths cannot contain symlinks')
    return path


def verify(output):
    """Offline byte/identity/source-coverage verification; no original code runs."""
    out=_ordinary(output)
    if not out.is_dir() or {p.name for p in out.iterdir()}!={ARCHIVE,'manifest.json'}:
        raise ValueError('Exact original-accounting archive inventory required')
    mpath=_ordinary(out/'manifest.json');apath=_ordinary(out/ARCHIVE)
    if not mpath.is_file() or not apath.is_file() or mpath.stat().st_size>MAX_MEMBER or apath.stat().st_size>MAX_ARCHIVE:
        raise ValueError('Ordinary bounded archive and manifest required')
    manifest=_json(mpath.read_bytes());raw=apath.read_bytes()
    if (not isinstance(manifest,dict) or manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
            or manifest.get('archive_sha256')!=_hash(raw)):
        raise ValueError('Original accounting manifest identity or archive hash differs')
    if raw[:10]!=b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff':
        raise ValueError('Portable deterministic gzip header required')
    with gzip.GzipFile(fileobj=io.BytesIO(raw),mode='rb') as reader:
        data=reader.read(MAX_TAR+1)
    if len(data)>MAX_TAR:raise ValueError('Decompressed accounting archive exceeds budget')
    files={}
    with tarfile.open(fileobj=io.BytesIO(data),mode='r:') as archive:
        members=archive.getmembers()
        if len(members)!=18 or sum(member.size for member in members)>MAX_TAR:
            raise ValueError('Exactly 18 bounded original files required')
        for member in members:
            name=_name(member.name)
            if name in files or not member.isfile() or not 0<=member.size<=MAX_MEMBER:
                raise ValueError('Duplicate, nonordinary or oversized archive member')
            files[name]=archive.extractfile(member).read()
    if RECORD not in files or data!=_tar(files):
        raise ValueError('Canonical original accounting tar payload required')
    expected=_manifest(files,raw,manifest.get('archiving_tools_sha256'))
    if manifest!=expected:raise ValueError('Original accounting sources, summary or scope differ')
    return manifest


def build(git_root=ROOT,output=None):
    """Capture only pinned Git bytes, atomically; existing evidence is immutable."""
    root=Path(git_root).resolve();out=_ordinary(root/OUTPUT if output is None else output)
    if out.exists():return verify(out)
    raw=_git_file(root,RECORD);record=_record(raw);files={RECORD:raw}
    for name,wanted in sorted(record['source_sha256'].items()):
        files[name]=_git_file(root,name)
        if _hash(files[name])!=wanted:raise ValueError('Pinned commit producer differs: '+name)
    archive_raw=portable_gzip.compress(_tar(files))
    if len(archive_raw)>MAX_ARCHIVE:raise ValueError('Compressed original accounting archive exceeds budget')
    tools={PRODUCER:_hash(Path(__file__).read_bytes()),
        'engineering/design_search/portable_gzip.py':_hash(Path(portable_gzip.__file__).read_bytes())}
    manifest=_manifest(files,archive_raw,tools);out.parent.mkdir(parents=True,exist_ok=True)
    temporary=Path(tempfile.mkdtemp(prefix='.original-accounting-',dir=out.parent))
    try:
        (temporary/ARCHIVE).write_bytes(archive_raw);(temporary/'manifest.json').write_bytes(encoded(manifest))
        verify(temporary)
        if out.exists():raise ValueError('Archive destination appeared during capture; preserve it')
        temporary.rename(out)
    finally:
        if temporary.exists():shutil.rmtree(temporary)
    return verify(out)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('build','verify'))
    parser.add_argument('--git-root',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv);output=args.output or args.git_root/OUTPUT
    result=build(args.git_root,output) if args.action=='build' else verify(output)
    print(json.dumps(dict(manifest_id=result['manifest_id'],original_cost_estimate_id=result['original_summary']['cost_estimate_id'],
        original_producer_count=len(result['original_declared_source_sha256']),numerical_reexecuted=False,physical_accepted=False),sort_keys=True))


if __name__=='__main__':main()
