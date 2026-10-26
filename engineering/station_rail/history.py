"""Read historical v0.5 evidence from immutable Git blobs, without copying datasets."""
from pathlib import Path
from hashlib import sha256
import json
import subprocess
from . import ROOT
from .common import encoded,identity
REVISION='92e1385e03dcd5c6f76a5b0a9dd5ba348f50d164'
FOLDER='docs/archives/v0.5-maglev'
def blob(root,name):
    if Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('ordinary historical path required')
    return subprocess.check_output(['git','show',REVISION+':'+name],cwd=root)
def create(root=ROOT):
    root=Path(root);folder=root/FOLDER;folder.mkdir(parents=True,exist_ok=True)
    publication=json.loads(blob(root,'docs/design-engine/current/manifest.json'))
    expected=dict(publication['source_sha256'])
    expected.update({'docs/design-engine/current/'+n:d for n,d in publication['files_sha256'].items()})
    expected['docs/design-engine/current/manifest.json']=sha256(blob(root,'docs/design-engine/current/manifest.json')).hexdigest()
    cityreceipt=json.loads(blob(root,'docs/design-engine/current/city-catalogue-manifest.json'))
    expected.update(cityreceipt['files_sha256'])
    for name in ('OpenSourceRail-Book.pdf','OpenSourceRail-Book.receipt.json','engineering/development-baseline.toml','README.md','docs/ROADMAP.md'):
        expected[name]=sha256(blob(root,name)).hexdigest()
    value=dict(schema='osr-v05-git-archive/1',revision=REVISION,role='Historical maglev development selection; not the v0.6 default',
       source_and_payload_sha256=dict(sorted(expected.items())),numerical_calculations_reexecuted=False,physical_accepted=False)
    value['archive_id']=identity(value);(folder/'manifest.json').write_bytes(encoded(value))
    (folder/'README.md').write_text('# Historical v0.5 maglev design\n\n'
       'The permanent-magnet suspension development design is preserved at Git revision `'+REVISION+'`. '
       'Its exact source, reader, current packets and city outputs remain in Git; this compact index avoids duplicating large generated datasets. '
       'The [v0.6 default](../../design-engine/current/README.md) uses passive wheel bogies and station propulsion. '
       'Magnetic suspension findings, quantities and costs do not describe that vehicle.\n\n'
       '[Archive receipt](manifest.json) · [Pinned former front page](https://github.com/modernecotech/OpenSourceRail/blob/'+REVISION+'/README.md). '
       'Use `./osr legacy verify` to check both retained archives. Reproduce numerical work in a separate checkout of its recorded revision; historical writers must not overwrite current outputs.\n')
    return value

def verify(root=ROOT):
    root=Path(root);value=json.loads((root/FOLDER/'manifest.json').read_bytes())
    if value['revision']!=REVISION or value['archive_id']!=identity({k:v for k,v in value.items() if k!='archive_id'}):raise ValueError('historical archive identity differs')
    process=subprocess.Popen(['git','cat-file','--batch'],cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    try:
        for name,expected in value['source_and_payload_sha256'].items():
            process.stdin.write((REVISION+':'+name+'\n').encode());process.stdin.flush()
            header=process.stdout.readline().decode().split()
            if len(header)!=3 or header[1]!='blob':raise ValueError('historical blob missing: '+name)
            raw=process.stdout.read(int(header[2]));assert process.stdout.read(1)==b'\n'
            if sha256(raw).hexdigest()!=expected:raise ValueError('historical blob differs: '+name)
    finally:process.stdin.close();process.wait()
    return dict(verified=True,revision=REVISION,blobs_verified=len(value['source_and_payload_sha256']),physical_accepted=False)
