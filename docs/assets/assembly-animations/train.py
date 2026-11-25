"""Assembly presentation of the Baghdad Airport first article and proposed fitout."""

from csv import DictReader
from functools import lru_cache
from hashlib import sha256
from io import StringIO
from json import loads
from pathlib import Path
from zipfile import ZipFile

from scene import Camera, Frame, Item, Mesh, box, combine, load_obj
from train_fitout import at, fitout_groups, staged


ROOT = Path(__file__).resolve().parents[3]
PROTOTYPE = "cities/Baghdad/engineering/prototype"
PACKET = f"{PROTOTYPE}/airport-prototype.zip"
CAM = f"{PROTOTYPE}/cam/cam-manifest.json"
SAW_CUTS = f"{PROTOTYPE}/cam/saw-cuts.csv"
FACTORY = f"{PROTOTYPE}/factory-routes.json"
GA = f"{PROTOTYPE}/vehicle-factory/installed-ga.json"
FITOUT_BOM = f"{PROTOTYPE}/vehicle-factory/installed-fitout-bom.csv"
QUOTE = f"{PROTOTYPE}/vehicle-factory/vehicle-quote.csv"
RAPID = f"{PROTOTYPE}/rapid-production/comparison.json"
ESTIMATE = f"{PROTOTYPE}/sourcing-estimate.json"
FITOUT_SCENE = "docs/assets/assembly-animations/train_fitout.py"
SOURCES = (PACKET, CAM, SAW_CUTS, FACTORY, GA, FITOUT_BOM, QUOTE, RAPID, ESTIMATE, FITOUT_SCENE)

TITLE = "Building and fitting the six-car Airport train"
DURATION = 188
POSTER_TIME = 92
CHAPTERS = (
    (0, "Cut and kit"),
    (10, "Underframe"),
    (22, "Side frames"),
    (39, "Roof and portals"),
    (48, "Bogie frames"),
    (58, "Body and bogies"),
    (72, "Powered equipment"),
    (90, "Saloon installation"),
    (108, "Doors and enclosure"),
    (126, "Two terminal cabs"),
    (145, "Couplers and services"),
    (166, "Gangways and formation"),
    (178, "Six-car overview"),
)

STRUCTURE = "#337f92"
FLOOR_STEEL = "#598b9d"
SIDE_STEEL = ("#467991", "#278397")
BRACES = ("#739caa", "#72a9b2")
GUSSET = "#c4ad83"
ROOF = "#659dae"
BOGIE = "#4f746f"
BOLSTER = "#ad814c"
LINER = "#dbbb72"
FIXTURE = "#869496"
DECK = "#304c60"
FLOOR_LINE = "#526c7f"
AMBER = "#e9a24a"
DARK = "#445b63"


def read_source():
    with ZipFile(ROOT / PACKET) as archive:
        manifest_bytes = archive.read("manifest.json")
        manifest = loads(manifest_bytes)
        mechanical_bytes = archive.read("mechanical.json")
        geometry = archive.read("car-and-bogies.obj")
    mechanical = loads(mechanical_bytes)
    cam = loads((ROOT / CAM).read_bytes())
    factory = loads((ROOT / FACTORY).read_bytes())
    for name, data in (("mechanical.json", mechanical_bytes), ("car-and-bogies.obj", geometry)):
        if sha256(data).hexdigest() != manifest["sha256"][name]:
            raise ValueError(f"Archive member changes from the sealed digest: {name}")
    if (
        sha256(geometry).hexdigest() != mechanical["artifact_sha256"]["car-and-bogies.obj"]
        or sha256(manifest_bytes).hexdigest() != cam["source_sha256"]["manifest.json"]
        or cam["packet_evaluation_id"] != manifest["evaluation_id"]
        or cam["mechanical_evaluation_id"] != mechanical["evaluation_id"]
        or any(source["candidate_id"] != manifest["candidate_id"] for source in (mechanical, cam, factory))
        or any(source["frame_revision"] != manifest["article"] for source in (mechanical, cam, factory))
    ):
        raise ValueError("The CAD, fabrication and CAM sources differ in identity")
    if not geometry.startswith(b"# Baghdad first-article lined jamb revision. Metres."):
        raise ValueError("Expected metre-based Baghdad first-article geometry")

    pieces = {piece["id"]: piece for piece in mechanical["pieces"]}
    meshes = load_obj(geometry.decode())
    if len(pieces) != len(mechanical["pieces"]) or set(pieces) != set(meshes):
        raise ValueError("The stock register differs from the CAD part names")
    for key, mesh in meshes.items():
        piece = pieces[key]
        for bound, reference in zip(mesh.bounds, (piece["lower_m"], piece["upper_m"]), strict=True):
            if max(abs(a - b) for a, b in zip(bound, reference, strict=True)) > 0.000002:
                raise ValueError(f"CAD coordinates differ from article bounds for {key}")

    cut_data = (ROOT / SAW_CUTS).read_bytes()
    if sha256(cut_data).hexdigest() != cam["artifact_sha256"]["saw-cuts.csv"]:
        raise ValueError("CAM cut-plan digest differs")
    kit_piece = next(
        key for key, piece in pieces.items()
        if piece["assembly"] == "body" and piece["part"] == "floor_tie"
    )
    low, high = meshes[kit_piece].bounds
    tie_length = round((high[1] - low[1]) * 1000)
    if not any(
        cut["part"] == "floor_tie" and abs(float(cut["length_mm"]) - tie_length) < 0.01
        for cut in DictReader(StringIO(cut_data.decode()))
    ):
        raise ValueError("No matching floor-tie blank in the CAM cut plan")

    return pieces, meshes, kit_piece, {
        "candidate_id": manifest["candidate_id"],
        "frame_revision": manifest["article"],
        "mechanical_evaluation_id": mechanical["evaluation_id"],
        "packet_evaluation_id": manifest["evaluation_id"],
        "cam_evaluation_id": cam["evaluation_id"],
        "factory_evaluation_id": factory["evaluation_id"],
        "mesh_sha256": manifest["sha256"]["car-and-bogies.obj"],
        "parts_by_assembly": {
            assembly: sum(piece["assembly"] == assembly for piece in pieces.values())
            for assembly in ("body", "bogie-A", "bogie-B")
        },
    }


