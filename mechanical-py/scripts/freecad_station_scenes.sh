#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$ROOT/.." && pwd)"
SCRIPT="$ROOT/src/osr_mech/freecad_station_scenes.py"

ARGS_PY="$(python3 - "$@" <<'PY'
import sys
print(repr(sys.argv[1:]))
PY
)"
WRAPPER="$(mktemp "$ROOT/.freecad_station_scenes.XXXXXX.py")"
trap 'rm -f "$WRAPPER"' EXIT
cat >"$WRAPPER" <<PY
import runpy
import sys
import traceback

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

if command -v FreeCAD >/dev/null 2>&1; then
    if command -v xvfb-run >/dev/null 2>&1; then
        xvfb-run -a FreeCAD "$WRAPPER"
    else
        FreeCAD "$WRAPPER"
    fi
    exit $?
fi

if command -v freecad >/dev/null 2>&1; then
    if command -v xvfb-run >/dev/null 2>&1; then
        xvfb-run -a freecad "$WRAPPER"
    else
        freecad "$WRAPPER"
    fi
    exit $?
fi

if command -v flatpak >/dev/null 2>&1 && flatpak info org.freecad.FreeCAD >/dev/null 2>&1; then
    if command -v xvfb-run >/dev/null 2>&1; then
        xvfb-run -a flatpak run \
            --filesystem="$REPO_ROOT" \
            --env=PYTHONPATH="$ROOT/src" \
            --command=FreeCAD org.freecad.FreeCAD \
            "$WRAPPER"
    else
        flatpak run \
            --filesystem="$REPO_ROOT" \
            --env=PYTHONPATH="$ROOT/src" \
            --command=FreeCAD org.freecad.FreeCAD \
            "$WRAPPER"
    fi
    exit $?
fi

cat >&2 <<'EOF'
FreeCAD GUI was not found.

Install FreeCAD or expose its GUI runtime, then retry:
  mechanical-py/scripts/freecad_station_scenes.sh

Flatpak installations are also supported when org.freecad.FreeCAD is installed.
EOF
exit 127
