"""Source-bound Workbench serving; refuse stale warm-cache evidence."""
from pathlib import Path
import json,threading
from engineering.station_rail.common import digest
from . import publication,coordinator
_lock=threading.RLock()
_verified={}


def verify_asset(root,relative,target):
    root=Path(root).resolve();folder=root/publication.OUTPUT
    if any(p.is_symlink() for p in (folder,*folder.parents)) or any(p.is_symlink() for p in folder.rglob('*')):
        raise ValueError('Ordinary closure publication files required')
    name=Path(target).resolve().relative_to(folder.resolve()).as_posix()
    if relative!=publication.OUTPUT+'/'+name:raise ValueError('Closure route identity differs')
    manifest=folder/'manifest.json'
    with _lock:
        token=digest(manifest);m=json.loads(manifest.read_bytes());key=str(root)
        if _verified.get(key)!=token:
            publication.verify(root=root)
            if digest(manifest)!=token:raise ValueError('Closure publication changed while verifying')
            if len(_verified)>=8:_verified.clear()
            _verified[key]=token
        if coordinator.sources(root)!=m['source_sha256']:raise ValueError('Closure source changed; regenerate the dossier')
        files={p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file() and p!=manifest}
        if files!=m['files_sha256'] or digest(manifest)!=token:raise ValueError('Closure asset changed')
        if name!='manifest.json' and name not in files:raise ValueError('Undeclared closure asset')
    return True
