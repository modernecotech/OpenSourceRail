# v0.7 systems and production handoff

The [selected digital 30 km railway](../reference-v07/digital/selected.toml) uses six-car powered-wheel trains, twelve stations and the [single production handoff](../reference-v07/digital/production/handoff.json). Its physical candidate is `osr-v07-joined-civil-518dad57a3af5046f40c8f4f`. Baghdad is a separate city design. The [station-launch comparison](v07-demonstrator-propulsion/station-assist.md) uses the retained passive-wheel vehicle and has a separate research identity.

| Work | Current connected output |
| --- | --- |
| Vehicle, assemblies and civil | [Car CAD and mass screen](../reference-v07/digital/vehicle/README.md), [beam FEM and civil revision](../reference-v07/digital/civil/README.md), [arrangement and interfaces](../reference-v07/integration/README.md) |
| BOM and workshop | [Assembly BOM, quantities, route and QA handoff](../reference-v07/digital/production/handoff.json); [source CSVs](../reference-v07/manufacturing/README.md) |
| Electronics and safety | [Logical interface schedule](../../control-electronics/interface-schedule.json) joins detection, interlocking, ATP, doors, brakes, station dispatch and power status. FUXA receives observations; ERP receives business records; passenger displays receive service information. None receives movement authority from a display. |
| Control room | [FUXA simulation view generator](../../services/integration/osr_integration/v07_supervision.py) builds 40 read-only equipment views from the handoff: twelve stations, six grid sites and 22 line sections. Live device addresses and commands are absent. |
| Passenger information | [Accessible display projection](../../services/integration/osr_integration/signage.py) uses a selected-candidate service snapshot and hides departures after the source is stale. It cannot command a train. |
| Project, purchasing and workforce | [Planning projection](../../services/integration/osr_integration/v07_business.py) reconciles fourteen capital scopes into a 43-month direct-cost draw, keeps contingency separate, produces 41 candidate-specific RFQ lines and counts 224,628 known workshop hours. Rates, supplier quotations, purchase orders, actual cash flow and payroll require approved source records. |
| ERPNext and HR | The [native integration](../../deployment/erpnext/README.md) supports candidate, procurement, workforce, QA and maintenance records. The selected handoff is a dry-run proposal; it creates no live transaction or employee record. |

The [station module schedule](v07-demonstrator-propulsion/station-module.json) counts minimum primary stock and receiving-space options. The [wheel-assist screen](v07-demonstrator-propulsion/station-assist.json) carries 500 m station launch into 2 km level and uphill traction demand, energy storage and charging. Both retain unknown installed mass, supplier price and independent braking evidence. Neither changes the selected powered-wheel digital design.

Generate the two planning exports from the repository root:

```bash
PYTHONPATH=services/integration python3 -m osr_integration.v07_supervision --project-out var/v07-fuxa-preview.json
PYTHONPATH=services/integration python3 -m osr_integration.v07_business --output var/v07-project-preview.json
```

The FUXA file is a simulation preview for inspection, not a live device import.
