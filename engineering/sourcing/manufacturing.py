"""Quantity-derived manufacturing hypotheses, not installed design qualification.

The laminate fraction is a *weight* fraction of glass in glass plus fully mixed
matrix. Dry reinforcement, mixed kits and separate catalysts have distinct
purchase scopes. Unknown process/equipment inputs remain None.
"""
from copy import deepcopy
from decimal import Decimal, ROUND_FLOOR
import re

from .model import UNITS, decimal, decimal_text, identity, is_id, record, text, validate_record


def _binding(candidate_id, input_id, source_ids):
    if not is_id(candidate_id) or not is_id(input_id):
        raise ValueError("Exact candidate and twin/CAD input identities required")
    if not isinstance(source_ids, (tuple, list)) or len(source_ids) != len(set(source_ids)) or any(not is_id(s) for s in source_ids):
        raise ValueError("Distinct source record identities required")


def _number(value, name, *, positive=False):
    return decimal(value, name, positive=positive)


def _jsonable(value):
    if isinstance(value, Decimal):
        return decimal_text(value, nonnegative=False)
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def _sealed(kind, **fields):
    return record(kind, **_jsonable(fields))


def _quantity_row(key, *, net_kg=None, area_m2=None, length_m=None, product_key=None,
                  retained=True, scope, scrap):
    def gross(value):
        return None if value is None else decimal_text(value / (1 - scrap))
    return dict(material_key=key, product_key=product_key, scope=scope, procurement_scope="raw-material",
                retained_in_part=retained,
                net_mass_kg=None if net_kg is None else decimal_text(net_kg),
                gross_mass_kg=gross(net_kg),
                net_area_m2=None if area_m2 is None else decimal_text(area_m2),
                gross_area_m2=gross(area_m2),
                net_length_m=None if length_m is None else decimal_text(length_m),
                gross_length_m=gross(length_m))


