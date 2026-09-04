# Station and civil factory/release work packages

These packages turn the 45 stable station product identities into bounded
drawing, tooling, site-handoff and verification tasks. They deliberately
separate reusable definitions from supplier configuration and deployment release.

- Packages: **9**
- Unique product rows: **45**
- Drawing/interface IDs: **18**
- Tool/gauge families: **22**
- Release paths: **18** reusable definition, **14** supplier configuration, **13** deployment-specific

`release-candidate` means the catalogue definition is mature enough to enter
controlled detailing; it never means a part, structure or site is released.

## `STN-FRP-010` — precast platform, guideway edge, drainage and closure pack

Delivery lane: `hybrid-prefabrication-and-site`.

Drawings/interfaces: `STN-CIV-100`, `STN-CIV-110`.
Tools/gauges: `STN-TOOL-PRECAST-MOULD`, `STN-TOOL-EDGE-GAUGE`, `STN-TOOL-LIFTING-GAUGE`.

### Controlled products

| Product | Route | Catalogue maturity | Release path | Default | Variants |
|---|---|---|---|---|---:|
| `STN-CIV-P010` — 6 m ground-level station slab and depressed double-track guideway-channel panel | `MAKE` | `release-candidate` | `reusable-definition` | `not-required` | 7 |
| `STN-CIV-P020` — platform sub-base, levelling pad, grout, and closure-pour kit | `MAKE` | `release-candidate` | `reusable-definition` | `not-required` | 7 |
| `STN-CIV-P030` — platform and track drainage channel, pipe, catch-pit, and outlet kit | `MAKE` | `release-candidate` | `reusable-definition` | `not-required` | 7 |
| `STN-CIV-P040` — 3 m at-grade guideway-channel edge beam, coping/tactile carrier, and drained service trough | `MAKE` | `release-candidate` | `reusable-definition` | `not-required` | 6 |
| `STN-PLT-P010` — platform coping, tactile strip, warning line, and edge-marker kit | `SOURCE` | `release-candidate` | `reusable-definition` | `not-required` | 7 |

### Frozen inputs

- accepted survey control, track alignment and platform stepping/gap envelope
- site geotechnical, drainage/outfall and foundation design
- released concrete, reinforcement, tactile and joint/seal systems

### Controlled outputs

- repeatable precast mould, reinforcement, insert and lifting drawings
- site set-out, levelling, drainage and closure-pour schedule
- platform-edge datum, tolerance and interface-control plan

### Verification

- mould and first-article dimensional survey
- concrete, reinforcement and lifting-insert records
- installed track/platform gap-step and drainage survey

Boundary: The reusable mould and panel definition does not release site excavation, foundations, drainage falls or track/platform geometry.

## `STN-FRP-020` — platform canopy steel, footing and solar-roof pack

Delivery lane: `hybrid-prefabrication-and-supplier`.

Drawings/interfaces: `STN-CNP-200`, `STN-CNP-210`.
Tools/gauges: `STN-TOOL-PORTAL-FIXTURE`, `STN-TOOL-ANCHOR-TEMPLATE`, `STN-TOOL-ROOF-WATER-TEST`.

### Controlled products

| Product | Route | Catalogue maturity | Release path | Default | Variants |
|---|---|---|---|---|---:|
| `STN-CNP-P010` — 6 m galvanised HEA portal-frame steel kit | `MAKE` | `release-candidate` | `reusable-definition` | `not-required` | 7 |
| `STN-CNP-P020` — canopy footing, reinforcement, base plate, and anchor-bolt kit | `MAKE` | `release-candidate` | `reusable-definition` | `not-required` | 7 |
| `STN-CNP-P030` — factory-bonded solar roof sandwich panel with MC4 leads | `BID` | `buildable-after-supplier-freeze` | `supplier-configuration` | `specified` | 7 |
| `STN-CNP-P040` — platform-canopy PV string, combiner, isolation, bonding, and downlink kit | `BID` | `buildable-after-supplier-freeze` | `supplier-configuration` | `specified` | 7 |

### Frozen inputs

- site wind, snow, seismic, thermal and maintenance load cases
- accepted steel, coating, roof-panel, PV and connector systems
- surveyed foundation, platform, electrical and drainage interfaces

