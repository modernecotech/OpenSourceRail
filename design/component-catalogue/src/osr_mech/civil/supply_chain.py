"""Chronological contracted production, acceptance, dispatch and beam deliveries.

Daily completion rates already include the supplier's demonstrated casting/cure
cycle. Acceptance holds and road journeys add separate delays. Study capacity
pools require an explicit opt-in and never become qualified suppliers.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
import math

from .supply import DeliveryRoute, SupplierCapacity


@dataclass(frozen=True)
class ComponentDemand:
    product: str
    manufactured_mass_t: float
    length_m: float
    width_m: float

    def __post_init__(self):
        if not self.product or any(not math.isfinite(v) or v <= 0 for v in
                                   (self.manufactured_mass_t, self.length_m, self.width_m)):
            raise ValueError("component identity and transport dimensions must be supplied")


class ConstructionSupplyChain:
    """Mutable execution state for one finite component order.

    Factory storage includes completed components awaiting acceptance and
    accepted components awaiting dispatch. In-transit components reserve front
    storage and are credited only upon arrival. Failed components are counted
    separately and replaced within the same installed order quantity.
    """

    def __init__(self, suppliers: list[SupplierCapacity], allocations: list[dict],
                 routes: list[DeliveryRoute], component: ComponentDemand, order_units: int,
                 *, allow_study_assumptions: bool = False):
        if type(order_units) is not int or order_units < 0:
            raise ValueError("order quantity must be a whole non-negative count")
        if len({s.id for s in suppliers}) != len(suppliers):
            raise ValueError("supplier identities must be unique")
        if len({r.id for r in routes}) != len(routes):
            raise ValueError("delivery route identities must be unique")
        self.suppliers = {s.id: s for s in suppliers}
        self.component = component
        self.order_units = order_units
        self.study = allow_study_assumptions
        self.routes = routes
        self.allocations = []
        totals = defaultdict(float)
        for row in allocations:
            if row['supplier'] not in self.suppliers or row['product'] != component.product:
                raise ValueError("allocation must identify a registered supplier and this component")
            rate = row['units_day']
            if not math.isfinite(rate) or rate < 0:
                raise ValueError("contracted completion rate must be finite and non-negative")
            totals[row['supplier']] += rate
            hold = row.get('acceptance_delay_days', 0)
            start = row.get('production_start_day', 1)
            rejection = row.get('manufacturing_rejection_fraction', 0.0)
            if type(hold) is not int or hold < 0 or type(start) is not int or start < 1:
                raise ValueError("acceptance holds and production dates must be whole model days")
            if not math.isfinite(rejection) or not 0 <= rejection < 1:
                raise ValueError("invalid manufacturing rejection fraction")
            self.allocations.append({**row, 'acceptance_delay_days': hold,
                                     'production_start_day': start,
                                     'manufacturing_rejection_fraction': rejection,
                                     'credit': 0.0, 'rejection_credit': 0.0})
        for sid, rate in totals.items():
            self.suppliers[sid].allocate(component.product, rate,
                                         allow_study_assumptions=allow_study_assumptions)
            total = self.suppliers[sid].total_plant_units_day
            if total is not None and rate > total:
                raise ValueError("allocation exceeds demonstrated total plant output")
        for route in routes:
            if route.supplier not in self.suppliers:
                raise ValueError("delivery route identifies an unknown supplier")
            if route.evidence and route.evidence.qualification.startswith('study') and not self.study:
                raise ValueError("study delivery routes require explicit study opt-in")
            if route.fleet_id and (type(route.fleet_daily_trips) is not int or route.fleet_daily_trips < 0):
                raise ValueError("shared transport fleet requires its available daily trips")
        fleet_caps = defaultdict(set)
        for route in routes:
            if route.fleet_id:
                fleet_caps[route.fleet_id].add(route.fleet_daily_trips)
        if any(len(values) != 1 for values in fleet_caps.values()):
            raise ValueError("shared transport fleet capacities disagree")
        self.raw = dict.fromkeys(self.suppliers, 0)
        self.accepted = dict.fromkeys(self.suppliers, 0)
        self.peak_storage = dict.fromkeys(self.suppliers, 0)
        self.acceptance_due = defaultdict(list)
        self.shipments = []
        self.transport_rejection_credit = dict.fromkeys((r.id for r in routes), 0.0)
        self.last_day = 0
        self.counts = dict(cast=0, accepted=0, dispatched=0, delivered=0,
                           manufacturing_rejected=0, transport_rejected=0)

    def _factory_ready(self, supplier: SupplierCapacity) -> bool:
        counts = (supplier.storage_units, supplier.dispatch_units_day)
        if any(type(v) is not int or v <= 0 for v in counts):
            return False
        c = self.component
        limits = ((supplier.handling_limit_t, c.manufactured_mass_t),
                  (supplier.maximum_length_m, c.length_m),
                  (supplier.maximum_width_m, c.width_m))
        return all(limit is not None and math.isfinite(limit) and limit >= need
                   for limit, need in limits)

    @property
    def accepted_stock(self) -> int:
        return sum(self.accepted.values())

    @property
    def in_transit(self) -> int:
        return sum(s['quantity'] for s in self.shipments)

    def _front_limit(self, front: str, shortfall: int) -> str:
        if sum(s['quantity'] for s in self.shipments if s['front'] == front) >= shortfall:
            return 'transport'
        sources = {r.supplier for r in self.routes if r.front == front}
        ready = sum(self.accepted[sid] for sid in sources)
        if ready >= shortfall:
            return 'transport'
        if ready + sum(self.raw[sid] for sid in sources) >= shortfall:
            return 'acceptance'
        return 'casting'

    def step(self, day: int, *, front_inventory: dict[str, int],
             front_buffer_capacity: dict[str, int], remaining_beams: dict[str, int],
             delivery_access: dict[str, str], closed_fronts: set[str] | None = None,
             factory_open: bool = True) -> dict:
        if day != self.last_day + 1:
            raise ValueError("supply chain must advance one chronological model day at a time")
        self.last_day = day
        closed_fronts = closed_fronts or set()
        known = set(front_inventory)
        if set(front_buffer_capacity) != known or set(remaining_beams) != known or set(delivery_access) != known:
            raise ValueError("front inventory, storage, remaining order and access must agree")
        if any(type(value) is not int or value < 0 for mapping in
               (front_inventory, front_buffer_capacity, remaining_beams) for value in mapping.values()):
            raise ValueError("front inventories and storage must be whole non-negative counts")
        if any(front_inventory[fid] > front_buffer_capacity[fid] for fid in known):
            raise ValueError("front inventory exceeds storage capacity")
        if any(r.front not in known for r in self.routes):
            raise ValueError("delivery route identifies an unknown front")
        inventory = dict(front_inventory)
        delivered = dict.fromkeys(known, 0)
        pending = []
        for shipment in self.shipments:
            fid = shipment['front']
            room = front_buffer_capacity[fid] - inventory[fid]
            if shipment['arrival_day'] <= day and fid not in closed_fronts and room >= shipment['quantity']:
                delivered[fid] += shipment['quantity']
                inventory[fid] += shipment['quantity']
                self.counts['delivered'] += shipment['quantity']
            else:
                pending.append(shipment)
        self.shipments = pending
        useful_accepted = self.counts['accepted'] - self.counts['transport_rejected']
        open_order = max(0, self.order_units - useful_accepted - sum(self.raw.values()))
        for i, row in enumerate(self.allocations):
            supplier = self.suppliers[row['supplier']]
            if not factory_open or day < row['production_start_day'] or not self._factory_ready(supplier):
                continue
            used = self.raw[supplier.id] + self.accepted[supplier.id]
            room = supplier.storage_units - used
            if room <= 0 or open_order <= 0:
                continue
            row['credit'] += row['units_day']
            completed = min(math.floor(row['credit'] + 1e-9), room, open_order)
            # Retain fractional progress, never unused whole production days.
            row['credit'] = max(0, row['credit'] - completed) % 1
            if completed:
                self.raw[supplier.id] += completed
                self.counts['cast'] += completed
                open_order -= completed
                self.acceptance_due[day + row['acceptance_delay_days']].append((i, completed))
            self.peak_storage[supplier.id] = max(self.peak_storage[supplier.id], used + completed)
        accepted_today = 0
        for i, quantity in self.acceptance_due.pop(day, []):
            if not factory_open:
                self.acceptance_due[day+1].append((i,quantity))
                continue
            row = self.allocations[i]
            sid = row['supplier']
            row['rejection_credit'] += quantity * row['manufacturing_rejection_fraction']
            rejected = min(quantity, math.floor(row['rejection_credit'] + 1e-9))
            row['rejection_credit'] -= rejected
            accepted = quantity - rejected
            self.raw[sid] -= quantity
            self.accepted[sid] += accepted
            self.counts['accepted'] += accepted
            self.counts['manufacturing_rejected'] += rejected
            accepted_today += accepted
        reserved = defaultdict(int)
        for shipment in self.shipments:
            reserved[shipment['front']] += shipment['quantity']
        dispatched_supplier = defaultdict(int)
        dispatched_fleet = defaultdict(int)
        used_access = set()
        # Rotate front priority, but retain configured primary/alternative route order.
        ordered_fronts = sorted(known)
        if ordered_fronts:
            offset = (day - 1) % len(ordered_fronts)
            ordered_fronts = ordered_fronts[offset:] + ordered_fronts[:offset]
        for fid in ordered_fronts:
            if fid in closed_fronts or delivery_access[fid] in used_access:
                continue
            for route in (r for r in self.routes if r.front == fid):
                if day in route.unavailable_days:
                    continue
                supplier = self.suppliers[route.supplier]
                if not self._factory_ready(supplier):
                    continue
                gross = route.trip_capacity(self.component.manufactured_mass_t,
                                            self.component.length_m, self.component.width_m)
                if route.fleet_id:
                    gross = min(gross, route.fleet_daily_trips - dispatched_fleet[route.fleet_id])
                room = min(front_buffer_capacity[fid], route.buffer_beams) - inventory[fid] - reserved[fid]
                need = remaining_beams[fid] - delivered[fid] - reserved[fid]
                quantity = min(gross, self.accepted[route.supplier], room, need,
                               supplier.dispatch_units_day - dispatched_supplier[route.supplier])
                if quantity <= 0:
                    continue
                self.accepted[route.supplier] -= quantity
                dispatched_supplier[route.supplier] += quantity
                if route.fleet_id:
                    dispatched_fleet[route.fleet_id] += quantity
                self.counts['dispatched'] += quantity
                credit = self.transport_rejection_credit[route.id] + quantity * route.rejection_fraction
                rejected = min(quantity, math.floor(credit + 1e-9))
                self.transport_rejection_credit[route.id] = credit - rejected
                self.counts['transport_rejected'] += rejected
                successful = quantity - rejected
                if successful:
                    lead = max(1, math.ceil((route.journey_hours + route.unloading_hours) / 24))
                    self.shipments.append(dict(route=route.id, supplier=route.supplier, front=fid,
                                               quantity=successful, arrival_day=day + lead))
                    reserved[fid] += successful
                used_access.add(delivery_access[fid])
                # One active delivery route per front/access per day. Alternatives
                # are used when the preferred route has no qualified capacity.
                break
        return dict(day=day, accepted_today=accepted_today, delivered=delivered,
                    accepted_factory_stock=self.accepted_stock, in_transit_beams=self.in_transit,
                    front_limiting_resource={fid: self._front_limit(fid, max(1, 2-inventory[fid])) for fid in known},
                    factories={sid: dict(awaiting_acceptance=self.raw[sid], accepted_stock=self.accepted[sid],
                                        storage_limit=s.storage_units, dispatched_today=dispatched_supplier[sid])
                               for sid, s in self.suppliers.items()},
                    cumulative=dict(self.counts))

    def summary(self) -> dict:
        return dict(input_mode='explicit-study-assumptions' if self.study else 'qualified-contracts',
                    supplier_inputs_qualified=bool(self.allocations) and not self.study,
                    component=asdict(self.component), installed_order_units=self.order_units,
                    cumulative=dict(self.counts), factory_peak_storage=self.peak_storage,
                    factory_storage_limits={sid: s.storage_units for sid, s in self.suppliers.items()},
                    factory_accepted_stock=self.accepted_stock, in_transit_beams=self.in_transit,
                    routes=[asdict(r) for r in self.routes])
