#!/usr/bin/env bash
set -euo pipefail

MECH_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$MECH_ROOT/../.." && pwd)"
TWIN_DIR="$REPO_ROOT/engineering/models/digital-twins/fabrication-assembly"
SCRIPT="$MECH_ROOT/src/osr_mech/blender_fabrication_assembly_twin.py"
OUTPUT="$TWIN_DIR/fabrication-assembly-digital-twin.gif"
VIDEO="$TWIN_DIR/fabrication-assembly-digital-twin.mp4"
BLEND="$TWIN_DIR/fabrication-assembly-digital-twin.blend"
MANIFEST="$TWIN_DIR/fabrication-assembly-digital-twin.json"
WIDTH=960
HEIGHT=540
FPS=6
SAMPLES=8
TOUR_DURATION=88
STILL_TIME=""

while [ "$#" -gt 0 ]; do
    case "$1" in
        --out) OUTPUT="$2"; shift 2 ;;
        --video) VIDEO="$2"; shift 2 ;;
        --blend) BLEND="$2"; shift 2 ;;
        --manifest) MANIFEST="$2"; shift 2 ;;
        --width) WIDTH="$2"; shift 2 ;;
        --height) HEIGHT="$2"; shift 2 ;;
        --fps) FPS="$2"; shift 2 ;;
        --samples) SAMPLES="$2"; shift 2 ;;
        --still-time) STILL_TIME="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [--out GIF] [--video MP4] [--blend FILE] [--manifest JSON] [--still-time SEC]"
            exit 0 ;;
        *) echo "unknown option: $1" >&2; exit 2 ;;
    esac
done

OUTPUT="$(realpath -m "$OUTPUT")"
VIDEO="$(realpath -m "$VIDEO")"
BLEND="$(realpath -m "$BLEND")"
MANIFEST="$(realpath -m "$MANIFEST")"
FRAME_DIR="$(mktemp -d /tmp/osr-fabrication-twin-frames.XXXXXX)"
cleanup() {
    status=$?
    if [ "$status" -eq 0 ]; then rm -rf "$FRAME_DIR"; else echo "retained frames: $FRAME_DIR" >&2; fi
}
trap cleanup EXIT

mkdir -p "$(dirname "$MANIFEST")"
PYTHONPATH="$MECH_ROOT/src" python3 -m osr_mech.fabrication_assembly_twin --out "$MANIFEST"

if command -v blender >/dev/null 2>&1; then
    BLENDER=(blender)
elif flatpak info --user org.blender.Blender >/dev/null 2>&1; then
    BLENDER=(flatpak run --filesystem="$REPO_ROOT" --filesystem="$FRAME_DIR" --command=blender org.blender.Blender)
else
    echo "Blender is required for the fabrication twin animation." >&2
    exit 127
fi
if command -v ffmpeg >/dev/null 2>&1; then
    FFMPEG=(ffmpeg)
else
    FFMPEG=(flatpak run --filesystem="$REPO_ROOT" --filesystem="$FRAME_DIR" --command=ffmpeg org.blender.Blender)
fi
FONT_FILE="$(fc-match -f '%{file}\n' 'DejaVu Sans Bold' | head -n 1)"
test -f "$FONT_FILE"

ARGS=(--background --python "$SCRIPT" -- --frames-dir "$FRAME_DIR" --blend "$BLEND" --width "$WIDTH" --height "$HEIGHT" --fps "$FPS" --samples "$SAMPLES")
if [ -n "$STILL_TIME" ]; then ARGS+=(--still-time "$STILL_TIME"); fi
"${BLENDER[@]}" "${ARGS[@]}"

if [ -n "$STILL_TIME" ]; then
    test -s "$FRAME_DIR/preview.png"
    cp "$FRAME_DIR/preview.png" "$OUTPUT"
    echo "wrote fabrication twin preview $OUTPUT"
    exit 0
fi

