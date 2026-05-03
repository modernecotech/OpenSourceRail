#!/usr/bin/env bash
# Regenerate every catalog city via scripts/regenerate-city.sh.
#
# Usage:
#   scripts/regenerate-all.sh
#   scripts/regenerate-all.sh --jobs 4         # run 4 cities in parallel
#   scripts/regenerate-all.sh --skip baghdad   # exclude one slug (repeatable)
#   scripts/regenerate-all.sh --only tunis,lyon  # subset (comma-separated)
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

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CATALOG="$REPO/lib/city-batches/world-sample.toml"
LOG_DIR="$REPO/.cache/osr-pipeline/logs"
JOBS=1
SKIP=()
ONLY=()
PYTHON="${PYTHON:-python3}"

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
echo "regenerating ${#SLUGS[@]} city/cities (jobs=$JOBS): ${SLUGS[*]}"
echo "logs → $LOG_DIR/regenerate-<slug>.log"
echo

run_one() {
    local slug="$1"
    local log="$LOG_DIR/regenerate-$slug.log"
    if bash "$REPO/scripts/regenerate-city.sh" "$slug" >"$log" 2>&1; then
        echo "OK   $slug"
        return 0
    else
        echo "FAIL $slug — see $log"
        return 1
    fi
}

# Parallelism via wait -n / xargs would mask which slug failed; do
# the bookkeeping by hand. Bash 4.3+ wait -n is widely available.
declare -A PIDS
declare -A SLUG_OF_PID
FAILED=()
RUNNING=0

reap_one() {
    local pid status slug
    if ! wait -n -p pid 2>/dev/null; then
        # Older bash: fall back to wait without -p (loses pid map).
        wait -n
        status=$?
        for p in "${!SLUG_OF_PID[@]}"; do
            if ! kill -0 "$p" 2>/dev/null; then
                slug="${SLUG_OF_PID[$p]}"
                unset 'SLUG_OF_PID[$p]'
                RUNNING=$((RUNNING - 1))
                if [[ $status -ne 0 ]]; then FAILED+=("$slug"); fi
                return
            fi
        done
        return
    fi
    status=$?
    slug="${SLUG_OF_PID[$pid]:-?}"
    unset 'SLUG_OF_PID[$pid]'
    RUNNING=$((RUNNING - 1))
    if [[ $status -ne 0 ]]; then FAILED+=("$slug"); fi
}

START_TS=$(date +%s)
for slug in "${SLUGS[@]}"; do
    while [[ $RUNNING -ge $JOBS ]]; do reap_one; done
    run_one "$slug" &
    pid=$!
    SLUG_OF_PID[$pid]="$slug"
    RUNNING=$((RUNNING + 1))
done
while [[ $RUNNING -gt 0 ]]; do reap_one; done
ELAPSED=$(( $(date +%s) - START_TS ))

echo
echo "elapsed: ${ELAPSED}s"
if [[ ${#FAILED[@]} -gt 0 ]]; then
    echo "${#FAILED[@]} of ${#SLUGS[@]} failed: ${FAILED[*]}"
    exit 1
fi
echo "all ${#SLUGS[@]} cities succeeded."
