"""Translate the Baghdad crowd train across a family of independent-pier box spans."""

import argparse
import json
import math
from pathlib import Path
import sys
import tomllib

from develop_civil import CITY, DIR, PARENT, box_screen, evaluate as reference_section, hash_file, identity

sys.path.insert(0, str(PARENT))
from develop import moving_load

ROOT = CITY.parents[1]
LENGTHS_M = (10, 20, 25, 30)
# Two quotation sensitivities. Neither value is a supplier or test result.
REFERENCE_CHART_T_AT_12_M = 60.0
TRANSFER_TO_EFFECTIVE_LOSS_FRACTION = 0.20


def monthly_yard_demand(delivery, stock_t):
    """Price a resource held throughout its first-to-last active month."""
    months = delivery["monthly_delivery"]["months"]
    yards = delivery["factory_yards_needed_at_declared_rate"]
    fronts = delivery["erection_fronts_needed_at_declared_rate"]

    first_cast = next(i for i, month in enumerate(months) if month["beams_cast"])
    lift_months = [i for i, month in enumerate(months) if month["beams_erected"]]

    def stock(month):
        return month["cast_beams_awaiting_release"] + month["released_beams_awaiting_erection"]

    peak = max(months, key=stock)
    return dict(yards=yards, fronts=fronts, yard_months=yards * (lift_months[-1] - first_cast + 1),
                front_months=fronts * (lift_months[-1] - lift_months[0] + 1),
                peak_month_end_units=stock(peak), peak_month_end_stock_t=stock(peak) * stock_t,
                peak_month=f"{peak['year']}-{peak['month']:02d}")


