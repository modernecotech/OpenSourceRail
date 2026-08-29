# OSR City Projects

This directory contains the small, Git-reviewable source packages used by OSR
City Studio. Generated catalogue outputs remain under designs/.

Every project pins its input design/GIS/scenario bytes, records manual network
intent separately from generator output, defines weekly service plans, and can
materialize content-addressed revision records for pull-request review.
Manual lines, stations, and alignment controls live in
`network/overrides.toml`; adding or retiring one therefore remains an ordinary,
reviewable Git diff. New-line day-type plans are stored beside the other
services in `services/service-plan.toml`.

Samawah also commits a compact planning raster under `routing/`. Cost, demand,
buildability, anchors, and derivation provenance are independently SHA-256
locked so demand-aware routes are reproducible in a fresh clone.

Start with the [Samawah project](samawah/project.osr.toml) and the
[City Studio guide](../docs/city-studio.md).
