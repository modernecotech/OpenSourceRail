#!/usr/bin/env bash
# Build the public OpenSourceRail system from the tracked source in one command.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
NODE_VERSION="22.23.2"
TOOL_ROOT="${HOME}/.local/share/opensource-rail/toolchains"
export PATH="$ROOT/.venv/bin:$TOOL_ROOT/bin:$TOOL_ROOT/node-v$NODE_VERSION/bin:${HOME}/.cargo/bin:$PATH"
cd "$ROOT"

(( $# == 0 )) || { printf 'Run ./osr build without options.\n' >&2; exit 2; }

section() {
    printf '\n==> %s\n' "$1"
}

section "Regenerating shared design, product, cost, and catalogue data"
python3 tools/automation/generate-civil-cost-model.py
tools/automation/design-iterate.sh
tools/automation/buildable-trainset.sh
tools/automation/buildable-stations.sh
python3 tools/automation/generate-cost-model.py
python3 tools/automation/generate-design-index.py
python3 tools/automation/generate-national-briefs.py
python3 tools/automation/generate-portfolio-summary.py
python3 tools/automation/generate-public-overview.py
python3 tools/automation/generate-doc-index.py

section "Building browser and native applications"
npm run frontend:build
cargo build --release --workspace

section "Generating BOM and open IFC4.3 reference packages"
python3 tools/automation/export-light-metro-bom.py
if python3 -c 'import ifcopenshell, ifctester, bcf' >/dev/null 2>&1; then
    python3 engineering/interchange/station_ifc.py --all-variants
    python3 engineering/interchange/trainset_manufacturing_ifc.py
    python3 engineering/interchange/lm3_product_ifc_library.py
    tools/automation/bonsai-civil.sh --generate \
        --out-dir engineering/models/bim/reference \
        --revision-id repository-reference
else
    printf 'IFC generation skipped: rerun ./install.sh and accept the engineering applications.\n'
fi
if command -v FreeCADCmd >/dev/null 2>&1 || command -v freecadcmd >/dev/null 2>&1 || \
   { command -v flatpak >/dev/null 2>&1 && flatpak info org.freecad.FreeCAD >/dev/null 2>&1; }; then
    tools/automation/freecad-generate.sh --assemblies
    python3 engineering/analysis/benchmarks/calculix/thermal_block.py
else
    printf 'FreeCAD review-model and CalculiX benchmark generation skipped: install the optional engineering applications.\n'
fi

section "Building the root documentation book"
python3 tools/automation/build-doc-book.py

section "Checking the generated repository"
python3 tools/automation/audit-project-twins.py
python3 tools/automation/check-readmes.py
python3 tools/automation/check-markdown-links.py
python3 tools/automation/repo-health.py --quiet

printf '\nOpenSourceRail build complete.\n'
printf '  Workbench: ./osr\n'
printf '  Book:      OpenSourceRail-Book.pdf\n'
printf '  BIM:       engineering/models/bim/reference/\n'
printf '  Job data:  build/\n'
