"""Pin producer bytes for a completed bounded research publication.

This verifies archive integrity under the original source epoch. It neither
replays the numerical work nor admits that result under current evaluators.
The original publication and its receipts remain byte-for-byte unchanged.
"""
import argparse
import gzip
import io
import json
from pathlib import Path
import subprocess
import tarfile

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity

PRODUCER='engineering/design_search/retained_publication.py'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
    manufacturing_release=False,operating_release=False)
WHEEL_PACKET='docs/design-engine/v06-optimisation'
WHEEL_EPOCH='docs/design-engine/retained-wheel-source-epoch'


def ordinary(root,name):
    relative=Path(name)
    if relative.is_absolute() or not relative.parts or '..' in relative.parts:
        raise ValueError('Ordinary repository-relative retained file required')
    p=Path(root)/relative
    for item in (p,*p.parents):
        if item==Path(root):break
        if item.is_symlink():raise ValueError('Retained evidence cannot use symlinks')
    if not p.is_file():raise ValueError('Retained evidence file missing: '+str(name))
    return p


def _packet(root,packet):
    root=Path(root).resolve();base=Path(packet)
    mpath=ordinary(root,base/'manifest.json');m=json.loads(mpath.read_bytes())
    if (m.get('schema')!='osr-wheel-campaign-publication-manifest/1'
            or m.get('manifest_id')!=identity({k:v for k,v in m.items() if k!='manifest_id'})
            or any(m.get(k) is not v for k,v in FLAGS.items())):
        raise ValueError('Original bounded-wheel publication identity or disposition differs')
    actual={p.relative_to(root/base).as_posix():digest(p) for p in (root/base).rglob('*')
        if p.is_file() and p!=mpath}
    if actual!=m.get('files_sha256'):
        raise ValueError('Original retained publication payload differs')
    for name,h in actual.items():
        if digest(ordinary(root,base/name))!=h:raise ValueError('Retained payload differs')
    sources=dict(m.get('source_sha256',{}))
    for name,h in m.get('recovery_source_sha256',{}).items():
        if name in sources and sources[name]!=h:raise ValueError('Conflicting original source bindings')
        sources[name]=h
    if not sources or any(not isinstance(k,str) or not isinstance(v,str) or len(v)!=64 for k,v in sources.items()):
        raise ValueError('Original exact source map required')
    return m,sources


def _source_bytes(root,name,wanted):
    p=ordinary(root,name)
    if digest(p)==wanted:return p.read_bytes()
    # Offline Git ancestry supplies bytes only when their content hash matches.
    commits=subprocess.check_output(['git','log','--all','--format=%H','--',name],cwd=root,text=True).splitlines()
    from hashlib import sha256
    for commit in commits:
        result=subprocess.run(['git','show',commit+':'+name],cwd=root,capture_output=True)
        if result.returncode==0 and sha256(result.stdout).hexdigest()==wanted:return result.stdout
    raise ValueError('Original producer bytes unavailable: '+name+' '+wanted)


def retain(root=ROOT,*,packet=WHEEL_PACKET,output=WHEEL_EPOCH,resolver=None):
    root=Path(root).resolve();m,sources=_packet(root,packet)
    relative=Path(output)
    if relative.is_absolute() or not relative.parts or '..' in relative.parts:
        raise ValueError('Retained output must stay inside the repository')
    out=root/relative;packet_path=root/packet
    if out==packet_path or out in packet_path.parents or packet_path in out.parents:
        raise ValueError('Retained output must be separate from the original packet')
    for item in (out,*out.parents):
        if item==root:break
        if item.is_symlink():raise ValueError('Retained output cannot use symlinks')
    if out.exists():return verify(root,packet=packet,output=output)
    provider=_source_bytes if resolver is None else resolver
    buf=io.BytesIO()
    from hashlib import sha256
    with tarfile.open(fileobj=buf,mode='w') as tar:
        for name,h in sorted(sources.items()):
            if Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('Ordinary source member required')
            raw=provider(root,name,h)
            if sha256(raw).hexdigest()!=h:raise ValueError('Recovered original source bytes differ: '+name)
            info=tarfile.TarInfo(name);info.size=len(raw);info.mode=0o644;info.mtime=0
            tar.addfile(info,io.BytesIO(raw))
    raw=gzip.compress(buf.getvalue(),mtime=0)
    if len(raw)>32*1024**2:raise ValueError('Bounded retained source archive required')
    receipt=dict(schema='osr-completed-research-source-epoch/1',
        packet=packet,original_manifest_id=m['manifest_id'],
        original_manifest_sha256=digest(root/packet/'manifest.json'),
        original_source_sha256=sources,source_archive_sha256=sha256(raw).hexdigest(),
        retention_producer_sha256={PRODUCER:digest(root/PRODUCER)},
        original_payload_sha256=m['files_sha256'],
        scope='Unchanged completed bounded packet and its top-level declared producer bytes only. Nested attempt/preliminary/material-patch archives are byte-preserved; additional per-attempt producer coverage or replay is not established.',
        top_level_source_coverage_complete=True,nested_attempt_source_epochs_enumerated=False,
        numerical_reexecuted=False,current_evaluator_admission=False,
        omitted_native_fields_restored=False,**FLAGS)
    receipt['retention_id']=identity(receipt)
    out.mkdir(parents=True)
    (out/'sources.tar.gz').write_bytes(raw);(out/'manifest.json').write_bytes(encoded(receipt))
    return verify(root,packet=packet,output=output)


