# Stations

This folder is the station front door. The controlled source now generates
positive-volume FreeCAD and IFC4.3 assemblies for all seven station archetypes;
site coordinates, surveys, calculations and authority approval remain external
release gates.
The default architecture is a prefab steel portal frame with a solar
canopy, platform edge systems, flat ground-level passenger slabs, and
minimal station-building scope. Overbridges, lifts, and stairs are
reserved for elevated/stacked sites or local road barriers.

## Packages

| Package | Scope |
|---|---|
| [`standard-archetype/`](standard-archetype/) | Shared `standard` station archetype envelope, canopy, accessibility, services, compliance, and drawing register |
| [`../../design/component-catalogue/catalog/buildable-stations/`](../../design/component-catalogue/catalog/buildable-stations/) | Generated EBOM/MBOM and matched assembly travelers for every station catalogue entry |
| [`../../design/component-catalogue/models/cad/stations/`](../../design/component-catalogue/models/cad/stations/) | Native FreeCAD assemblies for halt, standard, major, two interchange forms, terminal and depot-terminal |
| [`../../engineering/models/bim/reference/stations/`](../../engineering/models/bim/reference/stations/) | Matching geometric IFC4.3 assemblies plus deterministic validation summary |
| [`../../engineering/models/model-coverage.md`](../../engineering/models/model-coverage.md) | Product-by-product geometry fidelity and release-evidence boundary |

## FreeCAD Station Scene Renders

These planning-review renders show the station access assumptions in
context with ballastless track and driverless rolling stock.

| At-grade side-platform station | Elevated side-platform station | Elevated interchange station |
|---|---|---|
| ![At-grade side-platform station with ballastless track and driverless train](../screenshots/stations/freecad-at-grade-station-track-train.png) | ![Elevated side-platform station with ballastless track and driverless train](../screenshots/stations/freecad-elevated-station-track-train.png) | ![Elevated interchange station with stacked tracks and driverless trains](../screenshots/stations/freecad-elevated-interchange-track-train.png) |

## Related Artifacts

| Artifact | Location |
|---|---|
| Station canopy CAD source | [`../../design/component-catalogue/src/osr_mech/station/`](../../design/component-catalogue/src/osr_mech/station/) |
| Generated station FreeCAD scene document | [`../../design/component-catalogue/models/cad/station-scenes.FCStd`](../../design/component-catalogue/models/cad/station-scenes.FCStd) |
| Generated station FreeCAD screenshots | [`../screenshots/stations/`](../screenshots/stations/) |
| Station scene generation script | [`../../design/component-catalogue/scripts/freecad_station_scenes.sh`](../../design/component-catalogue/scripts/freecad_station_scenes.sh) |
| Station BOM/traveler generator | [`../../tools/automation/buildable-stations.sh`](../../tools/automation/buildable-stations.sh) |
| All-variant FreeCAD generator | [`../../design/component-catalogue/scripts/freecad_station_library.sh`](../../design/component-catalogue/scripts/freecad_station_library.sh) |
| All-variant IFC generator | [`../../engineering/interchange/station_ifc.py`](../../engineering/interchange/station_ifc.py) |
| Generated per-archetype BOMs | `build/bom/stations/` after running the generator |
| Station design RFC | [`../rfcs/0010-station-design-standard.md`](../rfcs/0010-station-design-standard.md) |
| Rapid implementation and recycled materials review | [`../civil/rapid-implementation-materials-review.md`](../civil/rapid-implementation-materials-review.md) |