def evaluate():
    base = reference_section()
    if base != json.loads((DIR / "section-results.json").read_bytes()):
        raise ValueError("Rebuild the Baghdad civil parent")
    schedule = json.loads((PARENT / "schedule.json").read_bytes())
    system = json.loads((CITY / "system-results.json").read_bytes())
    for path, fingerprint in system["source_sha256"].items():
        if hash_file(ROOT / path) != fingerprint:
            raise ValueError(f"Stale first-network estimate input {path}")
    network = system["networks"]["first"]
    cases = network["civil_cases"]
    base_case = cases["10m-separate"]
    if (network["selected_digital_civil_family"] != "10m-separate"
            or network["digital_cost_leader"] != "protected_conductor"
            or network["selected_candidate_id"] != schedule["parent_selected_candidate_id"]
            or network["selected_evaluation_id"] != schedule["parent_evaluation_id"]):
        raise ValueError("Different parent selection or pricing basis")
    cfg = tomllib.loads((DIR / "concept.toml").read_text())
    quote = tomllib.loads((PARENT / "quotation.toml").read_text())
    template = schedule["viaduct"]
    train = schedule["train"]
    power = network["power_cases"]["protected_conductor"]
    axles = [car + offset for car in train["car_centres_m"] for offset in train["body_axle_x_m"]]
    if len(axles) != power["driven_axles"]:
        raise ValueError("Axle count differs from the selected train")
    axle_kn = power["train_crowd_mass_t"] * cfg["materials"]["gravity_m_s2"] / len(axles)
    reference_length = template["beam_stock_length_m"]
    inset = quote["civil_seat"]["longitudinal_inset_m"]
    lateral = quote["civil_seat"]["lateral_m"]
    step = quote["screen"]["load_step_m"]
    rows = []
    for length in LENGTHS_M:
        case = cases[f"{length}m-separate"]
        bearing_span = length - 2 * inset
        live = moving_load(axles, bearing_span, step, axle_kn, overhang=inset)
        seats = [[x, y] for x in (inset, length - inset) for y in (-lateral, lateral)]
        track = dict(beam_stock_length_m=length, effective_span_m_hypothesis=bearing_span,
                     bearing_seat_xy_m_from_stock_end=seats, moving_gravity_only=live)
        box = dict(cfg["box"])
        box["lift_pick_inset_m"] *= length / reference_length
        actions = box_screen(box, cfg["materials"], track, cfg["pier"])
        if length == reference_length and actions != base["track"]:
            raise ValueError("10 m comparison must reproduce the Baghdad reference box")
        # Compression positive. Constant eccentric tendon at centre, symmetric picks.
        # Uncracked uniform midspan section; forces at full transfer before losses.
        transfer_kn = actions["effective_axial_force_for_zero_bottom_stress_kn"] / (1 - TRANSFER_TO_EFFECTIVE_LOSS_FRACTION)
        modulus = 2 * actions["midspan_I_m4"] / box["depth_m"]
        e = box["effective_tendon_eccentricity_m"]
        centre_bending = (actions["stock_lift_midspan_knm"] - transfer_kn * e) / modulus
        uniform = transfer_kn / actions["midspan_area_m2"]
        headroom = base_case["direct_elevated_civil_usd_m"] - case["direct_elevated_civil_usd_m"]
        pick_bending = (actions["stock_lift_hogging_knm"] - transfer_kn * e) / modulus
        physical = (base["physical_id"] if length == reference_length else
                    identity([base["physical_id"], case["civil_option_physical_id"], length, seats, box["lift_pick_inset_m"]]))
        rows.append(dict(length_m=length, physical_id=physical,
                         pricing_parent=case["civil_option_physical_id"], sampled_live=live, actions=actions,
                         transfer_lift_centre_top_compression_mpa=(uniform + centre_bending) / 1000,
                         transfer_lift_centre_bottom_compression_mpa=(uniform - centre_bending) / 1000,
                         transfer_lift_pick_top_compression_mpa=(uniform + pick_bending) / 1000,
                         transfer_lift_pick_bottom_compression_mpa=(uniform - pick_bending) / 1000,
                         stock_only_chart_balance_t=REFERENCE_CHART_T_AT_12_M - actions["equivalent_stock_t"],
                         placements=case["beam_count"], supports=case["pier_foundation_count"],
                         yards=case["factory_yards_needed"], fronts=case["erection_fronts_needed"],
                         direct_elevated_usd_m=case["direct_elevated_civil_usd_m"],
                         redesign_headroom_usd_each=headroom * 1e6 / case["beam_count"]))
    files = [Path(__file__).resolve(), DIR / "section-results.json", PARENT / "schedule.json", CITY / "system-results.json"]
    sources = {p.relative_to(ROOT).as_posix(): hash_file(p) for p in files}
    return dict(candidate=network["selected_candidate_id"], evaluation=identity([base["evaluation_id"], sources]),
                source_sha256=sources, rows=rows, reference_capital_usd_m=base_case["installed_capital_usd_m"],
                crowd_train_t=power["train_crowd_mass_t"], axle_count=len(axles), step_m=step,
                reference_delivery=monthly_yard_demand(network["selected_civil_delivery"], rows[0]["actions"]["equivalent_stock_t"]))


YARD_RATE_COUNTS = {
    "mobilise_one_yard": "yards", "mobilise_one_front": "fronts",
    "hold_one_yard_month": "yard_months", "hold_one_front_month": "front_months",
}


def yard_return_form(report):
    return {"candidate": report["candidate"], "evaluation": report["evaluation"],
            "scope_and_allowance_review": None,
            "rates_2026_usd": {item: {"cash_price": None, "included_allowance": None}
                               for item in YARD_RATE_COUNTS}}


def price_yard_return(report, form):
    expected = yard_return_form(report)
    if (not isinstance(form, dict) or set(form) != set(expected)
            or any(form[k] != expected[k] for k in ("candidate", "evaluation"))
            or not isinstance(form["scope_and_allowance_review"], str)
            or not form["scope_and_allowance_review"].strip()
            or not isinstance(form["rates_2026_usd"], dict)
            or set(form["rates_2026_usd"]) != set(YARD_RATE_COUNTS)):
        raise ValueError("Match the current candidate and attach the reviewed quotation and allowance reconciliation")
    quantities = report["reference_delivery"]
    rows = {}
    for name, quantity_key in YARD_RATE_COUNTS.items():
        rates = form["rates_2026_usd"][name]
        if (not isinstance(rates, dict) or set(rates) != {"cash_price", "included_allowance"}
                or any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in rates.values())):
            raise ValueError(f"Enter explicit nonnegative quoted and embedded unit amounts for {name}")
        count = quantities[quantity_key]
        rows[name] = dict(units=count, displaced_usd=count * rates["included_allowance"],
                          quoted_usd=count * rates["cash_price"],
                          net_direct_usd=count * (rates["cash_price"] - rates["included_allowance"]))
    baseline = report["rows"][0]["direct_elevated_usd_m"] * 1e6
    if sum(item["displaced_usd"] for item in rows.values()) > baseline:
        raise ValueError("Embedded allowances exceed the existing direct elevated scope")
    net = sum(item["net_direct_usd"] for item in rows.values())
    return dict(candidate=form["candidate"], evaluation=form["evaluation"],
                scope_and_allowance_review=form["scope_and_allowance_review"], matched_rows=rows,
                net_direct_change_usd=net, comparison_elevated_scope_usd=baseline + net)


