#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MECH_ROOT="$REPO_ROOT/design/component-catalogue"

PYTHONPATH="$MECH_ROOT/src${PYTHONPATH:+:$PYTHONPATH}" \
    python3 -m osr_mech.buildable_trainset "$@"
