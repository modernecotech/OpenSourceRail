# Dar Es Salaam — v0.5 maglev city planning

![Geographic corridor planning map](network.svg)

Provisional planning from retained geography, station demand and service schedules. All physical and manufacturing release flags remain false.

14 lines; 523 provisional trainsets / 3138 cars; 94,140 kWh gross onboard storage.

| Line | Cars | AW2 / AW3 | Bodies / assumed overall m | Topology | Peak / total trains | Dwell s |
|---|---:|---:|---:|---|---:|---:|
| line-1 | 6 | 720 / 960 | 102 / 104.5 | located-tangent-terminal-loops-with-station-powered-blocks | 40 / 45 | 60 |
| line-2 | 6 | 720 / 960 | 102 / 104.5 | located-tangent-terminal-loops-with-station-powered-blocks | 51 / 58 | 60 |
| line-3 | 6 | 720 / 960 | 102 / 104.5 | located-tangent-terminal-loops-with-station-powered-blocks | 34 / 39 | 60 |
| line-4 | 6 | 720 / 960 | 102 / 104.5 | located-tangent-terminal-loops-with-station-powered-blocks | 42 / 48 | 60 |
| line-5 | 6 | 720 / 960 | 102 / 104.5 | located-tangent-terminal-loops-with-station-powered-blocks | 25 / 29 | 60 |
| line-6 | 6 | 720 / 960 | 102 / 104.5 | located-tangent-terminal-loops-with-station-powered-blocks | 35 / 40 | 60 |
| line-7 | 6 | 720 / 960 | 102 / 104.5 | located-tangent-terminal-loops-with-station-powered-blocks | 24 / 28 | 60 |
| line-8 | 6 | 720 / 960 | 102 / 104.5 | located-tangent-terminal-loops-with-station-powered-blocks | 31 / 36 | 60 |
| line-9 | 6 | 720 / 960 | 102 / 104.5 | two-independent-directed-circuits | 112 / 125 | 60 |
| line-10 | 6 | 720 / 960 | 102 / 104.5 | located-tangent-terminal-loops-with-station-powered-blocks | 7 / 9 | 60 |
| line-11 | 6 | 720 / 960 | 102 / 104.5 | located-tangent-terminal-loops-with-station-powered-blocks | 10 / 12 | 60 |
| line-12 | 6 | 720 / 960 | 102 / 104.5 | located-tangent-terminal-loops-with-station-powered-blocks | 10 / 12 | 60 |
| line-13 | 6 | 720 / 960 | 102 / 104.5 | located-tangent-terminal-loops-with-station-powered-blocks | 13 / 16 | 60 |
| line-14 | 6 | 720 / 960 | 102 / 104.5 | located-tangent-terminal-loops-with-station-powered-blocks | 22 / 26 | 60 |

The requested urban plan uses a1.5km minimum and approximately2km average passenger spacing. Suburban4–5km is considered only with an explicit service classification and fixed, priced midway acceleration zones. Existing transfer nodes are retained; incompatible short gaps remain visible. The1km/88s case is a retained component benchmark. Exclusive whole-leg protection gives a conservative comparison headway; a180s sectioned or multiple-berth alternative needs its own proof and cost. No eligible full operating design is asserted.

- line-1: urban exclusive-model headway 320s versus source 180s; normal capacity 8,100/hour/direction; 0 held longitudinal cases; 1 transfer/terminal spacing conflicts.
  Proposed operating plan: 29 mainline stops versus 32 retained access records; 4 additional terminal service/motor zones. Retained capacity target met: false. Consolidated access connections and every station/loop site remain unapproved.
- line-2: urban exclusive-model headway 310s versus source 180s; normal capacity 8,361/hour/direction; 0 held longitudinal cases; 2 transfer/terminal spacing conflicts.
  Proposed operating plan: 37 mainline stops versus 34 retained access records; 4 additional terminal service/motor zones. Retained capacity target met: false. Consolidated access connections and every station/loop site remain unapproved.
- line-3: urban exclusive-model headway 330s versus source 180s; normal capacity 7,855/hour/direction; 0 held longitudinal cases; 4 transfer/terminal spacing conflicts.
  Proposed operating plan: 27 mainline stops versus 18 retained access records; 4 additional terminal service/motor zones. Retained capacity target met: false. Consolidated access connections and every station/loop site remain unapproved.
