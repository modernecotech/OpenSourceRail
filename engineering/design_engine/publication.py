"""Publish a complete legacy artifact directory at one atomic commit point.

Linux RENAME_EXCHANGE preserves existing reader paths and the previous complete
generation. Unsupported filesystems fail before changing the current directory.
See https://man7.org/linux/man-pages/man2/renameat2.2.html.
"""

from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import shutil
import tempfile
import uuid


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def hashes(root, names):
    return {name: digest(root / name) for name in sorted(names)}


def safe(root, relative):
    name = Path(relative)
    if name.is_absolute() or ".." in name.parts or not name.parts:
        raise ValueError("artifact must have a controlled relative path")
    target = root / name
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError("artifact escapes its publication directory")
    return target


def sync_directory(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def exchange(left, right):
    libc = ctypes.CDLL(None, use_errno=True)
    function = getattr(libc, "renameat2", None)
    if function is None:
        raise RuntimeError("atomic directory exchange requires Linux renameat2")
    function.argtypes = [
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    ]
    function.restype = ctypes.c_int
    if function(-100, os.fsencode(left), -100, os.fsencode(right), 2):
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code))


def publish(destination, outputs, *, repository, sources, history, before_commit=None):
    """Stage all bytes, verify the exact input epoch, exchange, retain old bytes.

    Existing subdirectories and historical records are copied unchanged. The
    callback is a crash-injection seam for tests, not a publication shortcut.
    """
    destination, repository, history = map(
        lambda p: Path(p).resolve(), (destination, repository, history)
    )
    if not outputs or not sources:
        raise ValueError("publication needs outputs and exact source dependencies")
    if hashes(repository, sources) != sources:
        raise ValueError("publication source epoch is stale")
    destination.parent.mkdir(parents=True, exist_ok=True)
    history.mkdir(parents=True, exist_ok=True)
    stage = Path(
        tempfile.mkdtemp(
            prefix=".osr-publication-stage-" + destination.name + "-",
            dir=destination.parent,
        )
    )
    committed = False
    try:
        if destination.exists():
            for path in destination.rglob("*"):
                if path.is_symlink():
                    raise ValueError(
                        "publication cannot replace a symlinked artifact tree"
                    )
            shutil.copytree(destination, stage, dirs_exist_ok=True)
        for name, data in outputs.items():
            target = safe(stage, name)
            if not isinstance(data, bytes):
                raise TypeError("publication payloads must be bytes")
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        for folder in sorted(
            (p for p in stage.rglob("*") if p.is_dir()),
            key=lambda p: len(p.parts),
            reverse=True,
        ):
            sync_directory(folder)
        sync_directory(stage)
        if before_commit:
            before_commit(stage)
        if hashes(repository, sources) != sources:
            raise ValueError("source changed while staging the publication")
        if destination.exists():
            exchange(stage, destination)
            committed = True
            sync_directory(destination.parent)
            previous = history / (destination.name + "-" + uuid.uuid4().hex)
            os.rename(stage, previous)
            sync_directory(history)
            return previous
        os.rename(stage, destination)
        committed = True
        sync_directory(destination.parent)
        return None
    finally:
        # After exchange, stage contains history: never delete it if archival
        # fails or a caller interrupts. Before exchange it is disposable output.
        if not committed:
            shutil.rmtree(stage, ignore_errors=True)
