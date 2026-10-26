"""Typed architecture registry: active wheel LIM and retained/comparison families."""
from enum import StrEnum
from . import ROOT
from .history import blob,REVISION
import gzip,json,tomllib
class Family(StrEnum):
    PM_MAGLEV='pm_maglev_station_powered'
    WHEEL_LIM='wheel_rail_station_lim'
    WHEEL_LSM='wheel_rail_station_lsm'
def describe(family,root=ROOT):
    family=Family(family)
    if family==Family.PM_MAGLEV:
        # The retained payload and its pinned receipt are already portable in
        # the tree. Ordinary comparison must also work in a shallow checkout;
        # full Git-object audit remains a separate historical command.
        from .vehicle import _read_parent
        car,_=_read_parent(root)
        return dict(family=family.value,state='retained_development_evidence',source_revision=REVISION,
            candidate_id=car['candidate_id'],vehicle=car,physical_accepted=False,active=False)
    if family==Family.WHEEL_LIM:
        from .vehicle import build
        return dict(family=family.value,state='development_candidate',vehicle=build(root),physical_accepted=False,active=True)
    return dict(family=family.value,state='concept_comparison',active=False,physical_accepted=False,
        candidate_id=None,installed_mass_kg=None,reason='Onboard propulsion PMs, containment, force maps and installed cost have not been designed; cannot compile a physical twin.')
