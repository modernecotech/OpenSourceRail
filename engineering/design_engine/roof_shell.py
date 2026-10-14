"""Native curved S8R laminate, discrete radial springs and hollow BOX rails.

CalculiX 2.23 shell/beam/spring cards follow its published input manual. This
model keeps unqualified transverse lamina and curved-contact assumptions visible;
it is not a joint-strength, thermal, fatigue, fire or physical qualification.
"""

from __future__ import annotations
import hashlib
import math
from pathlib import Path
import re
import shutil
import subprocess

from osr_mech.rolling_stock.composite_panels import roof_arc, balanced_skin
from osr_mech.section_contract import calculix_box
from .contracts import fingerprint, canonical


def partition(values, maximum):
    result = []
    points = sorted(set(round(float(x), 12) for x in values))
    for left, right in zip(points, points[1:]):
        count = max(1, math.ceil((right - left) / maximum))
        result.extend(left + (right - left) * i / count for i in range(count))
    return result + [points[-1]]


def deck(
    contract,
    *,
    mesh_size=0.08,
    pressure_pa=2000,
    failed_clip=None,
    contact_stiffness_n_m=1e7,
):
    p = contract["panel_parameters"]
    width = p["width_m"]
    arc = roof_arc(p["height_m"], p["crown_m"])
    if (
        not p["crown_m"]
        or p["holes"]
        or not 0.02 <= mesh_size <= 0.15
        or pressure_pa <= 0
        or contact_stiffness_n_m <= 0
    ):
        raise ValueError("bounded curved unperforated roof-shell domain required")
    radius = arc["radius_m"]
    length = arc["arc_length_m"]
    land = 0.025
    rails = contract["support_network"]["rails"]
    xs = [0, width, land, width - land]
    ys = [0, length, land, length - land]
    for rail in rails:
        a, b = rail["interval_m"]
        xs.extend([a + 0.2 * (b - a), a + 0.8 * (b - a)])
        ys.append(rail["station_m"])
    xs = partition(xs, mesh_size)
    ys = partition(ys, mesh_size)
    coords = {}
    lattice = {}
    next_node = 1
    next_element = 1
    elements = []
    loads = {}
    sections = []
    orientations = []

    def normal(y):
        angle = (y - length / 2) / radius
        return (0, math.sin(angle), math.cos(angle))

    def position(x, y, offset=0):
        angle = (y - length / 2) / radius
        return [
            x,
            (radius + offset) * math.sin(angle),
            (radius + offset) * math.cos(angle) - radius + p["crown_m"],
        ]

    def node(x, y):
        nonlocal next_node
        key = (round(x, 12), round(y, 12))
        if key not in lattice:
            lattice[key] = next_node
            coords[next_node] = position(x, y)
            next_node += 1
        return lattice[key]

    for j, (ya, yb) in enumerate(zip(ys, ys[1:])):
        for i, (xa, xb) in enumerate(zip(xs, xs[1:])):
            xy = [
                (xa, ya),
                (xb, ya),
                (xb, yb),
                (xa, yb),
                ((xa + xb) / 2, ya),
                (xb, (ya + yb) / 2),
                ((xa + xb) / 2, yb),
                (xa, (ya + yb) / 2),
            ]
            ids = [node(x, y) for x, y in xy]
            identifier = next_element
            next_element += 1
            name = f"S{identifier}"
            elements.append((identifier, ids, name))
            theta = ((ya + yb) / 2 - length / 2) / radius
            area = (xb - xa) * (yb - ya)
            for k, (x, y) in enumerate(xy):
                weight = -1 / 12 if k < 4 else 1 / 3
                direction = normal(y)
                tag = ids[k]
                value = loads.setdefault(tag, [0.0, 0.0, 0.0])
                for axis in range(3):
                    value[axis] -= pressure_pa * area * weight * direction[axis]
            solid = (
                (xa + xb) / 2 < land
                or (xa + xb) / 2 > width - land
                or (ya + yb) / 2 < land
                or (ya + yb) / 2 > length - land
            )
            layers = []
            for face in range(2):
                for ply in balanced_skin(p["skin_m"]):
                    angle = math.radians(ply.angle_deg)
                    orient = f"O{identifier}_{len(layers)}"
                    u = [
                        math.cos(angle),
                        math.sin(angle) * math.cos(theta),
                        -math.sin(angle) * math.sin(theta),
                    ]
                    v = [
                        -math.sin(angle),
                        math.cos(angle) * math.cos(theta),
                        -math.cos(angle) * math.sin(theta),
                    ]
                    orientations.extend(
                        [
                            "*ORIENTATION,NAME=" + orient,
                            ",".join(f"{x:.12g}" for x in u + v),
                        ]
                    )
                    layers.append((ply.thickness_m, "GLASS", orient))
                if face == 0:
                    layers.extend(
                        [
                            (0.0002, "BOND", None),
                            (p["core_m"], "GLASS" if solid else "CORE", None),
                            (0.0002, "BOND", None),
                        ]
                    )
            sections.append("*SHELL SECTION,ELSET=" + name + ",COMPOSITE")
            sections.extend(
                f"{thickness:.12g},,{material}"
                + ("," + orientation if orientation else "")
                for thickness, material, orientation in layers
            )
    plate_nodes = set(coords)
    beam_elements = []
    beam_sections = []
    anchors = []
    clips = []
    spring_elements = []
    for index, rail in enumerate(rails):
        station = rail["station_m"]
        a, b = rail["interval_m"]
        clip_x = [a + 0.2 * (b - a), a + 0.8 * (b - a)]
        positions = partition([a, *clip_x, b], mesh_size)
        tags = {}

        def beam_node(x):
            nonlocal next_node
            key = round(x, 12)
            if key not in tags:
                tags[key] = next_node
                coords[next_node] = position(x, station, -0.045)
                next_node += 1
            return tags[key]

        group = f"R{index}"
        for left, right in zip(positions, positions[1:]):
            ids = [beam_node(left), beam_node((left + right) / 2), beam_node(right)]
            beam_elements.append((next_element, ids, group))
            next_element += 1
        anchors.extend([beam_node(a), beam_node(b)])
        theta = (station - length / 2) / radius
        sec = contract["support_network"]["section"]
        beam_sections.extend(
            [
                "*BEAM SECTION,ELSET=" + group + ",MATERIAL=STEEL,SECTION=BOX",
                calculix_box(sec, units="m"),
                f"0,{math.cos(theta):.12g},{-math.sin(theta):.12g}",
            ]
        )
        for slot, x in enumerate(clip_x):
            clip_id = rail["id"] + f"-clip-{slot}"
            plate = node(x, station)
            beam = beam_node(x)
            bolt = next(
                item
                for item in contract["parts"]
                if item["id"] == rail["id"] + f"-clip-bolt-{slot}"
            )["manufacturing"]["primitives"][0]
            kbolt = (
                contract["materials"]["fastener"]["young_pa"]
                * math.pi
                * bolt["radius_m"] ** 2
                / bolt["length_m"]
            )
            effective = 1 / (1 / kbolt + 1 / contact_stiffness_n_m)
            clips.append(
                dict(
                    id=clip_id,
                    plate_node=plate,
                    rail_node=beam,
                    active=clip_id != failed_clip,
                    stiffness_n_m=effective,
                    contact_basis="unqualified curved insert/contact stiffness sensitivity",
                )
            )
            if clip_id != failed_clip:
                spring_elements.append((next_element, [plate, beam]))
                next_element += 1
    if failed_clip and failed_clip not in {c["id"] for c in clips}:
        raise ValueError("unknown physical roof clip")
    text = [
        "*HEADING",
        "OSR curved roof laminate and actual BOX rails, SI research only",
        "*NODE",
    ]
    text += [
        f"{tag}," + ",".join(f"{x:.12g}" for x in xyz)
        for tag, xyz in sorted(coords.items())
    ]
    for tag, ids, name in elements:
        text += ["*ELEMENT,TYPE=S8R,ELSET=" + name, f"{tag}," + ",".join(map(str, ids))]
    for tag, ids, name in beam_elements:
        text += [
            "*ELEMENT,TYPE=B32R,ELSET=" + name,
            f"{tag}," + ",".join(map(str, ids)),
        ]
    for (tag, ids), clip in zip(spring_elements, [c for c in clips if c["active"]]):
        text += [
            "*ELEMENT,TYPE=SPRINGA,ELSET=C" + str(tag),
            f"{tag}," + ",".join(map(str, ids)),
            "*SPRING,ELSET=C" + str(tag),
            "",
            f'{clip["stiffness_n_m"]:.8f}',
        ]
    glass = contract["materials"]["gfrp"]
    core = contract["materials"]["foam"]
    for name, E1, E2, E3, nu, G12, G13, G23 in [
        (
            "GLASS",
            glass["e1_pa"],
            glass["e2_pa"],
            glass["e2_pa"],
            glass["poisson12"],
            glass["g12_pa"],
            glass["g12_pa"],
            glass["g12_pa"],
        ),
        (
            "CORE",
            core["young_pa"],
            core["young_pa"],
            core["young_pa"],
            core["poisson"],
            core["shear_pa"],
            core["shear_pa"],
            core["shear_pa"],
        ),
    ]:
        text += [
            "*MATERIAL,NAME=" + name,
            "*ELASTIC,TYPE=ENGINEERING CONSTANTS",
            ",".join(map(str, [E1, E2, E3, nu, nu, nu, G12, G13])),
            str(G23),
        ]
    text += [
        "*MATERIAL,NAME=BOND",
        "*ELASTIC",
        "2.e9,0.3",
        "*MATERIAL,NAME=STEEL",
        "*ELASTIC",
        "210.e9,0.3",
        *orientations,
        *sections,
        *beam_sections,
    ]
    text += ["*NSET,NSET=PLATE"] + [
        ",".join(map(str, sorted(plate_nodes)[i : i + 12]))
        for i in range(0, len(plate_nodes), 12)
    ]
    text += ["*NSET,NSET=ANCHORS"] + [
        ",".join(map(str, anchors[i : i + 12])) for i in range(0, len(anchors), 12)
    ]
    # Three datum constraints suppress only in-plane rigid modes. Defined clips
    # and rail-end bracket supports carry transverse pressure.
    text += ["*BOUNDARY", f"{node(0,0)},1,2", f"{node(width,0)},2,2"] + [
        f"{n},1,3" for n in anchors
    ]
    text += ["*STEP", "*STATIC", "*CLOAD"]
    for tag, force in loads.items():
        for axis, value in enumerate(force, 1):
            if abs(value) > 1e-14:
                text.append(f"{tag},{axis},{value:.12g}")
    text += [
        "*NODE PRINT,NSET=PLATE",
        "U",
        "*NODE PRINT,NSET=ANCHORS,TOTALS=YES",
        "RF",
        "*END STEP",
    ]
    return "\n".join(text) + "\n", dict(
        clips=clips,
        nodes=coords,
        plate_nodes=sorted(plate_nodes),
        applied_force_n=[sum(f[i] for f in loads.values()) for i in range(3)],
        loaded_area_m2=width * length,
        plate_element_count=len(elements),
        hollow_rail_element_count=len(beam_elements),
    )