def verify(root=ROOT,*,packet=WHEEL_PACKET,output=WHEEL_EPOCH):
    root=Path(root).resolve();m,sources=_packet(root,packet)
    out=Path(output);receipt_path=ordinary(root,out/'manifest.json')
    r=json.loads(receipt_path.read_bytes())
    if (r.get('schema')!='osr-completed-research-source-epoch/1'
            or r.get('retention_id')!=identity({k:v for k,v in r.items() if k!='retention_id'})
            or r.get('packet')!=packet or r.get('original_manifest_id')!=m['manifest_id']
            or r.get('original_manifest_sha256')!=digest(root/packet/'manifest.json')
            or r.get('original_source_sha256')!=sources
            or r.get('original_payload_sha256')!=m['files_sha256']
            or r.get('top_level_source_coverage_complete') is not True
            or r.get('nested_attempt_source_epochs_enumerated') is not False
            or any(r.get(k) is not v for k,v in FLAGS.items())
            or any(r.get(k) is not False for k in ('numerical_reexecuted','current_evaluator_admission','omitted_native_fields_restored'))):
        raise ValueError('Retained source-epoch receipt or scope differs')
    archive=ordinary(root,out/'sources.tar.gz')
    if digest(archive)!=r.get('source_archive_sha256'):raise ValueError('Retained source archive bytes differ')
    from hashlib import sha256
    with tarfile.open(archive,'r:gz') as tar:
        members=tar.getmembers()
        if len(members)>256 or sum(item.size for item in members)>64*1024**2:
            raise ValueError('Retained source archive exceeds its resource bound')
        if (len({item.name for item in members})!=len(members)
                or any(not item.isfile() or Path(item.name).is_absolute() or '..' in Path(item.name).parts for item in members)):
            raise ValueError('Ordinary unique retained source members required')
        actual={item.name:sha256(tar.extractfile(item).read()).hexdigest() for item in members}
    if actual!=sources:raise ValueError('Retained original producer coverage or bytes differ')
    if r.get('retention_producer_sha256')!={PRODUCER:digest(ordinary(root,PRODUCER))}:
        raise ValueError('Retained-epoch verifier source differs')
    dependencies={str(Path(packet)/name):h for name,h in m['files_sha256'].items()}
    dependencies.update({str(Path(packet)/'manifest.json'):r['original_manifest_sha256'],
        str(out/'sources.tar.gz'):r['source_archive_sha256'],str(out/'manifest.json'):digest(receipt_path),
        **r['retention_producer_sha256']})
    return dict(verified=True,scope='original-packet-and-top-level-producer-byte-integrity',
        retention_id=r['retention_id'],original_manifest_id=m['manifest_id'],
        original_source_count=len(sources),numerical_reexecuted=False,
        current_evaluator_admission=False,dependency_sha256=dependencies,**FLAGS)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('retain','verify'))
    args=parser.parse_args();result=(retain if args.action=='retain' else verify)()
    print(json.dumps({k:v for k,v in result.items() if k!='dependency_sha256'},indent=2))
