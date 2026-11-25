"""Storyboard for the Baghdad 20 m shared-pier, rail-fed construction concept."""

import json
from functools import lru_cache
from pathlib import Path
import tomllib

from scene import Camera, Frame, Item, box, combine, load_obj

TITLE = "Build the viaduct from both ends"
DURATION = 156
POSTER_TIME = 116
CHAPTERS = (
    (0, "Two yards and two fronts"),
    (8, "Excavate and cast the spread footing"),
    (23, "Cast the column and crosshead"),
    (39, "Place the bearing assemblies"),
    (48, "Make and release the precast girder"),
    (69, "Make the starter bays and load the flatbed"),
    (84, "Assemble the transporter and gantry"),
    (102, "Feed the two girders and land the pair"),
    (127, "Extend the route and fit the service interfaces"),
    (142, "Close the line and return the plant"),
)

CIVIL = "cities/Baghdad/engineering/mechanical/civil"
CAD = f"{CIVIL}/rail-fed/rail-fed-launch.obj"
YARD = f"{CIVIL}/rail_fed_assumptions.toml"
COMPARISON = f"{CIVIL}/rail-fed/comparison.json"
WORKPLAN = f"{CIVIL}/rail-fed/crew-workplan.csv"
FAMILIES = f"{CIVIL}/family_comparison.py"
SOURCES = (CAD, YARD, COMPARISON, WORKPLAN, FAMILIES, f"{CIVIL}/rail-fed/CONCEPT-GEOMETRY.md",
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


def overview(t):
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
        items.append(Item(CROSSHEAD_CAGE, CAGE, offset=(0, 0, 1.2 * (1 - ease(t, 23, 24)))))
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
    for y in (-1.95, 1.93):
        for z in (.92, 1.31, 1.68, 1.98, 2.15):
            rods.append(shape(f"web_bar_{y}_{z}", (-9.85, y, z), (9.85, y + .027, z + .03)))
        for i in range(-9, 10):
            x = i * 1.035
            rods.append(shape(f"web_link_{y}_{i}", (x, y, .79), (x + .035, y + .031, 2.17)))
    return combine("schematic_girder_cage", rods)


GIRDER_CAGE = stock_on_ground()
STRANDS = combine("straight_strand_layout_proxy", [
    shape(f"strand_{y}", (-10.45, y, .70), (10.45, y + .033, .733))
    for y in (-1.54, -1.10, -.66, -.22, .22, .66, 1.10, 1.54)
])
STRESSING_HEAD = shape("stressing_head_proxy", (-10.73, -1.7, .59), (-10.49, 1.7, .84))



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
        items.append(Item(STRANDS, "#eec67e"))
        items.extend(Item(STRESSING_HEAD, STEEL, yaw=turn) for turn in (0, 180))
        if t >= 28.1:
            items.append(Item(GIRDER_CAGE, CAGE, offset=(0, 0, 1.5 * (1 - ease(t, 28.1, 29.5)))))
    if 29.8 <= t < 36.5:
        items.append(solid("core_former", (-10.02, -1.79, .86), (10.02, 1.79, 2.35), MOULD,
                           offset=(0, 0, 3.5 * ease(t, 34.5, 36.5))))
    if 31 <= t:
        items.append(Item(GIRDER, BEAM, offset=(23, 2.25, -6.45), pivot=(0, 0, 7.07),
                          scale=(1, 1, max(.001, ease(t, 31, 34.25)))))
    if 31 <= t < 34.2:
        p = ease(t, 31, 34.2)
        items += pour_hose(slide(-7, 7, p), 1.87, .65 + 1.55 * p)
    if t < 29.8:
        caption = "Set out the strand zone, end fixtures and reinforcement. Bar and strand counts are illustrative."
    elif t < 34.5:
        caption = "Fit the former and place concrete. The actual stressing sequence depends on the designed tendon system."
    else:
        caption = "Check release strength and stressing records, strip the mould, inspect and stage stock on the yard supports."
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
    items = starter_deck() + launcher()
    items += bearing_items(0) + bearing_items(20)
    far = t < 69.15
    if far:
        local = t - 57
    else:
        local = t - 69.15
        items.append(Item(GIRDER, BEAM, offset=(33, 4.5, -.92)))
    # Each girder travels into the pick position on a separate flatbed trip.
    arriving = slide(-4, 9, ease(local, -2.2, 1.2))
    flatbed_x = arriving - 13 * ease(local, 4.8, 8.1)
    items += transporter(flatbed_x)
    if local < 1.2:
        x, y, z = arriving, -2.25, 7.85
        subtitle = "Bring one girder per trip. Check transport restraints and the released support and feed track."
    else:
        x = slide(9, 33, ease(local, 3.4, 6.5))
        y = slide(-2.25, 2.25 if far else -2.25, ease(local, 6.5, 8.4))
        z = slide(7.85, 9.82, ease(local, 1.2, 3.4)) - 3.67 * ease(local, 8.4, 11.2)
        if local < 11.5:
            items += transfer_gear(x - 23, y, z + 1.55)
        if local < 8.4:
            subtitle = "Lift clear of the flatbed, move over the open bay and align the girder with the bearing seats."
        else:
            subtitle = "Check bearing contact, alignment and temporary restraint before releasing the lifting gear."
    items.append(Item(GIRDER, BEAM if far else CONCRETE, offset=(x, y + 2.25, z - 7.07)))
    camera = Camera((slide(-8, 5, ease(local, 1, 6.5)), .13, 6.9),
                    slide(104, 118, ease(local, 1, 6.5)), 23, slide(64, 55, ease(local, 0, 9)))
    girder = "far" if far else "near"
    return Frame(camera, items, f"Feed and seat the {girder} girder", subtitle,
                 ("ONE GIRDER PER DELIVERY", "SCHEMATIC RIGGING"))


def frame(seconds):
    """Return the geometry and caption for one time in the construction sequence."""
    if seconds < 8:
        return overview(seconds * 7 / 8)
    if seconds < 23:
        if seconds < 13:
            return excavation(seconds - 8)
        return foundation(7 + (seconds - 13))
    if seconds < 39:
        return piers(17 + (seconds - 23) * 10 / 16)
    if seconds < 48:
        return bearing_detail(seconds - 39)
    if seconds < 69:
        return yard(27 + (seconds - 48) * 13 / 21)
    if seconds < 84:
        if seconds < 75:
            return starter_works(seconds - 69)
        return transfer(40 + seconds - 75)
    if seconds < 102:
        if seconds < 90:
            return equipment_detail(seconds - 84, "flatbed")
        if seconds < 97:
            return equipment_detail(seconds - 90, "gantry")
        return feed(49 + (seconds - 97) * 8 / 5)
    if seconds < 127:
        return placement(57 + (seconds - 102) * 24.3 / 25)
    if seconds < 142:
        return service_interfaces(seconds - 127)
    return close_line(seconds - 142)


BEARING_LAYERS = (
    (shape("bearing_plinth", (-.44, -.37, 6), (.44, .37, 6.06)), CONCRETE),
    (shape("bearing_lower_plate", (-.38, -.31, 6.06), (.38, .31, 6.08)), STEEL),
    (shape("bearing_element_envelope", (-.32, -.26, 6.08), (.32, .26, 6.125)), RAIL),
    (shape("bearing_upper_plate", (-.38, -.31, 6.125), (.38, .31, 6.15)), STEEL),
)
BEARING = combine("bearing_stack_proxy", [mesh for mesh, _ in BEARING_LAYERS])
CROSSHEAD_CAGE = combine("crosshead_cage_proxy", [
    shape(f"crosshead_long_bar_{x}_{z}", (x, -4.8, z), (x + .047, 4.8, z + .047))
    for x in (-1.13, -.72, -.3, .3, .72, 1.13) for z in (5.38, 5.8)
] + [
    shape(f"crosshead_link_{i}", (-1.15, i * .52, 5.42), (1.15, i * .52 + .035, 5.455))
    for i in range(-9, 10)
])


def bearing_items(x):
    return [Item(mesh, color, offset=(x + dx, y, 0))
            for dx in (-.56, .56) for y in (-3.72, -.78, .78, 3.72)
            for mesh, color in BEARING_LAYERS]


def bearing_detail(t):
    # Concentrate on one girder end. The plinth and plates are envelopes.
    items = support(0)
    for i, (mesh, color) in enumerate(BEARING_LAYERS):
        clearance = 1 - ease(t, .7 + i * 1.28, 2.0 + i * 1.28)
        items += [Item(mesh, color, offset=(.56, y, (i + 1) * .29 * clearance))
                  for y in (.78, 3.72)]
    items.append(Item(GIRDER, BEAM, offset=(23, 4.5, -.92 + 2.3 * (1 - ease(t, 5.5, 8.7)))))
    return Frame(Camera((1.9, 2.1, 6.46), 134, 30, 10.9), items,
                 "Assemble and inspect the bearing stack",
                 "Check plinth levels, bearing orientation and reaction transfer. The bearing type, restraints and setting details need a design return.",
                 ("INDICATIVE PLINTH AND PLATES", "GIRDER END DETAIL"))


EXCAVATOR_BASE = shape("excavator_track_base_proxy", (-1.45, -1.19, 0), (1.45, 1.19, .55))
EXCAVATOR_BODY = shape("excavator_body_proxy", (-1.15, -.85, .55), (.84, .85, 1.52))
CRANE_BASE = shape("road_crane_carrier_proxy", (-3, -1.25, 0), (3, 1.25, 1.28))
CRANE_CAB = shape("road_crane_cab_proxy", (-2.7, -.95, 1.28), (-.95, .95, 2.6))


def brace(name, start, end, width, depth):
    """Rectangular section swept along a sloping link in the X–Z plane."""
    from math import hypot
    from scene import Mesh
    import numpy as np

    x, y, z = start
    ex, ey, ez = end
    span = hypot(ex - x, ez - z)
    dx, dz = (ez - z) * depth / (2 * span), (x - ex) * depth / (2 * span)
    vertices = np.array([(px + sx * dx, py + sy * width / 2, pz + sx * dz)
                         for px, py, pz in (start, end)
                         for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    return Mesh(name, vertices, shape("link_face_indices", (0, 0, 0), (1, 1, 1)).faces)


def excavation(t):
    items = excavated_area()
    x = slide(6.6, 5.4, ease(t, 0, 4))
    bucket_z = slide(-.42, 1.2, ease(t, .95, 4.55))
    items.extend((Item(EXCAVATOR_BASE, STEEL, offset=(x, 0, 0)),
                  Item(EXCAVATOR_BODY, PLANT, offset=(x, 0, 0)),
                  Item(brace("excavator_boom", (x - .64, 0, 1.08), (x - 2.6, 0, 2.8), .34, .32), PLANT),
                  Item(brace("excavator_dipper", (x - 2.6, 0, 2.8), (2.2, 0, bucket_z + .3), .22, .24), PLANT),
                  solid("excavator_bucket_proxy", (1.71, -.52, bucket_z), (2.32, .52, bucket_z + .47), STEEL)))
    return Frame(Camera((2.5, 0, .25), 56, 30, 15.2), items,
                 "Expose and verify the spread-footing formation",
                 "Survey and clear utilities, excavate and inspect the founding stratum. A piled alternative needs site ground data and a separate design.",
                 ("SHALLOW OPTION", "ILLUSTRATIVE EXCAVATOR"))


def crane_position(x, y, end_x, end_z, pick_y=None):
    pick_y = y if pick_y is None else pick_y
    items = [Item(CRANE_BASE, STEEL, offset=(x, y, 0)), Item(CRANE_CAB, PLANT, offset=(x, y, 0)),
             Item(brace("crane_boom_proxy", (x - .8, 0, 2.2), (end_x, 0, end_z), .52, .56),
                  PLANT, offset=(0, pick_y, 0))]
    for side in (-1, 1):
        for offset in (-2.0, 2.0):
            items.append(solid("outrigger_proxy", (-.25, min(0, side * 2.4), .13),
                               (.25, max(0, side * 2.4), .34), STEEL, offset=(x + offset, y, 0)))
            items.append(solid("outrigger_mat_proxy", (-.61, -.47, .02), (.61, .47, .13), MOULD,
                               offset=(x + offset, y + side * 2.4, 0)))
    return items


def road_rigging(x, y, top, hook):
    items = transfer_gear(x, y, top, z=hook)
    spreader_z = top + .36
    return [*items[2:], solid("crane_drop_line", (-.027, -.027, spreader_z), (.027, .027, hook),
                             RAIL, offset=(x, y, 0), outline=False)]


def starter_works(t):
    items = [piece for x in (-40, -20, 0) for piece in support(x)]
    items += [solid("starter_hardstand_proxy", (-43, -14, -.25), (5, 13, 0),
                    YARD_PAD, False, layer=-2)]
    items += track_pair(-40)
    items.append(Item(DECK[0], CONCRETE, offset=(20, 0, 0)))
    items += crane_position(4, 2.25, -10, 13.8)
    z = 6.0 + 3.7 * (1 - ease(t, .8, 5.2))
    items.append(Item(GIRDER, BEAM, offset=(13, 4.5, z - 7.07)))
    if t < 5.4:
        items += road_rigging(-10, 2.25, z + 1.55, 13.8)
    return Frame(Camera((-12, 0, 5.8), 71, 25, 49), items, "Place the starter bays with ground equipment",
                 "Book road delivery, working platform and ground lift. Release both starter bays before commissioning the deck-fed equipment.",
                 ("TWO STARTER BAYS PER END", "ILLUSTRATIVE ROAD CRANE"))


FLATBED_DECK = MESHES["transport_flatbed_envelope"]
BOGIES = tuple(mesh for name, mesh in MESHES.items() if name.startswith("transport_rail_bogie_envelope_"))
GANTRY_GIRDERS = tuple(mesh for name, mesh in MESHES.items() if name.startswith("gantry_longitudinal_envelope_"))
GANTRY_LEGS = tuple(mesh for name, mesh in MESHES.items() if name.startswith("gantry_support_envelope_"))
GANTRY_BRACES = tuple(mesh for name, mesh in MESHES.items() if name.startswith("gantry_transverse_envelope_"))


@lru_cache
def bogie_axles(center):
    # Four illustrative axles per bogie, as in the tare and axle study.
    return combine("flatbed_four_axles_proxy", [
        shape(f"axle_housing_{i}", (center + dx - .09, -3.09, 6.47),
              (center + dx + .09, -1.41, 6.59))
        for i, dx in enumerate((-.42, -.14, .14, .42))
    ])


def equipment_detail(t, equipment):
    if equipment == "flatbed":
        items = [Item(mesh, STEEL) for mesh in BOGIES]
        items.extend(Item(bogie_axles(x), "#71838c") for x in (-32, -14))
        lift = 2.9 * (1 - ease(t, .55, 4.25))
        items.append(Item(FLATBED_DECK, "#4c8ca4", offset=(0, 0, lift)))
        for x in (-29, -17):
            items.append(solid("stock_dunnage", (-.38, -3.45, 7.07), (.38, -1.05, 7.85), MOULD,
                               offset=(x, 0, lift + .9 * (1 - ease(t, 2.5, 5)))))
            items.append(solid("stock_restraint_envelope", (-.2, -3.51, 7.14), (.2, -3.32, 7.74),
                               RAIL, offset=(x, 0, lift + .9 * (1 - ease(t, 2.5, 5)))))
        return Frame(Camera((-23, -2.25, 7.65), 62, 23, 28.2), items,
                     "Assemble the flatbed transport package",
                     "Locate the two running gear envelopes, deck, stock dunnage and restraint zones. Actual wheel loads and restraints depend on the selected equipment.",
                     ("25 T TARE ASSUMPTION", "8-AXLE TRIAL"))
    items = starter_deck()
    items += [Item(mesh, PLANT) for mesh in GANTRY_LEGS]
    items += [Item(mesh, PLANT, offset=(0, 2.2 * sign * (1 - ease(t, 0, 3.4)), 0))
              for mesh, sign in zip(GANTRY_GIRDERS, (-1, 1), strict=True)]
    items += [Item(mesh, "#3aa4a1", offset=(0, 0, 1.8 * (1 - ease(t, 2.2, 5))))
              for mesh in GANTRY_BRACES]
    items += transfer_gear(-3, -2.25, 10.2)
    return Frame(Camera((5, 0, 9), 72, 19, 51), items,
                 "Set the launcher on temporary supports",
                 "The support frames carry the longitudinal beams and cross-members. The trolley, hoist and spreader serve the lift and transverse move.",
                 ("SUPPLIER GEOMETRY PENDING", "ASSEMBLY ENVELOPES"))


PROFILED_TENDON = combine("profiled_duct_zone_proxy", [
    brace(f"profiled_duct_{i}", (x, 0, z), (ex, 0, ez), .085, .068)
    for i, ((x, z), (ex, ez)) in enumerate(zip(
        ((.18, 7.1), (4, 6.82), (10, 6.46), (16, 6.82)),
        ((4, 6.82), (10, 6.46), (16, 6.82), (19.82, 7.1)), strict=True))
])
ANCHOR_ZONE = shape("profiled_tendon_anchor_zone_proxy", (.01, -.16, 6.97), (.18, .16, 7.23))

PERMANENT_TRACK = combine("permanent_rail_and_seat_proxy", [
    shape(f"permanent_rail_{side}", (0, side * .718 - .044, 6.42), (19.78, side * .718 + .044, 6.56))
    for side in (-1, 1)
] + [
    shape(f"permanent_rail_seat_{side}_{i}", (i * .72, side * .718 - .16, 6.39),
          (i * .72 + .22, side * .718 + .16, 6.42))
    for side in (-1, 1) for i in range(28)
])
WALKWAY = shape("walkway_interface_proxy", (0, .99, 6.65), (19.8, 1.71, 6.75))
TRAY = shape("cable_tray_interface_proxy", (0, -1.83, 6.57), (19.8, -1.58, 6.68))
DRAIN = shape("drainage_edge_interface_proxy", (0, -1.98, 6.40), (19.8, -1.85, 6.55))
PROPULSION = shape("reserved_propulsion_interface_proxy", (0, -.22, 6.43), (19.8, .22, 6.49))


def permanent_items(x, lift=0, interfaces=True):
    items = []
    for y in (-2.25, 2.25):
        items.append(Item(PERMANENT_TRACK, RAIL, offset=(x, y, lift), layer=1))
        if interfaces:
            items.extend(Item(mesh, color, offset=(x, y, lift), layer=1)
                         for mesh, color in ((WALKWAY, CONCRETE), (TRAY, PLANT),
                                            (DRAIN, STEEL), (PROPULSION, "#b486d1")))
    return items


def service_interfaces(t):
    items = [solid("under_deck_ground", (-23, -14, -.25), (36, 14, 0), GROUND, False, layer=-2)]
    items += [piece for x in (0, 20) for piece in support(x)]
    items += track_pair(-20) + [Item(mesh, CONCRETE, offset=(40, 0, .15)) for mesh in DECK]
    items += bearing_items(0) + bearing_items(20)
    if t < 4.1:
        for y in (-4.12, 4.12):
            items.append(Item(PROFILED_TENDON, "#e7b066", offset=(0, y, 0), layer=1))
            items.append(Item(ANCHOR_ZONE, STEEL, offset=(0, y, 0), layer=1))
        return Frame(Camera((8.8, 0, 6.75), 63, 24, 29), items,
                     "Complete the post-landing stressing stage",
                     "The tendon path is highlighted on the deck. Verify the designed stressing sequence, forces, anchorage and grout before releasing the bay.",
                     ("PROFILED DUCT ZONE", "SCHEMATIC OVERLAY"))
    if t < 8.8:
        t = (t - 4.1) * 6.7 / 4.7
        extension = slide(-3, 19.6, ease(t, .1, 4.6))
        for y in (-2.925, -1.575):
            items.append(solid("temporary_rail_extension", (0, y - .078, 6.49),
                               (max(.02, extension), y + .078, 6.61), RAIL,
                               offset=(0, 0, 1.6 * ease(t, 4.9, 6.7))))
        if t > 4.5:
            subtitle = "After the construction route is released from use, recover temporary gear and inspect the deck."
        else:
            subtitle = "Inspect the paired bay, fit temporary rail and joint transitions, then check the next feed path before loading it."
        return Frame(Camera((7.5, -.6, 6.97), 63, 27, 31.5), items,
                     "Release and extend the construction track", subtitle,
                     ("TEMPORARY RAIL AND JOINTS", "STAGE CHECK"))
    items += permanent_items(0, lift=1.7 * (1 - ease(t, 9.1, 12.9)), interfaces=t >= 9.9)
    return Frame(Camera((10, -.1, 6.8), 59, 48, 27.5), items,
                 "Fit the permanent rail and service interfaces",
                 "The running rail uses separate seats. Keep drainage, cable routing, access and reserved propulsion space clear at the handover interfaces.",
                 ("PERMANENT INTERFACES", "PROFILES AND FIXINGS PENDING"))


def close_line(t):
    items = riparian_ground()
    items += [piece for x in range(-80, 101, SPAN) for piece in support(x)]
    items += [piece for x in range(-80, 100, SPAN) if x != 0 for piece in track_pair(x)]
    if t < 11:
        items += crane_position(32, 0, 10, 16.6, 2.25 if t < 4.1 else -2.25)
    retreat = ease(t, 9, 13.5)
    items += [Item(GANTRY, PLANT, offset=(-30 - 25 * retreat, 0, 0)),
              Item(GANTRY, PLANT, yaw=180, offset=(54 + 24 * retreat, 0, 0))]
    for phase, lane in ((0, 4.5), (4.1, 0)):
        if t >= phase:
            z = slide(10.9, 6, ease(t, phase, phase + 3.9))
            items.append(Item(GIRDER, BEAM, offset=(33, lane, z - 7.07)))
            if t < phase + 3.9:
                items += road_rigging(10, lane - 2.25, z + 1.55, 16.6)
    return Frame(Camera((10, 0, 5), 104, 22, slide(77, 116, ease(t, 8, 14))), items,
                 "Close the meeting bay and clear the workfronts",
                 "A ground lift is priced for the meeting bay. Agree closure geometry, survey and release checks, then recover temporary plant and track.",
                 ("GROUND LIFT ALLOWANCE", "FINAL RELEASE AND DEMOBILISATION"))


def completed_still():
    shot = service_interfaces(14)
    return Frame(Camera((9, .1, 4.9), 57, 34, 39), shot.items, "Paired viaduct after temporary-track recovery",
                 shot.caption, shot.tags)


RENDERS = {
    "viaduct-completed": completed_still,
    "viaduct-placement": lambda: placement(64.7),
}


def inventory():
    """Parts for one paired bay and the separately grouped two-front plant."""
    from ledger import Part, solid_volume

    comparison = json.loads((ROOT / COMPARISON).read_text())
    geometry = comparison["geometry"]
    method = comparison["methods"]["rail_24h"]
    delivery = SETTINGS["delivery"]
    prices = SETTINGS["prices"]
    cases = ("low", "base", "high")
    bays = geometry["standard_bays"]
    supports = geometry["standard_shared_support_positions"]
    girders = geometry["standard_girders"]
    moulds = comparison["shared_quantities"]["moulds_per_yard"] * comparison["shared_quantities"]["yards"]
    catalogue_basis = f"Baghdad 20 m shared-pier concept OBJ envelope in {CAD}."
    sketch_basis = "Film geometry is illustrative. Detail design and supplier return are pending."
    work_basis = "Task hours are provisional person-hours for work packaging."
    records = []

    def register(key, assembly, name, meshes, quantity, material, process, crew, hours, account,
                 *, basis=sketch_basis, mass=None, price=None, kind="installed", after=()):
        records.append(Part(key=key, assembly=assembly, name=name, meshes=meshes, quantity=quantity,
                            material=material, mass_kg=mass, price_usd=price, process=process,
                            crew=crew, hours=hours, account=account, basis=f"{basis} {work_basis}",
                            kind=kind, predecessors=after))

    def common(account, divisor):
        return tuple(method["cases"][case]["common_scope_breakdown_usd"][account] / divisor
                     for case in cases)

    def reinforced_envelope(mesh, densities=(2350, 2450, 2550)):
        volume = float(solid_volume(mesh))
        return tuple(round(volume * density, 2) for density in densities)

    def dry_rate(plant):
        days = method["launcher_dry_hire_days_across_fronts"] / 2
        return tuple(a + b * days for a, b in zip(prices[f"{plant}_mobilisation_usd_each"],
                                                  prices[f"{plant}_dry_use_usd_day_each"], strict=True))

    def known(kg):
        return (kg,) * 3

    def crew_work(rows, names):
        return sum(row["paid_hours"] for row in rows if row["role"] in names)

    concrete_basis = (
        f"{catalogue_basis} The closed-envelope volume is multiplied by assumed composite densities "
        "of 2,350, 2,450 and 2,550 kg/m³. Reinforcement is included at this level. The cage "
        "meshes show arrangement and need bar schedules. The mass range describes this envelope."
    )

    register("excavation", "Ground works", "Excavation and founding stratum", (EXCAVATOR_BASE, EXCAVATOR_BODY),
             1, "Soil and illustrative plant", "Set out, survey utilities, excavate and inspect founding level.",
             "Alignment and installation", 32, "Support works allowance",
             price=common("supports", supports),
             basis=f"{sketch_basis} The excavator illustrates the task. Treat plant mass and ground scope as unconfirmed. "
                   f"{COMPARISON} allocates one support-works package per support. It includes site effort and is "
                   "exclusive of the separately pooled materials allowance. Reconcile overlapping workplan wages before adding costs.",
             kind="blended_package")
    register("footing_form", "Ground works", "Footing shutter faces",
             (shape("footing_shutter_west", (-2.13, -2.04, -.4), (-2.01, 2.04, .26)),
              shape("footing_shutter_south", (-2.02, -2.14, -.4), (2.02, -2.01, .26))),
             1, "Shutter panels", "Fix shutters, alignment and bracing and strip after cure.",
             "Alignment and installation", 12, "Support works allowance", kind="temporary", after=("excavation",))
    register("footing_cage", "Ground works", "Footing cage and column starters", (FOOTING_CAGE,), 1,
             "Reinforcing steel", "Tie cage, set cover and check column starters.",
             "Steel, cages and stressing", 24, "Pooled girder and support materials", after=("footing_form",))
    register("footing", "Ground works", "Shallow footing concrete", (FOUNDATION,), 1, "Reinforced concrete envelope",
             "Place and cure concrete and verify founding and cover records.",
             "Concrete placing and mould servicing", 24, "Pooled girder and support materials",
             basis=f"{concrete_basis} Actual shallow or piled design and quantity require local ground data.",
             mass=reinforced_envelope(FOUNDATION), after=("footing_cage",))
    register("column_cage", "Shared support", "Pier reinforcement cage", (PIER_CAGE,), 1, "Reinforcing steel",
             "Tie the column cage and locate it on the starters.", "Steel, cages and stressing", 20,
             "Pooled girder and support materials", after=("footing",))
    register("column_form", "Shared support", "Pier shutter faces",
             (shape("column_shutter_west", (-1.09, -1.01, .25), (-.95, 1.01, 5.32)),
              shape("column_shutter_south", (-.94, -1.14, .25), (.94, -1, 5.32))),
             1, "Shutter panels", "Align, brace and strip shutters after release.", "Alignment and installation", 24,
             "Support works allowance", kind="temporary", after=("column_cage",))
    register("column", "Shared support", "Pier concrete envelope", (PIER,), 1, "Reinforced concrete envelope",
             "Place concrete and release column for cap formwork.", "Concrete placing and mould servicing", 18,
             "Pooled girder and support materials", basis=concrete_basis, mass=reinforced_envelope(PIER),
             after=("column_form",))
    register("crosshead_form", "Shared support", "Crosshead formwork and falsework zone",
             (shape("crosshead_formwork", (-1.51, -5.10, 5.1), (1.51, 5.1, 5.26)),), 1, "Formwork",
             "Design falsework, then erect, survey and strike after cure.", "Alignment and installation", 24,
             "Support works allowance", kind="temporary", after=("column",))
    register("crosshead_cage", "Shared support", "Crosshead reinforcement cage", (CROSSHEAD_CAGE,), 1,
             "Reinforcing steel", "Tie cage and verify cover and bearing-seat anchorage zones.",
             "Steel, cages and stressing", 24, "Pooled girder and support materials", after=("crosshead_form",))
    register("crosshead", "Shared support", "Shared crosshead concrete envelope", (HEAD,), 1,
             "Reinforced concrete envelope", "Place, cure and survey the shared crosshead.",
             "Concrete placing and mould servicing", 24, "Pooled girder and support materials",
             basis=concrete_basis, mass=reinforced_envelope(HEAD), after=("crosshead_cage",))
    register("bearing_plinth", "Shared support", "Bearing plinths", (BEARING_LAYERS[0][0],), 8,
             "Grout/concrete", "Survey seats and form and finish bearing plinths.", "Alignment and installation",
             1.2, "Support works allowance",
             mass=reinforced_envelope(BEARING_LAYERS[0][0], (2100, 2250, 2400)),
             basis=f"{sketch_basis} Closed plinth envelope at assumed grout/concrete densities of 2,100, 2,250 and 2,400 kg/m³.",
             after=("crosshead",))
    register("bearing", "Shared support", "Bearing element and steel plates",
             tuple(mesh for mesh, _ in BEARING_LAYERS[1:]), 8, "Steel and unspecified bearing material",
             "Fit, level and inspect bearing stack and restraint.", "Alignment and installation", 1.3,
             "Bearing supply", price=(180, 450, 1400),
             basis=f"{sketch_basis} Eight bearing sets per paired bay, two per girder end. Purchase allowance from {FAMILIES}. Fitting labour is separate.",
             after=("bearing_plinth",))

    register("mould", "Precast tools", "Bed and external side forms",
             (shape("mould_bed", (-10.23, -2.17, .09), (10.23, 2.17, .62)),
              shape("side_mould_left", (-10.13, -2.25, .62), (10.13, -2.03, 2.17)),
              shape("side_mould_right", (-10.13, 2.03, .62), (10.13, 2.25, 2.17))),
             moulds, "Mould and bed construction pending", "Set, check and calibrate reusable moulds.",
             "Concrete placing and mould servicing", 32, "Two-yard forms",
             price=common("two_yard_forms", moulds), kind="plant",
             basis=f"{sketch_basis} The published full mould allowance includes former and end fixtures as one package.")
    register("former", "Precast tools", "Internal U-section former",
             (shape("core_former", (-10.02, -1.79, .86), (10.02, 1.79, 2.35)),), moulds, "Formwork",
             "Inspect release faces, secure the former and strip after cure.", "Concrete placing and mould servicing",
             8, "Included in two-yard forms", kind="plant", after=("mould",))
    register("stress_head", "Precast tools", "End fixture and stressing zones", (STRESSING_HEAD,), 2 * moulds,
             "Plant structural and hydraulic components", "Fit end fixture and verify stressing equipment and calibration.",
             "Steel, cages and stressing", 4, "Included in two-yard forms", kind="plant", after=("mould",))

    yard_rows = method["yard_shifts"]
    fabrication_usd = ", ".join(f"{amount:,.0f}" for amount in common("fabrication", girders))
    fabrication_basis = (
        f"Person-hours allocated from the published casting-yard roster in {WORKPLAN} per released girder."
    )
    fabrication_cost_basis = (
        f"The separate fabrication allowance in {COMPARISON} is USD {fabrication_usd} per girder (low/base/high), "
        "including those casting wages and yard handling. The allowance is reported here as a benchmark."
    )
    register("strand", "Girder", "Straight handling strand layout", (STRANDS,), 2, "Prestressing steel",
             "Set and check handling-stage strand and anchors.", "Steel, cages and stressing",
             crew_work(yard_rows, {"Steel, cages and stressing"}) / (3 * girders),
             "Pooled girder and support materials", basis=f"{sketch_basis} {fabrication_basis}", after=("stress_head",))
    register("girder_cage", "Girder", "Floor and web reinforcement cage", (GIRDER_CAGE,), 2, "Reinforcing steel",
             "Tie girder cage, locate ducts and check cover.", "Steel, cages and stressing",
             2 * crew_work(yard_rows, {"Steel, cages and stressing"}) / (3 * girders),
             "Pooled girder and support materials", basis=f"{sketch_basis} {fabrication_basis}", after=("strand",))
    register("girder", "Girder", "Precast 20 m U-girder handling unit",
             tuple(mesh for key, mesh in MESHES.items() if key.startswith("carried_girder_")), 2,
             "Reinforced and prestressed concrete", "Cast, cure, check release strength, strip and stage stock.",
             "Concrete placing and mould servicing",
             crew_work(yard_rows, {"Concrete placing and mould servicing", "Yard plant and released stock",
                                   "Yard lead and dispatch", "Batching and materials", "QA, strength and release records"}) / girders,
             "Pooled girder and support materials",
             mass=known(1000 * geometry["single_girder_bare_mass_t"]),
             price=common("materials", girders),
             basis=f"{catalogue_basis} Published bare handling mass, including the initial steel systems as a combined estimate. Material allowance includes both girders and their allocated share of supports across {bays} bays and {supports} priced support positions in {COMPARISON}. {fabrication_basis} {fabrication_cost_basis}",
             after=("girder_cage", "former"))

    yard_size = comparison["shared_quantities"]["yard"]
    yard_area = yard_size["area_m2"]
    yard_hardstand = shape("yard_hardstand_planning_footprint", (0, 0, -.25),
                           (yard_size["length_m"], yard_size["width_m"], 0))
    register("yard_hardstand", "Terminal works", "Terminal hardstand package", (yard_hardstand,), 2,
             "Surfacing and ground treatment pending", "Verify working platform and arrange hardstand installation.",
             "Alignment and installation", 24, "Terminal-yard temporary hardstand",
             price=common("terminal_yard_temporary_hardstand", 2), kind="blended_package",
             basis=f"{COMPARISON} prices {yard_area:,} m² per yard. The film shows representative work pads. "
                   "The ledger mesh shows the full preliminary footprint. Thickness and ground treatment need design. "
                   "The package includes site effort. The work allowance here covers coordination and verification.")

    terminal = (
        shape("terminal_transfer_leg_proxy", (-.29, -.32, 0), (.29, .32, 11.7)),
        shape("terminal_transfer_cap_proxy", (-.47, -13, 11.7), (.47, 7, 12.05)),
    )
    register("terminal_transfer", "Terminal handling", "Terminal transload frame", terminal, 2,
             "Supplier plant", "Install and commission the transfer station to the authorised lift design.",
             "Terminal transload coordinator", 80, "Terminal transfer and enabling allowance",
             price=tuple(prices["terminal_transfer_and_enabling_usd_each"]), kind="blended_package",
             basis=f"{sketch_basis} The package in {YARD} combines equipment and enabling. "
                   "Reconcile the overlapping installation effort before adding workplan wages.",
             after=("yard_hardstand",))
    dunnage = shape("stock_dunnage", (-.38, -3.45, 7.07), (.38, -1.05, 7.85))
    restraint = shape("stock_restraint_envelope", (-.2, -3.51, 7.14), (.2, -3.32, 7.74))
    register("flatbed", "Deck feed", "Flatbed platform and running gear",
             (FLATBED_DECK, *BOGIES, bogie_axles(-32), bogie_axles(-14)), 2, "Supplier plant",
             "Assemble, inspect, weigh and test brakes and recovery.",
             "Flatbed operator", 40, "Flatbed mobilisation and dry hire", price=dry_rate("flatbed"),
             mass=known(1000 * delivery["flatbed_tare_t"]), kind="plant",
             basis=f"{catalogue_basis} Published tare is a trial assumption, including outfitting. Actual axle and deck reactions require supplier data.")
    register("dunnage", "Deck feed", "Dunnage and restraint pair", (dunnage, restraint), 4,
             "Dunnage and restraint materials pending", "Fit and check restraint at each support zone.",
             "Rigging", 2, "Included in flatbed package", kind="plant", after=("flatbed",))
    register("temp_rail", "Deck feed", "Temporary feed rails, fasteners and joints",
             (RAILS, shape("transfer_track_sleeper", (-.12, -3.24, 6.24), (.12, -1.26, 6.33))),
             1, "Rail steel and support system", "Fit, inspect, extend and recover the temporary route.",
             "Temporary track and inspection", 2 * delivery["track_extension_and_ground_check_h_per_bay"],
             "Temporary track installed and recovered allowance", kind="temporary",
             basis=f"{sketch_basis} One representative bay allowance. The comparison blends tracked work and supply at USD {prices['temporary_track_installed_and_recovered_usd_km'][1]:,}/km. Final fit, support geometry and price split pending.",
             after=("bearing",))
    register("gantry_base", "Launcher", "Temporary launcher bearers and feet",
             (shape("rear_temporary_launcher_bearer", (-11.51, -5.81, 5.64), (-10.47, 5.81, 6)),
              shape("front_temporary_launcher_bearer", (18.48, -5.81, 5.78), (19.53, 5.81, 6))),
             2, "Temporary structural steel", "Confirm reaction and restraint design, set and survey support envelope.",
             "Alignment and installation", 24, "Launcher dry hire or staged works split pending",
             kind="plant", after=("bearing",))
    register("gantry", "Launcher", "Longitudinals, legs and cross-members",
             (*GANTRY_LEGS, *GANTRY_GIRDERS, *GANTRY_BRACES), 2, "Supplier structural steel",
             "Assemble, align and commission the gantry.", "Gantry operator", 96,
             "Launcher mobilisation and dry hire", price=dry_rate("launcher"), kind="plant",
             basis=f"{catalogue_basis} Hire rate covers the plant package. Actual reactions, mass and restraint geometry are open.",
             after=("gantry_base",))
    gear = tuple(item.mesh for item in transfer_gear(0, 0, 9.1))
    register("hoist", "Launcher", "Trolley, hoist and lifting assembly",
             gear[:2], 2, "Supplier mechanical and structural parts", "Fit, test and release hoist and trolley.",
             "Gantry operator", 18, "Included in launcher package", kind="plant", after=("gantry",))
    register("rigging", "Launcher", "Spreader, slings and attachment zones",
             gear[2:], 2, "Supplier lifting-rated parts", "Verify rigging, attach, lift and inspect before unhooking.",
             "Rigging", 2 * delivery["launcher_hours_per_standard_bay"], "Included in launcher package or rigging hire",
             kind="plant", after=("hoist",))
    register("road_plant", "Starter and closure", "Road crane and ground support",
             (CRANE_BASE, CRANE_CAB, brace("crane_boom_proxy", (-.8, 0, 2.2), (15, 0, 13), .52, .56)),
             1, "Supplier crane", "Verify lift chart and ground support and book starter and closure shifts.",
             "Crane operator", 8, "Operated road lift allowance", kind="plant",
             basis=f"{sketch_basis} Representative hired crane, reusable at other fronts. Operated hire includes crew. Actual capacity and supply split are open.")
    register("girder_seating", "Deck release", "Girder seating and release inspection",
             (BEARING,), 2, "Bearing interface", "Align on bearings and check seating, line and level.",
             "Alignment and installation", delivery["after_landing_deck_release_h"],
             "Included in deck erection roster", kind="task", after=("girder", "bearing", "rigging", "temp_rail"))
    register("final_stressing", "Deck release", "Profiled tendon and anchorage zone",
             (PROFILED_TENDON, ANCHOR_ZONE), 2, "Prestressing steel and duct system",
             "Complete the designed second-stage stress and verify the end zone, grout and deck release.",
             "Steel, cages and stressing", 12, "Stressed after landing allowance",
             basis=f"{sketch_basis} Comparison blends staged prestressing and labour. Strand count, profiles and stress/grout sequence remain open.",
             after=("girder_seating",))
    register("running_rail", "Permanent systems", "Running rails and seats for one deck",
             (PERMANENT_TRACK,), 2, "Rail steel and fastening system",
             "Set gauge, fit seats and inspect the permanent track geometry.",
             "Alignment and installation", 12, "Common elevated scope allowance",
             basis=f"{sketch_basis} Film shows representative rails and seats. Permanent track type, materials and scope need an agreed breakdown.",
             after=("final_stressing",))
    for key, name, mesh, material, action, hours in (
        ("walkway", "Maintenance access interface", WALKWAY, "Access structure pending",
         "Coordinate access panels, the walking surface and maintainable clearances.", 10),
        ("tray", "Cable tray route", TRAY, "Tray/containment material pending",
         "Coordinate cable routing and fit secure service brackets.", 8),
        ("drain", "Drainage route", DRAIN, "Drain/liner material pending",
         "Check falls and discharge and fit water control items.", 8),
        ("propulsion_zone", "Reserved propulsion interface", PROPULSION, "Space claim",
         "Check the reserved envelope, maintainability and other system clearances.", 2),
    ):
        register(key, "Permanent systems", name, (mesh,), 2, material, action,
                 "Alignment and installation", hours, "Common elevated scope allowance",
                 kind="interface" if key == "propulsion_zone" else "installed", after=("running_rail",))

    return records
