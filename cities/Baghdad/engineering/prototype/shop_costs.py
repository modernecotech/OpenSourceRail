"""Extend the Airport workshop's quantities at published planning rates."""

import argparse
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
import json
from math import ceil, prod
from pathlib import Path
import tomllib
from zipfile import ZipFile

from cities.Baghdad.airport_integration import write_atomic
from cities.Baghdad.engineering.prototype import factory, sourcing_estimates
from engineering.outline.baghdad_system import _id
from engineering.performance import check_disk_reservation, disk_reservation

HERE = Path(__file__).resolve().parent
RATES = "shop-rates.toml"
REPORT = "SHOP-COSTS.md"
REGISTER = "shop-costs.json"
CASES = ("low", "base", "high")
EQUIPMENT = "equipment purchase"
SERVICE = "opening services"
UPKEEP = "annual equipment upkeep"


def decimal(value):
    return Decimal(str(value))


def money(value):
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def commercial_quantity(resource, rate, drivers):
    basis = rate["basis"]
    if basis == "units":
        quantity = resource["required_units"]
        if quantity is None:
            minimum = resource["minimum_units"]
            return minimum, resource["unit"], "known-subset" if minimum else "open"
        return quantity, resource["unit"], "planned"
    if basis == "driver":
        quantity = drivers[rate["driver"]]
        return quantity, rate["unit"], "planned" if quantity is not None else "open"
    if basis not in {"hours", "shift"} or not resource.get("load"):
        raise ValueError(f"Unsupported price basis for {resource['id']}")

    # Peak output sizes capacity. Only the actual opening production and one
    # setup per operation are payable. Multiplying a peak by workdays overbills.
    hours = Decimal(0)
    has_known_scope = False
    incomplete = False
    for operation in resource["load"]:
        hours += decimal(operation.get("setup_hours", 0))
        cycle = decimal(operation["hours"]) * decimal(operation.get("multiplier", 1))
        for item in operation["items"]:
            if drivers[item] is None:
                incomplete = True
            else:
                hours += decimal(drivers[item]) * cycle
                has_known_scope = True
    unit = "booked shift" if basis == "shift" else "occupied hour"
    if not has_known_scope and incomplete and hours == 0:
        return None, unit, "open"
    quantity = ceil(hours / decimal(resource["usable_hours_per_day"])) if basis == "shift" else float(hours)
    return quantity, unit, "known-subset" if incomplete else "planned"


def verify_edition(record):
    if _id({k: v for k, v in record.items() if k != "evaluation_id"}) != record["evaluation_id"]:
        raise ValueError("Input evaluation digest differs from its contents")


def workshop_scenario(card):
    lines = []
    subtotals = {}
    for key, row in card["workshop"].items():
        rates = row["usd"]
        factors = row["quantity_factors"]
        refs = row.get("refs", [])
        if (any(type(v) is not int or v <= 0 for v in factors) or not factors
                or len(rates) != 3 or rates != sorted(rates) or any(v < 0 for v in rates)
                or set(refs) - card["reference"].keys()
                or (any(v == 0 for v in rates) and "freecad" not in refs)):
            raise ValueError(f"Invalid workshop assumption for {key}")
        quantity = prod(factors)
        amounts = {case: money(decimal(rate) * quantity) for case, rate in zip(CASES, rates, strict=True)}
        subtotal = subtotals.setdefault(row["period"], {case: Decimal(0) for case in CASES})
        for case, value in amounts.items():
            subtotal[case] += decimal(value)
        lines.append(dict(id=key, scope=row["scope"], quantity_factors=factors, priced_quantity=quantity,
                          pricing_unit=row["unit"], period=row["period"], scope_credit=row["credit"],
                          unit_rate_usd=dict(zip(CASES, rates, strict=True)), extended_usd=amounts,
                          references=refs, firm_offer_usd=None))
    return dict(lines=lines, period_subtotals_usd={p: {c: money(v) for c, v in cases.items()}
                                                  for p, cases in subtotals.items()},
                complete_local_price_usd=None, confirmed_scope_credits_usd=None)


