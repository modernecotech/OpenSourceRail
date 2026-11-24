"""Storyboard for the Baghdad 20 m shared-pier, rail-fed construction concept."""

from functools import lru_cache
from pathlib import Path
import tomllib

from scene import Camera, Frame, Item, box, combine, load_obj

TITLE = "Build the viaduct from both ends"
DURATION = 79
POSTER_TIME = 63
CHAPTERS = (
    (0, "Two ends"),
    (7, "Foundations"),
    (17, "Piers"),
    (27, "Precast yard"),
    (40, "Starter bays"),
    (49, "Flatbed delivery"),
    (57, "Land the girders"),
    (73, "Close the line"),
)

CIVIL = "cities/Baghdad/engineering/mechanical/civil"
CAD = f"{CIVIL}/rail-fed/rail-fed-launch.obj"
YARD = f"{CIVIL}/rail_fed_assumptions.toml"
SOURCES = (CAD, YARD, f"{CIVIL}/rail-fed/CONCEPT-GEOMETRY.md",
           f"{CIVIL}/RAIL-FED-ERECTION.md")
ROOT = Path(__file__).resolve().parents[3]
MESHES = load_obj((ROOT / CAD).read_text())
SETTINGS = tomllib.loads((ROOT / YARD).read_text())
SPAN = 20
SOIL = "#b59070"
GROUND = "#d9d4c8"
CONCRETE = "#9babb7"
STEEL = "#526774"
POUR = "#7c96a5"
CAGE = "#b46737"
MOULD = "#b58654"
BEAM = "#d68b43"
RAIL = "#273e48"
PLANT = "#218281"
YARD_PAD = "#a9b8ae"


def group(name, prefix):
    return combine(name, [mesh for key, mesh in MESHES.items() if key.startswith(prefix)])


FOUNDATION = MESHES["foundation_envelope_2"]
PIER = MESHES["pier_envelope_2"]
HEAD = MESHES["shared_crosshead_2"]
GIRDER = group("carried_girder", "carried_girder_")
GANTRY = group("launching_gantry", "gantry_")
RAILS = group("temporary_rail_path", "temporary_service_rail_")
FLATBED = combine("rail_flatbed", [MESHES["transport_flatbed_envelope"],
    MESHES["transport_rail_bogie_envelope_0"], MESHES["transport_rail_bogie_envelope_1"]])
DECK = tuple(group(f"starter_track_{i}", f"released_track{i}_bay0_") for i in range(2))


@lru_cache(maxsize=256)
def shape(name, lower, upper):
    return box(name, lower, upper)


def solid(name, lower, upper, color, outline=True, offset=(0, 0, 0), layer=0):
    return Item(shape(name, lower, upper), color, offset=offset, outline=outline, layer=layer)


def ease(time, start, finish):
    p = max(0.0, min(1.0, (time - start) / (finish - start)))
    return p * p * (3 - 2 * p)


def slide(start, end, phase):
    return start + (end - start) * phase


def support(x):
    return [Item(FOUNDATION, CONCRETE, offset=(x, 0, 0)),
            Item(PIER, CONCRETE, offset=(x, 0, 0)),
            Item(HEAD, CONCRETE, offset=(x, 0, 0))]


def track_pair(x, color=CONCRETE):
    return [Item(mesh, color, offset=(x + 40, 0, 0)) for mesh in DECK]


def riparian_ground():
    return [
        solid("construction_corridor", (-107, -20, -1), (127, 20, 0), GROUND, False, layer=-3),
        solid("left_street", (-107, -20, -.04), (127, -14, .01), "#afb8b6", False, layer=-2),
        solid("right_street", (-107, 14, -.04), (127, 20, .01), "#afb8b6", False, layer=-2),
    ]


