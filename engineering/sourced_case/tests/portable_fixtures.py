"""Portable test definitions: current baselines and tracked source-bound inputs.

Only ordinary bounded tar members are read. Archived Python is never imported
or executed. Cached immutable JSON bytes are decoded anew for every caller.
"""
from functools import lru_cache
from pathlib import Path,PurePosixPath
from hashlib import sha256
import json,tarfile
from engineering.station_rail.common import encoded,identity
from engineering.reference_cell.vehicles import evaluate
ROOT=Path(__file__).resolve().parents[3]
PUBLICATION=ROOT/'docs/design-engine/sourced-bolster'
MAX_ARCHIVE=128*1024**2
MAX_RAW=512*1024**2
MAX_MEMBER=64*1024**2
EXPECTED={'equipped-v1':'d88675872724a670f773ccb439cb1b505c7acd470751141ffdaad1cadcf446b4','equipped-v4':'d1b97ba718ff687336a4cdfa828cd3e39cb689544fd37f524eca05491165e710',
          'bolstered-v4':'4fd7a56ff432b4a6e86c9722b5677a6b34893e9ac840b7e1dff5148ba09aad8b'}


@lru_cache(maxsize=5)
def _baseline_bytes(name):
    return encoded(evaluate(name,root=ROOT))


def baseline(name='V1'):
    return json.loads(_baseline_bytes(name))


def _name(name):
    path=PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '\\' in name or path.as_posix()!=name:raise ValueError('Unsafe fixture archive member')
    return name


@lru_cache(maxsize=1)
def _published_inputs():
    descriptor=PUBLICATION/'bolster-cell.json';archive=PUBLICATION/'bolster-cell.tar.gz'
    if descriptor.is_symlink() or archive.is_symlink() or not descriptor.is_file() or not archive.is_file():raise ValueError('Tracked ordinary fixture publication required')
    if descriptor.stat().st_size>4*1024**2 or archive.stat().st_size>MAX_ARCHIVE:raise ValueError('Fixture archive size limit')
    d=json.loads(descriptor.read_bytes())
    if d['publication_id']!=identity({k:v for k,v in d.items() if k!='publication_id'}):raise ValueError('Fixture descriptor identity differs')
    h=sha256()
    with archive.open('rb') as stream:
        while block:=stream.read(1024**2):h.update(block)
    if h.hexdigest()!=d['archive_sha256'] or archive.stat().st_size!=d['archive_bytes']:raise ValueError('Tracked fixture archive differs')
    wanted={'equipped-v4':'ancestor-native/input.json','bolstered-v4':'bolster-native/input.json'};result={}
    with tarfile.open(archive,'r|gz') as tar:
        seen=set();total=0;byname={name:key for key,name in wanted.items()}
        for member in tar:
            name=_name(member.name)
            if name in seen or name not in d['files'] or not member.isfile() or member.issym() or member.islnk():raise ValueError('Closed ordinary fixture members required')
            seen.add(name);total+=member.size
            if len(seen)>64 or member.size<0 or total>MAX_RAW:raise ValueError('Fixture inventory/budget differs')
            if member.size!=d['files'][name]['bytes']:raise ValueError('Fixture member length differs')
            if name not in byname:continue
            key=byname[name];row=d['files'][name]
            if not 0<member.size<=MAX_MEMBER:raise ValueError('Fixture input length differs')
            raw=tar.extractfile(member).read(MAX_MEMBER+1)
            if len(raw)!=member.size or sha256(raw).hexdigest()!=row['sha256']:raise ValueError('Fixture input hash differs')
            value=json.loads(raw)['vehicle']
            if value['candidate_id']!=EXPECTED[key] or value['evaluation_id']!=identity({k:v for k,v in value.items() if k!='evaluation_id'}):raise ValueError('Exact published physical/evaluation fixture differs')
            result[key]=encoded(value)
        if seen!=set(d['files']) or set(result)!=set(wanted):raise ValueError('Fixture archive closure differs')
    return result


def published(kind):
    return json.loads(_gfrp_input() if kind=='equipped-v1' else _published_inputs()[kind])


@lru_cache(maxsize=1)
def _gfrp_input():
    folder=ROOT/'docs/design-engine/sourced-case';descriptor=folder/'structural-methods.json';archive=folder/'structural-methods.tar.gz'
    if descriptor.is_symlink() or archive.is_symlink() or not descriptor.is_file() or not archive.is_file():raise ValueError('Tracked GFRP structural publication required')
    if descriptor.stat().st_size>4*1024**2 or archive.stat().st_size>MAX_ARCHIVE:raise ValueError('GFRP fixture archive budget exceeded')
    d=json.loads(descriptor.read_bytes())
    if d['publication_id']!=identity({k:v for k,v in d.items() if k!='publication_id'}):raise ValueError('GFRP publication identity differs')
    h=sha256()
    with archive.open('rb') as stream:
        while block:=stream.read(1024**2):h.update(block)
    if h.hexdigest()!=d['files_sha256'][archive.name]:raise ValueError('GFRP fixture archive differs')
    packages=d['packages']
    if not 1<=len(packages)<=6:raise ValueError('Bounded native package count required')
    expected={}
    for package in packages:
        prefix=_name(package['name'])
        for name,value in package['files_sha256'].items():
            full=_name(prefix+'/'+name)
            if full in expected:raise ValueError('Duplicate GFRP fixture member')
            expected[full]=value
    wanted='distributed-V1/input.json';seen=set();total=0;result=None
    with tarfile.open(archive,'r|gz') as tar:
        for member in tar:
            name=_name(member.name)
            if name in seen or name not in expected or not member.isfile() or member.issym() or member.islnk():raise ValueError('Ordinary closed GFRP fixture required')
            seen.add(name);total+=member.size
            if len(seen)>64 or member.size<0 or total>MAX_RAW:raise ValueError('GFRP decompression budget exceeded')
            if name!=wanted:continue
            if not 0<member.size<=MAX_MEMBER:raise ValueError('Bounded GFRP input required')
            raw=tar.extractfile(member).read(MAX_MEMBER+1)
            if len(raw)!=member.size or sha256(raw).hexdigest()!=expected[name]:raise ValueError('GFRP input payload differs')
            value=json.loads(raw)['vehicle']
            if value['candidate_id']!=EXPECTED['equipped-v1'] or value['evaluation_id']!=identity({k:v for k,v in value.items() if k!='evaluation_id'}):raise ValueError('Exact GFRP candidate/evaluation differs')
            result=encoded(value)
    if seen!=set(expected) or result is None:raise ValueError('GFRP fixture closure differs')
    return result
