#!/usr/bin/env python3
"""Install one checksum-pinned official FreeCAD bundle for historical CI.

The download is an explicit workflow step. This installer checks its bytes before
executing extraction, then delegates to the bundle's actual freecadcmd binary.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shlex
import subprocess

VERSION = '1.1.4'
ASSET = 'FreeCAD_1.1.4-Linux-x86_64-py311.AppImage'
URL = 'https://github.com/FreeCAD/FreeCAD/releases/download/1.1.4/' + ASSET
SHA256 = 'f6dc6ba676e5ac96a565ebc8d657232f94c6158e85b4352141bd1a46f6b43434'
MAX_BYTES = 900_000_000


def digest(path):
    value=sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):value.update(block)
    return value.hexdigest()


def install(archive, output):
    archive,output=Path(archive).resolve(),Path(output).resolve()
    if archive.is_symlink() or not archive.is_file() or not 0<archive.stat().st_size<=MAX_BYTES:
        raise ValueError('Ordinary bounded official FreeCAD archive required')
    if digest(archive)!=SHA256:raise ValueError('Official FreeCAD archive SHA256 differs; extraction refused')
    if output.exists():raise ValueError('Fresh FreeCAD installation directory required')
    output.mkdir(parents=True)
    archive.chmod(archive.stat().st_mode | 0o100)
    result=subprocess.run([str(archive),'--appimage-extract'],cwd=output,capture_output=True,text=True,timeout=180)
    (output/'extract.log').write_text(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError('Official FreeCAD extraction failed; inspect extract.log')
    app=output/'squashfs-root';launcher=app/'AppRun';binary=app/'usr/bin/freecadcmd'
    if not launcher.is_file() or not binary.is_file():raise ValueError('Official AppRun/freecadcmd layout missing')
    wrapper=output/'bin/FreeCADCmd';wrapper.parent.mkdir()
    # AppRun configures the bundle's own Python3.11 and dispatches the packaged command.
    wrapper.write_text('#!/bin/sh\nunset PYTHONHOME PYTHONPATH LD_LIBRARY_PATH\nexec '+shlex.quote(str(launcher))+' freecadcmd "$@"\n')
    wrapper.chmod(0o755)
    report=dict(schema='osr-pinned-historical-freecad-install/1',release=VERSION,asset_url=URL,
        archive_sha256=SHA256,archive_bytes=archive.stat().st_size,
        app_run_sha256=digest(launcher),native_command_sha256=digest(binary),
        command_wrapper_sha256=digest(wrapper),installer_sha256=digest(__file__),
        bundled_python='3.11; actual version checked by native preflight',
        scope='Explicit reexecution toolchain; not a claim of identical historical native output or physical qualification',
        physical_accepted=False)
    (output/'install.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(install(args.archive,args.output),sort_keys=True))
