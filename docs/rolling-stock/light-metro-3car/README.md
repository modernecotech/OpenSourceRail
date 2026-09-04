# `light-metro-3car` trainset package

This directory holds the dimensioned specification for the
**light-metro-3car** trainset — the default family for populations
300 k – 1 M per [RFC 0008 §5](../../rfcs/0008-rolling-stock-reference-design.md#5-family-selection-policy).
Samawah is one generated city instance that selects this family; the
trainset package itself is shared.

This package started as the v1 RFC 0008 bid specification and now
also links the current envelope-level FreeCAD/PNG outputs and generated
buildable trainset handoff. A domestic
rolling-stock fabricator can read the dimensions, masses, interfaces,
sub-assembly tree, fabrication sequence, procurement BOM skeleton, and
design-review CAD. The design deliberately favours a modern low-capex
factory: COTS rail subsystems wherever possible, simple cut/bend/weld
fabrication for the primary frame, and composite non-structural panels
for sides, roof fairings, multi-part fiberglass cabless cowls, and
interior liners. The side and roof skin now uses a common 1 m mould/clip
pitch, allowing the three-car exterior body to be installed in one
eight-hour shift after the frames pass paint and dimensional release.

## Contents

| File | Scope |
|---|---|
| [`general-arrangement.md`](general-arrangement.md) | Overall envelope, gauge clearance, consist diagram, floor heights, door positions |
| [`fabrication-plan.md`](fabrication-plan.md) | Cut-bend-weld primary structure, composite cladding, COTS module installation sequence |
| [`bogie.md`](bogie.md) | 2-axle standard bogie spec, wheel profile, suspension, brake mount |
| [`body.md`](body.md) | Welded steel underframe/spaceframe, composite side panels, end bulkheads, articulation interface frames |
| [`dedicated-parts-and-moulds.md`](dedicated-parts-and-moulds.md) | Discrete chassis/body, fascia/glass/lamp and interior fitout parts with dedicated moulds, trim nests, gauges and release evidence |
| [`modular-fiberglass-body.md`](modular-fiberglass-body.md) | 1 m clip-on fiberglass side/roof modules, keyed retainers, dry seals, one-shift trainset body route, and cost basis |
| [`roof-fitout.md`](roof-fitout.md) | Roof skin/fairing mould family, HVAC curb and skirts, PV/gland/antenna closeouts, walkways, keep-outs and assembly tests |
| [`exterior-finish-process.md`](exterior-finish-process.md) | Simplified white base plus pre-cut livery film and trial-only calcium-carbonate radiative roof coating qualification route |
| [`end-cowl.md`](end-cowl.md) | Identical A/B-end fiberglass cowl kit, cast split, laminate/tooling rules, glazing/sensor interfaces |
| [`cabin-fiberglass.md`](cabin-fiberglass.md) | Cabin FRP/phenolic ceiling liners, sidewall/window reveals, battery strake covers, vestibule/PRM trims, tooling, lay-up, trim, inspection, and repair instructions |
| [`articulation.md`](articulation.md) | Inter-car and train-to-train articulation/gangway modules: lower spherical pivot, upper links, bellows, turntable, trainline routing, and configurable open-end option |
| [`cots-integration.md`](cots-integration.md) | COTS/fabricated interface diagrams, part delineation, and assembly sequence |
| [`traction.md`](traction.md) | 800 V-class LFP packs, six PMSM/controller sets, direct-DC auxiliaries, station charging, and verification gates |
| [`localization-plan.md`](localization-plan.md) | Staged make/buy policy for bogies, doors, articulation, windows, seats, battery, traction, and body |
| [`interfaces.md`](interfaces.md) | Coupler, station charging, articulation, platform gap, TCN-E connector, aux power |
| [`bom-skeleton.md`](bom-skeleton.md) | Procurement BOM lines and marketplace listed-price consist totals |
| [`marketplace-price-anchors.md`](marketplace-price-anchors.md) | Alibaba/AliExpress line-by-line price anchors and qualification caveats |
| [`compliance.md`](compliance.md) | Standards matrix: EN 15227, EN 45545, EN 14363, EN 50155, ISO 3095, EN 12299 |
| [`drawing-register.md`](drawing-register.md) | v2 drawing IDs, supplier documents, inspection evidence, release gates |
| [`v2-release-checklist.md`](v2-release-checklist.md) | Fabrication-release gates: supplier envelopes, FEA, weld maps, drawings, NC data, harness routing, first-article evidence |

The governing visual/layout reference is
[`solar-metro-trainset.png`](../../../docs/assets/solar-metro-trainset.png):
white/silver body, green waist band, dark skirts, single dark panoramic-glass ends,
mixed bonded/rail-mounted roof PV, two low-floor door pairs per side per car, repeated self-contained cars with one powered bogie and one trailer bogie each,
and batteries under longitudinal seats. The end glazing is an open
driverless passenger view through heated RF-transparent laminated
glass with LED headlamp and marker-light clusters below it.
Because the cars use
standard bogies, each car has ~3 m high-floor end decks over the bogies
and a 350 mm, ~10 m low-floor centre door/PRM zone.
The front and rear passenger ends are not walled off by cab bulkheads;
the end saloon looks through the single panoramic glass pane at both ends
of the driverless train. The front/back exterior module is the same
multi-part fiberglass cast kit at both ends; its controlled design is
in [`end-cowl.md`](end-cowl.md).

The companion production graphic is
[`solar-metro-production-assembly.png`](../../../docs/assets/solar-metro-production-assembly.png).
It shows the intended manufacturing story: a welded 16.5 m datum frame,
bolt/bond COTS side, roof, door, glazing, battery-seat, and HVAC
modules, then lower the car onto standard bogies and repeat the module
to make the consist.

COTS passenger-facing modules are controlled by the supplier-neutral
envelope catalogue at
[`control-electronics/trainset-interiors.md`](../../../control-electronics/trainset-interiors.md).
Locally moulded or CNC-trimmed cabin fiberglass/phenolic liners,
battery strake covers, and vestibule trims are controlled in
[`cabin-fiberglass.md`](cabin-fiberglass.md).
The current vendor-fit shortlist is captured in
[`bom-skeleton.md`](bom-skeleton.md#vendor-fit-in-references) and names
rail product families for doors, windows, HVAC, flooring, seats,
lighting, PIS/audio, batteries, traction motors, brakes, couplers, and
front/back sensing while keeping the CAD envelope swap-friendly.

## Canonical Parametric Source

The parametric Python source files are the design basis for envelopes,
interfaces, and generated review views. The styled fiberglass end-cowl
A-surfaces are controlled by the surface-modelled LM3-BDY-155 release
CAD described in [`end-cowl.md`](end-cowl.md); those surfaces are
exported back into the drawing pack as neutral CAD.

| Source | Controls |
|---|---|
| [`trainset.py`](../../../design/component-catalogue/src/osr_mech/rolling_stock/trainset.py) | Family length, car count, repeated car motorisation, cowl/body/bogie assembly |
| [`car_body.py`](../../../design/component-catalogue/src/osr_mech/rolling_stock/car_body.py) | 16.5 m body module as layered CAD subassemblies: primary structure, exterior/glazing/doors, interior, HVAC ducts, LV/data routing, HV/PV/thermal/fire paths |
| [`modular_fiberglass_body.py`](../../../design/component-catalogue/src/osr_mech/rolling_stock/modular_fiberglass_body.py) | Sixteen 1 m cladding bays per car, side/roof module geometry, clips, anti-lift retainers, dry gaskets, and the eight-hour body schedule |
| [`sensor_cowl.py`](../../../design/component-catalogue/src/osr_mech/rolling_stock/sensor_cowl.py) | Identical A/B-end multi-part fiberglass cowl kit envelope with one dark panoramic glass pane, LED headlamps, marker lights, and T-OBS visual interface |
| [`systems.py`](../../../design/component-catalogue/src/osr_mech/rolling_stock/systems.py) | Couplers, detailed articulations/gangways, batteries, rooftop solar/MPPT package, DC charge/protection racks, doors, electronics, charging, T-OBS packs |
| [`bogie/`](../../../design/component-catalogue/src/osr_mech/rolling_stock/bogie/) | Powered and trailer bogie assemblies |
| [`cad_templates/rolling_stock.py`](../../../design/component-catalogue/src/osr_mech/cad_templates/rolling_stock.py) | Sheet-metal/chassis manufacturing templates |
| [`buildable_trainset.py`](../../../design/component-catalogue/src/osr_mech/buildable_trainset.py) | Product-tree manifest, definitions, assembly integration design, and unsigned shop travelers |
| [`exterior_finish.py`](../../../design/component-catalogue/src/osr_mech/rolling_stock/exterior_finish.py) | Machine-readable finish zones, prohibited coverage, livery-film process, CaCO3 qualification gates and review geometry |

## Buildable handoff package

The generated buildable package lives under
[`design/component-catalogue/catalog/buildable-trainset/`](../../../design/component-catalogue/catalog/buildable-trainset/).
Use it as the bridge from concept CAD to build planning:

This is specifically the `light-metro-3car` detailed reference. The integrated
city twin uses these parts, moulds and travellers only when that family is
selected. Other-family cities retain their generated family cost and programme
but show an explicit family-definition hold until equivalent detailed packages
are engineered and released.

| Artifact | Use it for |
|---|---|
| [`buildable-trainset-manifest.md`](../../../design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.md) | Parts → subassemblies → assemblies → trainset tree, quantities, parentage, acceptance gates |
| [`train-end-interface.md`](../../../design/component-catalogue/catalog/buildable-trainset/train-end-interface.md) | Single configurable train-end interface that can select either the panoramic glass front/end or the optional mid open train-to-train connection |
| [`critical-path.md`](../../../design/component-catalogue/catalog/buildable-trainset/critical-path.md) | Rough first-train critical path, parallel fabrication plan, labour estimate, and minimum space model |
| [`factory-plan.md`](../../../design/component-catalogue/catalog/buildable-trainset/factory-plan.md) | Pilot factory sizing: chassis fabrication, bogie integration, moulding shop, final assembly, enclosed area, yard, machinery, and rough equipment prices |
| [`trainset-build-cost.md`](../../../design/component-catalogue/catalog/buildable-trainset/trainset-build-cost.md) | Recalculated 3-car trainset budget, including the explicit seats/floors/lighting/HVAC/windows/doors scope already inside the direct-module bucket |
| [`mass-budget.md`](../../../design/component-catalogue/catalog/buildable-trainset/mass-budget.md) | Reconciled 75.308 t modeled subtotal, 3.442 t engineering reserve, and 78.75 t controlled planning tare |
| [`mass-closure-ledger.md`](../../../design/component-catalogue/catalog/buildable-trainset/mass-closure-ledger.md) | All 120 product rows mapped to the nine mass categories, evidence routes for 117 active rows, the 73.376 t lightest existing design-space study, and recovery-reaction linkage |
| [`joint-control-schedule.md`](../../../design/component-catalogue/catalog/buildable-trainset/joint-control-schedule.md) | Machine-readable joining classes, torque authority, and release state for all 108 integration joints |
| [`definitions/index.md`](../../../design/component-catalogue/catalog/buildable-trainset/definitions/index.md) | Drawing/RFQ definitions for every fabricated part, external component, subassembly, assembly, and trainset node, including structured material and process specs |
| [`travelers/index.md`](../../../design/component-catalogue/catalog/buildable-trainset/travelers/index.md) | Unsigned shop travelers with material/process controls, operation routers, labor estimates, tooling IDs, QA gates, revision approvals, signoff blocks, and NCR/deviation logs |
| [`supplier-anchors.md`](../../../design/component-catalogue/catalog/buildable-trainset/supplier-anchors.md) | Real manufacturer-family anchor, procurement state, known fit gaps and controlled local-equivalent route for every bought-in product row |
| [`manufacturing-methods.md`](../../../design/component-catalogue/catalog/buildable-trainset/manufacturing-methods.md) | All 120 product links, timed mould/film/coating/seal/floor/fixture/motor methods, joining parts, hold points and external design references |
| [`FreeCAD part/assembly library`](../../../design/component-catalogue/models/cad/README.md) | 120 individual native part documents plus 26 subassembly/car/final-assembly documents, hashes and reachability checks |
| [`IFC4.3 part/assembly library`](../../../engineering/models/bim/reference/README.md) | Matching split geometric IFC files with retained product classes and hierarchy |
| [`lm3-manufacturing-tooling.FCStd`](../../../design/component-catalogue/models/cad/lm3-manufacturing-tooling.FCStd) | Selectable FreeCAD review objects for 30 mould, trim-nest, glass/lamp gauge, finish, stand and test-tool families |
| [`lm3-manufacturing-reference.ifc`](../../../engineering/models/bim/reference/lm3-manufacturing-reference.ifc) | IFC4.3 product hierarchy, typed doors/windows/floor/furniture/motor, 59 tasks, method assignments and multi-part tooling geometry |
| [`current-design-buildability-review.md`](../../../design/component-catalogue/catalog/buildable-trainset/current-design-buildability-review.md) | Current green/yellow/red closure status before first steel cut |

Typical first-article workflow:

1. Start at the buildability review and resolve release blockers.
2. Use the manifest to choose the next build cell or RFQ package.
3. Open that node's definition to create controlled drawings, supplier
   envelopes, material specs, process specs, or fixture requirements.
4. Open the matching traveler to plan operation sequence, labor,
   tooling, QA gates, and signoff responsibility.
5. During a real build, fill approval/signature fields and attach actual
   inspection evidence; generated traveler templates are intentionally
   unsigned.

## Current CAD / PNG Design Outputs

The whole-train part map and COTS interface diagrams are in
[`cots-integration.md`](cots-integration.md).

The present train design now has envelope-level definitions for the
major train assemblies, sub-assemblies, repeated components, and
body service layers. The `car_body()` assembly is deliberately nested
as components -> subassemblies -> final car body, so CAD review can
hide/show the primary steel shell, exterior solar-train skin, passenger
interior, HVAC ducting, LV/data harnesses, high-voltage traction/PV
routing, thermal-management pipes, and battery fire vent paths. The
models are supplier-neutral CAD geometry in
[`design/component-catalogue/src/osr_mech/rolling_stock`](../../../design/component-catalogue/src/osr_mech/rolling_stock)
and render to these design-review and manufacturing-method PNGs:

| Output | Scope |
|---|---|
| [`trainset-light-metro-3car.png`](../../../docs/screenshots/trainset-light-metro-3car.png) | Final 3-car trainset assembly with car bodies, bogies, single panoramic-glass cowls, couplers, inter-car articulation, and train systems |
| [`end-glass-cowl.png`](../../../docs/screenshots/end-glass-cowl.png) | Cabless trainset end close-up with multi-part fiberglass cowl casts, one heated laminated panoramic glass pane, bonded edge frame, demist busbars, and washer/service hardware |
| [`trainset-car-detail.png`](../../../docs/screenshots/trainset-car-detail.png) | 16.5 m layered car body: structure, door/window openings, glazing, livery, roof PV/HVAC, interior, ducts, LV/data and HV/thermal routes |
| [`trainset-car-body-structure.png`](../../../docs/screenshots/trainset-car-body-structure.png) | Primary fabricated structure: shell, 10 m low-floor pan, side sills, crossmembers, roof cantrails, door portals, window posts, end rings, and bogie clearance envelopes |
| [`trainset-car-body-bogie-subassembly.png`](../../../docs/screenshots/trainset-car-body-bogie-subassembly.png) | Single-car structure with standard motor/trailer bogies under the ~3 m raised high-floor end zones |
| [`trainset-car-body-exterior.png`](../../../docs/screenshots/trainset-car-body-exterior.png) | Solar-train exterior layer: glazing, door leaves, livery band, mixed bonded/rail-mounted roof PV/HVAC, and service skirts |
| [`trainset-roof-solar-system.png`](../../../docs/screenshots/trainset-roof-solar-system.png) | Per-car rooftop solar package with bonded flexible laminates, raised rigid panels, rails, clamps, junction boxes, fire isolators, MPPT combiner, and downlink gland |
| [`trainset-car-body-interior.png`](../../../docs/screenshots/trainset-car-body-interior.png) | Passenger interior layer: under-seat battery strakes, benches, PRM bays, grab poles, handrails, and PIS |
| [`trainset-car-body-services.png`](../../../docs/screenshots/trainset-car-body-services.png) | Service layers: HVAC ducts, LV/data trays, lighting, CCTV/intercoms, HV/PV routing, coolant, and battery fire vents |
| [`trainset-interior-fit-out.png`](../../../docs/screenshots/trainset-interior-fit-out.png) | COTS passenger fit-out envelopes inside the car body |
| [`trainset-body-sheet-metal-kit.png`](../../../docs/screenshots/trainset-body-sheet-metal-kit.png) | Sheet-metal/chassis manufacturing kit: underframe, bolsters, coupler pockets, side posts, rails, roof bows, end rings |
| [`trainset-factory-layout.png`](../../../docs/screenshots/trainset-factory-layout.png) | Pilot factory layout with one 55 m final bay, chassis/body-frame fixtures, GFRP moulding/trim, bogie assembly, interior/HVAC kits, paint, stores, QA, yard staging, and short test access |
| [`trainset-assembly-method-flow.png`](../../../docs/screenshots/trainset-assembly-method-flow.png) | Parallel first-article method plan tying critical-path tasks to chassis/body frame, GFRP modules, bogies, interior kits, doors/windows/roof, HV/electrical work, articulation/static testing, and dynamic release |
| [`trainset-gfrp-moulding-method.png`](../../../docs/screenshots/trainset-gfrp-moulding-method.png) | One-metre glass-fibre module method: mould/cure, demould/trim, insert/seal, master-frame dry fit, and clip-on installation to the painted carbody |
| [`trainset-bogie-marriage-method.png`](../../../docs/screenshots/trainset-bogie-marriage-method.png) | Bogie-to-carbody marriage method with mobile lifting columns, accepted motor/trailer bogies, centre-pivot/air-spring datum checks, and static release hold points |
| [`trainset-car-systems.png`](../../../docs/screenshots/trainset-car-systems.png) | One self-contained car systems package: four door cassettes, platform interlocks, batteries, rooftop PV package, traction/charge power rack, charging connector, and accessibility/safety reservations |
| [`trainset-battery-pack.png`](../../../docs/screenshots/trainset-battery-pack.png) | Eight LFP module envelopes plus HV contactor, fuse, BMS cabinet, outward vent, off-gas detection, and localized mist interfaces per car |
| [`trainset-door-system.png`](../../../docs/screenshots/trainset-door-system.png) | Door cassette pair with sill gap fillers, locks, and external emergency releases |
| [`trainset-electronics-cabinet.png`](../../../docs/screenshots/trainset-electronics-cabinet.png) | Per-end T-ECU/S, T-ECU/A, and crashworthy event recorder, two sets per trainset |
| [`trainset-end-coupler.png`](../../../docs/screenshots/trainset-end-coupler.png) | Scharfenberg Type 10 coupler, electric-head carrier, and EN 15227 crash absorber envelope |
| [`trainset-inter-car-articulation.png`](../../../docs/screenshots/trainset-inter-car-articulation.png) | Detailed inter-car articulation: lower spherical joint, anti-lift keeper, upper links, double-wall bellows, turntable floor, trainline routing, and kinematic envelopes; the same architecture now has a generated train-to-train open-end option in the buildable handoff |
| [`trainset-tobs-sensor-pack.png`](../../../docs/screenshots/trainset-tobs-sensor-pack.png) | T-OBS LIDAR, mmWave radar, stereo camera, and ultrasonic sensor envelopes |
| [`bogie-motor.png`](../../../docs/screenshots/bogie-motor.png) | Powered bogie assembly with frame, wheelsets, motors, gearboxes, suspension, and brakes |
| [`bogie-trailer.png`](../../../docs/screenshots/bogie-trailer.png) | Trailer bogie assembly using the common frame and suspension envelope |

## FreeCAD Assembly And FEA Screenshot Review

These screenshots are generated from the FreeCAD `.FCStd` review
documents and the FreeCAD/CalculiX screening-output document. The
assembled and exploded states are view groups in the FreeCAD files, not
separate hand-positioned drawings.

| Trainset FreeCAD review |
|---|
| ![FreeCAD trainset light metro 3-car](../../../docs/screenshots/freecad/freecad-trainset-light-metro-3car.png) |

| Chassis + bogie assembled | Chassis + bogie exploded |
|---|---|
| ![Chassis bogie assembled](../../../docs/screenshots/freecad/freecad-chassis-bogie-assembled.png) | ![Chassis bogie exploded](../../../docs/screenshots/freecad/freecad-chassis-bogie-exploded.png) |

| Full body assembled | Full body exploded |
|---|---|
| ![Full body assembled](../../../docs/screenshots/freecad/freecad-full-body-assembled.png) | ![Full body exploded](../../../docs/screenshots/freecad/freecad-full-body-exploded.png) |

| FEA screening models | Chassis FEA | Bogie FEA | Body FEA |
|---|---|---|---|
| ![FEA screening models](../../../docs/screenshots/freecad/freecad-fea-screening-models.png) | ![Chassis FEA](../../../docs/screenshots/freecad/freecad-fea-chassis-bogie-screen.png) | ![Bogie FEA](../../../docs/screenshots/freecad/freecad-fea-bogie-frame-screen.png) | ![Body FEA](../../../docs/screenshots/freecad/freecad-fea-full-body-frame-screen.png) |

The actual solver-result PNGs below are generated from CalculiX
`.dat` fields: deformed beam shape, support/load markers, and von Mises
stress colour scale.

| Chassis service gravity | Chassis AW3 proof | Chassis track twist |
|---|---|---|
| ![Chassis service FEA result](../../../docs/screenshots/freecad/freecad-fea-chassis-bogie-screen-result.png) | ![Chassis AW3 proof FEA result](../../../docs/screenshots/freecad/freecad-fea-chassis-aw3-proof-screen-result.png) | ![Chassis track twist FEA result](../../../docs/screenshots/freecad/freecad-fea-chassis-track-twist-screen-result.png) |

| Bogie vertical | Bogie brake/traction | Full body vertical | Full body lateral sway |
|---|---|---|---|
| ![Bogie vertical FEA result](../../../docs/screenshots/freecad/freecad-fea-bogie-frame-screen-result.png) | ![Bogie brake traction FEA result](../../../docs/screenshots/freecad/freecad-fea-bogie-brake-traction-screen-result.png) | ![Full body vertical FEA result](../../../docs/screenshots/freecad/freecad-fea-full-body-frame-screen-result.png) | ![Full body lateral sway FEA result](../../../docs/screenshots/freecad/freecad-fea-full-body-lateral-sway-screen-result.png) |

| Train-to-train joint vertical | Train-to-train joint lateral sway |
|---|---|
| ![Train-to-train joint vertical FEA result](../../../docs/screenshots/freecad/freecad-fea-train-to-train-joint-vertical-screen-result.png) | ![Train-to-train joint lateral sway FEA result](../../../docs/screenshots/freecad/freecad-fea-train-to-train-joint-lateral-sway-screen-result.png) |

The latest screening summary is
[`design/component-catalogue/catalog/fea/screening-summary.md`](../../../design/component-catalogue/catalog/fea/screening-summary.md).
The current FEA catalog includes solver-backed train-to-train local
joint cases: vertical passenger/gangway loading and lateral/racking.
The source FreeCAD review documents are catalogued in
[`design/component-catalogue/models/cad/README.md`](../../../design/component-catalogue/models/cad/README.md),
and raw CalculiX output folders are catalogued in
[`design/component-catalogue/catalog/fea/README.md`](../../../design/component-catalogue/catalog/fea/README.md).

The same `.FCStd` documents can also be exported to local STL render
meshes and rendered with Blender/Cycles for README-grade engineering-clay
views:

| Trainset clay render | Full-body clay render | Chassis/bogie clay render |
|---|---|---|
| ![Blender Cycles trainset render](../../../docs/screenshots/freecad/blender-trainset-light-metro-3car.png) | ![Blender Cycles full body render](../../../docs/screenshots/freecad/blender-full-body-assembly.png) | ![Blender Cycles chassis bogie render](../../../docs/screenshots/freecad/blender-chassis-bogie-assembly.png) |

After the low-floor chassis rework, the chassis screen is inside the
25 mm deflection target: 9.8 mm maximum displacement under the 360 kN
service-load screen. The broadened lateral body sway screen is now
inside the 20 mm screening target at 18.1 mm maximum displacement, with
stress still low at 40.2 MPa. The local train-to-train joint screens are
also inside target after the deeper end-ring, portal, threshold,
drawbar, and upper-link section update: 4.4 mm vertical displacement
against a 12 mm target and 2.3 mm lateral displacement against a 16 mm
target.

## Mechanical Interface Component Gallery

These component images are generated from
[`mechanical_interfaces.py`](../../../design/component-catalogue/src/osr_mech/rolling_stock/mechanical_interfaces.py)
and match the tracked FreeCAD assembly-review documents under
[`design/component-catalogue/models/cad/`](../../../design/component-catalogue/models/cad/).

| Bogie to chassis | Bogie to motor | Low-floor chassis |
|---|---|---|
| ![Bogie to chassis connector](../../../docs/screenshots/rolling-stock/interfaces/bogie-to-chassis-connector.png) | ![Bogie to motor connector](../../../docs/screenshots/rolling-stock/interfaces/bogie-to-motor-connector.png) | ![Low-floor chassis](../../../docs/screenshots/rolling-stock/interfaces/low-floor-chassis.png) |

| Side body frame | Composite body and roof | Window installations |
|---|---|---|
| ![Side body frame attachments](../../../docs/screenshots/rolling-stock/interfaces/side-body-frame-attachments.png) | ![Composite body roof attachments](../../../docs/screenshots/rolling-stock/interfaces/composite-body-roof-attachments.png) | ![Window installations](../../../docs/screenshots/rolling-stock/interfaces/window-installations.png) |

| Door mounts | Door design | Door installations |
|---|---|---|
| ![Door mounts](../../../docs/screenshots/rolling-stock/interfaces/door-mounts.png) | ![Door design](../../../docs/screenshots/rolling-stock/interfaces/door-design.png) | ![Door installations](../../../docs/screenshots/rolling-stock/interfaces/door-installations.png) |

| Door to body | Cabin flooring | Battery installations |
|---|---|---|
| ![Door to body installations](../../../docs/screenshots/rolling-stock/interfaces/door-to-body-installations.png) | ![Cabin flooring](../../../docs/screenshots/rolling-stock/interfaces/cabin-flooring.png) | ![Battery installations](../../../docs/screenshots/rolling-stock/interfaces/battery-installations.png) |

| Benches over batteries | Internal lighting | HVAC roof and ducting |
|---|---|---|
| ![Bench on battery installations](../../../docs/screenshots/rolling-stock/interfaces/bench-on-battery-installations.png) | ![Internal lighting installation](../../../docs/screenshots/rolling-stock/interfaces/internal-lighting-installation.png) | ![HVAC roof ducting installation](../../../docs/screenshots/rolling-stock/interfaces/hvac-roof-ducting-installation.png) |

| Screens and speakers | External lighting and LIDAR | Train connector mounts |
|---|---|---|
| ![Screen speaker mountings](../../../docs/screenshots/rolling-stock/interfaces/screen-speaker-mountings.png) | ![External lighting and LIDAR](../../../docs/screenshots/rolling-stock/interfaces/external-lighting-lidar-system.png) | ![Train connector mounts](../../../docs/screenshots/rolling-stock/interfaces/train-connector-mount-pair.png) |

| Complete mechanical interface package |
|---|
| ![Complete mechanical interface package](../../../docs/screenshots/rolling-stock/interfaces/mechanical-interface-package.png) |

The tracked generated CAD review artifacts are:
[`trainset-light-metro-3car.FCStd`](../../../design/component-catalogue/models/cad/trainset-light-metro-3car.FCStd),
[`chassis-bogie-assembly-states.FCStd`](../../../design/component-catalogue/models/cad/chassis-bogie-assembly-states.FCStd),
[`full-body-assembly-states.FCStd`](../../../design/component-catalogue/models/cad/full-body-assembly-states.FCStd), and
[`fea-screening-models.FCStd`](../../../design/component-catalogue/models/cad/fea-screening-models.FCStd).
The matching electronics host-class quantities are mirrored in
[`control-electronics/rolling-stock-integration.md`](../../../control-electronics/rolling-stock-integration.md).

The cross-domain [depot bogie-change interface](../../civil/depot-bogie-change-interface.md)
now ties the installed LM3 jack pads to the main-heavy depot lift heads through
one tested datum contract. It remains a design-reference coordination assembly
until vehicle reactions, underframe calculations, foundation design, selected
lifting equipment, proof tests, and local safety approval are released.

The [portable field-rerailing concept](field-rerailing-concept.md) now screens
the controlled 78.75 t tare and lighter sensitivity cases against a rail-rated
200 kN hydraulic cylinder envelope. It also pairs the J1--J4 vehicle interface
with an optional [wayside access interface](../../civil/wayside-rerailing-access-interface.md)
for hardstanding, equipment offload, transverse bridge bearing and controlled
access. Automotive scissor jacks and unilateral lifts are explicitly outside
the design basis.

The generated [product-level mass ledger](../../../design/component-catalogue/catalog/buildable-trainset/mass-closure-ledger.md)
keeps the lighter body/bogie option honest: its modeled subtotal is 73.376 t,
or 76.818 t with the current reserve retained, but it remains an unpromoted
study until all active row masses, individual-car weights, axle loads, centres
of gravity and affected structural/dynamic evidence are accepted.

The remaining gaps are not missing assemblies in the train envelope;
they are controlled detail-design and release tasks: frozen supplier exact envelopes,
one-car-first manufacturing drawings, weld maps, NDT acceptance sheets,
FEA-ready brackets, harness clamp locations, manufacturing tolerances,
weight-and-balance evidence, and release drawings listed in
[`drawing-register.md`](drawing-register.md) and
[`v2-release-checklist.md`](v2-release-checklist.md).

## Reference envelope (from RFC 0008 §1)

| Parameter | Value |
|---|---|
| Cars | 3 (articulated) |
| Overall length (over couplers) | 49.5 m |
| Tare mass target | 78.75 t controlled planning tare: 75.308 t modeled subtotal + 3.442 t engineering reserve; drawing-package mass closure still required |
| Axle load (AW3 crush) | ≤ 14 t |
| Max speed | 25 m/s (90 km/h) |
| Seats | 60 longitudinal seats |
| Passenger capacity (AW2) | 360 (seated + standing) |
| Passenger capacity (AW3 crush) | 480 short-duration crush load |
| Onboard battery | 540 kWh usable / 675 kWh gross LFP (180 / 225 kWh per car), in externally accessed, saloon-isolated side enclosures beneath the seat zone with outward venting |
| Peak onboard motor output | 1.8 MW operational cap (2.1 MW installed short-duration capability) |
| Floor height (above ToR) | 350 mm, ~10 m low-floor centre door/PRM zone; 760 mm, ~3 m high-floor end decks over standard bogies |
| Gauge | 1 435 mm standard gauge |

## What v1 does NOT include

- Production-detail MCAD files, selected supplier internals, tolerance
  stacks, manufacturing drawings, and custom-board KiCad files only
  where a deployment chooses custom electronics (v2).
- Detailed finite-element analysis (v3 — homologation phase).
- Operator-specific livery artwork and approved colour masters; the shared
  base-protection, pre-cut film and trial-only cool-roof process is defined.

## How to execute this package

1. A fabricator reads [`general-arrangement.md`](general-arrangement.md)
   + [`interfaces.md`](interfaces.md) to size their production
   line tooling.
2. [`fabrication-plan.md`](fabrication-plan.md) defines the shop
   route: tube/plate cutting, press-brake bends, welding fixtures,
   composite bonding, and COTS module installation.
3. Use the generated [buildable manifest](../../../design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.md)
   to see the current product-tree quantities and parent/child assembly
   structure.
4. [`assembly-plan.md`](assembly-plan.md) defines how those parts and
   subassemblies join: weld, bolt, bond, gasket, harness, coolant,
   articulation, bogie marriage, end-cowl, and final trainset sequence.
5. Use the generated [definition pack](../../../design/component-catalogue/catalog/buildable-trainset/definitions/index.md)
   to start controlled drawings, RFQs, material specs, process specs,
   and fixture requirements.
6. Use the generated [shop traveler pack](../../../design/component-catalogue/catalog/buildable-trainset/travelers/index.md)
   to plan operation routers, labor, tooling IDs, QA gates, signoff
   responsibilities, and NCR/deviation records.
7. [`bom-skeleton.md`](bom-skeleton.md) gives the procurement team
   the source-identified parts (off-the-shelf commodity) and the
   TBD parts (where the fabricator bids on make-or-buy).
8. [`drawing-register.md`](drawing-register.md) turns the current CAD
   package and v2 detail work into controlled drawing IDs, supplier
   document requirements, and release gates.
9. [`compliance.md`](compliance.md) lists the test campaigns the
   type-approval needs; each is a separately-tendered scope with
   an accredited test house.
10. The current FreeCAD/PNG package supports design review. The v2
   production CAD pack adds cut-lists, NC code, flat patterns,
   tolerance-controlled drawings, and welding-robot path artifacts for
   the shop floor.

## Licensing

v1 specification: CC-BY-SA 4.0.
v2 CAD + drawings: CERN-OHL-S v2, matching the hardware licensing
from [ARCHITECTURE.md §9](../../ARCHITECTURE.md#9-roadmap).
