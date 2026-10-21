# Yangon — v0.5 maglev city planning

![Geographic corridor planning map](network.svg)

Provisional planning from retained geography, station demand and service schedules. All physical and manufacturing release flags remain false.

14 lines; 351 provisional trainsets / 2106 cars; 63,180 kWh gross onboard storage.

| Line | Cars | AW2 / AW3 | Bodies / assumed overall m | Topology | Peak / total trains | Dwell s |
|---|---:|---:|---:|---|---:|---:|
| line-1 | 6 | 720 / 960 | 102 / 104.5 | fixed-terminal-loops | 23 / 27 | 323 |
| line-2 | 6 | 720 / 960 | 102 / 104.5 | fixed-terminal-loops | 19 / 22 | 345 |
| line-3 | 6 | 720 / 960 | 102 / 104.5 | fixed-terminal-loops | 39 / 44 | 279 |
| line-4 | 6 | 720 / 960 | 102 / 104.5 | fixed-terminal-loops | 23 / 27 | 322 |
| line-5 | 6 | 720 / 960 | 102 / 104.5 | fixed-terminal-loops | 29 / 33 | 319 |
| line-6 | 6 | 720 / 960 | 102 / 104.5 | fixed-terminal-loops | 16 / 19 | 343 |
| line-7 | 6 | 720 / 960 | 102 / 104.5 | fixed-terminal-loops | 31 / 36 | 280 |
| line-8 | 6 | 720 / 960 | 102 / 104.5 | fixed-terminal-loops | 38 / 43 | 286 |
| line-9 | 6 | 720 / 960 | 102 / 104.5 | two-independent-directed-circuits | 56 / 63 | 256 |
| line-10 | 6 | 720 / 960 | 102 / 104.5 | fixed-terminal-loops | 5 / 7 | 307 |
| line-11 | 6 | 720 / 960 | 102 / 104.5 | fixed-terminal-loops | 5 / 7 | 342 |
| line-12 | 6 | 720 / 960 | 102 / 104.5 | fixed-terminal-loops | 7 / 9 | 337 |
| line-13 | 6 | 720 / 960 | 102 / 104.5 | fixed-terminal-loops | 6 / 8 | 363 |
| line-14 | 6 | 720 / 960 | 102 / 104.5 | fixed-terminal-loops | 4 / 6 | 357 |

Station-powered dispatch recomputes headway from runtime,dwell and protected-zone clearance. The190s baseline and longer actual-leg bounds replace shorter source headways; fleet and capacity use the selected headway. Unpowered-coast feasibility, grade, phase/overlap and stalled-train recovery remain hard acceptance gates.

- line-1: selected headway 883s versus source 180s; normal capacity 2,935/hour/direction; 14 held longitudinal cases.
- line-2: selected headway 958s versus source 180s; normal capacity 2,706/hour/direction; 10 held longitudinal cases.
- line-3: selected headway 737s versus source 180s; normal capacity 3,517/hour/direction; 16 held longitudinal cases.
- line-4: selected headway 881s versus source 180s; normal capacity 2,942/hour/direction; 12 held longitudinal cases.
- line-5: selected headway 870s versus source 180s; normal capacity 2,979/hour/direction; 16 held longitudinal cases.
- line-6: selected headway 951s versus source 180s; normal capacity 2,726/hour/direction; 8 held longitudinal cases.
- line-7: selected headway 740s versus source 180s; normal capacity 3,503/hour/direction; 16 held longitudinal cases.
- line-8: selected headway 761s versus source 180s; normal capacity 3,406/hour/direction; 20 held longitudinal cases.
- line-9: selected headway 829s versus source 360s; normal capacity 3,127/hour/direction; 35 held longitudinal cases.
- line-10: selected headway 831s versus source 180s; normal capacity 3,119/hour/direction; 2 held longitudinal cases.
- line-11: selected headway 948s versus source 180s; normal capacity 2,734/hour/direction; 3 held longitudinal cases.
- line-12: selected headway 931s versus source 180s; normal capacity 2,784/hour/direction; 5 held longitudinal cases.
- line-13: selected headway 1016s versus source 180s; normal capacity 2,551/hour/direction; 3 held longitudinal cases.
- line-14: selected headway 997s versus source 180s; normal capacity 2,600/hour/direction; 1 held longitudinal cases.

Retained ring wrap distances do not close the complete geographic route. Recomputed closure adds the following distances to the input wrap values; actual closure alignment remains open: line-9 0.2 m.

**Integrated-beam/no-walkway target:** door-mounted evacuation is a study candidate. Continuous walkway removal is not approved. Necessary iron reaction faces, supports/foundations, joints and protection remain. 12636 onboard packs are a provisional door-count hypothesis; new mass, lifetime cost and net savings are unknown. Landing space, accessible alternatives, fire/weather/fault conditions and rescue/maintenance access must be proved along the complete route.


