"""Build two straight-station operator views from candidate-bound project records."""

from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json
import math
import tomllib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CORE = "docs/reference-v07/"
BAG = "cities/Baghdad/"
PACKET = "docs/design-engine/v07-prototype-bundle/packet/result.json"


def digest(path):
    return sha256((ROOT / path).read_bytes()).hexdigest()


def read(path):
    text = (ROOT / path).read_text()
    return tomllib.loads(text) if path.endswith(".toml") else json.loads(text)


def core():
    selpath, parentpath = (
        CORE + "digital/selected.toml",
        CORE + "integration/candidate.toml",
    )
    selection, parent = read(selpath), read(parentpath)
    supply = read(CORE + "digital/production/handoff.json")
    assert supply["physical_candidate_id"] == selection["physical_candidate_id"]
    assert supply["source_selection_evaluation_id"] == selection["evaluation_id"]
    assert supply["selection_id"] == selection["selection_id"]
    vehiclepath = CORE + "digital/vehicle/result.json"
    v = read(vehiclepath)
    assert selection["source_sha256"]["parent_joined_candidate"] == digest(parentpath)
    assert selection["source_sha256"]["digital_vehicle_result"] == digest(vehiclepath)
    assert selection["source_sha256"]["digital_civil_result"] == digest(
        CORE + "digital/civil/result.json"
    )
    assert (
        selection["parent_joined_physical_candidate_id"]
        == parent["physical_candidate_id"]
    )
    assert read(CORE + "digital/vehicle/input.json")["source_sha256"][PACKET] == digest(
        PACKET
    )
    packet = read(PACKET)
    assert (
        packet["candidate"]["candidate_id"]
        == parent["ancestry"]["powered_vehicle_physical_candidate_id"]
    )
    inherited = "docs/design-engine/current/evaluation.json.gz"
    assert read(CORE + "digital/vehicle/input.json")["source_sha256"][
        inherited
    ] == digest(inherited)
    mech = packet["candidate"]["physical_definition"]["mechanical_definition"]
    i = parent["station"]
    veh = parent["vehicle"]
    beam = selection["beam"]
    return dict(
        name="Core railway",
        subtitle="v0.7 powered-wheel study",
        key="core",
        candidate=selection["physical_candidate_id"],
        evaluation=selection["evaluation_id"],
        selection=selection["selection_id"],
        source=selpath,
        sourcePaths=[
            selpath,
            parentpath,
            CORE + "integration/interfaces.csv",
            CORE + "digital/vehicle/input.json",
            vehiclepath,
            inherited,
            CORE + "digital/civil/result.json",
            PACKET,
            CORE + "digital/production/handoff.json",
        ],
        body=[veh["car_body_length_m"], veh["car_body_width_m"], 3.8069],
        floor=veh["rail_to_floor_m"],
        carCount=veh["cars_per_train"],
        length=veh["train_end_to_end_length_m"],
        doorX=[-4.5, 4.5],
        doorWidth=veh["clear_door_width_m"],
        doorSides=[1],
        bogieX=mech["bogie_centres_car_x_m"],
        wheelbase=2.1,
        platform=[i["platform_length_m"], i["platform_width_m"]],
        spacing=i["nominal_track_centres_m_at_straight_station"],
        beam=[beam["length_m"], beam["width_m"], beam["depth_m"]],
        places=parent["requirements"]["normal_places_per_train"],
        scope="30 km synthetic corridor · 12 stations · 51 trainsets",
        quantity=f'{beam["bare_beam_mass_t"]:.6f} t per bare beam, including counted steel. Thirteen strands per beam.',
        collection="1.5 kV rigid overhead",
        powerText="Six stowed roof collectors and a proposed 4.8 m contact height. Check sharing, isolation, earthing and the full suspension travel.",
        control="Two train protection channels, two radio links, six car nodes, 12 door controllers and 12 bogie brake controllers per train. Compare equipment schedules with the marked installation zones. Actual cabinet positions remain open.",
        hold="Measure platform and door heights under empty and loaded suspension. Prove one-sided dispatch and stopping tolerance at both terminal turnbacks.",
        links=dict(
            body=CORE + "vehicle/README.md",
            bogie=CORE + "manufacturing/README.md",
            door=CORE + "integration/interfaces.csv",
            platform=CORE + "integration/README.md",
            beam=CORE + "digital/civil/README.md",
            power=CORE + "integration/README.md",
            control=CORE + "digital/production/README.md",
        ),
    )