def solve(contract, folder, **options):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    source, geometry = deck(contract, **options)
    binary = shutil.which("ccx")
    if not binary:
        raise RuntimeError("native CalculiX required; no flat-plate fallback")
    (folder / "roof.inp").write_text(source)
    result = subprocess.run(
        [binary, "-i", "roof"],
        cwd=folder,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=180,
    )
    (folder / "roof.log").write_text(result.stdout)
    if result.returncode or "*ERROR" in result.stdout.upper():
        raise RuntimeError(
            "native curved-shell execution failed; inspect retained roof.log"
        )
    values = {}
    forces = []
    mode = None
    for line in (folder / "roof.dat").read_text().splitlines():
        lower = line.lower()
        if "displacements" in lower:
            mode = "u"
        elif "forces" in lower:
            mode = "f"
        fields = line.split()
        if len(fields) == 4 and fields[0].isdigit():
            numbers = [float(x.replace("D", "E")) for x in fields[1:]]
            if mode == "u":
                values[int(fields[0])] = numbers
            elif mode == "f":
                forces.append(numbers)
    if not values or any(not math.isfinite(x) for u in values.values() for x in u):
        raise ValueError("native shell displacement evidence missing/nonfinite")
    radial = []
    p = contract["panel_parameters"]
    arc = roof_arc(p["height_m"], p["crown_m"])
    radius = arc["radius_m"]
    for tag, u in values.items():
        xyz = geometry["nodes"].get(tag)
        if xyz:
            normal = [0, xyz[1] / radius, (xyz[2] + radius - p["crown_m"]) / radius]
            radial.append(abs(sum(a * b for a, b in zip(u, normal))))
    if not radial:
        raise ValueError("native shell nodes do not reconcile their physical map")
    report = dict(
        schema="osr-native-curved-roof/1",
        contract_sha256=fingerprint(contract),
        options=options,
        maximum_radial_deflection_m=max(radial),
        maximum_translation_m=max(
            math.sqrt(sum(x * x for x in u)) for u in values.values()
        ),
        displacement_node_count=len(values),
        geometry=geometry,
        support_reaction_sum_n=[sum(f[i] for f in forces) for i in range(3)],
        deflection_screen="passed" if max(radial) <= 0.005 else "failed",
        physical_validation=False,
        production_released=False,
        model_limits=[
            "dry small-displacement S8R shell",
            "transverse lamina properties and bond constants are assumptions",
            "nominal core normal modulus assigned to unmeasured in-plane directions",
            "bilateral radial curved-contact sensitivity, no local pull-out/peel/contact law",
            "simply supported hollow rails; no bracket/weld resistance",
            "roof insert lands/seals/retention remain incomplete",
            "no thermal/fatigue/fire qualification",
        ],
    )
    force_scale = max(1, math.sqrt(sum(x * x for x in geometry["applied_force_n"])))
    residual = (
        math.sqrt(
            sum(
                (a + b) ** 2
                for a, b in zip(
                    report["support_reaction_sum_n"], geometry["applied_force_n"]
                )
            )
        )
        / force_scale
    )
    report["force_balance_relative_error"] = residual
    if residual > 1e-5:
        raise ValueError("curved shell/rail reactions do not balance applied pressure")
    report["native_files_sha256"] = {
        name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
        for name in ("roof.inp", "roof.dat", "roof.log")
    }
    (folder / "result.json").write_bytes(canonical(report) + b"\n")
    return report