**Predominantly elevated strategy:** 99% mainline elevation target; all ordinary sections proposed elevated. Ordinary viaduct planning length 505.486 km includes 87.697 km converted from retained at-grade scope. Special crossings remain separate and unpriced.

Straight tangents are preferred between demand anchors. Existing geographic alignments have not been rerouted or proved clear. Buildings/air rights, road and utility clearances, piers/foundations, wildlife/water passage, station access and construction access require evidence. Elevation does not establish zero displacement or zero environmental impact.


Formation matches both planning AW2/AW3 loads. Assumed overall length includes the shared configuration’s coupling gaps; body lengths alone exclude them. Platforms are screened against assumed overall length plus 10 m; final tolerances, overhang and berthing require qualification. Fleet is recomputed from hot AW3 services duty and selected station-resource headways, with 10% spares rounded up and one cold reserve per line. Pure trajectory and fixed-winding force feasibility are separate screens; unlocated intermediate-zone hints do not clear either hold.

Radials use unlocated fixed terminal loop allowances; rings use two independent directed circuits. A 100 m radius / 20 km/h loop allowance is not approved geometry. Depot-only switches or transfer devices require separate hardware, access and recovery qualification.

Station services charging is screened at 200 kW per car, including live connected services and replacement of run/disconnected-dwell energy. Main traction is supplied by separate station LSM equipment. Dwell is extended for the worst incoming services duty and terminal allowance. Multiple berths implied by dwell/headway require a conflict-free physical layout. Losses, taper, grade, curve forces, emergency reserve and missed charging remain open. No grid/PV/storage or site release is asserted.

| Scenario | Repeat fleet allowance USD | Ordinary elevated allowance USD | Station electrical target USD | Partial subtotal USD |
|---|---:|---:|---:|---:|
| low | 310,750,830 | 1,328,859,084 | 342,720,000 | 1,982,329,914 |
| base | 414,334,440 | 1,771,812,112 | 619,920,000 | 2,806,066,552 |
| high | 621,501,660 | 2,657,718,167 | 982,800,000 | 4,262,019,827 |

**Complete city programme cost remains unknown.** Partial allowances price each formation by car, coupling and shared train systems, plus measured section/reaction-steel quantities and explicit process assumptions per ordinary elevated route km. Station electrical rows price unquoted repeated fixed-group equipment targets separately; actual45-second charging and supply/thermal ratings require a configured quote. They exclude site-specific conversion/clearance premiums, terminal loops, special/bridge works, station buildings/access, depots, external utility reinforcement, land, NRE/plant, EPC and other scope listed in the structured report. Rates and productivity assumptions require supplier and site validation. Complete project costs and localisation remain unknown.

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

## Manufacture and erection

Local work is proposed for repeated frames, cartridges, coils, concrete units and system integration. Input origins and local value added remain unverified. Factory capacity and programme duration require measured cycle times, cure/release criteria and site access.

- **beam**: qualify concrete and reinforcement → assemble reusable mould and cage → stress approved tendons → cast and monitor cure → verify release strength → demould and survey → install reaction faces → proof/inspect serialised element.
- **supports**: investigate utilities and ground → qualify foundation type → prefabricate cage/pier where feasible → construct foundation → erect and temporarily stabilise pier/cap → survey bearing seats.
- **vehicle**: prepare repeatable sandwich moulds and layup → infuse or light-RTM selected laminate/core → verify cure and bondline → fit sized hardpoints, doors, glazing and interior → install support/guidance coils,30kWh services pack and auxiliaries → weigh, inspect and test exact revision.
- **magnetics**: qualify ferrite and core steel → machine carriers and reaction faces → wind and insulate coils → impregnate and cure → assemble replaceable cartridges → map force/loss/temperature → calibrate independent sensing.
- **erection**: survey delivery corridor → verify lift plan and crane at radius → deliver and lift beam → locate and positively lock engineered joint → survey reaction faces → complete serial QA traveller → test integrated route section.
- **software**: build reproducible Rust control → execute oracle/fault/deadline tests → bind exact geometry and force-map revision → test isolated SBC I/O and independent trips → measure worst-case timing → perform integrated rig and route tests.
- **station-propulsion**: manufacture paired2.5m stator cassettes → verify winding R/L,insulation and polarity → assemble two fixed groups per direction → integrate independent bridges,DCbus,resistor and services charging → calibrate phase sensors → replay launch/commit/fault protocol → low-energy rig and rated duty acceptance.

UK equipment candidates are capability leads, not prices or approved purchases. Rotary coil winding and CCL prestressing have explicit UK-manufacture statements; complete configuration, ratings and origin schedules remain open. See the linked manufacturing bill for dated primary sources.


[Structured plan](summary.json) · [Preserved geography/demand records](retained-records.json) · [Quantity bills, manufacturing routes and factory equipment](manufacturing.json)

The structured plan binds current source bytes and manufacturing bills with SHA-256.

[Primary planning method](../../../../../../../engineering/ferrite_maglev/README.md)

<!-- Generated by engineering.ferrite_maglev.cities; primary planning only. -->
