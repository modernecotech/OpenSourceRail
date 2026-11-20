"""Build the offline first-article enquiry register from the two engineering handoffs."""
import argparse
import hashlib
import json
import runpy
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CITY = "cities/Baghdad"
MECH = CITY + "/engineering/mechanical"
CORE = "docs/reference-v07"
sys.path.insert(0, str(ROOT / MECH))
from compare_returns import estimate


def lot(name, quantity, scope, witness, records):
    return dict(name=name, network_quantity=quantity, scope=scope, witness=witness,
                records={path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in records})


def register():
    identity, quantities, _, _, _ = estimate()
    handoff = json.loads((ROOT / CORE / "digital/production/handoff.json").read_text())
    compile_handoff = runpy.run_path(str(ROOT / CORE / "digital/production/generate.py"))["compile_handoff"]
    if compile_handoff() != handoff:
        raise ValueError("Regenerate the selected core production handoff before quoting")
    production = handoff["production"]
    common = [CORE + "/manufacturing/bom.csv", CORE + "/manufacturing/routing.csv",
              CORE + "/integration/interfaces.csv", CORE + "/digital/selected.toml"]
    vehicle = [MECH + "/vehicle/cut-list.csv", MECH + "/vehicle/frame-overview.svg",
               MECH + "/bogie-interface.svg", MECH + "/vehicle/result.json",
               MECH + "/vehicle/SECTION-POWER.md"]
    civil = [MECH + "/civil/station-and-box.svg", MECH + "/civil/section-results.json",
             MECH + "/civil/SPAN-COMPARISON.md"]
    core_lots = [
        lot("One powered car", production["fleet_cars"], "One complete 17 m car with two powered bogies, drive, independent brake, cooling, roof collection, doors and installed fitout.",
            "Weigh each axle, demonstrate brake reaction, clearance and a bogie exchange. Return body and equipped-bogie prices separately within the total.", common + [CORE + "/digital/vehicle/result.json"]),
        lot("One precast track beam", production["beam_count"], "One 10 m thirteen-strand running beam, including reinforcement, inserts, transport, rigging and placement. Identify shared support and bearing costs separately.",
            "Record batch, release strength, dimensions, bare weight, lift geometry and bearing-seat survey.", common + [CORE + "/digital/civil/result.json"]),
        lot("One station dispatch cabinet", None, "One first-article station dispatch cabinet, cables, test points, configuration, installation and operator training. Agree production quantity after channel allocation.",
            "Witness correct berth and side, loss of communications, false door lock and inhibition of traction. Return calibration and repair tooling.", common + ["control-electronics/interface-schedule.json"]),
    ]
    city_lots = [
        lot("One braced carbody", quantities["cars"], "One welded 17 m body with door openings, bogie attachments, joint preparation, coatings and acceptance inspection. Return bare frame and fitted additions separately. Price any aluminium extrusion or bonded composite hybrid on a separate revision. Include joining fixtures, local inspection and repair, heat/fire evidence, and the effect on installed mass and door deflection.",
            "Survey door apertures and suspension datums before and after welding. Return weigh sheet, weld map and repair procedure.", vehicle),
        lot("One equipped powered bogie", quantities["bogie_frames"], "One bogie with frame, wheelsets, bearings, suspension, drives, brakes, cooling connections, fasteners and removal pallet interface. Separate local frame and purchased equipment.",
            "Witness loaded reactions, brake mount, removal sweep and reinstallation. Weigh the complete assembly and identify the frame subtotal.", vehicle),
        lot("One typical elevated kilometre", None, "Straight double track, 100 bays per track at 10 m, 200 beams, 800 bearing positions and 200 lifts. Quote 202 support positions for a standalone sample and identify both boundaries.",
            "Submit priced tendon and reinforcement schedule, ground assumption, casting beds, stock, transport, lift radius, temporary restraint and bearing replacement.", civil),
        lot("One difficult crossing", None, "One crossing with approaches, clearances, temporary works and diversion. Owner and bidder must agree surveyed location, ground, envelope, access and possessions before matching prices.",
            "Identify each survey dependency. Submit alternative span arrangement, foundations, erection stages, inspection and possession duration.", civil),
        lot("One accessible station", quantities["budgeted_stations"], "One complete station with a 125 m island, lifts, stairs, deck, drainage, utilities, edge, access and commissioning. The continuous deck template precedes trimming of stair and lift openings.",
            "Return a dimensioned accessible route, egress calculations, measured boarding tolerances and maintainable lift and bearing access.", civil + [CITY + "/station-interface.svg", CITY + "/maps/STATION-PRICING.md"]),
        lot("One station cabinet and brake bench", None, "One station dispatch cabinet and one independently instrumented brake and door bench. Quote harness, installation, software configuration, spares and training.",
            "Record independent holding-brake feedback, rollback, lock proof and traction handover. Agree limits and witnesses before loading the rig.", [CITY + "/engineering/controls/README.md", CITY + "/engineering/controls/src/boarding.rs",
            CITY + "/engineering/controls/bench_trace.py"]),
    ]
    networks = {
        "first": dict(name="Baghdad · seven corridors", domestic="Iraqi", basis=identity, lots=city_lots),
        "core": dict(name="Core · 30 km", domestic="domestic", basis={
            "candidate": handoff["physical_candidate_id"], "evaluation": handoff["evaluation_id"],
            "selection": handoff["selection_id"], "currency": handoff["capital"]["currency"],
            "price_year": handoff["capital"]["price_year"]}, lots=core_lots),
    }
    for network in networks.values():
        for article in network["lots"]:
            basis = json.dumps([network["basis"], article], sort_keys=True).encode()
            article["revision"] = hashlib.sha256(basis).hexdigest()
    return networks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    dest = HERE / "enquiries-data.js"
    output = "const railwayEnquiries = " + json.dumps(register(), ensure_ascii=False, indent=2) + ";\n"
    if args.check:
        if dest.read_text() != output:
            raise SystemExit("Refresh the supplier enquiry register")
    elif not dest.exists() or dest.read_text() != output:
        dest.write_text(output)