PIECES, MESHES, KIT_PIECE, IDENTITY = read_source()


def side(mesh):
    low, high = mesh.bounds
    return (low[1] + high[1] > 0)


def classify(piece, mesh):
    kind = piece["part"]
    lateral = int(side(mesh))
    if piece["assembly"].startswith("bogie-"):
        bogie = piece["assembly"][-1]
        if kind in ("bogie_side", "primary_underside"):
            return f"bogie-{bogie}-side-{lateral}"
        if kind == "secondary_top":
            return f"bogie-{bogie}-pads"
        return f"bogie-{bogie}-cross"
    if kind in ("sill", "jamb_liner", "brace", "gusset"):
        return f"{kind}-{lateral}"
    return {
        "floor_tie": "floor",
        "bolster": "bolster",
        "secondary_body": "bolster",
        "end_tie": "ends",
        "roof_tie": "roof",
        "cantrail": f"side-{lateral}",
        "jamb": f"side-{lateral}",
        "end_post": f"side-{lateral}",
    }[kind]


def build_groups():
    members = {}
    for key, piece in PIECES.items():
        mesh = MESHES[key]
        members.setdefault(classify(piece, mesh), []).append(mesh)
    return {name: combine(name, meshes) for name, meshes in members.items()}


GROUPS = build_groups()


def smooth(value, start, end):
    unit = max(0.0, min(1.0, (value - start) / (end - start)))
    return unit * unit * (3.0 - 2.0 * unit)


def mix(start, end, weight):
    return start + (end - start) * weight


def cut_part(name):
    mesh = MESHES[name]
    low, high = mesh.bounds
    return Mesh("cut blank", mesh.vertices - (low + high) / 2, mesh.faces)


def base(name, lo, hi, color=FIXTURE, layer=0):
    return Item(box(name, lo, hi), color, outline=False, layer=layer)


def jig_tiles(span, half_width, z=-0.24):
    """Presentation fixtures use the indicative factory bed footprints."""
    return [
        base("bed rail", (-span, side_y - 0.08, z), (span, side_y + 0.08, z + 0.12), DARK)
        for side_y in (-half_width, half_width)
    ] + [
        base("support crossbar", (x - 0.08, -half_width, z + 0.02),
             (x + 0.08, half_width, z + 0.1))
        for x in (-span * 0.87, -span * 0.43, 0, span * 0.43, span * 0.87)
    ]


BODY_FLOOR = base("presentation floor", (-10.5, -4.9, -0.28),
                  (10.5, 4.9, -0.275), DECK, layer=-2)
BODY_JIG = [
    BODY_FLOOR, *jig_tiles(9.0, 1.52),
    *[base("locator pedestal", (x - 0.23, y - 0.14, -0.12),
           (x + 0.23, y + 0.14, 0.76), FIXTURE)
      for x in (-6.4, -2.8, 2.8, 6.4) for y in (-1.28, 1.28)],
]
BOGIE_JIG = jig_tiles(1.60, 1.17, z=-0.12)
BOGIE_FLOOR = base("presentation floor", (-2.8, -2.0, -0.34), (2.8, 2.0, -0.335), DECK, layer=-2)
ASSEMBLY_FLOOR = base("presentation floor", (-11.7, -4.2, -0.29),
                      (11.7, 4.2, -0.285), DECK, layer=-2)
