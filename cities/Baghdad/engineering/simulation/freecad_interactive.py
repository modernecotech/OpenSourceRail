"""Exercise a live FreeCAD CAM document on the released wax coupon."""

import argparse
from hashlib import sha256
import json
from math import hypot, pi
from pathlib import Path as FilePath

import FreeCAD as App
import Mesh  # Registers the CAM voxel removal mesh type.
import Part
import Path as CamPath
import PathSimulator
from Path.Main import Job, Stock
from Path.Op import Engrave
from Path.Post.Processor import PostProcessorFactory
from Path.Post.scripts import grbl_post


V = App.Vector
START = (15., 12., 5.)
CUTTER_RADIUS = 1.5
TOOL_PROJECTION = 12.
HOLDER_RADIUS = 10.
AXES = {"X": 0, "Y": 1, "Z": 2}
MOVES = ("G0", "G00", "G1", "G01")
POST_ARGS = "--no-header --no-show-editor --no-comments"
HERE = FilePath(__file__).resolve().parent
PRACTICE = HERE.parent / "prototype/cam/CAM.md"


def digest(data):
    return sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()


def box(limits):
    low, high = limits
    return Part.makeBox(*(b - a for a, b in zip(low, high)), V(*low))


def centreline(end_y):
    return Part.makePolygon([V(15, 12, 0), V(43, 12, 0), V(43, end_y, 0)])


def fixture(doc, name, limits):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = box(limits)
    return obj


def setup(doc):
    wire = doc.addObject("Part::Feature", "WaxSlotCentreline")
    wire.Shape = centreline(28)
    doc.recompute()

    job = Job.Create("WaxCouponJob", [wire])
    replaced = job.Stock
    job.Stock = Stock.CreateBox(job, V(60, 40, 8), App.Placement(V(0, 0, -8), App.Rotation()))
    doc.removeObject(replaced.Name)
    job.PostProcessor = "grbl"
    job.PostProcessorArgs = POST_ARGS
    job.Fixtures = ["G54"]  # Native work coordinate, not a physical fixture mesh.

    controller, = job.Tools.Group
    controller.Label = "T1 3 mm wax end mill"
    controller.Tool.Diameter = "3 mm"
    controller.Tool.ShankDiameter = "3 mm"
    controller.Tool.CuttingEdgeHeight = "12 mm"
    controller.Tool.Length = "12 mm"
    controller.HorizFeed = "180 mm/min"
    controller.VertFeed = "60 mm/min"
    controller.SpindleSpeed = 6000

    jaws = [
        fixture(doc, "NearSoftJaw", ((0, -6, -8), (60, 0, -2))),
        fixture(doc, "FarSoftJaw", ((0, 40, -8), (60, 46, -2))),
    ]
    doc.recompute()
    op = Engrave.Create("SlotCentrelineEngrave", parentJob=job)
    op.Base = [(job.Model.Group[0], ("Edge1", "Edge2"))]
    for key, value in dict(StartDepth=0., FinalDepth=-1., StepDown=.5, ClearanceHeight=5., SafeHeight=5.).items():
        op.setExpression(key, None)
        setattr(op, key, value)
    doc.recompute()
    assert op.ToolController == controller and op in job.Operations.Group
    assert job.Stock.Shape.Volume == 60 * 40 * 8
    return wire, job, controller, op, jaws


def post(job):
    processor = PostProcessorFactory.get_post_processor(job, job.PostProcessor)
    sections = processor.export()
    assert len(sections) == 1
    gcode = sections[0][1]
    assert all(word in gcode for word in ("G21", "G54", "G90", "M3 S6000", "F60.000", "F180.000"))
    return gcode


def motion(gcode):
    path = CamPath.Path()
    path.setFromGCode(gcode)
    position = list(START)
    for command in path.Commands:
        if command.Name in MOVES:
            origin = tuple(position)
            for axis, index in AXES.items():
                position[index] = command.Parameters.get(axis, position[index])
            yield command, origin, tuple(position)


