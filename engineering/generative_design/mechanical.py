"""Deterministic feedback search for a manufacturable locator-cassette concept.

Passes are geometry and expressly assumed stiffness screens. Unknown strength,
tool paths and process qualification always prevent engineering release.
"""

from __future__ import annotations

from collections import deque
import hashlib
import json
import math
from pathlib import Path

SPACE = Path(__file__).with_name("data") / "mechanical-space.json"
REFERENCE = Path(__file__).parents[1] / "factory_examples/data/connections.json"


def _read():
    cfg = json.loads(SPACE.read_text())
    retained = json.loads(REFERENCE.read_text())["locator"]
    for name in ["bore_diameter_m", "bore_tolerance_half_m", "stem_tolerance_half_m"]:
        if cfg["planning"][name] != retained[name]:
            raise ValueError("retained locator dimension drift: " + name)
    return cfg


def _id(variables):
    payload = json.dumps(variables, sort_keys=True, separators=(",", ":"))
    return "mechanical-" + hashlib.sha256(payload.encode()).hexdigest()[:12]


def evaluate(variables):
    """Assess positive continuous geometry, including independent test controls.

    Search generation is separately restricted to the declared finite choices;
    this assessor alone makes no claim that an input belongs to that search.
    No accepted material resistance is inferred.
    """
    cfg = _read()
    p, machine = cfg["planning"], cfg["equipment"]
    v = dict(variables)
    if set(v) != set(cfg["seed"]):
        raise ValueError("cassette variables must match the controlled search space")
    if any(not math.isfinite(x) or x <= 0 for x in v.values()):
        raise ValueError("cassette dimensions must be finite and positive")
    w, length, t = v["width_m"], v["length_m"], v["plate_m"]
    px, py, stem = v["pitch_x_m"], v["pitch_y_m"], v["stem_diameter_m"]
    checks = []

    def check(name, condition, basis):
        checks.append(
            dict(id=name, status="passed" if condition else "failed", basis=basis)
        )

    hole = p["bolt_clearance_diameter_m"]
    edge = min((w - px - hole) / 2, (length - py - hole) / 2)
    bore_gap = math.hypot(px / 2, py / 2) - (hole + p["bore_diameter_m"]) / 2
    head_gap = (
        math.hypot(px / 2, py / 2)
        - (p["bolt_head_diameter_m"] + p["locator_head_diameter_m"]) / 2
    )
    clearance_min = (
        p["bore_diameter_m"]
        - p["bore_tolerance_half_m"]
        - stem
        - p["stem_tolerance_half_m"]
    )
    clearance_max = (
        p["bore_diameter_m"]
        + p["bore_tolerance_half_m"]
        - stem
        + p["stem_tolerance_half_m"]
    )
    check(
        "plate_bolt_edge",
        edge >= p["minimum_hole_edge_ligament_m"] - 1e-12,
        "OSR 12 mm clear hole-edge ligament; geometric screen, not joint resistance",
    )
    check(
        "bolt_bore_ligament",
        bore_gap >= p["minimum_hole_to_bore_ligament_m"],
        "OSR 6 mm clear separation between finished holes",
    )
    check(
        "fastener_head_access",
        head_gap >= 0.005,
        "OSR 5 mm surface gap between bolt-head and locator-head envelopes",
    )
    check(
        "locator_fit",
        clearance_min >= 0 and clearance_max <= p["maximum_diametral_clearance_m"],
        "Worst-case diametral fit using independently bounded +/-2 micrometre size tolerances; no thermal/process credit",
    )
    gap = px - p["support_rail_width_m"]
    required_gap = max(
        p["minimum_underplate_access_m"],
        p["socket_outer_diameter_m"] + 2 * p["socket_side_clearance_m"],
    )
    check(
        "underside_access",
        gap >= required_gap - 1e-12,
        "OSR 100 mm clear support gap for access; also contains 24 mm socket plus 5 mm each side",
    )
    rail_edge = (p["support_rail_width_m"] - hole) / 2
    check(
        "rail_hole_edge",
        rail_edge >= p["minimum_support_hole_edge_ligament_m"],
        "OSR 8 mm clear support-rail hole-edge ligament; resistance unknown",
    )
    # Ideal whole-width strip with supports at OUTER rail edges: retain the
    # longest possible support span; perforations/joint flexibility stay unknown.
    # Central demand is a research operating-load assumption, not clamp preload.
    span = px + p["support_rail_width_m"]
    inertia = length * t**3 / 12
    moment = p["central_load_n"] * span / 4
    stress = moment * (t / 2) / inertia
    deflection = (
        p["central_load_n"] * span**3 / (48 * p["elastic_modulus_pa"] * inertia)
    )
    check(
        "strip_stiffness",
        deflection <= p["deflection_target_m"],
        "1.5 kN central force, E=200 GPa ideal strip and 10 micrometre OSR research target; no holes/contact/bolt flexibility",
    )
    bx = w + 2 * p["blank_each_side_m"] + 2 * p["workholding_each_side_m"]
    by = length + 2 * p["blank_each_side_m"] + 2 * p["workholding_each_side_m"]
    diameter = math.hypot(bx, by)
    height = t + 2 * p["blank_each_side_m"] + p["workholding_height_m"]
    # Gross blank + gross rails + retained pin are conservative loading masses.
    volume = (
        (w + 0.004) * (length + 0.004) * (t + 0.004)
        + 2 * p["support_rail_width_m"] * length * p["support_rail_height_m"]
        + math.pi * 0.016**2 * (t + 0.02)
    )
    mass = volume * p["steel_density_kg_m3"]
    check(
        "machine_workpiece_envelope",
        diameter <= machine["workpiece_diameter_m"]
        and height <= machine["workpiece_height_m"],
        "CV5-500 published diameter/height; square blank and planning clamp margins inside circle, no rotating sweep acceptance",
    )
    check(
        "machine_axis_travel",
        bx <= machine["travel_m"][0]
        and by <= machine["travel_m"][1]
        and height <= machine["travel_m"][2],
        "Conservative fixed-orientation setup bounding box against CV5-500 axis travels",
    )
    check(
        "machine_table_mass",
        mass + p["workholding_mass_kg"] <= machine["workpiece_mass_kg"],
        "Gross cassette blank/rails/pin plus assumed 35 kg workholding against published 200 kg table load",
    )
    for name, basis in [
        (
            "material_and_joint_resistance",
            "No certified grades, bolt preload, pin shear/bearing or thread resistance",
        ),
        (
            "machining_process_qualification",
            "No accepted tooling, NC collision check, two-setup locating trial or measured tolerance capability",
        ),
        (
            "operating_load_acceptance",
            "1.5 kN force and stiffness target are OSR planning inputs awaiting accepted use case",
        ),
        (
            "exact_retention_detail",
            "Washer/screw/chamfer/thread detail remains open; geometry includes retained button blind tap, not a qualified retention assembly",
        ),
    ]:
        checks.append(dict(id=name, status="unknown", basis=basis))
    return dict(
        id=_id(v),
        variables=v,
        metrics=dict(
            minimum_plate_hole_edge_m=edge,
            minimum_hole_to_bore_gap_m=bore_gap,
            fastener_head_gap_m=head_gap,
            minimum_diametral_clearance_m=clearance_min,
            maximum_diametral_clearance_m=clearance_max,
            underside_gap_m=gap,
            strip_span_m=span,
            nominal_strip_stress_pa=stress,
            nominal_strip_deflection_m=deflection,
            gross_blank_and_component_mass_kg=mass,
            machining_setup_diameter_m=diameter,
            machining_setup_height_m=height,
            machining_setup_mass_kg=mass + p["workholding_mass_kg"],
        ),
        checks=checks,
        conditional_screen_feasible=not any(c["status"] == "failed" for c in checks),
        design_complete=False,
        physical_release=False,
    )


