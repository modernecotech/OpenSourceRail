"""Presentation envelopes for the Baghdad Airport car fitout and end interfaces."""

from dataclasses import dataclass, replace
from functools import cached_property
from math import cos, pi, sin

import numpy as np

from scene import Item, Mesh, box, combine


CREAM = "#e9e6d9"
TEAL = "#235b65"
WINDOW = "#263d47"
REFLECTION = "#59707a"
SILVER = "#9ca8ad"
DARK = "#343e42"
RUBBER = "#313336"
FLOOR = "#a4a59c"
BLUE = "#337185"
YELLOW = "#e7b450"
COPPER = "#b77448"
LIGHT = "#fbf4d7"
RED = "#b92535"


def solid(name, lower, upper, color):
    return Item(box(name, lower, upper), color, outline=False)


def at(items, x=0, y=0, z=0, reverse=False):
    sign = -1 if reverse else 1
    return [replace(item, offset=(x + sign * item.offset[0], y + sign * item.offset[1], z + item.offset[2]),
                    yaw=(item.yaw + (180 if reverse else 0)) % 360)
            for item in items]


def section(name, profile, start, stop, axis, color):
    """Extrude a convex cross section along a coordinate axis."""
    def vertex(position, u, v):
        return ((position, u, v), (u, position, v), (u, v, position))[axis]

    n = len(profile)
    points = np.array([vertex(position, u, v) for position in (start, stop) for u, v in profile])
    faces = (tuple(range(n - 1, -1, -1)), tuple(range(n, 2*n)))
    faces += tuple((i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n))
    return Item(Mesh(name, points, faces), color, outline=False)


def round_stock(name, u, v, start, stop, radius, axis, color, sides=12):
    profile = [(u + radius * cos(2*pi*i/sides), v + radius * sin(2*pi*i/sides))
               for i in range(sides)]
    return section(name, profile, start, stop, axis, color)


def positioned_mesh(item):
    points = item.mesh.vertices
    if item.yaw == 180:
        points = points * (-1, -1, 1)
    return Mesh(item.mesh.name, points + item.offset, item.mesh.faces)


def bundle(items):
    """Reduce repeated Item work in the CPU renderer while keeping separate materials."""
    by_color = {}
    for item in items:
        by_color.setdefault(item.color, []).append(positioned_mesh(item))
    return tuple(Item(combine(meshes[0].name, meshes), color, outline=False)
                 for color, meshes in by_color.items())


@dataclass(frozen=True)
class Group:
    key: str
    name: str
    unit: tuple
    positions: tuple
    stage: str
    material: str
    mass: tuple
    price: tuple
    hours: float
    process: str
    crew: str
    quote: str
    per_set: int

    @cached_property
    def placed(self):
        return bundle([item for x, y, z, reverse in self.positions
                       for item in at(self.unit, x, y, z, reverse)])


def group(key, name, unit, stage, material, mass, price, hours, process, crew, quote,
          per_set, positions=((0, 0, 0, False),)):
    return Group(key, name, tuple(unit), tuple(positions), stage, material,
                 mass, price, hours, process, crew, quote, per_set)