def laminate_requirements(candidate_id, input_id, area_m2, plies,
                          fibre_mass_fraction, scrap_fraction, *, source_ids=(),
                          part_id=None, part_definition_id=None, cad_revision_id=None,
                          resin_product_key=None, resin_includes_hardener=None,
                          catalyst_ratio=None, catalyst_product_key=None,
                          core=None, adhesive=None, consumables=None,
                          labour_hours=None, mould_cycle_hours=None,
                          functional_basis_id=None):
    """Calculate a declared laminate schedule and gross purchase requirements.

    Each ply uses ``areal_weight_g_m2``, positive integer ``count`` and optional
    ``fabric_width_m``/``product_key``. Catalyst ratio is kg catalyst per kg base
    resin. If required but unknown, both constituent purchase masses stay None;
    the total mixed-matrix mass remains a declared schedule calculation.

    ``core`` accepts thickness_m+density_kg_m3 or explicit net_mass_kg;
    ``adhesive`` accepts mass_per_area_kg_m2 and optional coverage_count. An
    explicitly inapplicable core/adhesive needs ``not_required=True, reason=...``.
    Consumables are removed manufacturing inputs, never installed mass.
    """
    _binding(candidate_id, input_id, source_ids)
    for value in (part_definition_id, cad_revision_id, functional_basis_id):
        if value is not None and not is_id(value):
            raise ValueError("Exact optional part/CAD/functional identity required")
    if part_id is not None:
        text(part_id, "logical part identity")
    area = _number(area_m2, "area", positive=True)
    fraction = _number(fibre_mass_fraction, "fibre weight fraction", positive=True)
    scrap = _number(scrap_fraction, "scrap fraction")
    if fraction >= 1 or scrap >= 1:
        raise ValueError("Fibre fraction must be below1; scrap must be below1")
    if not isinstance(plies, list) or not plies or len(plies) > 1000:
        raise ValueError("Explicit bounded nonempty ply schedule required")
    if resin_includes_hardener is not None and type(resin_includes_hardener) is not bool:
        raise ValueError("Explicit mixed-kit scope or unknown required")
    if resin_includes_hardener is True and catalyst_ratio is not None:
        raise ValueError("Included hardener cannot also become an added constituent")
    rows, schedule, unknown = [], [], []
    glass = Decimal(0)
    for index, ply in enumerate(plies):
        if not isinstance(ply, dict):
            raise ValueError("Ply object required")
        gsm = _number(ply.get("areal_weight_g_m2"), "dry fibre areal weight", positive=True)
        count = _number(ply.get("count"), "ply count", positive=True)
        if count != count.to_integral_value():
            raise ValueError("Whole ply count required")
        width = None if ply.get("fabric_width_m") is None else _number(ply["fabric_width_m"], "fabric width", positive=True)
        ply_area = area * count
        mass = ply_area * gsm / 1000
        glass += mass
        key = ply.get("material_key", "glass-ply-" + str(index + 1))
        text(key, "fabric material key")
        rows.append(_quantity_row(key, net_kg=mass, area_m2=ply_area,
                    length_m=None if width is None else ply_area / width,
                    product_key=ply.get("product_key"), scope="dry-fabric-only", scrap=scrap))
        schedule.append(dict(areal_weight_g_m2=decimal_text(gsm), count=int(count),
                    fabric_width_m=None if width is None else decimal_text(width),
                    material_key=key, product_key=ply.get("product_key"),
                    orientation_deg=deepcopy(ply.get("orientation_deg"))))
        if width is None:
            unknown.append(key + ":purchased-linear-length")
    matrix = glass * (1 - fraction) / fraction
    if resin_includes_hardener is True:
        rows.append(_quantity_row("mixed-resin-kit", net_kg=matrix,
                    product_key=resin_product_key, scope="resin-and-included-hardener", scrap=scrap))
    elif resin_includes_hardener is False:
        ratio = None if catalyst_ratio is None else _number(catalyst_ratio, "catalyst/base-resin mass ratio")
        if ratio is not None and ratio >= 1:
            raise ValueError("Catalyst/base-resin ratio outside declared model domain")
        base = None if ratio is None else matrix / (1 + ratio)
        catalyst = None if ratio is None else matrix - base
        rows.append(_quantity_row("base-resin", net_kg=base, product_key=resin_product_key,
                    scope="base-resin-excluding-catalyst", scrap=scrap))
        rows.append(_quantity_row("catalyst", net_kg=catalyst, product_key=catalyst_product_key,
                    scope="separate-catalyst-within-mixed-matrix", scrap=scrap))
        if ratio is None:
            unknown.append("matrix:base-resin-and-catalyst-purchase-split")
    else:
        if catalyst_ratio is not None:
            raise ValueError("Catalyst ratio needs an explicit separate-constituent system")
        rows.append(_quantity_row("unresolved-mixed-matrix", net_kg=matrix,
                    scope="mixed-matrix-system-not-yet-sourced", scrap=scrap))
        unknown.append("matrix:kit-or-separate-constituent-definition")
    known_net = glass + matrix

    def added_material(key, value):
        nonlocal known_net
        if value is None:
            rows.append(_quantity_row(key, scope="required-installed-material-unresolved", scrap=scrap))
            unknown.append(key + ":installed-quantity")
            return
        if not isinstance(value, dict):
            raise ValueError("Explicit " + key + " definition or unknown required")
        if value.get("not_required") is True:
            text(value.get("reason"), key + " inapplicability reason")
            rows.append(dict(material_key=key, product_key=None, scope="explicitly-inapplicable", procurement_scope="raw-material",
                             retained_in_part=True, net_mass_kg="0", gross_mass_kg="0",
                             reason=value["reason"]))
            return
        if value.get("net_mass_kg") is not None:
            mass = _number(value["net_mass_kg"], key + " mass")
        elif key == "core":
            if value.get("thickness_m") is None or value.get("density_kg_m3") is None:
                rows.append(dict(_quantity_row(key, product_key=value.get("product_key"), scope="partially-defined-installed-core", scrap=scrap), declared_material_input=deepcopy(value)))
                unknown.append("core:mass-from-thickness-and-density")
                return
            mass = area * _number(value.get("thickness_m"), "core thickness", positive=True) * _number(value.get("density_kg_m3"), "core density", positive=True)
        else:
            if value.get("mass_per_area_kg_m2") is None:
                rows.append(dict(_quantity_row(key, product_key=value.get("product_key"), scope="partially-defined-installed-adhesive", scrap=scrap), declared_material_input=deepcopy(value)))
                unknown.append("adhesive:areal-quantity")
                return
            mass = area * _number(value.get("mass_per_area_kg_m2"), "adhesive areal loading") * _number(value.get("coverage_count", "1"), "adhesive coverage count", positive=True)
        known_net += mass
        rows.append(_quantity_row(key, net_kg=mass, product_key=value.get("product_key"),
                    scope="declared-installed-" + key, scrap=scrap))

    added_material("core", core)
    added_material("adhesive", adhesive)
    if consumables is None:
        unknown.append("consumables:process-inventory-and-quantities")
    elif not isinstance(consumables, list) or len(consumables) > 1000:
        raise ValueError("Bounded consumables list or unknown required")
    else:
        for item in consumables:
            if not isinstance(item, dict):
                raise ValueError("Explicit consumable definition required")
            quantity = item.get("quantity")
            if quantity is not None:
                quantity = decimal_text(quantity, "consumable quantity", positive=True)
            else:
                unknown.append(str(item.get("material_key")) + ":purchase-quantity")
            if item.get("quantity_unit") not in UNITS:
                raise ValueError("Canonical consumable quantity unit required")
            rows.append(dict(material_key=text(item.get("material_key"), "consumable key"),
                product_key=item.get("product_key"), scope="removed-process-consumable", procurement_scope="raw-material",
                retained_in_part=False, purchase_quantity=quantity,
                purchase_unit=text(item.get("quantity_unit"), "consumable unit"),
                installed_mass_kg="0", installed_zero_reason="Removed after declared manufacturing process"))
    labour = None if labour_hours is None else decimal_text(labour_hours, "labour hours")
    cycle = None if mould_cycle_hours is None else decimal_text(mould_cycle_hours, "mould cycle hours", positive=True)
    if labour is None:
        unknown.append("labour:hours")
    if cycle is None:
        unknown.append("mould:cycle-hours-and-utilisation")
    return _sealed("process", process_key="laminate-material-requirements", candidate_id=candidate_id,
        input_id=input_id, part_id=part_id, part_definition_id=part_definition_id,
        cad_revision_id=cad_revision_id, functional_basis_id=functional_basis_id,
        source_ids=list(source_ids), area_m2=decimal_text(area), ply_schedule=schedule,
        fibre_mass_fraction=decimal_text(fraction), fraction_basis="dry-glass/(dry-glass+fully-mixed-matrix)-by-weight",
        scrap_fraction=decimal_text(scrap), gross_quantity_rule="net/(1-scrap)",
        dry_glass_net_kg=decimal_text(glass), mixed_matrix_net_kg=decimal_text(matrix),
        material_rows=rows, conditional_known_net_material_kg=decimal_text(known_net),
        conditional_material_mass_bounds_kg=dict(lower=decimal_text(known_net), upper=None,
            basis="Declared nominal schedule; unknown additional installed material is nonnegative"),
        complete_installed_mass_kg=None, complete_installed_cost=None,
        labour_hours=labour, mould_cycle_hours=cycle,
        unknown_additional_quantities=sorted(set(unknown)),
        mechanical_compliance=None, fire_compliance=None, manufacturing_qualification=None,
        limitations=["A declared material takeoff, not cured-laminate allowables or an installed vehicle",
                     "One explicitly declared scrap fraction is applied uniformly; actual yields require measurements",
                     "Joints, inserts, coatings and equipment must be separately counted"])


