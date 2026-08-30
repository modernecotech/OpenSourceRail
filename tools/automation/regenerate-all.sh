#!/usr/bin/env bash
# Resynthesise and refresh every complete catalog city package in cities/catalogue/.
#
# Usage:
#   tools/automation/regenerate-all.sh
#   tools/automation/regenerate-all.sh --jobs 4         # run 4 cities in parallel
#   tools/automation/regenerate-all.sh --skip baghdad   # exclude one slug (repeatable)
#   tools/automation/regenerate-all.sh --only tunis,lyon  # subset (comma-separated)
#   tools/automation/regenerate-all.sh --from-scratch   # refetch OSM and resynthesise designs
#   tools/automation/regenerate-all.sh --resynthesise-corridors  # reroute from cached rasters
#
# Reads slugs from lib/city-batches/world-sample.toml so new entries
# get picked up automatically. One city's failure does not abort the
# rest — failures are collected and printed at the end with the path
# to each per-city log.
#
# Exit codes:
#   0  every city succeeded
#   1  one or more cities failed (see summary)
#   2  argument / setup error

set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CATALOG="$REPO/lib/city-batches/world-sample.toml"
LOG_DIR="$REPO/.cache/osr-pipeline/logs"
JOBS=1
SKIP=()
ONLY=()
FROM_SCRATCH=false
RESYNTHESISE_CORRIDORS=false
if [[ -z "${PYTHON:-}" ]]; then
    if [[ -x "$REPO/.venv/bin/python" ]]; then
        PYTHON="$REPO/.venv/bin/python"
    else
        PYTHON="python3"
    fi
fi

usage() {
    sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's|^# \{0,1\}||'
    exit 2
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --jobs|-j)
            JOBS="${2:-}"
            [[ "$JOBS" =~ ^[1-9][0-9]*$ ]] || { echo "error: --jobs needs a positive integer" >&2; exit 2; }
            shift 2 ;;
        --skip)
            IFS=',' read -ra _xs <<<"${2:-}"
            SKIP+=("${_xs[@]}")
            shift 2 ;;
        --only)
            IFS=',' read -ra _xs <<<"${2:-}"
            ONLY+=("${_xs[@]}")
            shift 2 ;;
        --from-scratch)
            FROM_SCRATCH=true
            shift ;;
        --resynthesise-corridors)
            RESYNTHESISE_CORRIDORS=true
            shift ;;
        -h|--help) usage ;;
        *) echo "error: unknown arg '$1'" >&2; usage ;;
    esac
done

if [[ ! -f "$CATALOG" ]]; then
    echo "error: missing $CATALOG" >&2
    exit 2
fi

ALL_SLUGS=()
while IFS= read -r slug; do
    ALL_SLUGS+=("$slug")
done < <("$PYTHON" -c "
import tomllib
catalog = tomllib.loads(open('$CATALOG').read())
for c in catalog.get('cities', []):
    if 'slug' in c:
        print(c['slug'])
")

if [[ ${#ALL_SLUGS[@]} -eq 0 ]]; then
    echo "error: no cities found in $CATALOG" >&2
    exit 2
fi

# Filter against --only / --skip.
in_list() {
    local needle="$1"; shift
    local n
    for n in "$@"; do [[ "$n" == "$needle" ]] && return 0; done
    return 1
}

SLUGS=()
for slug in "${ALL_SLUGS[@]}"; do
    if [[ ${#ONLY[@]} -gt 0 ]] && ! in_list "$slug" "${ONLY[@]}"; then
        continue
    fi
    if in_list "$slug" "${SKIP[@]}"; then
        continue
    fi
    SLUGS+=("$slug")
done

if [[ ${#SLUGS[@]} -eq 0 ]]; then
    echo "error: filter left no slugs to run" >&2
    exit 2
fi

mkdir -p "$LOG_DIR"
export OSR_ENGINEERING_DATA_ROOT="${OSR_ENGINEERING_DATA_ROOT:-$REPO/.cache/osr-engineering}"
ONLY_CSV="$(IFS=,; echo "${SLUGS[*]}")"
COMMAND=(
    "$PYTHON" "$REPO/tools/automation/generate-city-packages-fast.py"
    --jobs "$JOBS" --only "$ONLY_CSV"
)
if [[ "$FROM_SCRATCH" == true ]]; then
    COMMAND+=(--from-scratch)
fi
if [[ "$RESYNTHESISE_CORRIDORS" == true ]]; then
    COMMAND+=(--resynthesise-corridors)
fi
exec "${COMMAND[@]}"
