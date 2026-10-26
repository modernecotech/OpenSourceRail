#!/usr/bin/env python3
"""Portable default-design launcher, also suitable for a user timer's ExecStart."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from engineering.development_baseline.entrypoint import main
raise SystemExit(main())
