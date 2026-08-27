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
line/day/time, adjust every time-window headway for one line or every route in
an atomic day-type transaction, copy a complete plan between day types,
author period-specific origin–destination flows, screen them against the
conservative scheduled capacity bottleneck, and edit or remove those flows,
edit project-level civil construction intent and inspect derived thermal-unit,
deck-gap and bearing quantities,
regenerate GIS and simulator inputs, and compare the working
candidate with immutable Git revision records. Its engineering hub runs only
allowlisted GIS, simulator, and alignment-exchange adapters and persists their
progress, logs, exit state, and immutable artifact copies. The civil BIM
adapter emits an IFC4.3 rail federation, object index, quantities, provenance,
linked construction sequence, IDS audit, and BCF 3.0 release issues for Bonsai.
The integrated evidence viewer
re-verifies each hash before plotting GeoJSON, alignment JSON, civil IFC object
envelopes with object picking, IDS specifications, BCF topics, LandXML, railML,
stakeout CSV, or simulation results.
The civil viewer joins the verified IFC object index with its verified 4D task
sequence, supporting view rotation, discipline visibility, construction-stage
scrubbing/playback, task/QA-hold context, and stable object picking for BCF.

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
methods, mould-cycle target and road crossing-comparison rule.

Run the complete isolated GUI and restart-persistence acceptance suite with:

    node scripts/test-city-studio-gui.mjs

The report and full-page browser capture are written under
`build/gui-acceptance/`; the test fixture is removed and the committed Samawah
intent is never edited.

See the [City Studio guide](../../docs/city-studio/README.md) and
[RFC 0031](../../docs/rfcs/0031-city-studio-git-revisions.md).
