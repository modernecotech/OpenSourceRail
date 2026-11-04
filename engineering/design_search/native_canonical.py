"""Explicit, source-bound Rust canonical encoding for research campaigns.

The shared Python encoder remains the reference/default. This adapter accepts
only the strict built-in/string-key domain, like canonical_stream. Building and
loading native code are explicit. Receipts are local integrity records, not
signatures or engineering approval.
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from hashlib import sha256
import argparse
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import sysconfig
import tempfile
import threading

from engineering.station_rail import ROOT, common
from . import native_search

PRODUCER="engineering/design_search/native_canonical.py"
MODULE="osr_design_native"
TARGET="build/rust-canonical-target"
FEATURE="python-extension"
BUILD=["cargo","build","--locked","--release","-p","osr-design-search","--lib","--features",FEATURE]
MAX_BYTES=64*1024**2
MAX_DEPTH=256
_ORACLE_ENCODED=common.encoded
_ACTIVE=ContextVar("osr_native_canonical_session",default=None)
_RECORD_SEALING=ContextVar("osr_native_canonical_record_sealing",default=False)
_SCOPE_LOCK=threading.Lock()
_MODULES={}
LOADED={PRODUCER:common.digest(__file__),native_search.PRODUCER:common.digest(native_search.__file__)}


def _identity(value):return sha256(_ORACLE_ENCODED(value)).hexdigest()


def _abi():
    if platform.python_implementation()!="CPython":raise ValueError("Explicit CPython native encoder ABI required")
    return dict(implementation=platform.python_implementation(),python=sys.version,
        executable=str(Path(sys.executable).resolve()),executable_sha256=common.digest(Path(sys.executable).resolve()),
        SOABI=sysconfig.get_config_var("SOABI"),extension_suffix=sysconfig.get_config_var("EXT_SUFFIX"),
        machine=platform.machine(),platform=sys.platform)


def _sources(root):
    root=Path(root).resolve()
    if root!=Path(ROOT).resolve():raise ValueError("Use the checkout importing this native adapter")
    for name,expected in LOADED.items():
        if common.digest(native_search._regular(root/name))!=expected:raise ValueError("Loaded native canonical adapter changed")
    return dict(sorted({**native_search._sources(root),**LOADED}.items()))


def _write(path,value):
    path=Path(path);raw=_ORACLE_ENCODED(value)
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=".canonical-",dir=path.parent,delete=False) as stream:
        temporary=Path(stream.name);stream.write(raw)
    try:temporary.replace(path)
    finally:temporary.unlink(missing_ok=True)


def _record(path):return native_search._parse(native_search._read(path))


def build_extension(*,root=ROOT,target_dir=None):
    """Build for this exact CPython ABI, then copy into an immutable epoch path."""
    root=Path(root).resolve();sources=_sources(root);abi=_abi()
    target=Path(target_dir).absolute() if target_dir is not None else root/TARGET
    if target.is_symlink():raise ValueError("Ordinary native canonical target required")
    target.mkdir(parents=True,exist_ok=True)
    with (target/"canonical.build.lock").open("a+b") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        tools=native_search._tools();cargo_target=target/"cargo"/abi["SOABI"]
        environment=dict(os.environ,CARGO_TARGET_DIR=str(cargo_target),CARGO_BUILD_JOBS="2",PYO3_PYTHON=sys.executable)
        native_search._run(BUILD,timeout=180,cwd=root,env=environment)
        if _sources(root)!=sources or _abi()!=abi or native_search._tools()!=tools:
            raise ValueError("Native canonical source/tool/ABI changed during build")
        suffix=".dylib" if sys.platform=="darwin" else ".dll" if sys.platform=="win32" else ".so"
        binary=cargo_target/"release"/(("" if sys.platform=="win32" else "lib")+"osr_design_search"+suffix)
        raw=native_search._read(binary)
        receipt=dict(schema="osr-rust-canonical-build/1",sources=sources,abi=abi,tools=tools,build_command=BUILD,
            binary_sha256=sha256(raw).hexdigest(),hybrid_numeric_formatting="CPython float repr and arbitrary-size integer str; Rust traversal, escaping and SHA256")
        receipt["receipt_id"]=_identity(receipt)
        destination=target/"python"/abi["SOABI"]/receipt["receipt_id"]/(MODULE+abi["extension_suffix"])
        destination.parent.mkdir(parents=True,exist_ok=True)
        if destination.exists():
            if native_search._read(destination)!=raw:raise ValueError("Conflicting immutable native canonical binary")
        else:
            with destination.open("xb") as stream:stream.write(raw)
        _write(destination.with_name(destination.name+".receipt.json"),receipt)
        _write(target/"python"/abi["SOABI"]/"current.json",dict(extension=str(destination),receipt_id=receipt["receipt_id"]))
        return dict(extension=str(destination),**receipt)


def _default_extension(root):
    pointer=_record(Path(root)/TARGET/"python"/_abi()["SOABI"]/"current.json")
    extension=Path(pointer["extension"])
    receipt=_record(extension.with_name(extension.name+".receipt.json"))
    if pointer["receipt_id"]!=receipt.get("receipt_id"):raise ValueError("Native canonical pointer/receipt differs")
    return extension


class _Session:
    """One guarded source epoch; no per-object disk hashing or process launch."""
    def __init__(self,engine):self.engine=engine;self.active=True

    def _limits(self,size,depth):
        if not self.active:raise RuntimeError("Native canonical session has ended")
        self.engine._limits(size,depth)

    def encoded(self,value,*,max_bytes=MAX_BYTES,max_depth=128):
        self._limits(max_bytes,max_depth)
        return self.engine._module.encoded(value,max_bytes=max_bytes,max_depth=max_depth)

    def identity(self,value,*,max_bytes=MAX_BYTES,max_depth=128):
        self._limits(max_bytes,max_depth)
        return self.engine._module.identity(value,max_bytes=max_bytes,max_depth=max_depth)

    def encoded_with_identity(self,value,*,max_bytes=MAX_BYTES,max_depth=128):
        self._limits(max_bytes,max_depth)
        return self.engine._module.encoded_with_identity(value,max_bytes=max_bytes,max_depth=max_depth)

    def sealed_record(self,value,key="evaluation_id",*,max_bytes=MAX_BYTES,max_depth=128):
        """Return sealed bytes and the unsealed canonical hash; exact types only."""
        self._limits(max_bytes,max_depth)
        return self.engine._module.sealed_record(value,key=key,max_bytes=max_bytes,max_depth=max_depth)


class NativeCanonical:
    def __init__(self,*,root=ROOT,extension=None):
        self.root=Path(root).resolve()
        self.extension=Path(extension).absolute() if extension is not None else _default_extension(self.root)
        self.receipt_path=self.extension.with_name(self.extension.name+".receipt.json")
        self._receipt=_record(self.receipt_path)
        self._current()
        key=(str(self.extension),self._receipt["binary_sha256"])
        if key not in _MODULES:
            spec=importlib.util.spec_from_file_location(MODULE,str(self.extension))
            if spec is None or spec.loader is None:raise ValueError("Native canonical loader unavailable")
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            _MODULES[key]=module
        self._module=_MODULES[key]
        self._current()

    def _current(self):
        value={k:v for k,v in self._receipt.items() if k!="receipt_id"}
        if (self._receipt.get("schema")!="osr-rust-canonical-build/1"
                or self._receipt.get("receipt_id")!=_identity(value)
                or self._receipt.get("sources")!=_sources(self.root)
                or self._receipt.get("abi")!=_abi()
                or self._receipt.get("tools")!=native_search._tools()
                or self._receipt.get("build_command")!=BUILD
                or self._receipt.get("binary_sha256")!=sha256(native_search._read(self.extension)).hexdigest()
                or _record(self.receipt_path)!=self._receipt):
            raise ValueError("Native canonical source, tool, ABI, binary or receipt differs; explicitly rebuild")

    @staticmethod
    def _limits(size,depth):
        if type(size) is not int or not 1<=size<=MAX_BYTES or type(depth) is not int or not 1<=depth<=MAX_DEPTH:
            raise ValueError("Explicit positive bounded canonical byte/depth limits required")

    def provenance(self):
        self._current()
        return dict(receipt=deepcopy(self._receipt),backend_info=self._module.backend_info())

    @contextmanager
    def session(self):
        self._current()
        session=_Session(self)
        try:yield session
        finally:
            session.active=False
            self._current()

    def encoded(self,value,**kwargs):
        with self.session() as session:return session.encoded(value,**kwargs)

    def identity(self,value,**kwargs):
        with self.session() as session:return session.identity(value,**kwargs)

    def encoded_with_identity(self,value,**kwargs):
        with self.session() as session:return session.encoded_with_identity(value,**kwargs)

    def sealed_record(self,value,key="evaluation_id",**kwargs):
        with self.session() as session:return session.sealed_record(value,key,**kwargs)


def active_sealed_record(value,key="evaluation_id"):
    """Use only an explicitly enabled active Rust scope, without filesystem IO.

    None selects the unchanged Python fragment path. An enabled native error,
    unsupported type or missing extension method propagates rather than silently
    substituting another identity path. Native seal keys require exact str;
    the Python fallback retains its broader original isinstance(str) behavior.
    """
    active=_ACTIVE.get()
    if active is None or not _RECORD_SEALING.get():return None
    return active.sealed_record(value,key)


@contextmanager
def campaign_backend(mode="python",*,root=ROOT,extension=None,record_sealing=True):
    """Opt-in scoped aliases; other contexts keep the Python reference encoder.

    One native scope per process avoids conflicting alias installation. The
    context-local dispatcher keeps concurrent unrelated threads on Python.
    Every installed alias is restored, including modules imported in the scope.
    """
    if mode not in ("python","rust"):raise ValueError("Explicit python or rust canonical backend required")
    if type(record_sealing) is not bool:raise ValueError("Explicit boolean native record-sealing policy required")
    if mode=="python":
        if _ACTIVE.get() is not None:raise RuntimeError("A Python backend cannot nest inside an active Rust canonical scope")
        if extension is not None:raise ValueError("A native extension requires the rust backend")
        yield dict(mode="python",reference="engineering.station_rail.common.encoded")
        return
    if not _SCOPE_LOCK.acquire(blocking=False):raise RuntimeError("Another native canonical scope is active")
    try:
        engine=NativeCanonical(root=root,extension=extension)
        reference_encoded,reference_identity=common.encoded,common.identity
        def encoded(value):
            active=_ACTIVE.get()
            return active.encoded(value) if active is not None else reference_encoded(value)
        def identity(value):
            active=_ACTIVE.get()
            return active.identity(value) if active is not None else reference_identity(value)
        originals=[]
        for name,module in list(sys.modules.items()):
            if name.startswith("engineering."):
                for attribute,original,wrapper in (("encoded",reference_encoded,encoded),("identity",reference_identity,identity)):
                    if getattr(module,attribute,None) is original:
                        originals.append((module,attribute,original));setattr(module,attribute,wrapper)
        try:
            with engine.session() as session:
                token=_ACTIVE.set(session)
                sealing_token=_RECORD_SEALING.set(record_sealing)
                try:yield dict(mode="rust",record_sealing=record_sealing,**engine.provenance())
                finally:
                    _RECORD_SEALING.reset(sealing_token)
                    _ACTIVE.reset(token)
        finally:
            for module,attribute,original in reversed(originals):
                wrapper=encoded if attribute=="encoded" else identity
                if getattr(module,attribute,None) is wrapper:setattr(module,attribute,original)
            # A module imported after installation can retain the dispatcher.
            for name,module in list(sys.modules.items()):
                if name.startswith("engineering."):
                    if getattr(module,"encoded",None) is encoded:setattr(module,"encoded",reference_encoded)
                    if getattr(module,"identity",None) is identity:setattr(module,"identity",reference_identity)
    finally:_SCOPE_LOCK.release()


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=("build","status"))
    parser.add_argument("--target",type=Path)
    args=parser.parse_args(argv)
    value=build_extension(target_dir=args.target) if args.command=="build" else NativeCanonical().provenance()
    print(json.dumps(value,indent=2));return 0


if __name__=="__main__":raise SystemExit(main())