def frame_assembly(geometry):
    axes = geometry["axle_planes_x_m"]
    wheels = [
        round_stock("axle", 0, .27, -.99, .99, .075, 1, DARK),
        *[round_stock("wheel rim", 0, .27, y - .065, y + .065, .27, 1, SILVER)
          for y in (-.73, .73)],
        *[round_stock("wheel hub", 0, .27, y - .086, y + .086, .14, 1, DARK)
          for y in (-.73, .73)],
    ]
    boxes = [
        solid("split axlebox", (-.16, -.115, .17), (.16, .115, .32), DARK),
        solid("bearing cover", (-.12, -.135, .2), (.12, .135, .29), SILVER),
    ]
    primary = [
        *[round_stock("primary spring turn", 0, 0, z, z + .008, .073, 2, SILVER)
          for z in (.323, .338, .353, .368)],
        round_stock("primary bushing", 0, 0, .32, .378, .049, 2, DARK),
    ]
    secondary = [
        *[round_stock("secondary bellows", 0, 0, z, z + .039, r, 2, RUBBER)
          for z, r in ((.602, .12), (.641, .14), (.68, .14), (.719, .12))],
        *[round_stock("secondary spring plates", 0, 0, z, z + .012, .148, 2, SILVER)
          for z in (.602, .746)],
    ]
    motor = [
        round_stock("traction motor", -.18, .34, -.36, .35, .15, 1, TEAL),
        solid("gear casing and torque arm", (-.27, .32, .17), (.12, .52, .46), DARK),
        solid("traction connector", (-.34, -.11, .32), (-.25, .09, .44), COPPER),
    ]
    brake = [
        round_stock("disc", 0, .27, -.55, -.51, .18, 1, SILVER),
        solid("caliper body", (-.095, -.59, .41), (.095, -.48, .5), RED),
        solid("actuator", (-.065, -.62, .47), (.065, -.51, .54), DARK),
    ]
    axles = [(x, 0, 0, False) for x in axes]
    primary_positions = [(x, y, 0, False) for x in axes for y in (-1.04, 1.04)]
    secondary_positions = [(x, y, 0, False) for x in (-6.4, 6.4) for y in (-.85, .85)]
    return [
        group("wheelset", "Wheelset, rims, hubs and axle", wheels, "axles", "Wheel/axle steel",
              (390, 510, 710), (3200, 4600, 7200), 3, "Gauge and roll the wheelset into fixture",
              "Mechanical fitter", "V06", 24, axles),
        group("axlebox", "Axlebox bearings, carrier and covers", boxes, "axles", "Steel and bearing assembly",
              (24, 40, 65), (720, 1300, 2200), 1.4, "Fit bearings and check endplay",
              "Mechanical fitter", "V06", 48, primary_positions),
        group("primary-spring", "Primary spring, seat bushes and travel stop", primary, "suspension", "Steel and elastomer",
              (13, 23, 39), (350, 620, 1100), 1.1, "Fit to surveyed pad and check spring height",
              "Mechanical fitter", "V07", 48, primary_positions),
        group("secondary-spring", "Secondary spring, plate and shims", secondary, "suspension", "Elastomer and plate steel",
              (25, 42, 75), (900, 1500, 2900), 1.4, "Shim stack and check nominal fit",
              "Mechanical fitter", "V07", 24, secondary_positions),
        group("axle-drive", "Traction motor, axle gearbox, reaction arm and connector", motor, "drives", "Motor and gear assembly",
              (180, 275, 410), (8500, 14500, 25000), 7, "Align motor and gearbox then check disturbance and cooling",
              "Drive fitter", "V08", 24, axles),
        group("axle-brake", "Friction disc, caliper and actuator envelope", brake, "drives", "Steel and friction assembly",
              (23, 42, 75), (1600, 3000, 5800), 3.5, "Fit restraint, measure clearances and prove release",
              "Brake fitter", "V09", 24, axles),
    ]


