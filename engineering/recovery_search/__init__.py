"""Bounded, same-service station recovery economics research."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FLAGS=dict(engineering_accepted=False,physical_accepted=False,manufacturing_release=False,
           operating_release=False,movement_authority=False,selected_reference_changed=False)
