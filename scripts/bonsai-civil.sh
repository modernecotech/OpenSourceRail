#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT/build/engineering/bonsai-civil"
ALIGNMENT_INPUT=""
REVISION_ID="working-tree"
DO_GENERATE=false
DO_RENDER=false
DO_ANIMATE=false
DO_CHECK=false

usage() {
    echo 'Usage: scripts/bonsai-civil.sh [--generate] [--render] [--animate] [--check] [--out-dir PATH] [--alignment-input PATH] [--revision-id ID]'
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --generate) DO_GENERATE=true ;;
        --render) DO_GENERATE=true; DO_RENDER=true ;;
        --animate) DO_GENERATE=true; DO_RENDER=true; DO_ANIMATE=true ;;
        --check) DO_CHECK=true ;;
        --out-dir) OUT_DIR="$2"; shift ;;
        --alignment-input) ALIGNMENT_INPUT="$2"; shift ;;
        --revision-id) REVISION_ID="$2"; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    esac
    shift
done

OUT_DIR="$(realpath -m "$OUT_DIR")"
if [[ -n "$ALIGNMENT_INPUT" ]]; then
    ALIGNMENT_INPUT="$(realpath "$ALIGNMENT_INPUT")"
fi

if ! $DO_GENERATE && ! $DO_CHECK; then
    DO_GENERATE=true
fi

if $DO_CHECK; then
    "$ROOT/.venv/bin/python" -c 'import ifcopenshell; print("IfcOpenShell", ifcopenshell.version)'
    flatpak run org.blender.Blender --version | head -n 1
    flatpak run org.blender.Blender -b --python-expr \
        'import importlib.metadata; print("Bonsai", importlib.metadata.version("bonsai"))' 2>&1 | grep '^Bonsai '
fi

if $DO_GENERATE; then
    args=(
        "$ROOT/engineering/interchange/civil_bonsai_ifc.py"
        --out-dir "$OUT_DIR"
        --revision-id "$REVISION_ID"
    )
    if [[ -n "$ALIGNMENT_INPUT" ]]; then
        args+=(--alignment-input "$ALIGNMENT_INPUT")
    fi
    "$ROOT/.venv/bin/python" "${args[@]}"
fi

if $DO_RENDER; then
    blender_args=(
        -b --python "$ROOT/scripts/bonsai-render-civil.py" --
        --ifc "$OUT_DIR/civil-coordination.ifc"
        --index "$OUT_DIR/civil-coordination.index.json"
        --sequence "$OUT_DIR/civil-construction-sequence.json"
        --output "$OUT_DIR/civil-coordination.png"
        --blend "$OUT_DIR/civil-coordination.blend"
    )
    if $DO_ANIMATE; then
        blender_args+=(--animation-output "$OUT_DIR/civil-construction-sequence.mp4")
    fi
    flatpak run org.blender.Blender "${blender_args[@]}"
    if $DO_ANIMATE; then
        ffmpeg -y -framerate 24 \
            -i "$OUT_DIR/civil-construction-sequence-frames/frame-%04d.png" \
            -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
            "$OUT_DIR/civil-construction-sequence.mp4"
    fi
fi
