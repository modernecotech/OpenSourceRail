"""Propagate provisional architecture changes through civil and factory demands."""

from __future__ import annotations

import csv
from copy import deepcopy
from html import escape
import json
import math
from pathlib import Path
import shutil

from . import campaign, coverage, integration, queue_campaign
from .coverage import ROOT, local, sha

BASIS = Path(__file__).with_name("data") / "architecture-feedback.json"
PARENT = ROOT / "docs/design-engine/queued-systems"
FLAGS = ("engineering_design_complete", "manufacturing_release", "physical_release")


def read(path):
    return json.loads(Path(path).read_text())


def sources():
    result = queue_campaign.source_state(campaign.scope())
    result.update(
        {
            p.relative_to(ROOT).as_posix(): sha(p)
            for p in sorted(PARENT.rglob("*"))
            if p.is_file()
        }
    )
    return dict(sorted(result.items()))


def platform_case(length_m, *, module_m=6, end_allowance_m=2):
    if (
        not all(math.isfinite(v) for v in (length_m, module_m, end_allowance_m))
        or length_m <= 0
        or module_m <= 0
        or end_allowance_m < 0
    ):
        raise ValueError(
            "finite positive train/module length and nonnegative allowance required"
        )
    needed = length_m + 2 * end_allowance_m
    count = math.ceil(needed / module_m)
    return dict(
        train_length_m=length_m,
        required_research_length_m=needed,
        complete_modules_per_platform_edge=count,
        module_length_m=module_m,
        complete_module_platform_length_m=count * module_m,
        minimum_actual_end_allowance_m=(count * module_m - length_m) / 2,
        previous_116m_branch_uses_only_full_modules=math.isclose(
            116 % module_m, 0, abs_tol=1e-10
        ),
        partial_module_adopted=False,
        site_fit_accepted=False,
        egress_accepted=False,
        physical_release=False,
    )


def vehicle_demands(case, basis):
    """Elementary demand balances; ratings, actual brake/traction duty stay open."""
    a = read(ROOT / "engineering/generative_design/data/mechanical-systems.json")[
        "assumptions"
    ]
    mass, cars = case["total_mass_kg"], case["cars"]
    speed, acceleration = a["speed_km_hr"] / 3.6, a["braking_deceleration_m_s2"]
    return dict(
        reference_speed_km_h=a["speed_km_hr"],
        reference_deceleration_m_s2=acceleration,
        kinetic_energy_j=mass * speed**2 / 2,
        translational_braking_force_n=mass * acceleration,
        ideal_constant_deceleration_distance_m=speed**2 / (2 * acceleration),
        scope="Translational energy/force only; rotating mass, grade, resistance, adhesion allocation, regeneration, thermal/repeated stops and actual railway duty remain open",
        per_car_equal_mass_hypothesis_kg=mass / cars,
        per_point_lift_demands=[
            dict(
                effective_points=n,
                demand_n=mass
                / cars
                * 9.80665
                * basis["vehicle_lift_dynamic_sensitivity"]
                / n,
                required_mass_equivalent_kg=mass
                / cars
                * basis["vehicle_lift_dynamic_sensitivity"]
                / n,
                accepted_jack_rating_kg=None,
            )
            for n in basis["vehicle_lift_effective_points"]
        ],
        accepted_brake_capacity_n=None,
        accepted_traction_capacity_w=None,
        physical_release=False,
    )


def canonical_case(case):
    result = deepcopy(case)
    if isinstance(result.get("cars"), list):
        result["car_records"] = result["cars"]
        result["cars"] = result["body_count"]
    return result


