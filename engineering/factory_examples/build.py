"""Build/check the dimensioned factory examples and their review artifacts.

Run from the repository: .venv/bin/python -m engineering.factory_examples.build
Add --native for actual FreeCAD/STEP export, or --check for drift verification.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
from pathlib import Path

from . import models
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
            "unselected",
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
                160,
                "nonstressing-end grip candidates",
                "four beds x 40 strands, conditional on exact strand compatibility; live-end grips/jacks separate and unselected",
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
    }
    for key, model in native_models.items():
        out[f"{key}/model.json"] = json_text(model)
    for key in ("vehicle", "precast"):
        out[f'{layout[key]["id"]}/plan.svg'] = plan_svg(layout[key], scenes[key])
    for key in ("fixture", "pi25-mould-bed"):
        out[f"{key}/drawing.svg"] = projection_svg(native_models[key])
    out["README.md"] = readme(report, register)
    out["index.html"] = viewer(report, register, out)
    return out, native_models


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


def viewer(r, register, out):
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
        print("Factory text/source/native CAD correspondence verified (4 models).")
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
