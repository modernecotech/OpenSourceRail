#!/usr/bin/env bash
set -euo pipefail
cd /home/hayder/.local/state/opensourcerail/worktrees/v06-design-closure-20261108
ulimit -t 120
ulimit -v 1048576
PYTHONPATH=/home/hayder/.local/state/opensourcerail/worktrees/v06-design-closure-20261108 PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -v timeout 120s .venv/bin/python /home/hayder/.local/state/opensourcerail/runs/v06-design-closure-20261108/samawah-china-supply-cost-04/run.py