def six_car_cases(basis):
    result = []
    for mass in basis["six_car_mass_cases_kg"]:
        for cg in basis["six_car_longitudinal_cg_offsets_m"]:
            pattern = integration.planning_axles(mass, cg)
            result.append(
                dict(
                    id=f"planning-six-car-{mass:g}kg-cg{cg:g}",
                    architecture_id="metro-6car-planning",
                    cars=6,
                    train_length_m=111,
                    total_mass_kg=mass,
                    axles=pattern["axles"],
                    accepted_loading=False,
                    source_frozen_baseline=False,
                    existing_configuration_compatible=False,
                    source_basis="Separate planning architecture; 460800kg is independent +20% mass sensitivity. No LM3 member delta or intercar geometry transferred.",
                    pattern=pattern,
                    physical_release=False,
                )
            )
    return result


def validate_case(case, *, current=True):
    if (
        case["accepted_loading"] is not False
        or case["source_frozen_baseline"] is not False
    ):
        raise ValueError(
            "provisional load case cannot claim acceptance or a frozen baseline"
        )
    expected = {"LM3": (3, 12), "metro-6car-planning": (6, 24)}
    if case["architecture_id"] not in expected:
        raise ValueError("unknown architecture")
    cars, axles = expected[case["architecture_id"]]
    rows = case["axles"]
    if (
        case["cars"] != cars
        or len(rows) != axles
        or len({r["id"] for r in rows}) != axles
    ):
        raise ValueError("architecture support identity differs")
    if not all(
        math.isfinite(r["force_n"])
        and r["force_n"] > 0
        and math.isfinite(r["x_m"])
        and 0 <= r["x_m"] <= case["train_length_m"]
        for r in rows
    ):
        raise ValueError("nonfinite, negative or out-of-train provisional axle")
    if len({r["x_m"] for r in rows}) != axles:
        raise ValueError("duplicate provisional axle station")
    force = math.fsum(r["force_n"] for r in rows)
    if case["architecture_id"] == "LM3":
        if current:
            trace = read(
                ROOT / "engineering/industrialisation/vehicle-civil-load-trace.json"
            )["reference"]
            expected_force = (
                math.fsum(a["static_load_kn"] * 1000 for a in trace["axle_pattern"])
                + (case["total_mass_kg"] - trace["total_mass_kg"]) * 9.80665
            )
        else:
            expected_force = case["expected_source_plus_delta_force_n"]
        expected_cg = case["train_length_m"] / 2
    else:
        expected_force = case["total_mass_kg"] * 9.80665
        expected_cg = (
            case["train_length_m"] / 2 + case["pattern"]["longitudinal_cg_offset_m"]
        )
    if not math.isclose(force, expected_force, rel_tol=1e-10) or not math.isclose(
        math.fsum(r["force_n"] * r["x_m"] for r in rows) / force,
        expected_cg,
        abs_tol=1e-9,
    ):
        raise ValueError("architecture mass/CG equilibrium differs")


