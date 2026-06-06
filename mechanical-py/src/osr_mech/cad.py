"""Internal CAD facade for the mechanical catalogue.

The catalogue source geometry is written against this small API rather
than directly against a CAD kernel. When the code runs inside FreeCAD it
creates native ``Part`` shapes. In ordinary Python, where the FreeCAD
modules are usually unavailable, it keeps deterministic bounding-box and
volume metadata so unit tests can still validate geometry envelopes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Sequence

try:  # pragma: no cover - exercised by FreeCADCmd, not normal pytest.
    import FreeCAD as App  # type: ignore[import-not-found]
    import Part as FreeCADPart  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - local dev usually has no FreeCAD module.
    App = None  # type: ignore[assignment]
    FreeCADPart = None  # type: ignore[assignment]


class Align(Enum):
    MIN = "min"
    CENTER = "center"
    MAX = "max"


@dataclass(frozen=True)
class Color:
    r: float
    g: float
    b: float
    a: float = 1.0

    def __iter__(self):
        yield self.r
        yield self.g
        yield self.b
        yield self.a


@dataclass(frozen=True)
class _Point:
    X: float
    Y: float
    Z: float

    def __iter__(self):
        yield self.X
        yield self.Y
        yield self.Z

    def __getitem__(self, index: int) -> float:
        return (self.X, self.Y, self.Z)[index]


@dataclass(frozen=True)
class _BoundingBox:
    min: _Point
    max: _Point

    @property
    def volume(self) -> float:
        return (
            max(0.0, self.max.X - self.min.X)
            * max(0.0, self.max.Y - self.min.Y)
            * max(0.0, self.max.Z - self.min.Z)
        )


@dataclass(frozen=True)
class Axis:
    name: str
    vector: tuple[float, float, float]


Axis.X = Axis("X", (1.0, 0.0, 0.0))  # type: ignore[attr-defined]
Axis.Y = Axis("Y", (0.0, 1.0, 0.0))  # type: ignore[attr-defined]
Axis.Z = Axis("Z", (0.0, 0.0, 1.0))  # type: ignore[attr-defined]


@dataclass(frozen=True)
class Plane:
    name: str
    axes: tuple[str, str]
    normal: str
    offset_mm: float = 0.0

    def offset(self, amount: float) -> "Plane":
        return Plane(self.name, self.axes, self.normal, self.offset_mm + amount)


Plane.XY = Plane("XY", ("X", "Y"), "Z")  # type: ignore[attr-defined]
Plane.XZ = Plane("XZ", ("X", "Z"), "Y")  # type: ignore[attr-defined]
Plane.YZ = Plane("YZ", ("Y", "Z"), "X")  # type: ignore[attr-defined]


@dataclass(frozen=True)
class Location:
    position: _Point

    def __init__(self, position: Sequence[float] = (0.0, 0.0, 0.0)):
        object.__setattr__(
            self,
            "position",
            _Point(float(position[0]), float(position[1]), float(position[2])),
        )


def _empty_bb() -> _BoundingBox:
    return _BoundingBox(_Point(0.0, 0.0, 0.0), _Point(0.0, 0.0, 0.0))


def _bbox_from_points(points: Iterable[tuple[float, float, float]]) -> _BoundingBox:
    pts = list(points)
    if not pts:
        return _empty_bb()
    xs, ys, zs = zip(*pts)
    return _BoundingBox(
        _Point(min(xs), min(ys), min(zs)),
        _Point(max(xs), max(ys), max(zs)),
    )


def _bbox_corners(bb: _BoundingBox) -> list[tuple[float, float, float]]:
    return [
        (x, y, z)
        for x in (bb.min.X, bb.max.X)
        for y in (bb.min.Y, bb.max.Y)
        for z in (bb.min.Z, bb.max.Z)
    ]


def _translate_bb(bb: _BoundingBox, delta: tuple[float, float, float]) -> _BoundingBox:
    dx, dy, dz = delta
    return _BoundingBox(
        _Point(bb.min.X + dx, bb.min.Y + dy, bb.min.Z + dz),
        _Point(bb.max.X + dx, bb.max.Y + dy, bb.max.Z + dz),
    )


def _union_bb(boxes: Iterable[_BoundingBox]) -> _BoundingBox:
    bbs = list(boxes)
    if not bbs:
        return _empty_bb()
    return _BoundingBox(
        _Point(min(bb.min.X for bb in bbs), min(bb.min.Y for bb in bbs), min(bb.min.Z for bb in bbs)),
        _Point(max(bb.max.X for bb in bbs), max(bb.max.Y for bb in bbs), max(bb.max.Z for bb in bbs)),
    )


def _rotate_point(
    p: tuple[float, float, float],
    axis: Axis,
    angle_deg: float,
) -> tuple[float, float, float]:
    x, y, z = p
    a = math.radians(angle_deg)
    c = math.cos(a)
    s = math.sin(a)
    if axis.name == "X":
        return (x, y * c - z * s, y * s + z * c)
    if axis.name == "Y":
        return (x * c + z * s, y, -x * s + z * c)
    return (x * c - y * s, x * s + y * c, z)


def _rotate_bb(bb: _BoundingBox, axis: Axis, angle_deg: float) -> _BoundingBox:
    return _bbox_from_points(_rotate_point(p, axis, angle_deg) for p in _bbox_corners(bb))


def _plane_point(plane: Plane, u: float, v: float, normal: float = 0.0) -> tuple[float, float, float]:
    coords = {"X": 0.0, "Y": 0.0, "Z": 0.0}
    coords[plane.axes[0]] = u
    coords[plane.axes[1]] = v
    signed_normal = -normal if plane.name == "XZ" else normal
    coords[plane.normal] = plane.offset_mm + signed_normal
    return (coords["X"], coords["Y"], coords["Z"])


def _polygon_area(points: Sequence[tuple[float, float]]) -> float:
    if len(points) < 3:
        return 0.0
    acc = 0.0
    for (x0, y0), (x1, y1) in zip(points, [*points[1:], points[0]]):
        acc += x0 * y1 - x1 * y0
    return abs(acc) / 2.0


def _copy_freecad_shape(shape):
    if shape is None:
        return None
    copy = getattr(shape, "copy", None)
    return copy() if callable(copy) else shape


def _translate_freecad_shape(shape, delta: tuple[float, float, float]):
    shape = _copy_freecad_shape(shape)
    if shape is not None and App is not None:
        shape.translate(App.Vector(*delta))
    return shape


def _rotate_freecad_shape(shape, axis: Axis, angle_deg: float):
    shape = _copy_freecad_shape(shape)
    if shape is not None and App is not None:
        shape.rotate(App.Vector(0.0, 0.0, 0.0), App.Vector(*axis.vector), angle_deg)
    return shape


def _shape_bbox(shape) -> _BoundingBox | None:
    if shape is None:
        return None
    try:
        bb = shape.BoundBox
    except Exception:
        return None
    return _BoundingBox(_Point(bb.XMin, bb.YMin, bb.ZMin), _Point(bb.XMax, bb.YMax, bb.ZMax))


def _freecad_box(length: float, width: float, height: float):
    if FreeCADPart is None or App is None:
        return None
    shape = FreeCADPart.makeBox(length, width, height)
    shape.translate(App.Vector(-length / 2.0, -width / 2.0, -height / 2.0))
    return shape


def _freecad_cylinder(radius: float, height: float):
    if FreeCADPart is None or App is None:
        return None
    shape = FreeCADPart.makeCylinder(radius, height)
    shape.translate(App.Vector(0.0, 0.0, -height / 2.0))
    return shape


class _EdgeSelector:
    def __init__(self, owner: "Part | None" = None, axis: Axis | None = None):
        self.owner = owner
        self.axis = axis

    def filter_by(self, axis: Axis) -> "_EdgeSelector":
        return _EdgeSelector(self.owner, axis)


class Part:
    """A FreeCAD shape wrapper with test-friendly metadata."""

    def __init__(
        self,
        shape=None,
        *,
        bbox: _BoundingBox | None = None,
        volume: float | None = None,
        label: str = "",
        color: Color | None = None,
    ):
        self._shape = shape
        self._bbox = bbox or _shape_bbox(shape) or _empty_bb()
        self._volume = float(volume if volume is not None else self._bbox.volume)
        self.label = label
        self.color = color

    @property
    def wrapped(self):
        return self._shape

    @property
    def Shape(self):  # pragma: no cover - compatibility for FreeCAD scripts.
        return self._shape

    @property
    def volume(self) -> float:
        if self._shape is not None:
            try:
                return float(self._shape.Volume)
            except Exception:
                pass
        return self._volume

    def bounding_box(self) -> _BoundingBox:
        return _shape_bbox(self._shape) or self._bbox

    def copy(self) -> "Part":
        return Part(
            _copy_freecad_shape(self._shape),
            bbox=self._bbox,
            volume=self._volume,
            label=self.label,
            color=self.color,
        )

    def locate(self, loc: Location) -> "Part":
        return self.translate(loc.position)

    def moved(self, loc: Location) -> "Part":
        return self.locate(loc)

    def translate(self, delta: Sequence[float]) -> "Part":
        d = (float(delta[0]), float(delta[1]), float(delta[2]))
        return Part(
            _translate_freecad_shape(self._shape, d),
            bbox=_translate_bb(self._bbox, d),
            volume=self._volume,
            label=self.label,
            color=self.color,
        )

    def rotate(self, axis: Axis, angle: float) -> "Part":
        return Part(
            _rotate_freecad_shape(self._shape, axis, angle),
            bbox=_rotate_bb(self._bbox, axis, angle),
            volume=self._volume,
            label=self.label,
            color=self.color,
        )

    def cut(self, other: "Part") -> "Part":
        return self - other

    def __sub__(self, other: "Part") -> "Part":
        shape = _copy_freecad_shape(self._shape)
        if shape is not None and getattr(other, "_shape", None) is not None:
            try:
                shape = shape.cut(other._shape)
            except Exception:
                shape = _copy_freecad_shape(self._shape)
        return Part(
            shape,
            bbox=self._bbox,
            volume=max(0.0, self._volume - getattr(other, "volume", 0.0)),
            label=self.label,
            color=self.color,
        )

    def edges(self) -> _EdgeSelector:
        return _EdgeSelector(self)

    def tessellate(self, tolerance: float):  # pragma: no cover - renderer path.
        if self._shape is not None:
            return self._shape.tessellate(tolerance)
        del tolerance
        bb = self.bounding_box()
        if bb.volume <= 0.0:
            return ([], [])
        verts = [
            _Point(bb.min.X, bb.min.Y, bb.min.Z),
            _Point(bb.min.X, bb.min.Y, bb.max.Z),
            _Point(bb.min.X, bb.max.Y, bb.min.Z),
            _Point(bb.min.X, bb.max.Y, bb.max.Z),
            _Point(bb.max.X, bb.min.Y, bb.min.Z),
            _Point(bb.max.X, bb.min.Y, bb.max.Z),
            _Point(bb.max.X, bb.max.Y, bb.min.Z),
            _Point(bb.max.X, bb.max.Y, bb.max.Z),
        ]
        tris = [
            (0, 1, 3), (0, 3, 2),
            (4, 6, 7), (4, 7, 5),
            (0, 4, 5), (0, 5, 1),
            (2, 3, 7), (2, 7, 6),
            (0, 2, 6), (0, 6, 4),
            (1, 5, 7), (1, 7, 3),
        ]
        return (verts, tris)


class Solid(Part):
    pass


class Compound(Part):
    def __init__(self, label: str = "", children: Sequence[Part] | None = None):
        self.children = list(children or [])
        shape = None
        if FreeCADPart is not None:
            child_shapes = [c.wrapped for c in self.children if getattr(c, "wrapped", None) is not None]
            if child_shapes:
                shape = FreeCADPart.makeCompound(child_shapes)
        super().__init__(
            shape,
            bbox=_union_bb(c.bounding_box() for c in self.children),
            volume=sum(getattr(c, "volume", 0.0) for c in self.children),
            label=label,
        )

    def copy(self) -> "Compound":
        c = Compound(label=self.label, children=[child.copy() for child in self.children])
        c.color = self.color
        return c

    def translate(self, delta: Sequence[float]) -> "Compound":
        c = Compound(label=self.label, children=[child.translate(delta) for child in self.children])
        c.color = self.color
        return c

    def rotate(self, axis: Axis, angle: float) -> "Compound":
        c = Compound(label=self.label, children=[child.rotate(axis, angle) for child in self.children])
        c.color = self.color
        return c

    def locate(self, loc: Location) -> "Compound":
        return self.translate(loc.position)

    def moved(self, loc: Location) -> "Compound":
        return self.locate(loc)


def Box(
    length: float,
    width: float,
    height: float,
    *,
    align: tuple[Align, Align, Align] | None = None,
) -> Part:
    del align
    bbox = _BoundingBox(
        _Point(-length / 2.0, -width / 2.0, -height / 2.0),
        _Point(length / 2.0, width / 2.0, height / 2.0),
    )
    return Part(_freecad_box(length, width, height), bbox=bbox, volume=length * width * height)


def Cylinder(
    radius: float,
    height: float,
    *,
    align: tuple[Align, Align, Align] | None = None,
) -> Part:
    del align
    bbox = _BoundingBox(_Point(-radius, -radius, -height / 2.0), _Point(radius, radius, height / 2.0))
    return Part(
        _freecad_cylinder(radius, height),
        bbox=bbox,
        volume=math.pi * radius * radius * height,
    )


@dataclass
class _Sketch:
    plane: Plane
    points: list[tuple[float, float]]
    area: float
    kind: str = "polygon"
    radius: float = 0.0


_PART_STACK: list["BuildPart"] = []
_SKETCH_STACK: list["BuildSketch"] = []


class BuildSketch:
    def __init__(self, plane: Plane = Plane.XY):
        self.plane = plane
        self.sketch = _Sketch(plane=plane, points=[], area=0.0)

    def __enter__(self) -> "BuildSketch":
        _SKETCH_STACK.append(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if _SKETCH_STACK and _SKETCH_STACK[-1] is self:
            _SKETCH_STACK.pop()
        if _PART_STACK and exc_type is None:
            _PART_STACK[-1]._sketches.append(self.sketch)


class BuildPart:
    def __init__(self):
        self._sketches: list[_Sketch] = []
        self._parts: list[Part] = []
        self.part = Part()

    def __enter__(self) -> "BuildPart":
        _PART_STACK.append(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if _PART_STACK and _PART_STACK[-1] is self:
            _PART_STACK.pop()
        if self._parts:
            self.part = self._parts[-1] if len(self._parts) == 1 else Compound(children=self._parts)

    def _set_part(self, part: Part) -> None:
        self._parts.append(part)
        self.part = part

    def edges(self) -> _EdgeSelector:
        return self.part.edges()


def _set_active_sketch(points: Sequence[tuple[float, float]]) -> None:
    if not _SKETCH_STACK:
        return
    _SKETCH_STACK[-1].sketch.points = [(float(x), float(y)) for x, y in points]
    _SKETCH_STACK[-1].sketch.area = _polygon_area(_SKETCH_STACK[-1].sketch.points)
    _SKETCH_STACK[-1].sketch.kind = "polygon"
    _SKETCH_STACK[-1].sketch.radius = 0.0


def Rectangle(
    width: float,
    height: float,
    *,
    align: tuple[Align, Align] | None = None,
) -> None:
    align = align or (Align.CENTER, Align.CENTER)

    def bounds(size: float, a: Align) -> tuple[float, float]:
        if a == Align.MIN:
            return (0.0, size)
        if a == Align.MAX:
            return (-size, 0.0)
        return (-size / 2.0, size / 2.0)

    x0, x1 = bounds(float(width), align[0])
    y0, y1 = bounds(float(height), align[1])
    _set_active_sketch([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def Circle(radius: float) -> None:
    r = float(radius)
    # Area is exact; bbox comes from this square proxy.
    if not _SKETCH_STACK:
        return
    _SKETCH_STACK[-1].sketch.points = [(-r, -r), (r, -r), (r, r), (-r, r)]
    _SKETCH_STACK[-1].sketch.area = math.pi * r * r
    _SKETCH_STACK[-1].sketch.kind = "circle"
    _SKETCH_STACK[-1].sketch.radius = r


def Polygon(
    *points: tuple[float, float],
    align: tuple[Align, Align] | None = None,
) -> None:
    del align
    _set_active_sketch(points)


def _extrude_bbox(sketch: _Sketch, amount: float) -> _BoundingBox:
    pts = []
    for n in (0.0, amount):
        pts.extend(_plane_point(sketch.plane, u, v, n) for u, v in sketch.points)
    return _bbox_from_points(pts)


def _freecad_face(sketch: _Sketch):
    if FreeCADPart is None or App is None or len(sketch.points) < 3:
        return None
    if sketch.kind == "circle":
        center = App.Vector(*_plane_point(sketch.plane, 0.0, 0.0, 0.0))
        normals = {
            "X": App.Vector(1, 0, 0),
            "Y": App.Vector(0, -1 if sketch.plane.name == "XZ" else 1, 0),
            "Z": App.Vector(0, 0, 1),
        }
        try:
            edge = FreeCADPart.makeCircle(sketch.radius, center, normals[sketch.plane.normal])
            return FreeCADPart.Face(FreeCADPart.Wire([edge]))
        except Exception:
            return None
    verts = [App.Vector(*_plane_point(sketch.plane, u, v, 0.0)) for u, v in sketch.points]
    verts.append(verts[0])
    try:
        return FreeCADPart.Face(FreeCADPart.makePolygon(verts))
    except Exception:
        return None


def _freecad_wire(sketch: _Sketch):
    if FreeCADPart is None or App is None:
        return None
    if sketch.kind == "circle":
        center = App.Vector(*_plane_point(sketch.plane, 0.0, 0.0, 0.0))
        normals = {
            "X": App.Vector(1, 0, 0),
            "Y": App.Vector(0, -1 if sketch.plane.name == "XZ" else 1, 0),
            "Z": App.Vector(0, 0, 1),
        }
        try:
            return FreeCADPart.Wire(
                [FreeCADPart.makeCircle(sketch.radius, center, normals[sketch.plane.normal])]
            )
        except Exception:
            return None
    if len(sketch.points) < 3:
        return None
    try:
        verts = [App.Vector(*_plane_point(sketch.plane, u, v, 0.0)) for u, v in sketch.points]
        verts.append(verts[0])
        return FreeCADPart.Wire(FreeCADPart.makePolygon(verts).Edges)
    except Exception:
        return None


def extrude(amount: float) -> None:
    if not _PART_STACK or not _PART_STACK[-1]._sketches:
        return
    sketch = _PART_STACK[-1]._sketches[-1]
    bbox = _extrude_bbox(sketch, float(amount))
    shape = None
    face = _freecad_face(sketch)
    if face is not None and App is not None:
        normal = {
            "X": App.Vector(amount, 0, 0),
            "Y": App.Vector(0, -amount if sketch.plane.name == "XZ" else amount, 0),
            "Z": App.Vector(0, 0, amount),
        }
        try:
            shape = face.extrude(normal[sketch.plane.normal])
        except Exception:
            shape = None
    _PART_STACK[-1]._set_part(Part(shape, bbox=bbox, volume=sketch.area * abs(float(amount))))


def loft(sketches: Sequence[_Sketch]) -> None:
    if not _PART_STACK or not sketches:
        return
    bboxes = [_bbox_from_points(_plane_point(sk.plane, u, v, 0.0) for u, v in sk.points) for sk in sketches]
    bbox = _union_bb(bboxes)
    offsets = [sk.plane.offset_mm for sk in sketches]
    span = max(offsets) - min(offsets) if len(offsets) > 1 else max(
        bbox.max.X - bbox.min.X,
        bbox.max.Y - bbox.min.Y,
        bbox.max.Z - bbox.min.Z,
    )
    avg_area = sum(sk.area for sk in sketches) / len(sketches)
    shape = None
    if FreeCADPart is not None and App is not None:
        wires = [wire for wire in (_freecad_wire(sk) for sk in sketches) if wire is not None]
        if len(wires) >= 2:
            try:
                shape = FreeCADPart.makeLoft(wires, True)
            except Exception:
                shape = None
    _PART_STACK[-1]._set_part(Part(shape, bbox=bbox, volume=avg_area * abs(span)))


def fillet(edges: _EdgeSelector, radius: float) -> None:
    owner = edges.owner
    if owner is None or owner.wrapped is None:
        return
    candidates = list(getattr(owner.wrapped, "Edges", []))
    if edges.axis is not None:
        filtered = []
        for edge in candidates:
            try:
                v0, v1 = edge.Vertexes[0].Point, edge.Vertexes[-1].Point
            except Exception:
                continue
            dx, dy, dz = abs(v1.x - v0.x), abs(v1.y - v0.y), abs(v1.z - v0.z)
            if edges.axis.name == "X" and dx >= dy and dx >= dz:
                filtered.append(edge)
            elif edges.axis.name == "Y" and dy >= dx and dy >= dz:
                filtered.append(edge)
            elif edges.axis.name == "Z" and dz >= dx and dz >= dy:
                filtered.append(edge)
        candidates = filtered or candidates
    try:
        owner._shape = owner.wrapped.makeFillet(radius, candidates)
        owner._bbox = _shape_bbox(owner._shape) or owner._bbox
    except Exception:
        return


def export_brep(obj: Part | Compound, path: str) -> bool:
    shape = to_freecad_shape(obj)
    if shape is None:
        return False
    try:
        shape.exportBrep(path)
    except Exception:
        try:
            shape.writeBrep(path)
        except Exception:
            return False
    return True


def to_freecad_shape(obj: Part | Compound):
    """Return a native FreeCAD shape for a catalogue object, if possible."""

    if isinstance(obj, Compound):
        if obj.wrapped is not None:
            return _copy_freecad_shape(obj.wrapped)
        if FreeCADPart is None:
            return None
        child_shapes = [to_freecad_shape(child) for child in obj.children]
        child_shapes = [shape for shape in child_shapes if shape is not None]
        return FreeCADPart.makeCompound(child_shapes) if child_shapes else None
    if isinstance(obj, Part):
        return _copy_freecad_shape(obj.wrapped)
    return None


__all__ = [
    "Align",
    "Axis",
    "Box",
    "BuildPart",
    "BuildSketch",
    "Circle",
    "Color",
    "Compound",
    "Cylinder",
    "Location",
    "Part",
    "Plane",
    "Polygon",
    "Rectangle",
    "Solid",
    "export_brep",
    "extrude",
    "fillet",
    "loft",
    "to_freecad_shape",
]
