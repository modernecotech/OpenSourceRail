# OpenSourceRail changelog

## Unreleased

- Added a deterministic all-variant station systems package: OpenSees canopy
  gravity/uplift, JuPedSim normal/degraded/egress and repeatable-bay SWMM
  drainage, plus tracked EnergyPlus and FDS runs. The adverse enclosed depot
  baselines are retained alongside a passing separated/open energy-compound
  and N+1 cooled-controls screen, with six explicit deployment work packages.
- Extended the one-command optional engineering setup to install checksum-
  verified EnergyPlus 26.1 and FDS 6.11.1 user-locally without editing shell
  startup files; the engineering smoke check now exercises both native solvers.
- Added seven complete station-variant FreeCAD and geometric IFC4.3 assemblies,
  covering all 45 controlled station products with deterministic validation;
  the FreeCAD set now carries 4,324 installed/exploded native shapes, controlled
  interface/datums, compact variant definitions and a bidirectional orphan-ID gate.
- Expanded the LM3 reference library to 523 primitives, detailed door/window,
  bogie, traction, battery and HV interfaces, and added an installed-coordinate
  sidecar with nominal, curve and twist review states.
- Added STEP, DXF inspection and three-view SVG references for all 46 locally
  manufactured LM3 rows, plus a generated CAD/IFC fidelity register.
- Expanded turnout, depot and reusable civil maintenance-interface geometry.

## v0.3.1 — 2026-08-30 — CI correctness patch

Corrects the clean-checkout release gates discovered after v0.3.0: both Python
jobs now share one pinned IFC runtime, generated city acceptance reports link
only to tracked compact artifacts, and Kani CI runs explicit bounded properties
that complete inside its controlled timeout. See the
[v0.3.1 patch notes](docs/release-v0.3.1.md).

## v0.3.0 — 2026-08-30

v0.3 focuses on a credible product boundary and a reproducible integrated
delivery platform. It adds the shared Python runtime/CI path, three-product
maturity model, current standards baseline, safety-controller selection gate,
release-selected Kani workflow, consensus refinement map, corrected halt energy scope,
safer battery-enclosure definition and appropriately qualified economic claims.

See [the concise release notes](docs/release-v0.3.md). Physical first articles,
qualified safety hardware, formal refinement closure, independent assessment
and deployment approval remain open gates rather than release claims.

## v0.2 development baseline

Post-v0.1 development baseline. The repository has moved beyond the
initial publication baseline: it now has a complete, buildable software +
documentation surface, generated design catalogues, mechanical/CAD
evidence, COTS/DIY hardware integration paths, operations material, and
a regulator-facing pre-submission structure for a GoA 4 urban-rail
deployment. What's *not* yet done is everything that requires external
hands — physical pilot build, civil survey, independent assessor review,
regulator engagement, operator validation, and deployment approval.

This file summarises how the repo arrived here and what each
major subsystem is ready for.

## Headline numbers

- **55 Rust crates** with Kani harnesses, proptests, and integration
  tests across the safety-critical software surface.
- **Two Python sidecars**: `design/city-generation` (GIS + network synthesis),
  `design/component-catalogue` (parametric mechanical / civil / station
  source geometry), plus two Python tools. The current audit collects 429
  Python/tool tests across their four suites (428 passing, 1 environment-
  dependent test skipped).
- **Two egui operator GUIs**: `osr-sim-gui` (designer), `osr-occ-gui`
  (dispatcher). Both native + WebAssembly.
- **Thirty RFCs** covering software architecture, rail civil
  engineering, operations, driverless operation, wayside
  intrusion detection, cybersecurity, the operator GUIs, construction
  QA, maintenance scheduling, and manufacturing scheduling.
- Workspace builds are expected to stay warning-free; warnings are
  treated as drift from the v0.2 development baseline.

## What's ready

### Software

- **SIL-4-target onboard chain** — position fusion → ATP → brake +
  derailment + fire + door-control + obstacle-detect (RFC 0015).
  Every SIL-4 evaluator carries Kani bounded-model proofs and
  proptest coverage; GSN safety-case compiler gates CI.
