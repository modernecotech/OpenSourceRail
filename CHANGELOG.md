# OpenSourceRail — milestone 0.1

First publishable snapshot. The repository has a complete,
buildable software + documentation surface for a GoA 4 urban-
rail deployment. What's *not* yet done is everything that
requires external hands — fabrication, civil survey, regulator
engagement, operator review.

This file summarises how the repo arrived here and what each
major subsystem is ready for.

## Headline numbers

- **56 Rust crates**, **747 tests passing, 0 failing** (Kani
  harnesses + proptests + integration tests).
- **Two Python sidecars**: `design-py` (GIS + network synthesis),
  `mechanical-py` (parametric mechanical / civil / station
  components on build123d). 28 Python tests passing.
- **Two egui operator GUIs**: `osr-sim-gui` (designer), `osr-occ-gui`
  (dispatcher). Both native + WebAssembly.
- **Eighteen RFCs** covering software architecture, rail civil
  engineering, operations, driverless operation, wayside
  intrusion detection, cybersecurity, and the operator GUIs.
- **Zero workspace build warnings.**

## What's ready

### Software

- **SIL-4 onboard chain** — position fusion → ATP → brake +
  derailment + fire + door-control + obstacle-detect (RFC 0015).
  Every SIL-4 evaluator carries Kani bounded-model proofs and
  proptest coverage; GSN safety-case compiler gates CI.
- **SIL-4 wayside chain** — MA computer on top of Raft-derived
  consensus + point-machine controller + intrusion-detect
  (RFC 0016). Same Kani + proptest + GSN discipline.
- **Two-layer GoA 4 safety envelope** — wayside intrusion gate
  + onboard obstacle detect, both wired into the same brake
  chain, both demonstrable in the sim via scenario fault
  injection.
- **Distributed signalling** — `osr-consensus` refining the
  TLA+ `SMRaft` spec, differential-tested against an
  independent Python twin.
- **Message authentication** — `osr-secbus` (ed25519 on
  `osr-crypto`) with library-level verification (RFC 0017 v1);
  v2 wiring into the live consensus path is the one
  production-readiness gap on the software side.
- **Automatic network generation** — OSM → 20 m cost grid →
  Dijkstra → 2-line network, scales to 500-city batches.
- **Two operator GUIs** — see the README screenshots.

### Rail engineering

- **Four trainset families** (tram-2car → metro-6car),
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
- **Worked reference alignments** for both Samawah lines
  (29 km, 22 stations, validator-clean).

### Operations

- **Operations rulebook** across four shipping role families
  (dispatcher S1–S7, station-staff T1–T5, maintenance M1–M7,
  control-centre C1–C3), plus a historical driver section
  D1–D8 for legacy GoA 2 fleets. ~170 rules total.

### Hardware

- **Five host classes** fully spec'd: T-ECU/S (safety kernel),
  T-ECU/A (application), T-OBS (obstacle detect, RFC 0015),
  W-SBC (wayside), S-SBC (station / depot). Palette restricted
  to Raspberry Pi + Radxa for domestic procurement.
- **Board-level specs** per class: block diagram, power
  budget, pinouts, connector tables, safety-nets (SIL-4
  boards only).

### Certification

- **EN 62267 type-certification pre-submission pack** at
  `docs/certification/` covering system description, 24
  safety requirements, 17 hazards across 7 classes, a
  clause-by-clause compliance matrix, and an evidence
  register that links every claim to a concrete artefact.

## What needs external engagement

- **KiCad schematic capture + gerbers** for the five v2-spec
  boards. All net lists + pinouts + safety-net rules are
  frozen; someone with a KiCad workflow turns them into
  buildable files. *See RFC 0019 for a DIY module-based
  alternative that bypasses this step entirely for
  first-article deployments.*
- **Civil survey** replacing the planning-grade Samawah UTM
  coordinates with real GNSS data.
- **Independent safety-assessor review** of the certification
  pack. Deployment partner's scope.
- **Type-approval submission** to a national safety
  authority. Deployment partner's scope.
- **Practising-operator review** of RFC 0013 — a working
  dispatcher + maintenance foreman red-lining the rule text
  against reality.
- **RFC 0017 v2** — wire `osr-secbus::verify_signed` into
  the consensus receive path. The library is in tree; the
  plumbing is an afternoon's work but requires a safety-case
  addendum.
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
3. **PCB designers / fabricators** to capture the v2 hardware
   specs into KiCad, or to test the RFC 0019 DIY path against
   a real bill of materials.
4. **Independent safety assessors** familiar with EN 62267
   GoA 4 and IEC 62443-4-2 to read the `docs/certification/`
   pack and identify gaps we haven't seen.
5. **Contributors** willing to pick an open crate from
   RFC 0005 (cybersecurity consensus integration, full TSN
   transport, CBM backend) or an open RFC follow-up.

File issues with specific disagreements; send pull requests
with tests.

## Licence

- Software: Apache 2.0.
- Hardware designs: CERN-OHL-S v2.
- Documentation: CC-BY-SA 4.0.

Governance RFC is pending. Contributions made before it lands
are on the understanding that they will be licensed under
these terms.

## Milestone version

This snapshot is **v0.1**. There is no breakage policy yet —
the repo is pre-1.0 and interfaces can change.

Next milestone (**v0.2**) planned scope:

- DIY electronics cookbook (RFC 0019) with per-host-class
  commercial-module BOMs — **LANDED**.
- `osr-selftest` per-role commissioning CLI — **LANDED**. Runs
  known-good-fixture checks for each DIY-assembled SoC; the
  per-unit evidence stamp the custom-PCB path gets from
  flying-probe tests.
- **Commercial-tool gap-closing (Tier 1 from the Bentley OpenRail
  comparison) — LANDED:**
  - `osr-alignment` crate: horizontal + vertical alignment with
    cant schedule, LandXML + railML exports, stake-out CSV
    generator.
  - Earthworks quantities (cut / fill / rail tonnage / sleeper
    count / ballast / concrete) in `osr-alignment::earthworks`.
  - Trackside-equipment placement (axle counters, balises, radio
    masts, cable cabinets) in `osr-alignment::trackside`.
  - Parametric turnout CAD (1:9 / 1:14 / 1:18.5) in
    `osr_mech.track.turnout`.
  - Parametric depot CAD (three archetypes) in `osr_mech.depot`.
  - Gauge-clearance swept-solid check (EN 15273 baseline) in
    `osr_mech.clearance`.
  - PRM accessibility zones (EN 16584-1/3) in `osr_mech.accessibility`.
  - Crashworthiness scaffold (EN 15227 three-zone allocation) —
    RFC 0020 + `osr_mech.crashworthiness`.
- RFC 0017 v2 — secbus wired into consensus.
- Residual-risk narrative in the certification pack.
- First external review feedback incorporated.
