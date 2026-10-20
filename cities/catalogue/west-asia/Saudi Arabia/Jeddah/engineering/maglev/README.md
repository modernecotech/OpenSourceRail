# Jeddah — v0.5 maglev city planning

Provisional planning from retained geography, station demand and service schedules. All physical and manufacturing release flags remain false.

14 lines; 491 provisional trainsets / 2946 cars; 662,850 kWh gross onboard storage.

| Line | Cars | AW2 / AW3 | Body length m | Topology | Peak / total trains | Dwell s |
|---|---:|---:|---:|---|---:|---:|
| line-1 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 52 / 59 | 125 |
| line-2 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 29 / 33 | 135 |
| line-3 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 61 / 69 | 129 |
| line-4 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 47 / 53 | 137 |
| line-5 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 39 / 44 | 132 |
| line-6 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 35 / 40 | 120 |
| line-7 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 32 / 37 | 111 |
| line-8 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 36 / 41 | 123 |
| line-9 | 6 | 720 / 960 | 102 | two-independent-directed-circuits | 40 / 45 | 110 |
| line-10 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 20 / 23 | 130 |
| line-11 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 7 / 9 | 130 |
| line-12 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 16 / 19 | 126 |
| line-13 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 8 / 10 | 129 |
| line-14 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 7 / 9 | 133 |

Retained ring wrap distances do not close the complete geographic route. Recomputed closure adds the following distances to the old wrap values; actual closure alignment remains open: line-9 361.6 m.

Formation matches both retained AW2/AW3 loads. Body lengths exclude unresolved couplings/overhang; platform allowance is a planning screen. Fleet is recomputed from hot AW3, no-regen straight/level duty and retained peak headways, with 10% spares rounded up and one cold reserve per line.

Radials use unlocated fixed terminal loop allowances; rings use two independent directed circuits. A 100 m radius / 20 km/h loop allowance is not approved geometry. Depot-only switches or transfer devices require separate hardware, access and recovery qualification.

Station charging is screened at 600 kW per car, with dwell extended to cover the worst incoming hot/no-regen leg and terminal loop. Multiple berths implied by dwell/headway require a conflict-free physical layout. Losses, taper, grade, curve forces, emergency reserve and missed charging remain open. No grid/PV/storage or site release is asserted.

| Scenario | Repeat fleet allowance USD | Ordinary elevated allowance USD | Partial subtotal USD |
|---|---:|---:|---:|
| low | 750,441,863 | 2,502,406,954 | 3,252,848,816 |
| base | 856,497,863 | 2,963,315,109 | 3,819,812,971 |
| high | 1,109,853,863 | 3,738,289,978 | 4,848,143,840 |
| target-90000 | 803,469,863 | 2,963,315,109 | 3,766,784,971 |
| target-60000 | 768,117,863 | 2,963,315,109 | 3,731,432,971 |

**Complete city programme cost remains unknown.** Partial allowances extrapolate the supplied three-car cost per car and ordinary elevated route km. They exclude terminal loops, special/at-grade/bridge works, stations, depots, energy, controls, land, NRE/plant, EPC and other scope listed in the structured report. Targets are unquoted hypotheses; old city totals are not reused.

Open acceptance work:

- retained-geography: Survey, utilities, land, water crossings, terrain, ground investigation and alignment reconciliation; retained mapping is geographic evidence only.
- formation-platform: Close coupling pitch, full magnetic lifting-face/guidance-arm/below-floor swept envelope, door/egress layouts, actual mass and equal AW2/AW3 qualification. The 2.65 m cabin width does not bound running gear or platform clearance.
- field-control: Obtain force/loss maps and rig correlation, six-axis stability, target timing and independent support/capture/braking protection.
- terminal-topology: Locate fixed loops/ring closure, qualify curvature, clearance and land, and provide switch-free failure recovery.
- civil-release: Redesign guidebeam/passive rail, supports/foundations, joints/tolerances, movement, gap dynamics, evacuation and erection.
- route-duty: Run approved grade, curve, wind, hot, low-voltage, full-SOC, no-regen, missed-charge, failed-channel and rescue duty.
- fleet-timetable: Validate headway/conflicts, station berth throughput, dispatch, maintenance rotation, degraded service and reserve.
- charging-microgrid: Place charging interfaces and prove taper, power quality, PV/storage/backup sizing and adverse-weather replenishment.
- depot-access: Locate line-local storage/workshops and qualify depot-only connection/transfer, isolation, inspection, towing and recovery.
- programme-cost: Price all station/land/loop/bridge/at-grade/depot/energy/control/production/QA/NRE/spares/OPEX scope, origin-trace MBOM and apply EPC once.
- physical-release: Close G0–G5 through authenticated independent physical acceptance; planning arithmetic is insufficient.

[Structured plan](summary.json) · [Preserved geography/demand records](retained-records.json)

The structured plan binds source bytes with SHA-256. Retained old designs remain separate wheel/rail comparators.