def demand_envelope(demand, limits):
    return next((limit for limit in limits if demand <= limit), None)


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(output, *, native=False):
    from . import (
        architecture_mechanical,
        architecture_civil,
        architecture_equipment,
        civil,
    )
    from engineering.factory_examples.native import generate

    output = Path(output).resolve()
    if output.exists() or not output.is_relative_to(ROOT / "build"):
        raise ValueError("architecture feedback requires a fresh build directory")
    parent = queue_campaign.verify(PARENT, current=False, snapshot=True)
    source, environment = sources(), campaign.environment(native)
    basis = read(BASIS)
    output.mkdir(parents=True)
    campaign.write(
        output / "request.json",
        dict(
            schema="osr-architecture-feedback-request/1",
            source_sha256=source,
            environment=environment,
            native=native,
            basis=basis,
            parent_historical_verification=parent,
            physical_release=False,
        ),
    )
    try:
        mechanical = architecture_mechanical.run()
        equipment = architecture_equipment.run(
            loaded_car_mass_kg=max(
                c["total_mass_kg"] / c["body_count"] for c in mechanical["cases"]
            )
        )
        campaign.write(output / "mechanical.json", mechanical)
        campaign.write(output / "equipment.json", equipment)
        cases = [canonical_case(c) for c in mechanical["cases"]] + six_car_cases(basis)
        if len({c["id"] for c in cases}) != len(cases):
            raise ValueError("duplicate architecture case identity")
        family = architecture_civil.candidate_family()
        campaign.write(output / "beam-family.json", family)
        records, models = [], []
        for case in cases:
            validate_case(case)
            report = architecture_civil.assess_pattern(
                family, case, sensitivity=basis["force_sensitivity_multiplier"]
            )
            path = output / "cases" / case["id"] / "civil.json"
            campaign.write(path, report)
            # Candidate response schema belongs to the civil module. Its
            # selection remains a local sampled screen, never an adoption.
            selected = report["selected_candidate_ids"]
            record = dict(
                id=case["id"],
                architecture_id=case["architecture_id"],
                case=case,
                platform=platform_case(
                    case["train_length_m"],
                    module_m=basis["platform_module_length_m"],
                    end_allowance_m=basis["platform_end_allowance_m_each"],
                ),
                vehicle_demands=vehicle_demands(case, basis),
                civil_report=path.relative_to(output).as_posix(),
                selected_local_beam_ids=selected,
                selected_local_beams=[
                    dict(
                        id=c["id"],
                        variables=c["variables"],
                        metrics=c["metrics"],
                        hook_planning_envelope_kg=demand_envelope(
                            c["metrics"]["maximum_hook_equivalent_kg"],
                            basis["hook_planning_envelopes_kg"],
                        ),
                        bed_planning_envelope_n=demand_envelope(
                            c["metrics"]["initial_bed_force_n"],
                            basis["bed_force_planning_envelopes_n"],
                        ),
                        accepted_hook_capacity_kg=None,
                        accepted_bed_capacity_n=None,
                    )
                    for c in report["candidates"]
                    if c["id"] in selected
                ],
                existing_configuration_compatible=case[
                    "existing_configuration_compatible"
                ],
                required_gates=basis["open_gates"],
                engineering_design_complete=False,
                manufacturing_release=False,
                physical_release=False,
            )
            records.append(record)
            print(
                f'{case["id"]}: {len(report["candidates"])} beam responses; {len(selected)} local selections',
                flush=True,
            )
        targets = [
            max(
                (r for r in records if r["architecture_id"] == architecture),
                key=lambda r: (r["case"]["total_mass_kg"], r["id"]),
            )
            for architecture in ("LM3", "metro-6car-planning")
        ]
        for target in targets:
            if not target["selected_local_beam_ids"]:
                continue
            response = read(output / target["civil_report"])
            candidate = next(
                c
                for c in response["candidates"]
                if c["id"] == target["selected_local_beam_ids"][0]
            )
            model = (
                output
                / "models"
                / target["architecture_id"]
                / candidate["id"]
                / "model.json"
            )
            campaign.write(model, architecture_civil.model_definition(candidate))
            record = dict(
                case_id=target["id"],
                candidate_id=candidate["id"],
                model=model.relative_to(output).as_posix(),
                status="not-requested",
                physical_release=False,
            )
            if native:
                try:
                    proof = generate(model, model.parent, ROOT)
                    record.update(
                        status="passed",
                        part_count=proof["part_count"],
                        receipt=(model.parent / "native-cad.json")
                        .relative_to(output)
                        .as_posix(),
                    )
                except Exception as error:
                    record.update(status="failed", error=str(error))
            models.append(record)
            print(f'native {record["case_id"]}: {record["status"]}', flush=True)
        result = dict(
            schema="osr-architecture-feedback/1",
            basis=basis,
            cases=records,
            case_count=len(records),
            distinct_beam_geometries=len(family),
            beam_response_records=len(family) * len(records),
            native_geometry=models,
            affected_scope=affected_scope(),
            engineering_design_complete=False,
            manufacturing_release=False,
            physical_release=False,
        )
        campaign.write(output / "report.json", result)
        write_csv(
            output / "architecture-demands.csv",
            [
                dict(
                    case=r["id"],
                    architecture=r["architecture_id"],
                    train_length_m=r["case"]["train_length_m"],
                    train_mass_kg=r["case"]["total_mass_kg"],
                    axles=len(r["case"]["axles"]),
                    platform_full_modules=r["platform"][
                        "complete_modules_per_platform_edge"
                    ],
                    platform_length_m=r["platform"][
                        "complete_module_platform_length_m"
                    ],
                    braking_energy_j=r["vehicle_demands"]["kinetic_energy_j"],
                    braking_force_n=r["vehicle_demands"][
                        "translational_braking_force_n"
                    ],
                    physical_release=False,
                )
                for r in records
            ],
        )
        (output / "index.html").write_text(page(result))
        (output / "architecture-layout.svg").write_text(figure(result))
        if sources() != source or campaign.environment(native) != environment:
            raise ValueError(
                "architecture feedback sources/environment changed during execution"
            )
        campaign.write(
            output / "receipt.json",
            dict(
                schema="osr-architecture-feedback-receipt/1",
                source_sha256=source,
                environment=environment,
                files_sha256=queue_campaign.file_hashes(output),
                physical_release=False,
            ),
        )
        return verify(output)
    except Exception as error:
        campaign.write(
            output / "failure.json",
            dict(
                error=type(error).__name__, message=str(error), physical_release=False
            ),
        )
        raise


