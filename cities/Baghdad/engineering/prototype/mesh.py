"""Read the article OBJ once for both the browser mesh and IFC4 product occurrences."""

from base64 import b64encode
from math import isfinite
from uuid import NAMESPACE_URL, uuid5


def read_obj(content, pieces=None, *, assembly=None):
    vertices, faces = [], {}
    current = None
    for line in content.decode().splitlines():
        fields = line.split()
        if not fields or fields[0] == "#":
            continue
        if fields[0] == "o":
            current = fields[1]
            if current in faces:
                raise ValueError("Duplicate mesh occurrence " + current)
            faces[current] = []
        elif fields[0] == "v":
            xyz = [float(x) for x in fields[1:]]
            if len(xyz) != 3 or not all(map(isfinite, xyz)):
                raise ValueError("Invalid article mesh vertex")
            vertices.append(xyz)
        elif fields[0] == "f":
            polygon = [int(i) - 1 for i in fields[1:]]
            if current is None or len(set(polygon)) < 3 or any(i < 0 or i >= len(vertices) for i in polygon):
                raise ValueError("Invalid article mesh face")
            faces[current].append(polygon)
    if pieces is None:
        if not assembly or not faces:
            raise ValueError("Give each civil article a named assembly and mesh")
        pieces = []
        for key, polygons in faces.items():
            pts = [vertices[i] for face in polygons for i in face]
            pieces.append(
                {
                    "id": key,
                    "part": key,
                    "assembly": assembly,
                    "lower_m": [min(v[k] for v in pts) for k in range(3)],
                    "upper_m": [max(v[k] for v in pts) for k in range(3)],
                }
            )
    if set(faces) != {row["id"] for row in pieces} or len(faces) != len(pieces):
        raise ValueError("Stock identities differ between the mesh and the article register")
    items = []
    for part in pieces:
        polygons = faces[part["id"]]
        indices = sorted({i for polygon in polygons for i in polygon})
        local = {i: j for j, i in enumerate(indices)}
        points = [vertices[i] for i in indices]
        if not points or any(
            abs(fn(p[k] for p in points) - part[key][k]) > 0.000002
            for fn, key in ((min, "lower_m"), (max, "upper_m"))
            for k in range(3)
        ):
            raise ValueError("Occurrence bounds differ from the stock register")
        items.append(
            {**part, "vertices": points, "faces": [[local[i] for i in polygon] for polygon in polygons]}
        )
    return items


def ifc4(parts, article, opening, title="Car and powered bogie frames", datum="Car centre at rail head"):
    """One IFC4 assembly per load path with exact OBJ faces in car coordinates."""
    rows = []

    def item(entity, *args):
        rows.append(f"#{len(rows)+1}={entity}({','.join(args)});")
        return f"#{len(rows)}"

    def string(value):
        return "'" + value.replace("'", "''") + "'"

    def guid(label):
        raw = uuid5(NAMESPACE_URL, article + "/" + label).bytes
        encoded = (
            b64encode(b"\0\0" + raw)
            .decode()[2:]
            .translate(
                str.maketrans(
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
                    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$",
                )
            )
        )
        return string(encoded)

    def seq(refs):
        return "(" + ",".join(refs) + ")"

    p = item("IFCCARTESIANPOINT", "(0.,0.,0.)")
    axis = item("IFCAXIS2PLACEMENT3D", p, "$", "$")
    position = item("IFCLOCALPLACEMENT", "$", axis)
    context = item("IFCGEOMETRICREPRESENTATIONCONTEXT", "$", "'Model'", "3", "0.000001", axis, "$")
    unit = item("IFCSIUNIT", "*", ".LENGTHUNIT.", "$", ".METRE.")
    units = item("IFCUNITASSIGNMENT", seq([unit]))
    project = item(
        "IFCPROJECT",
        guid("project"),
        "$",
        string("Baghdad Airport / " + title),
        "$",
        "$",
        "$",
        "$",
        seq([context]),
        units,
    )
    site = item(
        "IFCSITE",
        guid("article-site"),
        "$",
        string(datum),
        "$",
        "$",
        position,
        "$",
        "$",
        ".ELEMENT.",
        "$",
        "$",
        "$",
        "$",
        "$",
    )
    item("IFCRELAGGREGATES", guid("project-site"), "$", "$", "$", project, seq([site]))
    body = item(
        "IFCELEMENTASSEMBLY",
        guid("car"),
        "$",
        string(title),
        string("Airport opening " + opening),
        string("Prototype quotation article"),
        position,
        "$",
        string(article),
        ".FACTORY.",
        ".USERDEFINED.",
    )
    item("IFCRELCONTAINEDINSPATIALSTRUCTURE", guid("site-car"), "$", "$", "$", seq([body]), site)
    groups = {}
    for part in parts:
        coords = item(
            "IFCCARTESIANPOINTLIST3D", seq(seq(format(x, ".6f") for x in pt) for pt in part["vertices"])
        )
        indices = [item("IFCINDEXEDPOLYGONALFACE", seq(str(i + 1) for i in face)) for face in part["faces"]]
        solid = item("IFCPOLYGONALFACESET", coords, "$", seq(indices), "$")
        rep = item("IFCSHAPEREPRESENTATION", context, "'Body'", "'Tessellation'", seq([solid]))
        shape = item("IFCPRODUCTDEFINITIONSHAPE", "$", "$", seq([rep]))
        piece = item(
            "IFCBUILDINGELEMENTPROXY",
            guid("stock/" + part["id"]),
            "$",
            string(part["id"]),
            string(part["part"]),
            "$",
            position,
            shape,
            string(part["id"]),
            ".NOTDEFINED.",
        )
        groups.setdefault(part["assembly"], []).append(piece)
    assemblies = []
    for key, children in groups.items():
        group = item(
            "IFCELEMENTASSEMBLY",
            guid("assembly/" + key),
            "$",
            string(key),
            "$",
            string("Article part group"),
            position,
            "$",
            "$",
            ".FACTORY.",
            ".USERDEFINED.",
        )
        item("IFCRELAGGREGATES", guid("parts/" + key), "$", "$", "$", group, seq(children))
        assemblies.append(group)
    item("IFCRELAGGREGATES", guid("car-assemblies"), "$", "$", "$", body, seq(assemblies))
    header = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ViewDefinition [DesignTransferView]'),'2;1');
FILE_NAME('car-and-bogies.ifc','2026-11-23T00:00:00',('OpenSourceRail'),('OpenSourceRail'),'OpenSourceRail','OpenSourceRail','');
FILE_SCHEMA(('IFC4'));
ENDSEC;
DATA;
"""
    return (
        header.replace("car-and-bogies.ifc", "quotation-article.ifc")
        + "\n".join(rows)
        + "\nENDSEC;\nEND-ISO-10303-21;\n"
    ).encode()
