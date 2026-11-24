# Train and railway control electronics

<!-- osr-system-context:start -->
OpenSourceRail connects locally maintainable railway hardware, design and delivery tools, and train and wayside software. The published v0.7.2 Baghdad opening study includes a service plan, traction assessment and supplier dossier. Current development joins revised route, vehicle, power, civil and purchasing assumptions for v0.8 production preparation; first-article measurements and independent review remain open. The v0.6 passive-wheel vehicle is a separate research selector. Safety and accessibility remain mandatory, and digital results do not grant fabrication or passenger-operation approval.

[Project introduction](../README.md) · [Engineering approach and current status](../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

The selected wheel railway needs train protection, braking, door control,
traction supervision, line-section protection and a staffed control room.
These are equipment in the railway budget, not an optional software layer.
The [Baghdad system model](../cities/Baghdad/system.toml) counts the equipment
for its protected-conductor train and assigns its price **within** existing
vehicle, station, signalling, grid and control-centre scopes. The
[calculated schedule](../cities/Baghdad/system-results.json) changes with fleet,
station, grid and power-section counts.

| Equipment | 148.2 km, 242 trains | 605.652 km, 934 trains | Location and function |
| --- | ---: | ---: | --- |
| Independent train protection channels | 484 | 1,868 | Two per train; enforce speed and movement limits |
| Train radio links | 484 | 1,868 | Two per train; authenticated train-to-ground status |
| Car control nodes | 1,452 | 5,604 | One per car; collect traction, auxiliary and door status |
| Door controllers | 11,616 | 44,832 | One per opening on both sides; release only the platform side |
| Bogie brake controllers | 2,904 | 11,208 | One per bogie; independent protected stop path |
| Train service-power units | 484 | 1,868 | Two per train; backed-up control and brake power |
| Contact-shoe status channels | 968 | 3,736 | Four per train; protected conductor contact and isolation status |
| Traction-inverter control units | 484 | 1,868 | Two per train; traction enable and fault reporting |
| Station dispatch controllers | 64 | 280 | Stop position, platform side, dwell and departure checks |
| Power-section control gateways | 114 | 532 | Isolation, earth-fault and access interlocks |
| Grid protection gateways | 30 | 100 | Substation protection and supervisory status |
| Control-room equipment sets | 2 | 4 | Traffic supervision and incident response |

The first-programme equipment price allocation is **$102.536m** across five
existing capital scopes: vehicles $75.020m, stations $7.680m, signalling
$14.136m, grid $4.500m and control centres $1.200m. The metropolitan allocation
is **$399.632m** within the same scopes. These are 2026 planning allowances,
not supplier quotations or extra capital. The model reserves **0.35 t** and
**6 kW** per train for controls inside its existing base vehicle mass and
auxiliary energy allowance. The Baghdad equipment and harness schedule totals
**299 kg** and **3.68 kW** per train, leaving **51 kg** and **2.32 kW** within
those reserves. These are digital planning allowances for supplier quotation;
heat rejection, cable routing and mounting use the same reserve. The same model sizes a separate
65 kWh nominal service battery per train: 52 kWh usable covers a 50.4 kWh
two-hour essential-duty request with brake and door events and reserve.
Its 0.50 t and $0.10m/train allowances sit inside the base vehicle mass and
price; charging requests 36.1 kW/train over two hours. Traction duty remains
on the protected conductor.

## Installed arrangement

The [Baghdad train](../cities/Baghdad/VEHICLE.md) has two protection channels,
two radios, six car control nodes, 48 door controllers, twelve bogie brake
controllers, four contact-shoe status channels and two traction-inverter
controllers. The protected DC conductor feeds the traction converters through
contact shoes, isolation and fault protection. A separate service battery and
two power units feed protection, brakes, door release and communication during
a line-power outage. Traction loss commands a protected stop; a control-room
request cannot bypass onboard braking or grant normal-service door release on
the wrong side. The door evaluator also treats authorised emergency egress as
a separate path and inhibits a motor-open command while the train is moving.

The [powered-wheel ATP adapter](../crates/osr-atp/src/powered_wheel.rs) inhibits
traction when the selected configuration, contact shoes, section permission or
inverter proof is lost and requests an independent mechanical stop. The
[protected-conductor TCMS adapter](../crates/osr-tcms/src/protected_conductor.rs)
keeps the service-battery contactor distinct from line traction supply. The
older station-launch/coast ATP interface remains a separate v0.6 research
configuration; its station-drive permissive is not the Baghdad traction gate.

At each station, the dispatch controller confirms train identity, stopping
position, platform side, doors closed and route authority before departure.
Wayside train detection, section switches and interlocking protect occupied
track and maintenance access. The control room supervises trains and power;
the [FUXA gateway](../deployment/supervision/README.md) is for observation and
records only. Its data cannot grant movement authority.

The [30 km v0.7 digital reference](../docs/reference-v07/integration/interfaces.csv)
is a different train and supply candidate: 51 six-car sets, twelve one-sided
door openings per train, twelve stations, six traction sites and roof
collectors under rigid overhead supply. It uses the same protection, brake,
door, station and control-room functions, but its Baghdad contact-shoe and
two-sided door counts must not be copied into its BOM or mass calculation.
The passive v0.6 comfort vehicle is retained separately.

| 30 km control equipment | Counted planning quantity |
| --- | ---: |
| Train protection channels / radios / service-power units | 102 each |
| Car control nodes | 306 |
| Door controllers / bogie brake controllers | 612 each |
| Station dispatch controllers / grid protection gateways | 12 / 6 |
| Line-section gateways / train detection route-km | 22 / 30 |
| Terminal control-room sets | 2 |

Using the same unit planning allowances gives **$9.180m** of train
electronics inside the existing **$300.900m** rolling-stock scope, **$1.440m**
inside the **$96.000m** station scope, **$0.900m** inside the **$18.000m**
substation scope. The 22 line-section gateways, train-detection allowance
and two control-room sets together allocate **$4.040m** within the existing
**$12.000m** turnback and line-control scope. The complete **$15.560m**
equipment schedule is in the selected candidate's [52-row BOM and 23-step
production handoff](../docs/reference-v07/digital/production/README.md).
Each train reserves 300 kg and 4 kW for this equipment inside the existing
vehicle mass and auxiliary-power budgets.

## Supply and build interfaces

Train and station electronics need numbered harnesses, isolated traction and
control power, protective earthing, accessible enclosures, cooling, EMC
segregation, replaceable connectors and logged software versions. The
interfaces to be fixed on assembly drawings are wheel odometry and position,
brake command and feedback, door closed and locked, platform side, traction
inhibit, contact-shoe status, power-section state and emergency-stop requests.
Factory inspection should check wiring continuity, insulation, channel
separation, fault inputs and loss-of-power behaviour before installation.

The available software modules are [ATP](../crates/osr-atp/),
[interlocking](../crates/osr-interlocking/), [train control](../crates/osr-tcms/),
[doors](../crates/osr-door-control/), [station control](../crates/osr-station-scada/),
[control room](../crates/osr-occ/) and [event recording](../crates/osr-event-recorder/).
They are development implementations, without a claimed safety integrity
qualification; the counted hardware and drawings are
the purchasing and installation scope. The former
[maglev controller](../crates/osr-maglev-control/README.md) and
[maglev host profile](../deployment/maglev.toml) are retained research only.
