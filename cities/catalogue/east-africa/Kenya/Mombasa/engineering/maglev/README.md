# Mombasa — v0.5 maglev city planning

Provisional planning from retained geography, station demand and service schedules. All physical and manufacturing release flags remain false.

9 lines; 359 provisional trainsets / 1436 cars; 323,100 kWh gross onboard storage.

| Line | Cars | AW2 / AW3 | Body length m | Topology | Peak / total trains | Dwell s |
|---|---:|---:|---:|---|---:|---:|
| line-1 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 27 / 31 | 109 |
| line-2 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 22 / 26 | 113 |
| line-3 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 29 / 33 | 112 |
| line-4 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 95 / 106 | 131 |
| line-5 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 39 / 44 | 100 |
| line-6 | 4 | 480 / 640 | 68 | two-independent-directed-circuits | 76 / 85 | 115 |
| line-7 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 11 / 14 | 139 |
| line-8 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 6 / 8 | 121 |
| line-9 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 10 / 12 | 128 |

Retained ring wrap distances do not close the complete geographic route. Recomputed closure adds the following distances to the old wrap values; actual closure alignment remains open: line-6 2,041.1 m.

Formation matches both retained AW2/AW3 loads. Body lengths exclude unresolved couplings/overhang; platform allowance is a planning screen. Fleet is recomputed from hot AW3, no-regen straight/level duty and retained peak headways, with 10% spares rounded up and one cold reserve per line.

Radials use unlocated fixed terminal loop allowances; rings use two independent directed circuits. A 100 m radius / 20 km/h loop allowance is not approved geometry. Depot-only switches or transfer devices require separate hardware, access and recovery qualification.

Station charging is screened at 600 kW per car, with dwell extended to cover the worst incoming hot/no-regen leg and terminal loop. Multiple berths implied by dwell/headway require a conflict-free physical layout. Losses, taper, grade, curve forces, emergency reserve and missed charging remain open. No grid/PV/storage or site release is asserted.

| Scenario | Repeat fleet allowance USD | Ordinary elevated allowance USD | Partial subtotal USD |
|---|---:|---:|---:|
| low | 365,795,830 | 1,800,686,074 | 2,166,481,904 |
| base | 417,491,830 | 2,132,347,115 | 2,549,838,945 |
| high | 540,987,830 | 2,690,004,794 | 3,230,992,624 |
| target-90000 | 391,643,830 | 2,132,347,115 | 2,523,990,945 |
| target-60000 | 374,411,830 | 2,132,347,115 | 2,506,758,945 |

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