def open_quantity_scenarios(factory_record, card):
    """Price only the additional work attached to unissued panel and cabinet counts."""
    drivers = factory_record["opening_drivers"]
    work = {r["id"]: r for r in factory_record["resources"]}

    def extension(rid, quantity, unit):
        rates = dict(zip(CASES, card["rates"][rid]["usd"], strict=True))
        return dict(resource_id=rid, lot_id=work[rid]["lot_id"], quantity=float(quantity), unit=unit,
                    unit_rate_usd=rates, extended_usd={c: money(decimal(quantity) * v) for c, v in rates.items()})

    scenarios = []
    panel_key = "station bay panels after plant and access openings"
    if drivers[panel_key] is None:
        with ZipFile(sourcing_estimates.PACKET) as archive:
            raw = archive.read("civil-article.json")
        if sha256(raw).hexdigest() != factory_record["drawing_member_sha256"]["civil-article.json"]:
            raise ValueError("Island template and workshop drawing edition differ")
        per_island = json.loads(raw)["station_panels"]["panels_per_island_template"]
        sites = drivers["passenger station sites"]
        panels = sites * per_island
        if panels != int(panels):
            raise ValueError("Panel scenario needs a whole number of panels")
        panels = int(panels)
        place, hook = work["civil-placement"], work["civil-panel-hook"]
        place_op, = (op for op in place["load"] if op["items"] == [panel_key])
        hook_op, = (op for op in hook["load"] if op["items"] == [panel_key])
        place_hours = decimal(place_op["hours"]) * decimal(place_op.get("multiplier", 1))
        moves = hook_op["multiplier"]
        move_hours = decimal(hook_op["hours"])
        shift_hours = decimal(hook["usable_hours_per_day"])
        handle_shifts = ceil(panels * moves * move_hours / shift_hours)
        scenarios.append(dict(label=f"{sites:g} nominal island templates, {panels} panels", driver=panel_key,
                              assumed_panels=panels, assumed_templates=sites, panels_per_template=per_island,
                              placement_hours_per_panel=float(place_hours), moves_per_panel=moves,
                              hours_per_move=float(move_hours), usable_hours_per_shift=float(shift_hours),
                              lines=[extension(place["id"], place_hours * panels, "placement hours"),
                                     extension(hook["id"], handle_shifts, "hook shifts")]))
    cabinet_key = "installed and tested rectifier cabinets"
    if drivers[cabinet_key] is None:
        sites = drivers["grid_sites"]
        for count in (1, 2):
            quantity = sites * count
            scenarios.append(dict(label=f"{quantity:g} cabinets at {count} per site", driver=cabinet_key,
                                  sites=sites, assumed_cabinets_per_site=count, assumed_cabinets=quantity,
                                  lines=[extension("wayside-power-test", quantity, "cabinet tests")]))
    for scenario in scenarios:
        scenario["additional_scope_usd"] = {
            case: money(sum(decimal(line["extended_usd"][case]) for line in scenario["lines"])) for case in CASES}
    return scenarios


