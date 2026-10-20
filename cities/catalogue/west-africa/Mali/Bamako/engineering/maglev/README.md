# Bamako — v0.5 maglev city planning

Provisional planning from retained geography, station demand and service schedules. All physical and manufacturing release flags remain false.

9 lines; 413 provisional trainsets / 1652 cars; 371,700 kWh gross onboard storage.

| Line | Cars | AW2 / AW3 | Body length m | Topology | Peak / total trains | Dwell s |
|---|---:|---:|---:|---|---:|---:|
| line-1 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 77 / 86 | 134 |
| line-2 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 41 / 47 | 124 |
| line-3 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 21 / 25 | 103 |
| line-4 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 79 / 88 | 136 |
| line-5 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 27 / 31 | 114 |
| line-6 | 4 | 480 / 640 | 68 | two-independent-directed-circuits | 76 / 85 | 121 |
| line-7 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 9 / 11 | 114 |
| line-8 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 11 / 14 | 106 |
| line-9 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 22 / 26 | 100 |

Retained ring wrap distances do not close the complete geographic route. Recomputed closure adds the following distances to the old wrap values; actual closure alignment remains open: line-6 -0.3 m.

Formation matches both retained AW2/AW3 loads. Body lengths exclude unresolved couplings/overhang; platform allowance is a planning screen. Fleet is recomputed from hot AW3, no-regen straight/level duty and retained peak headways, with 10% spares rounded up and one cold reserve per line.

Radials use unlocated fixed terminal loop allowances; rings use two independent directed circuits. A 100 m radius / 20 km/h loop allowance is not approved geometry. Depot-only switches or transfer devices require separate hardware, access and recovery qualification.

Station charging is screened at 600 kW per car, with dwell extended to cover the worst incoming hot/no-regen leg and terminal loop. Multiple berths implied by dwell/headway require a conflict-free physical layout. Losses, taper, grade, curve forces, emergency reserve and missed charging remain open. No grid/PV/storage or site release is asserted.

| Scenario | Repeat fleet allowance USD | Ordinary elevated allowance USD | Partial subtotal USD |
|---|---:|---:|---:|
| low | 420,818,044 | 1,583,631,519 | 2,004,449,562 |
| base | 480,290,044 | 1,875,314,164 | 2,355,604,208 |
| high | 622,362,044 | 2,365,751,832 | 2,988,113,875 |
| target-90000 | 450,554,044 | 1,875,314,164 | 2,325,868,208 |
| target-60000 | 430,730,044 | 1,875,314,164 | 2,306,044,208 |

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
