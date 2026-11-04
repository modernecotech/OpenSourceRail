"""Bounded project-volume make/buy arithmetic, without procurement approval.

Prices share one declared currency and output unit. Tier prices are final rates;
there is no implicit bulk discount, country preference or future-order credit.
An item owns the declared factory costs: callers comparing a shared factory must
allocate those costs explicitly once, outside this single-item calculation.
"""
from copy import deepcopy
from math import ceil, fsum, isclose, isfinite, log2
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity

PRODUCER = "engineering/outline/make_buy.py"
CASES = ("low", "base", "high")
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    procurement_approved=False, manufacturing_release=False,
    operating_release=False, selected_reference_changed=False)
_LOADED = {PRODUCER: digest(__file__),
    "engineering/station_rail/common.py": digest(Path(ROOT)/"engineering/station_rail/common.py")}
_OPERATIONS = ("cell_hours_per_unit", "labour_hours_per_unit", "machine_hours_per_unit",
    "setup_cell_hours_per_batch", "setup_labour_hours_per_batch", "setup_machine_hours_per_batch",
    "batch_quantity", "labour_rate_per_hour", "machine_rate_per_hour", "energy_kwh_per_unit", "setup_energy_kwh_per_batch",
    "energy_rate_per_kwh", "consumables_per_unit", "qa_per_unit")
_FIXED = ("equipment_per_cell", "tooling_per_cell", "building_shared", "commissioning_shared")
_LANDED = ("freight_per_unit", "insurance_fraction", "duty_fraction", "qa_per_unit", "local_delivery_per_unit")
_LEARNING_FIELDS = frozenset(("cell_hours_per_unit", "labour_hours_per_unit", "machine_hours_per_unit"))


class _Reader:
    def __init__(self, value, case):
        self.value, self.case, self.unknown = value, case, set()

    def raw(self, path):
        value = self.value
        for key in path.split("."):
            if not isinstance(value, dict) or key not in value or value[key] is None:
                self.unknown.add(path)
                return None
            value = value[key]
        return value

    def number(self, path, *, positive=False, fraction=False, scenario=True):
        value = self.raw(path)
        if isinstance(value, dict) and scenario:
            if set(value)-set(CASES):
                raise ValueError("Only low/base/high values are permitted: "+path)
            value = value.get(self.case)
            if value is None:
                self.unknown.add(path+"."+self.case)
                return None
        if value is None:
            return None
        if type(value) not in (int, float) or not isfinite(value) or value < 0 or positive and value <= 0:
            raise ValueError("Finite "+("positive" if positive else "nonnegative")+" value required: "+path)
        if fraction and value > 1:
            raise ValueError("Fraction exceeds one: "+path)
        return value

    def text(self, path):
        value = self.raw(path)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError("Nonempty string required: "+path)
        return value


def _choice(buy, make):
    if buy is None or make is None:
        return None
    if isclose(buy, make, rel_tol=1e-12, abs_tol=1e-9):
        return "tie"
    return "make" if make < buy else "buy"


def _finite(value):
    if isinstance(value, dict):
        for item in value.values():
            _finite(item)
    elif isinstance(value, list):
        for item in value:
            _finite(item)
    elif type(value) is float and not isfinite(value):
        raise ValueError("Make/buy arithmetic exceeded finite numeric range")


