"""Exploded presentation of the Baghdad first-article steel car and bogie frames."""

from csv import DictReader
from hashlib import sha256
from io import StringIO
from json import loads
from pathlib import Path
from zipfile import ZipFile

from scene import Camera, Frame, Item, Mesh, box, combine, load_obj


ROOT = Path(__file__).resolve().parents[3]
PROTOTYPE = "cities/Baghdad/engineering/prototype"
PACKET = f"{PROTOTYPE}/airport-prototype.zip"
CAM = f"{PROTOTYPE}/cam/cam-manifest.json"
SAW_CUTS = f"{PROTOTYPE}/cam/saw-cuts.csv"
FACTORY = f"{PROTOTYPE}/factory-routes.json"
SOURCES = (PACKET, CAM, SAW_CUTS, FACTORY)

TITLE = "Fabricating the train frame"
DURATION = 80
POSTER_TIME = 26
CHAPTERS = (
    (0, "Cut and kit"),
    (10, "Underframe"),
    (22, "Side frames"),
    (39, "Roof and portals"),
    (48, "Bogie frames"),
    (58, "Body and bogies"),
    (72, "Completed frame"),
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


def assembly_shot(t, final=False):
    travel = 2.20 * (1 - smooth(t, 59.2, 66))
    lift = 1.58 * (1 - smooth(t, 65.6, 71.8))
    items = [ASSEMBLY_FLOOR]
    if not final:
        for direction, stand in PAIR_STANDS:
            items.extend(Item(item.mesh, item.color, offset=(direction * travel, 0, 0), outline=False)
                         for item in stand)
    items.extend(underframe(t, lift))
    items.extend(side_frames(t, lift))
    items.extend(roof_and_linings(t, lift))
    items.extend(bogie_set("A", travel=-travel))
    items.extend(bogie_set("B", travel=travel))
    if final:
        w = smooth(t, 72, DURATION)
        return Frame(
            Camera((0, 0, 1.55 + 0.07 * w), -68 + 25 * w, 18 - 0.6 * w, 21 - 0.4 * w),
            items, "The completed steel frame assembly",
            "The carbody and both bare bogie frames are shown at their exact published CAD coordinates.",
            ("120 body pieces", "24 bogie frame pieces", "Pilot stock geometry"),
        )
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
    return assembly_shot(seconds, final=seconds >= 72)
