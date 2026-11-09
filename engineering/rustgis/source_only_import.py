"""Closed project imports compiled from authenticated source bytes only.

Bootstrap this file by its separately verified file path before importing the
controlled namespaces. ``install`` refuses namespaces already in ``sys.modules``.
The returned finder must remain installed for the whole guarded workload.

This is an import policy, not an OS sandbox. It does not authenticate its own
bootstrap, stdlib/native libraries, arbitrary resource reads, or trusted code
which deliberately replaces Python's import machinery. Those remain separate
runtime bindings. No project bytecode cache is inspected or generated here.
"""
import hashlib
import importlib.abc
import importlib.machinery
import os
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
import re
import stat
import sys


class SourceImportError(ImportError):
    """A controlled import cannot satisfy the authenticated-source contract."""


def _directory_flags():
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise SourceImportError("Source-only imports require no-follow directory opens")
    return os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC


def _open_root(root):
    """Walk from / without resolving away a symlink in the declared root."""
    fd = os.open(root.anchor, _directory_flags())
    try:
        for part in root.parts[1:]:
            nxt = os.open(part, _directory_flags(), dir_fd=fd)
            os.close(fd)
            fd = nxt
        return fd
    except BaseException:
        os.close(fd)
        raise


class _SourceLoader(importlib.abc.Loader):
    def __init__(self, owner, fullname, relative, package):
        self.owner, self.fullname = owner, fullname
        self.relative, self.package = relative, package

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        raw = self.owner._source(self.relative)
        filename = str(self.owner.root / self.relative)
        # Compile these bytes directly. SourceFileLoader.get_code() would also
        # search existing pyc files, even with -B/dont_write_bytecode enabled.
        code = compile(raw, filename, "exec", dont_inherit=True, optimize=0)
        module.__file__ = filename
        module.__cached__ = None
        if self.package:
            module.__path__ = [str((self.owner.root / self.relative).parent)]
        record = self.owner._record(self.fullname, self.relative,
                                    hashlib.sha256(raw).hexdigest(), len(raw), "source")
        try:
            exec(code, module.__dict__)
        except BaseException:
            record["execution"] = "failed"
            raise
        record["execution"] = "completed"


class _ClosedNamespaceLoader(importlib.abc.Loader):
    def __init__(self, owner, fullname, relative):
        self.owner, self.fullname, self.relative = owner, fullname, relative

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        self.owner._namespace(self.relative)
        module.__path__ = [str(self.owner.root / self.relative)]
        module.__file__ = None
        module.__cached__ = None
        record = self.owner._record(self.fullname, self.relative, None, None,
                                    "closed-namespace")
        record["execution"] = "completed"