def affected_scope():
    ids = {
        "BASIS-CONFIGURATION",
        "SYSTEM-ROUTE",
        "SYSTEM-INTEGRATION",
        "LM3-FRP-010",
        "LM3-FRP-120",
        "BUY-LM3-ART-SA810",
        "BUY-LM3-ART-SA820",
        "BUY-LM3-ART-SA830",
        "CIV-FRP-100",
        "CIV-FRP-110",
        "FACTORY-PRECAST",
        "FACTORY-HANDLING",
        "FACTORY-BUILDINGS",
        "SYSTEM-SAFETY",
        "SYSTEM-ENERGY",
        "SYSTEM-ASSURANCE",
        "STN-FRP-010",
        "STN-FRP-090",
        "CIV-FRP-120",
        "CIV-INT-200",
        "CIV-INT-210",
        "LM3-FRP-100",
        "LM3-FRP-110",
        "LM3-FRP-130",
        "LM3-FRP-140",
        "LM3-FRP-150",
        "BUY-LM3-BOG-SA610",
        "BUY-LM3-BOG-SA620",
        "BUY-LM3-BOG-SA611",
        "BUY-LM3-BOG-SA621",
        "BUY-LM3-TRC-SA615",
        "BUY-LM3-HV-SA510",
        "BUY-LM3-END-SA700",
        "FACTORY-EQUIPMENT",
        "FACTORY-FLOW",
    }
    packages = campaign.scope()["work_packages"]
    if ids - {p["id"] for p in packages}:
        raise ValueError("unknown affected work package")
    direct = set(ids)
    while True:
        next_ids = ids | {p["id"] for p in packages if set(p["dependencies"]) & ids}
        if next_ids == ids:
            break
        ids = next_ids
    return [
        dict(
            id=p["id"],
            authoritative_sources=p["authoritative_sources"],
            required_gates=p["required_gates"],
            completion_predicate=p["completion_predicate"],
            dependencies=p["dependencies"],
            impact_type=(
                "direct-research-interface"
                if p["id"] in direct
                else "dependent-package-recheck"
            ),
            source_baseline_changed=False,
            engineering_design_complete=False,
            manufacturing_release=False,
            physical_release=False,
        )
        for p in packages
        if p["id"] in ids
    ]


