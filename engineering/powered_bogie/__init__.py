"""Counted powered-bogie research changes; the passive reference is unchanged."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, supplier_fit_verified=False)