def throughput_upper_bound(candidate_id, input_id, casting_rate_m_min, unit_length_m,
                           shift_hours, *, source_ids=(), machine_application,
                           product_application, cure_hours=None, bed_length_m=None,
                           mould_count=None, crew_count=None, labour_hours_per_unit=None,
                           turnaround_hours=None):
    """Separate a casting-rate ceiling from conditional factory cycle capacity."""
    _binding(candidate_id, input_id, source_ids)
    rate = _number(casting_rate_m_min, "casting rate", positive=True)
    length = _number(unit_length_m, "unit length", positive=True)
    shift = _number(shift_hours, "shift duration", positive=True)
    text(machine_application, "machine application")
    text(product_application, "actual product application")
    supplied = dict(cure_hours=cure_hours, bed_length_m=bed_length_m,
                    mould_count=mould_count, crew_count=crew_count,
                    labour_hours_per_unit=labour_hours_per_unit,
                    turnaround_hours=turnaround_hours)
    parsed = {k: None if v is None else _number(v, k, positive=k not in ("cure_hours", "turnaround_hours")) for k, v in supplied.items()}
    for key in ("mould_count", "crew_count"):
        if parsed[key] is not None and parsed[key] != parsed[key].to_integral_value():
            raise ValueError("Whole factory resource counts required")
    cast_length = rate * 60 * shift
    cast_units = (cast_length / length).to_integral_value(rounding=ROUND_FLOOR)
    compatible = machine_application == product_application
    ideal_cycle_units = None
    if compatible and all(v is not None for v in parsed.values()):
        slots = min((parsed["bed_length_m"] / length).to_integral_value(rounding=ROUND_FLOOR), parsed["mould_count"])
        cycle_h = parsed["bed_length_m"] / rate / 60 + parsed["cure_hours"] + parsed["turnaround_hours"]
        crew_units = parsed["crew_count"] * shift / parsed["labour_hours_per_unit"]
        ideal_cycle_units = min(cast_units, slots * shift / cycle_h, crew_units)
    return _sealed("process", process_key="factory-throughput-upper-bound", candidate_id=candidate_id,
        input_id=input_id, source_ids=list(source_ids), machine_application=machine_application,
        product_application=product_application, application_compatibility="declared-match" if compatible else "unverified-product-process-transfer",
        casting_rate_m_min=decimal_text(rate), unit_length_m=decimal_text(length), shift_hours=decimal_text(shift),
        casting_only_upper_bound_length_m=decimal_text(cast_length),
        casting_only_upper_bound_units=int(cast_units),
        resource_inputs={k: None if v is None else decimal_text(v) for k, v in parsed.items()},
        conditional_steady_state_units_per_shift_upper_bound=None if ideal_cycle_units is None else decimal_text(ideal_cycle_units),
        complete_output_units=None,
        unknown_additional_quantities=[k for k, v in parsed.items() if v is None],
        required_unmodelled_steps=["initial-WIP-and-calendar", "prestress-release", "QA-and-rejects", "handling-and-storage"],
        limitations=["Casting speed alone is not plant throughput",
                     "Initial WIP, calendar, cutting, prestress release, QA, reject rate and handling remain separate",
                     "Hollow-core slab equipment does not establish railway-girder manufacture"])


