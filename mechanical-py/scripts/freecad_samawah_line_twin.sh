#!/usr/bin/env bash
set -euo pipefail

MECH_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$MECH_ROOT/.." && pwd)"
CITY_DIR="$REPO_ROOT/designs/west-asia/Iraq/Samawah"
RUNNER="$MECH_ROOT/freecad_samawah_line_twin_runner.py"
MODEL="$CITY_DIR/engineering/digital-twin/samawah-line1-digital-twin.FCStd"
OUTPUT="$CITY_DIR/engineering/digital-twin/samawah-line1-digital-twin.gif"
FRAMES=230
WIDTH=1280
HEIGHT=720

while [ "$#" -gt 0 ]; do
    case "$1" in
        --city-dir) CITY_DIR="$2"; shift 2 ;;
        --model) MODEL="$2"; shift 2 ;;
        --out) OUTPUT="$2"; shift 2 ;;
        --frames) FRAMES="$2"; shift 2 ;;
        --width) WIDTH="$2"; shift 2 ;;
        --height) HEIGHT="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [--city-dir DIR] [--model FCSTD] [--out GIF] [--frames N] [--width PX] [--height PX]"
            exit 0
            ;;
        *) echo "unknown option: $1" >&2; exit 2 ;;
    esac
done

if ! command -v convert >/dev/null 2>&1; then
    echo "ImageMagick 'convert' is required to encode the Samawah GIF." >&2
    exit 127
fi

FRAME_DIR="$(mktemp -d /tmp/osr-samawah-line1-frames.XXXXXX)"
cleanup() {
    rm -rf "$FRAME_DIR"
}
trap cleanup EXIT

export OSR_SAMAWAH_TWIN_RUN=1
export OSR_SAMAWAH_CITY_DIR="$CITY_DIR"
export OSR_SAMAWAH_TWIN_MODEL="$MODEL"
export OSR_SAMAWAH_TWIN_FRAME_DIR="$FRAME_DIR"
export OSR_SAMAWAH_TWIN_FRAMES="$FRAMES"
export OSR_SAMAWAH_TWIN_WIDTH="$WIDTH"
export OSR_SAMAWAH_TWIN_HEIGHT="$HEIGHT"

run_freecad() {
    if command -v FreeCAD >/dev/null 2>&1; then
        xvfb-run -a FreeCAD "$RUNNER"
    elif command -v freecad >/dev/null 2>&1; then
        xvfb-run -a freecad "$RUNNER"
    elif command -v flatpak >/dev/null 2>&1 && flatpak info org.freecad.FreeCAD >/dev/null 2>&1; then
        xvfb-run -a flatpak run \
            --filesystem="$REPO_ROOT" \
            --filesystem="$FRAME_DIR" \
            --env=OSR_SAMAWAH_TWIN_RUN=1 \
            --env=OSR_SAMAWAH_CITY_DIR="$CITY_DIR" \
            --env=OSR_SAMAWAH_TWIN_MODEL="$MODEL" \
            --env=OSR_SAMAWAH_TWIN_FRAME_DIR="$FRAME_DIR" \
            --env=OSR_SAMAWAH_TWIN_FRAMES="$FRAMES" \
            --env=OSR_SAMAWAH_TWIN_WIDTH="$WIDTH" \
            --env=OSR_SAMAWAH_TWIN_HEIGHT="$HEIGHT" \
            --command=FreeCAD org.freecad.FreeCAD "$RUNNER"
    else
        echo "FreeCAD GUI was not found; install FreeCAD or org.freecad.FreeCAD." >&2
        exit 127
    fi
}

run_freecad

mapfile -t FRAME_FILES < <(find "$FRAME_DIR" -maxdepth 1 -type f -name 'frame-*.png' | sort)
if [ "${#FRAME_FILES[@]}" -ne "$FRAMES" ]; then
    echo "expected $FRAMES Samawah frames, found ${#FRAME_FILES[@]}" >&2
    exit 1
fi

ANNOTATED_DIR="$FRAME_DIR/annotated"
mkdir -p "$ANNOTATED_DIR"
STATE_FILE="$FRAME_DIR/frame-state.tsv"
if [ ! -s "$STATE_FILE" ]; then
    echo "FreeCAD did not emit the real-time motion-state table" >&2
    exit 1
fi