def build(factory_record=None, estimate=None):
    if estimate is None:
        estimate = sourcing_estimates.estimate_lots()
    if factory_record is None:
        factory_record = factory.build(estimate)
    spec_bytes = (HERE / RATES).read_bytes()
    card = tomllib.loads(spec_bytes.decode())
    verify_edition(estimate)
    verify_edition(factory_record)
    for key in ("candidate_id", "frame_revision"):
        if len({estimate[key], factory_record[key], card[key]}) != 1:
            raise ValueError(f"Price card and production inputs differ on {key}")
    if (card["schema"] != "osr.airport.shop-rates.v1" or card["currency"] != "USD"
            or estimate["estimate_date"] != card["edition_date"]
            or factory_record["estimate_evaluation_id"] != estimate["evaluation_id"]
            or factory_record["opening_evaluation_id"] != estimate["opening_evaluation_id"]):
        raise ValueError("Incompatible commercial and factory editions")
    ids = [r["id"] for r in factory_record["resources"]]
    if len(ids) != len(set(ids)) or set(ids) != set(card["rates"]):
        raise ValueError("Factory and rate card require one matching line per resource")
    lots = {lot["lot_id"]: lot for lot in estimate["lots"]}
    subtotals = {}
    for period in (EQUIPMENT, SERVICE, UPKEEP):
        subtotals[period] = {case: Decimal(0) for case in CASES}
    credits = {}
    rows = []
    for resource in factory_record["resources"]:
        rid, lot_id = resource["id"], resource["lot_id"]
        rate = card["rates"][rid]
        refs = rate.get("refs", [])
        if (len(rate["usd"]) != 3 or list(sorted(rate["usd"])) != rate["usd"]
                or any(type(v) not in (int, float) or v <= 0 for v in rate["usd"])
                or not rate["scope"] or set(refs) - card["reference"].keys()):
            raise ValueError(f"Malformed unit rate or source for {rid}")
        quantity, unit, status = commercial_quantity(resource, rate, factory_record["opening_drivers"])
        period = EQUIPMENT if rate["basis"] == "units" else SERVICE
        amounts = None
        upkeep = None
        credit = credits.setdefault(lot_id, dict(
            planning_lot_base_usd=lots[lot_id]["base_usd"],
            priced_work_within_lot_usd=None,
            buyer_confirmed_overlap_credit_usd=None,
            uncovered_quantities=[],
        ))
        if status != "planned":
            credit["uncovered_quantities"].append(rid)
        if quantity is not None:
            amounts = {case: money(decimal(price) * decimal(quantity))
                       for case, price in zip(CASES, rate["usd"], strict=True)}
            if credit["priced_work_within_lot_usd"] is None:
                credit["priced_work_within_lot_usd"] = {case: Decimal(0) for case in CASES}
            for case, value in amounts.items():
                credit["priced_work_within_lot_usd"][case] += decimal(value)
                subtotals[period][case] += decimal(value)
            if period == EQUIPMENT:
                upkeep = {case: money(decimal(amounts[case]) * percent / 100)
                          for case, percent in zip(CASES, card["upkeep_percent"], strict=True)}
                for case, value in upkeep.items():
                    subtotals[UPKEEP][case] += decimal(value)
        rows.append(dict(
            id=rid, name=resource["name"], shop=resource["shop"], lot_id=lot_id,
            factory_units=resource["required_units"], minimum_units=resource["minimum_units"],
            factory_unit=resource["unit"], basis=rate["basis"], pricing_unit=unit,
            priced_quantity=quantity, quantity_status=status, period=period,
            unit_rate_usd=dict(zip(CASES, rate["usd"], strict=True)), extended_usd=amounts,
            annual_upkeep_usd=upkeep, scope=rate["scope"], references=refs,
            rate_status="engineering allowance", firm_offer_usd=None,
        ))
    for credit in credits.values():
        if credit["priced_work_within_lot_usd"] is not None:
            credit["priced_work_within_lot_usd"] = {k: money(v) for k, v in credit["priced_work_within_lot_usd"].items()}
    result = dict(
        schema="osr.airport.shop-costs.v1", edition_date=card["edition_date"], currency="constant 2026 USD",
        candidate_id=card["candidate_id"], frame_revision=card["frame_revision"],
        factory_evaluation_id=factory_record["evaluation_id"], estimate_evaluation_id=estimate["evaluation_id"],
        opening_evaluation_id=estimate["opening_evaluation_id"],
        source_sha256={RATES: sha256(spec_bytes).hexdigest(), "shop_costs.py": sha256(Path(__file__).read_bytes()).hexdigest()},
        references=card["reference"], resources=rows,
        period_subtotals_usd={p: {c: money(v) for c, v in cases.items()} for p, cases in subtotals.items()},
        lot_allocations=credits, upkeep_percent_by_case=dict(zip(CASES, card["upkeep_percent"], strict=True)),
        complete_workshop_installed_price_usd=None, international_freight_usd=None, import_duty_and_tax_usd=None,
        open_quantity_sensitivities=open_quantity_scenarios(factory_record, card),
        cam_and_training_scenario=workshop_scenario(card), approved_lot_credit_usd=None,
        physical_acceptance="open", fabrication_released=False,
    )
    result["evaluation_id"] = _id(result)
    return result


def fmt(number):
    return f"{number:,.3f}".rstrip("0").rstrip(".") if number else "0"