def figure(report):
    """Same metre scale for declared train cells, axle stations and modules."""
    e = lambda value: escape(str(value), quote=True)
    height = 100 + len(report["cases"]) * 72
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}"><rect width="1000" height="{height}" fill="#f4f3ed"/><g font-family="sans-serif" fill="#17313e"><text x="20" y="25" font-size="20">Architecture / full-module platform sensitivities</text><text x="20" y="48" font-size="12">Research cells and axle locations; supplier body/gap geometry, platform, site and gauging acceptance remain open.</text>'
    ]
    for index, row in enumerate(report["cases"]):
        case = row["case"]
        y = 85 + 72 * index
        elements.append(
            f'<text x="20" y="{y}" font-size="12">{index+1}. {e(row["architecture_id"])}</text><text x="20" y="{y+18}" font-size="11">{case["train_length_m"]:g} m / {case["total_mass_kg"]/1000:.3f} t</text>'
        )
        body = case.get("body_length_m", 18.5)
        gap = case.get("inter_car_gap_m", 0)
        start = (
            260
            + (
                row["platform"]["complete_module_platform_length_m"]
                - case["train_length_m"]
            )
            / 2
            * 5
        )
        for car in range(case["cars"]):
            x = start + car * (body + gap) * 5
            elements.append(
                f'<rect x="{x}" y="{y-14}" width="{body*5}" height="18" rx="3" fill="#5d8495"/>'
            )
        for axle in case["axles"]:
            elements.append(
                f'<circle cx="{start+axle["x_m"]*5}" cy="{y+5}" r="2.5" fill="#17313e"/>'
            )
        for module in range(row["platform"]["complete_modules_per_platform_edge"]):
            elements.append(
                f'<rect x="{260+module*30}" y="{y+18}" width="30" height="8" fill="#d7b674" stroke="#806c49" stroke-width=".5"/>'
            )
        elements.append(
            f'<text x="875" y="{y+25}" font-size="11">{row["platform"]["complete_module_platform_length_m"]:g} m</text>'
        )
    elements.append("</g></svg>")
    return "\n".join(elements) + "\n"


