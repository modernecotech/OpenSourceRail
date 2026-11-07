"""Serve source-bound research assets without recompiling every HTTP response."""
from pathlib import Path
import json,threading
from engineering.station_rail.common import digest
from . import publication

_lock=threading.RLock()
_verified={}


def verify_asset(root,relative,target):
    root=Path(root).resolve();folder=root/publication.OUTPUT;manifest=folder/'manifest.json'
    if any(p.is_symlink() for p in (folder,*folder.parents)):raise ValueError('Ordinary vehicle publication directory required')
    if any(p.is_symlink() for p in folder.rglob('*')):raise ValueError('Ordinary vehicle publication files required')
    name=Path(target).resolve().relative_to(folder.resolve()).as_posix()
    if relative!=publication.OUTPUT+'/'+name:raise ValueError('Vehicle parts route identity differs')
    with _lock:
        token=digest(manifest);m=json.loads(manifest.read_bytes());key=str(root)
        if _verified.get(key)!=token:
            publication.verify(root)
            if digest(manifest)!=token:raise ValueError('Vehicle parts publication changed during verification')
            if len(_verified)>=8:_verified.clear()
            _verified[key]=token
        # Reuse depends on the actual current source and complete artifact bytes.
        if (name!='manifest.json' and name not in m['files_sha256']) or any(digest(root/n)!=sha for n,sha in m['source_sha256'].items()):
            raise ValueError('Vehicle parts source epoch changed; regenerate the proposal')
        actual={p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file() and p!=manifest}
        if actual!=m['files_sha256']:raise ValueError('Vehicle parts asset changed')
        if digest(manifest)!=token:raise ValueError('Vehicle parts manifest changed during read')
    return True