def report(record):
    lines = [
        "# Baghdad Airport workshop cost estimate", "",
        "Use this estimate to compare workshop equipment and services for the selected opening. The [factory specification](FACTORY-SPECIFICATION.md) gives the capacity, tooling and manufacturing routes. The editable [unit rates](shop-rates.toml) and [machine-readable estimate](shop-costs.json) identify each resource and its procurement lot.", "",
        "| Period and scope | Low USD | Base USD | High USD |", "|---|---:|---:|---:|"]
    for period, subtotal in record["period_subtotals_usd"].items():
        lines.append(f"| {period.capitalize()} | " + " | ".join(fmt(subtotal[k]) for k in CASES) + " |")
    lines += ["", "The first line buys dedicated or retained equipment once. The second pays for the opening production run, including subcontract work and hire. The third reserves 2%, 4% or 7% of retained equipment cost per year for maintenance and calibration while that equipment stays in use. Keep the annual reserve separate from purchase and from service rates that already cover the contractor’s equipment.", "",
              "These sums cover the quantities shown below. A minimum provision for a table or a known part of a contract gives a quantity lower bound. The low, base and high rates are estimating scenarios. Even the high subtotal leaves some scope unpriced. Freight to Iraq, customs and tax, major works, staffing outside service contracts, approval tests and contingency need separate returns. CAM and staff training have a separate scenario below. No complete installed price or committed purchase is available.", "",
              "## Purchase and booking quantities", "",
              "Hours include each production operation and its setup once. Grouped shifts round the total hours up at the usable hours per unit in the factory specification. Peak throughput determines parallel capacity. The supplier should return calendar days, minimum callouts, idle time and mobilisation for the actual booking sequence.", ""]
    for shop in dict.fromkeys(r["shop"] for r in record["resources"]):
        lines.extend([f"### {shop}", "", "| Resource | Capacity provision | Quantity priced | Unit rate USD low / base / high | Base extended USD | Scope and choice |",
                      "|---|---:|---:|---:|---:|---|"])
        for r in record["resources"]:
            if r["shop"] != shop:
                continue
            cap = r["factory_units"]
            capacity = fmt(cap) if cap is not None else (f"≥{r['minimum_units']}" if r["minimum_units"] else "Open")
            quantity = "Open" if r["priced_quantity"] is None else fmt(r["priced_quantity"])
            if r["quantity_status"] == "known-subset":
                quantity = "≥" + quantity
            unit_rates = " / ".join(fmt(r["unit_rate_usd"][case]) for case in CASES)
            base = fmt(r["extended_usd"]["base"]) if r["extended_usd"] is not None else "Open"
            lines.append(f"| {r['name']} | {capacity} {r['factory_unit']} | {quantity} {r['pricing_unit']} | {unit_rates} | {base} | {r['scope']} |")
        lines.append("")
    lines.extend(["## How to credit the existing procurement lots", "",
                  "The buyer compares the workshop lines below against matching scope inside the existing [lot estimates](sourcing-estimate.json). A supplier offering finished bogies, for example, may include machining and bearing fitting. Record who owns the tooling, how many operations the offer covers, its hire term, commercial exclusions and the credit accepted by the buyer. Keep unmatched scope in the original lot. An unreturned credit stays open. Adding these amounts to the opening budget would count the work twice.", "",
                  "| Parent lot | Existing base USD | Base work allocated here USD | Quantities still open or partial |",
                  "|---|---:|---:|---|"])
    for key, lot in record["lot_allocations"].items():
        subtotal = lot["priced_work_within_lot_usd"]
        base = fmt(subtotal["base"]) if subtotal is not None else "Open"
        lines.append(f"| {key} | {fmt(lot['planning_lot_base_usd'])} | {base} | {', '.join(lot['uncovered_quantities']) or '—'} |")
    if record["open_quantity_sensitivities"]:
        lines.extend(["", "## What the outstanding panel and cabinet counts could cost", "",
                      "These one-time scenarios price additional services within the existing lots. The [station enquiry](infrastructure/STATION.md) describes an uninterrupted 125 m island. Use one such template per passenger station to test the budget. For the power supplier, test one or two witnessed cabinets per grid site. Actual panel schedules and cabinet lists remain open.", "",
                      "| Alternative scope | Additional bookings | Low USD | Base USD | High USD |",
                      "|---|---|---:|---:|---:|"])
        for case in record["open_quantity_sensitivities"]:
            booked = ", ".join(f"{line['quantity']:,.8f}".rstrip("0").rstrip(".") + " " + line["unit"] for line in case["lines"])
            totals = " | ".join(fmt(case["additional_scope_usd"][c]) for c in CASES)
            lines.append(f"| {case['label']} | {booked} | {totals} |")
            if "assumed_panels" in case:
                panel_formula = (f"Multiply the issued panel count by {case['placement_hours_per_panel']} placement hours. "
                                 f"Multiply it by {case['moves_per_panel']} moves of {case['hours_per_move']:g} h each, "
                                 f"divide by {case['usable_hours_per_shift']:g} productive hours per shift and round up.")
        if any("assumed_panels" in case for case in record["open_quantity_sensitivities"]):
            lines.extend(["", panel_formula + " Extend each quantity at the corresponding hourly or shift rate above. "
                          "The four minimum tables and beam placement are already priced. This scenario excludes panel materials, finishing and installation. Credit shared crane time once."])
        lines.extend(["", "Multiply the supplier’s issued cabinet count by the per-cabinet witness rate. Use one cabinet scenario at a time. Replace the provisional quantities and confirm the service scope and lot credit before budgeting. The 41-line register and its subtotals exclude these scenarios."])
    scenario = record["cam_and_training_scenario"]
    lines.extend(["", "## CAD/CAM, first-off inspection and staff training", "",
                  "This separate scenario equips one programmer and one shop-floor reader, prepares one machine-specific post, and runs two supervised sessions for seven participants. The factory can reuse the [CAM handoff](cam/CAM.md) and the [instructor guide](training/INSTRUCTOR.md). A first-off booking allows two shop shifts and two inspections. The machine owner must confirm the actual part, fixture, machine travel, tooling, process and post before a trial.", "",
                  "| Period | Low USD | Base USD | High USD |", "|---|---:|---:|---:|"])
    for period, subtotal in scenario["period_subtotals_usd"].items():
        lines.append(f"| {period.capitalize()} | " + " | ".join(fmt(subtotal[c]) for c in CASES) + " |")
    lines.extend(["", "The commercial licence is an optional annual substitution. Use the open-source seat in the reference case. Staff attendance and owner witnessing are resource costs even where payroll covers them. Record the included amount before changing a parent budget.", "",
                  "| Work | Quantity and base rate USD | Base extended USD | Check for an existing provision |", "|---|---:|---:|---|"])
    for row in scenario["lines"]:
        lines.append(f"| {row['scope']} | {fmt(row['priced_quantity'])} {row['pricing_unit']} × {fmt(row['unit_rate_usd']['base'])} | {fmt(row['extended_usd']['base'])} | {row['scope_credit']} |")
    lines.extend(["", "The tooling lot also covers route and recovery equipment. The setout line covers survey and staging only. Ground treatment and foundation construction require a site return. Station panel and rectifier cabinet production require issued item counts. All resource IDs, including priced lines, retain the technical limits and open items in their factory specifications.", "",
                  "## Market observations", "",
                  f"Prices and descriptions reviewed {record['edition_date']}. Supplier list prices below apply to their stated markets and configurations. Each workshop rate is an engineering allowance, including the rows that use a catalogue price as a benchmark. Obtain dated local quotations with currency, delivery, installation, warranty and validity.", ""])
    for ref in record["references"].values():
        lines.append(f"- {ref['observation']} [{ref['title']}]({ref['url']})")
    lines.extend(["", f"Factory evaluation `{record['factory_evaluation_id']}`. Buyer estimate `{record['estimate_evaluation_id']}`. Workshop estimate `{record['evaluation_id']}`.", "",
                  "Rebuild locally with `python3 -m cities.Baghdad.engineering.prototype.shop_costs --publish`. Check the published files with the same command and `--check`.", ""])
    return "\n".join(lines)


def artifacts(factory_record=None, estimate=None):
    record = build(factory_record, estimate)
    return {REGISTER: (json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode(),
            REPORT: report(record).encode()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--publish", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = artifacts()
    if args.publish:
        with disk_reservation(sourcing_estimates.ROOT, HERE, "Airport workshop cost files", 2 << 20) as lease:
            for name, raw in files.items():
                check_disk_reservation(lease)
                write_atomic(HERE / name, raw)
    elif any(not (HERE / name).is_file() or (HERE / name).read_bytes() != raw for name, raw in files.items()):
        raise SystemExit("Regenerate the Airport workshop cost files for the current rates and factory edition")
    print(json.loads(files[REGISTER])["evaluation_id"])


if __name__ == "__main__":
    main()
