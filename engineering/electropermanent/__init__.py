"""Counted EPM next experiments; no switching or suspension qualification."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             configuration_adopted=False, installed_mass_complete=False,
             design_complete=False, manufacturing_release=False)
