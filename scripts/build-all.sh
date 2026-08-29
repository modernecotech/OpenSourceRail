#!/usr/bin/env bash
# Build the public OpenSourceRail system from the tracked source in one command.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NODE_VERSION="22.23.2"
TOOL_ROOT="${HOME}/.local/share/opensource-rail/toolchains"
export PATH="$ROOT/.venv/bin:$TOOL_ROOT/bin:$TOOL_ROOT/node-v$NODE_VERSION/bin:${HOME}/.cargo/bin:$PATH"
cd "$ROOT"

(( $# == 0 )) || { printf 'Run ./scripts/osr build without options.\n' >&2; exit 2; }

section() {
    printf '\n==> %s\n' "$1"
}

section "Regenerating shared design, product, cost, and catalogue data"
python3 scripts/generate-civil-cost-model.py
scripts/design-iterate.sh
scripts/buildable-trainset.sh
scripts/buildable-stations.sh
python3 scripts/generate-cost-model.py
python3 scripts/generate-design-index.py
python3 scripts/generate-national-briefs.py
python3 scripts/generate-portfolio-summary.py
python3 scripts/generate-public-overview.py
python3 scripts/generate-doc-index.py

section "Building browser and native applications"
npm run frontend:build
cargo build --release --workspace

section "Generating BOM and open IFC4.3 reference packages"
python3 scripts/export-light-metro-bom.py
if python3 -c 'import ifcopenshell, ifctester, bcf' >/dev/null 2>&1; then
    python3 engineering/interchange/station_ifc.py --all-variants
    scripts/bonsai-civil.sh --generate
else
    printf 'IFC generation skipped: rerun ./install.sh and accept the engineering applications.\n'
fi

section "Building the root documentation book"
python3 scripts/build-doc-book.py

section "Checking the generated repository"
python3 scripts/check-readmes.py
python3 scripts/check-markdown-links.py
python3 scripts/repo-health.py --quiet

printf '\nOpenSourceRail build complete.\n'
printf '  Workbench: ./scripts/osr\n'
printf '  Book:      OpenSourceRail-Book.pdf\n'
printf '  Outputs:   build/\n'
