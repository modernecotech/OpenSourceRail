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
[`docs/rolling-stock/light-metro-3car/README.md`](../../../docs/rolling-stock/light-metro-3car/README.md#freecad-assembly-and-fea-screenshot-review)
and [`docs/stations/README.md`](../../../docs/stations/README.md#freecad-station-scene-renders).
The scripts below replace their stable output filenames on each run, so
the README screenshots and `.FCStd` links always point at the latest
generated review set.

## Add-on and Render Toolchain

The local FreeCAD runtime checked for this package is the
`org.freecad.FreeCAD` Flatpak at FreeCAD 1.1.3. The useful additional
modules installed into its user profile are:

| Capability | Installed tool | Current use |
|---|---|---|
| Assembly review | FreeCAD 1.1 built-in Assembly, Assembly4, A2plus | Existing generated review states remain source-driven; Assembly4/A2plus are available for GUI datum, constraint, and kinematic inspection experiments |
| Structural testing | FreeCAD FEM plus CalculiX | Already used for chassis, bogie, body, and train-to-train joint screening cases in [`../fea/`](../fea/) |
| Mould/manufacturing checks | DFM workbench with `OCP`, `vtk`, and `gmsh` in FreeCAD's Flatpak Python | Available for draft, undercut, wall/thickness, bridge-span, and process checks on moulded GFRP/end-cowl candidates; not yet a release gate |
| High-quality images | Render workbench plus Blender 5.2 Flatpak/Cycles | `--high-quality-renders` exports local STL render meshes and writes large clay-render PNGs under `docs/screenshots/freecad/` |

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
scripts/freecad-generate.sh --models --assemblies --fem --screenshots --station-scenes --high-quality-renders
```

The lower-level package launchers are still available when iterating on
one document:

```bash
scripts/freecad_trainset.sh --family light-metro-3car
scripts/freecad_assembly_review.sh
scripts/freecad_fea.sh
scripts/freecad_screenshots.sh
scripts/freecad_station_scenes.sh
scripts/freecad_catalog.sh
scripts/freecad_mesh_exports.sh
scripts/blender_freecad_renders.sh
```

The repository contains no Build123d implementation or dependency. The
portable `osr_mech.cad` layer remains as the tested parametric source so
geometry can be checked without FreeCAD; the documents above are the
native FreeCAD replacement and review handoff.

The high-quality render path writes transient STL files to
`mechanical-py/catalog/render-meshes/`. That directory is intentionally
ignored because it is large and fully reproducible from the tracked
FreeCAD documents and render scripts.
