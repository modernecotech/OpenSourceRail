"""Run the Airport audit on public GIS layers and price the simulated railway."""

import argparse
import csv
from hashlib import sha256
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from engineering.performance import disk_reservation

from . import airport_alignment, assumption_audit, scenario, site_cash, site_costs, site_layers, site_profile

HERE = Path(__file__).resolve().parent
PUBLIC_FILES = ("GIS-SIMULATION.md", "site-study.json", "site-study-profile.csv", "site-study.geojson")


def evaluate(layer_path=None, *, clearance_m=6.0, grade_pct=0.6, phase_s=1308):
    horizontal = airport_alignment.evaluate()
    layers = site_layers.load_site_layers(layer_path, alignment=horizontal)
    profile = site_profile.derive_site_profile(layers, horizontal, soffit_clearance_m=clearance_m,
                                               max_grade_pct=grade_pct)
    with TemporaryDirectory() as temporary:
        geometry = Path(temporary) / "desk-study-centreline.json"
        geometry.write_bytes(scenario.encode(profile["alignment_input"]))
        # The submitted-centreline adapter binds the DEM-based rail levels to the
        # actual vertex geometry. Its document and verification reference identify
        # a desktop estimate. Keep the published unprofiled experiment intact.
        audit = assumption_audit.audit(survey=geometry, phase_s=phase_s)
    if audit["alignment"]["survey_source"]["revision"] != profile["site_profile_id"]:
        raise ValueError("Operating replay did not use the desk-study rail profile")
    if not audit["civil_quotation"] or not audit["production"]:
        raise ValueError("The site study has no structurally screened civil row to price")
    civil = site_costs.evaluate(profile, audit["civil_quotation"])
    site_lots = [
        dict(lot_id=name, group="opening-direct", source_unit=row["unit"], quantity=row["quantity"],
             usd=row["usd"], year=None, cost_evidence=row["basis"],
             alignment_id=audit["alignment"]["alignment_id"], reference_site_cost_id=civil["evaluation_id"])
        for name, row in civil["lots"].items()
    ]
    cash = site_cash.evaluate(audit, {name: site_lots for name in audit["production"]})
    normal = {day["topology"]: day for day in audit["power_days"] if day["condition"] == "normal"}
    rail = audit["alignment"]
    samples = profile["samples"]
    result = {
        "schema": "osr-baghdad-airport-gis-study/1",
        "purpose": "Costed desktop simulation",
        "alignment_id": rail["alignment_id"],
        "alignment_record_id": rail["record_id"],
        "horizontal_parent_id": horizontal["alignment_id"],
        "audit_evaluation_id": audit["evaluation_id"],
        "site_profile_id": profile["site_profile_id"],
        "settings": {**profile["settings"], "terminal_phase_s": phase_s},
        "route_km": rail["route_km"],
        "stops": [{**stop, "location_scope": "Desk-study station location",
                   "rail_elevation_m": rail["grade_profile"]["elevations_m"][source["vertex"]]}
                  for stop, source in zip(rail["stops"], profile["alignment_input"]["stops"], strict=True)],
        "terrain": {
            "sample_count": len(samples),
            "lowest_dem_m": min(row["ground_elevation_m"] for row in samples),
            "highest_dem_m": max(row["ground_elevation_m"] for row in samples),
            "minimum_soffit_height_m": min(row["soffit_height_m"] for row in samples),
            "maximum_soffit_height_m": max(row["soffit_height_m"] for row in samples),
            "maximum_absolute_grade_pct": profile["maximum_absolute_grade_pct"],
            "samples_with_clay": sum(row["clay_pct"] is not None for row in samples),
            "samples_with_water_observation": sum(row["water_occurrence_pct"] is not None for row in samples),
            "maximum_nearby_water_occurrence_pct": max(
                (row["water_occurrence_100m_max_pct"] for row in samples
                 if row["water_occurrence_100m_max_pct"] is not None), default=None),
        },
        "source_layers": layers["sources"],
        "layers_sha256": profile["layers_sha256"],
        "working_day": {
            "headway_min": audit["timetable_offer"]["headway_min"],
            "dwell_s": audit["timetable_offer"]["dwell_s"],
            "annual_requested_journeys": audit["demand"]["annual_all_journeys"],
            "normal_by_layout": normal,
            "headway_sensitivities": audit["service_offers"],
            "all_cases": [{key: day[key] for key in ("topology", "condition", "completed", "booked",
                           "minimum_v", "numerical_valid", "failed_screens")}
                          for day in audit["power_days"]],
        },
        "design_screen": audit["decision"]["candidates"],
        "vehicle_evaluation_id": audit["vehicle"]["evaluation_id"],
        "vehicle_loaded_mass_kg": {name: case["loaded_train_kg"]
                                   for name, case in audit["vehicle"]["mass_cases"].items()},
        "civil": civil,
        "civil_stock": {key: audit["civil_quotation"][key]
                        for key in ("label", "placements", "supports", "bearings", "audit_row_id")},
        "cash": cash,
        "source_sha256": {path.name: sha256(path.read_bytes()).hexdigest() for path in
                          (Path(__file__), *(Path(module.__file__) for module in
                                             (site_layers, site_profile, site_costs, site_cash)))},
        "physical_acceptance": False,
    }
    result["evaluation_id"] = airport_alignment.identity(result)
    return result, profile


