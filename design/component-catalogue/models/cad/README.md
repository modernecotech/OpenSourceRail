# FreeCAD Review Assemblies

This folder contains `.FCStd` review assemblies generated directly from
the parametric source under `../../src/osr_mech/`, which remains the
authoritative geometry.

## Documents

| File | Purpose |
|---|---|
| [`trainset-light-metro-3car.FCStd`](trainset-light-metro-3car.FCStd) | Full light-metro trainset review assembly generated from source geometry |
| [`single-car-assembly.FCStd`](single-car-assembly.FCStd) | Corrected urban-shuttle single-car assembly with both bogies on the shared ±6,150 mm chassis datums |
| [`chassis-bogie-assembly-states.FCStd`](chassis-bogie-assembly-states.FCStd) | Chassis and bogie connector review with assembled and exploded state groups |
| [`full-body-assembly-states.FCStd`](full-body-assembly-states.FCStd) | Body frame, roof, windows, doors, floor, battery, bench, HVAC, lighting, and sensor attachment review states |
| [`fea-screening-models.FCStd`](fea-screening-models.FCStd) | Visual FreeCAD document for the expanded CalculiX screening models and support/load markers |
| [`station-scenes.FCStd`](station-scenes.FCStd) | Station, ballastless track, and driverless train review scenes for at-grade, elevated, and elevated interchange configurations |
| [`civil-systems-integration-test.FCStd`](civil-systems-integration-test.FCStd) | Source-driven civil/rolling-stock twin containing a ground station, 1:9 junction, six double-track viaduct spans, an elevated station, and two complete trains |
| [`civil-systems-integration-test.json`](civil-systems-integration-test.json) | Portable twin asset, transform, relationship, state, validation, and FCStd-hash snapshot |
| [`../../../../docs/assets/digital-twin-animation.gif`](../../../../docs/assets/digital-twin-animation.gif) | 32-frame FreeCAD/Coin3D animation of both test-site operating scenes with moving LM3 rolling stock |
| [`native-catalogue-parts.FCStd`](native-catalogue-parts.FCStd) | Native FreeCAD replacements for civil, track, station, depot, and fabrication-template source families |
| [`battery-pack-set.FCStd`](battery-pack-set.FCStd) | Per-car battery-pack source-geometry review document |
| [`car-body-17m.FCStd`](car-body-17m.FCStd) | Canonical car-body source-geometry review document |
| [`motor-bogie.FCStd`](motor-bogie.FCStd) | Powered-bogie source-geometry review document |
| [`trailer-bogie.FCStd`](trailer-bogie.FCStd) | Trailer-bogie source-geometry review document |
| [`raked-sensor-cowl.FCStd`](raked-sensor-cowl.FCStd) | Raked obstacle-sensor end-cowl review document |
| [`platform-at-grade-assembly.FCStd`](platform-at-grade-assembly.FCStd) | At-grade slab, platform edge, and complete track-panel assembly |
| [`platform-elevated-assembly.FCStd`](platform-elevated-assembly.FCStd) | U-girder, elevated deck, and complete track-panel assembly |
| [`station-platform-canopy-assembly.FCStd`](station-platform-canopy-assembly.FCStd) | Platform edge, track, canopy portals, roof, and PV assembly |
| [`assembly-geometry-review.md`](assembly-geometry-review.md) | Geometry-review notes for assembled and exploded FreeCAD documents |