EXPECTED=$((TOUR_DURATION * FPS))
ACTUAL="$(find "$FRAME_DIR" -maxdepth 1 -name 'frame-*.png' -type f | wc -l)"
test "$ACTUAL" -eq "$EXPECTED"
mkdir -p "$(dirname "$OUTPUT")" "$(dirname "$VIDEO")"
RAW_VIDEO="$FRAME_DIR/fabrication-tour-raw.mp4"
"${FFMPEG[@]}" -v error -framerate "$FPS" -i "$FRAME_DIR/frame-%04d.png" \
    -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -c:v libx264 -preset slow -crf 17 \
    -pix_fmt yuv420p -movflags +faststart -y "$RAW_VIDEO"
OVERLAY_FILTER="drawbox=x=0:y=0:w=iw:h=78:color=0x07131ee6:t=78,\
drawtext=fontfile='$FONT_FILE':text='OPENSOURCERAIL  •  GUIDED FABRICATION + ASSEMBLY TOUR':x=28:y=14:fontsize=20:fontcolor=white,\
drawtext=fontfile='$FONT_FILE':text='1/4  TRACK PANEL  •  PLINTHS > FASTENERS > RAILS > GEOMETRY RELEASE':x=28:y=44:fontsize=18:fontcolor=0x67e8f9:enable='between(t,0,20.99)',\
drawtext=fontfile='$FONT_FILE':text='2/4  STATION KIT  •  PLATFORMS > PORTALS > ROOF CASSETTES > SYSTEMS':x=28:y=44:fontsize=18:fontcolor=0x67e8f9:enable='between(t,21,40.99)',\
drawtext=fontfile='$FONT_FILE':text='3/4  VIADUCT BAY  •  SUBSTRUCTURE > BEARINGS > BEAMS > EGRESS':x=28:y=44:fontsize=18:fontcolor=0x67e8f9:enable='between(t,41,62.99)',\
drawtext=fontfile='$FONT_FILE':text='4/4  LM3 TRAINSET  •  BOGIES > BODIES > SYSTEMS > FIT-OUT > RELEASE':x=28:y=44:fontsize=18:fontcolor=0x67e8f9:enable='between(t,63,81.99)',\
drawtext=fontfile='$FONT_FILE':text='COMPLETED PRODUCTS  •  SOURCE-LINKED REVIEW OVERVIEW':x=28:y=44:fontsize=18:fontcolor=0x86efac:enable='between(t,82,88)',\
drawbox=x=0:y=74:w='iw*t/$TOUR_DURATION':h=4:color=0x22d3eeff:t=4"
"${FFMPEG[@]}" -v error -i "$RAW_VIDEO" -vf "$OVERLAY_FILTER" \
    -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -movflags +faststart -y "$VIDEO"
PALETTE="$FRAME_DIR/palette.png"
"${FFMPEG[@]}" -v error -i "$VIDEO" -vf "fps=4,scale=800:450:flags=lanczos,palettegen=max_colors=224:stats_mode=diff" -frames:v 1 -y "$PALETTE"
"${FFMPEG[@]}" -v error -i "$VIDEO" -i "$PALETTE" -lavfi "fps=4,scale=800:450:flags=lanczos[x];[x][1:v]paletteuse=dither=sierra2_4a:diff_mode=rectangle" -loop 0 -y "$OUTPUT"
SIZE_BYTES="$(stat -c %s "$OUTPUT")"
if [ "$SIZE_BYTES" -ge 20000000 ]; then
    "${FFMPEG[@]}" -v error -i "$VIDEO" -vf "fps=3,scale=640:360:flags=lanczos,palettegen=max_colors=192:stats_mode=diff" -frames:v 1 -y "$PALETTE"
    "${FFMPEG[@]}" -v error -i "$VIDEO" -i "$PALETTE" -lavfi "fps=3,scale=640:360:flags=lanczos[x];[x][1:v]paletteuse=dither=sierra2_4a:diff_mode=rectangle" -loop 0 -y "$OUTPUT"
    SIZE_BYTES="$(stat -c %s "$OUTPUT")"
fi
test "$SIZE_BYTES" -lt 20000000
echo "wrote $BLEND"
echo "wrote $VIDEO"
echo "wrote $OUTPUT ($SIZE_BYTES bytes, $EXPECTED source frames, ${TOUR_DURATION}s guided tour)"
