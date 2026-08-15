# Stations

This folder contains station envelope and drawing-register material.
The default architecture is a prefab steel portal frame with a solar
canopy, platform edge systems, flat ground-level passenger slabs, and
minimal station-building scope. Overbridges, lifts, and stairs are
reserved for elevated/stacked sites or local road barriers.

## Packages

| Package | Scope |
|---|---|
| [`standard-archetype/`](standard-archetype/) | Shared `standard` station archetype envelope, canopy, accessibility, services, compliance, and drawing register |
| [`../../mechanical-py/catalog/buildable-stations/`](../../mechanical-py/catalog/buildable-stations/) | Generated EBOM/MBOM and matched assembly travelers for every station catalogue entry |

## FreeCAD Station Scene Renders

These planning-review renders show the station access assumptions in
context with ballastless track and driverless rolling stock.

| At-grade side-platform station | Elevated side-platform station | Elevated interchange station |
|---|---|---|
| ![At-grade side-platform station with ballastless track and driverless train](../screenshots/stations/freecad-at-grade-station-track-train.png) | ![Elevated side-platform station with ballastless track and driverless train](../screenshots/stations/freecad-elevated-station-track-train.png) | ![Elevated interchange station with stacked tracks and driverless trains](../screenshots/stations/freecad-elevated-interchange-track-train.png) |

## Related Artifacts

| Artifact | Location |
|---|---|
| Station canopy CAD source | [`../../mechanical-py/src/osr_mech/station/`](../../mechanical-py/src/osr_mech/station/) |
| Generated station FreeCAD scene document | [`../../mechanical-py/catalog/freecad/station-scenes.FCStd`](../../mechanical-py/catalog/freecad/station-scenes.FCStd) |
| Generated station FreeCAD screenshots | [`../screenshots/stations/`](../screenshots/stations/) |
| Station scene generation script | [`../../mechanical-py/scripts/freecad_station_scenes.sh`](../../mechanical-py/scripts/freecad_station_scenes.sh) |
| Station BOM/traveler generator | [`../../scripts/buildable-stations.sh`](../../scripts/buildable-stations.sh) |
| Generated per-archetype BOMs | `build/bom/stations/` after running the generator |
| Station design RFC | [`../rfcs/0010-station-design-standard.md`](../rfcs/0010-station-design-standard.md) |
| Rapid implementation and recycled materials review | [`../civil/rapid-implementation-materials-review.md`](../civil/rapid-implementation-materials-review.md) |