def report(result):
    t = result["terrain"]
    c = result["civil"]
    q = c["quantities"]
    cash = result["cash"]["layouts"]
    scope = result["working_day"]
    lines = [
        "# Baghdad Airport GIS simulation and cost estimate",
        "",
        f"The {result['route_km']:.2f} km desktop study carries public elevation, soil texture "
        "and historical surface-water data through the alignment, train and feeder replay, "
        "civil quantities and 30-year cash estimate. All costs are planning estimates in constant 2026 USD.",
        "",
        "## Terrain and rail profile",
        "",
        f"The {t['sample_count']:,} route samples span {t['lowest_dem_m']:.2f} to {t['highest_dem_m']:.2f} m "
        "in the DEM. The model places the rail above that surface and keeps the platform intervals level. "
        f"The maximum simulated grade is {t['maximum_absolute_grade_pct']:.3f}%. The soffit is "
        f"{t['minimum_soffit_height_m']:.2f} to {t['maximum_soffit_height_m']:.2f} m above the sampled surface.",
        "",
        "The DEM is a surface model, so structures can affect sampled heights. Soil texture guides "
        "scenario allowances for foundation treatment. Historical water occurrence screens surface-water "
        "exposure. Bearing strength, groundwater and design flood levels remain assumptions in this model.",
        "",
        f"The soil grid returns a shallow clay estimate at {t['samples_with_clay']:,} of the "
        f"{t['sample_count']:,} samples. Historical water data cover {t['samples_with_water_observation']:,} samples.",
        "",
        "| Stop | Chainage km | Rail elevation m |",
        "|---|---:|---:|",
    ]
    for stop in result["stops"]:
        lines.append(f"| {stop['label']} | {stop['chainage_km']:.3f} | {stop['rail_elevation_m']:.2f} |")
    lines.extend([
        "",
        "## Train and power replay",
        "",
        f"The declared service runs every {scope['headway_min']} minutes with {scope['dwell_s']:g} s dwell. "
        f"The demand model projects {scope['annual_requested_journeys']:,.0f} requested journeys per year under "
        "the study assumptions.",
        "",
        "| Supply | Duty | Completed / booked trips | Lowest live collector V |",
        "|---|---|---:|---:|",
    ])
    for day in scope["all_cases"]:
        volts = day["minimum_v"]
        lines.append(f"| {day['topology']} | {day['condition']} | {day['completed']} / {day['booked']} | "
                     + (f"{volts:,.1f}" if volts is not None else "—") + " |")
    lines.extend(["", "| Supply | Failed integrated screens | Inputs still open in the model |",
                  "|---|---|---|"])
    for layout, screen in result["design_screen"].items():
        functional = screen["functional_screen"]
        failed = ", ".join(functional["failed"]) or "None in this run"
        unknown = ", ".join(functional["unknown"]) or "None in this run"
        lines.append(f"| {layout} | {failed} | {unknown} |")
    stock = result["civil_stock"]
    lines.extend(["", "## What the site layers change", "",
                  f"The {stock['label']} trial prices {stock['placements']:,} placements across "
                  f"{q['physical_supports']:,} supports. Trial column heights range from "
                  f"{q['trial_column_height_min_m']:.2f} to {q['trial_column_height_max_m']:.2f} m. "
                  f"Columns above standard stock add {q['extra_column_concrete_m3']:,.0f} m³ of concrete. "
                  "The foundation scenarios vary the bearing pressure, bore length and amount of ground treatment.",
                  "", "| Bearing assumption | Standard pad failures | Enlarged pads | Shaft allowance |",
                  "|---|---:|---:|---:|"])
    footing = c["footing_sensitivity"]
    for name, row in footing["resized_footings"].items():
        pressure = row["assumed_bearing_kpa"]
        fixed = footing["failed_support_count_by_assumed_bearing_kpa"][str(pressure)]
        lines.append(f"| {name} · {pressure:g} kPa | {fixed:,} | {row['supports_enlarged']:,} | "
                     f"{c['cases'][name]['trial_shaft_support_count']:,} supports |")
    lines.extend(["",
                  "| Additional priced site scope | Low USD m | Base USD m | High USD m |",
                  "|---|---:|---:|---:|"])
    for label, row in c["lots"].items():
        values = " | ".join(f"{row['usd'][key] / 1e6:,.2f}" for key in ("low", "base", "high"))
        lines.append(f"| {label} | {values} |")
    lines.extend(["", "## Simulated purchaser cash", "",
                  "| Layout | Price case | Capital USD m | Annual operation USD m | 30-year present cost USD m |",
                  "|---|---|---:|---:|---:|"])
    for layout, record in cash.items():
        for name, band in record["cash"]["profiles"].items():
            values = (band["capital_usd"], band["annual_opex_usd"], band["priced_30y_pv_usd"])
            lines.append(f"| {layout} | {name} | " + " | ".join(f"{value / 1e6:,.2f}" for value in values) + " |")
    lines.extend([
        "",
        "Compare the priced layouts against the replayed outage service above. "
        "The capital and cash totals include modelled equipment and site allowances. The record lists each "
        "lot, its estimate basis, any remaining scope exclusions and the annual cash flows.",
        "",
        "The decision record preserves the test conditions, rate sources and candidate identities.",
        "",
        "[Inputs and evaluation instructions](GIS-SIMULATION-GUIDE.md) · "
        "[Route map](site-study.geojson) · [Route samples](site-study-profile.csv) · "
        "[Cost and decision record](site-study.json)",
        "",
        f"Evaluation `{result['evaluation_id']}`.",
        "",
    ])
    return "\n".join(lines)