### Controlled outputs

- portal cut/weld, baseplate, anchor-template and erection drawings
- roof-panel layout, joints, gutters, penetrations and edge details
- PV string, isolation, bonding and cable-route schedule

### Verification

- steel certificates, weld/NDT and frame survey
- anchor-template and erected-frame survey
- roof watertightness, PV insulation/polarity and bond-continuity tests

Boundary: Catalogue bay geometry is not a structural release; foundations and every site load case require the deployment design authority.

## `STN-FRP-030` — auxiliary solar-canopy module, truss and site-interface pack

Delivery lane: `deployment-led-hybrid`.

Drawings/interfaces: `STN-CNP-220`, `STN-CNP-230`.
Tools/gauges: `STN-TOOL-TRUSS-FIXTURE`, `STN-TOOL-AUX-ANCHOR-TEMPLATE`, `STN-TOOL-AUX-ROOF-GAUGE`.

### Controlled products

| Product | Route | Catalogue maturity | Release path | Default | Variants |
|---|---|---|---|---|---:|
| `STN-CNP-P050` — 8.5 m × 22 m factory-bonded auxiliary solar-roof bay module | `BID` | `buildable-after-supplier-and-structural-release` | `supplier-configuration` | `specified` | 7 |
| `STN-CNP-P060` — 22 m S355 transverse Warren-truss frame with two HSS 200 columns | `MAKE` | `buildable-after-structural-calculation-and-drawing-release` | `reusable-definition` | `specified` | 7 |
| `STN-CNP-P070` — auxiliary-canopy pad footing, reinforcement, base plate, and anchor-bolt kit | `MAKE` | `buildable-after-site-structural-release` | `deployment-specific` | `specified` | 7 |
| `STN-CNP-P080` — auxiliary-canopy PV string, combiner, isolation, bonding, and downlink kit | `BID` | `buildable-after-electrical-and-supplier-freeze` | `supplier-configuration` | `specified` | 7 |
| `STN-CNP-P090` — auxiliary-canopy gutter, downpipe, lightning, maintenance-access, and edge-protection kit | `SOURCE` | `buildable-after-site-and-supplier-freeze` | `deployment-specific` | `specified` | 7 |

### Frozen inputs

- released site layout, egress, fire, drainage and maintenance-access plan
- site-specific structural calculation and foundation reactions
- selected roof/PV/lightning/edge-protection supplier configurations

### Controlled outputs

- repeatable truss fabrication and roof-bay module drawings
- site footing, anchor, erection, gutter/downpipe and access drawings
- PV string, protection, bonding and commissioning schedule

### Verification

- truss weld/NDT and dimensional survey
- foundation pre-pour, anchor and erected-geometry surveys
- water, electrical, lightning and edge-protection acceptance tests

Boundary: The 8.5 m by 22 m catalogue module is an area-planning unit only until site structure, foundations, egress and electrical integration are signed.

## `STN-FRP-040` — station services, passenger equipment and plinth integration pack

Delivery lane: `supplier-interface`.

Drawings/interfaces: `STN-SYS-300`, `STN-SYS-310`.
Tools/gauges: `STN-TOOL-CABINET-PLINTH-GAUGE`, `STN-TOOL-FARE-PLINTH-GAUGE`, `STN-TOOL-ACCESSIBILITY-GAUGE`.

### Controlled products