def sweep(a, b, radius, cylinder_height, offset=0.):
    """Union of cylindrical tool positions for the coupon's linear XY or Z moves."""
    bottom = min(a[2], b[2]) + offset
    height = abs(a[2] - b[2]) + cylinder_height
    start, end = V(a[0], a[1], bottom), V(b[0], b[1], bottom)
    first = Part.makeCylinder(radius, height, start)
    dx, dy = end.x - start.x, end.y - start.y
    length = hypot(dx, dy)
    if length < 1e-9:
        return first
    if a[2] != b[2]:
        raise ValueError("Stock/fixture sweep expects horizontal or axial motion")
    side = V(-dy / length * radius, dx / length * radius, 0)
    outline = Part.makePolygon([start + side, end + side, end - side, start - side, start + side])
    web = Part.Face(outline).extrude(V(0, 0, height))
    return first.fuse([web, Part.makeCylinder(radius, height, end)])


def measure(stock, gcode, fixtures, end_y, step_path=None, depth_mm=1.):
    voxel = PathSimulator.PathSim()
    voxel.BeginSimulation(stock, .25)
    voxel.SetToolShape(Part.makeCylinder(CUTTER_RADIUS, TOOL_PROJECTION), .10)
    position = App.Placement(V(*START), App.Rotation())
    cuts = []
    contacts = []
    for n, (command, a, b) in enumerate(motion(gcode)):
        position = voxel.ApplyCommand(position, command)
        assert (position.Base - V(*b)).Length < 1e-7
        if a == b:
            continue
        cutter = sweep(a, b, CUTTER_RADIUS, TOOL_PROJECTION)
        holder = sweep(a, b, HOLDER_RADIUS, 20., TOOL_PROJECTION)
        for obstacle in fixtures:
            for component, shape in (("cutter", cutter), ("holder", holder)):
                volume = shape.common(obstacle.Shape).Volume
                if volume > 1e-6:
                    contacts.append({"move": n, "fixture": obstacle.Name, "component": component,
                                     "overlap_mm3": round(volume, 5), "end_xyz_mm": b})
        if command.Name in ("G0", "G00") and a[:2] != b[:2] and min(a[2], b[2]) < 5.:
            raise ValueError("XY rapid below 5 mm approach plane")
        if a != b and min(a[2], b[2]) < 0:
            cuts.append(cutter.common(stock))
    _, removed_mesh = voxel.GetResultMesh()
    removed = cuts[0].fuse(cuts[1:]).removeSplitter()
    b = removed.BoundBox
    # Golden CAD solid from the designed XY legs and target depth, independent
    # of the native post's vertices. Compare both shapes before optional export.
    target_depth = depth_mm
    a, bend, c = (15, 12, -target_depth), (43, 12, -target_depth), (43, end_y, -target_depth)
    design_cut = sweep(a, bend, CUTTER_RADIUS, target_depth).fuse(
        sweep(bend, c, CUTTER_RADIUS, target_depth)).removeSplitter()
    shape_error = removed.cut(design_cut).Volume + design_cut.cut(removed).Volume
    assert shape_error < 1e-6
    if step_path is not None:
        stock.cut(design_cut).removeSplitter().exportStep(str(step_path))
    plan_area = 2 * CUTTER_RADIUS * (28 + end_y - 12) + (
        pi - (1 - pi / 4)) * CUTTER_RADIUS**2
    exact = plan_area * -b.ZMin
    assert abs(removed.Volume - exact) < 1e-4
    assert abs(removed_mesh.Volume - exact) / exact < .15
    # Take a detached cross section far from either rounded end and the bend.
    section = removed.common(Part.makePlane(40, 8, V(25, 0, -8), V(1, 0, 0), V(0, 1, 0)))
    section_box = section.BoundBox
    assert abs(section.Area - 3 * -b.ZMin) < 1e-6
    assert abs(section_box.YLength - 3.) < 1e-6
    return {
        "centreline_end_y_mm": end_y, "removed_brep_mm3": round(removed.Volume, 4),
        "removed_voxel_mesh_mm3": round(removed_mesh.Volume, 4),
        "voxel_pitch_mm": .25, "design_symmetric_difference_mm3": round(shape_error, 7),
        "remaining_stock_mm3": round(stock.Volume - removed.Volume, 4),
        "section_at_x25_mm": {"slot_width_mm": round(section_box.YLength, 4),
                              "slot_depth_mm": round(section_box.ZLength, 4),
                              "remaining_floor_mm": round(8 + b.ZMin, 4)},
        "fixture_contacts": contacts,
        "sha256_grbl": digest(gcode),
        "cut_endpoints_xyz_mm": [b for command, _, b in motion(gcode) if command.Name in ("G1", "G01")],
    }


