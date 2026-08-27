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
line/day/time, regenerate GIS and simulator inputs, and compare the working
candidate with immutable Git revision records. Its engineering hub runs only
allowlisted GIS, simulator, and alignment-exchange adapters and persists their
progress, logs, exit state, and immutable artifact copies. The civil BIM
adapter emits an IFC4.3 rail federation, object index, quantities, provenance,
and linked construction sequence for Bonsai. The integrated evidence viewer
re-verifies each hash before plotting GeoJSON, alignment JSON, civil IFC object
envelopes, LandXML, railML, stakeout CSV, or simulation results.

See the [City Studio guide](../../docs/city-studio/README.md) and
[RFC 0031](../../docs/rfcs/0031-city-studio-git-revisions.md).