while IFS=$'\t' read -r frame_number elapsed_s phase speed_kmh acceleration_mps2 offset_m doors; do
    [ "$frame_number" = "frame" ] && continue
    name="$(printf 'frame-%03d.png' "$frame_number")"
    frame="$FRAME_DIR/$name"
    elapsed_whole="${elapsed_s%.*}"
    service_total_seconds=$((27000 + elapsed_whole))
    service_hour=$((service_total_seconds / 3600))
    service_clock_minute=$(((service_total_seconds % 3600) / 60))
    service_clock_second=$((service_total_seconds % 60))
    service_clock="$(printf '%02d:%02d:%02d' "$service_hour" "$service_clock_minute" "$service_clock_second")"
    convert "$frame" \
        -gravity North -background '#073b59' -splice 0x68 \
        -font DejaVu-Sans-Bold -pointsize 25 -fill white \
        -annotate +0+20 "SAMAWAH LINE 1 • S5 ELEVATED STATION • $service_clock • 1:1 TIME" \
        -gravity South -background '#073b59' -splice 0x108 \
        -font DejaVu-Sans-Bold -pointsize 20 -fill white \
        -annotate +0+68 "$phase  •  SPEED $speed_kmh KM/H  •  ACCELERATION $acceleration_mps2 M/S²  •  DOORS $doors" \
        -font DejaVu-Sans -pointsize 16 -fill '#bde9f7' \
        -annotate +0+35 "T+$elapsed_s S  •  TRAIN OFFSET $offset_m M  •  49.5 M LM3 3-CAR CONSIST  •  PHYSICALLY TIMED MOTION" \
        "$ANNOTATED_DIR/$name"
done < "$STATE_FILE"

mkdir -p "$(dirname "$OUTPUT")"
if command -v ffmpeg >/dev/null 2>&1; then
    FFMPEG=(ffmpeg)
elif command -v flatpak >/dev/null 2>&1 && flatpak info org.freecad.FreeCAD >/dev/null 2>&1; then
    FFMPEG=(flatpak run --filesystem="$REPO_ROOT" --filesystem="$FRAME_DIR" --command=ffmpeg org.freecad.FreeCAD)
else
    echo "FFmpeg is required to assemble the full-resolution Samawah animation." >&2
    exit 127
fi

PALETTE="$FRAME_DIR/samawah-palette.png"
"${FFMPEG[@]}" -v error -framerate "$FRAMES/46" \
    -i "$ANNOTATED_DIR/frame-%03d.png" \
    -vf 'palettegen=max_colors=256:stats_mode=diff' -frames:v 1 -y "$PALETTE"
"${FFMPEG[@]}" -v error -framerate "$FRAMES/46" \
    -i "$ANNOTATED_DIR/frame-%03d.png" -i "$PALETTE" \
    -lavfi 'paletteuse=dither=sierra2_4a:diff_mode=rectangle' -loop 0 -y "$OUTPUT"

MAX_BYTES=20000000
SIZE_BYTES="$(stat -c %s "$OUTPUT")"
if [ "$SIZE_BYTES" -ge "$MAX_BYTES" ]; then
    "${FFMPEG[@]}" -v error -framerate "$FRAMES/46" \
        -i "$ANNOTATED_DIR/frame-%03d.png" \
        -vf 'scale=iw*0.88:ih*0.88,palettegen=max_colors=192:stats_mode=diff' \
        -frames:v 1 -y "$PALETTE"
    "${FFMPEG[@]}" -v error -framerate "$FRAMES/46" \
        -i "$ANNOTATED_DIR/frame-%03d.png" -i "$PALETTE" \
        -lavfi '[0:v]scale=iw*0.88:ih*0.88[scaled];[scaled][1:v]paletteuse=dither=sierra2_4a:diff_mode=rectangle' \
        -loop 0 -y "$OUTPUT"
    SIZE_BYTES="$(stat -c %s "$OUTPUT")"
fi
if [ "$SIZE_BYTES" -ge "$MAX_BYTES" ]; then
    echo "Samawah GIF is $SIZE_BYTES bytes, at or above the 20 MB limit" >&2
    exit 1
fi

echo "wrote $MODEL"
echo "wrote ${MODEL%.FCStd}.json"
echo "wrote $OUTPUT ($SIZE_BYTES bytes, ${#FRAME_FILES[@]} frames)"
