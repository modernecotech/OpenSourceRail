"""Source-bound first-article vehicle and civil records for the Baghdad Airport operating plan."""
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import tempfile
import tomllib
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from cities.Baghdad import airport_opening, airport_finance
from engineering.performance import disk_reservation, check_disk_reservation

HERE = Path(__file__).resolve().parent
CITY = HERE.parents[1]
ROOT = CITY.parents[1]
PACKAGE = HERE / "mechanical-article.zip"
EXPECTED = {"article.json", "car-and-bogies.obj", "door-leaf-travel.obj", "portal-detail.svg", "revised-cuts.csv",
            "track-span.obj","platform-bay.obj","pier.obj"}


def sha(data):
    return sha256(data).hexdigest()


def encode(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)+"\n").encode()


def identity(obj):
    return sha(json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def source_hashes():
    files = ["system.toml", "engineering/prototype/doorway.toml", "engineering/prototype/car.py",
             "engineering/prototype/car_worker.py", "engineering/mechanical/quotation.toml",
             "engineering/mechanical/vehicle/stock.toml", "engineering/mechanical/vehicle/result.json",
             "engineering/mechanical/vehicle/develop_vehicle.py","engineering/mechanical/vehicle/stock_mesh.py",
             "engineering/mechanical/vehicle/braced-frame.obj","engineering/mechanical/vehicle/cut-list.csv",
             "engineering/mechanical/develop.py","engineering/mechanical/schedule.json",
             "engineering/mechanical/civil/develop_civil.py","engineering/mechanical/civil/concept.toml",
             "engineering/mechanical/civil/section-results.json"]
    paths = [CITY / f for f in files] + [ROOT/"engineering/design_search/frame_analysis.py"]
    return {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in paths}


def service_inventory(liners, spec):
    leaves = liners
    return {
        "per_car": {"doors": leaves//2, "sliding_leaves": leaves, "two_carriages_per_leaf": 2*leaves,
            "two_guide_stops_per_leaf": 2*leaves, "anti_drop_retention_points": 2*leaves,
            "jamb_liner_strips":liners, "flush_liner_screws":liners*spec["liner_fixings_per_strip"],
            "liner_threaded_receivers":liners*spec["liner_fixings_per_strip"],
            "moving_leaf_harness_paths_if_powered_at_leaf":leaves, "primary_suspension_seat_positions":8,
            "secondary_suspension_seat_positions":4,"wheelset_bearing_positions":8,
            "powered_axle_modules":4,"brake_controllers":2, "bogie_exchange_interfaces":2},
        "scope":"New door fittings are first-article quotation quantities. Supplier must confirm fastener grip, preload, stop loads, seal friction, guides and harness cycling. Prove door locking and release with the selected controller.",
        "unresolved":{"joint_consumable_mass_kg":None,"coolant_hose_counts":None,"hose_sweep_and_bend_radius_m":None,
            "cable_lengths_m":None,"brake_disc_and_retention_counts":None,"bearing_fit":None,
            "lifting_point_allowable_load_kn":None,"finished_equipment_mass_kg":None}
    }


def interfaces(geom, rig, spec, pieces, schedule):
    car_x = geom["car_body_length_m"]/2
    bogies = []
    for name,pivot,sign in zip(("bogie-A","bogie-B"), geom["bogie_centres_m"], (-1,1), strict=True):
        group = [p for p in pieces if p["assembly"] == name]
        lower = [min(p["lower_m"][i] for p in group) for i in range(3)]
        upper = [max(p["upper_m"][i] for p in group) for i in range(3)]
        travel = round(car_x+rig["handling_standoff_m"] - (lower[0] if sign>0 else -upper[0]),6)
        end = sign*travel
        sw_lo, sw_hi = list(lower), list(upper)
        sw_lo[0] += min(0,end)
        sw_hi[0] += max(0,end)
        body = [p for p in pieces if p["assembly"]=="body" and
                all(p["upper_m"][i]>=sw_lo[i] and p["lower_m"][i]<=sw_hi[i] for i in (0,1))]
        bg_clear = min(p["lower_m"][2]-upper[2] for p in body)
        if bg_clear<=0:
            raise ValueError("Frame envelope intersects the body in its extraction stroke")
        bogies.append({"assembly":name,"body_from_bogie_translation_m":[pivot,0,0],"rotation_deg":[0,0,0],
            "installed_box_vehicle_m":[lower,upper],"signed_outward_travel_m":end,
            "stock_swept_box_vehicle_m":[sw_lo,sw_hi],"min_steel_vertical_separation_m":round(bg_clear,6),
            "service_lane_clear_width_m":round(rig["transfer_pallet_width_m"]+2*rig["handling_standoff_m"],6)})
    return {"automated_checks":"Rigid translation of the bare bogie assembly along x beneath a level, independently supported and separated car. Check wheel, traction motor, brake, hose, pallet and lifting fixture envelopes against the surveyed shop before removal.",
        "bogies":bogies,"formation_body_from_car_x_m":schedule["train"]["car_centres_m"],
        "body_from_axle_x_m":schedule["train"]["body_axle_x_m"],
        "origin_convention":"Frames share railhead z=0; yaw, pitch and roll are zero in the straight installed pose. Add the bogie centre x to each local point to obtain body coordinates.",
        "screw_z_m":[round(spec["liner_bottom_m"] + spec["first_fixing_from_end_m"] +
            i*(spec["liner_height_m"]-2*spec["first_fixing_from_end_m"])/(spec["liner_fixings_per_strip"]-1),6)
            for i in range(spec["liner_fixings_per_strip"])],
        "station_keep_clear_x_m":[r["edge_keep_clear_x_m"] for r in schedule["station"]["platform_edge_schedule_per_boarding_side"]],
        "curve_throw_screens":schedule["train"]["curve_screen"]}


def portal_drawing(record):
    d = record["doorway"]
    spec = d["specification"]
    raw = min(d["rough_widths_m"])
    # Scaled side elevation in a single doorway-centred frame.
    scale = 200
    centre = 275
    half = raw*scale/2
    x1,x2 = centre-half,centre+half
    jamb_depth = tomllib.loads((CITY/"engineering/mechanical/vehicle/stock.toml").read_text())["sections"]["jamb"][0]/1000
    jamb = scale*jamb_depth
    liner = scale*spec["liner_thickness_m"]
    base,top = 595,595-scale*spec["liner_height_m"]
    content = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 710" role="img" aria-labelledby="title desc">',
               '<title id="title">Lined doorway and sliding leaf reserve</title>',
               '<desc id="desc">Body side elevation and per-edge horizontal design budget for the Airport first article.</desc>',
               '<style>text{font:16px sans-serif;fill:#1b3548}.title{font:bold 29px sans-serif}.h{font:bold 19px sans-serif}.small{font:13px monospace}</style>',
               '<rect width="960" height="710" fill="white"/>']
    def text(x,y,msg,css=""):
        content.append(f'<text x="{x}" y="{y}" class="{css}">{escape(str(msg))}</text>')
    def line(a,b,c,e):
        content.append(f'<path d="M{a} {b} L{c} {e}" stroke="#354c5b" fill="none"/>')
    text(30,45,"Representative car  /  Doorway finishing budget","title")
    text(30,78,"Side elevation in the car x–z plane. Dimensions in millimetres. Drawn for first-article quotation.")
    for start in (x1-jamb,x2):
        content.append(f'<rect x="{start}" y="{top-8}" width="{jamb}" height="{base-top+16}" fill="#587784"/>')
    for start in (x1,x2-liner):
        content.append(f'<rect x="{start}" y="{top}" width="{liner}" height="{base-top}" fill="#e46925"/>')
    line(x1,top-22,x2,top-22)
    for x in (x1,x2): line(x,top-31,x,top-15)
    text(189,top-39,f'{raw*1000:.0f} steel opening',"h")
    line(x1,base+16,x2,base+16)
    text(75,base+49,"Orange strips are replaceable jamb liners.")
    text(496,153,"Horizontal budget per jamb","h")
    labels = (("Liner blank","liner_thickness_m"),("Seal projection","seal_projection_per_edge_m"),
              ("Fabrication error inward","fabrication_inward_per_edge_m"),("Loaded distortion inward","loaded_distortion_per_edge_m"),
              ("Fitting and wear","fitting_and_wear_per_edge_m"))
    for i,(label,key) in enumerate(labels):
        v = d["per_edge_allowances_m"][key]
        text(496,196+39*i,label)
        text(829,196+39*i,f"{v*1000:g} mm")
    line(496,372,910,372)
    text(496,408,f'Budgeted fitted width   {d["minimum_fitted_under_allocations_m"]*1000:.0f} mm',"h")
    text(496,446,f'Required fitted width   {d["required_fitted_m"]*1000:.0f} mm')
    text(496,482,f'Remaining budget   {d["residual_m"]*1000:.0f} mm overall')
    text(496,529,f'Leaf stroke   {spec["leaf_travel_m"]*1000:.0f} mm each way')
    text(496,565,f'Gross liner height   {spec["liner_height_m"]*1000:.0f} mm')
    text(30,678,"Body revision "+record["frame_revision"],"small")
    return "\n".join(content+["</svg>",""])


