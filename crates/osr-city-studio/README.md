# osr-city-studio

Rust compiler, validator, local HTTP service, and embedded browser interface
for Git-backed OSR city projects.

The crate deliberately operates above the safety-critical control stack. It
creates design and service-planning candidates; it cannot issue operational
movement or route-control commands.

Run the Samawah vertical slice from the repository root:

    cargo run -p osr-city-studio -- serve

The interface can create/move/retire manual stations, create complete manual
lines from two endpoints using locked demand/buildability surfaces or an
explicit direct chord, edit local alignment controls, plan service by
line/day/time over an offline GIS canvas with 16 content-hashed layers,
pan/zoom, visibility/opacity controls and feature inspection, and
adjust every time-window headway for one line or every route in
an atomic day-type transaction, copy a complete plan between day types,
author period-specific origin–destination flows, screen them against the
conservative scheduled capacity bottleneck, and edit or remove those flows,
edit project-level civil construction intent, persist accepted per-line IFC
survey/map conversions, and inspect derived thermal-unit, deck-gap and bearing quantities,
regenerate GIS and simulator inputs, and compare the working
candidate with immutable Git revision records. Its engineering hub runs only
allowlisted field-evidence, GIS, simulator, alignment-exchange and civil-BIM
adapters and persists their progress, logs, exit state, and immutable artifact copies. The field-evidence
adapter also exposes control through per-asset structural-release readiness without
claiming missing field data or approvals. The civil BIM
adapter emits an IFC4.3 rail federation, object index, quantities, provenance,
19 reusable source-recipe component types, three source-backed material
families, one native section profile driving 32 rail extrusions, two typed
`IfcVehicle/ROLLINGSTOCK` trainsets with standard measured base quantities,
a linked construction sequence that separates 134 physical outputs from 45
virtual review interfaces, 36 native typed bridge bearings and explicit
virtual foundation/jacking interfaces, 27 native support connections with 60
bearing realizations, one internal classification with 15
references covering all assets, five native coordination groups, six native
functional systems (three specialized as `IfcBuiltSystem`), seven
system-to-railway-part references,
four native presentation layers, nine native interface constraints with six
numeric `IfcMetric` benchmarks, three qualitative-only gates, and 107
scoped project/asset/group/system evidence links,
16 native property/quantity dictionaries with 99 typed fields,
native horizontal/vertical planning alignment segments and stationing,
one native USD schedule of three generated planning rates, 15 hash-locked native
source documents including a link to all nine objectives and six metrics, a
machine-readable register of nine external engineering decisions, IDS audit,
and BCF 3.0 release issues for Bonsai.
The integrated evidence viewer
re-verifies each hash before plotting GeoJSON, alignment JSON, civil IFC object
envelopes with object picking, asset-class inheritance, review-group and
functional-system membership, interface-constraint evidence,
property-template applicability and definition linkage,
alignment layout, stationing, and unresolved cant/transition evidence,
planning-rate provenance, quantity drivers, and no-estimate boundaries,
source-document records and hashes, IDS
specifications, BCF topics, LandXML, railML,
stakeout CSV, or simulation results.
The civil viewer joins the verified IFC object index with its verified 4D task
sequence, supporting view rotation, presentation-layer, coordination-group, and
functional-system visibility, construction-stage scrubbing/playback,
task/QA-hold context, and stable object picking for BCF.

BCF decisions are saved to project intent and included in Git revision hashes;
immutable job evidence is never edited in place. Resolution and closure require
recorded evidence and a reviewer before a regenerated BCF can carry that state.
New topics can be authored from one or more searched/selected IFC assets; content-derived issue,
topic, and viewpoint IDs keep repeated builds and Git review deterministic.
Materialized revisions can also receive append-only approval or
changes-requested records with a reviewer, role, date, rationale, and review/PR
reference. These records live in project TOML but remain outside the design
hash, so approving an immutable revision cannot create a circular new revision.

Demand periods and OD flows live in `demand/od-matrix.toml`. Flow IDs are
derived from period/origin/destination identity, capacity screens are rebuilt
from the corresponding line/day/time service windows, and both intent and
metrics participate in deterministic revision hashes and semantic comparison.
This is an indicative planning screen, not observed passenger data or a
passenger-assignment model.

Civil settings live in `[civil]` in `project.osr.toml`. The API and GUI reject
values outside the controlled product family before atomically persisting the
standard span, expansion-unit length, reinforced-soil height, slipform/ST6
methods, mould-cycle target and road crossing-comparison rule. Optional
`[[civil.ifc_georeferencing]]` records bind a single accepted EPSG/map
conversion and evidence source to a stable line ID. They participate in
revision hashes and semantic comparison; the civil job passes only the record
for its selected line to the IFC exporter.

Run the complete browser and cross-GUI acceptance suite with:

    npm run test:frontend

Tests use disposable City Studio projects and isolated SQLite databases; the
committed Samawah intent is never edited.

See the [City Studio guide](../../docs/city-studio.md) and
[RFC 0031](../../docs/rfcs/0031-city-studio-git-revisions.md).
