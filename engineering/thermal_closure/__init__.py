"""Source-bound hot-weather and support-winding research, not acceptance."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FLAGS = dict(configuration_adopted=False, engineering_accepted=False,
             physical_accepted=False, comfort_qualified=False,
             installed_mass_complete=False, complete_services_power_known=False)