def page(report):
    e = lambda value: escape(str(value), quote=True)

    def beam_labels(row):
        return "; ".join(
            f'{beam["metrics"]["actual_lower_strand_count"]}/{beam["variables"]["strand_count"]} actual lower strands; bed {beam["metrics"]["initial_bed_force_n"]/1e6:.3f} MN; hook {beam["metrics"]["maximum_hook_equivalent_kg"]/1000:.3f} t; service minimum {beam["metrics"]["minimum_service_compression_pa"]/1e6:.3f} MPa'
            for beam in row["selected_local_beams"]
        )

    rows = "".join(
        f'<tr><td>{e(r["id"])}<br>{e(r["architecture_id"])}</td><td>{r["case"]["train_length_m"]:.3f} m<br>{r["case"]["total_mass_kg"]/1000:.3f} t<br>{len(r["case"]["axles"])} axles</td><td>{r["platform"]["complete_modules_per_platform_edge"]} × 6 m = {r["platform"]["complete_module_platform_length_m"]:g} m</td><td>{r["vehicle_demands"]["kinetic_energy_j"]/1e6:.3f} MJ<br>{r["vehicle_demands"]["translational_braking_force_n"]/1000:.3f} kN</td><td><a href="{e(r["civil_report"])}">All beam responses</a><br>{e(", ".join(r["selected_local_beam_ids"]))}<br>{e(beam_labels(r))}</td><td>Open</td></tr>'
        for r in report["cases"]
    )
    native_links = " · ".join(
        f'<a href="{escape(str(Path(r["model"]).parent/"model.FCStd"),quote=True)}">{e(r["case_id"])}</a>'
        for r in report["native_geometry"]
        if r["status"] == "passed"
    )
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Provisional architecture feedback</title><style>body{{font:16px/1.5 system-ui,sans-serif;background:#f4f3ed;color:#17313e;margin:0}}main{{max-width:1250px;padding:24px;margin:auto}}.notice{{padding:16px;border-left:5px solid #ae553f;background:white}}.scroll{{overflow:auto}}table{{border-collapse:collapse;background:white;width:100%;min-width:850px}}td,th{{border:1px solid #cbd0cd;padding:10px;text-align:left;vertical-align:top;overflow-wrap:anywhere}}a{{color:#12667a}}@media(max-width:650px){{main{{padding:12px}}}}</style><main><h1>Provisional architecture feedback</h1><p class="notice">Changed vehicle mass and spacing propagate into axle patterns, civil demand, full-module platforms, braking and lifting sensitivities. No architecture, load, material, supplier configuration or manufacturing release is accepted.</p><p>{report["case_count"]} architecture cases; {report["distinct_beam_geometries"]} distinct beam geometries; {report["beam_response_records"]} response records. Local sampled screens do not complete a structure or railway.</p><p><a href="report.json">Whole report and open gates</a> · <a href="mechanical.json">Mechanical variants / mass equilibrium</a> · <a href="equipment.json">British equipment cases</a> · <a href="architecture-demands.csv">Demand CSV</a> · <a href="beam-family.json">Beam geometry family</a></p><p>LM3 uses three 16.5 m cars and 12 axles. The separate planning train uses six 18.5 m cars and 24 axles. No LM3 steel addition is transferred into the six-car case. Six-car 460.8 t is an independent +20% mass sensitivity.</p><p>A 116 m platform includes a partial module: it is not 20 complete 6 m modules. This study reserves complete modules; site, egress and detailed interfaces stay open.</p><p><a href="architecture-layout.svg">Train / axle / full-module platform diagram</a></p><div class="scroll"><table><thead><tr><th>Case</th><th>Architecture demand</th><th>Full-module platform</th><th>80km/h translational stop</th><th>Civil variations</th><th>Acceptance</th></tr></thead><tbody>{rows}</tbody></table></div><h2>Native geometry checks</h2><p>{native_links or "No native geometry confirmation requested."}</p><p>Reopened FCStd/STEP geometry does not qualify material resistance, reinforcement, stressing equipment or manufacture.</p><h2>Remaining acceptance gates</h2><ul>{"".join(f"<li>{e(g)}</li>" for g in report["basis"]["open_gates"])}</ul><p>British supplier sources establish catalogue leads only. No supplier is contacted. Earlier source-bound packets remain historical evidence.</p></main></html>"""


def verify(folder, *, current=True, snapshot=False):
    folder = Path(folder).resolve()
    seal = "snapshot.json" if snapshot else "receipt.json"
    seal_record = read(folder / seal)
    if (
        seal_record.get("schema")
        != (
            "osr-architecture-feedback-snapshot/1"
            if snapshot
            else "osr-architecture-feedback-receipt/1"
        )
        or seal_record.get("physical_release") is not False
    ):
        raise ValueError("controlled provisional architecture seal required")
    files = queue_campaign.file_hashes(folder, (seal,))
    if set(files) != set(seal_record["files_sha256"]):
        raise ValueError("architecture artifact membership differs")
    if files != seal_record["files_sha256"]:
        raise ValueError("architecture artifact changed")
    report = read(folder / "report.json")
    if any(report.get(k) is not False for k in FLAGS):
        raise ValueError("provisional architecture cannot grant release")
    ids = [c["id"] for c in report["cases"]]
    if len(set(ids)) != len(ids) or len(ids) != report["case_count"]:
        raise ValueError("architecture case identity differs")
    for row in report["cases"]:
        validate_case(row["case"], current=current)
        if (
            any(row.get(k) is not False for k in FLAGS)
            or row["required_gates"] != report["basis"]["open_gates"]
        ):
            raise ValueError("architecture case cannot erase gates or grant release")
        expected = platform_case(
            row["case"]["train_length_m"],
            module_m=report["basis"]["platform_module_length_m"],
            end_allowance_m=report["basis"]["platform_end_allowance_m_each"],
        )
        if row["platform"] != expected:
            raise ValueError("architecture full-module platform differs")
        local(row["civil_report"], folder).read_bytes()
    for record in report["native_geometry"]:
        if record["status"] != "passed":
            continue
        model = local(record["model"], folder)
        proof = read(local(record["receipt"], folder))
        definition = read(model)
        if (
            proof.get("schema") != "osr-factory-native-cad/1"
            or proof.get("physical_release") is not False
            or proof.get("fcstd_reopened") is not True
            or proof.get("step_reopened") is not True
            or proof.get("input_sha256") != sha(model)
            or proof.get("part_count") != len(definition["parts"])
            or record["part_count"] != len(definition["parts"])
            or {p["id"] for p in proof["parts"]}
            != {p["id"] for p in definition["parts"]}
        ):
            raise ValueError("architecture native proof incomplete")
        for name in (("model.FCStd",) if snapshot else ("model.FCStd", "model.step")):
            if sha(model.parent / name) != proof["files_sha256"][name]:
                raise ValueError("architecture native geometry differs")
    family = read(folder / "beam-family.json")
    observed_responses = 0
    for row in report["cases"]:
        study = read(local(row["civil_report"], folder))
        if len(study["candidates"]) != len(family) or {
            c["id"] for c in study["candidates"]
        } != {c["id"] for c in family}:
            raise ValueError("architecture beam candidate identities differ")
        observed_responses += len(study["candidates"])
    if (
        observed_responses != report["beam_response_records"]
        or len(family) != report["distinct_beam_geometries"]
    ):
        raise ValueError("architecture beam response rollup differs")
    expected_cases = [
        canonical_case(c) for c in read(folder / "mechanical.json")["cases"]
    ]
    planning_cases = [
        r["case"]
        for r in report["cases"]
        if r["architecture_id"] == "metro-6car-planning"
    ]
    expected_pairs = {
        (mass, cg)
        for mass in report["basis"]["six_car_mass_cases_kg"]
        for cg in report["basis"]["six_car_longitudinal_cg_offsets_m"]
    }
    actual_pairs = {
        (c["total_mass_kg"], c["pattern"]["longitudinal_cg_offset_m"])
        for c in planning_cases
    }
    if actual_pairs != expected_pairs or len(planning_cases) != len(expected_pairs):
        raise ValueError("architecture planning mass/CG cases differ")
    expected_cases += six_car_cases(report["basis"]) if current else planning_cases
    if {c["id"] for c in expected_cases} != set(ids) or {
        c["id"]: c for c in expected_cases
    } != {r["case"]["id"]: r["case"] for r in report["cases"]}:
        raise ValueError(
            "architecture cases differ from explicit mechanical/planning inputs"
        )
    if current and (
        sources() != seal_record["source_sha256"]
        or report["affected_scope"] != affected_scope()
        or report["basis"] != read(BASIS)
    ):
        raise ValueError("architecture feedback belongs to another source revision")
    return dict(
        integrity_verified=True,
        current_sources_checked=current,
        case_count=len(ids),
        beam_response_records=report["beam_response_records"],
        engineering_design_complete=False,
        native_geometry_passed=sum(
            r["status"] == "passed" for r in report["native_geometry"]
        ),
        native_geometry_failed=sum(
            r["status"] == "failed" for r in report["native_geometry"]
        ),
        manufacturing_release=False,
        physical_release=False,
        numerical_recomputation_performed=False,
    )


def publish(output, destination):
    output, destination = Path(output).resolve(), Path(destination).resolve()
    result = verify(output)
    if destination.exists() or not destination.is_relative_to(
        ROOT / "docs/design-engine"
    ):
        raise ValueError(
            "architecture publication requires a fresh docs/design-engine directory"
        )
    destination.mkdir(parents=True)
    receipt = read(output / "receipt.json")
    for name in receipt["files_sha256"]:
        source = output / name
        if source.suffix not in {".json", ".html", ".csv", ".svg", ".FCStd"}:
            continue
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    campaign.write(
        destination / "snapshot.json",
        dict(
            schema="osr-architecture-feedback-snapshot/1",
            source_sha256=receipt["source_sha256"],
            parent_receipt_sha256=sha(output / "receipt.json"),
            parent_verified_at_publication=result,
            files_sha256=queue_campaign.file_hashes(destination),
            physical_release=False,
        ),
    )
    return verify(destination, snapshot=True)
