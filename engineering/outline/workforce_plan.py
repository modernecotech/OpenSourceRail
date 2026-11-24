"""Prepare a shift-level workload from the published railway delivery study.

The input preserves three distinct periods: the procurement/delivery programme,
one initial training intake, and an operating year (or commissioning equivalent).
Wage amounts are paid-hour allowances in constant 2026 USD. Estimated attendance
and relief hours are attached to the task account that would buy them.
"""

import argparse
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from math import ceil
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
import tomllib

ROOT = Path(__file__).resolve().parents[2]
QUANTITIES = "docs/operator-review/delivery/quantities.json"
DELIVERY_GUIDE = "docs/operator-review/delivery/README.md"
SYSTEM = "cities/Baghdad/system-results.json"
BAGHDAD = "cities/Baghdad/system.toml"
CORE = "docs/reference-v07/digital/production/handoff.json"
NETWORKS = ("first", "metropolitan", "metropolitan-mainlines", "core")
MODES = ("goa4", "supervised", "assisted")
CASES = ("low", "base", "high")
OPERATING = "Operating year"
TRAINING = "Initial operator training"
VEHICLE = "Vehicle final assembly"
YARD = "Precast production"
ERECTION = "Site erection"
DAY_SHIFTS = (("Early", 360, 480), ("Late", 840, 480), ("Night", 1320, 480))
PUBLIC_SHIFTS = (*DAY_SHIFTS[:2], ("Night public service", 1320, 120))
SENIOR = "onboard commissioning supervisors"
RATES = (
    "October 2026 Baghdad construction wage proxies, rail recruitment/shift premium, "
    "employer contribution, and IQD conversion from the delivery study"
)
OPERATING_POOLS = {
    "station duty and passenger assistance": (PUBLIC_SHIFTS, (1, 1, 1)),
    "station security and cleaning": (PUBLIC_SHIFTS, (1, 1, 1)),
    "OCC control, traction, incidents and information": (DAY_SHIFTS, (1, 1, 1)),
    "depot rolling-stock technicians": (DAY_SHIFTS, (2, 2, 1)),
    "civil, track and power response": (DAY_SHIFTS, (1, 1, 1)),
}
LINE_SUPPORT = (
    ("Line coordinator", 1, 80_000),
    ("Production quality inspector", 1, 75_000),
    ("Stores coordinator", 1, 25_000),
    ("Line materials handler", 1, 35_000),
)
YARD_CREW = (
    ("Steel and strand", 4, 75_000),
    ("Mould and stressing", 4, 75_000),
    ("Batching and placement", 3, 35_000),
    ("Crane and yard transport", 3, 75_000),
    ("Quality and laboratory", 2, 80_000),
    ("Yard foreperson", 1, 75_000),
    ("Yard stores coordinator", 1, 25_000),
)
ERECTION_CREW = (
    ("Front supervisor", 1, 80_000),
    ("Crane operator", 1, 75_000),
    ("Rigging", 2, 75_000),
    ("Alignment and installation", 2, 75_000),
    ("Traffic and access", 2, 35_000),
)