def crane_screen(candidate_id, input_id, load_mass_kg, *, source_ids=(),
                 radius_m=None, configuration=None, chart_point=None,
                 rigging_mass_kg=None, dynamic_factor=None,
                 hook_height_m=None, ground_assessment_id=None):
    """Screen only an exact supplied load-chart point; never interpolate maxima.

    A point requires radius_m, capacity_kg, configuration and source_id. These
    are caller-supplied actual chart observations, not generated chart capacities.
    """
    _binding(candidate_id, input_id, source_ids)
    load = _number(load_mass_kg, "manufactured lifted mass", positive=True)
    radius = None if radius_m is None else _number(radius_m, "operating radius", positive=True)
    rigging = None if rigging_mass_kg is None else _number(rigging_mass_kg, "rigging mass")
    factor = None if dynamic_factor is None else _number(dynamic_factor, "declared lift factor", positive=True)
    if factor is not None and factor < 1:
        raise ValueError("Lift factor cannot reduce gravity load")
    if hook_height_m is not None:
        _number(hook_height_m, "required hook height", positive=True)
    required_config = {"crane_model", "boom_length_m", "counterweight_kg", "outrigger_setup", "slew_sector", "reeving_parts", "chart_revision"}
    if configuration is not None:
        if not isinstance(configuration, dict) or not required_config <= set(configuration):
            raise ValueError("Complete load-chart crane configuration required")
        for key in ("crane_model", "outrigger_setup", "slew_sector", "chart_revision"):
            text(configuration[key], "crane " + key)
        for key in ("boom_length_m", "counterweight_kg", "reeving_parts"):
            _number(configuration[key], "crane " + key, positive=key != "counterweight_kg")
        reeving = _number(configuration["reeving_parts"], "reeving count", positive=True)
        if reeving != reeving.to_integral_value():
            raise ValueError("Whole reeving count required")
    if ground_assessment_id is not None and not is_id(ground_assessment_id):
        raise ValueError("Exact ground assessment identity required")
    capacity = None
    if chart_point is not None:
        if not isinstance(chart_point, dict) or not is_id(chart_point.get("source_id")) or chart_point["source_id"] not in source_ids:
            raise ValueError("Load-chart source binding required")
        point_radius = _number(chart_point.get("radius_m"), "chart radius", positive=True)
        if radius is None or configuration is None or point_radius != radius or chart_point.get("configuration") != configuration:
            raise ValueError("Exact operating-radius/configuration chart point required; no extrapolation")
        capacity = _number(chart_point.get("capacity_kg"), "chart capacity", positive=True)
    demand = None if rigging is None or factor is None else (load + rigging) * factor
    screen = False if capacity is not None and load > capacity else None if demand is None or capacity is None else demand <= capacity
    return _sealed("process", process_key="exact-crane-chart-screen", candidate_id=candidate_id,
        input_id=input_id, source_ids=list(source_ids), load_mass_kg=decimal_text(load),
        radius_m=None if radius is None else decimal_text(radius), configuration=deepcopy(configuration),
        chart_point=deepcopy(chart_point), rigging_mass_kg=None if rigging is None else decimal_text(rigging),
        dynamic_factor=None if factor is None else decimal_text(factor),
        factored_hook_demand_kg=None if demand is None else decimal_text(demand),
        chart_capacity_kg=None if capacity is None else decimal_text(capacity),
        chart_capacity_screen=screen, lift_approved=False, hook_height_m=hook_height_m,
        ground_assessment_id=ground_assessment_id, installed_lift_cost=None,
        limitations=["Capacity screen only; no crane, rigging, access, wind or ground acceptance",
                     "Headline maximum tonnage is not capacity at an arbitrary radius"])