BED_MARKS = [
    base("floor datum mark", (x - 0.007, -4.74, -0.273), (x + 0.007, 4.74, -0.269), FLOOR_LINE, layer=-1)
    for x in range(-10, 11, 2)
]
CUT = cut_part(KIT_PIECE)
SAW = [
    base("material support", (-3.4, -0.42, -0.09), (3.25, 0.42, -0.04), DARK),
    *[base("roller envelope", (x - 0.14, -0.30, 0.30), (x + 0.14, 0.30, 0.42))
      for x in (-3.05, -2.1, -1.1, 0.8, 1.8, 2.85)],
    *[base("roller support legs", (x - 0.15, -0.23, -0.04), (x + 0.15, 0.23, 0.32))
      for x in (-3.05, -1.1, 0.8, 2.85)],
    base("illustrative saw housing", (-0.48, 0.22, -0.04), (0.27, 0.79, 1.47), DARK),
    base("illustrative saw housing", (-0.48, -0.64, 1.1), (0.27, 0.79, 1.47), AMBER),
    base("kit staging table", (0.05, -2.2, 0.32), (3.35, -0.87, 0.42)),
    *[base("staging table leg", (x - 0.06, y - 0.06, -0.04), (x + 0.06, y + 0.06, 0.32))
      for x in (0.16, 3.24) for y in (-2.09, -0.98)],
]
SAW_FLOOR = base("presentation floor", (-4.25, -2.7, -0.12), (4.1, 1.6, -0.115), DECK, layer=-2)
SAW_HEAD = box("illustrative moving saw head", (-0.13, -0.54, 0), (0.13, 0.51, 0.25))
KIT_PLATE = cut_part(next(key for key, row in PIECES.items() if row["part"] == "gusset"))


def cut_shot(t):
    lower_head = smooth(t, 0.8, 2.5) * (1 - smooth(t, 3.4, 4.7))
    transfer = smooth(t, 4.8, 8.5)
    clear = smooth(t, 4.8, 5.8) * (1 - smooth(t, 7.5, 8.7))
    items = [
        SAW_FLOOR, *SAW, Item(SAW_HEAD, AMBER, offset=(0, 0, 0.98 - 0.52 * lower_head)),
        Item(CUT, FLOOR_STEEL, offset=(-1.249, 0, 0.51), yaw=90),
        Item(CUT, STRUCTURE, offset=(1.23 + 0.30 * transfer, -1.13 * transfer, 0.51 + 0.38 * clear), yaw=90),
        Item(CUT, FLOOR_STEEL, offset=(1.68, -1.57, 0.51), yaw=90),
        Item(CUT, FLOOR_STEEL, offset=(1.68, -1.85, 0.51), yaw=90),
        Item(KIT_PLATE, GUSSET, offset=(3.10, -1.72, 0.65)),
    ]
    w = smooth(t, 0, 10)
    return Frame(
        Camera((-0.12 + 0.36 * w, -0.48, 0.40), -63 + 13 * w, 19, 8.7 - 0.5 * w),
        items, "Cut and kit the steel",
        "Prepare section and plate blanks to the cut schedule, then keep the kit traceable.",
        ("2.46 m floor tie", "Illustrative workcell"),
    )


def stock(name, color, dx=0, dy=0, dz=0):
    return Item(GROUPS[name], color, offset=(dx, dy, dz))


def underframe(t, lift=0):
    sill_gap = 0.76 * (1 - smooth(t, 11, 16))
    tie_rise = 1.85 * (1 - smooth(t, 14.8, 21))
    ends_rise = 1.25 * (1 - smooth(t, 17, 21.7))
    return [
        stock("sill-0", STRUCTURE, dy=-sill_gap, dz=lift),
        stock("sill-1", STRUCTURE, dy=sill_gap, dz=lift),
        stock("floor", FLOOR_STEEL, dz=tie_rise + lift),
        stock("bolster", BOLSTER, dz=tie_rise + lift),
        stock("ends", STRUCTURE, dz=ends_rise + lift),
    ]


def side_frames(t, lift=0):
    parts = []
    for pos, multiplier in enumerate((-1, 1)):
        fold = 1 - smooth(t, 25 + pos * 1.6, 35 + pos * 2.0)
        components = (
            (f"side-{pos}", SIDE_STEEL[pos]),
            (f"brace-{pos}", BRACES[pos]),
            (f"gusset-{pos}", GUSSET),
        )
        for name, color in components:
            parts.append(stock(name, color, dy=2.4 * multiplier * fold, dz=0.9 * fold + lift))
    return parts