def overview(t, final=False):
    """A condensed alignment diagram in 3D, with standard bays at actual pitch."""
    items = riparian_ground()
    items += [piece for x in range(-80, 101, SPAN) for piece in support(x)]
    items += [piece for x in (-80, -60, -40, 40, 60, 80) for piece in track_pair(x)]
    # The visible areas are representative terminal work pads. They do not
    # depict the complete operational yard, which has its own scaled DXF.
    for x in (-103, 100):
        items.append(solid("terminal_work_pad", (0, -14, 0), (23, 14, .25),
                           YARD_PAD, False, (x, 0, 0), layer=-1))
        for y in (-13, -7, -1, 5, 11):
            items.append(Item(GIRDER, BEAM, offset=(x + 34.5, y + 2.25, -6.82)))

    if final:
        items += track_pair(-20)
        items += track_pair(20)
        for start, lane in ((73, 0), (75.8, 4.5)):
            if start <= t:
                z = slide(8.5, 6, ease(t, start, start + 2))
                items.append(Item(GIRDER, BEAM, offset=(33, lane, z - 7.07)))
                if t < start + 2:
                    items += transfer_gear(10, lane - 2.25, z + 1.55)
        demobilising = ease(t, 77.7, 79)
        items += [Item(GANTRY, PLANT, offset=(-20 * demobilising, 0, 0)),
                  Item(GANTRY, PLANT, yaw=180, offset=(60 + 20 * demobilising, 0, 0))]
        camera = Camera((10, 0, 4), slide(111, 103, ease(t, 73, 79)), 25, 221)
        return Frame(camera, items, "Connect the two fronts",
                     "One agreed closure sequence joins the advancing decks. Remove temporary plant after handback.",
                     ("CLOSURE BAY", "TWO INWARD FRONTS"))
    items += [Item(GANTRY, PLANT, offset=(-20, 0, 0)),
              Item(GANTRY, PLANT, yaw=180, offset=(40, 0, 0)),
              Item(FLATBED, STEEL, offset=(-22, 0, 0)),
              Item(FLATBED, STEEL, yaw=180, offset=(42, 0, 0))]
    camera = Camera((10, 0, 4), slide(105, 111, ease(t, 0, 7)), 25, 221)
    return Frame(camera, items, "Two yards, two inward workfronts",
                 "Cast at the ends. Build shared supports ahead of the fronts and deliver girders over released spans.",
                 ("BAGHDAD STUDY", "20 M STANDARD BAY", "CONCEPT SEQUENCE"))


def footing_cage():
    lower = -.29
    upper = .17
    rods = []
    for i in range(-4, 5):
        at = i * .39
        rods.extend((shape(f"footing_x_{i}", (-1.78, at, lower), (1.78, at + .045, lower + .045)),
                     shape(f"footing_y_{i}", (at, -1.78, upper), (at + .045, 1.78, upper + .045))))
    return combine("footing_cage_proxy", rods)


def pier_cage():
    rods = []
    for side in (-.71, .71):
        for pos in (-.68, -.22, .22, .68):
            rods.append(shape(f"vertical_{side}_{pos}", (side, pos, .1),
                              (side + .035, pos + .035, 5.44)))
    for i in range(10):
        z = .44 + i * .49
        rods.append(shape(f"tie_{i}_north", (-.73, .71, z), (.77, .75, z + .035)))
        rods.append(shape(f"tie_{i}_south", (-.73, -.72, z), (.77, -.68, z + .035)))
        rods.append(shape(f"tie_{i}_east", (.73, -.72, z), (.77, .75, z + .035)))
        rods.append(shape(f"tie_{i}_west", (-.73, -.72, z), (-.69, .75, z + .035)))
    return combine("pier_cage_proxy", rods)


FOOTING_CAGE = footing_cage()
PIER_CAGE = pier_cage()


def excavated_area():
    return [
        solid("soil_visible_base", (-29, -12, -.91), (30, 12, -.45), SOIL, False, layer=-3),
        solid("north_ground", (-32, 3, -.45), (34, 14, .02), GROUND, False, layer=-2),
        solid("south_ground", (-32, -14, -.45), (34, -3, .02), GROUND, False, layer=-2),
        solid("west_ground", (-32, -3, -.45), (-3, 3, .02), GROUND, False, layer=-2),
        solid("east_ground", (3, -3, -.45), (34, 3, .02), GROUND, False, layer=-2),
        solid("excavated_footing_bed", (-2.95, -2.95, -.46), (2.95, 2.95, -.41), SOIL, layer=-1),
    ]


def cast(mesh, color, t, start, finish, base):
    height = ease(t, start, finish)
    return Item(mesh, color, scale=(1, 1, max(.001, height)), pivot=(0, 0, base))


def pour_hose(x, y, z):
    return [
        solid("concrete_hose", (x - .085, y - .085, z + .3), (x + .085, y + .085, z + 1.8), STEEL),
        solid("wet_concrete_stream", (x - .055, y - .055, z), (x + .055, y + .055, z + .34), POUR),
    ]


