#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="$ROOT/src/osr_mech/freecad_platform_l_unit.py"
OUTPUT="${1:-$ROOT/models/cad/platform-l-unit.FCStd}"
WRAPPER="$(mktemp "$ROOT/.freecad_platform_l_unit.XXXXXX.py")"
trap 'rm -f "$WRAPPER"' EXIT
cat >"$WRAPPER" <<PY
import runpy
import sys
sys.path.insert(0, r"$ROOT/src")
sys.argv = [r"$SCRIPT", r"$OUTPUT"]
runpy.run_path(r"$SCRIPT", run_name="__main__")
PY

if command -v FreeCADCmd >/dev/null 2>&1; then
    FreeCADCmd "$WRAPPER"
elif command -v freecadcmd >/dev/null 2>&1; then
    freecadcmd "$WRAPPER"
elif flatpak info org.freecad.FreeCAD >/dev/null 2>&1; then
    flatpak run --filesystem="$ROOT" --command=FreeCADCmd org.freecad.FreeCAD "$WRAPPER"
else
    echo "FreeCADCmd was not found." >&2
    exit 127
fi
