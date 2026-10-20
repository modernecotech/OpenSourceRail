# Nairobi — v0.5 maglev city planning

Provisional planning from retained geography, station demand and service schedules. All physical and manufacturing release flags remain false.

14 lines; 822 provisional trainsets / 4932 cars; 1,109,700 kWh gross onboard storage.

| Line | Cars | AW2 / AW3 | Body length m | Topology | Peak / total trains | Dwell s |
|---|---:|---:|---:|---|---:|---:|
| line-1 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 67 / 75 | 137 |
| line-2 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 120 / 133 | 133 |
| line-3 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 89 / 99 | 129 |
| line-4 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 35 / 40 | 122 |
| line-5 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 65 / 73 | 132 |
| line-6 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 73 / 82 | 134 |
| line-7 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 94 / 105 | 132 |
| line-8 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 49 / 55 | 127 |
| line-9 | 6 | 720 / 960 | 102 | two-independent-directed-circuits | 74 / 83 | 122 |
| line-10 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 19 / 22 | 125 |
| line-11 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 14 / 17 | 135 |
| line-12 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 10 / 12 | 133 |
| line-13 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 9 / 11 | 135 |
| line-14 | 6 | 720 / 960 | 102 | fixed-terminal-loops | 12 / 15 | 126 |

Retained ring wrap distances do not close the complete geographic route. Recomputed closure adds the following distances to the old wrap values; actual closure alignment remains open: line-9 3,608.0 m.

**Integrated-beam/no-walkway target:** door-mounted evacuation is a study candidate. Continuous walkway removal is not approved. Necessary iron reaction faces, supports/foundations, joints and protection remain. 29592 onboard packs are a provisional door-count hypothesis; new mass, lifetime cost and net savings are unknown. Landing space, accessible alternatives, fire/weather/fault conditions and rescue/maintenance access must be proved along the complete route.


**Predominantly elevated strategy:** 99% mainline elevation target; all ordinary sections proposed elevated. Ordinary viaduct planning length 584.396 km includes 49.151 km converted from retained at-grade scope. Special crossings remain separate and unpriced.

Straight tangents are preferred between demand anchors. Existing geographic alignments have not been rerouted or proved clear. Buildings/air rights, road and utility clearances, piers/foundations, wildlife/water passage, station access and construction access require evidence. Elevation does not establish zero displacement or zero environmental impact.


Formation matches both retained AW2/AW3 loads. Body lengths exclude unresolved couplings/overhang; platform allowance is a planning screen. Fleet is recomputed from hot AW3, no-regen straight/level duty and retained peak headways, with 10% spares rounded up and one cold reserve per line.

Radials use unlocated fixed terminal loop allowances; rings use two independent directed circuits. A 100 m radius / 20 km/h loop allowance is not approved geometry. Depot-only switches or transfer devices require separate hardware, access and recovery qualification.

Station charging is screened at 600 kW per car, with dwell extended to cover the worst incoming hot/no-regen leg and terminal loop. Multiple berths implied by dwell/headway require a conflict-free physical layout. Losses, taper, grade, curve forces, emergency reserve and missed charging remain open. No grid/PV/storage or site release is asserted.

| Scenario | Repeat fleet allowance USD | Ordinary elevated allowance USD | Partial subtotal USD |
|---|---:|---:|---:|
| low | 1,256,340,552 | 4,118,690,814 | 5,375,031,366 |
| base | 1,433,892,552 | 4,877,295,716 | 6,311,188,268 |
| high | 1,858,044,552 | 6,152,820,415 | 8,010,864,967 |
| target-90000 | 1,345,116,552 | 4,877,295,716 | 6,222,412,268 |
| target-60000 | 1,285,932,552 | 4,877,295,716 | 6,163,228,268 |
| indexed-joint-optimisation-target | 1,285,932,552 | 4,479,023,933 | 5,764,956,485 |

**Complete city programme cost remains unknown.** Partial allowances extrapolate the supplied three-car cost per car and ordinary elevated route km. They exclude site-specific conversion/clearance premiums, terminal loops, special/bridge works, stations, depots, energy, controls, land, NRE/plant, EPC and other scope listed in the structured report. The joint optimisation row uses unqualified mass/hardware targets and indexed civil quantities; it retains conservative baseline fleet counts. Targets are unquoted hypotheses; old city totals are not reused.

Open acceptance work:

- retained-geography: Survey, utilities, land, water crossings, terrain, ground investigation and alignment reconciliation; retained mapping is geographic evidence only.
- formation-platform: Close coupling pitch, full magnetic lifting-face/guidance-arm/below-floor swept envelope, door/egress layouts, actual mass and equal AW2/AW3 qualification. The 2.65 m cabin width does not bound running gear or platform clearance.
- field-control: Obtain force/loss maps and rig correlation, six-axis stability, target timing and independent support/capture/braking protection.
- terminal-topology: Locate fixed loops/ring closure, qualify curvature, clearance and land, and provide switch-free failure recovery.
- elevated-alignment: Locate the predominantly elevated straight-tangent proposal and verify buildings/air rights, road/utility clearance, wildlife/water passage, piers, station/egress and construction access; no zero-impact claim from elevation alone.
- civil-release: Redesign guidebeam/passive rail, supports/foundations, joints/tolerances, movement, gap dynamics, evacuation and erection.
- route-duty: Run approved grade, curve, wind, hot, low-voltage, full-SOC, no-regen, missed-charge, failed-channel and rescue duty.
- fleet-timetable: Validate headway/conflicts, station berth throughput, dispatch, maintenance rotation, degraded service and reserve.
- charging-microgrid: Place charging interfaces and prove taper, power quality, PV/storage/backup sizing and adverse-weather replenishment.
- depot-access: Locate line-local storage/workshops and qualify depot-only connection/transfer, isolation, inspection, towing and recovery.
- programme-cost: Price all station/land/loop/bridge/at-grade/depot/energy/control/production/QA/NRE/spares/OPEX scope, origin-trace MBOM and apply EPC once.
- physical-release: Close G0–G5 through authenticated independent physical acceptance; planning arithmetic is insufficient.

[Structured plan](summary.json) · [Preserved geography/demand records](retained-records.json)

The structured plan binds source bytes with SHA-256. Retained old designs remain separate wheel/rail comparators.

[Primary planning method](../../../../../../../engineering/ferrite_maglev/README.md)

<!-- Generated by engineering.ferrite_maglev.cities; primary planning only. -->
