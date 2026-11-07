"""Counted research installation proposals, not installed-vehicle acceptance."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FLAGS=dict(installed_mass_complete=False,engineering_accepted=False,physical_accepted=False,
    manufacturing_release=False,operating_release=False,movement_authority=False,selected_reference_changed=False)
