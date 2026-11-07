"""Retain the first fixed-brake comparison at its exact immutable Git epoch."""
from pathlib import Path
from hashlib import sha256
import gzip,io,json,subprocess,tarfile
from engineering.station_rail.common import digest,encoded,identity
from . import ROOT,FLAGS

BASE='8ed8bf7fa69d8fb76b0f8d370596a7d4765e10d7'
OUTPUT='docs/archives/station-pair-fixed-control-20261107'
PACKET='docs/design-engine/station-pair'


def _git(root,name):
    if Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('Ordinary retained path required')
    return subprocess.check_output(['git','show',BASE+':'+name],cwd=root)


def retain(root=ROOT):
    root=Path(root);folder=root/OUTPUT
    if folder.exists():return verify(root)
    m=json.loads(_git(root,PACKET+'/manifest.json'))
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Retained manifest identity differs')
    files={}
    for name,sha in m['files_sha256'].items():
        raw=_git(root,PACKET+'/'+name)
        if sha256(raw).hexdigest()!=sha:raise ValueError('Retained publication file differs')
        files['publication/'+name]=raw
    files['publication/manifest.json']=_git(root,PACKET+'/manifest.json')
    for name,sha in m['source_sha256'].items():
        raw=_git(root,name)
        if sha256(raw).hexdigest()!=sha:raise ValueError('Retained source differs: '+name)
        files['declared-sources/'+name]=raw
    buf=io.BytesIO()
    with tarfile.open(fileobj=buf,mode='w') as tar:
        for name,raw in sorted(files.items()):
            info=tarfile.TarInfo(name);info.size=len(raw);info.mode=0o644;info.mtime=0
            tar.addfile(info,io.BytesIO(raw))
    raw=gzip.compress(buf.getvalue(),mtime=0);folder.mkdir(parents=True)
    (folder/'packet-and-declared-sources.tar.gz').write_bytes(raw)
    value=dict(schema='osr-station-pair-fixed-control-retention/1',git_source_commit=BASE,
        study_id=m['study_id'],publication_manifest_id=m['manifest_id'],
        archive_sha256=digest(folder/'packet-and-declared-sources.tar.gz'),
        members_sha256={n:sha256(raw).hexdigest() for n,raw in files.items()},
        scope='Exact publication and its declared source files. Full dependency checkout/replay uses the pinned Git commit.',
        source_mutated=False,physical_evidence_added=False,**FLAGS)
    value['retention_id']=identity(value);(folder/'manifest.json').write_bytes(encoded(value))
    (folder/'README.md').write_text(f'''# Retained fixed-brake station-pair comparison

The first station-pair experiment is retained at Git commit `{BASE}` with its
original source-bound publication and declared source files. It uses an offline
fitted nominal brake point and replays faults without fitting each fault result.
Its berth misses, downhill overruns and hill-start limitations remain evidence.

This is historical conditional research, with no physical or operating acceptance.
The [current comparison](../../design-engine/station-pair/README.md) explores a
separate feedback-control evaluation without changing the physical reference.

[Download exact packet and declared sources](packet-and-declared-sources.tar.gz).
The archive is for inspection; use the complete pinned Git checkout for replay:

```bash
git worktree add --detach /path/to/fixed-control-source {BASE}
cd /path/to/fixed-control-source
./osr design station-pair verify --replay --state /path/to/private/replay
```

No current source is substituted into this historical evaluation. Retention ID
`{value['retention_id']}`; study `{value['study_id']}`.
''')
    return verify(root)


def verify(root=ROOT):
    root=Path(root);folder=root/OUTPUT;m=json.loads((folder/'manifest.json').read_bytes())
    if m['retention_id']!=identity({k:v for k,v in m.items() if k!='retention_id'}):raise ValueError('Retention identity differs')
    if m['git_source_commit']!=BASE or any(m[k] is not v for k,v in FLAGS.items()):raise ValueError('Historical scope or release differs')
    path=folder/'packet-and-declared-sources.tar.gz'
    if digest(path)!=m['archive_sha256']:raise ValueError('Historical archive changed')
    with tarfile.open(path,mode='r:gz') as tar:
        names=tar.getnames()
        if len(names)!=len(set(names)) or set(names)!=set(m['members_sha256']):raise ValueError('Historical inventory differs')
        for member in tar:
            if not member.isfile() or member.size>32*1024**2 or Path(member.name).is_absolute() or '..' in Path(member.name).parts:
                raise ValueError('Ordinary bounded historical member required')
            if sha256(tar.extractfile(member).read()).hexdigest()!=m['members_sha256'][member.name]:
                raise ValueError('Historical member changed')
        original=json.loads(tar.extractfile('publication/manifest.json').read())
        if (original['manifest_id']!=identity({k:v for k,v in original.items() if k!='manifest_id'})
            or original['manifest_id']!=m['publication_manifest_id'] or original['study_id']!=m['study_id']
            or any(original[k] is not v for k,v in FLAGS.items())):
            raise ValueError('Historical publication identity or release differs')
        for name,sha in original['files_sha256'].items():
            if m['members_sha256'].get('publication/'+name)!=sha:raise ValueError('Historical file binding differs')
        for name,sha in original['source_sha256'].items():
            if m['members_sha256'].get('declared-sources/'+name)!=sha:raise ValueError('Historical source binding differs')
    return dict(verified=True,study_id=m['study_id'],retention_id=m['retention_id'],git_source_commit=BASE,**FLAGS)