def baghdad():
    source = BAG + "system-results.json"
    cfg, result, mech = (
        read(BAG + "system.toml"),
        read(source),
        read(BAG + "engineering/mechanical/schedule.json"),
    )
    assert result["source_sha256"][BAG + "system.toml"] == digest(BAG + "system.toml")
    n = result["networks"]["first"]
    assert (
        n["digital_cost_leader"] == "protected_conductor"
        and n["selected_digital_civil_family"] == "10m-separate"
    )
    assert (
        mech["parent_selected_candidate_id"]
        == n["selected_candidate_id"]
        == n["power_cases"]["protected_conductor"]["physical_candidate_id"]
    )
    assert mech["parent_evaluation_id"] == n["selected_evaluation_id"]
    civil = read(BAG + "engineering/mechanical/civil/section-results.json")
    assert civil["parent_physical_id"] == mech["study_physical_id"]
    assert civil["parent_evaluation_id"] == mech["study_evaluation_id"]
    section = read(BAG + "engineering/mechanical/civil/concept.toml")
    assert civil["source_sha256"][
        "engineering/mechanical/civil/concept.toml"
    ] == digest(BAG + "engineering/mechanical/civil/concept.toml")
    geom, p, prog = (
        cfg["vehicle_geometry"],
        cfg["station_geometry"],
        cfg["networks"]["first"],
    )
    ctr = n["selected_control_electronics"]["installed_train_items"]
    return dict(
        name="Baghdad",
        subtitle="First programme · protected conductor",
        key="baghdad",
        candidate=n["selected_candidate_id"],
        evaluation=n["selected_evaluation_id"],
        selection="networks.first.digital_cost_leader / protected_conductor",
        source=source,
        sourcePaths=[
            source,
            BAG + "system.toml",
            BAG + "engineering/mechanical/schedule.json",
            BAG + "engineering/mechanical/quotation.toml",
            BAG + "engineering/mechanical/civil/concept.toml",
            BAG + "engineering/mechanical/civil/section-results.json",
        ],
        body=[geom["car_body_length_m"], geom["body_width_m"], 3.2],
        floor=geom["floor_above_rail_m"],
        carCount=cfg["vehicle"]["cars_per_train"],
        length=geom["train_length_m"],
        doorX=geom["door_centres_m"],
        doorWidth=geom["door_clear_width_m"],
        doorSides=[-1, 1],
        bogieX=geom["bogie_centres_m"],
        wheelbase=read(BAG + "engineering/mechanical/quotation.toml")["rig"][
            "wheelbase_m"
        ],
        platform=[p["platform_clear_length_m"], p["island_width_m"]],
        spacing=p["straight_track_centre_spacing_m"],
        beam=[
            cfg["selected_span_m"],
            section["box"]["width_m"],
            section["box"]["depth_m"],
        ],
        places=cfg["vehicle"]["normal_places_per_train"],
        offset=geom["contact_rail_outboard_offset_m"],
        scope=f'{prog["route_km"]} km planning allowance · {prog["stations"]} stations · {prog["fleet_trainsets"]} trainsets',
        quantity="29,640 planned beams and 29,654 separate-track support positions in the first programme. Trial box dimensions and bogie wheelbase follow the linked quotation study.",
        collection="Protected side conductor",
        powerText="Four monitored shoe sets per train. The outboard conductor lies 1.9 m from track centre. Shoe positions, protection geometry and voltage selection remain open.",
        control=f'{ctr["atp_channel"]} train protection channels, {ctr["radio_link"]} radios, {ctr["tcms_node"]} car nodes, {ctr["door_controller"]} door controllers and {ctr["brake_controller"]} bogie brake controllers per train. Equipment groups allow 299 kg and 3.68 kW including harness allocations. Cabinet markers indicate logical ownership.',
        hold="Prove the platform-side release on a double-sided car. Measure loaded threshold movement, stopping tolerance, shoe clearance and accessible boarding.",
        links=dict(
            body=BAG + "engineering/mechanical/vehicle/README.md",
            bogie=BAG + "engineering/mechanical/README.md",
            door=BAG + "VEHICLE.md",
            platform=BAG + "engineering/mechanical/civil/README.md",
            beam=BAG + "engineering/mechanical/civil/README.md",
            power=BAG + "VEHICLE.md",
            control=BAG + "engineering/controls/README.md",
        ),
    )


