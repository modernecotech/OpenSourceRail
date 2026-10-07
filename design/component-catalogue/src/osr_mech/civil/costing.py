"""Scope-reconciled costs: purchases, allocations and residuals stay separate."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import math
from osr_mech.provenance import stable_sum as sum


@dataclass(frozen=True)
class ComponentPurchase:
    product: str
    quantity: int
    delivered_unit_usd: float
    tooling_project_usd: float = 0
    tooling_in_unit_price: bool = False
    upgrades_usd: float = 0
    storage_dispatch_usd: float = 0
    new_factory_usd: float = 0

    def total(self) -> dict:
        if self.quantity < 0 or any(not math.isfinite(x) or x < 0 for x in (self.delivered_unit_usd,self.tooling_project_usd,self.upgrades_usd,self.storage_dispatch_usd,self.new_factory_usd)):
            raise ValueError("invalid make/buy cost")
        if self.tooling_in_unit_price and self.tooling_project_usd:
            raise ValueError("tooling amortisation counted in supplier price and project CAPEX")
        scope=dict(delivered_components_usd=self.quantity*self.delivered_unit_usd,
                   project_tooling_usd=self.tooling_project_usd,factory_upgrades_usd=self.upgrades_usd,
                   storage_dispatch_usd=self.storage_dispatch_usd,new_factory_usd=self.new_factory_usd)
        return {**scope,"cash_total_usd":sum(scope.values())}


def reconcile_installed_rate(installed_total_usd: float, embedded_erection_usd: float | None,
                             replacement_scope: dict[str,float]) -> dict:
    if any(not math.isfinite(v) or v < 0 for v in replacement_scope.values()):
        raise ValueError("cost scope must be finite and non-negative")
    if embedded_erection_usd is None:
        return dict(installed_reference_usd=installed_total_usd,replacement_scope=replacement_scope,
                    reconciled_total_usd=None,claimed_saving_usd=None,status="embedded-erection-scope-unverified")
    if not 0 <= embedded_erection_usd <= installed_total_usd:
        raise ValueError("invalid embedded erection credit")
    total=installed_total_usd-embedded_erection_usd+sum(replacement_scope.values())
    return dict(installed_reference_usd=installed_total_usd,removed_embedded_erection_usd=embedded_erection_usd,
                replacement_scope=replacement_scope,reconciled_total_usd=total,
                claimed_saving_usd=installed_total_usd-total,status="scope-matched-study")


def station_access_cost(layout, config: dict) -> dict:
    rates=config['installed_unit_cost_usd'];quantities=layout.quantities
    costs={kind:quantities[f'{kind}_count']*rates[kind] for kind in ('lift','escalator','staircase','shaft')}
    costs['associated_works']=rates['associated_works']*sum(level.startswith('concourse') for level in layout.level_elevations_mm)
    annual=config['annual_operation']
    total=sum(costs.values())
    energy=quantities['lift_count']*annual['energy_kwh_per_lift']+quantities['escalator_count']*annual['energy_kwh_per_escalator']
    return dict(installed_items_usd=costs,installed_total_usd=total,annual_energy_kwh=energy,
                annual_maintenance_usd=total*annual['maintenance_fraction'],replacement_year=annual['replacement_year'],
                replacement_cost_usd=total*annual['replacement_cost_fraction'],qualification='unquoted-study')


def island_net_saving(side_access_usd: float, island_access_usd: float, wider_deck_usd: float | None,
                      supports_usd: float | None, spreading_approaches_usd: float | None) -> float | None:
    if any(x is None for x in (wider_deck_usd,supports_usd,spreading_approaches_usd)):
        return None
    return side_access_usd-island_access_usd-wider_deck_usd-supports_usd-spreading_approaches_usd
