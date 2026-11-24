"""Resize the dated feeder planning rates for an issued Airport circuit."""

from hashlib import sha256
import json
from math import isclose, isfinite
from pathlib import Path
import tomllib

from . import motion_power, scenario


CASES = ("low", "base", "high")
PRICE_REGISTER = scenario.PROTO / "sourcing-estimate.json"
SYSTEM = scenario.CITY / "system.toml"
UNPRICED = (
    "utility tie-in design, offsite reinforcements and utility service charges",
    "installed equipment specifications, rated hot-circuit protection and demonstrated isolation",
    "site-specific foundations, clearances, access, earthing and intertrack leakage measures",
    "commissioning and any maintenance shared with other cash lots",
    "feeder replacements by equipment population and operating year",
)


def finite(value, label):
    if type(value) in (float, int) and value >= 0:
        try:
            if isfinite(value):
                return value
        except OverflowError:
            pass
    raise ValueError(f"Expected a finite nonnegative {label}")


def compare_operating_duties(days, high_mass, assessments):
    """Test the ordinary and degraded passenger offers on their actual outcomes."""
    unmatched = []
    cases = {name: [r for r in days if r["condition"] == name] for name in motion_power.CONDITIONS}
    cases["high_mass_combined"] = [r for r in high_mass if r["condition"] == "combined"]
    for label, rows in cases.items():
        pair = [r for r in rows if r["topology"] in assessments]
        if len(pair) != 2 or {r["topology"] for r in pair} != set(assessments):
            raise ValueError(f"Price comparison requires both physical layouts for {label}")
        if any(r["candidate_id"] != assessments[r["topology"]]["assemblies"]["feeder"] for r in pair):
            raise ValueError(f"Price comparison received another physical design for {label}")
        a, b = pair
        if (not all(r["numerical_valid"] and r["completed"] == r["booked"] for r in pair)
                or a["booked"] != b["booked"] or not isclose(a["served"], b["served"], abs_tol=.01)):
            unmatched.append(label)
    return dict(unmatched_duties=unmatched,
                failed_operating_layouts=sorted(name for name, assessment in assessments.items()
                                               if assessment["operating_screen"] != "passed"))


def priced_cash_gap(production, comparison, operating_comparison):
    first, second = (row["inputs"] for row in (production, comparison))
    scope_keys = ("alignment_id", "demand_evaluation_id", "vehicle_candidate_id", "vehicle_duty_id")
    if first["feeder"]["name"] == second["feeder"]["name"] or any(first[k] != second[k] for k in scope_keys):
        raise ValueError("Priced PV comparison requires different feeders for the same alignment, train, duty and requested demand")
    op_a, op_b = (row["operation_basis"] for row in (production, comparison))
    ordinary = all(op["working_day_completed"] for op in (op_a, op_b)) and all(
        isclose(op_a[key], op_b[key], rel_tol=1e-8, abs_tol=.01)
        for key in ("operated_annual_train_km", "annual_completed_journeys", "annual_paid_journeys_proxy")
    )
    matched_cost_scope = (first["civil_row_id"] == second["civil_row_id"]
                          and production["cash"]["scope"]["unpriced_lots_by_group"]
                          == comparison["cash"]["scope"]["unpriced_lots_by_group"]
                          and all(production["cash"][key] == comparison["cash"][key]
                                  for key in ("constant_currency", "discount_rate_real", "service_start_year")))
    comparable = (None if operating_comparison is None else ordinary
                  and not operating_comparison["unmatched_duties"] and not operating_comparison["failed_operating_layouts"])
    own_pv, other_pv = (finite(row["cash"]["profiles"]["base"]["priced_30y_pv_usd"], "priced PV")
                        for row in (production, comparison))
    return dict(other_layout=second["feeder"]["name"], base_priced_pv_difference_usd=own_pv - other_pv,
                ordinary_service_comparable=ordinary, operating_comparison=operating_comparison,
                achieved_service_comparable=comparable, matched_pricing_boundary=matched_cost_scope,
                extra_unpriced_pv_own_minus_other_for_equal_totals_usd=other_pv - own_pv if comparable and matched_cost_scope else None,
                scope=("Arithmetic on priced cash with matched modelled service and priced periods. Site and equipment evidence remain open."
                       if comparable and matched_cost_scope else "Partial cash amounts only. Establish equivalent service across the declared duties and match the pricing boundary before calculating parity."))