def scene(s):
    length, width, roof = s["body"]
    floor = s["floor"]
    t = -s["spacing"] / 2
    step = (s["length"] - length) / (s["carCount"] - 1)
    assert step >= length
    assert abs(abs(t) - s["platform"][1] / 2 - width / 2 - 0.075) < 1e-6
    records = []
    if s["key"] == "core":
        with gzip.open(
            ROOT / "docs/design-engine/current/evaluation.json.gz", "rt"
        ) as stream:
            car_geometry = json.load(stream)["vehicle"]["geometry_parts"]
        running_gear = [p for p in car_geometry if p["system"] == "bogies"]
        assert len(running_gear) == 60
        packet_parts = read(PACKET)["nominal_ifc_parts"]
        checked_mass = 0.0
        for p in running_gear:
            if p["kind"] == "box":
                volume = math.prod(p["size_m"])
            else:
                assert p["axis"] == [0, 1, 0]
                volume = (
                    math.pi
                    * (p["radius_m"] ** 2 - p["inner_radius_m"] ** 2)
                    * p["length_m"]
                )
            checked_mass += volume * p["density_kg_m3"]
        reference = read(CORE + "digital/vehicle/result.json")["component_handoff"][
            "inherited_modelled_geometry"
        ]
        assert (
            abs(
                checked_mass
                - next(
                    r["located_mass_kg"] for r in reference if r["system"] == "bogies"
                )
            )
            < 1e-6
        )
        s["modelledBogieStockKgPerCar"] = round(checked_mass, 6)

    def add(group, name, x, y, z, a, b, c, style, shape="box"):
        records.append(
            [group, name, *[round(v, 5) for v in (x, y, z, a, b, c)], style, shape]
        )

    for i in range(s["carCount"]):
        cx = (i - (s["carCount"] - 1) / 2) * step
        car = f"C{i+1:02d}"
        add("body", car + "/floor", cx, t, floor - 0.08, length, width, 0.16, "floor")
        add("body", car + "/roof", cx, t, roof - 0.07, length, width, 0.14, "roof")
        for side in (-1, 1):
            y = t + side * (width / 2 - 0.045)
            openings = s["doorX"] if side in s["doorSides"] else []
            ends = (
                [-length / 2]
                + [
                    p + d
                    for p in openings
                    for d in (-s["doorWidth"] / 2, s["doorWidth"] / 2)
                ]
                + [length / 2]
            )
            for j, (left, right) in enumerate(zip(ends[::2], ends[1::2])):
                mid = cx + (left + right) / 2
                h = roof - floor - 0.16
                name = f"{car}/side{side:+d}/bay{j+1}"
                add(
                    "body",
                    name + "/sill",
                    mid,
                    y,
                    floor + 0.37,
                    right - left,
                    0.09,
                    0.74,
                    "sill",
                )
                add(
                    "body",
                    name + "/glazing",
                    mid,
                    y,
                    floor + 0.74 + (h - 0.74) / 2,
                    right - left,
                    0.085,
                    h - 0.74,
                    "glass",
                )
                for k in range(1, round((right - left) / 1.4)):
                    sx = cx + left + k * (right - left) / round((right - left) / 1.4)
                    add(
                        "body",
                        name + f"/post{k}",
                        sx,
                        y + side * 0.005,
                        floor + 0.74 + (h - 0.74) / 2,
                        0.07,
                        0.09,
                        h - 0.74,
                        "roof",
                    )
            for j, dx in enumerate(openings):
                h = roof - floor - 0.18
                add(
                    "door",
                    f"{car}/side{side:+d}/D{j+1}",
                    cx + dx,
                    y,
                    floor + h / 2,
                    s["doorWidth"],
                    0.095,
                    h,
                    "door",
                )
        for side in (-1, 1):
            add(
                "body",
                f"{car}/end{side:+d}",
                cx + side * (length / 2 - 0.045),
                t,
                (roof + floor) / 2,
                0.09,
                width,
                roof - floor,
                "end",
            )
        # Symbols show controller ownership. Cabinet envelope and location remain open.
        add(
            "control",
            car + "/node-zone",
            cx,
            t - 0.50,
            0.57,
            0.64,
            0.43,
            0.32,
            "control",
        )
        for j, bx in enumerate(s["bogieX"] if s["key"] == "baghdad" else []):
            name = f"{car}/B{j+1}"
            for side in (-1, 1):
                add(
                    "bogie",
                    f"{name}/frame{side:+d}",
                    cx + bx,
                    t + side * 0.95,
                    0.52,
                    2.84,
                    0.16,
                    0.22,
                    "frame",
                )
            for k, dx in enumerate((-s["wheelbase"] / 2, s["wheelbase"] / 2)):
                x = cx + bx + dx
                add(
                    "bogie",
                    f"{name}/A{k+1}",
                    x,
                    t,
                    0.38,
                    0.14,
                    1.72,
                    0.14,
                    "axle",
                    "cylinder",
                )
                for side in (-1, 1):
                    add(
                        "bogie",
                        f"{name}/A{k+1}/wheel{side:+d}",
                        x,
                        t + side * 0.7575,
                        0.38,
                        0.76,
                        0.13,
                        0.76,
                        "wheel",
                        "cylinder",
                    )
        if s["key"] == "core":
            # The prototype file steps cars at 17 m. Transfer car-local coordinates
            # onto the 17.5 m pitch of the joined station formation.
            for p in running_gear:
                ids = p["id"].split("/")
                role = ids[2]
                if role == "axle":
                    name = f"{car}/B{int(ids[1])+1}/A{int(ids[3])+1}"
                else:
                    name = car + "/" + p["id"]
                xyz = p["cg_m"]
                if p["kind"] == "box":
                    size = p["size_m"]
                    add("bogie", name, cx + xyz[0], t + xyz[1], xyz[2], *size, "frame")
                else:
                    dia = 2 * p["radius_m"]
                    style = {
                        "axle": "axle",
                        "wheel": {"rim": "wheel", "web": "web", "hub": "hub"}.get(
                            ids[-1]
                        ),
                        "brake": "disc",
                    }[role]
                    add(
                        "bogie",
                        name,
                        cx + xyz[0],
                        t + xyz[1],
                        xyz[2],
                        dia,
                        p["length_m"],
                        dia,
                        style,
                        "cylinder",
                    )
                    records[-1].append(p["inner_radius_m"])
            for part in (p for p in packet_parts if p["id"].startswith(f"car-{i+1}/")):
                x, y, z = part["centre_m"]
                style = {
                    "motor-envelope": "motor",
                    "rail-brake-shoe-envelope": "brake",
                    "collector-stowed-envelope": "collection",
                }[part["kind"]]
                add(
                    "power" if style == "collection" else "bogie",
                    f'{car}/{part["id"].split("/",1)[1]}',
                    cx + x - i * length,
                    t + y,
                    z,
                    *part["size_m"],
                    style,
                )
    span, beamwidth, depth = s["beam"]
    # 140 m straight display with fourteen complete bays per track and explicit end supports.
    for side in (-1, 1):
        y = side * s["spacing"] / 2
        track = "T1" if side == -1 else "T2"
        for j in range(14):
            x = (j - 6.5) * span
            add(
                "beam",
                f"{track}/span{j+1:02d}",
                x,
                y,
                -0.2 - depth / 2,
                span,
                beamwidth,
                depth,
                "beam",
            )
        for j in range(15):
            x = (j - 7) * span
            add(
                "beam",
                f"{track}/pier{j+1:02d}",
                x,
                y,
                -0.2 - depth - 3,
                1,
                1,
                6,
                "pier",
            )
        for k in (-1, 1):
            add(
                "beam",
                f"{track}/rail{k:+d}",
                0,
                y + k * (1.435 / 2 + 0.035),
                -0.085,
                14 * span,
                0.07,
                0.17,
                "rail",
            )
        if s["key"] == "baghdad":
            add(
                "power",
                track + "/protected-conductor",
                0,
                y + side * s["offset"],
                0.38,
                14 * span,
                0.18,
                0.20,
                "collection",
            )
        else:
            add(
                "power",
                track + "/overhead-contact",
                0,
                y,
                4.8,
                14 * span,
                0.08,
                0.07,
                "collection",
            )
    pl, pw = s["platform"]
    add("platform", "ISL/deck", 0, 0, floor - 0.17, pl, pw, 0.34, "platform")
    for side in (-1, 1):
        add(
            "platform",
            f"ISL/edge{side:+d}",
            0,
            side * (pw / 2 - 0.16),
            floor + 0.008,
            pl,
            0.26,
            0.016,
            "edge",
        )
    # Station substructure is deliberately omitted pending an independent frame.
    assert len({r[1] for r in records}) == len(records)
    counts = Counter(r[8] for r in records)
    assert counts["door"] == s["carCount"] * len(s["doorX"]) * len(s["doorSides"])
    assert (
        counts["wheel"] == 48
        and counts["axle"] == 24
        and counts["beam"] == 28
        and counts["pier"] == 30
    )
    assert counts["motor"] == (24 if s["key"] == "core" else 0)
    s["sourceHashes"] = {
        p: digest(p)
        for p in sorted(set(s.pop("sourcePaths") + list(s["links"].values())))
    }
    s["parts"] = records
    return s