| Product | Route | Catalogue maturity | Release path | Default | Variants |
|---|---|---|---|---|---:|
| `STN-MEP-P010` — weatherproof services cabinet, plinth, cooling, and maintenance-light kit | `MAKE` | `release-candidate` | `reusable-definition` | `not-required` | 7 |
| `STN-MEP-P020` — incoming switchboard, distribution board, metering, UPS, and earthing kit | `BID` | `buildable-after-supplier-freeze` | `supplier-configuration` | `specified` | 7 |
| `STN-MEP-P030` — platform and emergency LED luminaire, support, and cable kit | `SOURCE` | `release-candidate` | `reusable-definition` | `not-required` | 7 |
| `STN-MEP-P040` — fire detection, alarm interface, extinguisher, and evacuation-sign kit | `SOURCE` | `release-candidate` | `reusable-definition` | `not-required` | 7 |
| `STN-PAX-P010` — S-SBC station/depot host and rack enclosure | `SOURCE` | `release-candidate` | `reusable-definition` | `not-required` | 7 |
| `STN-PAX-P020` — passenger-information display and route-strip kit | `SOURCE` | `release-candidate` | `reusable-definition` | `not-required` | 7 |
| `STN-PAX-P030` — CCTV, PA loudspeaker, help-point, radio, and station-LAN kit | `BID` | `buildable-after-supplier-freeze` | `supplier-configuration` | `specified` | 7 |
| `STN-PAX-P040` — fare gate, accessible gate, and validator equipment kit | `BID` | `buildable-after-supplier-freeze` | `supplier-configuration` | `specified` | 7 |
| `STN-PAX-P050` — ticket-vending machine equipment kit | `BID` | `buildable-after-supplier-freeze` | `supplier-configuration` | `specified` | 6 |
| `STN-PAX-P060` — seating, wheelchair-zone marking, wayfinding, and accessible-signage kit | `SOURCE` | `release-candidate` | `reusable-definition` | `not-required` | 7 |
| `STN-PAX-P070` — anchored rolled-steel fare-lane / validator plinth with protected cable void | `MAKE` | `release-candidate` | `reusable-definition` | `not-required` | 7 |
| `STN-PAX-P080` — anchored rolled-steel TVM plinth with protected power/data entry | `MAKE` | `release-candidate` | `reusable-definition` | `not-required` | 6 |

### Frozen inputs

- frozen operator equipment, communications, fare and cyber interfaces
- utility, UPS, cooling, earthing, fire and evacuation requirements
- released accessibility, sightline, coverage and maintainability zones

### Controlled outputs

- cabinet/plinth fabrication and coordinated equipment-layout drawings
- power, data, containment, earth and fire-interface schedules
- equipment anchorage, accessible reach and replacement-clearance map

### Verification

- plinth and anchorage dimensional/proof checks
- supplier FAT and station integrated functional tests
- accessibility, CCTV/PA coverage and power-loss survey

Boundary: Generic plinths may be prepared from controlled envelopes; holes, anchors and services may not be released against assumed supplier equipment.

## `STN-FRP-050` — pedestrian approach, lift/stair core and overbridge interface pack

Delivery lane: `deployment-led-hybrid`.

Drawings/interfaces: `STN-ACC-400`, `STN-ACC-410`.
Tools/gauges: `STN-TOOL-ACCESSIBILITY-GAUGE`, `STN-TOOL-STAIR-RISER-GAUGE`.

### Controlled products

| Product | Route | Catalogue maturity | Release path | Default | Variants |
|---|---|---|---|---|---:|
| `STN-ACC-P010` — direct/protected pedestrian approach, kerb, ramp, and boundary kit | `MAKE` | `release-candidate` | `reusable-definition` | `not-required` | 7 |
| `STN-ACC-P020` — lift/stair step-free circulation core | `BID` | `buildable-after-site-and-supplier-freeze` | `deployment-specific` | `specified` | 1 |
| `STN-ACC-P030` — pedestrian overbridge/concourse structural and enclosure kit | `BID` | `buildable-after-site-and-supplier-freeze` | `deployment-specific` | `specified` | 1 |

### Frozen inputs

- topographical survey, land boundary, pedestrian demand and road interfaces
- site structural, geotechnical, fire/egress and accessibility approvals
- selected lift, enclosure and emergency-power configuration

### Controlled outputs

- approach, ramp, kerb, boundary and accessible-route drawings
- lift/stair/overbridge structure, enclosure and service-interface drawings
- evacuation, rescue, drainage and inspection-access plan

### Verification

- route gradient, crossfall, width, surface and obstacle survey
- structural, clearance and weatherproofing acceptance
- lift certification, fire recall, backup power and egress test

Boundary: No catalogue access arrangement substitutes for a site accessibility, egress, highway or structural approval.

## `STN-FRP-060` — wayside charging and traction substation interface pack

Delivery lane: `supplier-and-utility-interface`.

Drawings/interfaces: `STN-PWR-500`, `STN-PWR-510`.
Tools/gauges: `STN-TOOL-CHARGER-ALIGNMENT`, `STN-TOOL-EARTH-BOND-TEST`.

