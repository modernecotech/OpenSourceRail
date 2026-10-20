# Kabul — v0.5 maglev city planning

Provisional planning from retained geography, station demand and service schedules. All physical and manufacturing release flags remain false.

11 lines; 466 provisional trainsets / 2796 cars; 629,100 kWh gross onboard storage.

| Line | Cars | AW2 / AW3 | Body length m | Topology | Peak / total trains | Dwell s |
|---|---:|---:|---:|---|---:|---:|
| line-1 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 42 / 48 | 129 |
| line-2 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 84 / 94 | 133 |
| line-3 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 45 / 51 | 108 |
| line-4 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 46 / 52 | 124 |
| line-5 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 74 / 83 | 135 |
| line-6 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 30 / 34 | 134 |
| line-7 | 6 | 720 / 960 | 102 | two-independent-directed-circuits | 54 / 61 | 121 |
| line-8 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 8 / 10 | 122 |
| line-9 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 6 / 8 | 122 |
| line-10 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 6 / 8 | 115 |
| line-11 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 14 / 17 | 105 |

Retained ring wrap distances do not close the complete geographic route. Recomputed closure adds the following distances to the old wrap values; actual closure alignment remains open: line-7 552.8 m.

Formation matches both retained AW2/AW3 loads. Body lengths exclude unresolved couplings/overhang; platform allowance is a planning screen. Fleet is recomputed from hot AW3, no-regen straight/level duty and retained peak headways, with 10% spares rounded up and one cold reserve per line.

Radials use unlocated fixed terminal loop allowances; rings use two independent directed circuits. A 100 m radius / 20 km/h loop allowance is not approved geometry. Depot-only switches or transfer devices require separate hardware, access and recovery qualification.

Station charging is screened at 600 kW per car, with dwell extended to cover the worst incoming hot/no-regen leg and terminal loop. Multiple berths implied by dwell/headway require a conflict-free physical layout. Losses, taper, grade, curve forces, emergency reserve and missed charging remain open. No grid/PV/storage or site release is asserted.

| Scenario | Repeat fleet allowance USD | Ordinary elevated allowance USD | Partial subtotal USD |
|---|---:|---:|---:|
| low | 712,231,992 | 1,630,664,845 | 2,342,896,837 |
| base | 812,887,992 | 1,931,010,368 | 2,743,898,359 |
| high | 1,053,343,992 | 2,436,013,870 | 3,489,357,861 |
| target-90000 | 762,559,992 | 1,931,010,368 | 2,693,570,359 |
| target-60000 | 729,007,992 | 1,931,010,368 | 2,660,018,359 |

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