def write_compact(items):
    if set(items) != EXPECTED:
        raise ValueError("Incomplete mechanical article package")
    with disk_reservation(ROOT,HERE,"Publish Baghdad mechanical article",4<<20) as lease:
        with tempfile.NamedTemporaryFile(dir=HERE,delete=False) as temp:
            pending = Path(temp.name)
        try:
            with ZipFile(pending,"w") as arc:
                for name,data in sorted(items.items()):
                    arc.writestr(ZipInfo(name),data,compress_type=ZIP_DEFLATED)
            check_disk_reservation(lease)
            pending.chmod(0o644)
            pending.replace(PACKAGE)
        finally:
            pending.unlink(missing_ok=True)


def read_compact():
    with ZipFile(PACKAGE) as arc:
        if len(arc.namelist())!=len(EXPECTED) or set(arc.namelist())!=EXPECTED:
            raise ValueError("Incomplete mechanical article")
        items = {n:arc.read(n) for n in EXPECTED}
    record = json.loads(items["article.json"])
    if (record["evaluation_id"] != identity({k:v for k,v in record.items() if k!="evaluation_id"})
            or record["artifact_sha256"] != {n:sha(v) for n,v in items.items() if n!="article.json"}
            or record["source_sha256"] != source_hashes()):
        raise ValueError("Regenerate the mechanical article from matching sources")
    return items


