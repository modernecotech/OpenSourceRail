#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
"$ROOT/tools/automation/osr-python" "$ROOT/tools/automation/generate-civil-cost-model.py"
OUT_DIR="$ROOT/build/engineering/bonsai-civil"
ALIGNMENT_INPUT=""
REVISION_ID="working-tree"
DO_GENERATE=false
DO_RENDER=false
DO_ANIMATE=false
DO_CHECK=false

usage() {
    echo 'Usage: tools/automation/bonsai-civil.sh [--generate] [--render] [--animate] [--check] [--out-dir PATH] [--alignment-input PATH] [--revision-id ID]'
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
    "$ROOT/tools/automation/osr-python" -c 'import ifcopenshell, importlib.metadata; print("IfcOpenShell", ifcopenshell.version); print("IfcTester", importlib.metadata.version("ifctester")); print("BCF", importlib.metadata.version("bcf-client"))'
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
    "$ROOT/tools/automation/osr-python" "${args[@]}"
fi

if $DO_RENDER; then
    REVIEW_OUTPUT="$OUT_DIR/civil-coordination.png"
    REVIEW_DETAIL="$OUT_DIR/civil-pi25-detail.png"
    if [[ "$OUT_DIR" == "$ROOT/engineering/models/bim/reference" ]]; then
        REVIEW_OUTPUT="$ROOT/docs/screenshots/civil/bonsai-ifc4x3-civil-coordination.png"
        REVIEW_DETAIL="$ROOT/docs/screenshots/civil/bonsai-pi25-support-detail.png"
    fi
    blender_args=(
        -b --python "$ROOT/tools/automation/bonsai-render-civil.py" --
        --ifc "$OUT_DIR/civil-coordination.ifc"
        --index "$OUT_DIR/civil-coordination.index.json"
        --sequence "$OUT_DIR/civil-construction-sequence.json"
        --output "$REVIEW_OUTPUT"
        --detail-output "$REVIEW_DETAIL"
        --blend "$OUT_DIR/civil-coordination.blend"
        --milestones-dir "$ROOT/docs/screenshots/civil"
    )
    if $DO_ANIMATE; then
        blender_args+=(--animation-output "$OUT_DIR/civil-construction-sequence.mp4")
    fi
    flatpak run org.blender.Blender "${blender_args[@]}"
    if $DO_ANIMATE; then
        FPS="$("$ROOT/tools/automation/osr-python" -c 'import json,sys; print(json.load(open(sys.argv[1]))["animation"]["fps"])' "$OUT_DIR/civil-construction-sequence.json")"
        ffmpeg -y -framerate "$FPS" \
            -i "$OUT_DIR/civil-construction-sequence-frames/frame-%04d.png" \
            -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
            "$OUT_DIR/civil-construction-sequence.mp4"
        PALETTE="$OUT_DIR/civil-construction-sequence-palette.png"
        ffmpeg -v error -y -i "$OUT_DIR/civil-construction-sequence.mp4" \
            -vf "fps=4,scale=800:450:flags=lanczos,palettegen=max_colors=192:stats_mode=diff" \
            -frames:v 1 "$PALETTE"
        ffmpeg -v error -y -i "$OUT_DIR/civil-construction-sequence.mp4" -i "$PALETTE" \
            -lavfi "fps=4,scale=800:450:flags=lanczos[x];[x][1:v]paletteuse=dither=sierra2_4a:diff_mode=rectangle" \
            -loop 0 "$OUT_DIR/civil-construction-sequence.gif"
        test "$(stat -c %s "$OUT_DIR/civil-construction-sequence.gif")" -lt 20000000
        rm -f "$PALETTE"
        rm -rf "$OUT_DIR/civil-construction-sequence-frames"
    fi
fi
