"""Reconcile installed train weights and individual axle readings for the proposed Airport car."""

import argparse
import json
from pathlib import Path
import tomllib

from cities.Baghdad import airport_finance, airport_opening, airport_integration
from cities.Baghdad.engineering.mechanical.civil.develop_civil import box_screen
from cities.Baghdad.engineering.mechanical.vehicle.power_interface import mass_form, mass_return
from cities.Baghdad.engineering.prototype import car, commercial


def axle_positions(record):
    centres = record["interfaces"]["formation_body_from_car_x_m"]
    offsets = record["interfaces"]["body_from_axle_x_m"]
    return {f"C{i}-A{j}": cx + dx for i, cx in enumerate(centres, 1) for j, dx in enumerate(offsets, 1)}


def form(record):
    basis = {
        "candidate_id": record["candidate_id"],
        "frame_revision": record["frame_revision"],
        "opening_evaluation_id": record["opening"]["evaluation_id"],
    }
    return {
        "basis": basis,
        "documents": {},
        "mass_groups": mass_form(basis),
        "axle_weighing": {
            "tare_document": None,
            "loaded_document": None,
            "balance_limit_document": None,
            "permitted_total_discrepancy_kg": None,
            "readings": {ax: {"tare_kg": None, "loaded_kg": None} for ax in axle_positions(record)},
        },
    }


def moving_span(axles, span, overhang):
    """Point-axle train crossing both ideal supports and both overhangs.

    Within each interval of unchanged support/load order, reactions are affine in
    train position. Moment at a moving axle or support is at most quadratic.
    Sweep both orientations, exact events and the adjacent one-sided limits.
    """
    if not axles or span <= 0 or overhang < 0:
        raise ValueError("Need a loaded train and a valid span")
    extrema = {}

    def update(key, value, pose):
        if key not in extrema or (
            (value > extrema[key][0]) if key.startswith("max") else (value < extrema[key][0])
        ):
            extrema[key] = (value, pose)

    for direction in (1, -1):
        train = [(direction * x, f, name) for name, x, f in axles]
        events = sorted(
            {round(b - x, 10) for x, _, _ in train for b in (-overhang, 0, span, span + overhang)}
        )

        def occupants(p):
            return [row for row in train if -overhang - 1e-9 <= row[0] + p <= span + overhang + 1e-9]

        def sample(p, live, section):
            loads = [(x + p, f, name) for x, f, name in live]
            right = sum(x * f / span for x, f, _ in loads)
            left = sum(f for _, f, _ in loads) - right
            x = section + p if isinstance(section, float) else (0 if section == "left" else span)
            moment = (
                left * max(x, 0) + right * max(x - span, 0) - sum(f * max(x - a, 0) for a, f, _ in loads)
            )
            return left, right, moment, x

        def evaluate_interval(a, b, live):
            for section in ["left", "right", *(float(x) for x, _, _ in live)]:
                p0, pm, p1 = [sample(p, live, section)[2] for p in (a, (a + b) / 2, b)]
                quad = 2 * (p0 + p1 - 2 * pm)
                slope = p1 - p0 - quad
                poses = [a, b]
                if a != b and abs(quad) > 1e-9:
                    t = -slope / (2 * quad)
                    if 0 < t < 1:
                        poses.append(a + t * (b - a))
                for p in poses:
                    left, right, moment, x = sample(p, live, section)
                    pose = {
                        "direction": direction,
                        "train_centre_m": round(p, 6),
                        "loaded_axles": [name for _, _, name in live],
                    }
                    for end, f in (("left", left), ("right", right)):
                        for prefix in ("min", "max"):
                            update(prefix + "_reaction", f, dict(pose, end=end))
                    for prefix in ("min", "max"):
                        update(prefix + "_moment", moment, dict(pose, section_x_m=round(x, 6)))

        for a, b in zip(events, events[1:]):
            evaluate_interval(a, b, occupants((a + b) / 2))
        for a in events:
            evaluate_interval(a, a, occupants(a))
    return {key: {"value": round(value, 6), "pose": pose} for key, (value, pose) in extrema.items()}


