# Viaduct building, support and terrain clearance

**Status: controlled planning screen; physical release blocked.** Straight
horizontal routes can overfly low buildings only with a verified vertical
alignment and property/air rights. Elevation does not remove a tall obstacle
or provide a place to build a pier.

`tools/automation/audit-viaduct-clearance.py --all --retain-inputs` retains
source footprints near the actual full-resolution corridor and any available
height tags and terrain. `--all --check` repeats the calculation offline and
rejects altered sources or stale corridor evidence. Every city's
`engineering/clearance/README.md` reports beam/building, support/foundation and
terrain findings separately; the compressed register records actual chainages.
Unknown heights, omitted footprints, invalid geometry, missing terrain,
utilities and property approvals remain unresolved even if a reference screen
finds no collision. These reports do not alter the accepted scenario or prices.

The reference swept envelope includes both tracks, deck/walkways and a lateral
allowance. A building below a provisional soffit is a conditional overflight,
not a released design. Each pier's entire foundation envelope is tested
separately. A terrain crest is tested against the straight beam between its
supports; provisional support elevations are checked for excessive railway
grade. SRTM-derived tiles can contain surface/roof/canopy returns and must not
be represented as a precise bare-earth survey.

The current screen uses these explicit planning assumptions:

| Item | Assumption |
|---|---:|
| Twin-track structure/walkway envelope | 9.0 m |
| Extra lateral building allowance | 2.0 m each side |
| Foundation reference radius / setback | 3.0 m / 2.0 m |
| Rail height above support ground | 12.0 m |
| Conservative rail-to-soffit depth allowance | 1.6 m |
| Minimum provisional roof-to-soffit allowance | 2.0 m |
| Pi25 / Pi20 reference span | 25 m / 20 m |
| Reference maximum gradient | 3.5% |

The Pi20/Pi25 bare structural section is 1.155 m deep in
`design/component-catalogue/src/osr_mech/civil/decked_pi.py`. The 1.6 m
rail-to-soffit screening allowance leaves 0.445 m for the unverified track/rail
stack. Special U/box/crossing products need their own supplier geometry; this
Pi reference cannot establish their clearance.

These values require project approval and supplier/site design. They are not
deployment-country statutory clearances. Building storeys times 3.5 m provide
an explicitly uncertain estimate only; they do not replace a height survey.

To resolve a conflict, reroute or secure an approved property solution; raise
the railway with grade-compliant approaches and revised structure costs; move
support lines using verified Pi20/Pi25 spans; change independently checked
foundation/cap arrangements; or release a project-specific crossing. The
catalogue contains no ordinary 30 m full-span beam. Boundary and special span
layouts remain unresolved until independently designed.

Release requires a surveyed building/roof/plant and ground model, longitudinal
and cross-section profiles, utilities and protected zones, property/air rights,
fire and rescue access, flood levels, vertical curves, railway/bridge movement,
pile-group and cap layout, temporary works and each transport/erection stage.
Any adopted geometry change requires regeneration of stations, quantities,
costs, schedule, financial cash flows and native service evidence.

OSM height tags and Overture building/part height fields can supplement
footprints, but neither source establishes mapping completeness. See the
[OSM height definition](https://wiki.openstreetmap.org/wiki/Key:height),
[Overture building documentation](https://docs.overturemaps.org/guides/buildings/)
and [Terrain Tiles source](https://registry.opendata.aws/terrain-tiles/).