def render(report):
    rows = report["rows"]
    yard = report["reference_delivery"]
    lines = [
        "# Baghdad viaduct span comparison",
        "",
        f"For the 148.2 km proposal, the installed-capital allowance is ${report['reference_capital_usd_m']:,.2f}m in 2026 USD. "
        "Its repetitive single-track beam is 10 m long on separate piers. The comparisons below keep the two-track railway, "
        "seven corridors and loaded train fixed. They test what happens when a precaster lengthens the same trial box. "
        "The longer units need their own section, tendons, handling scheme and price before selection.",
        "",
        "## Structure and handling",
        "",
        f"Each train has {report['axle_count']} axle planes and a crowd-loaded mass of {report['crowd_train_t']:.3f} t. "
        f"The train advances in {report['step_m']*1000:g} mm steps, with additional entry and exit positions. Each "
        "trial retains the 2.00 × 1.40 m cross-section, 550 mm solid ends, bearing seats 250 mm from each end, "
        "the trial pier and footing, and lifting lines one fifth of the stock length from each end. "
        "The structural screening uses the same 1.30 moving-load multiplier and 150 mm eccentricity as the 10 m study.",
        "",
        "| Stock length | Concrete per beam | Bare equivalent mass | Dead + live positive moment¹ | Elastic displacement bound | Trial soil pressure | Load margin at 12 m radius² |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        a = row["actions"]
        lines.append(f"| {row['length_m']} m | {a['gross_concrete_m3']:.2f} m³ | {a['equivalent_stock_t']:.2f} t | {a['positive_moment_upper_knm']:,.1f} kNm | {a['centre_deflection_curvature_bound_mm']:.1f} mm | {a['pier_gravity_screen']['uniform_soil_contact_pressure_kpa']:.1f} kPa | {row['stock_only_chart_balance_t']:+.2f} t |")
    lines += [
        "",
        "¹ Separately peaked dead moment and sampled train moment give a positive-action screen. The uncracked gross-section displacement bound excludes camber, cracking, creep, settlement and rail continuity. Compare measured rail and conductor elevations with the collector travel and station boarding tolerance before accepting the result.",
        "",
        "² Against the project’s illustrative 60 t chart at 12 m, before hook block, lifting beam, slings, inserts, construction tolerances or crane setup. A negative margin rules out that assumed lift. A positive margin requires a supplier chart at the surveyed radius, ground pressure and rigging take-off. Obtain trailer payload, axle-group reactions, swept path and temporary bracing design.",
        "",
        "| Stock length | Support-pair torque | Effective prestress screen | Pick-line hogging | Pick top / bottom³ | Centre top / bottom³ |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        a = row["actions"]
        lines.append(f"| {row['length_m']} m | {a['bearing_pair_torsion_knm']:.1f} kNm | {a['effective_axial_force_for_zero_bottom_stress_kn']/1000:.2f} MN | {a['stock_lift_hogging_knm']:.1f} kNm | {row['transfer_lift_pick_top_compression_mpa']:+.2f} / {row['transfer_lift_pick_bottom_compression_mpa']:+.2f} MPa | {row['transfer_lift_centre_top_compression_mpa']:+.2f} / {row['transfer_lift_centre_bottom_compression_mpa']:+.2f} MPa |")
    lines += [
        "",
        "³ Compression is positive. Assume a bonded constant-eccentricity tendon at 0.30 m and full transfer before a bare-stock lift. Divide the effective prestress screen by 0.80 to illustrate 20% total loss. Combine that force with self-weight moment at each pick and at midspan. Negative top-fibre stresses identify tension to check against measured concrete release strength. Anchorage, transfer length, end-zone bursting, shear, unequal slings, buckling, bearing seat strength, fatigue and lateral stability require individual checks.",
        "",
        "## Price and deliver the same service",
        "",
        "| Length | Placements | Pier and foundation positions | Yards / erection fronts | Modelled direct elevated scope | Maximum extra cost per placement to match 10 m⁴ |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(f"| {row['length_m']} m | {row['placements']:,} | {row['supports']:,} | {row['yards']} / {row['fronts']} | ${row['direct_elevated_usd_m']:,.2f}m | ${row['redesign_headroom_usd_each']:,.0f} |")
    lines += [
        "",
        "⁴ Divide the difference in the direct elevated allowance by the longer option’s placements. The combined **net** extra cost for redesigned stock, foundations, yard, transport, rigging and erection must fit within that amount to preserve the modelled saving. Include avoided costs once. These prices use the existing length-scaled rates. All four alternatives require ground and access evidence.",
        "",
        f"The 10 m programme deploys {yard['yards']} yards for {yard['yard_months']} yard-months and {yard['fronts']} fronts for {yard['front_months']} front-months under a continuous-hire scenario, assuming all yards store beams from first casting through final erection and all fronts remain on hire between first and last lift. Peak month-end inventory is {yard['peak_month_end_units']:,} beams in {yard['peak_month']} or about {yard['peak_month_end_stock_t']:,.0f} t of stock systemwide. Daily peaks and yard allocations require a dispatch plan. Confirm the asset hand-back dates and demobilisation price.",
        "",
        f"For the 10 m case, each additional $10,000 per yard-month amounts to ${yard['yard_months']*0.01:.2f}m of direct cost, and each additional $10,000 per front-month to ${yard['front_months']*0.01:.2f}m. Apply only the residual after deducting work already included in beam, pier, lift, transport and tooling prices. Quote mobilisation, rent, beds, moulds, shifts, utilities, working capital, route permits and crane possessions separately. Use the [matched return calculation](../compare_returns.py) once a complete elevated scope is priced.",
        "",
        "Obtain the yard return form with `--yard-template > build/baghdad-yard-rates.json`. Enter tendered 2026 USD rates and the itemised amount already carried per unit, attach the scope review reference, then run `--yard-return build/baghdad-yard-rates.json`. The result compares direct elevated costs for the 10 m family. It covers mobilisation and continuous hire. Transport, other civil trades, financing and project-level allowances require their own reconciliations.",
        "",
        "The pier model envelopes two adjacent peak vertical reactions on the trial 2.50 m square footing. Verify site bearing, settlement, overturning, flood/scour and lateral action. Price the river crossing and a step-free station as separate lots, with surveyed access windows and traffic management.",
        "",
        "## Reproduce the comparison",
        "",
        "Run `python3 cities/Baghdad/engineering/mechanical/civil/compare_spans.py --check` from the repository root. Use `--json` for every candidate identity, source fingerprint, axle envelope, pad reaction, lift demand and price threshold. [10 m parent section and assembly details](README.md) · [City capital model](../../../system-results.json)",
        "",
        f"Train candidate `{report['candidate']}`. Evaluation `{report['evaluation']}`.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--json", action="store_true")
    mode.add_argument("--yard-template", action="store_true")
    mode.add_argument("--yard-return", type=Path)
    args = parser.parse_args()
    result = evaluate()
    path = DIR / "SPAN-COMPARISON.md"
    if args.check:
        if path.read_text() != render(result):
            raise SystemExit("Stale Baghdad span comparison")
    elif args.yard_template:
        print(json.dumps(yard_return_form(result), indent=2))
    elif args.yard_return:
        print(json.dumps(price_yard_return(result, json.loads(args.yard_return.read_text())), indent=2, allow_nan=False))
    elif args.json:
        print(json.dumps(result, indent=2, allow_nan=False))
    else:
        path.write_text(render(result))
