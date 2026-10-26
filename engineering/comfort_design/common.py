"""Shared identity, provenance and publication contracts for the comfort design."""
from hashlib import sha256
import gzip
import io
import json
from pathlib import Path, PurePosixPath
import re
import tarfile
from . import ROOT, FLAGS


def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def identity(value):return sha256(encoded(value)).hexdigest()


def ordinary(root,name):
    name=PurePosixPath(name)
    if name.is_absolute() or '..' in name.parts or name.as_posix()=='.':
        raise ValueError('ordinary repository-relative source path required')
    p=Path(root)/name
    if p.is_symlink() or not p.is_file():raise ValueError('missing or linked source: '+str(name))
    return p


def require_candidate(result,vehicle):
    for key in ('candidate_id','body_candidate_id','magnet_component_id'):
        if key not in vehicle or result.get(key)!=vehicle[key]:
            raise ValueError('mixed or missing '+key+' in domain result')
    return True


def sources(root=ROOT,records=()):
    root=Path(root).resolve();out={}
    for record in records:
        for name,digest in record.get('source_sha256',{}).items():
            if name in out and out[name]!=digest:raise ValueError('mixed evaluator revisions: '+name)
            out[name]=digest
    for p in sorted((root/'engineering/comfort_design').rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix in {'.py','.json','.html','.js','.css','.toml','.geo','.pro','.inp'}:
            out[p.relative_to(root).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for name in ('.github/workflows/comfort-design.yml','tools/automation/tests/verify-comfort-design.mjs'):
        out[name]=sha256(ordinary(root,name).read_bytes()).hexdigest()
    for name,digest in out.items():
        if not re.fullmatch('[a-f0-9]{64}',digest) or sha256(ordinary(root,name).read_bytes()).hexdigest()!=digest:
            raise ValueError('executing and retained sources differ: '+name)
    return dict(sorted(out.items()))


def gate(name,state,reason,*,evidence=(),values=None):
    if state not in ('pass','fail','unknown') or not reason:
        raise ValueError('explicit engineering gate state and reason required')
    return dict(name=name,state=state,reason=reason,evidence=list(evidence),values=values or {},
                scope='Stated numerical/design criterion only; physical acceptance separate',**FLAGS)


def inventory(directory,exclude=()):
    directory=Path(directory);out={}
    for p in sorted(directory.rglob('*')):
        if p.is_symlink():raise ValueError('linked artifact forbidden')
        if p.is_file() and p.relative_to(directory).as_posix() not in exclude:
            out[p.relative_to(directory).as_posix()]=sha256(p.read_bytes()).hexdigest()
    return out


def package(directory,label):
    directory=Path(directory);data=io.BytesIO()
    with tarfile.open(fileobj=data,mode='w') as archive:
        for name in inventory(directory):
            raw=(directory/name).read_bytes()
            if len(raw)>80*1024**2:raise ValueError('artifact exceeds bounded publication budget')
            item=tarfile.TarInfo(label+'/'+name);item.size=len(raw);item.mode=0o644;item.mtime=0
            archive.addfile(item,io.BytesIO(raw))
    value=gzip.compress(data.getvalue(),mtime=0)
    if len(value)>95*1024**2:raise ValueError('compressed package exceeds Git file budget')
    return value


def unpack(raw,directory,label):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as archive:
        members=archive.getmembers()
        if len(members)>2000 or sum(m.size for m in members)>512*1024**2:
            raise ValueError('bounded native archive required')
        for m in members:
            name=PurePosixPath(m.name)
            if not m.isfile() or name.is_absolute() or '..' in name.parts or name.parts[0]!=label:
                raise ValueError('ordinary correctly scoped native archive members required')
            target=directory.joinpath(*name.parts[1:]);target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(archive.extractfile(m).read())
    return directory
