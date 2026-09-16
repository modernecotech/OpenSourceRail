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
- City-scoped Workbench navigation, trends, alarms, serial/batch history,
  lifecycle evidence and bounded simulation-only lighting requests.
- Revision-safe supervisory updates: removed equipment is retained as retired
  history, pending commands fail, telemetry and new commands are rejected, and a
  later reviewed package can reactivate the stable asset identity.
- Occurrence-bound alarm acknowledgment, including stale-view rejection and a
  fresh acknowledgment requirement when a cleared condition activates again.

## Boundary

The local stack is an integration and simulation baseline. Production TLS,
organisation identity/MFA, commissioned physical MQTT/OPC UA/Modbus or device-bus
adapters, supplier calibration, signed live actions, HIL, operator validation and
independent railway acceptance remain deployment work. ERP case closure, alarm
clearance and local lifecycle evidence do not grant a railway operational release.

The repository remains pre-1.0. A v0.4.0 software version is not a safety
certificate, construction release, production drawing set or deployment approval.
