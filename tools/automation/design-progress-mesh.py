"""Read retained FreeCAD solids for presentation; never regenerate or save CAD."""
import json


def export_mesh(source, destination):
    import FreeCAD as App

    doc = App.openDocument(str(source))
    parts = []
    triangles = 0
    try:
        for obj in doc.Objects:
            if "DesignId" not in obj.PropertiesList:
                continue
            vertices, faces = obj.Shape.tessellate(1.0)  # mm display tolerance
            triangles += len(faces)
            if triangles > 250_000:
                raise ValueError("presentation triangle budget exceeded")
            parts.append(dict(id=obj.DesignId, role=obj.Role,
                vertices=[[p.x / 1000, p.y / 1000, p.z / 1000] for p in vertices],
                faces=[list(f) for f in faces]))
        if not parts:
            raise ValueError("no identified native solids")
        with open(destination, "w") as stream:
            json.dump(dict(parts=parts, triangles=triangles), stream)
    finally:
        App.closeDocument(doc.Name)
