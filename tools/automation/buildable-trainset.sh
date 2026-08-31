#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MECH_ROOT="$REPO_ROOT/design/component-catalogue"

PYTHONPATH="$MECH_ROOT/src${PYTHONPATH:+:$PYTHONPATH}" \
    python3 -m osr_mech.buildable_trainset "$@"

PYTHONPATH="$MECH_ROOT/src${PYTHONPATH:+:$PYTHONPATH}" \
    python3 -m osr_mech.trainset_supplier_anchors "$@"

PYTHONPATH="$MECH_ROOT/src${PYTHONPATH:+:$PYTHONPATH}" \
    python3 -m osr_mech.trainset_manufacturing_methods "$@"

python3 "$REPO_ROOT/tools/automation/generate-lm3-first-article-work.py"
