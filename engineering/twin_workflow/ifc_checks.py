"""Schema-checked adapter for the retained research civil exporter.

Keep corrections in this new adapter so historical exporter-bound design packets
are not silently changed. Physical solid representations are left untouched.
"""
from pathlib import Path
import re


def issues(model):
    import ifcopenshell.validate
    logger = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(model, logger, express_rules=True)
    # IFC entity handles in json_logger are not JSON serialisable. Preserve their
    # STEP record and stable identifier instead of discarding validator failures.
    rows = []
    for row in logger.statements:
        result = dict(row)
        instance = result.get("instance")
        if instance is not None:
            result["instance"] = str(instance)
        result["message"] = re.sub(r"0x[0-9a-fA-F]+", "<runtime-address>", str(result["message"]))
        rows.append(result)
    return rows


def correct_analytical_representation(path):
    import ifcopenshell
    from ifcopenshell.api import geometry
    import numpy as np
    path = Path(path)
    model = ifcopenshell.open(str(path))
    before = issues(model)
    changed = []
    for obj in model.by_type("IfcStructuralItem"):
        if obj.Representation is not None and obj.ObjectPlacement is None:
            geometry.edit_object_placement(model, product=obj, matrix=np.eye(4), is_si=True)
            changed.append(dict(id=obj.id(), name=obj.Name, repair="explicit identity placement"))
        if not obj.Representation:
            continue
        for representation in obj.Representation.Representations:
            items = []
            for item in representation.Items:
                if item.is_a() == "IfcEdge":
                    curve = model.create_entity("IfcPolyline", Points=[item.EdgeStart.VertexGeometry, item.EdgeEnd.VertexGeometry])
                    replacement = model.create_entity("IfcEdgeCurve", EdgeStart=item.EdgeStart,
                        EdgeEnd=item.EdgeEnd, EdgeGeometry=curve, SameSense=True)
                    items.append(replacement)
                    changed.append(dict(id=item.id(), repair="geometry-backed IfcEdgeCurve replaces bare IfcEdge"))
                else:
                    items.append(item)
            representation.Items = items
    # Write only to the new attempt's draft file, never the source packet.
    model.write(str(path))
    restored = ifcopenshell.open(str(path))
    return dict(before=before, repairs=changed, after=issues(restored))
