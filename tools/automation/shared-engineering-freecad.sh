#!/usr/bin/env bash
# Use the installed native FreeCAD runtime, preserving quoted engineering arguments.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
mkdir -p "$ROOT/build"
NATIVE_WRAPPER="$(mktemp "$ROOT/build/.shared-freecad.XXXXXX.py")"
NATIVE_SUCCESS="$NATIVE_WRAPPER.ok"
trap 'rm -f "$NATIVE_WRAPPER" "$NATIVE_SUCCESS"' EXIT
python3 - "$ROOT" "$NATIVE_SUCCESS" "$@" > "$NATIVE_WRAPPER" <<'PY'
import sys
from pathlib import Path
root,success,*arguments=sys.argv[1:]
script=str(Path(root)/'tools/automation/shared-engineering-freecad.py')
print('import runpy,sys,traceback')
print('from pathlib import Path')
print('sys.argv='+repr([script,*arguments]))
print('try:')
print('    runpy.run_path(sys.argv[0],run_name="__main__")')
print('    Path('+repr(success)+').write_text("ok")')
print('except Exception:')
print('    traceback.print_exc()')
print('    raise SystemExit(1)')
PY
if command -v FreeCADCmd >/dev/null 2>&1; then
    FreeCADCmd "$NATIVE_WRAPPER"
elif command -v freecadcmd >/dev/null 2>&1; then
    freecadcmd "$NATIVE_WRAPPER"
elif command -v flatpak >/dev/null 2>&1 && flatpak info org.freecad.FreeCAD >/dev/null 2>&1; then
    flatpak run --filesystem="$ROOT" --command=FreeCADCmd org.freecad.FreeCAD "$NATIVE_WRAPPER"
else
    printf 'FreeCADCmd or the FreeCAD Flatpak runtime is required.\n' >&2
    exit 127
fi
test -f "$NATIVE_SUCCESS"