def shell_groups(geometry):
    doors = [d for d in geometry["door_apertures"] if d["wall_reference_y_m"] < 0]
    apertures = [d["centre_x_m"] for d in doors]
    edges = [-8.5]
    for door in doors:
        half = door["rough_width_m"] / 2
        edges.extend((door["centre_x_m"] - half, door["centre_x_m"] + half))
    edges.append(8.5)
    panels, glazing = [], []
    for x0, x1 in zip(edges[0::2], edges[1::2]):
        panels.extend((
            solid("lower side cladding", (x0, -1.35, .91), (x1, -1.33, 1.15), TEAL),
            solid("body side cladding", (x0, -1.35, 1.15), (x1, -1.33, 1.91), CREAM),
            solid("cantrail wrap", (x0, -1.35, 2.65), (x1, -1.33, 3.18), CREAM),
        ))
        if x1 - x0 > .55:
            for a, b in ((x0, x0 + .14), (x1 - .14, x1)):
                panels.append(solid("window pillar", (a, -1.35, 1.91), (b, -1.33, 2.65), CREAM))
            glazing.append(solid("saloon glazing", (x0+.14, -1.36, 1.91),
                                 (x1-.14, -1.343, 2.65), WINDOW))
            glazing.append(solid("glazing reflection", (x0+.17, -1.361, 2.58),
                                 (x1-.17, -1.360, 2.60), REFLECTION))
    for x in apertures:
        panels.append(solid("portal header cover", (x-.68, -1.35, 3.0), (x+.68, -1.33, 3.19), CREAM))
    mirrored = ((0, 0, 0, False), (0, 0, 0, True))
    roof_profile = [(-1.35,3.17), (1.35,3.17), (1.24,3.29), (.84,3.37), (-.84,3.37), (-1.24,3.29)]
    bays = np.linspace(-8.5, 8.5, 21)
    roof = [section("rolled roof fairing segment", roof_profile, x0, x1, 0, CREAM)
            for x0, x1 in zip(bays, bays[1:])]
    deck = [solid("modular floor panel", (x0,-1.19,.96), (x1,1.19,1), FLOOR)
            for x0, x1 in zip(bays, bays[1:])]
    deck.extend(solid("floor joining strip", (x-.012,-1.18,1), (x+.012,1.18,1.004), SILVER)
                for x in (-6.3,-2.1,2.1,6.3))
    leaf = [
        *[solid("door lower or header panel", (a,-1.21,z0), (b,-1.18,z1), TEAL)
          for a,b in ((-.70,-.008),(.008,.70)) for z0,z1 in ((1.005,1.99),(2.64,2.995))],
        *[solid("door glazing", (a,-1.213,1.99), (b,-1.18,2.64), WINDOW)
          for a,b in ((-.70,-.008),(.008,.70))],
        solid("door seals", (-.008,-1.218,1.005), (.008,-1.18,2.995), RUBBER),
        solid("door drive header", (-.67,-1.22,3.00), (.67,-1.15,3.065), DARK),
        solid("boarding threshold", (-.66,-1.36,.983), (.66,-1.15,1.001), SILVER),
        solid("door emergency release", (.54,-1.218,1.12), (.60,-1.15,1.34), YELLOW),
        *[solid("guide carriage", (a-.036,-1.22,2.974), (a+.036,-1.15,3.015), SILVER)
          for a in (-.54,-.24,.24,.54)],
    ]
    hatches = [(x, 0, 0, False) for x in apertures] + [(x, 0, 0, True) for x in apertures]
    return [
        group("floor-panels", "Finished floor, subfloor and joining strips", deck, "deck", "Composite floor, insulation and metal",
              (240, 370, 620), (5100, 8500, 15000), 34, "Cut, dry-fit, seal and fasten modular floor", "Body fitter", "V12", 6),
        group("side-skins", "Side cladding, thresholds surround and bonded liners", panels, "shell", "Sheet, lining and isolation finish",
              (180, 290, 460), (4000, 7200, 13500), 35, "Check portal and cold-fit panels, then seal and fasten",
              "Body fitter", "V12", 12, mirrored),
        group("side-glazing", "Saloon glazing panes and gasket kits", glazing, "glazing", "Safety glazing and gasket",
              (74, 118, 190), (1600, 3300, 6000), 9, "Set glazing blocks, bond and check glazing retention",
              "Glazing fitter", "V12", 12, mirrored),
        group("roof-skin", "Roof fairing, ceiling backing and insulation", roof, "roof", "Sheet and insulation",
              (185, 290, 470), (4200, 7200, 13500), 27, "Close service access after cable and drain checks",
              "Body fitter", "V12", 6),
        group("door-set", "Twin leaves, glazing, guides, retention, drive, edge seals and threshold", leaf,
              "doors", "Aluminium, safety glazing and door machinery", (110, 175, 260), (4200, 7300, 12700), 7,
              "Fit guide stops, retainers and harness. Gauge aperture and verify full sweep", "Door fitter", "V10", 48, hatches),
    ]


