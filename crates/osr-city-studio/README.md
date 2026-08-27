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
line/day/time, adjust every time-window headway in bulk, copy a complete plan
between day types, regenerate GIS and simulator inputs, and compare the working
candidate with immutable Git revision records. Its engineering hub runs only
allowlisted GIS, simulator, and alignment-exchange adapters and persists their
progress, logs, exit state, and immutable artifact copies. The civil BIM
adapter emits an IFC4.3 rail federation, object index, quantities, provenance,
linked construction sequence, IDS audit, and BCF 3.0 release issues for Bonsai.
The integrated evidence viewer
re-verifies each hash before plotting GeoJSON, alignment JSON, civil IFC object
envelopes with object picking, IDS specifications, BCF topics, LandXML, railML,
stakeout CSV, or simulation results.

BCF decisions are saved to project intent and included in Git revision hashes;
immutable job evidence is never edited in place. Resolution and closure require
recorded evidence and a reviewer before a regenerated BCF can carry that state.
New topics can be authored from one or more searched/selected IFC assets; content-derived issue,
topic, and viewpoint IDs keep repeated builds and Git review deterministic.

Run the complete isolated GUI and restart-persistence acceptance suite with:

    node scripts/test-city-studio-gui.mjs

The report and full-page browser capture are written under
`build/gui-acceptance/`; the test fixture is removed and the committed Samawah
intent is never edited.

See the [City Studio guide](../../docs/city-studio/README.md) and
[RFC 0031](../../docs/rfcs/0031-city-studio-git-revisions.md).
