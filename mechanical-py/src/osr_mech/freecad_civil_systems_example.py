"""Generate the native FreeCAD civil-systems integration test document."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import FreeCAD as App  # type: ignore[import-not-found]

from osr_mech.cad import to_freecad_shape
from osr_mech.civil_systems_integration import (
    DIGITAL_TWIN_SCHEMA,
    ZONE_ASSET_IDS,
    asset_class_for_component,
    asset_id_for_component,
    assert_integration_checks,
    integration_components,
    operational_state_for_component,
    write_digital_twin_manifest,
)


ZONE_COLOURS: dict[str, tuple[float, float, float]] = {
    "01 At-grade ground station": (0.72, 0.72, 0.69),
    "02 At-grade junction": (0.62, 0.48, 0.29),
    "03 Viaduct approaches and substructure": (0.68, 0.69, 0.70),
    "04 Elevated station": (0.47, 0.62, 0.75),
    "05 Rolling stock": (0.05, 0.38, 0.18),
}


def _catalog_root() -> Path:
    return Path(__file__).resolve().parents[2] / "catalog" / "freecad"


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", value.strip()).strip("_") or "Object"
    if cleaned[0].isdigit():
        cleaned = f"OSR_{cleaned}"
    return cleaned[:72]


def validate_saved_document(path: Path, expected_components: int) -> tuple[int, int]:
    """Reopen the saved artifact and verify its persisted native geometry."""

    doc = App.openDocument(str(path))
    try:
        notes = doc.getObject("IntegrationReviewNotes")
        if notes is None or not bool(getattr(notes, "AllNativeShapesValid", False)):
            raise RuntimeError("saved document is missing its successful integration review record")
        if len(getattr(notes, "PassedInterfaceChecks", [])) != 9:
            raise RuntimeError("saved document does not contain all nine interface PASS records")
        if len(getattr(notes, "PassedNativeClashChecks", [])) != 9:
            raise RuntimeError("saved document does not contain all nine native clash-clearance PASS records")
        features = [obj for obj in doc.Objects if getattr(obj, "TypeId", "") == "Part::Feature"]
        if len(features) != expected_components:
            raise RuntimeError(
                f"saved document contains {len(features)} source features; expected {expected_components}"
            )
        invalid = [
            obj.Label
            for obj in features
            if obj.Shape.isNull() or not obj.Shape.isValid()
        ]
        if invalid:
            raise RuntimeError("saved document contains invalid native shapes: " + "; ".join(invalid))
        return len(features), sum(len(obj.Shape.Solids) for obj in features)
    finally:
        App.closeDocument(doc.Name)


def _station_clearance_clash_checks(features_by_label: dict[str, object]) -> list[str]:
    """Run native Boolean clashes for fixed station items near each envelope."""

    checks: list[str] = []
    cases = (
        (
            "Ground-station tangent kinematic envelope",
            ("Ground-station +Y guideway edge", "Ground-station -Y guideway edge", "Ground-station +Y standard solar canopy", "Ground-station -Y standard solar canopy"),
        ),
        (
            "Elevated-station tangent kinematic envelope",
            ("Elevated-station +Y platform run", "Elevated-station -Y platform run", "Elevated-station +Y standard solar canopy", "Elevated-station -Y standard solar canopy", "60 m project-specific elevated station deck"),
        ),
    )
    for envelope_label, fixed_prefixes in cases:
        envelope = features_by_label[envelope_label]
        for label, fixed in features_by_label.items():
            if not label.startswith(fixed_prefixes):
                continue
            common_volume = envelope.Shape.common(fixed.Shape).Volume
            if common_volume > 1e-3:
                raise RuntimeError(
                    f"station clearance clash: {envelope_label!r} intersects {label!r} "
                    f"by {common_volume:.3f} mm^3"
                )
            checks.append(f"PASS — {envelope_label} clears {label}")
    return checks


def build(path: Path) -> tuple[int, int]:
    """Build, validate, and save the integration document.

    Returns ``(component_count, solid_count)`` for command-line reporting.
    """

    checks = assert_integration_checks()
    components = integration_components()
    doc = App.newDocument("OSRCivilSystemsIntegrationTest")
    doc.Label = "OSR civil systems integration test site"
    root = doc.addObject("App::Part", "IntegrationTestSite")
    root.Label = "Civil systems integration test site (not an operational alignment)"

    notes = doc.addObject("App::FeaturePython", "IntegrationReviewNotes")
    notes.Label = "Integration test scope and results"
    notes.addProperty("App::PropertyString", "DesignStatus", "Review")
    notes.DesignStatus = "Interface-review example; not a released structural or operational design"
    notes.addProperty("App::PropertyString", "GeometryAuthority", "Review")
    notes.GeometryAuthority = "Canonical osr_mech source geometry with explicit integration placements"
    notes.addProperty("App::PropertyString", "TwinSchema", "Digital twin")
    notes.TwinSchema = DIGITAL_TWIN_SCHEMA
    notes.addProperty("App::PropertyString", "TwinSnapshot", "Digital twin")
    notes.TwinSnapshot = "OSR-DT-DESIGN-REFERENCE-001"
    notes.addProperty("App::PropertyString", "TwinManifest", "Digital twin")
    notes.TwinManifest = path.with_suffix(".json").name
    notes.addProperty("App::PropertyInteger", "ComponentCount", "Review")
    notes.ComponentCount = len(components)
    notes.addProperty("App::PropertyStringList", "PassedInterfaceChecks", "Review")
    notes.PassedInterfaceChecks = [f"PASS — {check.name}: {check.detail}" for check in checks]
    notes.addProperty("App::PropertyString", "Limitations", "Review")
    notes.Limitations = (
        "Four separated review zones; no vertical transition alignment. The station deck is a project-specific "
        "coordination envelope requiring structural, seismic, bearing, erection, and geotechnical release."
    )
    root.addObject(notes)

    zone_groups: dict[str, object] = {}
    for zone in sorted({component.zone for component in components}):
        group = doc.addObject("App::DocumentObjectGroup", _safe_name(zone))
        group.Label = zone
        group.addProperty("App::PropertyString", "AssetId", "Digital twin")
        group.AssetId = ZONE_ASSET_IDS[zone]
        group.addProperty("App::PropertyString", "AssetClass", "Digital twin")
        group.AssetClass = "digital-twin.zone"
        root.addObject(group)
        zone_groups[zone] = group

    solid_count = 0
    invalid: list[str] = []
    features_by_label: dict[str, object] = {}
    source_shape_cache: dict[str, object] = {}
    for index, component in enumerate(components, start=1):
        base_shape = source_shape_cache.get(component.source)
        if base_shape is None:
            base_shape = to_freecad_shape(component.builder(), clean=False)
            if base_shape is not None:
                source_shape_cache[component.source] = base_shape
        if base_shape is None or base_shape.isNull():
            invalid.append(f"{component.label}: null shape")
            continue
        shape = base_shape.copy()
        if component.rotation_z_deg:
            shape.rotate(App.Vector(0.0, 0.0, 0.0), App.Vector(0.0, 0.0, 1.0), component.rotation_z_deg)
        if component.translation_mm != (0.0, 0.0, 0.0):
            shape.translate(App.Vector(*component.translation_mm))
        if not shape.isValid():
            invalid.append(f"{component.label}: invalid shape")
        solid_count += len(shape.Solids)

        feature = doc.addObject(
            "Part::Feature",
            f"C{index:03d}_{_safe_name(component.label)}",
        )
        feature.Label = component.label
        feature.Shape = shape
        feature.addProperty("App::PropertyString", "SourceGeometry", "OSR integration")
        feature.SourceGeometry = component.source
        feature.addProperty("App::PropertyString", "IntegrationZone", "OSR integration")
        feature.IntegrationZone = component.zone
        feature.addProperty("App::PropertyString", "InterfaceStatus", "OSR integration")
        feature.InterfaceStatus = "Placed by the checked civil_systems_integration manifest"
        feature.addProperty("App::PropertyString", "AssetId", "Digital twin")
        feature.AssetId = asset_id_for_component(component)
        feature.addProperty("App::PropertyString", "AssetClass", "Digital twin")
        feature.AssetClass = asset_class_for_component(component)
        feature.addProperty("App::PropertyString", "ParentAssetId", "Digital twin")
        feature.ParentAssetId = ZONE_ASSET_IDS[component.zone]
        feature.addProperty("App::PropertyString", "OperationalStateJson", "Digital twin")
        feature.OperationalStateJson = json.dumps(
            operational_state_for_component(component), sort_keys=True, separators=(",", ":")
        )
        feature.addProperty("App::PropertyString", "GeometryRole", "Digital twin")
        feature.GeometryRole = (
            "physical plus interface/reservation overlays"
            if component.zone == "05 Rolling stock"
            else "physical review geometry"
        )
        view = getattr(feature, "ViewObject", None)
        if view is not None:
            view.ShapeColor = ZONE_COLOURS[component.zone]
            view.LineColor = (0.18, 0.20, 0.22)
            view.DisplayMode = "Flat Lines"
            if component.transparency:
                view.Transparency = component.transparency
                view.ShapeColor = (0.95, 0.35, 0.22)
        zone_groups[component.zone].addObject(feature)
        features_by_label[component.label] = feature

    if invalid:
        App.closeDocument(doc.Name)
        raise RuntimeError("FreeCAD integration geometry validation failed: " + "; ".join(invalid))

    clearance_checks = _station_clearance_clash_checks(features_by_label)
    notes.addProperty("App::PropertyStringList", "PassedNativeClashChecks", "Review")
    notes.PassedNativeClashChecks = clearance_checks

    notes.addProperty("App::PropertyInteger", "SolidCount", "Review")
    notes.SolidCount = solid_count
    notes.addProperty("App::PropertyBool", "AllNativeShapesValid", "Review")
    notes.AllNativeShapesValid = True
    doc.recompute()
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveAs(str(path))
    App.closeDocument(doc.Name)
    persisted_components, persisted_solids = validate_saved_document(path, len(components))
    if persisted_solids != solid_count:
        raise RuntimeError(
            f"saved document contains {persisted_solids} solids; generated document contained {solid_count}"
        )
    write_digital_twin_manifest(
        path.with_suffix(".json"),
        model_path=path,
        native_clash_checks=tuple(clearance_checks),
    )
    return persisted_components, persisted_solids


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=_catalog_root() / "civil-systems-integration-test.FCStd",
    )
    args = parser.parse_args(argv)
    component_count, solid_count = build(args.out)
    print(
        f"Wrote {args.out} with {component_count} checked components and "
        f"{solid_count} valid native solids"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
