"""Continuing numerical/physical design with explicit external acceptance gates."""
from engineering.station_rail import ROOT
from engineering.station_rail.common import identity, encoded, digest
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
           operating_release=False,selected_reference_changed=False)
