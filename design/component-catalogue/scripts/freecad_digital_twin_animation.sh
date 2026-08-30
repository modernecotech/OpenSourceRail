#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$ROOT/../.." && pwd)"
source "$ROOT/scripts/headless_gui.sh"
RUNNER="$ROOT/freecad_digital_twin_animation_runner.py"
MODEL="$ROOT/models/cad/civil-systems-integration-test.FCStd"
OUTPUT="$REPO_ROOT/docs/assets/digital-twin-animation.gif"
GROUND_FRAMES=72
ELEVATED_FRAMES=88
WIDTH=960
HEIGHT=540

while [ "$#" -gt 0 ]; do
    case "$1" in
        --model) MODEL="$2"; shift 2 ;;
        --out) OUTPUT="$2"; shift 2 ;;
        --ground-frames) GROUND_FRAMES="$2"; shift 2 ;;
        --elevated-frames) ELEVATED_FRAMES="$2"; shift 2 ;;
        --width) WIDTH="$2"; shift 2 ;;
        --height) HEIGHT="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [--model FILE] [--out GIF] [--ground-frames N] [--elevated-frames N] [--width PX] [--height PX]"
            exit 0
            ;;
        *) echo "unknown option: $1" >&2; exit 2 ;;
    esac
done

if ! command -v magick >/dev/null 2>&1 || ! command -v ffmpeg >/dev/null 2>&1; then
    echo "ImageMagick 'magick' and FFmpeg are required to annotate and encode the animation." >&2
    exit 127
fi

FRAME_DIR="$(mktemp -d /tmp/osr-digital-twin-frames.XXXXXX)"
cleanup() {
    rm -rf "$FRAME_DIR"
}
trap cleanup EXIT

export OSR_TWIN_ANIMATION_RUN=1
export OSR_TWIN_MODEL="$MODEL"
export OSR_TWIN_FRAME_DIR="$FRAME_DIR"
export OSR_TWIN_GROUND_FRAMES="$GROUND_FRAMES"
export OSR_TWIN_ELEVATED_FRAMES="$ELEVATED_FRAMES"
export OSR_TWIN_WIDTH="$WIDTH"
export OSR_TWIN_HEIGHT="$HEIGHT"

run_freecad() {
    if command -v FreeCAD >/dev/null 2>&1; then
        run_headless_gui FreeCAD "$RUNNER"
    elif command -v freecad >/dev/null 2>&1; then
        run_headless_gui freecad "$RUNNER"
    elif command -v flatpak >/dev/null 2>&1 && flatpak info org.freecad.FreeCAD >/dev/null 2>&1; then
        run_headless_gui flatpak run \
            --filesystem="$REPO_ROOT" \
            --filesystem="$FRAME_DIR" \
            --env=OSR_TWIN_ANIMATION_RUN=1 \
            --env=OSR_TWIN_MODEL="$MODEL" \
            --env=OSR_TWIN_FRAME_DIR="$FRAME_DIR" \
            --env=OSR_TWIN_GROUND_FRAMES="$GROUND_FRAMES" \
            --env=OSR_TWIN_ELEVATED_FRAMES="$ELEVATED_FRAMES" \
            --env=OSR_TWIN_WIDTH="$WIDTH" \
            --env=OSR_TWIN_HEIGHT="$HEIGHT" \
            --command=FreeCAD org.freecad.FreeCAD "$RUNNER"
    else
        echo "FreeCAD GUI was not found." >&2
        exit 127
    fi
}

run_freecad

mapfile -t FRAMES < <(find "$FRAME_DIR" -maxdepth 1 -type f -name 'frame-*.png' | sort)
EXPECTED_FRAMES=$((GROUND_FRAMES + ELEVATED_FRAMES))
if [ "${#FRAMES[@]}" -ne "$EXPECTED_FRAMES" ]; then
    echo "expected $EXPECTED_FRAMES frames, found ${#FRAMES[@]}" >&2
    exit 1
fi

ANNOTATED_DIR="$FRAME_DIR/annotated"
mkdir -p "$ANNOTATED_DIR"
for frame in "${FRAMES[@]}"; do
    name="$(basename "$frame")"
    if [[ "$name" == *-ground.png ]]; then
        caption="GROUND STATION → JUNCTION  •  LM3-001  •  DEPARTURE"
    else
        caption="VIADUCT → ELEVATED STATION  •  LM3-002  •  IN SERVICE"
    fi
    magick "$frame" \
        -gravity South -background '#0f172a' -splice 0x48 \
        -font DejaVu-Sans-Bold -pointsize 18 -fill white \
        -annotate +0+14 "$caption" \
        "$ANNOTATED_DIR/$name"
done

mkdir -p "$(dirname "$OUTPUT")"
PALETTE="$FRAME_DIR/palette.png"
ffmpeg -v error -framerate 25/3 -pattern_type glob \
    -i "$ANNOTATED_DIR/frame-*.png" \
    -vf "palettegen=max_colors=128:stats_mode=diff" -frames:v 1 -y "$PALETTE"
ffmpeg -v error -framerate 25/3 -pattern_type glob \
    -i "$ANNOTATED_DIR/frame-*.png" -i "$PALETTE" \
    -lavfi "fps=25/3[x];[x][1:v]paletteuse=dither=sierra2_4a:diff_mode=rectangle" \
    -loop 0 -y "$OUTPUT"

MAX_BYTES=20000000
SIZE_BYTES="$(stat -c %s "$OUTPUT")"
if [ "$SIZE_BYTES" -ge "$MAX_BYTES" ]; then
    ffmpeg -v error -framerate 25/3 -pattern_type glob \
        -i "$ANNOTATED_DIR/frame-*.png" \
        -vf "fps=6,scale=800:-1:flags=lanczos,palettegen=max_colors=96:stats_mode=diff" \
        -frames:v 1 -y "$PALETTE"
    ffmpeg -v error -framerate 25/3 -pattern_type glob \
        -i "$ANNOTATED_DIR/frame-*.png" -i "$PALETTE" \
        -lavfi "fps=6,scale=800:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=sierra2_4a:diff_mode=rectangle" \
        -loop 0 -y "$OUTPUT"
    SIZE_BYTES="$(stat -c %s "$OUTPUT")"
fi
if [ "$SIZE_BYTES" -ge "$MAX_BYTES" ]; then
    echo "encoded GIF is $SIZE_BYTES bytes, at or above the 20 MB repository limit" >&2
    exit 1
fi

ffprobe -v error -select_streams v:0 -count_frames \
    -show_entries stream=width,height,nb_read_frames,avg_frame_rate \
    -of default=noprint_wrappers=1 "$OUTPUT"
echo "wrote $OUTPUT ($SIZE_BYTES bytes, ${#FRAMES[@]} frames)"
