# Samawah close-station consolidation study

This is a separate, source-bound planning revision for the package-07 body and
the existing 0.4 m/s² comparison policy. It consolidates only two nearby
markers on line 1, then rebinds and deduplicates their references in
`interchange-001`. The source city, selected reference, vehicle body, and
propulsion policy are unchanged. The published city catalogue and its original
calculation remain intact.

The original city evaluation (`0b1715bb…`) reproduced byte-for-byte before the
revision. The two source markers were verified against the exact route
polyline. The new planning marker is the along-route midpoint at chainage
9,339.174 m, with ID `complex-8e5085cf2af63c4ef50ac9f7`. The consolidation
removes the prior 79.977 m separation conflict in this planning scenario.

| Measure | Original scenario | Consolidated scenario |
| --- | ---: | ---: |
| Route length | 57.873 km | 57.873 km |
| Station markers | 26 | 25 |
| Requested boarding faces | 52 | 50 |
| Line 1 conditional one-way time | 2,041.838 s | 1,985.331 s |
| Base conditional fleet | 59 | 59 |
| High conditional fleet | 88 | 87 |
| High counted BOM/process subtotal | $297.136m | $293.759m |

The fleet and running-time values are kinematic planning requests, not a
protected timetable or achieved service. The counted subtotal is not a
delivered or installed project price. All fourteen complete cost scopes and
whole-life NPV remain `null`. Demand/catchment, access and transfer walks,
station footprint, ground, utilities, grade, available propulsion force,
independent braking, charging, thermal duty, detailed civil loads, and the
18-hour staffing roster remain unresolved. The result does not establish
station buildability, safety, accessibility, or a city-wide route selection.

The complete immutable run package is in
[`samawah-station-consolidation/`](samawah-station-consolidation/manifest.json).
It records exact source and input hashes, the successful attempt's logs and
resource use, and hashes of unchanged prior packets. Earlier failed attempts
remain in the private run record. The successful
worker used 6.832 s wall time, 6.859 CPU seconds, and 311,668 KiB maximum RSS
under 60 CPU seconds, 1 GiB address space, and 60 seconds wall time. The source
filesystem was writable; no OS read-only sandbox is claimed. No native GIS,
CAD, or FEM tool ran.

This result improves one local map detail; it does not close the mapped-corridor
release gate.