The matching captured review images are documented in
[`docs/rolling-stock/light-metro-3car/README.md`](../../../../docs/rolling-stock/light-metro-3car/README.md#freecad-assembly-and-fea-screenshot-review)
and [`docs/stations/README.md`](../../../../docs/stations/README.md#freecad-station-scene-renders).
The scripts below replace their stable output filenames on each run, so
the README screenshots and `.FCStd` links always point at the latest
generated review set.

## Add-on and Render Toolchain

The supported launcher checks the `org.freecad.FreeCAD` Flatpak and records the
actual runtime in generated evidence. Optional workbenches are review aids;
they do not change the Python geometry or IFC/Bonsai authority boundaries.

| Capability | Installed tool | Current use |
|---|---|---|
| Assembly review | FreeCAD 1.1 built-in Assembly, Assembly4, A2plus | Existing generated review states remain source-driven; Assembly4/A2plus are available for GUI datum, constraint, and kinematic inspection experiments |
| Structural testing | FreeCAD FEM plus CalculiX | Already used for chassis, bogie, body, and train-to-train joint screening cases in [`../../catalog/fea/`](../../catalog/fea/) |
| Mould/manufacturing checks | DFM workbench with `OCP`, `vtk`, and `gmsh` in FreeCAD's Flatpak Python | Available for draft, undercut, wall/thickness, bridge-span, and process checks on moulded GFRP/end-cowl candidates; not yet a release gate |
| High-quality stills | Render workbench plus the optional Blender/Cycles export path | `--high-quality-renders` uses Blender when installed; the GIF path does not require it |

For repeatable repository animation, the selected path is FreeCAD's built-in
Coin3D view renderer plus ImageMagick GIF encoding. The runner checks both
dependencies and operates directly on the generated FCStd review file. Blender's
[Python animation API](https://docs.blender.org/api/dev/info_quickstart.html)
is the stronger future route for cinematic lighting and materials, while
Godot's [glTF/3D scene importer](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/index.html)
is suitable for a user-driven interactive twin. Neither Blender nor Godot is
needed for the tracked GIF. FreeCAD's optional
[Animation workbench](https://www.freecad.org/addons.php?lang=eng) is also not
required because the repository script drives placements and frames directly.

The MBDyn-style multibody dynamics add-ons were reviewed as candidates
for rail dynamic testing, but are not installed as a default repo
dependency because the available public workbench path is not yet a
clean, maintained, headless pipeline for these models. Dynamic release
therefore remains represented here by CalculiX quasi-static structural
screens plus operational/dynamic commissioning plans, not by validated
multibody ride simulation.

## Regenerate

From the repository root, the canonical orchestrator is:

```bash
tools/automation/freecad-generate.sh --models --assemblies --civil-systems --fem --screenshots --station-scenes --digital-twin-animation --high-quality-renders
```

When iterating on one document, run the lower-level package launchers from
`design/component-catalogue/`:

```bash
scripts/freecad_trainset.sh --family light-metro-3car
scripts/freecad_assembly_review.sh
scripts/freecad_fea.sh
scripts/freecad_screenshots.sh
scripts/freecad_station_scenes.sh
scripts/freecad_catalog.sh
scripts/freecad_civil_systems_example.sh
scripts/freecad_digital_twin_animation.sh
scripts/freecad_mesh_exports.sh
scripts/blender_freecad_renders.sh
```

## Civil systems integration test

The integration document is organized into five independently selectable
FreeCAD groups: an at-grade ground station, an at-grade 1:9 junction, viaduct
approaches/substructure, an elevated station, and rolling stock. It assembles
82 placed source components and 13,861 native solids, including 12 U-girders
on nine shared piers, direct-fixation track, platform edge kits, four solar
canopies, translucent controlled kinematic envelopes, and two complete
three-car light-metro trainsets.

Every placed feature carries a stable asset ID, asset class, parent zone,
geometry role, and JSON operational state in its FreeCAD properties. The
paired JSON snapshot records the same 82 assets, five zones, 86 relationships,
two train states, nine interface checks, nine native clearance-clash checks,
and a SHA-256 link back to the exact FCStd artifact. It is suitable for
deterministic design review and as an initial-state handoff to OCC/CBM tooling;
it does not claim to be a live telemetry feed.

Generation stops before saving if any native shape is null or invalid, or if
an interface check fails. The checked datums are pier bearing-to-girder soffit,
viaduct-to-station track support, 350 mm platform height above top of rail, and
75 mm platform clearance from the tangent dynamic envelope; both complete
rolling-stock assemblies must also be present. Open the document's
`IntegrationReviewNotes` object to see the recorded PASS results.

The four zones form a review test site, not an operational alignment. In
particular, no vertical transition is implied between its at-grade and elevated
zones. The wide elevated-station deck is explicitly a project-specific
coordination envelope; structural, seismic, bearing, erection, and geotechnical
design remain release work.

The animated review reopens the unchanged FCStd model for each scene, selects
the relevant integration zones, moves each complete LM3 train along its checked
track Y/Z datum, and computes the axonometric camera from visible source
geometry. FreeCAD/Coin3D renders the PNG frames and ImageMagick encodes the
looping GIF. No FreeCAD animation workbench is required. Regenerate and enforce
the repository's strict sub-20-MB media limit with:

```bash
tools/automation/freecad-generate.sh --digital-twin-animation
```

The repository contains no Build123d implementation or dependency. The
portable `osr_mech.cad` layer remains as the tested parametric source so
geometry can be checked without FreeCAD; the documents above are the
native FreeCAD replacement and review handoff.

The high-quality render path writes transient STL files to
`design/component-catalogue/catalog/render-meshes/`. That directory is intentionally
ignored because it is large and fully reproducible from the tracked
FreeCAD documents and render scripts.