def _purchase(reader, quantity, unit, currency):
    start = set(reader.unknown)
    branch = reader.raw("purchase")
    if not isinstance(branch, dict):
        if branch is not None:
            raise ValueError("purchase must be a mapping")
        return None
    if any("discount" in key.lower() for key in branch):
        raise ValueError("Tier prices are final; a second purchase discount is not permitted")
    supplied_unit = reader.text("purchase.unit")
    if unit is not None and supplied_unit is not None and supplied_unit != unit:
        raise ValueError("Purchase/output unit mismatch; perform an explicit conversion first")
    if "currency" in branch and branch["currency"] != currency:
        raise ValueError("Purchase currency mismatch; perform an explicit FX conversion first")
    tiers = reader.raw("purchase.tiers")
    if tiers is None:
        return None
    if not isinstance(tiers, list) or not 1 <= len(tiers) <= 64:
        raise ValueError("One to 64 explicit purchase tiers required")
    parsed = []
    for index, tier in enumerate(tiers):
        if not isinstance(tier, dict):
            raise ValueError("Each purchase tier must be a mapping")
        if any("discount" in key.lower() for key in tier):
            raise ValueError("Tier prices already include their declared quantity terms")
        prefix = "tier"+str(index)
        r = _Reader({prefix: tier}, reader.case)
        minimum = r.number(prefix+".minimum_quantity", scenario=False)
        price = r.number(prefix+".unit_price")
        source_class = r.text(prefix+".source_class")
        source = r.text(prefix+".source")
        bulk = r.raw(prefix+".already_bulk")
        if bulk is not None and type(bulk) is not bool:
            raise ValueError("already_bulk must be an explicit boolean")
        reader.unknown.update("purchase.tiers["+str(index)+"]."+p.split(".", 1)[1] for p in r.unknown)
        parsed.append(dict(minimum_quantity=minimum, unit_price=price, already_bulk=bulk,
            source_class=source_class, source=source, tier_index=index))
    minima = [t["minimum_quantity"] for t in parsed if t["minimum_quantity"] is not None]
    if len(minima) != len(set(minima)):
        raise ValueError("Purchase tier minimum quantities must be unique")
    landed = {key: reader.number("purchase.landed."+key,
        fraction=key.endswith("fraction")) for key in _LANDED}
    if quantity is None or unit is None or reader.unknown-start:
        return None
    applicable = [tier for tier in parsed if tier["minimum_quantity"] <= quantity]
    if not applicable:
        reader.unknown.add("purchase.no_applicable_quantity_tier")
        return None
    selected = max(applicable, key=lambda tier: tier["minimum_quantity"])
    goods = quantity*selected["unit_price"]
    freight = quantity*landed["freight_per_unit"]
    insurance = (goods+freight)*landed["insurance_fraction"]
    duty = (goods+freight+insurance)*landed["duty_fraction"]
    costs = dict(goods=goods, freight=freight, insurance=insurance, duty=duty,
        QA=quantity*landed["qa_per_unit"], local_delivery=quantity*landed["local_delivery_per_unit"])
    total = fsum(costs.values())
    return dict(total=total, per_unit=total/quantity, components=costs, selected_tier=selected,
        quantity=quantity, unit=unit, currency=currency, extra_bulk_discount_applied=False,
        insurance_basis="goods plus freight", duty_basis="goods plus freight plus insurance",
        price_maturity=selected["source_class"], quoted_price_authenticated=False)