def frame_study():
    """Load the actual quotation mesh with its own candidate and stock quantities."""
    folder = BAG + "engineering/mechanical/vehicle/"
    result = read(folder + "result.json")
    assert (
        result["parent_train_id"]
        == read(BAG + "system-results.json")["networks"]["first"][
            "selected_candidate_id"
        ]
    )
    assert result["selection"] is None and not result["physical_accepted"]
    for path, expected in result["source_sha256"].items():
        assert digest(path) == expected, path
    mesh_path = folder + "braced-frame.obj"
    verts = []
    rows = []
    shapes = {}
    for line in (ROOT / mesh_path).read_text().splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] == "o":
            name = fields[1]
            shapes[name] = []
        elif fields[0] == "v":
            verts.append([float(x) for x in fields[1:]])
        elif fields[0] == "f":
            shapes[name].append([int(i) - 1 for i in fields[1:]])
    assert len(shapes) == result["braced_mesh_component_count"]
    for name, faces in shapes.items():
        points = [verts[i] for face in faces for i in face]
        lo, hi = ([fn(p[i] for p in points) for i in range(3)] for fn in (min, max))
        centre = [round((a + b) / 2, 6) for a, b in zip(lo, hi)]
        dims = [round(b - a, 6) for a, b in zip(lo, hi)]
        family = name.rsplit("_", 1)[0]
        style = (
            "brace"
            if family == "brace"
            else (
                "plate"
                if family.startswith(("primary", "secondary"))
                else (
                    "bogiestock"
                    if family in ("bogie_side", "transom", "saddle")
                    else "stock"
                )
            )
        )
        rows.append(["stock", name, *centre, *dims, style, "mesh"])
    return dict(
        key="frame",
        name="Baghdad carbody",
        subtitle="First article · braced frame quotation B",
        scope="One carbody and two bogie frames · cut steel stock",
        candidate=result["braced_revision_id"],
        evaluation=result["evaluation_id"],
        selection="Unselected first-article quotation revision",
        source=folder + "result.json",
        sourceHashes={
            p: digest(p)
            for p in [
                folder + "result.json",
                mesh_path,
                folder + "cut-list.csv",
                folder + "stock.toml",
            ]
        },
        parent=result["parent_train_id"],
        links={"stock": folder + "README.md"},
        stockKg=result["braced_body_and_two_bogie_cut_stock_kg_per_car"],
        vertices=verts,
        faces=shapes,
        parts=rows,
    )


