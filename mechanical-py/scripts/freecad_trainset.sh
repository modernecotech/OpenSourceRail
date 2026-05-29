#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="$ROOT/src/osr_mech/freecad_trainset.py"

ARGS_PY="$(python3 - "$@" <<'PY'
import sys
print(repr(sys.argv[1:]))
PY
)"
WRAPPER="$(mktemp "$ROOT/.freecad_trainset.XXXXXX.py")"
trap 'rm -f "$WRAPPER"' EXIT
cat >"$WRAPPER" <<PY
import runpy
import sys

sys.argv = [r"$SCRIPT"] + $ARGS_PY
runpy.run_path(r"$SCRIPT", run_name="__main__")
PY

if command -v FreeCADCmd >/dev/null 2>&1; then
    FreeCADCmd "$WRAPPER"
    exit $?
fi

if command -v freecadcmd >/dev/null 2>&1; then
    freecadcmd "$WRAPPER"
    exit $?
fi

if command -v flatpak >/dev/null 2>&1 && flatpak info org.freecad.FreeCAD >/dev/null 2>&1; then
    flatpak run \
        --filesystem="$ROOT" \
        --env=PYTHONPATH="$ROOT/src" \
        --command=FreeCADCmd org.freecad.FreeCAD \
        "$WRAPPER"
    exit $?
fi

cat >&2 <<'EOF'
FreeCADCmd was not found.

Install FreeCAD or expose its command-line runtime, then retry:
  FreeCADCmd src/osr_mech/freecad_trainset.py --family light-metro-3car

Flatpak installations are also supported when org.freecad.FreeCAD is installed.
EOF
exit 127
