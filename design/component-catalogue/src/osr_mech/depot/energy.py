"""Quantified depot equipment requirements, shared by layout, BOM and audit.

The operating tier is authoritative. Earlier physical allowances are retained
only to expose additional scope; no site placement or installed price is implied.
"""

from __future__ import annotations

import math
import tomllib
from pathlib import Path
from typing import Any


TEMPLATES = Path(__file__).resolve().parents[5] / "lib/templates"


def depot_energy_scope(
    archetype: str, *, templates_root: Path = TEMPLATES,
    site: dict[str, Any] | None = None,
) -> dict[str, Any]:
    depots = tomllib.loads((templates_root / "depots.toml").read_text())
    tiers = tomllib.loads((templates_root / "energy-sites.toml").read_text())["tiers"]
    physical = depots["archetypes"][archetype]
    tier = physical["energy_site_tier"]
    equipment = dict(tiers[tier])
    if site is not None:
        if site.get("tier") != tier:
            raise ValueError(f"{archetype}: expected energy tier {tier}, got {site.get('tier')}")
        equipment.update(site)
    pv = float(equipment["pv_nameplate_kw"])
    storage = float(equipment["storage_capacity_kwh"])
    module = float(equipment["storage_module_kwh"])
    density = float(depots["energy_scope"]["pv_nameplate_kw_per_m2"])
    if not all(math.isfinite(v) and v >= 0 for v in (pv, storage)) or module <= 0 or density <= 0:
        raise ValueError("depot PV/storage quantities must be finite and nonnegative; module and density positive")
    if not math.isfinite(module) or not math.isfinite(density):
        raise ValueError("depot module size and PV density must be finite")
    modules = storage / module
    if not math.isclose(modules, round(modules), abs_tol=1e-8, rel_tol=0):
        raise ValueError(f"{storage} kWh cannot be supplied by whole {module} kWh modules")
    area = pv / density
    return {
        "energy_site_tier": tier,
        "pv_nameplate_kw": pv,
        "storage_capacity_kwh": storage,
        "storage_module_kwh": module,
        "storage_module_count": round(modules),
        "reference_pv_canopy_m2": float(physical["pv_canopy_m2"]),
        "required_pv_module_area_m2": area,
        "additional_pv_module_area_m2": max(0.0, area - float(physical["pv_canopy_m2"])),
        "additional_pv_kw": max(0.0, pv - float(physical["baseline_pv_nominal_kwp"])),
        "additional_storage_kwh": max(0.0, storage - float(physical["baseline_battery_kwh"])),
        "storage_compound_area_m2": None,
        "placement_status": depots["energy_scope"]["placement_status"],
        "deployment_release_ready": False,
    }
