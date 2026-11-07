"""Proposed part-level vehicle manufacture; selected references remain unchanged."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FLAGS=dict(engineering_accepted=False,physical_accepted=False,installed_mass_complete=False,
    manufacturing_release=False,operating_release=False,selected_reference_changed=False,
    movement_authority=False,procurement_approved=False)
