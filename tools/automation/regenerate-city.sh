#!/usr/bin/env bash
# Regenerate every artefact for a single city, end-to-end.
#
# Usage:
#   tools/automation/regenerate-city.sh <slug>
#   tools/automation/regenerate-city.sh samawah
#
# The slug must appear in `lib/city-batches/world-sample.toml`. Every
# parameter (population, country, bbox, climate) is read from the
# canonical catalogue — no flags need to be passed by hand.
#
# Pipeline steps:
#   1. Pull OSM features for the bbox via `osr_osm` (cache-keyed on
#      query text — no network round-trip if unchanged since last run).
#   2. Rasterise OSM + WorldPop population layer onto the demand /
#      cost / buildability grid via `osr_geo`.
#   3. Synthesise the design via `osr-design` (rust): topology, station
#      placement, civil classification, fleet sizing, CAPEX.
#   4. Emit the simulator scenario via `osr_scenario`.
#   5. Render the network map PNG via `osr_scenario.render_map`.
#   6. Generate and run the city-local SUMO, QGIS and energy screening.
#   7. Generate finance, project-twin, procurement, cashflow and operations evidence.
#   8. Emit the per-network README via `osr_scenario.network_readme`.
#   9. Print summary stats and run the design-quality drift tests.
#  10. Fail closed through a hashed planning-package manifest.
#
# Adding a new city is a one-line change to
# `lib/city-batches/world-sample.toml`; this script handles the rest.

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
    echo "usage: $(basename "$0") <slug>" >&2
    echo "       (slug must exist in lib/city-batches/world-sample.toml)" >&2
    exit 2
fi

SLUG="$1"
if [[ ${2:-} == "--publish-reference" ]]; then
    echo "note: --publish-reference is now the default; writing to cities/catalogue/" >&2
elif [[ $# -eq 2 ]]; then
    echo "error: unknown option: $2" >&2
    exit 2
fi
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CATALOG="$REPO/lib/city-batches/world-sample.toml"
DESIGN_PY="$REPO/design/city-generation"
CACHE_ROOT="$REPO/.cache/osr-pipeline"
OSM_CACHE="$CACHE_ROOT/osm"
RASTER_CACHE="$CACHE_ROOT/rasters"
PYTHON="${PYTHON:-python3}"
CARGO_BIN="${CARGO:-cargo}"
if ! command -v "$CARGO_BIN" >/dev/null 2>&1; then
    echo "error: cargo not found; set CARGO=/path/to/cargo" >&2
    exit 1
fi

if [[ ! -f "$CATALOG" ]]; then
    echo "error: missing $CATALOG" >&2
    exit 1
fi

# Pull the city record from the catalogue. Stdlib-only TOML parser via
# python so we don't add a shell-side dependency.
read_field() {
    local field="$1"
    "$PYTHON" -c "
import sys, tomllib
catalog = tomllib.loads(open('$CATALOG').read())
for c in catalog.get('cities', []):
    if c.get('slug') == '$SLUG':
        v = c.get('$field')
        if v is None:
            sys.exit(f'error: city $SLUG has no field $field')
        if isinstance(v, dict):
            print(','.join(str(v[k]) for k in ('south', 'west', 'north', 'east')))
        else:
            print(v)
        sys.exit(0)
sys.exit(f'error: slug $SLUG not in $CATALOG')
"
}

COUNTRY="$(read_field country)"
BBOX="$(read_field bbox)"
CONTINENT="$(read_field continent)"

# Resolve full country name from `lib/templates/country-costs.toml`
# (e.g. IQ → Iraq, FR → France) so the design folder reads as
# `cities/catalogue/west-asia/Iraq/Samawah/` rather than `cities/catalogue/west-asia/IQ/Samawah/`.
# Falls back to the ISO-2 code if the country isn't in country-costs.
COUNTRY_NAME="$("$PYTHON" -c "
import sys, tomllib
costs = tomllib.loads(open('$REPO/lib/templates/country-costs.toml').read())
country = costs.get('countries', {}).get('$COUNTRY')
print(country.get('name', '$COUNTRY') if country else '$COUNTRY')
")"

# Resolve `<region>/<country>/<City>` design folder. Country code → region
# uses the catalogue's `continent` field.
case "$CONTINENT" in
    middle-east|west-asia)        REGION="west-asia" ;;
    north-africa)                 REGION="north-africa" ;;
    east-africa|west-africa|*-africa) REGION="${CONTINENT}" ;;
    south-asia|southeast-asia)    REGION="$CONTINENT" ;;
    europe)                       REGION="europe" ;;
    latin-america)                REGION="latin-america" ;;
    *)                            REGION="$CONTINENT" ;;
esac
CITY_TITLE="$(echo "$SLUG" | "$PYTHON" -c 'import sys; print(sys.stdin.read().strip().title())')"
DESIGN_DIR="$REPO/cities/catalogue/$REGION/$COUNTRY_NAME/$CITY_TITLE"