- line-4: urban exclusive-model headway 290s versus source 180s; normal capacity 8,938/hour/direction; 0 held longitudinal cases; 4 transfer/terminal spacing conflicts.
  Proposed operating plan: 29 mainline stops versus 44 retained access records; 4 additional terminal service/motor zones. Retained capacity target met: false. Consolidated access connections and every station/loop site remain unapproved.
- line-5: urban exclusive-model headway 290s versus source 180s; normal capacity 8,938/hour/direction; 0 held longitudinal cases; 2 transfer/terminal spacing conflicts.
  Proposed operating plan: 17 mainline stops versus 15 retained access records; 4 additional terminal service/motor zones. Retained capacity target met: false. Consolidated access connections and every station/loop site remain unapproved.
- line-6: urban exclusive-model headway 270s versus source 180s; normal capacity 9,600/hour/direction; 0 held longitudinal cases; 0 transfer/terminal spacing conflicts.
  Proposed operating plan: 22 mainline stops versus 18 retained access records; 4 additional terminal service/motor zones. Retained capacity target met: false. Consolidated access connections and every station/loop site remain unapproved.
- line-7: urban exclusive-model headway 290s versus source 180s; normal capacity 8,938/hour/direction; 0 held longitudinal cases; 2 transfer/terminal spacing conflicts.
  Proposed operating plan: 16 mainline stops versus 12 retained access records; 4 additional terminal service/motor zones. Retained capacity target met: false. Consolidated access connections and every station/loop site remain unapproved.
- line-8: urban exclusive-model headway 300s versus source 180s; normal capacity 8,640/hour/direction; 0 held longitudinal cases; 5 transfer/terminal spacing conflicts.
  Proposed operating plan: 22 mainline stops versus 36 retained access records; 4 additional terminal service/motor zones. Retained capacity target met: false. Consolidated access connections and every station/loop site remain unapproved.
- line-9: urban exclusive-model headway 360s versus source 360s; normal capacity 7,200/hour/direction; 0 held longitudinal cases; 9 transfer/terminal spacing conflicts.
  Proposed operating plan: 99 mainline stops versus 81 retained access records; 0 additional terminal service/motor zones. Retained capacity target met: true. Consolidated access connections and every station/loop site remain unapproved.
- line-10: urban exclusive-model headway 290s versus source 180s; normal capacity 8,938/hour/direction; 0 held longitudinal cases; 0 transfer/terminal spacing conflicts.
  Proposed operating plan: 4 mainline stops versus 3 retained access records; 4 additional terminal service/motor zones. Retained capacity target met: false. Consolidated access connections and every station/loop site remain unapproved.
- line-11: urban exclusive-model headway 250s versus source 180s; normal capacity 10,368/hour/direction; 0 held longitudinal cases; 0 transfer/terminal spacing conflicts.
  Proposed operating plan: 5 mainline stops versus 3 retained access records; 4 additional terminal service/motor zones. Retained capacity target met: false. Consolidated access connections and every station/loop site remain unapproved.
- line-12: urban exclusive-model headway 260s versus source 180s; normal capacity 9,969/hour/direction; 0 held longitudinal cases; 0 transfer/terminal spacing conflicts.
  Proposed operating plan: 5 mainline stops versus 3 retained access records; 4 additional terminal service/motor zones. Retained capacity target met: false. Consolidated access connections and every station/loop site remain unapproved.
- line-13: urban exclusive-model headway 270s versus source 180s; normal capacity 9,600/hour/direction; 0 held longitudinal cases; 0 transfer/terminal spacing conflicts.
  Proposed operating plan: 7 mainline stops versus 3 retained access records; 4 additional terminal service/motor zones. Retained capacity target met: false. Consolidated access connections and every station/loop site remain unapproved.
- line-14: urban exclusive-model headway 250s versus source 180s; normal capacity 10,368/hour/direction; 0 held longitudinal cases; 2 transfer/terminal spacing conflicts.
  Proposed operating plan: 13 mainline stops versus 7 retained access records; 4 additional terminal service/motor zones. Retained capacity target met: false. Consolidated access connections and every station/loop site remain unapproved.