def roof_and_linings(t, lift=0):
    parts = [
        stock("roof", ROOF, dz=2.45 * (1 - smooth(t, 39.8, 46.3)) + lift),
    ]
    for pos, direction in enumerate((-1, 1)):
        offset = 0.68 * (1 - smooth(t, 42 + pos * 0.25, 47 + pos * 0.4))
        parts.append(stock(f"jamb_liner-{pos}", LINER, dy=offset * direction, dz=lift))
    return parts


def underframe_shot(t):
    w = smooth(t, 10, 22)
    return Frame(
        Camera((0, 0, 1.0), -69 + 12 * w, 25 - 5 * w, 21.1),
        [*BODY_JIG, *BED_MARKS, *underframe(t)],
        "Set the underframe on its datums",
        "Bring in sill members, floor ties, end ties and the two transverse bolsters.",
        ("17 m car frame", "18 × 3.2 m jig envelope"),
    )


def side_shot(t):
    w = smooth(t, 22, 39)
    return Frame(
        Camera((0, 0, 2.02 - 0.53 * w), -70 + 13 * w, 16.5, 22.1),
        [*BODY_JIG, *BED_MARKS, *underframe(t), *side_frames(t)],
        "Bring in both braced side frames",
        "The side assemblies bring their posts, cantrails, braces and gussets to the bed.",
        ("Two side assemblies", "Eight door portals"),
    )


def roof_shot(t):
    w = smooth(t, 39, 48)
    return Frame(
        Camera((0.60 * w, 0, 2.72 - 1.21 * w), -69 - 4 * w, 16, 22.5 - 1.3 * w),
        [*BODY_JIG, *BED_MARKS, *underframe(t), *side_frames(t), *roof_and_linings(t)],
        "Fit roof ties and portal liners",
        "Cross ties span between the cantrails. Sixteen lined-jamb pieces close the portal detail.",
        ("Roof cross ties", "Lined jamb revision"),
    )


def bogie_set(letter, t=None, travel=0, centre_shift=0):
    if t is None:
        rail_gap = transom_rise = pad_rise = 0
    else:
        rail_gap = 0.83 * (1 - smooth(t, 49.5, 55.15))
        transom_rise = 0.96 * (1 - smooth(t, 51.4, 56.0))
        pad_rise = 1.32 * (1 - smooth(t, 53.0, 57.5))
    prefix = f"bogie-{letter}-"
    dx = travel + centre_shift
    return [
        stock(prefix + "side-0", BOGIE, dx=dx, dy=-rail_gap),
        stock(prefix + "side-1", BOGIE, dx=dx, dy=rail_gap),
        stock(prefix + "cross", FLOOR_STEEL, dx=dx, dz=transom_rise),
        stock(prefix + "pads", BOLSTER, dx=dx, dz=pad_rise),
    ]


def bogie_shot(t):
    w = smooth(t, 48, 58)
    return Frame(
        Camera((0, 0, 0.74 - 0.47 * smooth(t, 54.0, 58)),
               -69 + 14 * w, 18 + 4 * w, 8.9 - 1.55 * w),
        [BOGIE_FLOOR, *BOGIE_JIG, *bogie_set("A", t=t, centre_shift=6.4)],
        "Fit up a powered bogie frame",
        "Side members, transoms, saddles and seat plates assemble on the nominal frame jig.",
        ("12 pieces per frame", "Two matching assemblies"),
    )


PAIR_STANDS = [
    (direction, [
        base("illustrative transfer stand", (x - 1.55, -1.17, -0.27),
             (x + 1.55, 1.17, -0.10), FIXTURE),
        *[base("illustrative frame support", (x + local_x - 0.09, y - 0.085, -0.10),
               (x + local_x + 0.09, y + 0.085, 0.378), FIXTURE)
          for local_x in (-1.05, 1.05) for y in (-1.04, 1.04)],
    ])
    for direction, x in ((-1, -6.4), (1, 6.4))
]


def assembly_shot(t):
    travel = 2.20 * (1 - smooth(t, 59.2, 66))
    lift = 1.58 * (1 - smooth(t, 65.6, 71.8))
    items = [ASSEMBLY_FLOOR]
    for direction, stand in PAIR_STANDS:
        items.extend(Item(item.mesh, item.color, offset=(direction * travel, 0, 0), outline=False)
                     for item in stand)
    items.extend(underframe(t, lift))
    items.extend(side_frames(t, lift))
    items.extend(roof_and_linings(t, lift))
    items.extend(bogie_set("A", travel=-travel))
    items.extend(bogie_set("B", travel=travel))
    w = smooth(t, 58, 72)
    return Frame(
        Camera((0, 0, 2.16 - 0.67 * w), -82 + 14 * w, 19 - 1 * w, 23.6 - 2.6 * w),
        items, "Bring body and bogie frames together",
        "Line up both frames under the body. Seat faces leave the nominal suspension allowance open.",
        ("Bogie centres ±6.4 m", "156 mm seat-face gap"),
    )


