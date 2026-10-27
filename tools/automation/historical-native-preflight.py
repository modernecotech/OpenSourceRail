#!/usr/bin/env python3
"""Bounded direct-FreeCAD and runner-tool preflight for the pinned v0.5 cycle."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def _run(output):
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    freecad = shutil.which('FreeCADCmd') or shutil.which('freecadcmd')
    if not freecad:
        raise ValueError('Direct FreeCADCmd/freecadcmd required; the runner must not fall through to an uninstalled Flatpak app')
    paths = {'freecad': freecad}
    for name in ('gmsh', 'getdp', 'ccx', 'ffmpeg', 'ffprobe'):
        paths[name] = shutil.which(name)
        if paths[name] is None:
            raise ValueError('Historical cycle runner dependency missing: ' + name)
    environment = dict(os.environ, QT_QPA_PLATFORM='offscreen')
    with tempfile.TemporaryDirectory(prefix='historical-cad-preflight-', dir=output.parent) as temporary:
        directory = Path(temporary)
        result = directory / 'freecad-result.json'
        script = directory / 'probe.py'
        script.write_text('import sys\nsys.path.insert(0, ' + repr(str(Path.cwd())) + ')\n'
                          'import FreeCAD as App, Part, json, sys\n'
                          'from engineering.factory_examples import native\n'
                          'from engineering.ferrite_maglev import assembled_body, shared_hub_layout\n'
                          'shape = Part.makeBox(1, 1, 1)\n'
                          'assert shape.isValid() and abs(shape.Volume - 1) < 1e-12\n'
                          'open(' + repr(str(result)) + ', "w").write(json.dumps(dict(freecad_version=list(App.Version()), opencascade_version=Part.OCC_VERSION, python_version=sys.version)))\n')
        try:
            completed = subprocess.run([freecad, str(script)], env=environment, capture_output=True, text=True, timeout=60)
        except subprocess.TimeoutExpired as exc:
            def decoded(value):
                return value.decode(errors='replace') if isinstance(value, bytes) else (value or '')
            output.with_suffix('.log').write_text(decoded(exc.stdout) + decoded(exc.stderr) + '\nFreeCAD preflight timed out after 60 seconds\n')
            raise
        output.with_suffix('.log').write_text(completed.stdout + completed.stderr)
        if completed.returncode or not result.is_file():
            raise RuntimeError('Direct FreeCAD preflight failed; inspect ' + str(output.with_suffix('.log')))
        native = json.loads(result.read_text())
    report = dict(schema='osr-historical-native-runner-preflight/1',
                  tools={name:dict(path=path, binary_sha256=sha256(Path(path).read_bytes()).hexdigest()) for name, path in paths.items()},
                  freecad=native, qt_platform='offscreen',
                  scope='Dependency import and unit-cube BRep smoke check; no vehicle or physical qualification',
                  physical_accepted=False, engineering_accepted=False)
    output.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n')
    return report


def run(output):
    output = Path(output).resolve()
    try:
        return _run(output)
    except Exception as exc:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(dict(schema='osr-historical-native-runner-preflight/1',
            execution='held', error=type(exc).__name__ + ': ' + str(exc),
            required_tools=['FreeCADCmd or freecadcmd', 'gmsh', 'getdp', 'ccx', 'ffmpeg', 'ffprobe'],
            qt_platform='offscreen', physical_accepted=False, engineering_accepted=False),
            sort_keys=True, indent=2) + '\n')
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    print(json.dumps(run(parser.parse_args().output), sort_keys=True))
