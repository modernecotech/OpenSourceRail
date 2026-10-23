#!/usr/bin/env bash
# Current maglev development checks; all physical release gates remain open.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
cargo fmt --all -- --check
cargo clippy --locked --workspace --all-targets -- -D warnings
cargo test --locked --workspace --all-targets
cargo check --locked -p osr-maglev-control --no-default-features
observer_manifest=engineering/ferrite_maglev/observer-prototype/Cargo.toml
cargo fmt --manifest-path "$observer_manifest" -- --check
cargo clippy --locked --manifest-path "$observer_manifest" --all-targets -- -D warnings
cargo test --locked --manifest-path "$observer_manifest" --all-targets
tools/automation/osr-python engineering/ferrite_maglev/observer-prototype/tests/differential.py
tools/automation/osr-python -m pytest -q engineering/analysis/tests/test_ferrite_maglev*.py
tools/automation/osr-python -m engineering.ferrite_maglev.pilot_assurance verify --require-executed
tools/automation/osr-python tools/automation/validate-host-manifests.py
tools/automation/osr-python tools/automation/capabilities.py --check
tools/automation/osr-python tools/automation/catalogue.py index --check
tools/automation/osr-python tools/automation/generate-design-index.py --check
tools/automation/osr-python tools/automation/generate-doc-index.py --check
tools/automation/osr-python tools/automation/check-readmes.py
tools/automation/osr-python tools/automation/generate-public-overview.py --check
tools/automation/osr-python tools/automation/build-doc-book.py --check
tools/automation/osr-python tools/automation/ferrite-maglev-study.py check
node tools/automation/tests/verify-maglev-v05.mjs build/maglev-test-browser
node tools/automation/tests/verify-maglev-workbench.mjs build/maglev-test-workbench-browser