def frame(seconds):
    if seconds < 10:
        return cut_shot(seconds)
    if seconds < 22:
        return underframe_shot(seconds)
    if seconds < 39:
        return side_shot(seconds)
    if seconds < 48:
        return roof_shot(seconds)
    if seconds < 58:
        return bogie_shot(seconds)
    if seconds < 72:
        return assembly_shot(seconds)
    if seconds < 90:
        return running_shot(seconds)
    if seconds < 108:
        return interior_shot(seconds)
    if seconds < 126:
        return enclosure_shot(seconds)
    if seconds < 145:
        return cab_shot(seconds)
    if seconds < 166:
        return connection_shot(seconds)
    if seconds < 178:
        return gangway_shot(seconds)
    return formation_shot(seconds)


def fitout_sources():
    ga = loads((ROOT / GA).read_bytes())
    rapid = loads((ROOT / RAPID).read_bytes())
    estimate = loads((ROOT / ESTIMATE).read_bytes())
    for source in (ga, rapid, estimate):
        if (source["candidate_id"], source["frame_revision"]) != (
                IDENTITY["candidate_id"], IDENTITY["frame_revision"]):
            raise ValueError("The train fitout references a different physical revision")
    if ga["mechanical_evaluation_id"] != IDENTITY["mechanical_evaluation_id"]:
        raise ValueError("Installed arrangement references a different mechanical evaluation")
    if rapid["factory_evaluation_id"] != IDENTITY["factory_evaluation_id"]:
        raise ValueError("Rapid-production model references a different factory evaluation")
    if rapid["cam_evaluation_id"] != IDENTITY["cam_evaluation_id"]:
        raise ValueError("Rapid-production model references a different CAM evaluation")
    if sha256((ROOT / FITOUT_BOM).read_bytes()).hexdigest() != ga["outputs_sha256"]["installed-fitout-bom.csv"]:
        raise ValueError("Installed fitout BOM differs from the general-arrangement manifest")
    with ZipFile(ROOT / PACKET) as archive:
        mass_bytes = archive.read("revised-cuts.csv")
        if sha256(mass_bytes).hexdigest() != rapid["archive_member_sha256"]["revised-cuts.csv"]:
            raise ValueError("The sealed cut register differs from the rapid-production basis")
    return ga["geometry"], tuple(DictReader(StringIO(mass_bytes.decode()))), rapid


GEOMETRY, CUT_ROWS, RAPID_STUDY = fitout_sources()
FITOUT = fitout_groups(GEOMETRY)
BODY = (*underframe(72), *side_frames(72), *roof_and_linings(72))
RUNNING = (*bogie_set("A"), *bogie_set("B"))
BASE_STAGES = ("axles", "suspension", "drives", "services")
CLOSED_STAGES = ("deck", "shell", "glazing", "roof", "doors", "roof-services")
SALON_STAGES = ("deck", "interior", "underroof")
INSERT_STAGES = ("connector-draft", "connector-utilities", "connector-bridge", "connector-bellows")
CENTRES = GEOMETRY["formation_body_from_car_x_m"]


@lru_cache(maxsize=None)
def fitting(*stages):
    return tuple(staged(FITOUT, stages))


def graded_parts(stages, t, start, end, dx=0, dy=0, dz=0):
    remaining = 1 - smooth(t, start, end)
    return at(fitting(*stages), dx * remaining, dy * remaining, dz * remaining)


def track(x_min, x_max):
    """Presentation-only rails and ground mat under the train."""
    return [
        base("ballast and shop floor context", (x_min,-2.8,-.29), (x_max,2.8,-.259), DECK, layer=-2),
        *[base("running rail", (x_min,y-.037,-.15), (x_max,y+.037,0), "#8b999d")
          for y in (-.72,.72)],
        *[base("track sleeper context", (x-.11,-1.16,-.23), (x+.11,1.16,-.14), "#6c7979")
          for x in range(int(x_min)+1,int(x_max),2)],
    ]


def running_shot(t):
    items = [
        *track(-10.5,10.5), *RUNNING,
        *graded_parts(("axles",),t,72,78,dy=-2.1),
        *graded_parts(("suspension",),t,76,82,dz=.7),
        *graded_parts(("drives",),t,79,85,dy=1.2),
        *graded_parts(("services",),t,81,87,dy=-1.3),
    ]
    return Frame(Camera((-4.2,0,.48),-71 + 17*smooth(t,72,90),20,13.0),
                 items, "Equip the powered bogies",
                 "Fit wheelsets, suspension, traction and brakes. Prepare the underfloor power and controls trays.",
                 ("Baghdad powered bogies", "Equipment study envelopes", "Bearing and brake evidence open"))