**Integrated-beam/no-walkway target:** door-mounted evacuation is a study candidate. Continuous walkway removal is not approved. Necessary iron reaction faces, supports/foundations, joints and protection remain. 18828 onboard packs are a provisional door-count hypothesis; new mass, lifetime cost and net savings are unknown. Landing space, accessible alternatives, fire/weather/fault conditions and rescue/maintenance access must be proved along the complete route.


**Predominantly elevated strategy:** 99% mainline elevation target; all ordinary sections proposed elevated. Ordinary viaduct planning length 586.849 km includes 48.476 km converted from retained at-grade scope. Special crossings remain separate and unpriced.

Straight tangents are preferred between demand anchors. Existing geographic alignments have not been rerouted or proved clear. Buildings/air rights, road and utility clearances, piers/foundations, wildlife/water passage, station access and construction access require evidence. Elevation does not establish zero displacement or zero environmental impact.


Formation matches both planning AW2/AW3 loads. Assumed overall length includes the shared configuration’s coupling gaps; body lengths alone exclude them. Platforms are screened against assumed overall length plus 10 m; final tolerances, overhang and berthing require qualification. Fleet is recomputed from hot AW3 services duty and selected station-resource headways, with 10% spares rounded up and one cold reserve per line. Pure trajectory and fixed-winding force feasibility are separate screens; unlocated intermediate-zone hints do not clear either hold.

Default plans retain passenger-transfer nodes between independent fixed lines and choose fewer intermediate passenger stops. Ordinary retained stops remain demand/access records. Short transfer gaps remain explicit exceptions; no train switches or junction routing are introduced. Radial terminals have tangent-connected provisional R-L-R loops, three station-powered sections, two added service/motor stops per loop and explicit 150 m winding zones. Their 25 km/h arclength and lateral-acceleration screens do not qualify six-car curve phase, guidance, clearance, land or construction. Rings retain two independent directed circuits. Depot access and recovery remain unqualified.

Charging alternatives compare240/400/600kW input per car at90% conversion, with exact connected fractions, hotel load, reserve and computed dwell. The displayed research candidate is not an eligible operating recommendation; changed50/60kWh packs require new formation confirmation. Main traction is supplied by separate station LSM equipment. Dwell is extended for the worst incoming services duty and terminal allowance. Multiple berths implied by dwell/headway require a conflict-free physical layout. Conversion loss is a declared planning allowance; taper, grade, curve forces, emergency reserve and missed charging remain open. No grid/PV/storage or site release is asserted.

| Scenario | Repeat fleet allowance USD | Ordinary elevated allowance USD | Terminal civil allowance USD | Station electrical target USD | Foundation proposal increment USD | Booster electrical/mount targets USD | Rescue kits USD | Partial subtotal USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| low | 463,027,590 | 1,606,099,695 | 35,708,265 | 658,680,000 | 162,233,181 | 9,793,758 | 182,166,681 | 3,117,709,171 |
| base | 617,370,120 | 2,141,466,260 | 47,611,020 | 1,193,920,000 | 216,310,908 | 17,300,011 | 242,888,908 | 4,476,867,228 |
| high | 926,055,180 | 3,212,199,390 | 71,416,531 | 1,905,200,000 | 324,466,363 | 27,277,516 | 364,333,362 | 6,830,948,341 |

Terminal civil allowances use actual proposed arc length, beam/support counts and ordinary section quantity equivalents; curved detailing premiums remain unpriced. Added one-way service zones conservatively carry complete two-direction electrical package targets. The primary priced subtotal includes the conditional 6.5 m foundation proposal increment once; the previous smaller-foundation subtotal is retained only as a comparison. Every fixed booster has separately priced electrical equipment and mount/cabinet stock; rescue nodes have independently priced winch/portal/foundation kits. Higher voltage/current rating premiums, ground capacity, anchorage and access remain unaccepted and unpriced where unknown.


**Complete city programme cost remains unknown.** Partial allowances price each formation by car, coupling and shared train systems, plus measured section/reaction-steel quantities and explicit process assumptions per ordinary elevated route km. Station electrical rows price unquoted repeated fixed-group equipment targets separately; actual45-second charging and supply/thermal ratings require a configured quote. They exclude site-specific conversion/clearance premiums, terminal curved-detail/land premiums, special/bridge works, station buildings/access, depots, external utility reinforcement, land, NRE/plant, EPC and other scope listed in the structured report. Rates and productivity assumptions require supplier and site validation. Complete project costs and localisation remain unknown.

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