def _repairs(candidate, cfg):
    """Generate descendants from the actual failed predicates, not random retry."""
    v = candidate["variables"]
    failed = {c["id"] for c in candidate["checks"] if c["status"] == "failed"}
    proposals = []

    def propose(reason, **changes):
        proposals.append((reason, dict(v, **changes)))

    if "locator_fit" in failed:
        propose("repair worst-case locator interference", stem_diameter_m=0.01999)
    if "underside_access" in failed:
        for pitch in [0.14, 0.16, 0.18]:
            propose("open underside socket/operator access", pitch_x_m=pitch)
    if "plate_bolt_edge" in failed:
        widths = [
            x
            for x in cfg["choices"]["width_m"]
            if x >= v["pitch_x_m"] + 0.009 + 0.024 - 1e-12
        ]
        lengths = [
            x
            for x in cfg["choices"]["length_m"]
            if x >= v["pitch_y_m"] + 0.009 + 0.024 - 1e-12
        ]
        if widths and lengths:
            propose(
                "restore bolt edge distance", width_m=min(widths), length_m=min(lengths)
            )
    if "fastener_head_access" in failed or "bolt_bore_ligament" in failed:
        propose("separate central locator and mounting fasteners", pitch_y_m=0.06)
    if "strip_stiffness" in failed:
        for thickness in cfg["choices"]["plate_m"]:
            if thickness > v["plate_m"]:
                propose(
                    "increase plate inertia after stiffness failure", plate_m=thickness
                )
    if failed & {
        "machine_workpiece_envelope",
        "machine_axis_travel",
        "machine_table_mass",
    }:
        propose(
            "reduce blank to locally machined cassette", width_m=0.22, length_m=0.12
        )
    if not failed:
        # Explore mass/stiffness tradeoffs only after reaching geometric feasibility.
        for thickness in cfg["choices"]["plate_m"]:
            propose("explore stiffness/mass tradeoff", plate_m=thickness)
        for pitch in [0.14, 0.16, 0.18]:
            propose("explore access/span tradeoff", pitch_x_m=pitch)
        for width in [0.18, 0.2, 0.22, 0.24]:
            propose("explore edge distance/blank mass tradeoff", width_m=width)
    return proposals