def saloon_groups(geometry):
    seat = [
        solid("seat post", (-.085,-.10,1.0), (.085,.11,1.41), DARK),
        solid("longitudinal seat cushion", (-.21,-.22,1.41), (.21,.22,1.50), BLUE),
        solid("inward-facing seat back", (-.21,-.235,1.48), (.21,-.156,1.93), BLUE),
        solid("seat end handhold", (.17,-.226,1.91), (.21,-.13,1.966), SILVER),
    ]
    # Five seats along each wall between each pair of outer doorways. The far
    # wall mirrors the near wall to keep seats clear of the equipment at the jambs.
    row_centres = (-5.00, -4.54, -4.08, -3.62, -3.16, 3.40, 3.86, 4.32, 4.78, 5.24)
    places = [(x, -.91, 0, False) for x in row_centres] + [
        (-x, .91, 0, True) for x in row_centres
    ]
    accessibility = [
        solid("wheelchair bay surround", (-.57,-1.14,1.001), (.57,-.67,1.015), BLUE),
        solid("wheelchair bay restraint rail", (-.55,-1.16,1.76), (.55,-1.10,1.81), YELLOW),
        solid("wheelchair stop and backrest", (.52,-1.14,1.22), (.59,-.63,1.68), DARK),
        solid("call panel", (.50,-1.10,1.69), (.56,-1.05,1.77), RED),
    ]
    trim = [
        solid("assistance intercom and door indicator", (-.20,-1.16,1.84), (.02,-1.10,2.04), DARK),
        solid("extinguisher shell", (.06,-1.15,1.27), (.21,-1.04,1.68), RED),
        solid("signage panel", (-.31,-1.16,2.43), (.18,-1.12,2.56), LIGHT),
    ]
    handrail = [
        round_stock("stanchion", 0, -.53, 1.01, 2.86, .021, 2, YELLOW),
        round_stock("stanchion", 0, .53, 1.01, 2.86, .021, 2, YELLOW),
        round_stock("overhead grab rail", -.53, 2.49, -1.17, 1.17, .021, 0, SILVER),
        round_stock("overhead grab rail", .53, 2.49, -1.17, 1.17, .021, 0, SILVER),
    ]
    underbody_brake = [
        solid("brake control and parking unit", (-.29,-.36,.08), (.29,.36,.31), DARK),
        solid("brake manifold", (-.17,.09,.10), (.17,.42,.26), COPPER),
        round_stock("local reservoir", -.17,.21,-.37,.37,.08,0,SILVER),
    ]
    overhead = [
        *[solid("ceiling light diffuser", (-2.65,y-.055,2.79), (2.65,y+.055,2.83), LIGHT)
          for y in (-.64,.64)],
        solid("insulated distribution duct", (-2.68,-.28,2.868), (2.68,.28,2.965), SILVER),
        solid("inspection panel and supply diffuser", (-2.6,-.24,2.81), (2.6,.24,2.87), CREAM),
    ]
    hvac = [
        solid("roof HVAC curb and gasket", (-.72,-.68,3.356), (.72,.68,3.404), DARK),
        section("roof HVAC module fairing", [(-.68,3.4),(.68,3.4),(.55,3.61),(-.55,3.61)], -.68,.68,0,SILVER),
        *[solid("roof HVAC grille", (x-.04,-.32,3.611), (x+.04,.32,3.623), DARK)
          for x in (-.48,-.24,0,.24,.48)],
    ]
    cabinet = [
        solid("underframe equipment cradle", (-1.66,-.61,.46), (1.66,.61,.51), DARK),
        solid("traction inverter cabinet", (-1.49,-.56,.51), (-.46,.50,.76), SILVER),
        solid("service battery enclosure", (-.37,-.56,.51), (.43,.50,.76), TEAL),
        solid("control cabinet isolator", (.52,-.56,.51), (1.53,.50,.76), SILVER),
        solid("coolant expansion chamber", (1.56,-.49,.51), (1.92,-.18,.69), BLUE),
        *[round_stock("power conduit or branch pipe", y, .54, -4.5, 4.5, .036, 0, color)
          for y, color in ((-.71,COPPER),(.70,BLUE),(.79,DARK))],
        *[solid("service clamp", (x-.022,.67,.49), (x+.022,.84,.59), SILVER)
          for x in (-3.8,-2,0,2,3.8)],
    ]
    collectors = [
        solid("collector mount", (-.36,-.14,.42), (.36,.14,.48), DARK),
        solid("insulating shoe arm", (-.17,-.37,.26), (.17,.02,.42), TEAL),
        solid("contact shoe", (-.15,-.40,.20), (.15,-.28,.26), COPPER),
    ]
    return [
        group("saloon-seat", "Seat with cushion, back and stand", seat, "interior", "Metal stand and fire-rated trim",
              (8,15,25), (170,310,590), .9, "Install to reserved floor anchors and fit trim",
              "Interior fitter", "V12", 6*len(places), places),
        group("wheelchair-bay", "Wheelchair bay panel, rail, backrest and call point", accessibility, "interior",
              "Metal and trim", (12,23,42), (340,710,1350), 2.6, "Fit rail and backrest then review boarding and circulation",
              "Interior fitter", "V12", 12, ((0,0,0,False),(0,0,0,True))),
        group("passenger-trim", "Emergency equipment, intercom, signage and indicator group", trim, "interior",
              "Composite, steel and electronics", (8,15,32), (440,870,1800), 2.1, "Secure emergency mounts and prove communications",
              "Interior fitter", "V12/V13", 48, [(d["centre_x_m"]+.87,0,0,d["wall_reference_y_m"]>0)
                                                if d["wall_reference_y_m"]<0 else
                                                (d["centre_x_m"]-.87,0,0,True)
                                                for d in geometry["door_apertures"]]),
        group("grab-rails", "Stanchions and overhead rails", handrail, "interior", "Stainless and coated steel",
              (8,13,21), (180,340,680), 2.5, "Gauge handrail reach, secure and inspect fixings",
              "Interior fitter", "V12", 18, [(x,0,0,False) for x in (-4.2,0,4.2)]),
        group("overhead-run", "Ceiling duct, supply diffuser and lighting harness", overhead, "underroof",
              "Duct, liner and LED equipment", (20,42,80), (870,1750,3400), 4.5,
              "Fit duct and light run and check access before roof closure", "HVAC and electrical fitter",
              "V11/V13", 18, [(x,0,0,False) for x in (-5.5,0,5.5)]),
        group("roof-hvac", "Roof HVAC casing, curb, grille and drain interface", hvac, "roof-services",
              "HVAC and aluminium assembly", (75,130,230), (3100,5800,10500), 5.5, "Lift, mount, bond and test drain and filter access",
              "HVAC fitter", "V11", 12, [(x,y,0,False) for x,y in geometry["roof_study_points_xy_m"]]),
        group("services", "Inverter, service battery and controls cabinets, harness and cooling runs", cabinet, "services",
              "Electrical assemblies, tubes and tray", (195,365,690), (12500,27400,57600), 26,
              "Bench-test, marry cabinets and check branch insulation, protection and leakage",
              "Electrical and HVAC fitter", "V08/V13", 6),
        group("brake-controller", "Brake controller, parking actuation and local manifold", underbody_brake, "drives",
              "Pneumatic and electrical assemblies", (41,76,145), (2100,4900,10200), 5.5,
              "Connect and prove service and parking interfaces", "Brake fitter", "V09", 12,
              [(x,0,0,False) for x in (-6.4,6.4)]),
        group("collector", "Collector, insulating arm and contact shoe", collectors, "collector", "Insulator, metal and contact insert",
              (18,32,58), (1600,3100,5900), 4, "Set role, height and contact force with guideway interface",
              "Electrical fitter", "V13", 4, [(x,-.97,0,reverse) for x,reverse in ((-3,False),(3,False))]),
    ]