def _make(reader, quantity, unit, currency, years):
    start = set(reader.unknown)
    branch = reader.raw("make")
    if not isinstance(branch, dict):
        if branch is not None:
            raise ValueError("make must be a mapping")
        return None
    supplied_unit = reader.text("make.unit")
    if unit is not None and supplied_unit is not None and supplied_unit != unit:
        raise ValueError("Manufacturing/output unit mismatch")
    if "currency" in branch and branch["currency"] != currency:
        raise ValueError("Manufacturing currency mismatch; perform an explicit FX conversion first")
    material_unit = reader.text("make.material.unit")
    net = reader.number("make.material.net_quantity_per_unit", positive=True)
    material_price = reader.number("make.material.unit_price")
    yield_fraction = reader.number("make.material.yield_fraction", positive=True, fraction=True)
    # An omitted/None scrap credit explicitly means no recovery credit, not free material.
    credit_spec = branch.get("material", {}).get("scrap_credit_per_unit") if isinstance(branch.get("material"), dict) else None
    credit = 0. if credit_spec is None else reader.number("make.material.scrap_credit_per_unit")
    operations = {key: reader.number("make.operations."+key,
        positive=key in ("cell_hours_per_unit", "batch_quantity")) for key in _OPERATIONS}
    fixed = {key: reader.number("make.fixed."+key) for key in _FIXED}
    building_reference = None
    if fixed["building_shared"] == 0:
        priced_elsewhere = reader.raw("make.fixed.building_priced_elsewhere")
        building_reference = reader.text("make.fixed.building_cost_reference")
        if priced_elsewhere is not None and priced_elsewhere is not True:
            raise ValueError("Zero building cost requires an explicit priced-elsewhere allocation")
    labour_basis = reader.text("make.operations.labour_rate_basis")
    machine_basis = reader.text("make.operations.machine_rate_basis")
    if labour_basis not in (None,"productive-hour-loaded","paid-hour"):
        raise ValueError("labour_rate_basis must be productive-hour-loaded or paid-hour")
    if machine_basis not in (None,"cash-operating-excluding-capital-recovery"):
        raise ValueError("Machine hourly rate must be cash operating cost excluding capital recovery")
    paid_factor = reader.number("make.operations.paid_hours_per_productive_hour",positive=True) if labour_basis=="paid-hour" else 1.
    if paid_factor is not None and paid_factor < 1:
        raise ValueError("Paid hours cannot be smaller than the declared productive hours")
    capacity = {key: reader.number("make.capacity."+key, positive=True,
        fraction=key=="utilisation") for key in ("shifts_per_day", "hours_per_shift", "days_per_year", "utilisation")}
    if capacity["shifts_per_day"] not in (None, 2):
        raise ValueError("This manufacturing planning contract uses two shifts/day")
    learning = branch.get("learning")
    factor, applies = 1., []
    if learning is not None:
        if not isinstance(learning, dict):
            raise ValueError("learning must be None or an explicit bounded curve")
        ratio = reader.number("make.learning.progress_ratio", positive=True, fraction=True)
        reference = reader.number("make.learning.reference_quantity", positive=True)
        minimum = reader.number("make.learning.floor_fraction", positive=True, fraction=True)
        applies = reader.raw("make.learning.applies_to")
        if applies is not None and (not isinstance(applies, list) or not applies
                or len(applies)!=len(set(applies)) or not set(applies)<=_LEARNING_FIELDS):
            raise ValueError("Learning may affect only declared cell/labour/machine hours")
        if all(x is not None for x in (quantity, ratio, reference, minimum)):
            factor = max(minimum, min(1., (quantity/reference)**log2(ratio)))
    if quantity is None or unit is None or years is None or reader.unknown-start:
        return None
    if applies is None:
        return None
    effective = {key: value*factor if key in applies else value for key, value in operations.items()}
    batches = ceil(quantity/effective["batch_quantity"])
    required = quantity*effective["cell_hours_per_unit"]+batches*effective["setup_cell_hours_per_batch"]
    hours_per_cell_year = capacity["shifts_per_day"]*capacity["hours_per_shift"]*capacity["days_per_year"]*capacity["utilisation"]
    project_hours_per_cell = hours_per_cell_year*years
    cells = max(1, ceil(required/project_hours_per_cell))
    labour_hours = quantity*effective["labour_hours_per_unit"]+batches*effective["setup_labour_hours_per_batch"]
    machine_hours = quantity*effective["machine_hours_per_unit"]+batches*effective["setup_machine_hours_per_batch"]
    gross_per_unit = net/yield_fraction
    scrap_per_unit = gross_per_unit-net
    if credit > scrap_per_unit*material_price:
        raise ValueError("Scrap credit exceeds the purchased waste-material cost")
    variable = dict(material_gross=quantity*gross_per_unit*material_price,
        scrap_credit=-quantity*credit, labour=labour_hours*paid_factor*effective["labour_rate_per_hour"],
        machine=machine_hours*effective["machine_rate_per_hour"],
        energy=(quantity*effective["energy_kwh_per_unit"]+batches*effective["setup_energy_kwh_per_batch"])*effective["energy_rate_per_kwh"],
        consumables=quantity*effective["consumables_per_unit"], QA=quantity*effective["qa_per_unit"])
    fixed_components = dict(equipment=cells*fixed["equipment_per_cell"], tooling=cells*fixed["tooling_per_cell"],
        building=fixed["building_shared"], commissioning=fixed["commissioning_shared"])
    variable_total = fsum(variable.values()); fixed_total = fsum(fixed_components.values())
    total = variable_total+fixed_total
    return dict(total=total, per_unit=total/quantity, variable_components=variable,
        fixed_components=fixed_components, variable_total=variable_total, fixed_total=fixed_total,
        fixed_cost_counted_once=True, fixed_amortisation_volume=quantity,
        fixed_cost_per_committed_unit=fixed_total/quantity, speculative_future_order_credit=0., resale_credit=0.,
        quantity=quantity, unit=unit, currency=currency, project_years=years,
        material=dict(unit=material_unit, net_quantity=quantity*net,
            purchased_quantity=quantity*gross_per_unit, scrap_quantity=quantity*scrap_per_unit,
            yield_fraction=yield_fraction, scrap_credit_per_output_unit=credit,
            scrap_credit_declared=credit_spec is not None),
        batches=batches, cell_count=cells, required_cell_hours=required,
        labour_hours=labour_hours, charged_labour_hours=labour_hours*paid_factor, machine_hours=machine_hours,
        labour_rate_basis=labour_basis, paid_hours_per_productive_hour=paid_factor,
        labour_utilisation_adjustment_inferred=False, machine_rate_basis=machine_basis,
        building_cost_reference=building_reference,
        effective_operations=effective,
        available_hours_per_cell_per_year=hours_per_cell_year,
        available_hours_per_cell_project=project_hours_per_cell,
        available_project_cell_hours=cells*project_hours_per_cell,
        capacity=capacity, capacity_model="aggregate cell occupancy; not an executable workstation schedule",
        learning=dict(declared=learning is not None, average_hours_factor=factor, applies_to=applies,
            convention="Bounded cumulative-average hours at committed project volume; setup, materials and QA unchanged"))


