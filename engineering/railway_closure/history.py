"""Keep the earlier public methods at their exact Git/source epoch."""
from pathlib import Path
from hashlib import sha256
import gzip,io,json,subprocess,tarfile
from engineering.station_rail.common import identity,encoded,digest
from . import ROOT,FLAGS

BASE='ad51871d71f5eb8d691d84ebea1b48b61bcad0df'


def retain(packet,*,root=ROOT):
    if packet not in ('station-pair','station-cycle'):raise ValueError('Named historical method required')
    root=Path(root);out=root/'docs/archives'/f'{packet}-before-closure-20261107'
    if out.exists():return verify(out)
    prefix='docs/design-engine/'+packet
    def read(name):return subprocess.check_output(['git','show',BASE+':'+name],cwd=root)
    m=json.loads(read(prefix+'/manifest.json'))
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Historical manifest identity differs')
    files={'publication/manifest.json':read(prefix+'/manifest.json')}
    for n,want in m['files_sha256'].items():
        raw=read(prefix+'/'+n)
        if sha256(raw).hexdigest()!=want:raise ValueError('Historical artifact differs')
        files['publication/'+n]=raw
    for n,want in m['source_sha256'].items():
        raw=read(n)
        if sha256(raw).hexdigest()!=want:raise ValueError('Historical source differs: '+n)
        files['declared-sources/'+n]=raw
    buf=io.BytesIO()
    with tarfile.open(fileobj=buf,mode='w') as tar:
        for n,raw in sorted(files.items()):
            info=tarfile.TarInfo(n);info.size=len(raw);info.mtime=0;info.mode=0o644
            tar.addfile(info,io.BytesIO(raw))
    out.mkdir(parents=True);(out/'packet-and-declared-sources.tar.gz').write_bytes(gzip.compress(buf.getvalue(),mtime=0))
    value=dict(schema='osr-pre-closure-history/1',git_source_commit=BASE,study_id=m['study_id'],
               packet=packet,archive_sha256=digest(out/'packet-and-declared-sources.tar.gz'),
               members_sha256={n:sha256(raw).hexdigest() for n,raw in files.items()},**FLAGS)
    value['retention_id']=identity(value);(out/'manifest.json').write_bytes(encoded(value))
    (out/'README.md').write_text(f'# Retained {packet} before coordinated closure\n\nExact study `{m["study_id"]}` at Git `{BASE}`.\n\n[Packet and declared sources](packet-and-declared-sources.tar.gz) preserve the original numerical and cost methods. Replay in an isolated checkout of the pinned commit. No physical acceptance or operating release.\n')
    return verify(out)


def verify(folder):
    folder=Path(folder);m=json.loads((folder/'manifest.json').read_bytes())
    if m['retention_id']!=identity({k:v for k,v in m.items() if k!='retention_id'}):raise ValueError('History seal differs')
    if digest(folder/'packet-and-declared-sources.tar.gz')!=m['archive_sha256']:raise ValueError('History archive differs')
    with tarfile.open(folder/'packet-and-declared-sources.tar.gz') as tar:
        if len(tar.getnames())!=len(set(tar.getnames())) or set(tar.getnames())!=set(m['members_sha256']):raise ValueError('History inventory differs')
        if sum(member.size for member in tar.getmembers())>128*1024**2:raise ValueError('Historical archive total byte budget exceeded')
        for member in tar:
            p=Path(member.name)
            if not member.isfile() or p.is_absolute() or '..' in p.parts or member.size>64*1024**2:
                raise ValueError('Bounded ordinary history member required')
            if sha256(tar.extractfile(member).read()).hexdigest()!=m['members_sha256'][member.name]:raise ValueError('History member differs')
    return dict(verified=True,retention_id=m['retention_id'],git_source_commit=m['git_source_commit'],**FLAGS)
