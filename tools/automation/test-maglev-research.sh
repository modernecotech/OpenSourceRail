#!/usr/bin/env bash
# Separate source-bound follow-up studies; never a canonical adoption step.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
tools/automation/osr-python -m pytest -q engineering/maglev_research/tests
tools/automation/osr-python -m engineering.maglev_research.readme_context --check
tools/automation/osr-python -m engineering.maglev_research.research_closure check
