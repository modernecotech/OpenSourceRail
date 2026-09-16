# OpenSourceRail v0.4.0 development line

v0.4 recognizes ERPNext business execution and FUXA/OSR equipment supervision as
part of the connected OpenSourceRail product rather than optional demonstrations.
The Workbench now carries city and asset context across planning, engineering,
procurement, manufacturing, construction, commissioning, operations, maintenance
and renewal while each service retains its own permissions and authority.

## Included baseline

- Reproducible ERPNext city projects, component imports and native project,
  procurement, stock, manufacturing, quality, finance, HR and maintenance views.
- Generated FUXA devices and displays backed by the OSR historian, with explicit
  quality and timestamp tags and no FUXA write-through to railway controls.
- Native Rust simulation bindings for station energy/SCADA and vehicle BMS,
  auxiliary power, HVAC and condition monitoring.
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

## Boundary

The local stack is an integration and simulation baseline. Production TLS,
organisation identity/MFA, commissioned physical MQTT/OPC UA/Modbus or device-bus
adapters, supplier calibration, signed live actions, HIL, operator validation and
independent railway acceptance remain deployment work. ERP case closure, alarm
clearance and local lifecycle evidence do not grant a railway operational release.

The repository remains pre-1.0. A v0.4.0 software version is not a safety
certificate, construction release, production drawing set or deployment approval.
