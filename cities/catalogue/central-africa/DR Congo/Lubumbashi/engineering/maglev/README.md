# Lubumbashi — v0.5 maglev city planning

Provisional planning from retained geography, station demand and service schedules. All physical and manufacturing release flags remain false.

8 lines; 192 provisional trainsets / 768 cars; 172,800 kWh gross onboard storage.

| Line | Cars | AW2 / AW3 | Body length m | Topology | Peak / total trains | Dwell s |
|---|---:|---:|---:|---|---:|---:|
| line-1 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 32 / 37 | 124 |
| line-2 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 30 / 34 | 127 |
| line-3 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 15 / 18 | 124 |
| line-4 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 31 / 36 | 127 |
| line-5 | 4 | 480 / 640 | 68 | two-independent-directed-circuits | 22 / 26 | 106 |
| line-6 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 12 / 15 | 119 |
| line-7 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 9 / 11 | 96 |
| line-8 | 4 | 480 / 640 | 68 | fixed-terminal-loops | 12 / 15 | 120 |

Retained ring wrap distances do not close the complete geographic route. Recomputed closure adds the following distances to the old wrap values; actual closure alignment remains open: line-5 3,468.1 m.

**Integrated-beam/no-walkway target:** door-mounted evacuation is a study candidate. Continuous walkway removal is not approved. Necessary iron reaction faces, supports/foundations, joints and protection remain. 4608 onboard packs are a provisional door-count hypothesis; new mass, lifetime cost and net savings are unknown. Landing space, accessible alternatives, fire/weather/fault conditions and rescue/maintenance access must be proved along the complete route.


**Predominantly elevated strategy:** 99% mainline elevation target; all ordinary sections proposed elevated. Ordinary viaduct planning length 156.438 km includes 11.954 km converted from retained at-grade scope. Special crossings remain separate and unpriced.

Straight tangents are preferred between demand anchors. Existing geographic alignments have not been rerouted or proved clear. Buildings/air rights, road and utility clearances, piers/foundations, wildlife/water passage, station access and construction access require evidence. Elevation does not establish zero displacement or zero environmental impact.


Formation matches both retained AW2/AW3 loads. Body lengths exclude unresolved couplings/overhang; platform allowance is a planning screen. Fleet is recomputed from hot AW3, no-regen straight/level duty and retained peak headways, with 10% spares rounded up and one cold reserve per line.

Radials use unlocated fixed terminal loop allowances; rings use two independent directed circuits. A 100 m radius / 20 km/h loop allowance is not approved geometry. Depot-only switches or transfer devices require separate hardware, access and recovery qualification.

Station charging is screened at 600 kW per car, with dwell extended to cover the worst incoming hot/no-regen leg and terminal loop. Multiple berths implied by dwell/headway require a conflict-free physical layout. Losses, taper, grade, curve forces, emergency reserve and missed charging remain open. No grid/PV/storage or site release is asserted.

| Scenario | Repeat fleet allowance USD | Ordinary elevated allowance USD | Partial subtotal USD |
|---|---:|---:|---:|
| low | 195,634,538 | 1,102,542,645 | 1,298,177,183 |
| base | 223,282,538 | 1,305,615,488 | 1,528,898,027 |
| high | 289,330,538 | 1,647,063,885 | 1,936,394,423 |
| target-90000 | 209,458,538 | 1,305,615,488 | 1,515,074,027 |
| target-60000 | 200,242,538 | 1,305,615,488 | 1,505,858,027 |
| indexed-joint-optimisation-target | 200,242,538 | 1,199,001,118 | 1,399,243,657 |

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