def _whole(number):
    return int(Decimal(str(number)).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _split(total, weights):
    """Allocate whole minutes without losing hours to independent rounding."""
    cumulative = 0
    previous = 0
    whole = sum(weights)
    for weight in weights:
        cumulative += weight
        next_total = total * cumulative // whole
        yield next_total - previous
        previous = next_total


def _rate(prices, *, role=None, daily_iqd=None):
    if prices is None:
        return None, "Pay open for this location. Obtain loaded wages and shift premiums from the buyer."
    if role is not None:
        hours = prices["paid_days_year"] * 8
        return [
            _whole(prices["cases"][case]["loaded_usd_per_fte_year"][role] * 100 / hours)
            for case in CASES
        ], RATES
    multiplier = (1 + prices["employer_social_insurance_share"]) / prices["currency"]["iqd_per_usd"]
    cents = daily_iqd * 100 * multiplier / 8
    return [_whole(cents * (1 + prices["cases"][case]["rail_and_shift_premium"])) for case in CASES], (
        f"{RATES}; grade blend IQD {daily_iqd:,.0f} per paid day (planning hypothesis)"
    )


def _row(work_id, phase, role, shift, *, posts, days, required, paid, utilisation, rates, account):
    label, start, minutes = shift
    values, basis = rates
    return {
        "work_id": work_id, "phase": phase, "role": role, "shift": label,
        "start_minute": start, "minutes_per_shift": minutes, "days": days,
        "assigned_posts": posts, "required_minutes": required, "paid_minutes": paid,
        "utilisation_bps": utilisation, "rates_cents_per_hour": values, "rate_basis": basis,
        "cost_account": account,
    }


def _operating_rows(study, mode, hours, account):
    """Place published role totals in repeat shifts with one relief pool per role."""
    roster = study["workforce_scenarios"][mode]
    prices = study.get("iraq_payroll")
    calendar_hours = 2080 if prices is None else prices["paid_days_year"] * 8
    rows = []
    for index, (role, annual_hours) in enumerate(roster["duty_hours_per_year"].items(), 1):
        required = _whole(annual_hours * 60)
        paid = roster["posts_fte"][role] * calendar_hours * 60
        rates = _rate(prices, role=role)
        if role == "planning, payroll, stores and trainers":
            shifts = (("Office", 480, 480),)
            weights = (1,)
            days = 215  # rosterable workdays; salary covers the full paid year
        elif role == roster["onboard_role"]:
            days = 365
            shifts = PUBLIC_SHIFTS
            weights = hours
        else:
            shifts, density = OPERATING_POOLS[role]
            weights = [s[2] * n for s, n in zip(shifts, density, strict=True)]
            days = 365

        for number, (shift, duty, pay) in enumerate(
            zip(shifts, _split(required, weights), _split(paid, weights), strict=True), 1
        ):
            capacity = shift[2] * days
            average_posts = ceil(duty / capacity)
            rows.append(_row(
                f"operate-{index}-{number}", OPERATING, role, shift, posts=average_posts, days=days,
                required=duty, paid=pay, utilisation=10_000, rates=rates, account=account,
            ))
    return rows


def _training_rows(study):
    """Price the baseline GoA4 intake with the same cohort bounds as the delivery study."""
    prices = study.get("iraq_payroll")
    posts = study["workforce_scenarios"]["goa4"]["posts_fte"]
    account = "Commissioning · one initial GoA4 operating intake"
    rows = []
    for group, description in (("class", "Classroom / simulator"), ("field", "Mentored field duty")):
        shift = (f"Unscheduled {description.lower()}", None, None)
        for number, (role, people) in enumerate(posts.items(), 1):
            if not people:
                continue
            minutes = people * 80 * 60
            rows.append(_row(
                f"learn-{group}-{number}", TRAINING, f"{role} · learner", shift,
                posts=None, days=None, required=minutes, paid=minutes, utilisation=10_000,
                rates=_rate(prices, role=role), account=account,
            ))
        limit = 12 if group == "class" else 4
        minutes = 80 * 60 * ceil(sum(posts.values()) / limit)
        rows.append(_row(
            f"teach-{group}", TRAINING, "Instructor" if group == "class" else "Field mentor", shift,
            posts=None, days=None, required=minutes, paid=minutes, utilisation=10_000,
            rates=_rate(prices, role=SENIOR), account=account,
        ))
    return rows


def _factory_rows(study):
    """Price staffed vehicle-line windows, including capacity that may be idle."""
    prices = study.get("iraq_payroll")
    vehicle = study["vehicle"]
    days = vehicle["scheduled_workdays"]
    lines = vehicle["lines"]
    workday = ("Factory day", 420, 480)
    stages = vehicle["hours_per_car_by_stage"]
    wage_by_stage = vehicle.get("direct_assembly_labour", {}).get("proxy_daily_iqd_by_stage", {})
    rows = []
    for index, (role, hours) in enumerate(stages.items(), 1):
        posts = vehicle["direct_posts_by_stage"][role] * lines
        paid = None if prices is None else _whole(posts * days * 480 * prices["paid_days_year"] / 250)
        rows.append(_row(
            f"assembly-{index}", VEHICLE, role, workday, posts=posts, days=days,
            required=vehicle["cars"] * hours * 60, paid=paid, utilisation=6800,
            rates=_rate(prices, daily_iqd=wage_by_stage.get(role)), account="Fleet purchase · staffed assembly window",
        ))
    for index, (role, count, wage) in enumerate(LINE_SUPPORT, 1):
        posts = count * lines
        paid = None if prices is None else _whole(posts * days * 480 * prices["paid_days_year"] / 250)
        rows.append(_row(
            f"line-support-{index}", VEHICLE, role, workday, posts=posts, days=days,
            required=posts * days * 480, paid=paid, utilisation=10_000,
            rates=_rate(prices, daily_iqd=wage), account="Fleet purchase · factory support posts",
        ))
    return rows


def _civil_rows(study, calendars):
    """Screen crews against declared daily output and dated production availability."""
    civil = study["civil"]
    prices = study.get("iraq_payroll")
    rows = []
    teams = (("yard", YARD, YARD_CREW, civil["yards"]), ("erect", ERECTION, ERECTION_CREW, civil["erection_fronts"]))
    for prefix, phase, grades, teams_count in teams:
        days, utilisation, units_per_day = calendars[prefix]
        for index, (role, crew, wage) in enumerate(grades, 1):
            posts = crew * teams_count
            demand = ceil(civil["beams"] * crew * 480 / units_per_day)
            paid = None if prices is None else _whole(days * posts * 480 * prices["paid_days_year"] / 250)
            rows.append(_row(
                f"{prefix}-{index}", phase, role, ("Civil day · possession times open", 420, 480),
                posts=posts, days=days, required=demand, paid=paid, utilisation=utilisation,
                rates=_rate(prices, daily_iqd=wage), account=f"Elevated civil · {phase.lower()} crew allowance",
            ))
    return rows


def _gaps(network, mode, capital):
    project_scope = (
        f" Scope comparator from the selected infrastructure estimate, in US$m at its published basis. "
        f"Design assurance {capital['design_assurance']:,.2f}, land/utilities/disruption "
        f"{capital['land_utilities_disruption']:,.2f}."
        if capital else ""
    )
    site_scope = (
        f" Same-candidate scope comparators include elevated civil {capital['elevated_civil']:,.2f}, "
        f"stations/access {capital['stations_access']:,.2f}, track/walkways {capital['track_walkways']:,.2f}, "
        f"traction supply {capital['line_traction_supply']:,.2f}, signalling/comms "
        f"{capital['signalling_comms']:,.2f} and depots/control {capital['depots_control']:,.2f} US$m."
        if capital else ""
    )
    commissioning_scope = (
        f" The testing/commissioning envelope is {capital['testing_commissioning']:,.2f} US$m."
        if capital else ""
    )
    records = [
        (OPERATING, "Timetabled relief, peak coverage, staff breaks, accessibility and rescue",
         "Operating and safety directors", "Price actual duty diagrams, mobilisation and specialist response separately; annual pools only."),
        (TRAINING, "Classroom capacity, mentors, assessors, bilingual courses and operator competence",
         "HR and assessment leads", "Price facilities, independent assessments, simulators, travel and backfill; intake labour only is priced."),
        ("Programme definition", "Survey, access, design review, utility diversion, permits and programme management",
         "Owner and designer", "Use matched surveys and engineering tenders. Dates and staff quantities await the issue scope." + project_scope),
        ("Site construction", "Foundations, stations, trackwork, traction electrical, controls and depot construction",
         "Civil and systems contractors", "Use candidate-specific work breakdown and priced bills. Crew rows cover beam production and erection." + site_scope),
        (YARD, "Transport, stock imbalance, rejected batches, contractor supervision and night watch",
         "Yard and logistics leads", "Separate labour after mapping operated crane and haul contracts to the crew allowance."),
        (ERECTION, "Possessions, closures, relief, lifting design and subcontract staff",
         "Installation planner", "Return actual front bookings and split labour from hire; do not add the allowance to an operated crane quote."),
        (VEHICLE, "Component factories, supplier lead time, specialised shops, rework and integrated qualification",
         "Vehicle supply and quality leads", "Use measured times and matched fleet or supplier lots; the staffing allowance covers final assembly and support."),
        ("Commissioning", "System tests, transition, trials and independent review",
         "Operator and integrator", "Set trial dates and approval work. Use supervisory payroll for the actual trial period." + commissioning_scope),
    ]
    if mode != "goa4":
        records.append((OPERATING, "Attended train and relief turns by operator, route and shift",
                        "Duty planner", "Shift distribution is an exposure assumption, until the operator assigns actual turns."))
    if network == "metropolitan":
        records.append((OPERATING, "Held service groups M01, M02, M04 and M09",
                        "Network planners", "Existing source allows peak-fleet proxies. Replace these once the train paths and dwell times are verified."))
    if network == "core":
        records.append(("Payroll", "Location-specific loaded wages and paid civil/production employment calendar",
                        "Buyer and employer", "Obtain pay/leave rules and a dated contract. Keep this non-localised comparison unpriced."))
    return [dict(phase=phase, work=work, owner=owner, cost_basis=basis) for phase, work, owner, basis in records]


def build_plan(network="first", mode="goa4", root=ROOT):
    root = Path(root)
    sources = {}

    def read(path):
        raw = (root / path).read_bytes()
        sources[path] = hashlib.sha256(raw).hexdigest()
        return tomllib.loads(raw.decode()) if path.endswith(".toml") else json.loads(raw)

    quantities = read(QUANTITIES)
    for path, expected in quantities["source_sha256"].items():
        actual = hashlib.sha256((root / path).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Regenerate the published delivery quantities after changing {path}")
        sources[path] = actual
    sources["engineering/outline/workforce_plan.py"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    delivery = quantities["studies"]
    study = {**delivery, **quantities["operating_options"]}[network]
    production = delivery["metropolitan"] if network == "metropolitan-mainlines" else study
    if production["source_physical_id"] != study["source_physical_id"]:
        raise ValueError("The production and operating selections use different physical candidates")
    sources[DELIVERY_GUIDE] = hashlib.sha256((root / DELIVERY_GUIDE).read_bytes()).hexdigest()

    capital = None
    if network == "core":
        weights = (8, 8, 2)  # service window proportions until duty turns are assigned
        calendar = {stage["stage"]: stage for stage in read(CORE)["schedule"]["stages"]}
        calendars = {
            "yard": (calendar["beam-factory"]["duration_months"] * 20, 10_000, 8),
            "erect": (calendar["beam-erection"]["duration_months"] * 20, 10_000, 8),
        }
    else:
        config = read(BAGHDAD)
        departures = config["service_plan"]["departures_per_hour_direction"]
        if len(departures) != 18:
            raise ValueError("An 18-hour departure profile is required for the proposed public shifts")
        weights = (sum(departures[:8]), sum(departures[8:16]), sum(departures[16:]))
        if min(weights) <= 0:
            raise ValueError("Each proposed public shift needs a positive departure weight")
        key = "metropolitan" if network == "metropolitan-mainlines" else network
        system = read(SYSTEM)["networks"][key]
        if (system["selected_candidate_id"] != study["source_physical_id"]
                or system["selected_evaluation_id"] != study["source_evaluation_id"]):
            raise ValueError("Civil calendar belongs to a different physical candidate")
        capital = system["selected_capital_scope_usd_m"]
        civil = system["selected_civil_delivery"]
        days = civil["nominal_workdays_per_yard_or_front"]
        availability = int(10_000 * civil["effective_workdays_per_yard_or_front"] / days)
        rates = config["civil_rates"]
        calendars = {
            "yard": (days, availability, rates["factory_beams_per_workday_per_yard"]),
            "erect": (days, availability, rates["erection_lifts_per_workday_per_front"]),
        }
    account = ("Trial commissioning · annual equivalent" if mode == "supervised"
               else "Operating payroll · annual equivalent")
    rows = [
        *_operating_rows(study, mode, weights, account),
        *_training_rows(production),
        *_factory_rows(production),
        *_civil_rows(production, calendars),
    ]
    scope = {
        "network": network, "workforce_mode": mode, "label": study["workforce_scenarios"][mode]["name"],
        "candidate_id": study["source_physical_id"], "source_evaluation_id": study["source_evaluation_id"],
        "diagram_evaluation_id": study["source_diagram_evaluation_id"],
        "currency": "constant 2026 USD",
        "annual_paid_hours_per_fte": 2080, "annual_rosterable_hours_per_fte": 1720,
        "operating_establishment_fte": study["workforce_scenarios"][mode]["total_fte"],
        "train_duty_basis": study["workforce_scenarios"][mode]["train_duty_basis"],
        "calendar_basis": "Repeated day patterns in local time. Fixed 06:00 public start is a planning assumption."
                          " Annual wages include relief from the source role pool. Civil crews are budgeted over the full"
                          " reservation window, with effective availability from the source plan.",
        "cost_basis": "Programme labour, intake and operating-year payroll have separate periods. These are"
                      " allowances inside the fleet, civil, commissioning and operating accounts. Match contract"
                      " exclusions and labour credits before substituting them.",
        "scope_boundaries": "No named staff, awarded shifts or authorisation. Peak role/shift coverage is a workload screen."
                            " Onboard scenarios distribute annual duty using the departure profile where available.",
    }
    plan = {
        "schema": "osr-workforce-plan/1", "scope": scope, "source_sha256": sources,
        "rows": rows, "gaps": _gaps(network, mode, capital),
    }
    plan["plan_id"] = hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network", choices=NETWORKS, default="first")
    parser.add_argument("--mode", choices=MODES, default="goa4")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    content = json.dumps(build_plan(args.network, args.mode), indent=2, allow_nan=False) + "\n"
    if args.output:
        with NamedTemporaryFile("w", encoding="utf-8", dir=args.output.parent, delete=False) as stream:
            temporary = Path(stream.name)
            try:
                stream.write(content)
                stream.flush()
                os.replace(temporary, args.output)
            finally:
                temporary.unlink(missing_ok=True)
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
