"""Candidate-specific engineering readiness, separate from physical acceptance."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FLAGS=dict(configuration_adopted=False,engineering_accepted=False,physical_accepted=False,
           physical_release=False,manufacturing_release=False,design_complete=False)
