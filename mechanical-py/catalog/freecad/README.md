# FreeCAD Review Assemblies

This folder contains `.FCStd` review assemblies generated from the STEP
catalogue. The build123d source under `../../src/osr_mech/` remains the
authoritative geometry.

## Documents

| File | Purpose |
|---|---|
| [`trainset-light-metro-3car.FCStd`](trainset-light-metro-3car.FCStd) | Full light-metro trainset review assembly imported from generated STEP artifacts |
| [`chassis-bogie-assembly-states.FCStd`](chassis-bogie-assembly-states.FCStd) | Chassis and bogie connector review with assembled and exploded state groups |
| [`full-body-assembly-states.FCStd`](full-body-assembly-states.FCStd) | Body frame, roof, windows, doors, floor, battery, bench, HVAC, lighting, and sensor attachment review states |
| [`fea-screening-models.FCStd`](fea-screening-models.FCStd) | Visual FreeCAD document for the CalculiX screening models and support/load markers |
| [`assembly-geometry-review.md`](assembly-geometry-review.md) | Geometry-review notes for assembled and exploded FreeCAD documents |

The matching captured review images are documented in
[`docs/rolling-stock/light-metro-3car/README.md`](../../../docs/rolling-stock/light-metro-3car/README.md#freecad-assembly-and-fea-screenshot-review).
The scripts below replace their stable output filenames on each run, so
the README screenshots and `.FCStd` links always point at the latest
generated review set.

## Regenerate

```bash
scripts/freecad_trainset.sh --family light-metro-3car
scripts/freecad_assembly_review.sh
scripts/freecad_fea.sh
scripts/freecad_screenshots.sh
```
