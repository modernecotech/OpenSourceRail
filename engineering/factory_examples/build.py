"""Build/check the dimensioned factory examples and their review artifacts.

Run from the repository: .venv/bin/python -m engineering.factory_examples.build
Add --native for actual FreeCAD/STEP export, or --check for drift verification.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import csv
import hashlib
import html
import io
import json
from pathlib import Path

from . import models
from . import development
from . import connections
from .figures import development_svg, connections_svg
from .native import digest, generate

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
DEFAULT = PACKAGE / "examples"


def json_text(value):
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def csv_text(rows):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def source_hashes():
    paths = [
        *PACKAGE.glob("*.py"),
        *PACKAGE.glob("data/*.json"),
        ROOT / "lib/templates/baghdad-factory.toml",
        ROOT / "design/component-catalogue/src/osr_mech/civil/decked_pi.py",
        ROOT / "engineering/industrialisation/assembly.py",
        ROOT / "engineering/industrialisation/common.py",
        ROOT / "engineering/design_engine/civil_qualification.py",
        ROOT / "engineering/design_engine/contracts.py",
        ROOT / "design/component-catalogue/src/osr_mech/freecad_assembly_review.py",
    ]
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths)}


def plan_svg(layout, scene):
    W, H = layout["size_m"]
    scale = 7

    def text(x, y, s, **kw):
        attrs = " ".join(f'{k.replace("_","-")}="{v}"' for k, v in kw.items())
        return f'<text x="{x}" y="{y}" {attrs}>{html.escape(s)}</text>'

    bits = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-35 -45 {W*scale+70} {H*scale+100}" role="img" aria-label="{layout["id"]} dimensioned reservations">',
        "<style>text{font-family:Arial,sans-serif;fill:#142c39;font-size:10px}.title{font-size:18px;font-weight:bold}.aisle{fill:#d6e0e5}.cell{fill:#d9eee5}.zone:hover{stroke:#064e3b;stroke-width:3}</style>",
        f'<rect width="{W*scale}" height="{H*scale}" fill="#f5f8fa" stroke="#173a4a"/>',
        text(
            0,
            -22,
            layout["id"].replace("-", " ").title() + f" — {W} × {H} m",
            class_="title",
        ),
    ]
    for row in layout["zones"]:
        x, y, w, h = [v * scale for v in row["rect_m"]]
        cls = (
            "aisle"
            if any(
                k in row["id"]
                for k in ("haul", "transfer", "transport", "pedestrian", "exclusion")
            )
            else "cell"
        )
        bits.append(
            f'<g class="zone"><title>{html.escape(row["label"])}; {row["rect_m"][2]} × {row["rect_m"][3]} m</title><rect x="{x}" y="{y}" width="{w}" height="{h}" class="{cls}" stroke="#647e88"/>'
        )
        label_y = y + h - 15 if row["equipment"] else y + 13
        bits.append(text(x + 3, label_y, row["id"]))
        bits.append(
            text(x + 3, label_y + 12, f'{row["rect_m"][2]} × {row["rect_m"][3]} m')
        )
        bits.append("</g>")
    for p in scene["parts"]:
        if p["role"] not in {
            "supplier-envelope",
            "auxiliary-reservation",
            "mould-reservation",
        }:
            continue
        x, y, _ = p["at_m"]
        w, h, _ = models.global_size(p)
        bits.append(
            f'<g><title>{html.escape(p["id"])}: {w:g} × {h:g} m; {html.escape(p.get("basis",p["role"]))}</title><rect x="{x*scale:.3f}" y="{y*scale:.3f}" width="{w*scale:.3f}" height="{h*scale:.3f}" fill="#174e63" fill-opacity="0.35" stroke="#174e63" stroke-dasharray="3 2"/></g>'
        )
    bits.extend(
        [
            text(
                0,
                H * scale + 20,
                "Cells include planning service space. Verify egress, separation, swept paths, buried services and hook coverage.",
            ),
            text(
                0,
                H * scale + 35,
                "OSR engineering reservations · metre coordinates · unissued · 2026-10-16",
            ),
            "</svg>",
        ]
    )
    return "\n".join(bits) + "\n"


def projection_svg(model):
    # Orthographic x/z elevation and x/y plan, metres mapped to pixels.
    is_fixture = model["id"] == "OSR-FIX-500"
    scale = 240 if is_fixture else 27
    width = 1050
    bits = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 900" role="img" aria-label="{model["id"]} development drawing">',
        "<style>text{font:14px Arial,sans-serif;fill:#163747}.head{font-size:22px;font-weight:bold}</style>",
        f'<text class="head" x="30" y="35">{model["id"]} — geometry coordination</text>',
        '<text x="30" y="60">Unissued development model · dimensions in metres · details/assumptions in model.json</text>',
    ]
    for title, vertical, ox, oy in (
        ("PLAN X/Y", 1, 330 if is_fixture else 100, 280),
        ("ELEVATION X/Z", 2, 330 if is_fixture else 100, 790),
    ):
        bits.append(f'<text x="30" y="{100 if vertical==1 else 500}">{title}</text>')
        for p in model["parts"]:
            dims = list(p["size_m"])
            axis = p.get("cylinder_axis", "z")
            if p["kind"] == "cylinder" and axis != "z":
                dims = [p["size_m"][0]] * 3
                dims["xyz".index(axis)] = p["size_m"][2]
            x = ox + p["at_m"][0] * scale
            y = oy - (p["at_m"][vertical] + dims[vertical]) * scale
            fill = "#8baba0" if p["kind"] == "tube" else "#d2d9d8"
            if p["role"] == "strand-envelope":
                fill = "#aa633b"
            bits.append(
                f'<g><title>{html.escape(p["id"])}; {p["size_m"]} m; {p["role"]}</title><rect x="{x:.3f}" y="{y:.3f}" width="{dims[0]*scale:.3f}" height="{dims[vertical]*scale:.3f}" stroke="#214653" stroke-width="0.6" fill="{fill}" fill-opacity="0.5"/></g>'
            )
    label = (
        "Frame 1.600 × 1.000 m; RHS 100 × 50 × 5 mm idealised; four 200 × 160 × 20 mm feet with 18 mm holes"
        if is_fixture
        else "Pi25: 25.000 × 2.900 × 1.155 m; conceptual mould and 27 m stressing-bed reservation"
    )
    bits.append(f'<text x="30" y="845">{html.escape(label)}</text>')
    bits.append(
        '<text x="30" y="875">Envelope projections; inspect native model for holes/hollows. No fabrication tolerances or release implied.</text></svg>'
    )
    return "\n".join(bits) + "\n"


def process_routes():
    # Hold points are requirements for future trials, never completed inspection records.
    rows = [
        (
            "fixture-10",
            "fixture",
            "Receive RHS/plate/pin stock",
            "tata-celsius",
            "Check certificates, exact corner properties, grade, straightness and origin; reject substitutions pending review",
        ),
        (
            "fixture-20",
            "fixture",
            "Cut RHS per fixture-bom.csv",
            "prosaw-bomar-510",
            "Verify blade/clamping trial, burr removal, square ends and cut-length tolerances; do not infer rate from motor power",
        ),
        (
            "fixture-30",
            "fixture",
            "Cut 20 mm mounting and foot plates",
            "esprit-photon-3015",
            "Prove alloy/thickness/edge quality and assist gas; if laser process unqualified, buy machined blanks",
        ),
        (
            "fixture-40",
            "fixture",
            "Drill/ream locator bores and anchor clearance holes",
            "mazak-cv5-500",
            "Trial fixture/stock/probe/tool access; pin fit, retention and finished tolerances require detail drawing",
        ),
        (
            "fixture-50",
            "fixture",
            "Dry assemble/tack frame; controlled opposing weld sequence",
            "oxford-multimig-333",
            "Qualify joint design/WPS/operator; use temporary squaring jig and record before/after distortion; no weld capacity assumed",
        ),
        (
            "fixture-60",
            "fixture",
            "Inspect datum plates/pins then survey assembled fixture",
            "aberlink-axiom-900",
            "Condition small parts; assembled fixture exceeds CMM range: separate survey equipment/procedure required",
        ),
        (
            "fixture-70",
            "fixture",
            "Fit clamps/retention/anchors; first-article load and repeatability trials",
            "brauer-h350-2blc (candidate); retention/anchors unselected",
            "Approve clamp/joint/anchor details before loading; define proof protocol, exclusion and acceptance criteria; not performed",
        ),
        (
            "panel-10",
            "panel",
            "Pilot injection/cure trials on representative mould",
            "ciject-1 + airflow-oven",
            "Select resin and machine variant; qualify cure, extraction/fire conditions, release, dimensions and railway fire performance",
        ),
        (
            "beam-10",
            "Pi20/Pi25",
            "Prepare mould, reinforcements and prestress strand",
            "matravers-pi25",
            "Approve mould/bed and concrete/strand design; verify cover, anchors, dimensional survey, release agent and exclusion zone",
        ),
        (
            "beam-20",
            "Pi20/Pi25",
            "Calibrate, stress and record every tendon",
            "ccl-sla15",
            "Select matched pretensioning system and actual strand/grips; verify bed forces, bracing and abutment resistance before stressing",
        ),
        (
            "beam-30",
            "Pi20/Pi25",
            "Batch/place/consolidate concrete with samples",
            "rapid-planetary",
            "Prove mix/cycle/workability/temperature, joints and full batching system; developed Pi25 needs at least 33 one-m3 batches without waste allowance",
        ),
        (
            "beam-40",
            "Pi20/Pi25",
            "Cure, verify transfer strength, controlled prestress release",
            "unselected",
            "Measured maturity/strength and approved release sequence control; two-working-day bed occupation is a planning hypothesis",
        ),
        (
            "beam-50",
            "Pi20/Pi25",
            "Strip, inspect geometry/cracks and approve lifting",
            "street-open-winch",
            "Approve lifting inserts/rigging and exact crane/runway; developed Pi25 scalar demand 103.56 t does not establish lift safety",
        ),
        (
            "beam-60",
            "Pi20/Pi25",
            "Store/transport/erect using designed supports",
            "unselected",
            "Approve storage stability/support spacing, trailer/axle loads, route survey and erection method; four storage positions only",
        ),
    ]
    return [
        dict(
            id=i,
            product=p,
            operation=o,
            equipment=e,
            required_hold_point=h,
            completed="no",
        )
        for i, p, o, e, h in rows
    ]


def rfq_rows(equipment):
    rows = []
    common = "Confirm exact model/options; UK factory and origin; Baghdad delivery/install/training/spares/service; itemised price and Incoterms; GA/foundations; connected utilities and ambient derating; FAT/SAT criteria"
    for e in equipment:
        quantity, quantity_unit, quantity_scope = {
            "brauer-h350-2blc": (
                3,
                "hold-down clamp candidates",
                "one development fixture; requested preload 500 N each, actual spindle force and mount details unqualified",
            ),
            "matravers-pi25": (
                4,
                "casting mould positions",
                "pilot yard only; Pi20 conversion arrangement to confirm",
            ),
            "street-open-winch": (
                2,
                "configured crane enquiries",
                "one 30 m-span runway bay per paired casting column; coverage/support design open",
            ),
            "ccl-sla15": (
                192,
                "nonstressing-end grip candidates",
                "four development beds x 48 strands, conditional on exact strand compatibility; baseline was 40/bed; live-end grips/jacks separate and unselected",
            ),
            "tata-celsius": (
                2,
                "6 m nominal RHS bars",
                "one fixture only; exact stock/corner/length certificate pending",
            ),
        }.get(e["id"], (1, "unit or package enquiry", "pilot factory example only"))
        rows.append(
            dict(
                id=e["id"],
                supplier=e["supplier"],
                model=e["model"],
                origin=e["origin"],
                process=e["process"],
                quantity=quantity,
                quantity_unit=quantity_unit,
                quantity_scope=quantity_scope,
                published_specifications=json.dumps(e["published"], sort_keys=True),
                osr_planning_allowances=json.dumps(e["planning"], sort_keys=True),
                technical_questions="; ".join(e["unknown"]),
                commercial_questions=common,
                source=" | ".join(e["sources"]),
                source_locator=e["source_locator"],
                observed_on="2026-10-16",
                supplier_contacted="no",
                offered_price_gbp="",
            )
        )
    return rows


def make_outputs():
    basis = json.loads((PACKAGE / "data/basis.json").read_text())
    register = json.loads((PACKAGE / "data/equipment.json").read_text())
    a = basis["assumptions"]
    for key, value in a.items():
        if key != "fixture_payload_cg_xy_m":
            models.positive(value, key)
    if a["bed_positions"] != 4:
        raise ValueError(
            "Four-position pilot layout: revise geometry before changing position count"
        )
    pi = models.pi
    if (
        pi.DECK_WIDTH_MM,
        pi.FLANGE_THICKNESS_MM,
        pi.STEM_WIDTH_MM,
        pi.STEM_DEPTH_MM,
        pi.STEM_CENTRE_OFFSET_MM,
        pi.END_DIAPHRAGM_LENGTH_MM,
    ) != (2900, 220, 300, 935, 717.5, 550):
        raise ValueError(
            "Canonical pi section changed: revise mould/bed coordination before publication"
        )
    capacity = models.capacity(a)  # Validate fractions before downstream use.
    equipment = {e["id"]: e for e in register["equipment"]}
    if len(equipment) != len(register["equipment"]):
        raise ValueError("unique equipment identities required")
    fix = models.fixture(a)
    civil = models.civil(a)
    development_basis = json.loads((PACKAGE / "data/development.json").read_text())
    iteration = development.build(a, development_basis, fix, civil, equipment)
    candidate = next(
        r
        for r in iteration["prestress"]["alternatives"]
        if r["id"] == iteration["prestress"]["candidate_id"]
    )
    connection_basis = json.loads((PACKAGE / "data/connections.json").read_text())
    fabrication_suppliers = json.loads(
        (PACKAGE / "data/fabrication-suppliers.json").read_text()
    )
    fabrication = connections.build(
        a, connection_basis, candidate, iteration, equipment, fabrication_suppliers
    )
    layout = models.layouts(ROOT)
    canonical = layout["canonical_factory"]["factory"]
    if (
        canonical["family"],
        canonical["trainset_bay_length_m"],
        canonical["trainset_bay_width_m"],
    ) != ("metro-6car", 135, 6.5):
        raise ValueError("canonical factory changed: revise layout before publication")
    scenes = {
        k: models.factory_scene(
            layout[k],
            equipment,
            roof_load_pa=a["roof_dead_load_pa"],
            slab_thickness=a["factory_slab_thickness_m"],
        )
        for k in ("vehicle", "precast")
    }
    native_models = {
        "fixture": fix,
        "pi25-mould-bed": dict(id="OSR-Pi25-MOULD-BED", parts=models.mould_bed()),
        "vehicle-factory": scenes["vehicle"],
        "precast-yard": scenes["precast"],
        "fixture-workholding": dict(
            id="OSR-FIX-500-WORKHOLDING",
            parts=development.workholding_parts(fix, development_basis["fixture"]),
        ),
        "pi25-revised-bed": dict(
            id="OSR-Pi25-REVISED-BED",
            parts=development.revised_bed_parts(
                models.mould_bed(), candidate, development_basis["bed"]
            ),
        ),
        "runway-bay": dict(
            id="OSR-RUNWAY-BAY",
            parts=development.runway_parts(development_basis["runway"]),
        ),
        "strongback-end": dict(
            id="OSR-ALIGNED-STRONGBACK-END",
            parts=connections.strongback_parts(
                connection_basis["strongback"], fabrication["strongback"]
            ),
            interference_roles=["strongback-steel", "return-rail-steel", "post-steel"],
        ),
        "locator-cartridge": dict(
            id="OSR-LOCATOR-RETENTION-COUPON",
            parts=connections.locator_parts(connection_basis["locator"]),
            interference_roles=["locator-support-steel", "locator-machined-steel"],
        ),
    }
    utilities = []
    for e in register["equipment"]:
        pub = e["published"]
        # Unknowns stay null. An output motor rating or fuse is never converted to input demand.
        utilities.append(
            dict(
                id=e["id"],
                input_kva_max=pub.get("input_kva_range", [None, None])[-1],
                air_l_min=pub.get("air_l_min"),
                air_bar=pub.get("air_bar"),
                connected_load_complete=False,
                temperature_c=pub.get(
                    "operating_temperature_c", pub.get("optimum_temperature_c")
                ),
                utility_gaps=e["unknown"],
            )
        )
    report = dict(
        schema="osr-factory-development-examples/1",
        revision=basis["revision"],
        design_basis=basis,
        source_sha256=source_hashes(),
        canonical_vehicle_scope=canonical,
        fixture={k: v for k, v in fix.items() if k != "parts"},
        civil=civil,
        capacity=capacity,
        capability=models.capability(equipment, fix),
        layouts={k: layout[k] for k in ("vehicle", "precast")},
        building_screen=scenes["vehicle"]["building_screen"],
        utilities=utilities,
        costs=dict(
            installed_capex_gbp=None,
            complete=False,
            dated_uk_retail_reference_only=dict(
                id="oxford-multimig-333", gbp_ex_vat=2640, observed_on="2026-10-16"
            ),
            unknown_categories=[
                "most machine prices",
                "tooling and software",
                "extraction and guarding",
                "MEP and foundations",
                "handling",
                "freight/duties",
                "installation and training",
                "qualification",
                "spares",
                "working capital",
            ],
        ),
        test_infrastructure=dict(
            track_count=canonical["test_tracks"],
            each_track_length_m=canonical["test_track_length_m"],
            included_in_hall_layout=False,
            land_and_alignment_unknown=True,
        ),
        physical_release=False,
        supplier_contacted=False,
        development=development_summary(iteration),
        fabrication_summary=dict(
            revision=fabrication["revision"],
            results_reference="connections.json",
            physical_release=False,
        ),
    )
    bom = []
    for p in fix["parts"]:
        bom.append(
            dict(
                id=p["id"],
                kind=p["kind"],
                dimensions_m=" x ".join(str(v) for v in p["size_m"]),
                cut_length_m=p["size_m"][p["axis"]] if p["kind"] == "tube" else "",
                nominal_volume_m3=volume if (volume := models.volume(p)) else 0,
                nominal_mass_kg=volume * a["steel_density_kg_m3"],
                holes=json.dumps(p.get("holes", [])),
                stock_basis=fix["geometry_basis"],
            )
        )
    out = {
        "report.json": json_text(report),
        "equipment-rfq.csv": csv_text(rfq_rows(register["equipment"])),
        "fixture-bom.csv": csv_text(bom),
        "fixture-cutting-plan.json": json_text(models.cutting_plan(fix)),
        "utilities.json": json_text(utilities),
        "process-routes.csv": csv_text(process_routes()),
        "development.json": json_text(iteration),
        "development.md": development_notes(iteration),
        "development.svg": development_svg(iteration),
        "connections.json": json_text(fabrication),
        "connections.md": connection_notes(fabrication),
        "connections.svg": connections_svg(fabrication),
        "fabrication-bom.csv": csv_text(fabrication_bom(native_models, a)),
        "stressing-sequence.csv": csv_text(
            [
                dict(
                    revision=fabrication["revision"],
                    sequence_id="balanced_pairs",
                    issued=False,
                    **stage,
                )
                for stage in fabrication["strongback"]["sequences"]["balanced_pairs"][
                    "stages"
                ]
            ]
        ),
        "fabrication-rfq.csv": csv_text(fabrication_rfq(fabrication_suppliers)),
    }
    for key, model in native_models.items():
        out[f"{key}/model.json"] = json_text(model)
    for key in ("vehicle", "precast"):
        out[f'{layout[key]["id"]}/plan.svg'] = plan_svg(layout[key], scenes[key])
    for key in ("fixture", "pi25-mould-bed"):
        out[f"{key}/drawing.svg"] = projection_svg(native_models[key])
    out["README.md"] = readme(report, register)
    out["index.html"] = viewer(report, register, out, fabrication)
    return out, native_models


def fabrication_bom(models_by_id, a):
    rows = []
    for model_id in ("strongback-end", "locator-cartridge"):
        for p in models_by_id[model_id]["parts"]:
            steel = p["role"].endswith("-steel")
            rows.append(
                dict(
                    assembly=model_id,
                    id=p["id"],
                    quantity=1,
                    role=p["role"],
                    dimensions_m=json.dumps(p["size_m"]),
                    kind=p["kind"],
                    holes=json.dumps(p.get("holes", [])),
                    nominal_steel_volume_m3=models.volume(p) if steel else "",
                    nominal_steel_mass_kg=(
                        models.volume(p) * a["steel_density_kg_m3"] if steel else ""
                    ),
                    basis=(
                        "OSR idealised steel; grade/origin/welds not released"
                        if steel
                        else "Envelope only; no density or purchased mass inferred"
                    ),
                )
            )
    return rows


def fabrication_rfq(suppliers):
    scope = {
        "boneham-custom-pin": "Three headed locator buttons to OSR coupon drawing; bore/shaft fits, finish/hardness and retention trial",
        "promil-starcut260": "Eight strongback assemblies for four pilot beds and four baseplates for one runway-bay example; confirm setup/payload and machining",
        "responsive-horizontal": "Fabrication/machining alternative for strongbacks and 6 m runway girders; material/weld/NDE and setup/payload return required",
        "asquith-service": "Legacy-machine service/retrofit availability and support enquiry; no new machine purchase specification assumed",
    }
    return [
        dict(
            id=r["id"],
            supplier=r["supplier"],
            model_or_service=r["model_or_service"],
            origin=r["origin"],
            scope=scope[r["id"]],
            published=json.dumps(r["published"]),
            source=" | ".join(r["sources"]),
            observed_on=suppliers["observed_on"],
            technical_questions="; ".join(r["unknown"]),
            commercial_questions="Itemise UK work/stock origin, price, freight/export/duties, Iraq installation/interfaces, inspection, documentation and warranty",
            price_gbp="",
            supplier_contacted="no",
            contract_accepted="no",
        )
        for r in suppliers["cases"]
    ]


def connection_notes(r):
    s, l, m = r["strongback"], r["locator"], r["manufacturing"]
    lines = [
        "# Factory fabrication interfaces — iteration 3",
        "",
        "This extends the mechanical and civil examples together. Original models and failed cases remain available. Two additional native models develop a perforated/diaphragm-stiffened strongback end and a retained locator-button coupon. These are preliminary fabrication concepts, with no physical release.",
        "",
        "## Grip spacing and strongback layout",
        "",
        f"The baseline 45 mm strand pitch clashes with the candidate 50 mm grip bodies by {-s['baseline_grip_fit']['minimum_surface_gap_m']*1000:.1f} mm. The 60 mm-pitch candidate gives {s['revised_grip_fit']['minimum_surface_gap_m']*1000:.1f} mm body clearance against a 5 mm research allowance. Side cover to the 15.2 mm clearance envelope is {s['nominal_stem_side_cover_m']*1000:.1f} mm. This does not qualify concrete cover, the exact strand/grip combination or jack-nose access.",
        "",
        "The new end box is 4 m across, 900 mm deep in the stressing direction and 1.3 m high, with 40 mm outer plates, 20 mm internal diaphragms and 48 aligned 22 mm clearance holes in each stressing face. Return-rail stubs are raised to the initial tendon centroid. Strongback plate holes are actual native boolean cuts; the grip cylinders remain external envelopes.",
        "",
        f"The initial 1.2 m-height aligned box also leaves an upper grip body overhanging the plate by {-s['baseline_plate_grip_edge_clearance_m']*1000:.1f} mm. The 1.3 m-height candidate provides {s['revised_plate_grip_edge_clearance_m']*1000:.1f} mm minimum body-to-plate-edge clearance. This is a geometric seat screen, not local plate resistance or a qualified bearing seat.",
        "",
        f"The aligned return axis is z={s['axis_z_m']:.4f} m. Its final initial-force vertical couple is zero in the stated symmetric model; temporary stressing stages still matter. The lower-first sequence reaches {s['sequences']['lower_first']['maximum_abs_end_couple_nm']/1e6:.3f} MNm, while the proposed balanced-pair ordering reaches {s['sequences']['balanced_pairs']['maximum_abs_end_couple_nm']/1e6:.3f} MNm. Both individual-strand half-steps are retained, so simultaneous stressing is not assumed. Release needs its own accepted sequence.",
        "",
        f"Gross in-plane bending demand is {s['nominal_in_plane_bending_demand_pa']/1e6:.1f} MPa. The nominal combined bending/average shear/closed-box torsion demand over the balanced stages is {s['maximum_stage_nominal_von_mises_demand_pa']/1e6:.1f} MPa. Nominal grip annular bearing is {s['grip_annular_bearing_demand_pa']/1e6:.1f} MPa. These omit local plate bending, openings/seat effects, weld resistance, buckling, distortional behaviour and fatigue; no stress allowable is adopted.",
        "",
        "[Strongback end CAD](strongback-end/model.FCStd) · [48-step proposed stressing sequence](stressing-sequence.csv)",
        "",
        "## Ground-restraint load path",
        "",
        f"The raised return-rail support uses a nominal 250 × 250 × 12.5 mm post concept of {s['post_length_m']:.4f} m height. Its ideal fixed-base lateral stiffness is {s['post_cantilever_stiffness_n_m']/1e6:.1f} MN/m. Steel-post, base rotation, connection and ground translation compliance act in series. Actual effective restraint remains unknown.",
        "",
        f"If every other interface were rigid, the ground-translation stiffness alone would need at least {s['foundation_translation_required_if_other_interfaces_rigid_n_m']/1e6:.3f} MN/m to retain the proposed 1 MN/m spring. Alternatively, with all other interfaces rigid, the base rotational stiffness alone needs {s['base_rotation_required_if_other_interfaces_rigid_nm_rad']/1e6:.3f} MNm/rad. These individual limiting budgets cannot be combined as if they jointly met the requirement. Both-plane restraint, column/base/anchor resistance and geotechnical design remain open.",
        "",
        "## Retained mechanical locator",
        "",
        f"The cartridge preserves the z={l['contact_plane_z_m']:.3f} m datum with a 32 mm contact head and a 19.990 mm nominal stem in a 20.000 mm bore. Declared ±2 micrometre size hypotheses give a {l['worst_case_diametral_clearance_m'][0]*1e6:.0f}–{l['worst_case_diametral_clearance_m'][1]*1e6:.0f} micrometre diametral clearance range; heat treatment, temperature, finish and actual machining capability are not qualified.",
        "",
        "A proposed M8 × 20 retaining screw passes through the RHS top-wall clearance hole; a 22 mm underside access opening permits assembly. A stepped pin solid contains a blind tap-drill, while the screw is a nominal thread envelope. Helical threads and their intended engagement interference are not modelled. Mount retention is not a rated lifting connection.",
        "",
        f"The button's nominal mass is {l['button_nominal_mass_kg']:.3f} kg, top contact demand is {l['nominal_top_contact_pressure_pa']/1e6:.2f} MPa and nominal screw engagement is {l['screw_nominal_engagement_m']*1000:.1f} mm. Thread stripping, screw grade/preload/locking, local tube-wall/access-hole effects, pin heat treatment and repeatability remain open.",
        "",
        "[Locator cartridge CAD](locator-cartridge/model.FCStd) · [concept fabrication BOM](fabrication-bom.csv)",
        "",
        "## British manufacture and subcontract machining cases",
        "",
        "These are published capabilities and unsent enquiries, not supplier offers. Pro-Mil's listed Starcut 260 travel is 6 × 4.35 × 2.15 m; its 50 t shop crane does not establish machine payload. Responsive lists a 10 × 3 × 1.5 m horizontal CNC capability. Boneham publishes UK custom cylindrical-component manufacture. Asquith Butler's current site focuses on service, spares and retrofit, so no new-build machine offer is inferred.",
        "",
        "| Part with OSR setup allowance | Pro-Mil Starcut travel screen | Responsive advertised-range screen |",
        "| --- | --- | --- |",
    ]
    for name in (
        "runway-baseplate",
        "strongback-box",
        "strongback-end-steel",
        "runway-girder",
    ):
        cases = [c for c in m["cases"] if c["part"] == name]
        lines.append(
            f"| {name}, {[round(v,3) for v in cases[0]['setup_reservation_m']]} m | {'within' if cases[0]['geometric_range_screen'] else 'outside'} | {'within' if cases[1]['geometric_range_screen'] else 'outside'} |"
        )
    lines += [
        "",
        "The 6 m girder plus 300 mm setup length exceeds the 6 m Starcut X travel. Axis orientation, usable simultaneous envelope, workholding, table payload, tool/head clearance and fabrication inspection need actual supplier returns for every case. UK work, raw-stock origin and installed Iraqi costs remain separate unknowns.",
        "",
        "[Unsent fabrication RFQs](fabrication-rfq.csv) · [Full staged calculations](connections.json)",
        "",
    ]
    for supplier in m["suppliers"]["cases"]:
        lines.append(
            f"- {supplier['supplier']}: "
            + "; ".join(
                f"[official source {j+1}]({url})"
                for j, url in enumerate(supplier["sources"])
            )
        )
    return "\n".join(lines) + "\n"


def connection_html(r):
    s = r["strongback"]
    return f'<h2>Fabrication and assembly interfaces</h2><img src="connections.svg" style="width:100%;height:auto" alt="Grip layout, stressing sequence, locator section and machining-range screens"><p>Baseline 45 mm pitch clashes with 50 mm grip bodies. The proposed 60 mm pitch has {s["revised_grip_fit"]["minimum_surface_gap_m"]*1000:.0f} mm body clearance; actual grips, strands and jack access remain unqualified.</p><p>The aligned return axis removes the final symmetric end couple. Individual-strand sequencing still produces temporary couples: lower-first {s["sequences"]["lower_first"]["maximum_abs_end_couple_nm"]/1e6:.3f} MNm; balanced ordering {s["sequences"]["balanced_pairs"]["maximum_abs_end_couple_nm"]/1e6:.3f} MNm.</p><p><a href="strongback-end/model.FCStd">Perforated strongback CAD</a> · <a href="locator-cartridge/model.FCStd">Retained locator CAD</a> · <a href="connections.md">Calculations and supplier route findings</a></p><p><a href="fabrication-bom.csv">Concept fabrication BOM</a> · <a href="stressing-sequence.csv">Individual-strand sequence</a> · <a href="fabrication-rfq.csv">Unsent UK fabrication RFQs</a></p><p>Material/local resistance, heat treatment, screw preload/locking, ground restraint, supplier setup/payload and Iraqi installed cost remain open.</p>'


def development_summary(iteration):
    summary = deepcopy(iteration)
    for alt in summary["prestress"]["alternatives"]:
        for scenario in alt["scenarios"]:
            scenario["station_count"] = len(scenario.pop("stations"))
            scenario["station_results_reference"] = (
                "development.json (same layout id and span)"
            )
    return summary


def development_notes(r):
    w, p, b, c = r["workholding"], r["prestress"], r["bed"], r["runway"]
    lines = [
        "# Joint mechanical and civil development — iteration 2",
        "",
        "The baseline four-model package remains available. These three additional CAD models develop workholding, prestress/bed restraint and crane-runway interfaces. Every physical release remains open. [Engineering comparison figure](development.svg).",
        "",
        "## Fixture workholding",
        "",
        f"Three British-made [Brauer H350/2BLC](https://www.brauer.co.uk/product/horizontal-positive-locking-clamps/) positive-locking clamp candidates each have a published nominal holding force of 350 daN (3,500 N). The requested 500 N clamping preload is a separate unverified input. Mounting plates are OSR concepts; equipment boxes reserve operation clearance rather than reproduce the supplier's geometry.",
        "",
        f"The declared payload/CG/tool cases leave a minimum vertical locator reaction of {w['minimum_contact_reaction_n']:.1f} N. That checks contact compression in those scenarios only. The conservative shear-only crossrail weld demand is {w['crossrail_connection_shear_screen']['nominal_shear_demand_pa']/1e6:.2f} MPa; weld resistance, local wall/plate bending and connection eccentricity remain unknown.",
        "",
        "[Workholding CAD](fixture-workholding/model.FCStd) · [detailed numerical inputs/results](development.json)",
        "",
        "## Prestress alternatives along both spans",
        "",
        "The first iteration showed a Pi20 midspan tension warning. The full-force prismatic extension to the beam ends exposes a larger baseline warning. Actual pretension force develops over a transmission length that remains unknown, so the endpoint extension is diagnostic. This model includes end-diaphragm gravity patches and known strand displacement mass, while retaining gross prismatic stiffness. Conventional reinforcement and railway/track loads remain unquantified.",
        "",
        "| Layout | Strands | Span | Minimum transfer compression | Minimum after-loss dead-load compression | Zero-tension research screen |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for alt in p["alternatives"]:
        for s in alt["scenarios"]:
            m = s["minimum_compression_pa_by_stage"]
            lines.append(
                f"| {alt['id']} | {alt['strands']} | {s['span_m']:g} m | {m['transfer']/1e6:.3f} MPa | {m['service_dead_only']/1e6:.3f} MPa | {'within' if s['no_tension_research_screen'] else 'outside'} |"
            )
    candidate = next(v for v in p["alternatives"] if v["id"] == p["candidate_id"])
    span25 = next(s for s in candidate["scenarios"] if s["span_m"] == 25)
    lines += [
        "",
        f"The {candidate['id']} candidate increases initial bed force to {candidate['initial_force_n']/1e6:.3f} MN. Its known concrete-plus-strand Pi25 handling equivalent is at least {span25['handling_equivalent_kg_lower_bound']/1000:.2f} t including the stated rigging and multiplier; unquantified reinforcement and attachments can increase it. A zero-tension screen does not establish compression strength, transfer/bond/end-zone performance, deflection, shear, fatigue or railway capacity.",
        "",
        "[Revised beam/bed CAD](pi25-revised-bed/model.FCStd)",
        "",
        "## Stressing-bed restraint",
        "",
        "Pinned beam-column finite elements check the nominal side boxes over the 26 m return path between assumed inner strongback faces x=-0.5 and +25.5 m, with ground restraints at the CAD's x=3,6,...,24 m stations. Pin-connected cross ties alone do not establish a 3 m effective length: a common sway mode remains. End rotational restraint and a real restraint path in both buckling planes must be designed, including foundations and anchorages.",
        "",
        "| Spring per restraint | Critical force per side | Elastic load factor at candidate force | Second-order brace force maximum |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for row in b["cases"]:
        force = row["imperfect_response"].get("maximum_abs_brace_force_n")
        lines.append(
            f"| {row['spring_n_m']/1e6:g} MN/m | {row['critical_force_per_side_n']/1e6:.3f} MN | {row['elastic_load_factor']:.3f} | {f'{force/1000:.2f} kN' if force is not None else 'unstable elastic tangent'} |"
        )
    lines += [
        "",
        "The proposed 1 MN/m spring is a requirement scenario, not measured ground stiffness. Second-order reactions use an assumed sinusoidal 10 mm stress-free bow and springs initially unstressed in that crooked shape. The revised CAD adds interface stools/pad reservations, with no demonstrated foundation stiffness or capacity. Strongback load distribution, vertical eccentricity, local plates/welds, staged release and anchorage design remain open.",
        "",
        f"The candidate adds {b['strongback_in_plane_moment_demand_nm']/1e6:.3f} MNm in-plane strongback moment and a {b['end_vertical_eccentric_couple_nm']/1e6:.3f} MNm end couple from the tendon/return-box height offset. These are unresolved load-path demands; the large strongback solids remain reservations, not designed steel sections or concrete abutments.",
        "",
        "## Dedicated crane-runway bay",
        "",
        f"A separate 6 m runway bay develops a proposed 30 m-span, 125 t rated crane interface. Assumed crab/bridge masses, lift factor, two wheels per rail and approach yield near/far wheel actions {c['near_wheel_n']/1000:.1f}/{c['far_wheel_n']/1000:.1f} kN. These are OSR scenarios requiring Street's actual configuration/reaction return. [Street describes wheel loads and duty as configuration-dependent](https://streetcrane.com/blog/2026/07/29/understanding-crane-duty-ratings/).",
        "",
        f"The fabricated 1.2 m-deep runway girder has gross elastic bending demand {c['nominal_bending_demand_pa']/1e6:.1f} MPa and sampled deflection envelope {c['sampled_elastic_deflection_envelope_m']*1000:.2f} mm for the stated loads. Local wheel/web bearing, stability, fatigue, torsion, clips, connections and column resistance remain open. The conservative two-adjacent-bay column scenario is {c['two_adjacent_bays_column_gravity_envelope_n']/1e6:.3f} MN. A 2.5 × 2.5 m pad reservation gives {c['pad_average_gravity_pressure_scenario_pa']/1000:.1f} kPa average gravity pressure; ground capacity, eccentric bearing and uplift are unknown, so no footing acceptance is given.",
        "",
        "[Runway bay CAD](runway-bay/model.FCStd). Runway supports remain separate from the vehicle hall's roof-only frame. Runway rail/clip/stiffener dead weights and final project load combinations remain unknown.",
        "",
        "The 900 × 900 × 50 mm runway baseplate blank is about 318 kg. It exceeds both the CV5-500's published part diameter and mass limits, while the 6 m girders also need a separate fabrication route. Outsourced plate machining/long-girder fabrication or additional machinery must be selected before this pilot factory can manufacture those structures. Sheet-plan fit alone does not establish 50 mm laser-cut capacity.",
        "",
        "## Next evidence and ownership",
        "",
        "Mechanical engineering: clamp GA/preload trials, pin retention and mount/weld/bolt details. Prestress/civil engineering: project concrete/strand limits, transmission/end-zone and railway loading, strongbacks, both-plane restraint and geotechnical design. Crane supplier/structural engineering: exact duty/configuration, wheel actions, rails/stops, runway/column/foundation design. Procurement: technical returns, certificates, Baghdad support and itemised installed prices. No contacts have been sent and no appointments invented.",
    ]
    return "\n".join(lines) + "\n"


def development_html(r):
    p = r["prestress"]
    rows = []
    for alt in p["alternatives"]:
        for s in alt["scenarios"]:
            m = s["minimum_compression_pa_by_stage"]
            rows.append(
                f"<tr><td>{alt['id']}</td><td>{s['span_m']:g} m</td><td>{m['transfer']/1e6:.3f}</td><td>{m['service_dead_only']/1e6:.3f}</td></tr>"
            )
    return (
        '<h2>Joint mechanical and civil development</h2><p>Three additional CAD models develop the open load paths. Compression-positive MPa below; negative values predict tension in this research idealisation.</p><img src="development.svg" style="width:100%;height:auto" alt="Prestress stress distributions, bed restraint sensitivity and crane wheel actions"><div style="overflow-x:auto"><table style="border-spacing:12px 6px"><thead><tr><th>Layout</th><th>Span</th><th>Minimum transfer</th><th>Minimum after-loss, dead only</th></tr></thead><tbody>'
        + "".join(rows)
        + '</tbody></table></div><p>Balanced 48 is a further-design candidate. Transmission, concrete limits, railway loading and physical qualification remain open.</p><p><a href="fixture-workholding/model.FCStd">Workholding CAD</a> · <a href="pi25-revised-bed/model.FCStd">Revised beam/bed CAD</a> · <a href="runway-bay/model.FCStd">Runway bay CAD</a></p><p><a href="development.md">Calculations, assumptions and next gates</a> · <a href="development.json">Station-by-station results, buckling and wheel actions</a></p>'
    )


def readme(r, register):
    f, c = r["fixture"], r["civil"]
    lines = [
        "# Baghdad mechanical, civil and factory development examples",
        "",
        "Generated from versioned SI inputs and official supplier information checked on 16 October 2026. These are review models; all physical release gates remain open.",
        "",
        "Open [the offline visual review](index.html), [the engineering report](report.json), [the equipment/RFQ register](equipment-rfq.csv), [utility gaps](utilities.json) or [process/inspection routes](process-routes.csv).",
        "",
        "## What is built",
        "",
        "The [second development iteration](development.md) adds three native models and full-span prestress alternatives, explicit bed-restraint stiffness/imperfection cases, fixture workholding and crane-runway interface demands. The original four models below remain baseline examples.",
        "",
        f"The fixture has a nominal model mass of {f['mass_kg']:.2f} kg, a 500 kg payload hypothesis and a 1.5 load multiplier. Its six locators have independent kinematic rank. The payload-only elastic deflection bound is {f['payload_only_combined_deflection_bound_m']*1000:.3f} mm against a provisional 1 mm review limit. This does not establish weld, pin, clamp, wall or anchor resistance.",
        "",
        "[Fixture drawing](fixture/drawing.svg), [native FreeCAD](fixture/model.FCStd), [cut list/BOM](fixture-bom.csv), [stock cutting plan](fixture-cutting-plan.json). Datum plates are welded mounts with bored locator interfaces; locator retention, shims and clamps need detailed design. Inspect the assembled fixture by a separate survey: it does not fit the Axiom CMM.",
        "",
        f"The canonical pi section is {c['section']['area_m2']:.4f} m², centroid {c['section']['centroid_z_m']:.4f} m above soffit and gross inertia {c['section']['inertia_x_m4']:.6f} m⁴. New solid end-diaphragm fill is a separate hypothesis with nonoverlapping solids, not a canonical accepted detail.",
        "",
        "| Span | Bare mass | With hypothetical solid end diaphragms | Lifting demand incl 2 t rigging and 1.25 multiplier | Bare dead-load deflection |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for s in c["scenarios"]:
        lines.append(
            f"| {s['span_m']:g} m | {s['bare_mass_kg']/1000:.2f} t | {s['developed_mass_kg']/1000:.2f} t | {s['handling_equivalent_kg']/1000:.2f} t | {s['bare_dead_elastic_deflection_m']*1000:.2f} mm |"
        )
    lines += [
        "",
        f"The bare-section Pi20 transfer hypothesis gives top-fibre stress {c['scenarios'][0]['transfer_fiber_stress']['top_pa']/1e6:.3f} MPa with compression positive, so it predicts slight top tension. Concrete tensile/transfer limits are unknown. This needs a revised or qualified prestress/transfer design; a numerical stress result supplies no acceptance.",
        "",
        "[Pi25 mould/bed drawing](pi25-mould-bed/drawing.svg) and [native FreeCAD](pi25-mould-bed/model.FCStd) show concrete, conceptual mould faces, side boxes, ties, strongback reservations and 40 tendon axes. These overlap across manufacturing states by design; this is not a finished mould or stressing-bed fabrication package.",
        "",
        f"The proposed 40-strand research scenario starts at {c['prestress_hypothesis']['initial_force_n']/1e6:.2f} MN. Ideal pinned Euler screening of two 500 × 300 × 16 mm bed boxes gives demand/Euler = {c['bed_screen']['full_25m_euler_ratio']:.2f} over an unbraced 25 m, so that unsupported configuration fails even the ideal screen. The alternative 3 m brace assumption needs real brace/connection/foundation design. No railway live-load result or resistance acceptance is supplied.",
        "",
        "## Factory examples",
        "",
        "[Vehicle hall plan](vehicle-factory/plan.svg) and [native model](vehicle-factory/model.FCStd): 144 × 60 m; one canonical 135 × 6.5 m six-car assembly lane, component machining/welding, conditioned metrology and separated pilot composites reservations. Roof grid 12 × 30 m, 10 m concept columns and a 250 mm slab are coordination hypotheses. Roof-only gravity takeoff does not include wind, seismic or crane loads. Ground bearing capacity and foundation sizes remain unknown. Crane runways require separate supports/design. The two canonical 2 km test tracks require additional land and alignment.",
        "",
        "[Pilot precast yard plan](precast-yard/plan.svg) and [native model](precast-yard/model.FCStd): 160 × 100 m with four casting positions, reinforcing/stressing, batching/washwater reservations, heavy transport routes and four storage positions. A complete concrete batching plant, rebar/strand preparation line, heavy trailers and laboratory remain unselected; the named mixer/grips do not supply those systems.",
        "",
        f"At {r['capacity']['occupation_working_days']:g} working days per full bed cycle, 85% availability and 95% accepted yield, four positions give {r['capacity']['planning_accepted_beams_per_working_day']:.3f} accepted beams/working day. The earlier 54/day programme target needs at least {r['capacity']['positions_required_at_same_assumptions']} positions at the same assumptions, before other bottlenecks. This pilot has no qualified production rate.",
        "",
        "## Named equipment candidates",
        "",
        "| Supplier/model | Origin basis | Specification source |",
        "| --- | --- | --- |",
    ]
    for e in register["equipment"]:
        lines.append(
            f"| {e['supplier']} — {e['model']} | {e['origin']} | [Official source]({e['sources'][0]}) |"
        )
    lines += [
        "",
        "Supplier dimensions and numerical fields are in [the versioned register](../data/equipment.json), with document/page pointers. Published dimensions, historical specifications and OSR reservations are separate. Machine solids are external envelope proxies, not manufacturer CAD. UK supply/integration does not prove British manufacture. Rapid's Northern Ireland manufacture is identified separately.",
        "",
        "The laser's 4 kW output is not its electrical input: the historical 4 kW-option sheet lists 40.2–58.9 kVA. The Mazak's 18.5 kW figure is spindle output at 10% ED. Total site power remains unknown. Axiom plus CIJECT publish 700 L/min combined air demand at their respective conditions; reference-flow bases and diversity are unconfirmed, so no compressor rating is adopted. Baghdad heat, dust, process cooling, extraction, fire and metrology HVAC require design.",
        "",
        "The 80 t crane screen fails for the developed Pi25 lifting scenario. A 125 t Street open-winch configuration is an enquiry within its published 80–250 t family, not a quoted catalogue model or accepted lifting design. The 10 t ZX8 is for component handling. Bridge span is distinct from trolley gauge.",
        "",
        "Installed CAPEX is **unknown**. The £2,640 ex-VAT Oxford UK retail reference is dated and excludes an agreed Iraq package; it is not a factory estimate. No supplier has been contacted and no delivery, service, performance or origin has been accepted.",
        "",
        "## Build and inspect",
        "",
        "```sh",
        ".venv/bin/python -m engineering.factory_examples.build --native",
        ".venv/bin/python -m engineering.factory_examples.build --check",
        ".venv/bin/python -m pytest engineering/analysis/tests/test_factory_examples.py -q",
        "```",
        "",
        "FCStd documents are retained in Git; neutral STEP exports are generated beside them and remain ignored under repository policy. Each native receipt records toolchain, exact input/exporter hashes, per-part volumes/bounds, file hashes and actual FCStd/STEP reopen checks. `--check` verifies tracked CAD and reproducible text; it verifies STEP hashes when local exports exist. Deleted STEP files can be regenerated with `--native`.",
        "",
        "Follow the [staged plan](../../../docs/design-engine/mechanical-civil-factory-plan-2026-10-16.md). Next gates are supplier technical returns, site/ground design, detailed fabrication/structural checks, measured first articles and accepted factory trials; all remain open.",
    ]
    return "\n".join(lines) + "\n"


def viewer(r, register, out, fabrication):
    cards = []
    for e in register["equipment"]:
        cards.append(
            f'<details><summary>{html.escape(e["supplier"]+" — "+e["model"])}</summary><p>{html.escape(e["origin"])}</p><p>{html.escape(e["process"])}</p><pre>{html.escape(json.dumps(e["published"],indent=2))}</pre><p>Planning allowances: {html.escape(json.dumps(e["planning"]))}</p><p>Open: {html.escape("; ".join(e["unknown"]))}</p>'
            + " ".join(
                f'<a href="{html.escape(s,quote=True)}">Source {i+1}</a>'
                for i, s in enumerate(e["sources"])
            )
            + "</details>"
        )
    return (
        """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Baghdad factory development examples</title><style>body{font:16px/1.5 system-ui;background:#f2f6f7;color:#173746;max-width:1250px;margin:auto;padding:24px}a{color:#07644d}h1{font-size:2rem}nav{display:flex;gap:12px;flex-wrap:wrap}button{padding:10px 16px;border:1px solid #456;background:white;border-radius:6px;cursor:pointer}button[aria-selected=true]{background:#173746;color:white}section{background:white;padding:20px;margin-top:20px;border-radius:8px}svg{width:100%;height:auto}details{border-top:1px solid #cbd8dc;padding:12px}summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap;font-size:13px}.note{border-left:4px solid #b57a25;padding:12px;background:#fff5e3} [hidden]{display:none}</style><h1>Baghdad factory development examples</h1><p>Six-car vehicle/component hall and pilot Pi20/Pi25 production yard. Official UK supplier data checked 16 October 2026.</p><p class="note">Engineering development models. Factory capability, structural resistance, supplier configuration and site acceptance remain open. Equipment models show external envelopes and labelled planning allowances.</p><nav aria-label="Review view">"""
        + "".join(
            f'<button type="button" data-view="{key}" aria-selected="{str(i==0).lower()}">{label}</button>'
            for i, (key, label) in enumerate(
                [
                    ("vehicle", "Vehicle hall"),
                    ("yard", "Precast yard"),
                    ("mechanical", "Fixture"),
                    ("civil", "Mould & bed"),
                    ("equipment", "Equipment & sources"),
                    ("development", "Joint development"),
                    ("fabrication", "Fabrication interfaces"),
                ]
            )
        )
        + "</nav>"
        + "".join(
            f'<section id="{key}"'
            + (" hidden" if i else "")
            + ">"
            + content
            + "</section>"
            for i, (key, content) in enumerate(
                [
                    (
                        "vehicle",
                        out["vehicle-factory/plan.svg"]
                        + '<p>144 × 60 m; canonical six-car assembly lane. Two 2 km test tracks need separate land. Roof/slab concepts have no site resistance acceptance.</p><a href="vehicle-factory/model.FCStd">Native CAD</a>',
                    ),
                    (
                        "yard",
                        out["precast-yard/plan.svg"]
                        + f'<p>Four casting positions: {r["capacity"]["planning_accepted_beams_per_working_day"]:.3f} accepted beams/working day under declared assumptions; not demonstrated throughput. At least {r["capacity"]["positions_required_at_same_assumptions"]} positions for the 54/day case.</p><a href="precast-yard/model.FCStd">Native CAD</a>',
                    ),
                    (
                        "mechanical",
                        out["fixture/drawing.svg"]
                        + f'<p>Nominal stock mass {r["fixture"]["mass_kg"]:.2f} kg. Locator restraint rank 6; clamps, joints, anchors, survey and proof loads remain open.</p><a href="fixture/model.FCStd">Native CAD</a> · <a href="fixture-bom.csv">BOM</a>',
                    ),
                    (
                        "civil",
                        out["pi25-mould-bed/drawing.svg"]
                        + '<p>Concrete and strand/mould interfaces are different manufacturing states. 40-strand research hypothesis; no railway live-load acceptance. Unsupported 25 m stressing boxes fail ideal Euler screening.</p><a href="pi25-mould-bed/model.FCStd">Native CAD</a>',
                    ),
                    ("equipment", "<h2>Equipment candidates</h2>" + "".join(cards)),
                    ("development", development_html(r["development"])),
                    ("fabrication", connection_html(fabrication)),
                ]
            )
        )
        + """<p><a href="README.md">Design notes and limitations</a> · <a href="report.json">Full numerical report</a> · <a href="equipment-rfq.csv">Unsent RFQ schedule</a></p><script>for(const button of document.querySelectorAll('[data-view]'))button.addEventListener('click',()=>{for(const item of document.querySelectorAll('[data-view]'))item.setAttribute('aria-selected',String(item===button));for(const panel of document.querySelectorAll('section'))panel.hidden=panel.id!==button.dataset.view;});</script></html>\n"""
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=DEFAULT)
    p.add_argument("--native", action="store_true")
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    if args.check and args.native:
        p.error("--native and --check are separate operations")
    out, native_models = make_outputs()
    if args.check:
        errors = [
            name
            for name, text in out.items()
            if not (args.output / name).is_file()
            or (args.output / name).read_text() != text
        ]
        for key in native_models:
            folder = args.output / key
            receipt = folder / "native-cad.json"
            if not receipt.is_file():
                errors.append(key + ": native receipt missing")
                continue
            record = json.loads(receipt.read_text())
            if (
                record["input_sha256"] != digest(folder / "model.json")
                or record["exporter_sha256"] != digest(PACKAGE / "native.py")
                or record.get("geometry_helpers_sha256")
                != digest(PACKAGE / "models.py")
                or record["part_count"] != len(native_models[key]["parts"])
            ):
                errors.append(key + ": native source mismatch")
            for name, sha in record["files_sha256"].items():
                path = folder / name
                if (path.is_file() and digest(path) != sha) or (
                    name.endswith("FCStd") and not path.is_file()
                ):
                    errors.append(key + ": native file mismatch " + name)
        if errors:
            raise SystemExit("Factory example drift: " + ", ".join(errors))
        print(
            f"Factory text/source/native CAD correspondence verified ({len(native_models)} models)."
        )
        return
    for name, text in out.items():
        path = args.output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    if args.native:
        for key in native_models:
            receipt = generate(
                args.output / key / "model.json", args.output / key, ROOT
            )
            print(
                f"Native {key}: {receipt['part_count']} parts, FCStd and STEP reopened",
                flush=True,
            )
    print(f"Generated {len(out)} text artifacts in {args.output}")


if __name__ == "__main__":
    main()
