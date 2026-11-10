# Editable city GIS with RustGIS

OpenSourceRail uses **RustGIS 0.5.0** for native city GIS projects and headless
map export. The existing interactive city atlas, SVG maps and calculated service,
fleet, delivery and cost dossiers remain available. QGIS is not required by any
current city generator or by the business-platform artifact reader.

In the local Workbench, select a city and choose **Download editable RustGIS
project and source tables**. Extract the ZIP and open `<city>.rgis` in RustGIS.
The download is bound to the exact displayed city packet. A verified local
planning study exports its own geometry and source base, so repeated native
editing does not revert to the published network.

After editing and saving, choose **Import native GIS edits and recalculate** in
the same city atlas. Name the author and reason, and upload the `.rgis` file.
OSR compares embedded route/station data with the authenticated export, then
uses the existing planning, service, fleet, civil-quantity, cost and delivery
evaluators. The new map, prices and delivery links belong to one revised study;
the original published city remains available. Camera or styling changes alone
create no railway revision or recalculation.

```bash
./osr gis install                         # Verified upstream desktop + CLI binaries
./osr gis audit                           # Version, executable pin and cache location
./osr gis export --city baghdad --preview  # Native project, exact sources and PNG
./osr gis open --city baghdad              # Open a separate editable desktop copy
./osr gis export --all                    # Import, save, reopen and check all 266 cities
./osr gis export --all --output /path/to/retained-gis  # Keep every complete ZIP
./osr gis verify --output /path/to/cache/city/request-hash
./osr gis export-study --study LOCAL_JOB_ID
./osr gis import --city samawah --packet-id DISPLAYED_PACKET_ID --project edited.rgis \
  --actor "Planning author" --reason "Declared route revision" --data-crs EPSG:4326
./osr gis reprice --city samawah --packet-id DISPLAYED_PACKET_ID --project edited.rgis \
  --actor "Planning author" --reason "Declared route revision" --data-crs EPSG:4326 \
  --refreshed-output /path/to/fresh-updated-gis
./osr gis verify-revision --output /path/to/retained-import
```

`reprice --refreshed-output` verifies the retained native edit and its canonical
request, waits for the bounded city study, then exports and verifies a new
RustGIS project bound to that exact completed study. The input
receipt remains in `build/rustgis-imports`; the refreshed editable project is
written beneath the requested fresh directory. A no-op edit does not create a
child study or refreshed export. This returns edited planning geometry and its
recalculated outline costs; it does not establish revised railway physics or
engineering acceptance.

The installer checks the pinned release archive and both executable SHA256s.
Linux x86_64 is the currently tested installation target. It uses about 170 MiB
for the desktop and CLI together, without a Rust compilation or Python GIS
runtime. It adds a desktop menu entry and `.rgis` file association support.
It does not replace existing commands or remove other applications automatically.

## What each city contains

- Native editable geometry and styles, plus portable relative source files.
- The eight existing railway GIS datasets: routes, stations, platforms, original
  access markers, interchanges, civil segments, access connectors and unlocated
  requirements. All-null geometry is correctly imported as a **table**.
- Retained offline roads, buildings, land use, terrain, boundaries, places and
  water context where present, with original attribution and licensing.
- Exact original compressed GeoJSON, atlas packet, city summary and CSV tables
  for costs, finance, line service, stations, energy, local prices, make/buy,
  delivery and workforce. Cost confidence and uncertainty remain unchanged.
- A manifest binding the physical/selection/evaluation identities, original
  bytes, tool/source versions and actual native round-trip checks.
- A hidden `_osr_export_context` table identifying the trusted published seed or
  verified local study. Keep this table unchanged. Older exports without the
  context must be re-exported before using the return path.

Data coordinates are **WGS84 longitude/latitude**. The saved display uses Web
Mercator. Use OSR's declared chainages and quantity models for engineering and
costs; screen distances are not a replacement. Water lines and polygon areas
are separate native layers, and polygon holes stay attached to their polygons.
The adapter does not close open water lines or invent missing site locations.

RustGIS assigns numeric local feature IDs. `_osr_source_index` maps each feature
back to its exact original record and string ID. Nested attributes become JSON
text in native tables; every value is checked after export. Single/multipart
geometry normalisation is permitted only when coordinates and topology agree.
The coordinate comparison tolerance is 10^-12 degrees; this checks digital
interchange and makes no claim about the accuracy of unsurveyed geography.

## Disk, execution and editing

The default cache is `$XDG_CACHE_HOME/opensourcerail/rustgis`, falling back to
`~/.cache/opensourcerail/rustgis`. Successful reproducible ZIPs have a **256 MiB
cache budget**; older ZIPs are evicted and regenerated on demand. Receipts and
native logs remain, as do failed/interrupted inputs and outputs. Use `--output`
to retain every ZIP outside that automatic cache policy. No bulky city exports
need to be checked into Git.

The native RustGIS worker solves no transport physics: it imports geometry, styles,
saves, reopens, exports every layer/table, checks coordinates and attributes,
and optionally renders a PNG. Each native process has a 60 CPU-second, 75
wall-second and 2 GiB address-space limit. The download endpoint permits one
worker and requires loopback client/Host and the exact current city packet.
Plugins, AI, saved credentials and external tiles are not enabled by this adapter.

`open` creates an editable copy under `$XDG_DATA_HOME/opensourcerail/gis` (normally
`~/.local/share/opensourcerail/gis`). Reopening that same copy preserves edits.
Saving the drawing does not automatically reprice or select it. The explicit
import operation submits a typed revision to the same bounded city job service
used by the planning editor. It grants no engineering, manufacturing or
operating approval and performs no business transactions or movement commands.

Editable data are the existing route geometry, route `shape`, `headway_s` and
`design_speed_cap_m_s`, station positions and `dwell_s`. New stations need a new
string `id`, an existing `line_id`, explicit dwell and a null source index.
Retired/merged stations retain their original access-marker consequences.
Stops must lie within the existing 20 mm **digital consistency** tolerance of
their declared polyline; ambiguous intersections need an explicit geometry
revision. This is not a survey-accuracy or physical-acceptance claim. Original
source identities and derived civil/platform/access/cost layers are read-only;
they are regenerated by OSR, never imported as approved evidence.

The importer reads embedded data without executing saved jobs, tasks, plugins,
workspaces or external source paths. Native uploads are bounded at 32 MiB and
retained separately from the 2 MiB canonical city request. Source input,
failures, normalized changes and calculation links remain in
`build/rustgis-imports` under a 256 MiB evidence-store budget. Oversized or
ambiguous revisions fail explicitly; no geometry is silently truncated. The
loopback upload requires matching Host and Origin. See the returned import
receipt for exact candidate/base/source identities and execution status.

Historical QGIS `.qgz` metadata inspection is retained using Python's standard
ZIP/XML readers. No QGIS installation is needed to inspect those archives.
An arbitrary external QGIS project, plugin or processing model is not covered by
this migration; only the repository's actual current city work is covered.

[Upstream release](https://github.com/opengeos/RustGIS/releases/tag/v0.5.0) ·
[Pinned backend](../../engineering/rustgis/backend.json) ·
[City catalogue](../../cities/catalogue/README.md) ·
[Current engineering](../design-engine/current/README.md)