def interior_shot(t):
    items = [
        *track(-10,10), *BODY, *RUNNING, *fitting(*BASE_STAGES),
        *graded_parts(("deck",),t,90,95,dz=1.5),
        *graded_parts(("interior",),t,95,103,dz=1.45),
    ]
    return Frame(Camera((0,0,1.72),-72 + 6*smooth(t,90,108),28,20.0),
                 items, "Install the passenger saloon",
                 "Lower the floor panels and fit seats, accessibility fittings, handrails, intercom and emergency equipment.",
                 ("Roof open for access", "Furniture layout study"))


def enclosure_shot(t):
    items = [
        *track(-10,10), *BODY, *RUNNING, *fitting(*BASE_STAGES,"deck","interior"),
        *graded_parts(("underroof",),t,108,112,dz=1.05),
        *graded_parts(("shell","glazing"),t,111,117,dz=1.15),
        *graded_parts(("doors",),t,115,120,dz=1),
        *graded_parts(("roof","roof-services"),t,118,124,dz=1.55),
    ]
    return Frame(Camera((0,0,1.77),-72 + 10*smooth(t,108,126),18,21.6),
                 items, "Close the car envelope",
                 "Fit the duct and lighting runs, then bring in cladding, glazing, door modules, roof panels and HVAC units.",
                 ("Eight door openings per Airport car", "Roof HVAC at two nominated study points"))


def cab_shot(t):
    rear = t >= 135.5
    end = 1 if rear else -1
    run = [*track(-11,11), *BODY, *RUNNING, *fitting(*BASE_STAGES, "deck","interior")]
    start = 135.5 if rear else 126
    for stage, z in (("cab-interior",.85),("cab-nose",.4),("cab-rescue",.0)):
        parts = graded_parts((stage,), t, start+1, start+7, dx=-1.75, dz=z)
        run.extend(at(parts, reverse=rear))
    if not rear:
        run.extend(fitting("shell","glazing","doors","roof","roof-services"))
    title = "Fit the rear-facing terminal cab" if rear else "Fit the forward-facing terminal cab"
    caption = (
        "The opposite cab faces outward at the far end of the set. This open view shows the rear bulkhead and service door."
        if rear else
        "Offer the cab front to the terminal car. Fit the windshield, markers, driver console and rescue mounting."
    )
    return Frame(Camera((end*7.47,0,1.66),-112 if rear else -147,14,8.8),
                 run, title, caption,
                 ("Two opposite terminal cabs", "Cab volumes and rescue mounts are concepts"))


def end_context(gap, *, dress=True):
    half = 8.75 + gap/2
    base_car = (*RUNNING,*fitting(*BASE_STAGES))
    if dress:
        base_car = (*base_car, *fitting("shell","glazing","doors","roof"))
    else:
        base_car = (*base_car, *BODY, *fitting("deck"))
    return [
        *at(base_car,-half), *at(base_car,half),
        *at(fitting("vestibule"), half), *at(fitting("vestibule"),-half,reverse=True),
    ]


def connection_shot(t):
    gap = 1.45 * (1 - smooth(t,156,165))
    items = [
        *track(-5,5), *end_context(gap),
        *graded_parts(("connector-draft",),t,145,155,dy=-1.15),
        *graded_parts(("connector-utilities",),t,151,162,dy=-1.55),
    ]
    return Frame(Camera((0,-.26,.81),-81 + 12*smooth(t,145,166),17,5.7),
                 items, "Mate draft gear and train services",
                 "Bring in the drawbars and heads. Connect the air hose, service power, control bus and bonding strap.",
                 ("500 mm nominal body separation", "Open articulation and load evidence"))


def gangway_shot(t):
    items = [
        *track(-5,5), *end_context(0),
        *fitting("connector-draft","connector-utilities"),
        *graded_parts(("connector-bridge",),t,166,171,dz=.55),
        *graded_parts(("connector-bellows",),t,168,175,dz=.87),
    ]
    return Frame(Camera((0,0,1.55),-86 + 5*smooth(t,166,178),8,7.8),
                 items, "Close the passenger gangway",
                 "Place the non-slip floor bridge above the coupling, then close and seal the framed bellows.",
                 ("Five inter-car connections", "Floor bridge, bellows and sealed carrier frames"))


@lru_cache(maxsize=None)
def closed_formation():
    stock_and_fit = (*RUNNING,*fitting(*BASE_STAGES,*CLOSED_STAGES[1:]))
    items = track(-58,58)
    for index, x in enumerate(CENTRES):
        items.extend(at(stock_and_fit,x))
        if index in (0,len(CENTRES)-1):
            reverse = index != 0
            items.extend(at(fitting("cab-nose","cab-interior","cab-rescue"),x,reverse=reverse))
            items.extend(at(fitting("vestibule"),x,reverse=not reverse))
        else:
            items.extend(at(fitting("vestibule"),x))
            items.extend(at(fitting("vestibule"),x,reverse=True))
        if index < len(CENTRES)-1:
            items.extend(at(fitting(*INSERT_STAGES),(x+CENTRES[index+1])/2))
    return tuple(items)