def evaluate(production, duties, *, comparison=None, operating_comparison=None):
    """Price only attributable rate-sensitivity scope. Leave the owner cash ledger alone."""
    context = production["inputs"]
    design = context["feeder"]
    layout = design["name"]
    physical = dict(alignment_id=context["alignment_id"], feeder=design)
    physical_id = scenario._id(physical)
    quantities = production["quantities"]
    sites = design["sites"]
    track_km = finite(quantities["track_km"], "track-km")
    count = len(sites)
    paths = design["paths"]
    if (layout not in ("radial30", "paired6") or paths != (2 if layout == "paired6" else 1)
            or count < 2 or quantities["grid_sites"] != count
            or sites[0] != 0 or any(not 0 <= a < b for a, b in zip(sites, sites[1:]))
            or not isclose(sites[-1], track_km * 500, rel_tol=1e-10)):
        raise ValueError("Planning sensitivity requires matching issued sites, track length and topology")
    if any(row["feeder_physical_id"] != physical_id or scenario._id(row["feeder_physical"]) != physical_id
           for row in duties):
        raise ValueError("Planning sensitivity needs duty replays for the exact physical feeder")
    valid_peaks = {row["evaluation_id"]: finite(row["peak_site_ka"], "source peak current")
                   for row in duties if row["numerical_valid"] and row["peak_site_ka"] is not None}
    governing_id = max(valid_peaks, key=valid_peaks.get) if valid_peaks else None

    source_peak = valid_peaks.get(governing_id)
    # The 1.5 kV value is the declared nominal voltage in the retained design.
    # Use it as a common MW pricing scalar for the replay current envelope.
    radial = motion_power.reference()[3]["radial30"]["design"]
    nominal_kv = finite(radial["source_kv"], "nominal source voltage")
    dc_mw_proxy = nominal_kv * source_peak if source_peak is not None else None
    register_bytes, system_bytes = (path.read_bytes() for path in (PRICE_REGISTER, SYSTEM))
    register_id, system_id = (sha256(raw).hexdigest() for raw in (register_bytes, system_bytes))
    if (production["source_sha256"]["sourcing-estimate.json"] != register_id
            or production["source_sha256"]["cities/Baghdad/system.toml"] != system_id):
        raise ValueError("Feeder sensitivity source rates differ from the production issue")
    register = json.loads(register_bytes)
    cfg = tomllib.loads(system_bytes.decode())
    rates = cfg["power_price_allowances_usd_m"]
    site_base = cfg["capital_rates_usd_m"]["traction_supply_site"]
    line_rate = rates["protected_conductor_per_track_km"]
    switch_rate = rates["protected_section_switchgear_each"]
    outgoing = 4 * (count - 1)
    ties = 2 * (count - 1)
    branch_points = 4 * outgoing if paths == 2 else 0
    factor = finite(design["trunk_factor"], "trunk resistance multiplier")
    outward = finite(design["outward"], "outward resistance") * factor
    return_path = finite(design["return_path"], "return resistance") * factor
    if min(outward, return_path) <= 0:
        raise ValueError("The conductor pricing proxy requires positive loop resistances")
    conductance_factor = max(radial["outward_ohm_per_km"] / outward, radial["return_ohm_per_km"] / return_path)
    base_site_usd_m = (site_base + max(0., dc_mw_proxy - rates["traction_supply_site_base_rating_mw"])
                       * rates["additional_site_capacity_per_mw"] if dc_mw_proxy is not None else None)
    results = {}
    for case, share, site_factor, switch_factor, branch_factor, upkeep in zip(
        CASES, (.25, .40, .60), (.85, 1.10, 1.40), (1., 1.4, 2.), (.10, .20, .40), (.005, .01, .02),
        strict=True,
    ):
        if paths == 1:
            site_factor = switch_factor = 1.
        path_factor = share * conductance_factor * paths + (1 - share) * (1 + paths) / 2
        parts = dict(
            railway_side_supply_sites_and_plant=(count * base_site_usd_m * site_factor * 1e6
                                                  if base_site_usd_m is not None else None),
            protected_positive_and_return_paths=track_km * line_rate * path_factor * 1e6,
            breakers_ties_and_branch_points=((outgoing + ties) * switch_factor + branch_points * branch_factor)
                                             * switch_rate * 1e6,
        )
        subtotal = finite(sum(amount for amount in parts.values() if amount is not None), "rail-side USD subtotal")
        results[case] = dict(parts_usd=parts, known_rail_side_direct_subtotal_usd=subtotal,
                             rail_side_annual_upkeep_usd=subtotal * upkeep if base_site_usd_m is not None else None,
                             upkeep_share=upkeep)
    gap = priced_cash_gap(production, comparison, operating_comparison) if comparison is not None else None
    record = dict(
        status="rail-side planning sensitivity outside priced cash", layout=layout, feeder_physical_id=physical_id,
        source_date=register["estimate_date"], price_basis=register["price_basis"], cases=results,
        source_sha256={str(path.relative_to(scenario.ROOT)): fingerprint
                       for path, fingerprint in ((PRICE_REGISTER, register_id), (SYSTEM, system_id),
                                                 (Path(__file__).resolve(), sha256(Path(__file__).read_bytes()).hexdigest()))},
        quantities=dict(dc_source_groups=count, protected_track_km=track_km, parallel_paths=paths,
                        outgoing_circuits=outgoing, midpoint_ties=ties, branch_disconnect_and_test_points=branch_points),
        duty_proxy=dict(governing_evaluation_id=governing_id, peak_site_ka=source_peak, nominal_source_kv=nominal_kv,
                        dc_mw_pricing_proxy=dc_mw_proxy, installed_nameplate_mw=None,
                        evaluated_duties=[row["evaluation_id"] for row in duties],
                        basis="Maximum reported source peak across supplied numerically valid replays at nominal DC voltage. Installed duty and safety require site-specific equipment returns."),
        conductor_proxy=dict(conductance_factor=conductance_factor, installed_conductor_area_mm2=None,
                             basis="Archived conductor cost split and resistance ratio stress. Material quantity and ampacity require product data."),
        case_basis=("Archived line, site and switch allowances are fixed at the reference radial resistance. "
                    "Upkeep varies at the published 0.5%, 1% and 2% fractions."
                    if paths == 1 else
                    "Published low, base and high conductor allocations, site, switch and branch-point factors "
                    "and upkeep fractions. These assumptions describe price sensitivity."),
        offsite_utility_usd=None, installed_package_usd=None, renewal_usd=None, unresolved_scope=list(UNPRICED),
        priced_cash_break_even=gap,
    )
    record["sensitivity_id"] = scenario._id(record)
    return record