class SourceOnlyImporter(importlib.abc.MetaPathFinder):
    """Finder for an exact source allowlist and its closed namespace prefixes.

    Namespace packages have no source bytes/hash. They are admitted only as
    prefixes of allowlisted modules, with one ordinary in-root directory and no
    unlisted __init__.py. They never merge paths discovered from sys.path.
    """
    def __init__(self, *, repo_root, source_sha256, namespaces,
                 max_source_bytes=8 * 1024 * 1024):
        self.root = Path(repo_root)
        if not self.root.is_absolute() or ".." in self.root.parts:
            raise ValueError("An explicit absolute repository root is required")
        if isinstance(namespaces, str):
            raise ValueError("Declared top-level namespace identifiers are required")
        namespaces = tuple(namespaces)
        if (not namespaces or
                any(not isinstance(n, str) or not n.isidentifier() for n in namespaces)):
            raise ValueError("Declared top-level namespace identifiers are required")
        if not isinstance(source_sha256, Mapping):
            raise ValueError("An explicit source path to SHA256 mapping is required")
        self.namespaces = frozenset(namespaces)
        if type(max_source_bytes) is not int or max_source_bytes <= 0:
            raise ValueError("A positive source byte limit is required")
        self.max_source_bytes = max_source_bytes
        self._sources, self._modules, self._prefixes, self._records = {}, {}, {}, []
        for relative, expected in source_sha256.items():
            if not isinstance(relative, str) or "\\" in relative:
                raise ValueError("Canonical repository-relative POSIX source paths required")
            path = PurePosixPath(relative)
            if (path.is_absolute() or ".." in path.parts or path.as_posix() != relative or
                    "__pycache__" in path.parts or path.suffix != ".py"):
                raise ValueError("Canonical repository-relative .py source paths required")
            if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                raise ValueError("An exact lowercase SHA256 is required for each source")
            package = path.name == "__init__.py"
            names = path.parts[:-1] if package else (*path.parts[:-1], path.stem)
            if not names or any(not n.isidentifier() for n in names) or names[0] not in self.namespaces:
                raise ValueError("Source path must name a module in a declared namespace")
            fullname = ".".join(names)
            if fullname in self._modules:
                raise ValueError("Ambiguous module/package source: " + fullname)
            self._sources[relative] = expected
            self._modules[fullname] = (relative, package)
            for i in range(1, len(names)):
                self._prefixes[".".join(names[:i])] = "/".join(names[:i])
        for name in self._prefixes:
            if name in self._modules and not self._modules[name][1]:
                raise ValueError("A source module cannot also be a package: " + name)
        try:
            os.close(_open_root(self.root))
        except OSError as exc:
            raise SourceImportError("Repository root must contain ordinary directories only") from exc

    def _open_parent(self, parts):
        fd = _open_root(self.root)
        try:
            for part in parts:
                nxt = os.open(part, _directory_flags(), dir_fd=fd)
                os.close(fd)
                fd = nxt
            return fd
        except BaseException:
            os.close(fd)
            raise

    def _source(self, relative):
        parts = PurePosixPath(relative).parts
        parent = fd = None
        try:
            parent = self._open_parent(parts[:-1])
            fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
                         dir_fd=parent)
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_size > self.max_source_bytes:
                raise SourceImportError("Ordinary bounded source file required: " + relative)
            chunks, total = [], 0
            while True:
                chunk = os.read(fd, min(65536, self.max_source_bytes + 1 - total))
                if not chunk:
                    break
                chunks.append(chunk)
                total += len(chunk)
                if total > self.max_source_bytes:
                    raise SourceImportError("Source byte limit exceeded: " + relative)
            raw, after = b"".join(chunks), os.fstat(fd)
            if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                    after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise SourceImportError("Source changed during read: " + relative)
            if hashlib.sha256(raw).hexdigest() != self._sources[relative]:
                raise SourceImportError("Source SHA256 differs: " + relative)
            return raw
        except OSError as exc:
            raise SourceImportError("Missing, symlinked or inaccessible source: " + relative) from exc
        finally:
            if fd is not None:
                os.close(fd)
            if parent is not None:
                os.close(parent)

    def _namespace(self, relative):
        fd = None
        try:
            fd = self._open_parent(PurePosixPath(relative).parts)
            for initializer in ("__init__.py", "__init__.pyc"):
                try:
                    os.stat(initializer, dir_fd=fd, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                raise SourceImportError("Unlisted package initializer: " + relative)
        except OSError as exc:
            raise SourceImportError("Missing or symlinked namespace: " + relative) from exc
        finally:
            if fd is not None:
                os.close(fd)

    def _record(self, module, path, sha256, size, kind):
        row = dict(module=module, path=path, sha256=sha256, bytes=size,
                   kind=kind, execution="started")
        self._records.append(row)
        return row

    @property
    def records(self):
        """Copies of actual execution records; failed source execution is retained."""
        return tuple(dict(row) for row in self._records)

    def find_spec(self, fullname, path=None, target=None):
        if fullname.partition(".")[0] not in self.namespaces:
            return None
        if fullname in self._modules:
            relative, package = self._modules[fullname]
            loader = _SourceLoader(self, fullname, relative, package)
            spec = importlib.machinery.ModuleSpec(fullname, loader,
                origin=str(self.root / relative), is_package=package)
            if package:
                spec.submodule_search_locations = [str((self.root / relative).parent)]
            return spec
        if fullname in self._prefixes:
            relative = self._prefixes[fullname]
            loader = _ClosedNamespaceLoader(self, fullname, relative)
            spec = importlib.machinery.ModuleSpec(fullname, loader, is_package=True)
            spec.submodule_search_locations = [str(self.root / relative)]
            return spec
        # Raise rather than returning None: later finders must not supply an
        # unlisted source, extension, sourceless pyc or foreign namespace.
        raise ModuleNotFoundError("Source-only allowlist refuses " + fullname, name=fullname)

    def close(self):
        """Remove this finder after the workload; already imported modules remain."""
        if self in sys.meta_path:
            sys.meta_path.remove(self)


def install(*, repo_root, source_sha256, namespaces=("engineering", "services"),
            max_source_bytes=8 * 1024 * 1024):
    """Install before any controlled namespace; never purge/relabel loaded code.

    Caller must also launch Python with -B/PYTHONDONTWRITEBYTECODE=1 and bind the
    bootstrap, interpreter and nonproject runtime separately. This loader itself
    directly compiles source bytes and never consults a bytecode cache.
    """
    if sys.dont_write_bytecode is not True:
        raise SourceImportError("Bytecode generation must be disabled before installing source policy")
    finder = SourceOnlyImporter(repo_root=repo_root, source_sha256=source_sha256,
                               namespaces=namespaces, max_source_bytes=max_source_bytes)
    if any(name.partition(".")[0] in finder.namespaces for name in sys.modules):
        raise SourceImportError("Install source policy before importing controlled namespaces")
    for active in sys.meta_path:
        if isinstance(active, SourceOnlyImporter) and active.namespaces & finder.namespaces:
            raise SourceImportError("An overlapping source-only policy is already installed")
    sys.meta_path.insert(0, finder)
    return finder