def search(*, budget=128):
    if (
        not isinstance(budget, int)
        or isinstance(budget, bool)
        or not 1 <= budget <= 4096
    ):
        raise ValueError("budget must be an integer from 1 to 4096")
    cfg = _read()
    queue = deque([(cfg["seed"], None, 0, "initial retained-locator cassette study")])
    seen, candidates = set(), []
    while queue and len(candidates) < budget:
        variables, parent, generation, reason = queue.popleft()
        if any(value not in cfg["choices"][name] for name, value in variables.items()):
            raise ValueError("generated proposal outside the declared search choices")
        identity = _id(variables)
        if identity in seen:
            continue
        seen.add(identity)
        candidate = evaluate(variables)
        candidate.update(
            parent_ids=[] if parent is None else [parent],
            generation=generation,
            generation_reason=reason,
        )
        candidates.append(candidate)
        for repair, child in _repairs(candidate, cfg):
            if _id(child) not in seen:
                queue.append((child, identity, generation + 1, repair))
    feasible = [c for c in candidates if c["conditional_screen_feasible"]]
    selected = []
    if feasible:
        selected.append(
            min(
                feasible,
                key=lambda c: (
                    c["metrics"]["gross_blank_and_component_mass_kg"],
                    c["id"],
                ),
            )["id"]
        )
        stiffest = min(
            feasible,
            key=lambda c: (
                c["metrics"]["nominal_strip_deflection_m"],
                c["metrics"]["gross_blank_and_component_mass_kg"],
                c["id"],
            ),
        )["id"]
        if stiffest not in selected:
            selected.append(stiffest)
    return dict(
        schema="osr-generative-mechanical-report/1",
        scope=cfg["scope"],
        candidates=candidates,
        selected_candidate_ids=selected,
        termination=dict(
            reason="budget_exhausted" if queue else "feedback_frontier_exhausted",
            evaluation_budget=budget,
            evaluations=len(candidates),
            pending_proposals=len(queue),
            conditional_feasible_count=len(feasible),
            complete_solution_found=False,
        ),
        sources=cfg["equipment"],
        input_sha256={
            str(SPACE.relative_to(Path(__file__).parents[2])): hashlib.sha256(
                SPACE.read_bytes()
            ).hexdigest(),
            str(REFERENCE.relative_to(Path(__file__).parents[2])): hashlib.sha256(
                REFERENCE.read_bytes()
            ).hexdigest(),
        },
        required_evidence=cfg["required_evidence"],
        design_complete=False,
        physical_release=False,
    )