- **SIL-4-target wayside chain** — MA computer on top of Raft-derived
  consensus + point-machine controller + intrusion-detect
  (RFC 0016). Same Kani + proptest + GSN discipline.
- **Two-layer GoA 4 safety envelope** — wayside intrusion gate
  + onboard obstacle detect, both wired into the same brake
  chain, both demonstrable in the sim via scenario fault
  injection.
- **Distributed signalling** — `osr-consensus` designed against the
  TLA+ `SMRaft` spec and differential-tested against an independent Python
  twin; formal refinement remains an open certification gate.
- **Message authentication** — `osr-secbus` (ed25519 on
  `osr-crypto`) plus authenticated consensus proposal/commit paths and
  simulator fault-injection coverage (RFC 0017 v2/v3). Deployment key
  provisioning and production-transport/hardware evidence remain open.
- **Automatic network generation** — OSM → 20 m cost grid →
  Dijkstra → population-tiered multi-line network, scales to
  500-city batches.
- **Two operator GUIs** — see the README screenshots.

### Rail engineering

- **Five trainset families** (urban-shuttle-1car → metro-6car),
  cabless per RFC 0015.
- **Four track-geometry presets** with a machine-readable
  OSR-ALN interchange format, LandXML → OSR-ALN converter, and
  a validator that enforces 8 hard gates + 3 soft gates per
  the format spec.
- **Six station archetypes**; prefab steel-portal + solar-
  canopy, no station building, bolt-together on-site.
- **Three civil classes** (at-grade / elevated / bridge) —
  tunnels explicitly excluded per RFC 0011.
- **Three turnout tangents** covering tram / urban / mainline.
- **Three depot archetypes** with a fleet-sizing formula.
- **Worked OSR-ALN alignment instance** for an earlier Samawah
  generated network (29 km, 22 stations, validator-clean), proving the
  shared civil export/validate workflow rather than a Samawah-specific
  civil standard.

### Operations

- **Operations rulebook** across four shipping role families
  (dispatcher S1–S7, station-staff T1–T5, maintenance M1–M7,
  control-centre C1–C3). Cabbed operation and train-driver procedures
  are outside repository scope.
- **First adoptable product path** — Ops Core + simulator + asset
  register + QA/maintenance/evidence portal for an existing depot,
  workshop, or pilot corridor, explicitly before safety-critical train
  control is deployed.

### Governance and release readiness

- **Top-level contribution and governance docs** now define project
  status, contribution expectations, safety-claim boundaries, decision
  process, release responsibilities, and the current founder-led
  pre-1.0 operating model.
- **Deployment roles page** assigns owner/operator, prime integrator,
  independent safety assessor, insurer, EPC/civil contractor, local
  workshop, hardware integrator, financing entity, and regulator
  responsibilities.
- **v0.2 release pack** identifies release notes, PDF/brochure assets,
  Samawah case-study links, simulator instructions, evidence matrix,
  GitHub metadata, and publication commands.

### Hardware

- **Five host classes** reference-spec'd and assigned controlled service
  manifests: T-ECU/S (safety kernel),
  T-ECU/A (application), T-OBS (obstacle detect, RFC 0015),
  W-SBC (wayside), S-SBC (station / depot). Palette restricted
  to Raspberry Pi + Radxa for domestic procurement.
