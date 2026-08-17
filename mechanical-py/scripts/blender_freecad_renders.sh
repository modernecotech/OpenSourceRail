#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$ROOT/.." && pwd)"
SCRIPT="$ROOT/src/osr_mech/blender_freecad_renders.py"

if command -v blender >/dev/null 2>&1; then
    blender --background --python "$SCRIPT" -- "$@"
    exit $?
fi

if command -v flatpak >/dev/null 2>&1 && flatpak info org.blender.Blender >/dev/null 2>&1; then
    flatpak run \
        --filesystem="$REPO_ROOT" \
        --command=blender org.blender.Blender \
        --background --python "$SCRIPT" -- "$@"
    exit $?
fi

cat >&2 <<'EOF'
Blender was not found.

Install Blender or expose its command-line runtime, then retry:
  mechanical-py/scripts/blender_freecad_renders.sh

Flatpak installations are also supported when org.blender.Blender is installed.
EOF
exit 127
