"""Equipped-car inventory accounting; structural coupons never qualify a car."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FLAGS = dict(engineering_accepted=False, physical_accepted=False,
             configuration_adopted=False, complete_equipped_vehicle=False,
             installed_mass_complete=False, manufacturing_release=False)
