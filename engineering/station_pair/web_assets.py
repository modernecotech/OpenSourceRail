"""Source- and artifact-bound static serving for the research comparison."""
from pathlib import Path
import json,threading
from engineering.station_rail.common import digest
from . import publication

_lock=threading.RLock()
_verified={}


def verify_asset(root,relative,target):
    root=Path(root).resolve();folder=root/publication.OUTPUT;manifest=folder/'manifest.json'
    if any(p.is_symlink() for p in (folder,*folder.parents)) or any(p.is_symlink() for p in folder.rglob('*')):
        raise ValueError('Ordinary station-pair publication files required')
    name=Path(target).resolve().relative_to(folder.resolve()).as_posix()
    if relative!=publication.OUTPUT+'/'+name:raise ValueError('Station-pair route identity differs')
    with _lock:
        token=digest(manifest);m=json.loads(manifest.read_bytes());key=str(root)
        if _verified.get(key)!=token:
            publication.verify(root=root)
            if digest(manifest)!=token:raise ValueError('Station-pair publication changed while verifying')
            if len(_verified)>=8:_verified.clear()
            _verified[key]=token
        if (name!='manifest.json' and name not in m['files_sha256']) or publication.sources(root)!=m['source_sha256']:
            raise ValueError('Station-pair source changed; regenerate the comparison')
        got={p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file() and p!=manifest}
        if got!=m['files_sha256'] or digest(manifest)!=token:raise ValueError('Station-pair asset changed')
    return True