def formation_shot(t):
    return Frame(Camera((-3,0,1.42),-49 + 9*smooth(t,178,DURATION),15,91), list(closed_formation()),
                 "A six-car Airport train",
                 "Two terminal cabs face out. The five internal junctions connect the cars and their passenger gangways.",
                 ("Baghdad Airport first article", "Concept fitout and end interfaces", "105 m platform reference"))


def exterior_render():
    # Two coupled cars fill the foreground; the full formation remains behind them.
    return Frame(Camera((-37,0,1.61),-147,16,32), list(closed_formation()),
                 "Airport train exterior", "Outboard terminal cab, four-door side and roof HVAC packs.",
                 ("Train exterior and starting end",))


def interior_render():
    items = [*track(-10,10), *BODY, *RUNNING,
             *fitting(*BASE_STAGES,"deck","interior"), *fitting("vestibule"),
             *at(fitting("vestibule"),reverse=True)]
    return Frame(Camera((0,0,1.7),-63,30,19.4), items, "Passenger interior cutaway",
                 "Floor, seat rows, handrails, emergency equipment and two wheelchair bay study locations.",
                 ("Roof and side skin removed for the cutaway",))


def connector_render():
    items = [*track(-5,5), *end_context(.70), *fitting(*INSERT_STAGES)]
    return Frame(Camera((0,0,1.59),-82,9,8.3), items, "Inter-car connection exploded view",
                 "Framed bellows and floor bridge above. Drawgear, air, electrical jumpers and bonding below.",
                 ("Exploded separation for inspection", "Air blue • Service power copper • Control yellow",))


def saloon_render():
    items = [
        *fitting("deck","interior","shell","glazing","doors","roof","underroof"),
        *fitting("vestibule"), *at(fitting("vestibule"),reverse=True),
    ]
    return Frame(Camera((.8,0,1.75),178,0,3.2), items, "Passenger saloon at eye level",
                 "Seats, wheelchair fittings, handrails and ceiling supply runs in an illustrative arrangement.",
                 ("Equipment locations await layout, circulation and evacuation review",))


RENDERS = {"train-exterior": exterior_render, "train-interior": interior_render,
           "train-connector": connector_render, "train-saloon": saloon_render}
RENDER_EYES = {"train-saloon": ((-2.8,-.06,1.65),(4.2,.07,1.68))}


def stock_ledger():
    from ledger import Part

    masses = {}
    for row in CUT_ROWS:
        kind = row["part"]
        gross_kg = float(row["gross_mass_kg"]) * (2 if row["assembly"] == "bogie" else 1)
        masses[kind] = masses.get(kind, 0) + gross_kg
    cut_kg = sum(masses.values())
    if abs(cut_kg - 5272.6597) > .002:
        raise ValueError("Gross stock mass differs from the first-article takeoff")
    shared_cnc = RAPID_STUDY["orders"]["36"]["shared_cnc"]
    price_cases = shared_cnc["price_cases"]
    case_prices = tuple((price_cases[case]["total_usd"] - price_cases[case]["direct_local_labour_usd"]) / 36
                        for case in ("low", "base", "high"))
    crew_hours = shared_cnc["direct_local_crew_hours"] / 36
    for kind, mass in masses.items():
        weight = mass/cut_kg
        items = tuple(MESHES[key] for key, part in PIECES.items() if part["part"] == kind)
        is_bogie = any(part["assembly"].startswith("bogie") and part["part"] == kind
                       for part in PIECES.values())
        yield Part(
            key=f"steel-{kind}", assembly="Bogie frame stock" if is_bogie else "Carbody frame stock",
            name=f"{kind.replace('_', ' ').capitalize()} stock group ({len(items)} pieces per car)",
            meshes=items, quantity=len(CENTRES), material="Steel grade and certificate from quotation",
            mass_kg=(mass, mass, mass),
            price_usd=tuple(round(weight*usd + mass*rate, 2)
                            for usd, rate in zip(case_prices, (.95, 1.45, 2.30), strict=True)),
            process=("Cut and label, fixture, join, gauge and inspect. Protect surfaces and record release."
                     if not is_bogie else
                     "Cut and label, fixture, join, inspect and machine seats. Record coplanarity after release."),
            crew="Steel fabrication team", hours=round(weight*crew_hours, 3),
            account="V04/V05; fleet estimate replacement comparison only",
            basis=("Sealed revised-cuts.csv gross mass, exact stock mesh. Mass allocation excludes unknown net "
                   "changes after welding, machining, inserts and coating. Shared CNC 36-car scenario allocated "
                   "in proportion to gross kg; direct local labour appears in work hours and "
                   "is removed from price. Additional raw stock rate screen $0.95/1.45/2.30 per kg, "
                   "illustrative and no supplier offer. Price includes allocated tooling and setup."),
            kind="stock",
        )