def artifacts(result, profile):
    output = StringIO()
    columns = ("chainage_m", "longitude_deg", "latitude_deg", "ground_elevation_m", "rail_elevation_m",
               "soffit_height_m", "clay_pct", "water_occurrence_pct", "water_occurrence_100m_max_pct")
    writer = csv.DictWriter(output, columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in profile["samples"]:
        writer.writerow({**row, **dict(zip(columns[1:3], row["longitude_latitude"], strict=True))})
    aligned = profile["alignment_input"]
    features = [
        {"type": "Feature", "properties": {"kind": "study centreline"}, "geometry": aligned["geometry"]},
        *({"type": "Feature", "properties": {**stop, "kind": "study station"},
           "geometry": {"type": "Point", "coordinates": stop["longitude_latitude"]}}
          for stop in result["stops"]),
        *({"type": "Feature",
           "properties": {**{key: val for key, val in row.items() if key != "longitude_latitude"},
                          "kind": "GIS sample"},
           "geometry": {"type": "Point", "coordinates": row["longitude_latitude"]}}
          for row in profile["samples"]),
    ]
    geojson = {"type": "FeatureCollection", "alignment_id": result["alignment_id"],
               "elevation_datum": aligned["vertical_profile"]["datum"], "features": features}
    return dict(zip(PUBLIC_FILES, (
        report(result).encode(), scenario.encode(result) + b"\n", output.getvalue().encode(),
        scenario.encode(geojson) + b"\n"), strict=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layers", type=Path, help="Replacement GIS sample on the matching horizontal alignment")
    parser.add_argument("--clearance-m", type=float, default=6.0)
    parser.add_argument("--grade-pct", type=float, default=0.6)
    parser.add_argument("--phase-s", type=int, default=1308)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--output", type=Path, help="Write the complete desk study under this directory")
    actions.add_argument("--publish", action="store_true", help="Regenerate the published case")
    actions.add_argument("--check", action="store_true", help="Reproduce the published case")
    args = parser.parse_args()
    if (args.publish or args.check) and (args.layers is not None or args.clearance_m != 6
                                         or args.grade_pct != 0.6 or args.phase_s != 1308):
        parser.error("Use --output for alternative inputs. The published case uses the defaults.")
    with disk_reservation(airport_alignment.ROOT, airport_alignment.ROOT, "Airport GIS site study", 96 << 20):
        study, profile = evaluate(args.layers, clearance_m=args.clearance_m, grade_pct=args.grade_pct,
                                  phase_s=args.phase_s)
        files = artifacts(study, profile)
        if args.check:
            for name, expected in files.items():
                if (HERE / name).read_bytes() != expected:
                    raise SystemExit(f"Rebuild the Airport GIS study. {name} differs.")
            print(f"Airport GIS study reproduced: {study['evaluation_id']}")
        elif args.publish or args.output:
            directory = HERE if args.publish else args.output
            directory.mkdir(parents=True, exist_ok=True)
            for name, content in files.items():
                scenario.write_atomic(directory / name, content)
            if args.output:
                scenario.write_atomic(directory / "desk-study-centreline.json",
                                      scenario.encode(profile["alignment_input"]) + b"\n")
            print(study["evaluation_id"])
        else:
            print(report(study))


if __name__ == "__main__":
    main()
