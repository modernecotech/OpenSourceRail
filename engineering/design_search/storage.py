"""Atomic, no-replace installation of immutable bytes."""
import os
from pathlib import Path
import tempfile


class ImmutableConflict(ValueError):
    pass


def atomic_immutable(path,raw):
    path=Path(path)
    if not isinstance(raw,bytes):raise TypeError('immutable payload bytes required')
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):raise ImmutableConflict('ordinary immutable record path required')
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(prefix='.'+path.name+'.',suffix='.pending',dir=path.parent,delete=False) as stream:
            temporary=Path(stream.name);stream.write(raw);stream.flush();os.fsync(stream.fileno())
        try:os.link(temporary,path)
        except FileExistsError:
            if not path.is_file() or path.is_symlink() or path.read_bytes()!=raw:raise ImmutableConflict('immutable record differs: '+str(path))
        descriptor=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(descriptor)
        finally:os.close(descriptor)
        return path
    finally:
        if temporary is not None:temporary.unlink(missing_ok=True)
