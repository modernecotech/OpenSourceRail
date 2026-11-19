"""IFC4 export with metres, stable design occurrence IDs and shared representations."""

import json
import uuid
import ifcopenshell
import ifcopenshell.geom
from ifcopenshell.util.shape import get_vertices

PALETTE = dict(
    web="52717B",
    hub="63818A",
    disc="8E938B",
    floor="436175",
    roof="DCE5E1",
    sill="DDE6DF",
    glass="285164",
    end="416273",
    door="36AC98",
    frame="506472",
    wheel="304654",
    axle="758B99",
    control="D16B38",
    motor="CC8062",
    brake="D7A74A",
    collection="C27B37",
    beam="889C9D",
    pier="ABBAB1",
    rail="546A71",
    platform="CCD0BD",
    edge="EAC66D",
)


def export(m, target, check):
    f = ifcopenshell.file(schema="IFC4")
    f.header.file_name.time_stamp = "2026-11-19T00:00:00"
    f.header.file_name.name = target.name
    f.header.file_description.description = ("ViewDefinition [DesignTransferView]",)
    make = f.create_entity

    def guid(key):
        return ifcopenshell.guid.compress(
            uuid.uuid5(uuid.NAMESPACE_URL, m["candidate"] + "/" + key).hex
        )

    def point(v):
        return make("IfcCartesianPoint", Coordinates=tuple(map(float, v)))

    def axes(v):
        return make("IfcAxis2Placement3D", Location=point(v))

    world = axes((0, 0, 0))
    ctx = make(
        "IfcGeometricRepresentationContext",
        ContextType="Model",
        CoordinateSpaceDimension=3,
        Precision=1e-6,
        WorldCoordinateSystem=world,
    )
    unit = make("IfcSIUnit", UnitType="LENGTHUNIT", Name="METRE")
    project = make(
        "IfcProject",
        GlobalId=guid("project"),
        Name=m["name"] + " straight station study",
        RepresentationContexts=[ctx],
        UnitsInContext=make("IfcUnitAssignment", Units=[unit]),
    )
    site = make(
        "IfcSite",
        GlobalId=guid("site"),
        Name="Illustrative 140 m straight station window",
        CompositionType="ELEMENT",
        ObjectPlacement=make("IfcLocalPlacement", RelativePlacement=world),
    )
    make(
        "IfcRelAggregates",
        GlobalId=guid("project/site"),
        RelatingObject=project,
        RelatedObjects=[site],
    )
    properties = {
        "PhysicalCandidateId": m["candidate"],
        "EvaluationId": m["evaluation"],
        "SelectionRecord": m["selection"],
        "SourceSelection": m["source"],
        "DesignRevision": "operator-station-envelope.1",
        "ModelScope": "Design occurrences and illustrative solids. Installed mass and physical serial status unknown.",
        "SourceSHA256": json.dumps(m["sourceHashes"], sort_keys=True),
    }
    props = [
        make("IfcPropertySingleValue", Name=k, NominalValue=make("IfcText", v))
        for k, v in properties.items()
    ]
    pset = make(
        "IfcPropertySet",
        GlobalId=guid("identity"),
        Name="OSR_DesignIdentity",
        HasProperties=props,
    )
    make(
        "IfcRelDefinesByProperties",
        GlobalId=guid("project/properties"),
        RelatedObjects=[project],
        RelatingPropertyDefinition=pset,
    )
    styles = {}
    for style, hexcolour in PALETTE.items():
        rgb = [int(hexcolour[p : p + 2], 16) / 255 for p in (0, 2, 4)]
        color = make("IfcColourRgb", Red=rgb[0], Green=rgb[1], Blue=rgb[2])
        shade = make("IfcSurfaceStyleShading", SurfaceColour=color)
        styles[style] = make("IfcSurfaceStyle", Name=style, Side="BOTH", Styles=[shade])
    shapes = {}
    contained = []
    for group, name, x, y, z, a, b, c, style, shape, *extra in m["parts"]:
        key = (a, b, c, style, shape, tuple(extra))
        if key not in shapes:
            if shape == "cylinder":
                inner = extra[0] if extra else 0.0
                if inner:
                    profile = make(
                        "IfcCircleHollowProfileDef",
                        ProfileType="AREA",
                        Radius=a / 2,
                        WallThickness=a / 2 - inner,
                    )
                else:
                    profile = make(
                        "IfcCircleProfileDef", ProfileType="AREA", Radius=a / 2
                    )
                loc = make(
                    "IfcAxis2Placement3D",
                    Location=point([0, -b / 2, 0]),
                    Axis=make("IfcDirection", DirectionRatios=(0.0, 1.0, 0.0)),
                    RefDirection=make("IfcDirection", DirectionRatios=(1.0, 0.0, 0.0)),
                )
                depth = b
            else:
                profile = make(
                    "IfcRectangleProfileDef",
                    ProfileType="AREA",
                    XDim=float(a),
                    YDim=float(b),
                )
                loc = axes((0, 0, -c / 2))
                depth = c
            solid = make(
                "IfcExtrudedAreaSolid",
                SweptArea=profile,
                Position=loc,
                ExtrudedDirection=make("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
                Depth=float(depth),
            )
            make("IfcStyledItem", Item=solid, Styles=[styles[style]])
            rep = make(
                "IfcShapeRepresentation",
                ContextOfItems=ctx,
                RepresentationIdentifier="Body",
                RepresentationType="SweptSolid",
                Items=[solid],
            )
            shapes[key] = make("IfcProductDefinitionShape", Representations=[rep])
        product = make(
            "IfcBuildingElementProxy",
            GlobalId=guid(name),
            Name=name,
            Description=group + " | " + style,
            ObjectType=style,
            Tag=name,
            PredefinedType="USERDEFINED",
            Representation=shapes[key],
            ObjectPlacement=make(
                "IfcLocalPlacement",
                PlacementRelTo=site.ObjectPlacement,
                RelativePlacement=axes((x, y, z)),
            ),
        )
        contained.append(product)
    make(
        "IfcRelContainedInSpatialStructure",
        GlobalId=guid("site/products"),
        RelatedElements=contained,
        RelatingStructure=site,
    )
    output = f.to_string()
    if check:
        if output != target.read_text():
            raise ValueError(f"{target.name} differs from the exporter output")
    else:
        target.write_text(output)
    # Round-trip every placement, GUID and represented dimension. Tessellate every
    # distinct geometry via the OpenCascade backend, in local product coordinates.
    reopened = ifcopenshell.open(str(target))
    settings = ifcopenshell.geom.settings()
    seen = {}
    import ifcopenshell.validate as validate

    logger = validate.json_logger()
    validate.validate(reopened, logger)
    assert not logger.statements, logger.statements
    for group, name, x, y, z, a, b, c, style, shape, *extra in m["parts"]:
        obj = reopened.by_guid(guid(name))
        assert obj.Tag == name
        assert obj.ObjectPlacement.RelativePlacement.Location.Coordinates == (x, y, z)
        k = obj.Representation.id()
        if k not in seen:
            geom = ifcopenshell.geom.create_shape(settings, obj)
            verts = get_vertices(geom.geometry)
            seen[k] = verts.max(0) - verts.min(0)
        # OpenCascade tessellates circles within chord tolerance.
        assert max(abs(seen[k] - [a, b, c])) < 0.002, (name, seen[k], (a, b, c))
    print(
        f"{target.name}: {len(contained)} occurrences, {len(seen)} native shapes verified"
    )