def _case(spec, case, override_quantity=None):
    reader = _Reader(spec, case)
    unit = reader.text("unit"); currency = reader.text("currency")
    reader.text("item_id")
    quantity = reader.number("quantity", positive=True, scenario=False)
    committed = reader.number("committed_volume", positive=True, scenario=False)
    years = reader.number("project_years", positive=True, scenario=False)
    if quantity is not None and committed is not None and quantity != committed:
        raise ValueError("Project quantity must equal declared committed volume; no speculative factory amortisation")
    if override_quantity is not None:
        quantity = override_quantity
    top_unknown = set(reader.unknown)
    purchase = _purchase(reader, quantity, unit, currency)
    make = _make(reader, quantity, unit, currency, years)
    if top_unknown:
        purchase = make = None
    preferred = _choice(purchase["total"] if purchase else None, make["total"] if make else None)
    result = dict(case=case, status="complete" if preferred is not None else "incomplete",
        quantity=quantity, purchase=purchase, make=make, preferred=preferred,
        make_minus_buy=make["total"]-purchase["total"] if preferred is not None else None,
        unknowns=sorted(reader.unknown))
    _finite(result)
    return result


def _break_even(spec):
    request = spec.get("break_even")
    if request is None:
        return dict(status="not-requested", global_crossover_established=False)
    if not isinstance(request, dict):
        raise ValueError("break_even must be an explicit bounded integer search request")
    low, high, budget = (request.get(k) for k in ("minimum_quantity", "maximum_quantity", "max_evaluations"))
    if any(type(v) is not int for v in (low, high, budget)) or not 1 <= low <= high or not 2 <= budget <= 2048:
        raise ValueError("Break-even needs positive integer bounds and 2..2048 evaluations")
    complete = high-low+1 <= budget
    if complete:
        quantities = list(range(low, high+1))
    else:
        # Spaced samples cannot prove what happens in their untested gaps.
        quantities = sorted({low, high, *[round(low+(high-low)*i/(budget-1)) for i in range(budget)]})
    samples = {case: [] for case in CASES}
    for q in quantities:
        for case in CASES:
            row = _case(spec, case, override_quantity=q)
            samples[case].append(dict(quantity=q, preferred=row["preferred"], make_minus_buy=row["make_minus_buy"],
                cell_count=row["make"]["cell_count"] if row["make"] else None,
                tier_index=row["purchase"]["selected_tier"]["tier_index"] if row["purchase"] else None,
                unknowns=row["unknowns"]))
    transitions = {case: [] for case in CASES}
    intervals = {case: [] for case in CASES}
    for case in CASES:
        rows = samples[case]
        for left, right in zip(rows, rows[1:]):
            if left["preferred"] != right["preferred"]:
                transitions[case].append(dict(lower_quantity=left["quantity"], upper_quantity=right["quantity"],
                    lower_preferred=left["preferred"], upper_preferred=right["preferred"],
                    exact_adjacent_integer_boundary=right["quantity"]==left["quantity"]+1,
                    same_fixed_cell_and_tier_segment=(left["cell_count"]==right["cell_count"]
                        and left["tier_index"]==right["tier_index"])))
        if complete:
            for row in rows:
                if intervals[case] and intervals[case][-1]["preferred"]==row["preferred"]:
                    intervals[case][-1]["maximum_quantity"]=row["quantity"]
                else:
                    intervals[case].append(dict(minimum_quantity=row["quantity"],maximum_quantity=row["quantity"],
                        preferred=row["preferred"]))
    return dict(status="complete-in-declared-integer-domain" if complete else "sampled-unresolved-gaps",
        method="bounded direct cost evaluation including tier, batch and capacity steps",
        domain=dict(minimum_quantity=low,maximum_quantity=high,quantity_unit=spec.get("unit")),
        distinct_quantities_evaluated=len(quantities), complete_integer_domain=complete,
        samples=samples, transitions=transitions, preferred_intervals=intervals,
        exact_cost_ties={case:[r["quantity"] for r in samples[case] if r["preferred"]=="tie"] for case in CASES},
        untested_intervals=[dict(minimum_quantity=a+1,maximum_quantity=b-1)
            for a,b in zip(quantities,quantities[1:]) if b>a+1],
        global_crossover_established=False,
        limitation="Counterfactual committed integer quantities only; capacity/tier steps may reverse preference repeatedly. No extrapolated global crossover.")


