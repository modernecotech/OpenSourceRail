# Roadmap

This page tracks remaining validation and hardening work for the v0.2
development baseline. It is a planning map, not a release contract.
The open-source CAD, survey, analysis, and simulation selections and the
evidence-producing work packages for the remaining engineering items are in
the [engineering design and simulation plan](engineering-design-simulation-plan.md).

## v0.2 Workstream

| Workstream | Target outcome |
|---|---|
| Documentation accessibility | One root front door and source registry are enforced; local READMEs retain only discipline/city evidence, with generated inventory and link/drift checks |
| Rolling-stock detail package | Supplier-exact envelopes, weld maps, tolerance stacks, harness clamp locations, FEA-ready brackets, 2D drawings, and NC/flat-pattern outputs |
| Mechanical CAD | Material-aware sheet-metal templates, COTS variants with selected SKUs, generated FreeCAD/PNG drift gates, and catalog manifests |
| Control-electronics integration evidence | Pilot-ready COTS/DIY integration packs for T-ECU/S, T-ECU/A, T-OBS, W-SBC, and S-SBC: exact SKUs, wiring/harness maps, connector maps, enclosure/mounting notes, power/thermal margins, SD-card images, self-test logs, and bench records |
| Custom-board release artifacts | KiCad capture, gerbers, board BOMs, DFM review, and assembly drawings only for deployments that choose OSR-specific carrier, power, safety-I/O, or sensor-interface boards |
| DIY deployment path | Prebuilt SD-card images, checksums, role-specific self-test evidence, and first external build feedback |
| Software integration | Workbench context plus onboard, station, intrusion and T2G-to-depot CBM/historian/analytics software-in-loop are implemented; signed live actions, production transports, asset-specific points/crossing/fare-gate harnesses, HIL, and authenticated live GUI paths remain |
| City Studio | Git-backed city projects, source locks, layered offline GIS editing, complete manual line/station/alignment authoring, semantic revision comparison including BCF, OD demand, and per-line IFC survey control, editable service for generated/manual routes, atomic all-route day-type headway scenarios and day-plan copying, deterministic period/OD intent with conservative scheduled-capacity screens, deterministic manifests, source-locked demand-aware alternatives, controlled GIS/simulation/alignment/IFC4.3 civil jobs with native map conversion, hash-verified GIS/alignment/IFC object/IDS/BCF evidence viewers, interactive discipline-filtered 4D envelope playback, searchable multi-asset deterministic BCF topic authoring, evidence-gated coordination management, append-only non-circular revision approvals, and 122-check Playwright browser/restart persistence acceptance (implemented); survey/parcel/utility source packs, native tessellated IFC geometry streaming, passenger assignment, and platform/interchange pedestrian capacity next |
| Certification evidence | Residual-risk narrative, independent-assessor review notes, first-article field-evidence plan, and traceability updates |
| Civil/station package | Survey-grade Samawah alignment replacement, per-span checks, station archetype variants, and deployment-specific assumptions |

Open release gates for certification, hardware, rolling stock,
civil/station, and operations are tracked in the relevant section
checklists rather than left as implicit TODOs.

## v0.2 Definition Of Done

- All top-level domains have local READMEs and current status notes.
- `python3 tools/automation/repo-health.py --quiet` passes on the release tree.
- Rolling-stock documentation links to the current FreeCAD/PNG/COTS
  package and clearly separates envelope CAD from production drawings.
- Hardware host classes have either pilot-ready COTS/DIY integration
  packs or explicit custom-board KiCad/gerber/BOM gaps where custom
  boards are actually required.
- Certification and safety-case pages identify remaining external
  evidence rather than implying it already exists.