echo "=== regenerating $SLUG ($COUNTRY) → $DESIGN_DIR ==="

echo "0) CAD quantity cost contract"
"$PYTHON" "$REPO/tools/automation/generate-civil-cost-model.py"

cd "$DESIGN_PY"
export PYTHONPATH="$DESIGN_PY/src"

mkdir -p "$OSM_CACHE" "$RASTER_CACHE" "$DESIGN_DIR"

mkdir -p "$DESIGN_DIR/engineering/alignment" \
    "$DESIGN_DIR/engineering/simulation" \
    "$DESIGN_DIR/engineering/screenshots"

echo "1) OSM pull → $OSM_CACHE/$SLUG.json (cached on query text)"
# Use --bbox=... (no space) so a southern-hemisphere bbox (leading
# minus sign on south/north) doesn't get parsed as an argparse flag.
"$PYTHON" -m osr_osm.cli --slug "$SLUG" --bbox="$BBOX" \
    --out "$OSM_CACHE/$SLUG.json"

echo "2) raster bundle → $RASTER_CACHE/$SLUG.{cost,demand,buildability,grid,anchors}.*"
"$PYTHON" -m osr_geo.cli --slug "$SLUG" \
    --osm-json "$OSM_CACHE/$SLUG.json" \
    --out-dir "$RASTER_CACHE" \
    --country "$COUNTRY"

echo "3) design synthesis → $DESIGN_DIR/design.toml"
"$CARGO_BIN" run --release --bin osr-design --manifest-path "$REPO/Cargo.toml" -- \
    --slug "$SLUG" \
    --sidecar "$RASTER_CACHE/$SLUG.grid.json" \
    --out-dir "$DESIGN_DIR"

echo "4) scenario file → $DESIGN_DIR/$SLUG.toml"
"$PYTHON" -m osr_scenario --design "$DESIGN_DIR/design.toml" \
    --out "$DESIGN_DIR/$SLUG.toml"

echo "5) network map PNG → $DESIGN_DIR/$SLUG-network-map.png"
"$PYTHON" -m osr_scenario.render_map --design "$DESIGN_DIR/design.toml"

echo "6) SUMO + QGIS + energy engineering package → $DESIGN_DIR/engineering/"
"$REPO/tools/automation/engineering-toolchain.sh" --cities \
    --design "$DESIGN_DIR/design.toml" --jobs 1 --skip-shared-models

echo "6b) full-window OSR simulation validation → $DESIGN_DIR/engineering/simulation/"
"$PYTHON" "$REPO/tools/automation/validate-city-simulation.py" \
    --scenario "$DESIGN_DIR/$SLUG.toml" --resilience
"$PYTHON" "$REPO/tools/automation/render-sim-screenshots.py" \
    --scenario "$DESIGN_DIR/$SLUG.toml"

echo "7) operations + project digital twin → $DESIGN_DIR/operations/ and engineering/project-twin/"
"$PYTHON" "$REPO/tools/automation/generate-qa-maintenance-data.py" \
    --design "$DESIGN_DIR/design.toml" \
    --scenario "$DESIGN_DIR/$SLUG.toml" \
    --out-dir "$DESIGN_DIR/operations"
"$PYTHON" "$REPO/tools/automation/generate-acceptance-evidence-report.py" \
    --bundle "$DESIGN_DIR/operations/$SLUG-operations.json.gz"

echo "8) per-network README → $DESIGN_DIR/README.md"
"$PYTHON" -m osr_scenario.network_readme \
    --design "$DESIGN_DIR/design.toml" \
    --scenario "$DESIGN_DIR/$SLUG.toml" \
    --out "$DESIGN_DIR/README.md"

echo "9) summary stats:"
"$PYTHON" -m osr_scenario.stats --design "$DESIGN_DIR/design.toml"

echo "10) design-quality drift tests (mandatory)"
"$PYTHON" -m pytest tests/test_osr_scenario.py tests/test_population_drift.py -q

echo "11) complete package manifest"
"$PYTHON" "$REPO/tools/automation/generate-city-package-manifest.py" \
    --city-dir "$DESIGN_DIR"

echo
echo "Done. Output:"
echo "  $DESIGN_DIR/"
echo "  README.md, design.toml, $SLUG.toml, $SLUG-network-map.png,"
echo "  $SLUG.corridor.geojson, $SLUG.stations.json, $SLUG.design-quality.yaml"
echo "  operations/ (asset, CPM, orders, cashflow, QA, maintenance, and acceptance data)"
echo "  engineering/project-twin/summary.json (compact Git-reviewable delivery twin)"
echo "  engineering/ (alignment, SUMO, QGIS/GDAL, energy, simulation, screenshots, finance)"
echo "  package-manifest.json (hashed screening-package completeness gate)"