def evaluate(spec, root=ROOT):
    """Compare one explicit committed project item in three declared cases.

    Missing required numeric inputs hold the affected calculation at None.
    Invalid values, mixed units/currencies and speculative allocation are rejected.
    No exchange rate, country multiplier, bulk reduction or financing is invented.
    """
    if not isinstance(spec, dict):
        raise ValueError("Explicit make/buy specification mapping required")
    root = Path(root)
    if any(digest(root/name) != sha for name, sha in _LOADED.items()):
        raise ValueError("Loaded make/buy source changed; restart calculation worker")
    request = deepcopy(spec)
    input_id = identity(dict(schema="osr-make-buy-input/1",specification=request))
    cases = {case: _case(request,case) for case in CASES}
    base_choice = cases["base"]["preferred"]
    for row in cases.values():
        branch = {"make":"make","buy":"purchase"}.get(base_choice)
        row["cost_of_base_choice"] = row[branch]["total"] if branch and row[branch] is not None else None
        row["preference_differs_from_base"] = row["preferred"] != base_choice if row["preferred"] is not None and base_choice is not None else None
    result = dict(schema="osr-make-buy-evaluation/1", input_id=input_id, specification=request,
        item_id=request.get("item_id"),unit=request.get("unit"),currency=request.get("currency"),
        cases=cases, base_choice=base_choice,
        status="complete" if all(row["status"]=="complete" for row in cases.values()) else "incomplete",
        unknowns=sorted({u for row in cases.values() for u in row["unknowns"]}),
        break_even=_break_even(request),source_sha256=dict(_LOADED),
        runtime_contract=dict(implementation="CPython",supported_python=["3.12","3.13"],
            arithmetic="stdlib binary64 arithmetic and canonical JSON; no native solver",
            observed_execution_runtime="Record actual interpreter/tool versions in the external execution receipt"),
        estimate_scope="Declared one-item project production or landed purchase; complete only for supplied comparable scope",
        accounting_notes=["Machine rate must exclude capital already counted in fixed factory cost; only operating charges belong in that rate.",
            "Cell occupancy includes declared setup. Labour/machine/energy setup inputs are separately costed by batch.",
            "Capacity utilisation does not automatically price paid idle time: declare an inclusive productive-hour labour rate or an explicit paid/productive-hours factor.",
            "Factory building and commissioning are counted once, equipment/tooling once per required parallel cell.",
            "No speculative future volume, resale, imported-price preference or automatic learning discount is credited.",
            "Shared factory or procurement overhead allocation belongs to the caller and must not be charged twice across items."],**FLAGS)
    _finite(result)
    if any(digest(root/name) != sha for name, sha in _LOADED.items()):
        raise ValueError("Make/buy source changed during evaluation")
    result["evaluation_id"] = identity(result)
    return result