def compare_raw_material_costs(processes, unit_prices, *, currency="GBP"):
    """Compare only declared raw-material requirements at one functional basis.

    Price rows must state unit, unit_price, currency and source_id. Commercial
    pack/MOQ/tax/freight normalization belongs to the sourcing pricing adapter.
    """
    if not isinstance(processes, list) or len(processes) < 2:
        raise ValueError("At least two explicit process records required")
    for process in processes:
        validate_record(process, "process")
        if process.get("process_key") != "laminate-material-requirements":
            raise ValueError("Laminate takeoff records required")
    basis = processes[0].get("functional_basis_id")
    if not is_id(basis) or any(p.get("functional_basis_id") != basis or p["area_m2"] != processes[0]["area_m2"] for p in processes):
        raise ValueError("Same explicit functional basis and area required")
    if not isinstance(unit_prices, dict):
        raise ValueError("Explicit source-linked material unit prices required")
    if not isinstance(currency, str) or re.fullmatch("[A-Z]{3}", currency) is None:
        raise ValueError("Explicit ISO comparison currency required")
    source_ids = {s for process in processes for s in process["source_ids"]}
    results = []
    for process in processes:
        subtotal = Decimal(0);missing=[];lines=[]
        for row in process["material_rows"]:
            if row["scope"] == "explicitly-inapplicable":
                continue
            key = row["material_key"];price = unit_prices.get(key)
            if price is None:
                missing.append(key);continue
            if not isinstance(price, dict) or price.get("currency") != currency or not is_id(price.get("source_id")):
                raise ValueError("Same currency and exact price-source identity required")
            source_ids.add(price["source_id"])
            unit = price.get("unit")
            if row["scope"] == "removed-process-consumable":
                if row.get("purchase_unit") != unit:
                    raise ValueError("Consumable price quantity unit mismatch")
                quantity = row.get("purchase_quantity")
            else:
                if unit not in ("kg", "m", "m2"):
                    raise ValueError("Material price quantity unit mismatch")
                quantity = row.get({"kg":"gross_mass_kg", "m":"gross_length_m", "m2":"gross_area_m2"}[unit])
            if unit not in ("kg", "m", "m2") and row.get("purchase_unit") != unit:
                raise ValueError("Material price quantity unit mismatch")
            if quantity is None:
                missing.append(key);continue
            total = _number(quantity, "gross material requirement") * _number(price.get("unit_price"), "material unit price")
            subtotal += total;lines.append(dict(material_key=key, unit=unit, quantity=quantity,
                unit_price=decimal_text(price["unit_price"]), source_id=price["source_id"], subtotal=decimal_text(total)))
        results.append(dict(process_id=process["record_id"], candidate_id=process["candidate_id"],
            known_material_subtotal=None if not lines else decimal_text(subtotal), priced_line_count=len(lines), missing_material_prices=missing,
            declared_material_total=None if missing else decimal_text(subtotal), lines=lines,
            complete_installed_cost=None, complete_whole_life_cost=None))
    return _sealed("run", purpose="same-area-raw-material-cost-screen-only", source_ids=sorted(source_ids),
        functional_basis_id=basis, area_m2=processes[0]["area_m2"], currency=currency,
        process_ids=[p["record_id"] for p in processes], results=results,
        qualified_selection=None, procurement_winner=None,
        limitations=["Raw material screen excludes labour, tooling, inspection, installation, operation and renewal",
                     "Same declared functional basis does not demonstrate structural/thermal/fire compliance"])


def example_buildups():
    """Three explicit research hypotheses; none changes the selected reference."""
    basis = identity(dict(scope="10m2 roof material screen", loads="unqualified", comfort="same declared target"))
    recipes = [("solid-glass", "4", "0.50", dict(not_required=True, reason="Solid laminate hypothesis")),
               ("sandwich-glass", "2", "0.50", dict(thickness_m="0.02", density_kg_m3="80")),
               ("higher-fibre-sandwich", "2", "0.60", dict(thickness_m="0.02", density_kg_m3="80"))]
    output=[]
    for name,count,fraction,core in recipes:
        defined=dict(recipe=name,area_m2="10",plies=[dict(areal_weight_g_m2="600",count=count,fabric_width_m="1.27",material_key="glass-600",product_key="EC-GF-BA-600-127")],fibre_mass_fraction=fraction,scrap_fraction="0.10",core=core)
        output.append(laminate_requirements(identity(dict(physical_hypothesis=defined)),identity(defined),"10",defined["plies"],fraction,"0.10",core=core,
            resin_includes_hardener=True,resin_product_key="EC-EP-IN2-S-1",functional_basis_id=basis))
    return output
