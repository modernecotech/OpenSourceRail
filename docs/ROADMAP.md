# Roadmap

This page tracks near-term work after the v0.1 publishable snapshot.
It is a planning map, not a release contract.

## v0.2 Workstream

| Workstream | Target outcome |
|---|---|
| Documentation accessibility | Section-level READMEs, stale-reference cleanup, link checks, and clearer front-door navigation |
| Rolling-stock detail package | Supplier-exact envelopes, weld maps, tolerance stacks, harness clamp locations, FEA-ready brackets, 2D drawings, and NC/flat-pattern outputs |
| Mechanical CAD | Material-aware sheet-metal templates, COTS variants with selected SKUs, generated STEP/PNG drift gates, and catalog manifests |
| Hardware release artifacts | KiCad capture, gerbers, board BOMs, and assembly drawings for T-ECU/S, T-ECU/A, T-OBS, W-SBC, and S-SBC |
| DIY deployment path | Prebuilt SD-card images, checksums, role-specific self-test evidence, and first external build feedback |
| Software integration | RFC 0017 signed-message verification on the live consensus receive path, TSN transport maturation, CBM backend, and GUI live-data paths |
| Certification evidence | Residual-risk narrative, independent-assessor review notes, first-article field-evidence plan, and traceability updates |
| Civil/station package | Survey-grade Samawah alignment replacement, per-span checks, station archetype variants, and deployment-specific assumptions |

## v0.2 Definition Of Done

- All top-level domains have local READMEs and current status notes.
- `python3 scripts/repo-health.py --quiet` passes on the release tree.
- Rolling-stock documentation links to the current STEP/PNG/COTS
  package and clearly separates envelope CAD from production drawings.
- Hardware host classes have either released v2-spec documents or
  explicit KiCad/gerber/BOM gaps.
- Certification and safety-case pages identify remaining external
  evidence rather than implying it already exists.

