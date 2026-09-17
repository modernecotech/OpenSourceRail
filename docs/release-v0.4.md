# OpenSourceRail v0.4.0

v0.4 recognizes ERPNext business execution and FUXA/OSR equipment supervision as
part of the connected OpenSourceRail software platform.
The Workbench now carries city and asset context across planning, engineering,
procurement, manufacturing, construction, commissioning, operations, maintenance
and renewal while each service retains its own permissions and authority.

## Included baseline

- Reproducible ERPNext city projects, component imports and native project,
  procurement, stock, manufacturing, quality, finance, HR and maintenance views.
- Generated FUXA devices and displays backed by the OSR historian, with explicit
  quality and timestamp tags and no FUXA write-through to railway controls.
- Native Rust simulation bindings for station energy/SCADA, vehicle BMS,
  auxiliary power, HVAC and condition monitoring, points, level crossings and
  station-aggregate fare gates. Existing switch identities are reused; crossing
  positions remain absent until a city declares real assets.
- Nine production-plant views for cities selecting the LM3 family, generated
  directly from its validated method source, covering the 120-product union and 30 tooling families. Explicit cell
  and quality-hold fixtures route accountable ERP Issues; reviewed Item/BOM
  mappings require the exact Item/BOM pair at the engineering revision. Other
  families receive no implied LM3 production coverage, and QA release stays separate.
- Durable, ordered and idempotent condition-event delivery to ERP maintenance
  Issues, plus case-status reconciliation without automatic railway release.
- A reviewed, repeat-safe Issue-to-Asset-Repair transition with native part/stock
  consumption, technician assignment, expected/actual downtime, linked condition
  and serial evidence, permission-filtered feedback and no automatic handback.
- City-scoped Workbench navigation, trends, alarms, serial/batch history,
  lifecycle evidence and bounded simulation-only lighting requests.
- Revision-safe supervisory updates: removed equipment is retained as retired
  history, pending commands fail, telemetry and new commands are rejected, and a
  later reviewed package can reactivate the stable asset identity.
- A review-bound package-change workflow and Workbench surface that classify
  design, embedded, telemetry, alarm, command, ERP and display changes; trace
  installed serials and append-only evidence; reject stale reviews; isolate city
  baselines; and block unsafe installed-position or pending-command changes.
- Review-bound FUXA replacement with a package/device/view manifest, explicit
  add/change/remove sets, stale-review rejection and backups of both the previous
  project and the applied review.
- Occurrence-bound alarm acknowledgment, including stale-view rejection and a
  fresh acknowledgment requirement when a cleared condition activates again.
- A generated catalogue-readiness gate that compiles all 266 ERP/component
  profiles and real-asset supervision packages, preserves per-city hashes and
  distinguishes on-demand task payloads from operator/commissioning inputs.
- A disposable native-stack CI gate covering ERP transactions and feedback,
  FUXA/gateway/controller behaviour, Workbench navigation and service
  outage/recovery, condition-to-repair execution, retained removed-serial history
  and independent replacement re-release, alongside version-pinned Kani proofs.

## Review corrections and release verification

- Default FUXA displays follow the configured city/site, while explicit equipment
  selection takes precedence. Adding a factory cannot change a city's default.
- Retired equipment retains history without stopping telemetry for active assets.
- Safety-case traceability, current successful result records and independent
  acceptance are separate. Result checks bind named harnesses, tools, bounds,
  input/report hashes and acceptance fingerprints; they do not execute proofs or
  authenticate reviewers. Missing controlled results remain open.
- GSN counts are generated from TOML. Operations rules use accepted charging duty
  and morning readiness, new business transactions belong to ERPNext, and formal
  model refinement remains an assurance objective rather than a completed proof.
- Catalogue readiness is independent of untracked local generated bundles.

The software release gates are the complete Rust/Python/browser CI workflow,
the two pinned Kani properties, and the disposable ERPNext/FUXA/controller/
Workbench workflow, including service loss and recovery. The attached release
evidence manifest records the exact commit and successful workflow runs; its
checksums bind the published reader book, overview and evidence assets.

Only ATP rejection of expired authority and interlocking validity-window
arithmetic are selected Kani release gates. Passing these does not close the
remaining topology proofs, all 71 declared safety-case solution records, or
independent safety acceptance. See [result validation](safety-case/result-validation.md).

## Upgrade and compatibility

Back up ERPNext, the integration database and FUXA project before upgrading.
Rebuild the ERP application image and run site migration, rebuild the gateway,
regenerate each city package, review the exact old/new package hashes, then
apply and reimport the reviewed FUXA project. Restart the native simulator.
Use [deployment instructions](../deployment/supervision/README.md) for the commands.

Factory metadata now records its rolling-stock family. Earlier packages must be
regenerated; incompatible factory positions become retired history through the
normal reviewed package-change process. Installed-position removals remain
blocked for independent disposition. Samawah's bounded simulation package has
19 positions; Mosul's has 10, with no LM3 factory methods. Historical records,
serials, Issues and evidence must not be erased to make an upgrade pass.

## Boundary

The local stack is an integration and simulation baseline. Supervisory points
and crossing views are maintenance/status surfaces only: they expose no movement
authority, point/barrier command, protection reset or interlocking bypass.
Production TLS, organisation identity/MFA, commissioned physical MQTT/OPC UA/Modbus or device-bus
adapters, supplier calibration, signed live actions, HIL, operator validation and
independent railway acceptance remain deployment work. ERP case closure, alarm
clearance and local lifecycle evidence do not grant a railway operational release.
Likewise, simulated factory progress and quality holds are workflow demonstrations:
performed travelers, process observations, NCR/rework disposition, Quality
Inspections and manufacturing acceptance require accountable real records.

The repository remains pre-1.0. A v0.4.0 software version is not a safety
certificate, construction release, production drawing set or deployment approval.