### Controlled products

| Product | Route | Catalogue maturity | Release path | Default | Variants |
|---|---|---|---|---|---:|
| `STN-CHG-P010` — station charging cabinet, protection, cable, and wayside connector kit | `BID` | `buildable-after-supplier-freeze` | `supplier-configuration` | `specified` | 6 |
| `STN-CHG-P020` — traction power substation transformer/rectifier and protection interface | `BID` | `buildable-after-utility-and-supplier-freeze` | `deployment-specific` | `specified` | 5 |

### Frozen inputs

- utility fault level, capacity, metering and protection requirements
- selected charger and transformer/rectifier supplier data
- released vehicle docking envelope and operational charging duty

### Controlled outputs

- equipment arrangement, foundation reaction and maintainability drawings
- single-line, protection, earthing, isolation and cable schedules
- vehicle/wayside datum, alignment, interlock and abort interface control

### Verification

- supplier FAT and protection-coordination review
- earthing, insulation, isolation and utility witness tests
- vehicle alignment, charge, abort and emergency-isolation SAT

Boundary: Rated catalogue power is a requirement, not authority to connect; the utility and electrical design authority retain release.

## `STN-FRP-070` — 1:9 turnout, actuation, detection, heating and track-end pack

Delivery lane: `hybrid-fabrication-and-supplier`.

Drawings/interfaces: `STN-TRK-600`, `STN-TRK-610`.
Tools/gauges: `STN-TOOL-TURNOUT-BENCH`, `STN-TOOL-BLADE-PROFILE-GAUGE`, `STN-TOOL-TRACK-GEOMETRY`.

### Controlled products

| Product | Route | Catalogue maturity | Release path | Default | Variants |
|---|---|---|---|---|---:|
| `STN-TRK-P010` — 1:9 UIC60 stock-rail, machined switch-blade, and closure-rail kit | `MAKE` | `buildable-after-controlled-drawing-release` | `reusable-definition` | `specified` | 2 |
| `STN-TRK-P020` — cast-manganese frog, check-rail, stretcher-bar, and mechanical-lock kit | `BID` | `buildable-after-supplier-freeze` | `supplier-configuration` | `specified` | 2 |
| `STN-TRK-P030` — prestressed turnout sleeper, slide-chair, and elastic-fastener set | `SOURCE` | `buildable-after-supplier-freeze` | `supplier-configuration` | `specified` | 2 |
| `STN-TRK-P040` — 6 kN nominal / 12 kN peak point-machine actuator, crank, and hand-wind kit | `BID` | `buildable-after-actuator-qualification` | `supplier-configuration` | `specified` | 2 |
| `STN-TRK-P050` — dual position detector, W-SBC interface, junction, and turnout harness kit | `SOURCE` | `buildable-after-hardware-freeze` | `supplier-configuration` | `specified` | 2 |
| `STN-TRK-P060` — 3 kW points-heating strip, thermostat, IP67 cabinet, isolation, and cabling kit | `SOURCE` | `buildable-after-climate-and-supplier-freeze` | `supplier-configuration` | `specified` | 2 |
| `STN-TRK-P070` — terminal stop-block, passive end marker, foundation, and fixing kit | `SOURCE` | `buildable-after-site-geometry-freeze` | `deployment-specific` | `specified` | 2 |

### Frozen inputs

- released wheel/rail interface, axle loads, route speed and climate envelope
- selected rail, frog, sleeper, actuator, detector and heater configurations
- site track alignment, signalling, drainage and track-end geometry

### Controlled outputs

- rail machining, switch/closure, gauge and weld drawings
- complete turnout assembly, harness, detection, heating and bench-test schedule
- site set-out, installation, stop-block and commissioning drawings

### Verification

- material, machining, weld/NDT and dimensional records
- bench throw, lock, detection, hand-wind and heating proof
- installed geometry, route/detection and stop-block acceptance

Boundary: The catalogue tangent and geometry do not release rail machining or site installation without controlled drawings and supplier qualifications.

## `STN-FRP-080` — depot site, drainage, track and throat-turnout pack

Delivery lane: `deployment-specific`.

