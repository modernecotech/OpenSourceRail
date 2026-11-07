"""Retain the paired fixed and feedback comparison at its exact immutable Git epoch."""
from pathlib import Path
from hashlib import sha256
import gzip,io,json,subprocess,tarfile
from engineering.station_rail.common import digest,encoded,identity
from . import ROOT,FLAGS

BASE='b5212904e3f6c3af35a901b23d98a368fd2a8666'
OUTPUT='docs/archives/station-pair-feedback-20261107'
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
    value=dict(schema='osr-station-pair-feedback-retention/1',git_source_commit=BASE,
        study_id=m['study_id'],publication_manifest_id=m['manifest_id'],
        archive_sha256=digest(folder/'packet-and-declared-sources.tar.gz'),
        members_sha256={n:sha256(raw).hexdigest() for n,raw in files.items()},
        scope='Exact publication and its declared source files. Full dependency checkout/replay uses the pinned Git commit.',
        source_mutated=False,physical_evidence_added=False,**FLAGS)
    value['retention_id']=identity(value);(folder/'manifest.json').write_bytes(encoded(value))
    (folder/'README.md').write_text(f'''# Retained station-pair feedback comparison

Exact source-bound publication at `{BASE}`, before the stateful regenerative
cycle and extended lifecycle accounting. Original nominal/fault results remain
conditional research, with no physical acceptance or operating release.

[Download packet and declared sources](packet-and-declared-sources.tar.gz).
Use a full checkout at the pinned Git commit for independent native replay:

```bash
git worktree add --detach /path/to/prior-source {BASE}
cd /path/to/prior-source
./osr design station-pair verify --replay --state /path/to/private/replay
```

Study `{value['study_id']}`; retention `{value['retention_id']}`.
[Current cycle comparison](../../design-engine/station-cycle/README.md).
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