def inventory():
    from ledger import Part
    from train_fitout import positioned_mesh

    anchors = {
        "axles": ("steel-bogie_side",),
        "suspension": ("wheelset", "steel-primary_underside", "steel-secondary_top", "steel-secondary_body"),
        "drives": ("wheelset", "axlebox"),
        "deck": ("steel-floor_tie",),
        "interior": ("floor-panels",),
        "underroof": ("steel-roof_tie",),
        "shell": ("steel-cantrail", "steel-jamb"),
        "glazing": ("side-skins",),
        "doors": ("steel-jamb_liner",),
        "roof": ("overhead-run",),
        "roof-services": ("roof-skin",),
        "cab-interior": ("floor-panels",),
        "cab-nose": ("end-cab-interior", "steel-end_post"),
        "cab-rescue": ("steel-end_tie",),
        "vestibule": ("steel-end_post", "floor-panels"),
        "connector-draft": ("end-vestibule", "steel-end_tie"),
        "connector-utilities": ("connector-draft", "services"),
        "connector-bridge": ("connector-draft", "end-vestibule"),
        "connector-bellows": ("connector-bridge",),
        "collector": ("services",),
        "services": ("steel-floor_tie",),
    }
    scope_basis = {
        "axles": "Bogie axle x datums from installed-ga.json. Wheel profile, diameter and bracket envelopes are studies.",
        "suspension": "Seat coordinates and 156 mm nominal secondary gap from installed-ga.json.",
        "drives": "Four driven axles and two brake controller places per car per installed-fitout-bom.csv. Metrology and supplier brake friction counts are open.",
        "doors": "Eight openings and sixteen leaves per car per installed-fitout-bom.csv. Leaf thickness and rough apertures from installed-ga.json. Door machinery and anchors are indicative.",
        "roof-services": "Two study points per car per installed-ga.json. Package footprint, loads, cooling and drain trial are open.",
        "services": "Centre service study point from installed-ga.json. Cabinet split, hose lengths, qualified capacity, wiring routing and equipment mass await suppliers.",
        "collector": "24 contact sets for six opening formations per installed-fitout-bom.csv. Four is the implied one-set quantity, with only two example envelopes displayed and car assignment open.",
        "cab-nose": "Outboard cab concept repeated mirrored at the other terminal. Visibility, structure, protection and supplier attachments are open.",
        "cab-interior": "Both terminal driver cabs and rear service bulkheads are concepts. Qualified controls and escape envelope open.",
        "cab-rescue": "Two outboard locations proposed. Coupler design, load limits, stowage and recovery arrangements remain open.",
        "vestibule": "Ten inner end locations are implied by the proposed two-cab, six-car arrangement. End portal and personnel protection open.",
        "connector-draft": "Five inter-car joints implied by the published six centre positions. The nominal 500 mm separation follows 17 m body length and 17.5 m spacing. Approve drawgear, coupler loads and curvature before fit.",
        "connector-bridge": "Five proposed inter-car bridges. Bridge sweep, emergency retention and floor gap in articulated poses are open.",
        "connector-bellows": "Five proposed bellows sets. Fire, weather sealing and articulated body sweep are open.",
        "connector-utilities": "Five proposed train utility connections. Jumper bend, strain relief, isolation, pinout and endurance are open.",
        "interior": "Proposed furniture quantities depict a study layout only. Passenger capacity, seat anchors, accessible route and escape widths are unrated.",
    }
    parts = list(stock_ledger())
    for component in FITOUT:
        parts.append(Part(
            key=component.key, assembly=component.stage.replace("-", " ").capitalize(),
            name=component.name, meshes=tuple(positioned_mesh(item) for item in component.unit),
            quantity=component.per_set, material=component.material, mass_kg=component.mass,
            price_usd=component.price, process=component.process, crew=component.crew, hours=component.hours,
            account=f"{component.quote}; fleet estimate replacement comparison only",
            basis=(scope_basis.get(component.stage, "Proposed installation on nominal installed GA datums.") +
                   " Concept allowance for complete group with its standard mount hardware. "
                   "Ranges and crew hours are engineering scenario inputs pending drawings, weighings and quotes. "
                   "The source fleet allowance is a separate whole-train comparison, with no additive allocation."),
            predecessors=anchors[component.stage],
        ))
    return parts