def artifacts(parent):
    """Bind the reviewed mechanical packet to an exact Airport operating and cost case."""
    items = read_compact()
    article = json.loads(items.pop("article.json"))
    case = parent["opening"]
    if (case["candidate_id"] != article["parent_candidate_id"]
            or case["evaluation_id"] != article["parent_evaluation_id"]
            or case["candidate_id"] != identity(case["bundle"])
            or case["bundle"]["vehicle_revision"] != article["parent_frame_revision"]
            or parent["selection"]["physical_candidate_id"] != case["candidate_id"]
            or parent["service"]["evaluation_id"] != article["parent_service_evaluation_id"]
            or parent["service"]["evaluation_id"] != identity({k:v for k,v in parent["service"].items() if k!="evaluation_id"})
            or parent["assembly"]["candidate_id"] != case["candidate_id"]
            or parent["selection"]["service_evaluation_id"] != parent["service"]["evaluation_id"]):
        raise ValueError("Mechanical prototype requires its source-bound Airport parent")
    inputs = airport_opening.opening_inputs()
    child = airport_opening.calculate(inputs=inputs,service=parent["service"],size_feeder=True,
                loaded_mass_t=article["planning_crowd_train_t"],vehicle_revision=article["frame_revision"])
    if child["power"]["parent_candidate_id"] != child["candidate_id"] or child["candidate_id"] == case["candidate_id"]:
        raise ValueError("Mechanical revision did not propagate into the opening")
    finance = airport_finance.evaluate(child, inputs[0], inputs[0]["service_plan"]["departures_per_hour_direction"])
    record = dict(article, candidate_id=child["candidate_id"], parent_evaluation_id=case["evaluation_id"],
             opening=child, finance=finance, article_evaluation_id=article["evaluation_id"],
             mass_basis="Parent gross planning load plus the six-car difference in counted stock. All other tare and payload held constant as a sensitivity; actual net installed mass may change.",
             cost_scope="Updated civil, electrical and operating planning quantities. Fleet purchase rates remain allowances; the revised car and liner price, tooling and time in maintenance need quotes.")
    record.pop("evaluation_id")
    record["evaluation_id"] = identity(record)
    items["workshop-guide.md"] = (HERE/"mechanical.md").read_bytes()
    return record,items


def build(parent):
    return artifacts(parent)[0]