def end_groups():
    cab = [
        section("formed cab skirt", [(-1.28,.92),(1.28,.92),(1.34,1.15),(-1.34,1.15)],
                -8.50,-8.35,0,TEAL),
        section("formed cab nose panel", [(-1.34,1.15),(1.34,1.15),(1.28,1.88),(-1.28,1.88)],
                -8.52,-8.35,0,CREAM),
        section("cab windshield and gasket", [(-1.19,1.87),(1.19,1.87),(1.08,2.77),(-1.08,2.77)],
                -8.53,-8.46,0,WINDOW),
        solid("window reflection", (-8.533,-1.02,2.62), (-8.531,1.02,2.65), REFLECTION),
        section("cab destination header", [(-1.28,2.77),(1.28,2.77),(1.24,3.24),(-1.24,3.24)],
                -8.51,-8.34,0,CREAM),
        solid("destination display enclosure", (-8.527,-.54,2.83), (-8.513,.54,3.042), DARK),
        solid("cab access and rescue hatch", (-8.54,-.32,.98), (-8.49,.32,1.32), TEAL),
        solid("windshield wiper", (-8.543,-.89,1.94), (-8.533,-.34,1.968), SILVER),
        solid("windshield wiper", (-8.543,.34,1.94), (-8.533,.89,1.968), SILVER),
        *[round_stock("front marker", y,z,-8.54,-8.515,.062,0,color) for y in (-.94,.94)
          for z,color in ((1.48,LIGHT),(1.33,RED))],
    ]
    cab_interior = [
        solid("driver console pedestal", (-8.32,-.64,1.01), (-7.96,.56,1.46), DARK),
        section("console desk", [(-8.37,1.46),(-7.91,1.46),(-8.08,1.58),(-8.37,1.60)],
                -.59,.51,1,SILVER),
        solid("driver display and controls", (-8.26,-.30,1.56), (-8.03,.29,1.66), WINDOW),
        solid("driver seat stand", (-7.74,-.16,1.0), (-7.51,.16,1.41), DARK),
        solid("driver cushion", (-7.80,-.25,1.39), (-7.33,.25,1.49), BLUE),
        solid("driver seat back and headrest", (-7.40,-.23,1.44), (-7.30,.23,2.08), BLUE),
        solid("cab rear bulkhead, side section", (-7.22,-1.17,1), (-7.15,-.40,3.01), CREAM),
        solid("cab rear bulkhead, side section", (-7.22,.40,1), (-7.15,1.17,3.01), CREAM),
        solid("cab rear service door", (-7.23,-.391,1), (-7.16,.391,2.12), TEAL),
        solid("cab rear service door window", (-7.232,-.19,1.48), (-7.158,.19,1.98), WINDOW),
        solid("cab rear service door lock", (-7.235,-.35,1.51), (-7.151,-.30,1.56), SILVER),
    ]
    rescue = [
        solid("rescue coupler mounting flange", (-8.5,-.32,.49), (-8.29,.32,.79), DARK),
        round_stock("rescue drawbar reservation", 0,.64,-8.72,-8.29,.087,0,SILVER),
        solid("rescue adaptor access", (-8.73,-.14,.54), (-8.65,.14,.75), SILVER),
    ]
    end_panel = [
        *[solid("end vestibule side panel", (-8.51,y0,1), (-8.38,y1,3.17), CREAM)
          for y0,y1 in ((-1.35,-.63),(.63,1.35))],
        solid("end vestibule header", (-8.51,-.63,2.63), (-8.38,.63,3.17), CREAM),
        solid("end vestibule threshold extrusion", (-8.51,-.63,.97), (-8.37,.63,1.03), SILVER),
    ]
    connector_frame = [
        *[solid("bellows carrier frame upright", (-.26,y-.035,1.0), (-.22,y+.035,2.61), SILVER)
          for y in (-.595,.595)],
        solid("bellows carrier frame header", (-.26,-.63,2.57), (-.22,.63,2.62), SILVER),
    ]
    bellows = [
        *[solid("bellows vertical fold", (x-.022,y-.034,1.0), (x+.022,y+.034,2.60), RUBBER)
          for x in (-.19,-.126,-.063,0,.063,.126,.19) for y in (-.58,.58)],
        *[solid("bellows roof fold", (x-.022,-.612,2.56), (x+.022,.612,2.61), RUBBER)
          for x in (-.19,-.126,-.063,0,.063,.126,.19)],
        *[solid("bellows side membrane", (-.23,y-.016,1.0), (.23,y+.016,2.58), DARK)
          for y in (-.57,.57)],
        solid("bellows roof membrane", (-.23,-.58,2.56), (.23,.58,2.58), DARK),
        *connector_frame, *at(connector_frame, reverse=True),
    ]
    bridge = [
        solid("gangway slip bridge", (-.27,-.48,.973), (.27,.48,1.003), SILVER),
        *[solid("non-slip ribs", (x-.008,-.45,1.002), (x+.008,.45,1.007), DARK)
          for x in (-.21,-.15,-.09,-.03,.03,.09,.15,.21)],
    ]
    draft_half = [
        solid("end mounting plate", (-.31,-.245,.44), (-.235,.245,.69), SILVER),
        solid("draft gear and energy absorption housing", (-.30,-.15,.48), (-.152,.15,.662), TEAL),
        round_stock("drawbar shaft", 0,.57,-.19,-.056,.063,0,SILVER),
        solid("coupler head", (-.092,-.13,.49), (.002,.13,.66), SILVER),
        solid("coupler key and jaw profile", (-.052,-.095,.49), (.012,.003,.64), DARK),
    ]
    utilities = []
    for y, z, radius, color, name in (
        (-.47,.44,.036,BLUE,"air hose and gladhand"),
        (-.66,.50,.032,COPPER,"service power jumper and plug"),
        (.47,.48,.025,YELLOW,"control bus jumper and receptacle"),
        (.66,.395,.019,SILVER,"inter-car equipotential bond"),
    ):
        utilities.extend([
            *[solid(name + " end bracket", (x-.034,y-.052,z-.044), (x+.034,y+.052,z+.063), SILVER)
              for x in (-.25,.25)],
            round_stock(name, y,z,-.23,.23,radius,0,color),
            round_stock(name + " coupling", y,z,-.035,.035,radius+.011,0,DARK),
        ])
    return [
        group("end-cab-nose", "Terminal front panels, windshield, wipers, lamps, display and rescue hatch",
              cab, "cab-nose", "Formed sheet, safety glazing and electrical kit", (290,520,870),
              (11500,22600,47000), 59, "Fit front module, survey mounting and check seal and visibility",
              "Body and glazing fitter", "V01/V03", 2),
        group("end-cab-interior", "Cab desk, display, seat and rear service bulkhead",
              cab_interior, "cab-interior", "Console equipment, steel and lining", (210,415,770),
              (10500,22200,49000), 48, "Fit bulkhead, then install cab console, seating and cabling",
              "Electrical and interior fitter", "V01/V03", 2),
        group("end-rescue", "Outboard rescue flange, adaptor and mount",
              rescue, "cab-rescue", "Steel coupler assembly", (74,135,275), (2400,5100,10600), 7,
              "Fit terminal drawgear and check stowage and rescue access", "Mechanical fitter", "V15", 2),
        group("end-vestibule", "Inner end panels, opening portal, threshold and trim",
              end_panel, "vestibule", "Sheet, gasket and liner", (71,125,245), (1700,3100,6900), 11,
              "Fit portal and gauge floor datum and opening", "Body fitter", "V01/V03/V12", 10),
        group("connector-draft", "Paired inter-car heads, drawbars, mount flanges and draft gears",
              [*draft_half, *at(draft_half, reverse=True)], "connector-draft", "Steel coupler assembly",
              (145,270,510), (7800,15500,33000), 20, "Align drawgear and prove fit and securement before mating",
              "Mechanical fitter", "V03/V15", 5),
        group("connector-utilities", "Air hose, power and control jumpers, bonding strap, sockets and brackets",
              utilities, "connector-utilities", "Conductors, hose, plugs and brackets",
              (11,22,44), (1650,3550,7800), 11, "Key and label services; leak, continuity and motion checks",
              "Electrical and brake fitter", "V03/V13", 5),
        group("connector-bridge", "Non-slip gangway bridge and sill interface",
              bridge, "connector-bridge", "Aluminium plate and traction surface", (15,26,53),
              (880,1900,4300), 5, "Fit bridge and check articulated floor gap and step", "Interior fitter", "V03/V12", 5),
        group("connector-bellows", "Gangway bellows, two carrier frames and edge seals",
              bellows, "connector-bellows", "Fabric-reinforced elastomer and frame", (92,178,320),
              (5400,10800,23500), 14, "Mount and seal bellows then check articulation and escape path",
              "Body fitter", "V03/V12", 5),
    ]


def fitout_groups(geometry):
    return tuple([*frame_assembly(geometry), *shell_groups(geometry), *saloon_groups(geometry), *end_groups()])


def staged(groups, stage, x=0, y=0, z=0):
    return at([item for group in groups if group.stage in stage for item in group.placed], x, y, z)