def assess(record, submission, *, directory=None, inputs=None, service=None):
    template = form(record)
    if (
        record["evaluation_id"]
        != car.identity({k: v for k, v in record.items() if k != "evaluation_id"})
        or not isinstance(submission, dict)
        or submission.keys() != template.keys()
        or submission["basis"] != template["basis"]
    ):
        raise ValueError("Weight return must match the prototype and evaluation")
    docs = commercial.evidence(submission["documents"], directory)
    groups = mass_return(submission["mass_groups"], template["basis"])
    for row in groups["weight_return"]["train_mass_groups"].values():
        if row["kg"] is not None and row["evidence"] not in docs:
            raise ValueError("Each returned mass group needs its source attachment")
    missing = list(groups["missing_groups"])
    scales = submission["axle_weighing"]
    if not isinstance(scales, dict) or scales.keys() != template["axle_weighing"].keys():
        raise ValueError("Expected the prototype axle weighing fields")
    positions = axle_positions(record)
    readings = scales["readings"]
    if not isinstance(readings, dict) or readings.keys() != positions.keys():
        raise ValueError("Retain the axle identifiers and car order on the form")
    for name, row in readings.items():
        if not isinstance(row, dict) or row.keys() != {"tare_kg", "loaded_kg"}:
            raise ValueError("Each axle needs empty and loaded mass fields")
        for key, value in row.items():
            if value is not None:
                commercial.number(value, name + " " + key, positive=True)
    used = any(v is not None for row in readings.values() for v in row.values()) or any(
        scales[k] is not None for k in scales if k != "readings"
    )
    if used:
        for key in ("tare_document", "loaded_document", "balance_limit_document"):
            if scales[key] is None:
                missing.append(key)
            elif scales[key] not in docs:
                raise ValueError("Axle weighing and balance tolerance require original attachments")
        if scales["permitted_total_discrepancy_kg"] is None:
            missing.append("permitted_total_discrepancy_kg")
        else:
            commercial.number(scales["permitted_total_discrepancy_kg"], "permitted total discrepancy")
        missing += [f"{name}.{k}" for name, row in readings.items() for k, v in row.items() if v is None]
    source_files = [
        Path(__file__),
        Path(commercial.__file__),
        Path(airport_opening.__file__),
        Path(airport_finance.__file__),
        car.CITY / "engineering/mechanical/civil/develop_civil.py",
        car.CITY / "engineering/mechanical/vehicle/power_interface.py",
    ]
    response = {
        "source_sha256": {
            p.relative_to(car.ROOT).as_posix(): car.sha(p.read_bytes()) for p in source_files
        },
        "parent_candidate_id": record["candidate_id"],
        "submission_id": car.identity(submission),
        "missing": missing,
        "evidence_documents": docs,
        "physical_accepted": False,
        "mass_account": groups,
        "opening": None,
        "finance": None,
        "axle_civil": None,
        "result": "partial return",
    }
    if not missing:
        inputs = inputs or airport_opening.opening_inputs()
        service = service or airport_integration.build()["service"]
        if service["evaluation_id"] != record["parent_service_evaluation_id"] or service[
            "evaluation_id"
        ] != car.identity({k: v for k, v in service.items() if k != "evaluation_id"}):
            raise ValueError("Use the matching Airport timetable for the returned weights")
        kg = groups["returned_crowd_train_kg"]
        if used:
            tolerance = scales["permitted_total_discrepancy_kg"]
            totals = {k: sum(row[k] for row in readings.values()) for k in ("tare_kg", "loaded_kg")}
            if (
                abs(totals["tare_kg"] - groups["returned_tare_kg"]) > tolerance
                or abs(totals["loaded_kg"] - kg) > tolerance
            ):
                raise ValueError("Axle sum and group weights exceed the documented balance tolerance")
            schedule = json.loads((car.CITY / "engineering/mechanical/schedule.json").read_bytes())
            cfg = tomllib.loads((car.CITY / "engineering/mechanical/civil/concept.toml").read_text())
            track = dict(schedule["viaduct"])
            live = dict(track["moving_gravity_only"])
            span, overhang = track["effective_span_m_hypothesis"], live["stock_overhang_per_end_m"]
            gravity = cfg["materials"]["gravity_m_s2"]
            forces = [(ax, x, readings[ax]["loaded_kg"] * gravity / 1000) for ax, x in positions.items()]
            envelope = moving_span(forces, span, overhang)
            track["moving_gravity_only"] = {
                "stock_overhang_per_end_m": overhang,
                "max_end_reaction_kn_sampled": envelope["max_reaction"]["value"],
                "max_live_moment_knm_sampled": envelope["max_moment"]["value"],
            }
            beam = box_screen(cfg["box"], cfg["materials"], track, cfg["pier"])
            response["axle_civil"] = {
                "axle_sum_kg": totals,
                "loaded_minus_group_total_kg": totals["loaded_kg"] - kg,
                "tare_minus_group_total_kg": totals["tare_kg"] - groups["returned_tare_kg"],
                "equal_axle_kg": kg / len(forces),
                "measured_max_axle_kg": max(row["loaded_kg"] for row in readings.values()),
                "gravity_envelope": envelope,
                "updated_beam_and_pier": beam,
                "scope": "Both directions under the supplied axle weights. Global box and concentric foundation screen only. Side-to-side wheel split, dynamic interaction, twist, local anchors, load combinations and site bearing capacity remain open.",
            }
        physical_basis = car.identity(
            {
                "group_kg": {
                    k: r["kg"] for k, r in groups["weight_return"]["train_mass_groups"].items()
                },
                "axle_kg": readings if used else None,
            }
        )
        try:
            opening = airport_opening.calculate(
                inputs=inputs,
                service=service,
                size_feeder=True,
                loaded_mass_t=kg / 1000,
                vehicle_revision=record["frame_revision"],
                mass_basis_id=physical_basis,
            )
        except ValueError as error:
            if not str(error).startswith("No priceable supply design"):
                raise
            response.update(result="feeder design held", engineering_hold=str(error))
        else:
            response.update(
                result="planning recalculation",
                opening=opening,
                finance=airport_finance.evaluate(
                    opening, inputs[0], inputs[0]["service_plan"]["departures_per_hour_direction"]
                ),
            )
        response["scope"] = (
            "Supplier declarations and weighed-article records are attached for independent authentication. "
            "The track screen uses returned axle loads when available. Fleet rates and civil costs use the opening's planning allowances; "
            "review site foundations, fatigue, brake duty and equipment changes before pricing the measured load as a selected design."
        )
    response["evaluation_id"] = car.identity(response)
    return response


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--return-file", type=Path)
    parser.add_argument("--attachments", type=Path)
    args = parser.parse_args()
    record = car.build(airport_integration.build())
    result = (
        form(record)
        if args.return_file is None
        else assess(record, json.loads(args.return_file.read_bytes()), directory=args.attachments)
    )
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