def foundation(t):
    items = excavated_area()
    items += [Item(FOUNDATION, CONCRETE, offset=(x, 0, 0)) for x in (-20, 20)]
    if t < 14.75:
        items.append(Item(FOOTING_CAGE, CAGE, offset=(0, 0, 1.55 * (1 - ease(t, 8, 10.8)))))
        items.extend((
            solid("footing_shutter_west", (-2.13, -2.04, -.4), (-2.01, 2.04, .26), MOULD),
            solid("footing_shutter_south", (-2.02, -2.14, -.4), (2.02, -2.01, .26), MOULD),
        ))
    if t >= 11.2:
        items.append(cast(FOUNDATION, CONCRETE, t, 11.2, 14.5, -.4))
    if 11.2 <= t < 14.5:
        p = ease(t, 11.2, 14.5)
        items += pour_hose(slide(-1.05, 1.03, p), .4, -.36 + .64 * p)
    camera = Camera((0, 0, .5), slide(46, 64, ease(t, 7, 17)), 33, 14)
    return Frame(camera, items, "Excavate, reinforce and pour the footing",
                 "Lower the reinforcement cage into the prepared excavation, then cast and cure the footing.",
                 ("GROUND WORKS", "SCHEMATIC REBAR"))


def piers(t):
    items = excavated_area()
    items.append(Item(FOUNDATION, CONCRETE))
    items += support(-20) + support(20)
    if t < 23.5:
        items.append(Item(PIER_CAGE, CAGE))
        shutter = ease(t, 17.3, 19.4) * (1 - ease(t, 22.8, 23.9))
        if shutter > 0:
            items.extend((
                solid("pier_shutter_west", (-1.09, -1.01, .25), (-.95, 1.01, .25 + 5.07 * shutter), MOULD),
                solid("pier_shutter_south", (-.94, -1.14, .25), (.94, -1, .25 + 5.07 * shutter), MOULD),
            ))
    if 19.6 <= t:
        items.append(cast(PIER, CONCRETE, t, 19.6, 22.8, .25))
    if 19.6 <= t < 22.8:
        items += pour_hose(0, 0, .28 + 5 * ease(t, 19.6, 22.8))
    if 23 <= t < 25.7:
        items.append(solid("crosshead_formwork", (-1.51, -5.10, 5.1), (1.51, 5.1, 5.26), MOULD))
    if t >= 23.7:
        items.append(cast(HEAD, CONCRETE, t, 23.7, 25.8, 5.25))
    camera = Camera((0, 0, slide(2.5, 3.05, ease(t, 17, 27))), 55, 25, 18)
    return Frame(camera, items, "Pour the pier and shared crosshead",
                 "The column and crosshead form one support position for the two parallel U-girders.",
                 ("SHARED PIER", "SCHEMATIC FORMWORK"))


def stock_on_ground():
    rods = []
    for i in range(-9, 10):
        x = i * 1.035
        rods.append(shape(f"beam_floor_cage_{i}", (x, -1.86, .77), (x + .035, 1.86, .808)))
    for y in (-1.86, -1.41, -.88, -.32, .32, .88, 1.41, 1.86):
        rods.append(shape(f"strand_{y}", (-9.83, y, .73), (9.83, y + .023, .753)))
    for y in (-1.95, 1.93):
        for z in (.92, 1.31, 1.68, 1.98, 2.15):
            rods.append(shape(f"web_bar_{y}_{z}", (-9.85, y, z), (9.85, y + .027, z + .03)))
        for i in range(-9, 10):
            x = i * 1.035
            rods.append(shape(f"web_link_{y}_{i}", (x, y, .79), (x + .035, y + .031, 2.17)))
    return combine("schematic_girder_cage", rods)


GIRDER_CAGE = stock_on_ground()


