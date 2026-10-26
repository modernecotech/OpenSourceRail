#!/usr/bin/env python3
"""Read-only Workbench for the explicitly selected development design."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from engineering.development_baseline.server import main
raise SystemExit(main())
