"""Shared supplier, delivery-route and construction-front contracts.

Unknown contracted capacity grants zero supply. Historical industrial capability
never constitutes a current prestressing qualification or available order slot.
"""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Evidence:
    units: str
    source: str
    date: str
    confidence: str
    qualification: str
    kind: str  # user-selected-scenario / engineering-calculation / supplier-quotation

    def __post_init__(self):
        if not all((self.units,self.source,self.date,self.confidence,self.qualification)):
            raise ValueError("assumptions require units, source, date, confidence and qualification")
        if self.kind not in ("user-selected-scenario","engineering-calculation","supplier-quotation","documented-capability"):
            raise ValueError("unsupported evidence kind")


@dataclass(frozen=True)
class SupplierCapacity:
    id: str
    location: str
    delivery_catchment: tuple[str,...]
    relevant_products: tuple[str,...]
    prestressing_qualified: bool
    beds: int | None
    moulds: int | None
    handling_limit_t: float | None
    maximum_length_m: float | None
    maximum_width_m: float | None
    demonstrated_cycle_days: float | None
    total_plant_units_day: float | None
    contracted_units_day: dict[str,float]
    storage_units: int | None
    dispatch_units_day: int | None
    existing_commitments: str
    qualification: str
    required_upgrades: tuple[str,...]
    delivered_prices_usd: dict[str,float]
    commercial_terms: str
    evidence: Evidence

    def allocate(self, product: str, units_day: float, *, allow_study_assumptions: bool = False) -> float:
        if not math.isfinite(units_day) or units_day < 0:
            raise ValueError("allocation must be finite and non-negative")
        qualified = self.qualification == "qualified"
        study = allow_study_assumptions and self.qualification == "study-assumed"
        if product not in self.relevant_products or not (qualified or study):
            raise ValueError("supplier/product not qualified")
        if product.startswith("pi-beam") and not self.prestressing_qualified:
            raise ValueError("prestressing qualification required")
        contracted = self.contracted_units_day.get(product,0)
        if not math.isfinite(contracted) or contracted < 0:
            raise ValueError("contracted capacity must be finite and non-negative")
        if units_day > contracted:
            raise ValueError("allocation exceeds contracted capacity")
        return units_day


def validate_supplier_allocations(suppliers: list[SupplierCapacity], allocations: list[dict]) -> None:
    register = {s.id:s for s in suppliers}
    totals: dict[tuple[str,str],float] = {}
    for row in allocations:
        key = (row["supplier"],row["product"])
        totals[key] = totals.get(key,0)+row["units_day"]
    for (supplier,product),units in totals.items():
        register[supplier].allocate(product,units)


@dataclass(frozen=True)
class DeliveryRoute:
    id: str
    supplier: str
    front: str
    journey_hours: float
    trailers: int
    payload_t: float
    trips_per_trailer_day: int
    delivery_window_hours: float
    loading_hours: float
    unloading_hours: float
    maximum_length_m: float
    bridge_limit_t: float
    buffer_beams: int
    access_released: bool = False
    turning_space_released: bool = False
    loading_equipment_released: bool = False
    unloading_equipment_released: bool = False
    rejection_fraction: float = 0.0
    alternatives: tuple[str,...] = ()
    delivery_order: str = "front-bay-track"
    vehicle_tare_t: float | None = None
    maximum_width_m: float | None = None
    unavailable_days: tuple[int, ...] = ()
    fleet_id: str | None = None
    fleet_daily_trips: int | None = None
    evidence: Evidence | None = None

    def trip_capacity(self, component_t: float, length_m: float, width_m: float | None = None) -> int:
        """Gross single-component trips; rejection is accounted chronologically."""
        values = (self.journey_hours,self.payload_t,self.delivery_window_hours,self.loading_hours,self.unloading_hours,component_t,length_m,self.bridge_limit_t,self.maximum_length_m)
        if any(not math.isfinite(v) or v <= 0 for v in values) or not 0 <= self.rejection_fraction < 1:
            raise ValueError("invalid logistics inputs")
        if any(type(value) is not int or value < 0 for value in (self.trailers,self.trips_per_trailer_day,self.buffer_beams)):
            raise ValueError("trailers, trips and storage must be whole non-negative counts")
        if not all(value is True for value in (self.access_released,self.turning_space_released,self.loading_equipment_released,self.unloading_equipment_released)):
            return 0
        if self.vehicle_tare_t is None:
            return 0
        if not math.isfinite(self.vehicle_tare_t) or self.vehicle_tare_t < 0:
            raise ValueError("vehicle/trailer tare must be finite and non-negative")
        if component_t > self.payload_t or component_t+self.vehicle_tare_t > self.bridge_limit_t or length_m > self.maximum_length_m:
            return 0
        if width_m is not None:
            if not math.isfinite(width_m) or width_m <= 0:
                raise ValueError("component width must be finite and positive")
            if self.maximum_width_m is None:
                return 0
            if not math.isfinite(self.maximum_width_m) or self.maximum_width_m <= 0:
                raise ValueError("route width limit must be finite and positive")
            if width_m > self.maximum_width_m:
                return 0
        cycle = 2*self.journey_hours+self.loading_hours+self.unloading_hours
        trips = min(self.trips_per_trailer_day,math.floor(self.delivery_window_hours/cycle))
        return self.trailers*trips

    def capacity(self, component_t: float, length_m: float, width_m: float | None = None) -> int:
        """Average accepted planning capacity; use trip_capacity for simulation."""
        return math.floor(self.trip_capacity(component_t,length_m,width_m)*(1-self.rejection_fraction))


@dataclass(frozen=True)
class ErectionFront:
    id: str
    line: str
    start_chainage_m: float
    end_chainage_m: float
    direction: int
    launcher: str
    delivery_access: str
    sequential_path: str
    available_foundations: int
    planned_start_day: int = 1
    interruptions_days: tuple[int,...] = ()
    relocation_days: int = 0
    permitted_hours_day: float = 24.0
    planned_finish_day: int | None = None
    relocation_date: str | None = None
    work_intervals_m: tuple[tuple[float,float],...] = ()

    def __post_init__(self):
        if self.end_chainage_m <= self.start_chainage_m or self.direction not in (-1,1):
            raise ValueError("front chainage/direction invalid")
        if any(a<self.start_chainage_m or b>self.end_chainage_m or b<=a for a,b in self.work_intervals_m):
            raise ValueError("work intervals must lie inside front chainages")
        ordered=sorted(self.work_intervals_m)
        if any(a[1]>b[0] for a,b in zip(ordered,ordered[1:])):
            raise ValueError("front work intervals overlap")
        if self.available_foundations < 0 or self.planned_start_day < 1 or self.relocation_days < 0:
            raise ValueError("front readiness/date invalid")
