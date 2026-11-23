"""Independent FreeCAD importer, upstream GRBL post and material-removal check.

Run in FreeCAD's own Python environment. See CAM.md for the exact command.
"""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path as FilePath

import FreeCAD as App
import Import
import Mesh  # Registers the mesh data type returned by PathSimulator.
import Part
import Path as CamPath
import PathSimulator
from Path.Post.scripts import grbl_post

HERE = FilePath(__file__).resolve().parent
VECTOR = App.Vector
# Geometry from the sealed revised cut list, independent of the generator.
BLANKS = {"gusset": [(0,0),(450,0),(0,450)],
          "primary_underside": [(0,0),(180,0),(180,140),(0,140)],
          "secondary_top": [(0,0),(170,0),(170,140),(0,140)],
          "secondary_body": [(0,0),(170,0),(170,160),(0,160)]}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_contours(path):
    doc = App.newDocument("Dxf")
    try:
        Import.readDXF(str(path), doc.Name, False)
        result = []
        for obj in doc.Objects:
            if hasattr(obj, "Shape") and not obj.Shape.isNull():
                for wire in obj.Shape.Wires:
                    if not wire.isClosed():
                        raise ValueError(f"Open wire {path}")
                    result.append(wire.copy())
        return result
    finally:
        App.closeDocument(doc.Name)


def coordinates(wire):
    return tuple(sorted((round(v.X,5), round(v.Y,5)) for v in wire.Vertexes))


def verify_drawings():
    for name, points in BLANKS.items():
        wires = import_contours(HERE / f"parts/{name}.dxf")
        if len(wires) != 1 or coordinates(wires[0]) != tuple(sorted(points)):
            raise ValueError(f"CAD profile failed {name}")
    placements = defaultdict(list)
    for row in csv.DictReader((HERE / "sheet-placements.csv").read_text().splitlines()):
        sign = {0: 1, 180: -1}[int(row["z_rotation_deg"])]
        placements[row["layout"]].append(tuple(sorted(
            (int(row["origin_x_mm"])+sign*x, int(row["origin_y_mm"])+sign*y)
            for x, y in BLANKS[row["part"]])))
    found = {}
    for layout, targets in sorted(placements.items()):
        wires = import_contours(HERE / f"sheets/{layout}.dxf")
        if Counter(map(coordinates, wires)) != Counter(targets):
            raise ValueError(f"DXF arrangement differs from setup {layout}")
        faces = [Part.Face(wire) for wire in wires]
        for i, first in enumerate(faces):
            a = first.BoundBox
            if min(a.XMin-10, a.YMin-10, 2990-a.XMax, 1490-a.YMax) < -1e-5:
                raise ValueError(f"Sheet border breach {layout}")
            for second in faces[:i]:
                b = second.BoundBox
                if max(a.XMin-b.XMax,b.XMin-a.XMax,a.YMin-b.YMax,b.YMin-a.YMax) < 7-1e-5:
                    if first.distToShape(second)[0] < 7-1e-5:
                        raise ValueError(f"Insufficient contour spacing {layout}")
        found[layout] = len(wires)
    return found


def verify_practice():
    doc = App.newDocument("Practice")
    feature = doc.addObject("Path::Feature", "WaxSlot")
    commands = []
    for line in (HERE / "training/practice-path.txt").read_text().splitlines():
        # FreeCAD internal feed in mm/s, posted GRBL feed in mm/min.
        words = [f"F{float(w[1:])/60}" if w.startswith("F") else w for w in line.split()]
        commands.append(CamPath.Command(" ".join(words)))
    feature.Path = CamPath.Path(commands)
    native = grbl_post.export([feature], "-", "--no-header --no-show-editor --no-comments")
    if native.encode() != (HERE / "training/practice.nc").read_bytes():
        raise ValueError("Independent FreeCAD GRBL post output differs")
    path = CamPath.Path()
    path.setFromGCode(native)
    stock = Part.makeBox(60, 40, 8, VECTOR(0,0,-8))
    voxel = PathSimulator.PathSim()
    voxel.BeginSimulation(stock, 0.25)
    voxel.SetToolShape(Part.makeCylinder(1.5, 12), 0.10)
    position = App.Placement(VECTOR(15,12,5), App.Rotation())
    visited = []
    for command in path.Commands:
        if command.Name in ("G0","G00","G1","G01"):
            prev = position.Base
            position = voxel.ApplyCommand(position, command)
            pos = position.Base
            visited.append(tuple(round(c, 3) for c in pos))
            # 3 mm flat mill, 12 mm projection, 20 mm diameter holder. Jaws
            # occupy Y=-6..0 and 40..46, with tops at Z=-2. Linear sweeps only.
            if min(prev.z, pos.z) < -1 or min(prev.z, pos.z)+12 <= -2:
                raise ValueError("Tool depth or holder clearance breach")
            if min(prev.x,pos.x)-1.5 < 0 or max(prev.x,pos.x)+1.5 > 60 or min(prev.y,pos.y)-1.5 < 0 or max(prev.y,pos.y)+1.5 > 40:
                raise ValueError("Tool outside coupon or inside a jaw")
            if command.Name in ("G0","G00") and (prev.x,prev.y) != (pos.x,pos.y) and min(prev.z,pos.z) < 5:
                raise ValueError("XY rapid below approach plane")
    expected = [(15,12,5),(15,12,5),(15,12,-.5),(43,12,-.5),(43,28,-.5),(43,28,5),
                (15,12,5),(15,12,-1),(43,12,-1),(43,28,-1),(43,28,5)]
    if visited != expected:
        raise ValueError("Program failed two-depth L-slot trace")
    _, removed = voxel.GetResultMesh()
    radius = 1.5
    # Two round-ended cuts overlap at a right-angle turn. Interior overlap
    # exceeds the common circular cap by the square corner outside that circle.
    exact = 2*radius*(28+16) + math.pi*radius**2 - (1-math.pi/4)*radius**2
    if abs(removed.Volume-exact) / exact > 0.15:
        raise ValueError("Voxel removal exceeds 15% discretisation agreement band")
    App.closeDocument(doc.Name)
    return dict(linear_move_endpoints_mm=visited, tool_diameter_mm=3, holder_diameter_mm=20,
                holder_projection_mm=12, minimum_remaining_floor_mm=7,
                analytic_swept_removal_mm3=round(exact,4), voxel_removed_mm3=round(removed.Volume,4),
                voxel_pitch_mm=0.25, simulated_rapid_xy_clearance_mm=5,
                posted_nc_sha256=digest(HERE/"training/practice.nc"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    receipt = dict(native_tool="FreeCAD", version=App.Version()[:5],
                   grbl_post_sha256=digest(FilePath(grbl_post.__file__)), verifier_sha256=digest(FilePath(__file__)),
                   input_cam_evaluation_id=json.loads((HERE/"cam-manifest.json").read_bytes())["evaluation_id"],
                   independently_imported_dxf_entities=verify_drawings(), practice=verify_practice(),
                   verification_scope="Native CAD import, geometry and spacing, GRBL repost and voxel tool sweep. Physical stock, spindle, controller, fixture and machine qualification pending.")
    data = (json.dumps(receipt, sort_keys=True, indent=2)+"\n").encode()
    path = HERE/"training/freecad-receipt.json"
    if args.write:
        path.write_bytes(data)
    elif data != path.read_bytes():
        raise ValueError("Native replay differs from archived FreeCAD receipt")
    print(f"FreeCAD replay passed; {hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
