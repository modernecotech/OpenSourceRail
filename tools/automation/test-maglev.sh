#!/usr/bin/env bash
# Primary development checks; no hardware commands or legacy city synthesis.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
cargo fmt --package osr-maglev-control -- --check
cargo clippy --locked -p osr-maglev-control --all-targets -- -D warnings
cargo test --locked -p osr-maglev-control --all-targets
cargo check --locked -p osr-maglev-control --no-default-features
tools/automation/osr-python -m pytest -q engineering/analysis/tests/test_ferrite_maglev*.py
tools/automation/osr-python tools/automation/validate-host-manifests.py
tools/automation/osr-python tools/automation/capabilities.py --check
tools/automation/osr-python tools/automation/check-readmes.py
tools/automation/osr-python tools/automation/generate-public-overview.py --check
tools/automation/osr-python tools/automation/build-doc-book.py --check
tools/automation/osr-python tools/automation/ferrite-maglev-study.py check
node tools/automation/tests/verify-maglev-v05.mjs build/maglev-test-browser
node tools/automation/tests/verify-maglev-workbench.mjs build/maglev-test-workbench-browser
