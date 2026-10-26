"""Authoritative development default, separate from physical qualification."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
INPUT='engineering/development-baseline.toml'
OUTPUT='docs/design-engine/current'
WORKBENCH='docs/workbench/current'
FLAGS=dict(engineering_accepted=False,physical_accepted=False,installed_mass_complete=False,
           manufacturing_release=False,operating_release=False)
