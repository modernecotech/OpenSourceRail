"""Actual numerical runtime identity, independent of engineering source hashes."""
import importlib.metadata
from pathlib import Path
import platform
import sys
import os
import shutil
import subprocess

from engineering.twin_workflow import core

_hashes={}
_tools=None
_tool_token=None
_linked={}


def file_hash(path):
    stat=path.stat();token=(stat.st_ino,stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns)
    cached=_hashes.get(str(path))
    if cached is None or cached[0]!=token:
        _hashes[str(path)]=(token,core.sha(path))
    return _hashes[str(path)][1]


def actual_tools():
    global _tools,_tool_token
    from engineering.design_engine.generated_parts_native import toolchain
    paths=[shutil.which(name) for name in ("ccx","FreeCADCmd","freecadcmd","flatpak")]
    if _tools:
        for value in _tools.values():
            if isinstance(value,dict):
                paths.extend(v for k,v in value.items() if k.endswith("path") and isinstance(v,str) and Path(v).is_file())
    stats=[(p,os.stat(p).st_size,os.stat(p).st_mtime_ns,os.stat(p).st_ctime_ns) for p in paths if p and Path(p).is_file()]
    commits=[]
    if shutil.which("flatpak"):
        for option in ("--show-commit","--show-runtime"):
            call=subprocess.run(["flatpak","info",option,"org.freecad.FreeCAD"],capture_output=True,text=True,timeout=10)
            commits.append(call.stdout.strip())
        if commits[-1]:
            call=subprocess.run(["flatpak","info","--show-commit",commits[-1]],capture_output=True,text=True,timeout=10)
            commits.append(call.stdout.strip())
    token=core.digest(dict(stats=stats,commits=commits))
    if _tools is None or token!=_tool_token:
        _tools=toolchain();_tool_token=token
    return _tools


def capture():
    packages = {}
    for name in ("numpy", "scipy", "gmsh", "ifcopenshell"):
        try:
            dist = importlib.metadata.distribution(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = dict(available=False)
            continue
        files = {}
        for member in dist.files or []:
            if str(member).endswith((".py", ".dll", ".dylib", "/RECORD")) or ".so" in Path(member).name:
                path = Path(dist.locate_file(member)).resolve()
                if path.is_file():
                    files[str(path)] = file_hash(path)
        packages[name] = dict(version=dist.version, files_sha256=files)
    tools=actual_tools();libraries={}
    binaries=[str(Path(sys.executable).resolve())]
    for name in ("calculix","gmsh"):
        value=tools.get(name,{})
        binaries.extend(value[k] for k in ("resolved_path","library_path") if k in value)
    for binary in binaries:
        path=Path(binary)
        cache=Path("/etc/ld.so.cache")
        token=(file_hash(path),cache.stat().st_mtime_ns if cache.exists() else None)
        if binary not in _linked or _linked[binary][0]!=token:
            import re
            call=subprocess.run(["ldd",str(path)],capture_output=True,text=True,timeout=10)
            names=re.findall(r"(/[^\s()]+)",call.stdout)
            _linked[binary]=(token,names)
        for name in _linked[binary][1]:
            path=Path(name).resolve()
            if path.is_file():libraries[str(path)]=file_hash(path)
    return dict(schema="osr-numerical-runtime/1", python=sys.version,
        executable=str(Path(sys.executable).resolve()), python_sha256=file_hash(Path(sys.executable).resolve()),
        platform=platform.platform(), tools=tools, packages=packages,linked_libraries_sha256=libraries)


def digest(identity):
    return core.digest(identity)
