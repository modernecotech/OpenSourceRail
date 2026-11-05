"""Reuse verified publication epochs while checking every requested member.

Stat signatures include inode and ctime as well as size and mtime. They are an
invalidation mechanism, not an OS security boundary. Changed epochs receive the
ordinary full source/payload verification again; requested bytes are SHA checked.
"""
from collections import OrderedDict
from copy import deepcopy
from hashlib import sha256
import gzip
import io
import json
from pathlib import Path
from threading import RLock

from engineering.station_rail import ROOT
from . import completion,completion_publication

_cache=OrderedDict()
_lock=RLock()
MAX_ROOTS=3


def _signature(root,folder,manifest):
    paths=[folder/'manifest.json']
    for names,base in ((manifest['source_sha256'],Path(root)),(manifest['files_sha256'],folder)):
        for name in names:
            path=Path(name)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('Repository-relative publication evidence required')
            paths.append(base/path)
    values=[]
    for path in paths:
        completion._ordinary(path)
        s=path.stat()
        values.append((str(path),s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns))
    return tuple(values)


def verified(root=ROOT):
    root=Path(root).resolve();folder=root/completion_publication.PUBLICATION
    with _lock:
        raw=completion._ordinary(folder/'manifest.json').read_bytes()
        manifest=json.loads(raw)
        key=str(root);stamp=(sha256(raw).hexdigest(),_signature(root,folder,manifest))
        cached=_cache.get(key)
        if cached is not None and cached['stamp']==stamp:
            _cache.move_to_end(key)
            return deepcopy(cached['manifest']),deepcopy(cached['catalogue'])
        actual,catalogue=completion_publication.verify(folder,root=root)
        after=(sha256((folder/'manifest.json').read_bytes()).hexdigest(),_signature(root,folder,actual))
        if after!=stamp:raise ValueError('Publication changed during verification; retry against a stable epoch')
        _cache[key]=dict(stamp=stamp,manifest=actual,catalogue=catalogue)
        _cache.move_to_end(key)
        while len(_cache)>MAX_ROOTS:_cache.popitem(last=False)
        return deepcopy(actual),deepcopy(catalogue)


def member(name,root=ROOT):
    root=Path(root).resolve();manifest,_=verified(root)
    if name not in manifest['files_sha256']:
        raise ValueError('Known published outline artifact required')
    path=completion._ordinary(root/completion_publication.PUBLICATION/name)
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=manifest['files_sha256'][name]:
        with _lock:_cache.pop(str(root),None)
        raise ValueError('Requested outline artifact differs')
    return raw


def json_member(name,root=ROOT,maximum=64*1024**2):
    raw=member(name,root)
    if name.endswith('.gz'):
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:raw=stream.read(maximum+1)
    if len(raw)>maximum:raise ValueError('Published outline member exceeds read budget')
    return json.loads(raw)


def clear():
    with _lock:_cache.clear()
