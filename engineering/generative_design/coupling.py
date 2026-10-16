"""Proposed beam force changes feed bounded gross stressing-rail sensitivities."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from engineering.factory_examples import development
from .coverage import ROOT


def search(civil_report):
    a = json.loads((ROOT / "engineering/factory_examples/data/basis.json").read_text())[
        "assumptions"
    ]
    cfg = json.loads(
        (ROOT / "engineering/factory_examples/data/development.json").read_text()
    )["bed"]
    length = cfg["active_length_m"]
    springs = [x - cfg["origin_x_m"] for x in cfg["brace_stations_m"]]
    selected = set(civil_report["selected_candidate_ids"])
    rows = []
    for beam in civil_report["candidates"]:
        if beam["id"] not in selected:
            continue
        total = beam["metrics"]["initial_bed_force_n"]
        for wall in (0.016, 0.020, 0.025):
            B, H = 0.3, 0.5
            area = B * H - (B - 2 * wall) * (H - 2 * wall)
            inertias = [
                (H * B**3 - (H - 2 * wall) * (B - 2 * wall) ** 3) / 12,
                (B * H**3 - (B - 2 * wall) * (H - 2 * wall) ** 3) / 12,
            ]
            for stiffness in (1e5, 1e6, 1e7):
                critical = [
                    development.column_buckling(
                        length,
                        a["steel_elastic_modulus_pa"],
                        inertia,
                        cfg["elements"],
                        [(x, stiffness) for x in springs],
                    )
                    for inertia in inertias
                ]
                factor = min(critical) / (total / 2)
                variables = dict(
                    beam=beam["id"], wall_m=wall, hypothetical_spring_n_m=stiffness
                )
                row = dict(
                    id="bed-"
                    + hashlib.sha256(
                        json.dumps(variables, sort_keys=True).encode()
                    ).hexdigest()[:12],
                    variables=variables,
                    initial_bed_force_n=total,
                    per_rail_compression_n=total / 2,
                    minimum_elastic_eigenvalue_factor=factor,
                    nominal_axial_stress_pa=total / (2 * area),
                    known_two_rail_mass_kg=2 * length * area * a["steel_density_kg_m3"],
                    checks=dict(
                        gross_elastic_stability=dict(
                            state="passed" if factor > 1 else "failed",
                            basis="Euler-Bernoulli rails with inherited ideal end pins and hypothetical intermediate springs; factor >1 is a numerical stability screen, not code resistance",
                        )
                    ),
                    actual_ground_stiffness_n_m=None,
                    accepted_rail_resistance_n=None,
                    complete_bed_qualified=False,
                    physical_release=False,
                )
                rows.append(row)
    selected_ids = []
    for beam in sorted(selected):
        stable = [
            r
            for r in rows
            if r["variables"]["beam"] == beam
            and r["checks"]["gross_elastic_stability"]["state"] == "passed"
        ]
        if stable:
            selected_ids.append(
                min(
                    stable,
                    key=lambda r: (
                        r["known_two_rail_mass_kg"],
                        r["variables"]["hypothetical_spring_n_m"],
                    ),
                )["id"]
            )
    return dict(
        schema="osr-generative-bed-coupling/1",
        candidates=rows,
        selected_candidate_ids=selected_ids,
        basis="Beam force propagated to two symmetric axial return rails; no inherited bed capacity or adopted stiffness",
        remaining_gates=[
            "New strand/grip/jack pattern, head/diaphragm force and eccentricity, plate/weld/local and staged resistance",
            "Return-axis and new mould, rail splices, post/base/anchor/ground redesign; measured spring stiffness",
            "Complete product mass, inserts, rig, crane/headroom, logistics and erection",
        ],
        design_complete=False,
        physical_release=False,
    )
