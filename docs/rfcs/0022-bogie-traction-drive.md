# RFC 0022 — Bogie and Traction Drive

**Status:** Current
**Depends on:** [RFC 0008](0008-rolling-stock-reference-design.md), [RFC 0021](0021-battery-traction.md)

## 1. Decision

Each car has one two-axle powered bogie and one two-axle trailer bogie. The
powered bogie carries two independent heavy-commercial-vehicle-class PMSM
and controller channels. The promoted three-car train therefore has three
powered bogies, six powered axles, and six controllers.

## 2. Reference envelope

| Parameter | Reference |
|---|---:|
| Gauge | 1,435 mm |
| Wheelbase | 2,100 mm |
| Wheel diameter | 760 mm new / 680 mm worn |
| Candidate motor | Inovance HM47-class or qualified equivalent |
| Candidate controller | Inovance LD32-class or qualified equivalent |
| Candidate short peak | 350 kW per motor |
| Train installed peak | 2.1 MW |
| Initial control cap | 1.8 MW |
| DC operating range | 650–700 V nominal, 740 V provisional upper limit |

The bogie frame, suspension, brake mounts, axlebox, wheelset, and carbody
interfaces are common wherever axle load and kinematic-envelope evidence
permit.

## 3. Gearbox

No fixed ratio is released. The integrator selects the ratio from the actual
motor torque-speed map, new/worn wheel diameters, 90 km/h service speed,
overspeed margin, grade, acceleration, adhesion, and thermal duty. Packaging
CAD values are explicitly non-authoritative seeds.

## 4. Acceptance

Evidence covers frame static/fatigue load, wheel/axle/bearing qualification,
AW0–AW3 acceleration, wet/dry adhesion, wheel-slip protection, braking blend,
regen at high SOC, motor/controller thermal soak, one-channel unavailable
operation, ride dynamics, noise, ingress, EMC, lubrication, and wheel-lathe
access.
