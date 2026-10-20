"""SI solid primitives shared by current native CAD exports."""
import math


def positive(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name}: finite positive number required")
    return float(value)


def part(identifier, size, at, *, kind="box", role="design-solid", **kw):
    for x in size:
        positive(x, identifier)
    if len(size) != 3 or len(at) != 3 or not all(math.isfinite(x) for x in at):
        raise ValueError("three-dimensional geometry required")
    return dict(
        id=identifier, kind=kind, size_m=list(size), at_m=list(at), role=role, **kw
    )


def volume(p):
    if p["kind"] not in {"box", "tube", "cylinder", "stepped-cylinder"}:
        raise ValueError("unsupported factory solid primitive")
    x, y, z = p["size_m"]
    result = x * y * z
    if p["kind"] == "tube":
        axis, wall = p["axis"], p["wall_m"]
        positive(wall, "wall")
        inner = list(p["size_m"])
        for j in range(3):
            if j != axis:
                inner[j] -= 2 * wall
                positive(inner[j], "tube bore")
        result -= math.prod(inner)
    elif p["kind"] == "cylinder":
        result = math.pi * x * y * z / 4
    elif p["kind"] == "stepped-cylinder":
        if abs(sum(s["length_m"] for s in p["steps"]) - z) > 1e-10:
            raise ValueError("step lengths must cover declared cylinder height")
        result = sum(
            math.pi * s["diameter_m"] ** 2 / 4 * s["length_m"] for s in p["steps"]
        )
    for h in p.get("holes", []):
        result -= (
            math.pi
            * h["diameter_m"] ** 2
            / 4
            * h.get("length_m", p["size_m"]["xyz".index(h.get("axis", "z"))])
        )
    return result


def global_size(p):
    size = list(p["size_m"])
    if p["kind"] == "cylinder":
        size = [p["size_m"][0]] * 3
        size["xyz".index(p.get("cylinder_axis", "z"))] = p["size_m"][2]
    return size
