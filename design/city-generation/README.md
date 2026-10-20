# City Generation

This Python package owns the deterministic geospatial side of city generation:
OSM acquisition and caching, demand/cost/buildability/water rasters,
source-locked open-DEM elevation and terrain slope, batch catalogue generation,
station and line planning, and simulator-scenario emission. Rust routing and
design crates consume its outputs.

| Package | Responsibility |
|---|---|
| `osr_osm` | OSM/Geofabrik acquisition with a local cache |
| `osr_geo` | Demand, cost, buildability, water and open-terrain raster preparation |
| `osr_batch` | Catalogue batch import and regeneration |
| `osr_planner` | Lines, stations, anchors and deterministic network synthesis |
| `osr_scenario` | City design to simulation/finance/README outputs |

After using the root setup instructions, test this package with:

```bash
pytest design/city-generation/tests -q
```

Editable inputs live in [`../../cities/workspaces/`](../../cities/workspaces/README.md);
published results live in [`../../cities/catalogue/`](../../cities/catalogue/README.md).

The current package pipeline preserves adopted layouts during ordinary refreshes.
New cities and explicit `--resynthesise-design` runs also execute
`tools/automation/correct-city-network.py` after the core planner. It retains
source corridor shapes instead of forcing radial core chords, preserves selected
residential stop cells, and joins disconnected route components with bounded
land/water/terrain-constrained extensions or continuous diversions. Small raster
knots have a 200 m total removal bound per line; any wider city-specific scope
requires a named line and recorded basis in `network-layout-policy.toml`.

Correction inputs, routing costs, population pixels and OSM demand anchors are
retained with hashes. The raster CLI reuses a matching, checked city population
crop before downloading another whole-country raster. Its nearest-pixel values
are a relative routing index; resident coverage uses the original native pixels.
The independent `audit-city-geography.py` checks the actual regenerated geometry
and grouped platforms, including networks without rings, disconnected components
and self-intersections. A geometric crossing remains a proposed interchange;
walking access, levels, property and engineering acceptance need separate evidence.

After changing a controlled route, regenerate its stations/maps and downstream
service, civil, energy and cost evidence. The pipeline reimports building and
terrain evidence when its retained corridor hash differs. The named-city batch
can be run with:

```bash
.venv/bin/python tools/automation/generate-city-packages-fast.py \
  --only kisangani,lubumbashi,garissa --resynthesise-design --jobs 2
```
