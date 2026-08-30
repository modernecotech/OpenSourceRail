# City Generation

This Python package owns the deterministic geospatial side of city generation:
OSM acquisition and caching, demand/cost/buildability rasters, batch catalogue
generation, station and line planning, and simulator-scenario emission. Rust
routing and design crates consume its outputs.

| Package | Responsibility |
|---|---|
| `osr_osm` | OSM/Geofabrik acquisition with a local cache |
| `osr_geo` | Demand, cost and buildability raster preparation |
| `osr_batch` | Catalogue batch import and regeneration |
| `osr_planner` | Lines, stations, anchors and deterministic network synthesis |
| `osr_scenario` | City design to simulation/finance/README outputs |

After using the root setup instructions, test this package with:

```bash
pytest design/city-generation/tests -q
```

Editable inputs live in [`../../cities/workspaces/`](../../cities/workspaces/README.md);
published results live in [`../../cities/catalogue/`](../../cities/catalogue/README.md).