def yard(t):
    # Show one cell at the planning model pitch. Ancillary equipment is schematic.
    pitch_x = SETTINGS["yard"]["mould_pitch_length_m"]
    pitch_y = SETTINGS["yard"]["mould_pitch_width_m"]
    items = [solid("precast_yard_surface", (-22, -16, -.45), (22, 16, .0), YARD_PAD, False, layer=-3)]
    for y in (-pitch_y, 0, pitch_y):
        items.append(solid("mould_cell_bay", (-pitch_x / 2, y - pitch_y / 2 + .12, 0),
                           (pitch_x / 2, y + pitch_y / 2 - .12, .08), GROUND, False, layer=-2))
        if y != 0:
            items.append(Item(GIRDER, CONCRETE, offset=(23, y + 2.25, -6.45)))
    items.append(solid("mould_bed", (-10.23, -2.17, .09), (10.23, 2.17, .62), STEEL))
    release = ease(t, 34.5, 37)
    for k in (-1, 1):
        at = k * (2.14 + .6 * release)
        items.append(solid("side_mould", (-10.13, at - .11, .62), (10.13, at + .11, 2.17), MOULD))
    if t < 34.2:
        items.append(Item(GIRDER_CAGE, CAGE, offset=(0, 0, 1.5 * (1 - ease(t, 27.6, 29.5)))))
    if 29.8 <= t < 36.5:
        items.append(solid("core_former", (-10.02, -1.79, .86), (10.02, 1.79, 2.35), MOULD,
                           offset=(0, 0, 3.5 * ease(t, 34.5, 36.5))))
    if 31 <= t:
        items.append(Item(GIRDER, BEAM, offset=(23, 2.25, -6.45), pivot=(0, 0, 7.07),
                          scale=(1, 1, max(.001, ease(t, 31, 34.25)))))
    if 31 <= t < 34.2:
        p = ease(t, 31, 34.2)
        items += pour_hose(slide(-7, 7, p), 1.87, .65 + 1.55 * p)
    caption = ("The end yards make standard girders in parallel with the foundations and piers."
               if t < 34.5 else
               "After curing and release checks, strip the mould and stage the girder for delivery.")
    camera = Camera((0, 0, 1.04), slide(58, 69, ease(t, 27, 40)), 36, 29)
    return Frame(camera, items, "Cast the U-girder at the precast yard", caption,
                 (f"{pitch_x:g} × {pitch_y:g} M MOULD CELL", "SCHEMATIC MOULD & CAGE"))


def starter_deck():
    items = [solid("starter_ground", (-53, -17, -.4), (33, 18, 0), GROUND, False, layer=-2)]
    items += [piece for x in (-40, -20, 0, 20) for piece in support(x)]
    items += track_pair(-40) + track_pair(-20)
    for i in range(20):
        x = -38.4 + i * 1.96
        items.append(solid("transfer_track_sleeper", (-.12, -3.24, 6.24), (.12, -1.26, 6.33),
                           STEEL, False, (x, 0, 0)))
    items.append(Item(RAILS, RAIL))
    return items


def transporter(x):
    # The stock support above the flatbed leaves a visible shipping gap over
    # the starter webs. This offset illustrates transport staging.
    items = [Item(FLATBED, STEEL, offset=(x, 0, 0))]
    for block in (-30, -16):
        items.append(solid("stock_dunnage", (-.38, -3.45, 7.07), (.38, -1.05, 7.85),
                           MOULD, offset=(block + x, 0, 0)))
        items.append(solid("bogie_envelope_wheel_hint", (-.34, -3.08, 6.40), (.34, -1.42, 6.52),
                           RAIL, offset=(block - 2 + x, 0, 0)))
    return items


def launcher():
    # Temporary support interfaces are drawn as envelopes, with final bearing
    # geometry and erection reactions left to the lifting design.
    return [
        Item(GANTRY, PLANT),
        solid("rear_temporary_launcher_bearer", (-11.51, -5.81, 5.64), (-10.47, 5.81, 6), STEEL),
        solid("front_temporary_launcher_bearer", (18.48, -5.81, 5.78), (19.53, 5.81, 6), STEEL),
    ]


def transfer_gear(girder_x, girder_y, girder_top, *, z=13.2):
    """Stylised trolley and two vertical straps showing the handled geometry."""
    items = [
        solid("transverse_trolley", (-.64, -5.57, z), (.64, 5.57, z + .27),
              "#e3b466", offset=(girder_x, 0, 0)),
        solid("hoist", (-.47, -.42, z - .32), (.47, .42, z + .06),
              RAIL, offset=(girder_x, girder_y, 0)),
        solid("lifting_spreader", (-6.6, -.23, girder_top + .15), (6.6, .23, girder_top + .34),
              STEEL, offset=(girder_x, girder_y, 0)),
    ]
    for dx in (-6.15, 6.15):
        items.append(solid("sling", (-.032, -.032, girder_top + .3), (.032, .032, z - .27),
                           RAIL, offset=(girder_x + dx, girder_y, 0), outline=False))
        items.append(solid("lifting_attachment_proxy", (-.19, -1.88, girder_top - .06),
                           (.19, 1.88, girder_top + .18), STEEL,
                           offset=(girder_x + dx, girder_y, 0)))
    return items