Drawings/interfaces: `STN-DEP-700`, `STN-DEP-710`.
Tools/gauges: `STN-TOOL-DEPOT-SET-OUT`, `STN-TOOL-TRACK-GEOMETRY`, `STN-TOOL-DRAINAGE-TEST`.

### Controlled products

| Product | Route | Catalogue maturity | Release path | Default | Variants |
|---|---|---|---|---|---:|
| `STN-DEP-P010` — main-heavy depot site formation, drainage, service-road, and secure-boundary kit | `MAKE` | `buildable-after-site-design-release` | `deployment-specific` | `specified` | 1 |
| `STN-DEP-P020` — stabling, inspection, wash, and workshop track-panel/stop-block package | `MAKE` | `buildable-after-controlled-layout-release` | `deployment-specific` | `specified` | 1 |
| `STN-DEP-P030` — 1:9 depot-throat turnout assembly replicated from the terminal turnout standard | `MAKE` | `buildable-after-turnout-design-and-site-freeze` | `deployment-specific` | `specified` | 1 |

### Frozen inputs

- boundary/topographical/utility/geotechnical surveys and environmental approvals
- released fleet plan, movements, swept paths and maintenance concept
- controlled depot layout, gradients, drainage/outfall and track standards

### Controlled outputs

- earthworks, pavement, drainage, boundary and service-road drawings
- stabling, inspection, wash and workshop track-layout drawings
- turnout, stop-block, walkways, crossings and clearance-control schedule

### Verification

- formation, compaction, drainage and pavement records
- track geometry, clearance and stop-block proof
- route, detection and vehicle swept-path demonstration

Boundary: These are deployment drawings: the reference depot quantities do not authorize site works or fix a universal depot layout.

## `STN-FRP-090` — depot charging, energy, workshop and services integration pack

Delivery lane: `deployment-and-supplier`.

Drawings/interfaces: `STN-DEP-720`, `STN-DEP-730`.
Tools/gauges: `STN-TOOL-VEHICLE-LIFT-GAUGE`, `STN-TOOL-CHARGER-ALIGNMENT`, `STN-TOOL-ENERGY-ISOLATION-TEST`.

### Controlled products

| Product | Route | Catalogue maturity | Release path | Default | Variants |
|---|---|---|---|---|---:|
| `STN-DEP-P040` — outdoor/open-sided per-stall plug-in charger, isolation, suspended cable, and data-dock kit | `BID` | `buildable-after-supplier-and-energy-freeze` | `deployment-specific` | `specified` | 1 |
| `STN-DEP-P050` — depot PV canopy, inverter, microgrid switchgear, and separated outdoor stationary-battery package | `BID` | `buildable-after-energy-site-and-supplier-freeze` | `deployment-specific` | `specified` | 1 |
| `STN-DEP-P060` — main workshop, synchronized LM3 lift/bogie-change bay, overhaul/inspection bays, 40 t crane, wash plant, stores, and wheel-lathe package | `BID` | `buildable-after-building-and-equipment-freeze` | `deployment-specific` | `specified` | 1 |
| `STN-DEP-P070` — depot cooled controls room, LV, compressed-air, fire, lighting, CCTV, LAN, access-control, and maintenance-data kit | `BID` | `buildable-after-services-and-supplier-freeze` | `deployment-specific` | `specified` | 1 |

### Frozen inputs

- selected equipment loads, heat rejection, utilities and maintenance envelopes
- site building, fire, structural, energy and environmental approvals
- released LM3 lift points, bogie extraction path and service requirements

### Controlled outputs

- equipment layouts, foundations, clearances and replacement paths
- power/microgrid/battery isolation, fire, cooling and controls drawings
- workshop lift, crane, pit, wash, stores and maintenance-data schedules

### Verification

- supplier FAT, certification and equipment foundation survey
- charging, energy, fire, cooling and emergency-isolation SAT
- synchronised lift, mechanical lock, bogie extraction and crane proof

Boundary: Reference duties and envelopes do not select suppliers or release a depot building, stationary battery compound, crane or lifting system.

Global boundary: These packages define reusable drafting and deployment handoff scope. They are not approved fabrication/construction drawings, supplier selections, signed calculations, permits, surveys or performed acceptance records.
