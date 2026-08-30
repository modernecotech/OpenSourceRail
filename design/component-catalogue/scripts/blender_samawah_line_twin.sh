#!/usr/bin/env bash
set -euo pipefail

MECH_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$MECH_ROOT/../.." && pwd)"
CITY_DIR="$REPO_ROOT/cities/catalogue/west-asia/Iraq/Samawah"
SCRIPT="$MECH_ROOT/src/osr_mech/blender_samawah_line_twin.py"
OUTPUT="$CITY_DIR/engineering/digital-twin/samawah-line1-digital-twin.gif"
VIDEO="$CITY_DIR/engineering/digital-twin/samawah-line1-digital-twin.mp4"
BLEND="$CITY_DIR/engineering/digital-twin/samawah-line1-digital-twin.blend"
WIDTH=800
HEIGHT=450
FPS=5
SAMPLES=4
STILL_TIME=""

while [ "$#" -gt 0 ]; do
    case "$1" in
        --city-dir) CITY_DIR="$2"; shift 2 ;;
        --out) OUTPUT="$2"; shift 2 ;;
        --video) VIDEO="$2"; shift 2 ;;
        --blend) BLEND="$2"; shift 2 ;;
        --width) WIDTH="$2"; shift 2 ;;
        --height) HEIGHT="$2"; shift 2 ;;
        --fps) FPS="$2"; shift 2 ;;
        --samples) SAMPLES="$2"; shift 2 ;;
        --still-time) STILL_TIME="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [--out GIF] [--video MP4] [--blend FILE] [--width PX] [--height PX] [--fps N] [--samples N] [--still-time SEC]"
            exit 0
            ;;
        *) echo "unknown option: $1" >&2; exit 2 ;;
    esac
done

OUTPUT="$(realpath -m "$OUTPUT")"
VIDEO="$(realpath -m "$VIDEO")"
BLEND="$(realpath -m "$BLEND")"

FRAME_DIR="$(mktemp -d /tmp/osr-samawah-blender-frames.XXXXXX)"
cleanup() {
    status=$?
    if [ "$status" -eq 0 ]; then
        rm -rf "$FRAME_DIR"
    else
        echo "retained Blender frames after failure: $FRAME_DIR" >&2
    fi
}
trap cleanup EXIT

if command -v blender >/dev/null 2>&1; then
    BLENDER=(blender)
    FFMPEG=(ffmpeg)
elif command -v flatpak >/dev/null 2>&1 && flatpak info --user org.blender.Blender >/dev/null 2>&1; then
    BLENDER=(flatpak run --filesystem="$REPO_ROOT" --filesystem="$FRAME_DIR" --command=blender org.blender.Blender)
    FFMPEG=(flatpak run --filesystem="$REPO_ROOT" --filesystem="$FRAME_DIR" --command=ffmpeg org.blender.Blender)
elif command -v flatpak >/dev/null 2>&1 && flatpak info org.blender.Blender >/dev/null 2>&1; then
    BLENDER=(flatpak run --filesystem="$REPO_ROOT" --filesystem="$FRAME_DIR" --command=blender org.blender.Blender)
    FFMPEG=(flatpak run --filesystem="$REPO_ROOT" --filesystem="$FRAME_DIR" --command=ffmpeg org.blender.Blender)
else
    echo "Blender is required for the Samawah perspective animation." >&2
    exit 127
fi

BLENDER_ARGS=(
    --background --python "$SCRIPT" --
    --frames-dir "$FRAME_DIR"
    --blend "$BLEND"
    --width "$WIDTH"
    --height "$HEIGHT"
    --fps "$FPS"
    --samples "$SAMPLES"
)
if [ -n "$STILL_TIME" ]; then
    BLENDER_ARGS+=(--still-time "$STILL_TIME")
fi
"${BLENDER[@]}" "${BLENDER_ARGS[@]}"

if [ -n "$STILL_TIME" ]; then
    if [ ! -s "$FRAME_DIR/preview.png" ]; then
        echo "Blender did not produce the requested preview frame" >&2
        exit 1
    fi
    cp "$FRAME_DIR/preview.png" "$OUTPUT"
    echo "wrote Blender preview $OUTPUT"
    exit 0
fi

EXPECTED_FRAMES=$((46 * FPS))
ACTUAL_FRAMES="$(find "$FRAME_DIR" -maxdepth 1 -type f -name 'frame-*.png' | wc -l)"
if [ "$ACTUAL_FRAMES" -ne "$EXPECTED_FRAMES" ]; then
    echo "expected $EXPECTED_FRAMES Blender frames, found $ACTUAL_FRAMES" >&2
    exit 1
fi

mkdir -p "$(dirname "$OUTPUT")" "$(dirname "$VIDEO")"
"${FFMPEG[@]}" -v error -framerate "$FPS" -i "$FRAME_DIR/frame-%04d.png" \
    -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -movflags +faststart -y "$VIDEO"

PALETTE="$FRAME_DIR/palette.png"
"${FFMPEG[@]}" -v error -i "$VIDEO" \
    -vf "fps=$FPS,scale=$WIDTH:$HEIGHT:flags=lanczos,palettegen=max_colors=256:stats_mode=full" \
    -frames:v 1 -y "$PALETTE"
"${FFMPEG[@]}" -v error -i "$VIDEO" -i "$PALETTE" \
    -lavfi "fps=$FPS,scale=$WIDTH:$HEIGHT:flags=lanczos[x];[x][1:v]paletteuse=dither=sierra2_4a" \
    -loop 0 -y "$OUTPUT"

SIZE_BYTES="$(stat -c %s "$OUTPUT")"
if [ "$SIZE_BYTES" -ge 20000000 ]; then
    SMALL_WIDTH=$((WIDTH * 5 / 6))
    SMALL_HEIGHT=$((HEIGHT * 5 / 6))
    "${FFMPEG[@]}" -v error -i "$VIDEO" \
        -vf "fps=4,scale=$SMALL_WIDTH:$SMALL_HEIGHT:flags=lanczos,palettegen=max_colors=192:stats_mode=diff" \
        -frames:v 1 -y "$PALETTE"
    "${FFMPEG[@]}" -v error -i "$VIDEO" -i "$PALETTE" \
        -lavfi "fps=4,scale=$SMALL_WIDTH:$SMALL_HEIGHT:flags=lanczos[x];[x][1:v]paletteuse=dither=sierra2_4a:diff_mode=rectangle" \
        -loop 0 -y "$OUTPUT"
    SIZE_BYTES="$(stat -c %s "$OUTPUT")"
fi
if [ "$SIZE_BYTES" -ge 20000000 ]; then
    echo "Blender Samawah GIF exceeds the 20 MB README limit: $SIZE_BYTES bytes" >&2
    exit 1
fi

echo "wrote $BLEND"
echo "wrote $VIDEO"
echo "wrote $OUTPUT ($SIZE_BYTES bytes, $EXPECTED_FRAMES source frames)"
