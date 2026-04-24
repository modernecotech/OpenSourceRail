#!/usr/bin/env bash
# Regenerate every downstream Samawah artefact from the authoritative
# designs/west-asia/Iraq/Samawah/design.toml.
#
# Run this whenever the design.toml changes. The simulator scenario,
# the README + RFC 0003 map PNGs, and the design-quality drift tests
# all read from the same source.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESIGN="$REPO/designs/west-asia/Iraq/Samawah/design.toml"
DESIGN_PY="$REPO/design-py"

if [[ ! -f "$DESIGN" ]]; then
    echo "error: missing $DESIGN" >&2
    exit 1
fi

cd "$DESIGN_PY"
export PYTHONPATH="$DESIGN_PY/src"

echo "1) scenario file → designs/west-asia/Iraq/Samawah/samawah.toml"
python3 -m osr_scenario --design "$DESIGN"

echo "2) network map PNGs → designs/west-asia/Iraq/Samawah/samawah-network-map{,-detail}.png"
python3 -m osr_scenario.render_map --design "$DESIGN"

echo "3) per-network README → designs/west-asia/Iraq/Samawah/README.md"
python3 -m osr_scenario.network_readme \
    --design "$DESIGN" \
    --scenario "$REPO/designs/west-asia/Iraq/Samawah/samawah.toml" \
    --out "$REPO/designs/west-asia/Iraq/Samawah/README.md" \
    --population 220000

echo "4) stats summary:"
python3 -m osr_scenario.stats --design "$DESIGN"

echo "5) drift tests"
python3 -m pytest tests/test_osr_scenario.py tests/test_rfc_drift.py -q

echo
echo "Done. To verify end-to-end:"
echo "  cargo run --release --bin osr-sim -- --config designs/west-asia/Iraq/Samawah/samawah.toml --duration 3600"
