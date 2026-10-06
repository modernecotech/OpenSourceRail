"""Whole-bay chronological erection with explicit supply and support releases."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import math
from .supply import ErectionFront
from .supply_chain import ConstructionSupplyChain


@dataclass(frozen=True)
class ShiftCycle:
    shifts_day: int = 1
    hours_shift: float = 8.0
    productive_fraction: float = 1.0
    handover_hours: float = 0.0
    maintenance_hours_day: float = 0.0
    placement_hours_beam: float = 2.0
    securing_hours_beam: float = 1.0
    advance_hours_bay: float = 2.0
    weather_availability: float = 1.0
    permitted_hours_day: float = 24.0
    mobilisation_days: int = 0
    ramp_up_days: int = 0
    ramp_up_fraction: float = 0.5

    def __post_init__(self):
        if type(self.shifts_day) is not int or not 1 <= self.shifts_day <= 3:
            raise ValueError("one to three distinct crews/shifts required")
        if any(not math.isfinite(x) or x <= 0 for x in (self.hours_shift,self.placement_hours_beam,self.securing_hours_beam,self.advance_hours_bay,self.permitted_hours_day)):
            raise ValueError("cycle times and work windows must be positive")
        if self.shifts_day*self.hours_shift > 24 or min(self.handover_hours,self.maintenance_hours_day,self.mobilisation_days,self.ramp_up_days) < 0:
            raise ValueError("invalid shift/calendar allowances")
        if any(not 0 < x <= 1 for x in (self.productive_fraction,self.weather_availability,self.ramp_up_fraction)):
            raise ValueError("availability factors must be in (0,1]")
        if self.productive_hours_day <= 0:
            raise ValueError("no productive hours remain")

    @property
    def productive_hours_day(self) -> float:
        hours = min(self.shifts_day*self.hours_shift,self.permitted_hours_day)
        return max(0,(hours-(self.shifts_day-1)*self.handover_hours-self.maintenance_hours_day)*self.productive_fraction*self.weather_availability)

    @property
    def bay_cycle_hours(self) -> float:
        return 2*(self.placement_hours_beam+self.securing_hours_beam)+self.advance_hours_bay

    @property
    def bays_launcher_day(self) -> float:
        return self.productive_hours_day/self.bay_cycle_hours


def support_requirements(front: ErectionFront, span_m: float = 25.0) -> list[int]:
    """Each disconnected running interval needs its own first support pair."""
    requirements=[];cumulative=0
    intervals=front.work_intervals_m or ((front.start_chainage_m,front.end_chainage_m),)
    if front.direction == -1:
        intervals=tuple(reversed(intervals))
    for a,b in intervals:
        for bay in range(math.ceil((b-a)/span_m)):
            cumulative+=2 if bay==0 else 1
            requirements.append(cumulative)
    return requirements


def simulate_erection(fronts: list[ErectionFront], cycle: ShiftCycle, *,
                      accepted_beams_day: dict[int,int], delivered_beams_day: dict[int,dict[str,int]],
                      supports_released_day: dict[int,dict[str,int]], buffer_capacity: dict[str,int],
                      span_m: float = 25.0, maximum_days: int = 3650,
                      dispatch_capacity_day: dict[str,int] | None = None,
                      supply_chain: ConstructionSupplyChain | None = None) -> dict:
    """Daily integer receipts and completed two-track bays; no future supply credit.

    Hours can carry across days only while a bay is active. Idle access, missing
    components and missing supports do not accrue future erection capacity.
    Receipts are accepted components only; casting/rejection is upstream.
    Shared obstructed delivery routes and sequential paths are exclusive per day.
    """
    if span_m not in (20,25) or maximum_days <= 0:
        raise ValueError("invalid span or simulation horizon")
    if supply_chain is not None and (accepted_beams_day or delivered_beams_day or dispatch_capacity_day is not None):
        raise ValueError("use the supply chain or explicit supply/delivery schedules, not both")
    if len({f.id for f in fronts}) != len(fronts):
        raise ValueError("front identities must be unique")
    if any(f.id not in buffer_capacity or buffer_capacity[f.id] < 2 for f in fronts):
        raise ValueError("front requires buffer capacity for a complete bay")
    for i,a in enumerate(fronts):
        for b in fronts[i+1:]:
            if a.line == b.line:
                first=a.work_intervals_m or ((a.start_chainage_m,a.end_chainage_m),)
                second=b.work_intervals_m or ((b.start_chainage_m,b.end_chainage_m),)
                if any(max(x,u)<min(y,v)-1e-9 for x,y in first for u,v in second):
                    raise ValueError("construction fronts overlap the same physical erection path")
    needs = {f.id:sum(math.ceil((b-a)/span_m) for a,b in f.work_intervals_m) if f.work_intervals_m else math.ceil((f.end_chainage_m-f.start_chainage_m)/span_m) for f in fronts}
    required_supports={f.id:support_requirements(f,span_m) for f in fronts}
    done = dict.fromkeys(needs,0)
    inventory = dict.fromkeys(needs,0)
    hours = dict.fromkeys(needs,0.0)
    supports = {f.id:f.available_foundations for f in fronts}
    accepted_stock = 0
    receipts = 0
    rows = []
    finished = {}
    machine_owner = {}
    machine_available_day = {}
    if supply_chain is not None and supply_chain.order_units != 2*sum(needs.values()):
        raise ValueError("supply order must match the installed erection quantities")
    for day in range(1,maximum_days+1):
        supply = None
        if supply_chain is not None:
            supply = supply_chain.step(day,front_inventory=inventory,front_buffer_capacity=buffer_capacity,
                remaining_beams={fid:2*(needs[fid]-done[fid])-inventory[fid] for fid in needs},
                delivery_access={f.id:f.delivery_access for f in fronts},
                closed_fronts={f.id for f in fronts if day in f.interruptions_days})
        incoming = supply['accepted_today'] if supply is not None else accepted_beams_day.get(day,0)
        if type(incoming) is not int or incoming < 0:
            raise ValueError("accepted components must be whole non-negative beams")
        receipts += incoming
        accepted_stock = supply['accepted_factory_stock'] if supply is not None else accepted_stock+incoming
        delivered = supply['delivered'] if supply is not None else delivered_beams_day.get(day,{})
        if dispatch_capacity_day is not None:
            if delivered:
                raise ValueError("use explicit deliveries or constrained dispatch, not both")
            delivered = {}
            ordered = fronts[(day-1)%len(fronts):]+fronts[:(day-1)%len(fronts)] if fronts else []
            available_stock = accepted_stock
            used_delivery_routes = set()
            for f in ordered:
                if f.delivery_access in used_delivery_routes:
                    continue
                remaining = 2*(needs[f.id]-done[f.id])-inventory[f.id]
                quantity = min(dispatch_capacity_day.get(f.id,0),buffer_capacity[f.id]-inventory[f.id],remaining,available_stock)
                if type(quantity) is not int or quantity < 0:
                    raise ValueError("dispatch capacity must be whole non-negative beams")
                delivered[f.id] = quantity
                available_stock -= quantity
                if quantity:
                    used_delivery_routes.add(f.delivery_access)
        for fid,quantity in delivered.items():
            if fid not in inventory or type(quantity) is not int or quantity < 0:
                raise ValueError("invalid front delivery")
            if supply is None and quantity > accepted_stock:
                raise ValueError("delivery exceeds available accepted components")
            if inventory[fid]+quantity > buffer_capacity[fid]:
                raise ValueError("delivery exceeds front buffer capacity")
            if supply is None:
                accepted_stock -= quantity
            inventory[fid] += quantity
        for fid,quantity in supports_released_day.get(day,{}).items():
            if fid not in supports or type(quantity) is not int or quantity < 0:
                raise ValueError("invalid support release")
            supports[fid] = min(required_supports[fid][-1],supports[fid]+quantity)
        access_used, paths_used = set(), set()
        today = []
        # Rotate priority so shared access does not permanently starve a front.
        rotated = fronts[(day-1)%len(fronts):]+fronts[:(day-1)%len(fronts)] if fronts else []
        for f in rotated:
            fid = f.id
            if done[fid] == needs[fid]:
                continue
            reason = "erection"
            if machine_owner.get(f.launcher) not in (None,fid):
                reason = "equipment-assigned-to-another-front"
            elif day < machine_available_day.get(f.launcher,1):
                reason = "equipment-relocation"
            elif day < f.planned_start_day+cycle.mobilisation_days+f.relocation_days or day in f.interruptions_days:
                reason = "work-window-or-station-interruption"
            elif f.delivery_access in access_used or f.sequential_path in paths_used:
                reason = "shared-access-or-sequential-path"
            elif inventory[fid] < 2:
                reason = supply['front_limiting_resource'][fid] if supply is not None else "transport" if accepted_stock else "casting-or-acceptance"
            elif supports[fid] < required_supports[fid][done[fid]]:
                reason = "foundations"
            else:
                machine_owner[f.launcher] = fid
                access_used.add(f.delivery_access)
                paths_used.add(f.sequential_path)
                ramp = cycle.ramp_up_fraction if day < f.planned_start_day+cycle.mobilisation_days+cycle.ramp_up_days else 1.0
                available = min(cycle.productive_hours_day,f.permitted_hours_day)*ramp
                hours[fid] += available
                complete = min(math.floor(hours[fid]/cycle.bay_cycle_hours),inventory[fid]//2,
                               sum(required <= supports[fid] for required in required_supports[fid])-done[fid], needs[fid]-done[fid])
                done[fid] += complete
                inventory[fid] -= 2*complete
                hours[fid] -= complete*cycle.bay_cycle_hours
                # Only fractional progress in an active bay carries forward.
                hours[fid] = min(hours[fid],cycle.bay_cycle_hours-1e-9)
                if done[fid] == needs[fid]:
                    finished[fid] = day
                    machine_owner.pop(f.launcher,None)
                    machine_available_day[f.launcher] = day+f.relocation_days+1
            if reason != "erection":
                hours[fid] = 0.0
            today.append(dict(front=fid,bays_complete=done[fid],buffer_beams=inventory[fid],
                              supports_released=supports[fid],limiting_resource=reason))
        rows.append(dict(day=day,fronts=today,accepted_factory_stock=accepted_stock,
                         cumulative_accepted_beams=receipts,cumulative_erected_beams=2*sum(done.values()),
                         **({'supply_chain':supply} if supply is not None else {})))
        if all(done[k] == needs[k] for k in needs):
            break
    return dict(complete=all(done[k] == needs[k] for k in needs),days=len(rows),
                completed_bays=done,required_bays=needs,finish_days=finished,daily=rows,
                cycle=asdict(cycle),bays_launcher_day=cycle.bays_launcher_day,
                **({'supply_chain':supply_chain.summary()} if supply_chain is not None else {}))
