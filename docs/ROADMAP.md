# Roadmap

This page tracks remaining validation and hardening work for the v0.2
development baseline. It is a planning map, not a release contract.
The open-source CAD, survey, analysis, and simulation selections and the
evidence-producing work packages for the remaining engineering items are in
the [engineering design and simulation plan](engineering-design-simulation-plan.md).

## v0.2 Workstream

| Workstream | Target outcome |
|---|---|
| Documentation accessibility | Section-level READMEs, stale-reference cleanup, link checks, and clearer front-door navigation |
| Rolling-stock detail package | Supplier-exact envelopes, weld maps, tolerance stacks, harness clamp locations, FEA-ready brackets, 2D drawings, and NC/flat-pattern outputs |
| Mechanical CAD | Material-aware sheet-metal templates, COTS variants with selected SKUs, generated FreeCAD/PNG drift gates, and catalog manifests |
| Hardware integration evidence | Pilot-ready COTS/DIY integration packs for T-ECU/S, T-ECU/A, T-OBS, W-SBC, and S-SBC: exact SKUs, wiring/harness maps, connector maps, enclosure/mounting notes, power/thermal margins, SD-card images, self-test logs, and bench records |
| Custom-board release artifacts | KiCad capture, gerbers, board BOMs, DFM review, and assembly drawings only for deployments that choose OSR-specific carrier, power, safety-I/O, or sensor-interface boards |
| DIY deployment path | Prebuilt SD-card images, checksums, role-specific self-test evidence, and first external build feedback |
| Software integration | RFC 0017 signed-message verification on the live consensus receive path, TSN transport maturation, CBM backend, and GUI live-data paths |
| City Studio | Git-backed city projects, source locks, complete manual line/station/alignment authoring, semantic revision comparison, weekly service planning, deterministic manifests, source-locked demand-aware alternatives, and controlled GIS/simulation/alignment-exchange jobs (implemented); richer CAD/IFC and GIS viewers next |
| Certification evidence | Residual-risk narrative, independent-assessor review notes, first-article field-evidence plan, and traceability updates |
| Civil/station package | Survey-grade Samawah alignment replacement, per-span checks, station archetype variants, and deployment-specific assumptions |

Open release gates for certification, hardware, rolling stock,
civil/station, and operations are tracked in the relevant section
checklists rather than left as implicit TODOs.

## v0.2 Definition Of Done

- All top-level domains have local READMEs and current status notes.
- `python3 scripts/repo-health.py --quiet` passes on the release tree.
- Rolling-stock documentation links to the current FreeCAD/PNG/COTS
  package and clearly separates envelope CAD from production drawings.
- Hardware host classes have either pilot-ready COTS/DIY integration
  packs or explicit custom-board KiCad/gerber/BOM gaps where custom
  boards are actually required.
- Certification and safety-case pages identify remaining external
  evidence rather than implying it already exists.