def transfer(t):
    items = starter_deck() + transporter(-4)
    for y in (-12.5, 6.5):
        for x in (-38.65, -16.6):
            items.append(solid("terminal_transfer_leg_proxy", (-.29, -.32, 0), (.29, .32, 11.7),
                               PLANT, offset=(x, y, 0)))
    for x in (-38.65, -16.6):
        items.append(solid("terminal_transfer_cap_proxy", (-.47, -13, 11.7), (.47, 7, 12.05),
                           PLANT, offset=(x, 0, 0)))
    y = slide(-10, -2.25, ease(t, 43.6, 46.5))
    z = slide(1.05, 8.52, ease(t, 40.8, 43.5)) - .67 * ease(t, 46.5, 48.4)
    items.append(Item(GIRDER, BEAM, offset=(-4, y + 2.25, z - 7.07)))
    if t < 48.4:
        # The terminal transfer equipment is represented by a simple envelope.
        for x in (-38.65, -16.6):
            items.append(solid("terminal_hoist", (-.12, -.36, z + 1.55), (.12, .36, 11.73),
                               STEEL, offset=(x, y, 0), outline=False))
    camera = Camera((-26, -3.5, 5.8), 88, 24, 53)
    return Frame(camera, items, "Establish the starter bays and load the flatbed",
                 "Ground plant establishes two starter bays. Transfer the released girder onto the temporary deck track.",
                 ("2 STARTER BAYS PER END", "SCHEMATIC TRANSFER"))


def feed(t):
    items = starter_deck()
    x = slide(-4, 9, ease(t, 49.2, 56.4))
    items += transporter(x)
    items.append(Item(GIRDER, BEAM, offset=(x, 0, 7.85 - 7.07)))
    items += launcher()
    camera = Camera((slide(-20, -9, ease(t, 49, 57)), -.3, 6.15), 96, 24, 63)
    return Frame(camera, items, "Carry a girder along the released spans",
                 "The flatbed runs on temporary rails behind the advancing gantry. The next bay is still open.",
                 ("TEMPORARY DECK TRACK", "FLATBED → GANTRY"))


def placement(t):
    items = starter_deck()
    items += transporter(slide(9, -4, ease(t, 60.5, 66)))
    items += launcher()
    if t < 69.15:
        x = slide(9, 33, ease(t, 60.1, 64.2))
        y = slide(-2.25, 2.25, ease(t, 64.2, 66.1))
        z = slide(7.85, 9.82, ease(t, 57.5, 60.1)) - 3.82 * ease(t, 66.1, 69.15)
        items.append(Item(GIRDER, BEAM, offset=(x, y + 2.25, z - 7.07)))
        items += transfer_gear(x - 23, y, z + 1.55)
        subtitle = ("Lift from the flatbed. Move forward over the open span, then traverse onto the far seats."
                    if t < 66.1 else "Lower the far girder onto the shared supports and check the seating.")
    else:
        items.append(Item(GIRDER, BEAM, offset=(33, 4.5, -1.07)))
        near = slide(8.94, 6, ease(t, 69.45, 72.2))
        items.append(Item(GIRDER, CONCRETE, offset=(33, 0, near - 7.07)))
        if t < 72.25:
            items += transfer_gear(10, -2.25, near + 1.55)
        subtitle = "Repeat from the same feed track for the near girder. Release the paired bay before extending the track."
    camera = Camera((slide(-8, 5, ease(t, 57, 68)), .13, 6.9),
                    slide(104, 118, ease(t, 61, 68)), 23, slide(64, 55, ease(t, 57, 69)))
    return Frame(camera, items, "Lift, traverse and seat the paired span", subtitle,
                 ("LAUNCHING GANTRY", "SHARED CROSSHEAD", "SCHEMATIC RIGGING"))


def frame(seconds):
    """Return the geometry and caption for one time in the construction sequence."""
    if seconds < 7:
        return overview(seconds)
    if seconds < 17:
        return foundation(seconds)
    if seconds < 27:
        return piers(seconds)
    if seconds < 40:
        return yard(seconds)
    if seconds < 49:
        return transfer(seconds)
    if seconds < 57:
        return feed(seconds)
    if seconds < 73:
        return placement(seconds)
    return overview(seconds, final=True)
