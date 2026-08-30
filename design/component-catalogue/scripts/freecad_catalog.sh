#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$ROOT/../.." && pwd)"
SCRIPT="$ROOT/src/osr_mech/freecad_catalog.py"
ARGS_PY="$(python3 - "$@" <<'PY'
import sys
print(repr(sys.argv[1:]))
PY
)"
WRAPPER="$(mktemp "$ROOT/.freecad_catalog.XXXXXX.py")"
trap 'rm -f "$WRAPPER"' EXIT
cat >"$WRAPPER" <<PY
import runpy, sys, traceback
sys.path.insert(0, r"$ROOT/src")
sys.argv = [r"$SCRIPT"] + $ARGS_PY
try:
    runpy.run_path(r"$SCRIPT", run_name="__main__")
except SystemExit:
    raise
except Exception:
    traceback.print_exc()
    sys.exit(1)
PY

if command -v FreeCADCmd >/dev/null 2>&1; then
    FreeCADCmd "$WRAPPER"
elif command -v freecadcmd >/dev/null 2>&1; then
    freecadcmd "$WRAPPER"
elif command -v flatpak >/dev/null 2>&1 && flatpak info org.freecad.FreeCAD >/dev/null 2>&1; then
    flatpak run --filesystem="$REPO_ROOT" --env=PYTHONPATH="$ROOT/src" \
        --command=FreeCADCmd org.freecad.FreeCAD "$WRAPPER"
else
    echo "FreeCADCmd was not found; install FreeCAD or org.freecad.FreeCAD Flatpak." >&2
    exit 127
fi