def exercise(out=None):
    doc = App.newDocument("WaxCouponInteractive")
    try:
        if out is not None:
            out.mkdir(parents=True, exist_ok=True)
        wire, job, controller, op, jaws = setup(doc)
        stock = job.Stock.Shape
        opening = post(job)
        baseline = measure(stock, opening, jaws, 28, out / "wax-coupon-baseline.step" if out else None)
        assert not baseline["fixture_contacts"]

        wire.Shape = centreline(30)
        doc.recompute()
        assert op.Base[0][0] == job.Model.Group[0]
        edited = post(job)
        changed = measure(stock, edited, jaws, 30, out / "wax-coupon-y30.step" if out else None)
        assert not changed["fixture_contacts"]
        assert opening != edited
        assert [(43., 28., -.5), (43., 28., -1.)] == [p for p in baseline["cut_endpoints_xyz_mm"] if p[1] == 28]
        assert [(43., 30., -.5), (43., 30., -1.)] == [p for p in changed["cut_endpoints_xyz_mm"] if p[1] == 30]

        op.FinalDepth = -1.5
        doc.recompute()
        depth = post(job)
        depth_test = measure(stock, depth, jaws, 30, depth_mm=1.5)
        assert depth_test["section_at_x25_mm"]["remaining_floor_mm"] == 6.5
        assert not depth_test["fixture_contacts"]
        op.FinalDepth = -1
        doc.recompute()
        assert post(job) == edited

        # A physical obstacle is a model object. The native job Fixtures
        # property is only a WCS list, so the caller checks fixture BReps.
        obstruction = fixture(doc, "CrossingObstacle", ((35, 10, -2), (40, 14, 3)))
        doc.recompute()
        unsafe_native_post = post(job)
        assert unsafe_native_post == edited
        overlap = measure(stock, unsafe_native_post, [*jaws, obstruction], 30)
        assert {x["component"] for x in overlap["fixture_contacts"]} == {"cutter"}
        assert {x["fixture"] for x in overlap["fixture_contacts"]} == {"CrossingObstacle"}
        receipt = {
            "schema": "freecad-wax-coupon-interactive/1",
            "freecad_version": App.Version()[:5], "gui_up": bool(App.GuiUp),
            "source_practice_sha256": digest(PRACTICE.read_bytes()),
            "script_sha256": digest(FilePath(__file__).read_bytes()),
            "grbl_post_sha256": digest(FilePath(grbl_post.__file__).read_bytes()),
            "job_type": type(job.Proxy).__name__, "controller_type": type(controller.Proxy).__name__,
            "operation_type": type(op.Proxy).__name__, "native_work_coordinates": job.Fixtures,
            "tool": {"diameter_mm": 3., "projection_mm": 12., "holder_diameter_mm": 20.,
                     "rpm": 6000, "feed_xy_mm_min": 180., "feed_z_mm_min": 60.},
            "stock_mm": [60., 40., 8.], "stock_top_z_mm": 0.,
            "baseline": baseline, "geometry_edit": changed, "depth_edit_control": depth_test,
            "blocked_fixture_trial": {"native_status": "posted unchanged", "caller_status": "blocked",
                                      "fixture_bounds_mm": [[35, 10, -2], [40, 14, 3]],
                                      "fixture_contacts": overlap["fixture_contacts"]},
            "physical_accepted": False,
        }
        if out is not None:
            (out / "baseline-preview.txt").write_text(opening)
            (out / "geometry-edit-preview.txt").write_text(edited)
            doc.saveAs(str(out / "wax-coupon.FCStd"))
        return receipt
    finally:
        App.closeDocument(doc.Name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=FilePath)
    parser.add_argument("--receipt", type=FilePath, default=HERE / "freecad_interactive.json")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    receipt = exercise(args.out)
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.write:
        args.receipt.write_text(text)
    elif args.receipt.read_text() != text:
        raise ValueError("FreeCAD interactive benchmark differs from retained receipt")
    print(digest(text))


if __name__ == "__main__":
    main()
