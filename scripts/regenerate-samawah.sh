#!/usr/bin/env bash
# Regenerate every downstream Samawah artefact from the authoritative
# designs/middle-east/iraq/samawah/design.toml.
#
# Run this whenever the design.toml changes. The simulator scenario,
# the README + RFC 0003 map PNGs, and the design-quality drift tests
# all read from the same source.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESIGN="$REPO/designs/middle-east/iraq/samawah/design.toml"
DESIGN_PY="$REPO/design-py"

if [[ ! -f "$DESIGN" ]]; then
    echo "error: missing $DESIGN" >&2
    exit 1
fi

cd "$DESIGN_PY"
export PYTHONPATH="$DESIGN_PY/src"

echo "1) scenario file → scenarios/samawah.toml"
python3 -m osr_scenario --design "$DESIGN"

echo "2) network map PNGs → docs/screenshots/samawah-network-map{,-detail}.png"
python3 -m osr_scenario.render_map --design "$DESIGN"

echo "3) stats summary:"
python3 -m osr_scenario.stats --design "$DESIGN"

echo "4) drift tests"
python3 -m pytest tests/test_osr_scenario.py tests/test_rfc_drift.py -q

echo
echo "Done. To verify end-to-end:"
echo "  cargo run --release --bin osr-sim -- --config scenarios/samawah.toml --duration 3600"