- **Board-level specs** per class: block diagram, power
  budget, pinouts, connector tables, safety-nets (SIL-4
  target boards only; none is qualification evidence by itself.
- **Pilot COTS/DIY path** per RFC 0019: commodity SBCs,
  Pi Pico 2 boards, sensor modules, relay/HAT modules,
  terminal blocks, DIN-rail enclosures, and prepared image
  flow. KiCad is not a first-pilot prerequisite when no
  custom PCB is used.

### Certification

- **EN 62267 type-certification pre-submission pack** at
  `docs/certification/` covering system description, 24
  safety requirements, 17 hazards across 7 classes, a
  clause-by-clause compliance matrix, and an evidence
  register that links every claim to a concrete artefact.

## What needs external engagement

- **Pilot hardware integration evidence** for the RFC 0019
  COTS/SBC path: exact SKU BOMs, wiring/harness maps, connector
  maps, enclosure/mounting notes, power/thermal margins, SD-card
  image checksums, `osr-selftest` output, safety-net bench tests,
  and commissioning records.
- **Custom-board KiCad + gerbers** only where a deployment chooses
  OSR-specific carrier, power, safety-I/O, or sensor-interface
  boards. All net lists + pinouts + safety-net rules are frozen;
  a KiCad workflow turns those specs into volume-production files.
- **Civil survey** replacing the planning-grade Samawah UTM
  coordinates with real GNSS data.
- **Independent safety-assessor review** of the certification
  pack. Deployment partner's scope.
- **Type-approval submission** to a national safety
  authority. Deployment partner's scope.
- **Practising-operator review** of RFC 0013 — a working
  dispatcher + maintenance foreman red-lining the rule text
  against reality.
- **RFC 0017 deployment closure** — freeze the key registry and secure-
  element provisioning/rotation procedure, then capture production-
  transport and hardware-in-the-loop verification evidence.
- **Revenue operation** — the last item. Requires all of the
  above.

## What this repo is not

- **Not a standards body.** Where good open standards exist
  (GTFS, NeTEx, IEEE 802.1 TSN, EN 50126/8/9, IEC 62443-4-2)
  we adopt them.
- **Not a safety certifier.** The project produces artefacts
  suitable for independent assessment; certification is done
  by national authorities.
- **Not a museum.** We do not aim for plug-in compatibility
  with every legacy vendor protocol. Migration paths are
  scoped; permanent legacy support is not.
- **Not a vendor.** There is no OSR commercial entity. Support
  and deployment are the responsibility of the deployment
  partner.

## How to engage

The project is looking for, in order:

1. **Practising rail operators** to review the RFC 0013
   rulebook and flag the places where real-world procedure
   differs from what we wrote.
2. **Civil engineering firms** in the target deployment
   footprint (MENA, sub-Saharan Africa, South Asia, Latin
   America) to pilot the OSR-ALN converter against a real
   survey.
3. **Pilot integrators and hardware reviewers** to test the RFC 0019
   DIY path against a real bill of materials, wiring maps, enclosures,
   power/thermal margins, and self-test logs. PCB designers remain
   valuable for custom-board deployments and later volume production.
4. **Independent safety assessors** familiar with EN 62267
   GoA 4 and IEC 62443-4-2 to read the `docs/certification/`
   pack and identify gaps we haven't seen.
5. **Contributors** willing to pick an open crate from
   RFC 0005 (cybersecurity consensus integration, full TSN
   transport, CBM backend) or an open RFC follow-up.

File issues with specific disagreements; send pull requests
with tests.

## License

- Software: Apache 2.0.
- Hardware designs: CERN-OHL-S v2.
- Documentation: CC-BY-SA 4.0.

Contribution and governance process is now in
[`CONTRIBUTING.md`](CONTRIBUTING.md) and
[`GOVERNANCE.md`](GOVERNANCE.md). Exact license texts and path-level
applicability are in [`LICENSE.md`](LICENSE.md) and [`LICENSES/`](LICENSES/).

## Milestone version

This repository is now at a **v0.2 development baseline**. There is no
breakage policy yet — the repo is pre-1.0 and interfaces can change.

Remaining v0.2 hardening work is tracked in
[`docs/ROADMAP.md`](docs/ROADMAP.md). Several originally planned
items have already landed after the v0.1 snapshot, including the DIY
electronics cookbook, `osr-selftest`, commercial-tool gap-closing in
`osr-alignment`, turnout/depot/clearance/accessibility CAD, the
crashworthiness scaffold, and the two-track hardware release model.
The remaining high-value v0.2 targets are:

- RFC 0017 deployment evidence — secure-element provisioning,
  production-transport capture, and hardware-in-the-loop verification.
- Pilot hardware integration evidence for the RFC 0019 COTS/SBC path,
  plus KiCad, gerber, board BOM, and assembly outputs where custom
  boards are chosen.
- Rolling-stock production-detail package: supplier-exact envelopes,
  weld maps, tolerance stacks, FEA-ready brackets, and release
  drawings.
- Residual-risk narrative and first external safety/operator review
  feedback incorporated into the certification pack.