def model(candidate):
    """Executable primitive geometry, sharing selected dimensions with all checks."""
    v = candidate["variables"]
    w, l, t, px, py = (
        v[k] for k in ["width_m", "length_m", "plate_m", "pitch_x_m", "pitch_y_m"]
    )
    holes = [dict(x_m=w / 2, y_m=l / 2, diameter_m=0.02)]
    holes += [
        dict(x_m=w / 2 + x, y_m=l / 2 + y, diameter_m=0.009)
        for x in [-px / 2, px / 2]
        for y in [-py / 2, py / 2]
    ]
    parts = [
        dict(
            id="mount-plate",
            kind="box",
            role="designed-steel",
            at_m=[-w / 2, -l / 2, 0.1],
            size_m=[w, l, t],
            holes=holes,
        )
    ]
    for i, x in enumerate([-px / 2, px / 2]):
        parts.append(
            dict(
                id=f"support-rail-{i}",
                kind="box",
                role="designed-steel",
                at_m=[x - 0.02, -l / 2, 0.06],
                size_m=[0.04, l, 0.04],
                holes=[
                    dict(x_m=0.02, y_m=l / 2 + y, diameter_m=0.009)
                    for y in [-py / 2, py / 2]
                ],
            )
        )
    parts.append(
        dict(
            id="retained-headed-locator",
            kind="stepped-cylinder",
            role="designed-steel",
            at_m=[-0.016, -0.016, 0.1],
            size_m=[0.032, 0.032, t + 0.02],
            steps=[
                dict(diameter_m=v["stem_diameter_m"], length_m=t),
                dict(diameter_m=0.032, length_m=0.02),
            ],
            holes=[dict(x_m=0.016, y_m=0.016, diameter_m=0.0068, length_m=0.016)],
        )
    )
    for i, (x, y) in enumerate(
        (x, y) for x in [-px / 2, px / 2] for y in [-py / 2, py / 2]
    ):
        parts.append(
            dict(
                id=f"M8-thread-envelope-{i}",
                kind="cylinder",
                role="fastener-envelope",
                at_m=[x - 0.004, y - 0.004, 0.055],
                size_m=[0.008, 0.008, t + 0.045],
            )
        )
        parts.append(
            dict(
                id=f"M8-head-envelope-{i}",
                kind="cylinder",
                role="fastener-envelope",
                at_m=[x - 0.008, y - 0.008, 0.1 + t],
                size_m=[0.016, 0.016, 0.008],
            )
        )
    return dict(
        id="OSR-GENERATIVE-" + candidate["id"],
        parts=parts,
        interference_roles=["designed-steel"],
        manufacturing_released=False,
        omissions=[
            "Retaining washer/screw detail and nut/thread engagement remain unqualified",
            "Bolt shapes are envelopes; grades, preload and bearing/contact resistance unknown",
            "Plate strip model neglects perforations, local contact and joint flexibility",
        ],
    )


def write_artifacts(report, output: Path):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    paths = []
    for candidate in report["candidates"]:
        if candidate["id"] in report["selected_candidate_ids"]:
            folder = output / candidate["id"]
            folder.mkdir(exist_ok=True)
            target = folder / "model.json"
            target.write_text(
                json.dumps(model(candidate), indent=2, sort_keys=True) + "\n"
            )
            paths.append(target)
    return paths