if __name__ == "__main__":
    import argparse
    from export_ifc import export

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    opts = ap.parse_args()
    data = {}
    inventory = {}
    for candidate in (core(), baghdad()):
        model = scene(candidate)
        data[model["key"]] = model
        target = HERE / (model["key"] + ".ifc")
        export(model, target, opts.check)
        key = model["key"]
        docs = (
            [
                CORE + "manufacturing/bom.csv",
                CORE + "manufacturing/routing.csv",
                CORE + "manufacturing/lifecycle-draft.json",
                CORE + "digital/production/handoff.json",
            ]
            if key == "core"
            else [
                BAG + "engineering/mechanical/schedule.json",
                BAG + "engineering/mechanical/vehicle/cut-list.csv",
                BAG + "engineering/mechanical/civil/section-results.json",
                BAG + "BUYER-COMPARISON.md",
            ]
        )
        inventory[key] = dict(
            candidate=model["candidate"],
            evaluation=model["evaluation"],
            selection=model["selection"],
            view_revision="operator-station-envelope.1",
            serial=None,
            physical_acceptance=False,
            installed_train_mass_kg=None,
            purpose="Operator comparison of adjacent assemblies and access interfaces",
            source_sha256=model["sourceHashes"],
            native_ifc_sha256=sha256(target.read_bytes()).hexdigest(),
            native_ifc_occurrences=len(model["parts"]),
            occurrence_counts_in_display_window=dict(
                sorted(Counter(r[8] for r in model["parts"]).items())
            ),
            production_and_procurement_record_sha256={p: digest(p) for p in docs},
        )
        if key == "core":
            inventory[key]["located_bogie_geometry_kg_per_car"] = model[
                "modelledBogieStockKgPerCar"
            ]
    receipt = HERE / "model-register.json"
    record = json.dumps(inventory, sort_keys=True, indent=2) + "\n"
    if opts.check:
        assert receipt.read_text() == record
    else:
        receipt.write_text(record)
    data["frame"] = frame_study()
    target = HERE / "models.js"
    output = (
        "window.RAIL_MODELS="
        + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        + ";\n"
    )
    if opts.check:
        assert target.read_text() == output, "Regenerate the operator scene."
    else:
        target.write_text(output)
