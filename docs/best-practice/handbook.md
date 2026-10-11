# OpenSourceRail best-practice handbook

Research baseline 2026-10-11 · generated from the reviewed open register.

54 practice cards, 43 primary references and 356 explicitly mapped definitions. Coverage means guidance exists for the scoped inventory. Project adoption, production release and physical qualification remain open.

The design, materials, assembly, inspection and maintenance guidance below is original OSR synthesis. References support the method or application context; public standard scopes and supplier examples do not establish clause conformity or product performance.

Use [OSR-BP-001](../standards/OSR-BP-001.md) and the [research plan](research-plan.md). The [component mapping](../../engineering/best_practice/component-guidance.csv), [coverage audit](../../engineering/best_practice/coverage.json) and [open verification plan](../../engineering/best_practice/verification-plan.json) are generated together.

## Scope and coverage

| Definition kind | Mapped |
|---|---:|
| civil-type | 19 |
| software-package | 60 |
| station-assembly | 10 |
| station-product | 50 |
| station-system | 7 |
| subsystem-template | 64 |
| train-assembly | 26 |
| train-product | 120 |

Station variants: depot-terminal, halt, interchange, interchange-elevated, major, standard, terminal.

Optional zero-quantity train products are retained as configuration alternatives; they are not counted as installed. Civil coordination envelopes retain their interface status. Station applicability records preserve titles and quantities across variants. A kit mapping does not decompose its individual bolts, terminals, seals or consumables. Software source titles may contain SIL/GoA targets; they are not achieved integrity claims. Common lifecycle cards require applicability review; physical material/tool checks do not automatically apply to pure software.

## Practice index

| Practice | Domain | Responsible role |
|---|---|---|
| [Configuration, requirements and open interfaces](#configuration) | lifecycle | systems engineer |
| [Reliability, availability, maintainability and safety](#rams) | lifecycle | safety assurance lead |
| [Datums, measurement and acceptance decisions](#metrology) | lifecycle | quality/metrology lead |
| [Material qualification and supplier equivalence](#materials) | lifecycle | materials engineer |
| [Qualified manufacture, travelers and quality learning](#manufacturing) | lifecycle | production/quality lead |
| [Lifecycle energy, carbon, repair and circularity](#environment) | lifecycle | environment/lifecycle lead |
| [Secure software, networks and maintenance access](#cybersecurity) | lifecycle | cybersecurity/software lead |
| [Carbody load paths, lifting and equipment mounts](#carbody) | train | structural/mechanical engineer |
| [Composite shells, liners and bonded inserts](#composites) | train | composites/process engineer |
| [Coatings, graphics, seals and weathering](#coatings) | train | surface/materials engineer |
| [Fasteners, captive service rails and retained fixtures](#fasteners) | train | joint/assembly engineer |
| [Bogie frames, guards and torque reaction](#bogie-frame) | train | bogie structural engineer |
| [Wheelsets, rail profiles and running contact](#wheelsets) | train | vehicle/track dynamics engineer |
| [Axleboxes, bearings, lubrication and sensing](#axleboxes) | train | bearing/running-gear engineer |
| [Primary/secondary suspension and body connection](#suspension) | train | suspension/dynamics engineer |
| [Service, emergency and parking braking with adhesion](#braking) | train | brake/safety engineer |
| [Motors, gearboxes, couplings and thermal duty](#traction) | train | traction engineer |
| [Traction batteries, enclosures and safe removal](#batteries) | train | battery/electrical safety engineer |
| [HV/LV power distribution, bonding and harnesses](#hv-distribution) | train | electrical integration engineer |
| [Cooling, fluids, pneumatic auxiliaries and drains](#cooling) | train | thermal/fluid engineer |
| [HVAC, air distribution and passenger comfort](#hvac) | train | HVAC engineer |
| [Passenger doors, carriers and boarding interlocks](#doors) | train | door/control engineer |
| [Glazing, retention, seals and replacement](#glazing) | train | glazing/joint engineer |
| [Floors, seats, handrails and passenger fixtures](#interiors) | train | interior/accessibility engineer |
| [Couplers, articulation, gangways and flexible services](#gangways) | train | coupling/articulation engineer |
| [Train control, navigation and automated lifecycle](#automation) | train | train-control/safety engineer |
| [Train/wayside communications, timing and event records](#communications) | train | communications/software engineer |
| [Information, lighting, intercom and security equipment](#passenger-systems) | train | passenger systems engineer |
| [Fire detection, containment, evacuation and rescue](#fire-response) | system | fire/life-safety engineer |
| [Survey, alignment, gauge and route configuration](#survey) | infrastructure | survey/track engineer |
| [Ground investigation, foundations and settlement](#ground) | infrastructure | geotechnical/foundation engineer |
| [Precast/prestressed beams, decks, piers and platform units](#precast) | infrastructure | civil structural/production engineer |
| [Bridge bearings, joints, jacking and replaceability](#bearings) | infrastructure | bridge/interface engineer |
| [Logistics, lifting, temporary works and site assembly](#erection) | infrastructure | construction/temporary works engineer |
| [Drainage, water management and climate resilience](#drainage) | infrastructure | drainage/environment engineer |
| [Rails, fastenings, slabs and wheel/rail interfaces](#track) | infrastructure | track/vehicle integration engineer |
| [Turnouts, point machines, detection and track ends](#turnouts) | infrastructure | turnout/signalling engineer |
| [Wayside signalling, detection and movement authority](#signalling) | infrastructure | signalling safety engineer |
| [Platforms, boarding gaps and platform doors](#platforms) | station | station/vehicle interface engineer |
| [Station steel, solar roofs and safe access](#canopies) | station | station structural/roof engineer |
| [Station LV services, UPS, cabinets and lighting](#station-services) | station | station electrical/MEP engineer |
| [Station information, fares, CCTV and help points](#station-passenger) | station | passenger systems/operations engineer |
| [Approaches, lifts, escalators, stairs and overbridges](#vertical-access) | station | access/vertical transport engineer |
| [Train/wayside charging and traction substations](#charging) | infrastructure | traction power/charging engineer |
| [PV, stationary storage and microgrid integration](#solar-storage) | infrastructure | energy/electrical engineer |
| [Depot lifts, workshops, wash, lathe and isolation](#depots) | operations | depot/workshop engineer |
| [Service planning, degraded operation and incident response](#operations) | operations | operator/operations lead |
| [Maintenance, spares, condition monitoring and return to service](#maintenance) | operations | maintenance authority |
| [Level crossings, public interfaces and intrusion](#level-crossings) | infrastructure | crossing/public safety engineer |
| [Integrated vehicle, track, bridge and station dynamics](#vehicle-track-system) | system | integrated vehicle/civil engineer |
| [Integrated train, charger, route and energy supply](#energy-system) | system | system energy engineer |
| [Integrated accessible passenger journey and evacuation](#boarding-system) | system | accessibility/fire/operations lead |
| [Integrated safety control, power, doors and operations](#control-system) | system | system safety/control engineer |
| [Software requirements, deterministic behaviour and target validation](#software-lifecycle) | software | software assurance lead |

<a id="configuration"></a>

## Configuration, requirements and open interfaces

Responsible role: systems engineer. Applied to 356 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-001, STD-CTRL-002, STD-CTRL-010, STD-CTRL-016. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Allocate measurable requirements and hazards to named owners. Publish mechanical, electrical, fluid and control interface revisions.

**Materials:** Bind candidate and released grades to distinct states. Preserve third-party licensing and source provenance.

**Assembly:** Use revision-bound drawings and portable JSON/CSV work records. Identify each physical part by serial or lot.

**Inspection:** Reconcile BOM, CAD, installation and retained evidence identities. Review changes across all affected interfaces.

**Maintenance:** Keep as-built and as-maintained configurations. Record approved substitutions and obsolescence.

**Verification:** Independent requirement-to-verification matrix review. Round-trip interface and unit reconciliation.

**Open evidence and decisions:** Accepted project configuration and authority. Complete physical allocation of kits and area quantities.

Basis: [NASA: Systems engineering handbook: interfaces and verification](https://www.nasa.gov/reference/system-engineering-handbook-appendix/), [buildingSMART: IFC railway domain and open exchange](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcRailway.htm), [ISO: ISO 22163:2023 railway quality-management scope](https://www.iso.org/standard/79427.html).

<a id="rams"></a>

## Reliability, availability, maintainability and safety

Responsible role: safety assurance lead. Applied to 356 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-001, STD-CTRL-003, STD-CTRL-004, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Define service concept and normal, degraded, rescue and maintenance modes. Allocate hazards and common-cause failures across system boundaries.

**Materials:** Use environment and life assumptions in failure analysis. Identify safety-significant materials and consumables.

**Assembly:** Identify safety holds and competence requirements. Preserve independent checks for critical installation.

**Inspection:** Trace mitigations to evidence and residual risk disposition. Retain failures and nonconformances.

**Maintenance:** Feed service failures into controlled risk review. Qualify interval changes before adoption.

**Verification:** Independent hazard and failure-analysis review. Fault-injection and emergency exercises under approved protocols.

**Open evidence and decisions:** Project risk criteria and assurance independence. Safety integrity allocation and applicable complete standards.

Basis: [IEC: IEC 62278-1:2025](https://webstore.iec.ch/en/publication/68933), [FTA: Public Transportation Agency Safety Plans](https://www.transit.dot.gov/PTASP).

<a id="metrology"></a>

## Datums, measurement and acceptance decisions

Responsible role: quality/metrology lead. Applied to 356 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-012, STD-CTRL-013. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Specify functional datums and signed tolerance chains. Define acceptance limits and uncertainty decision rules before measurement.

**Materials:** Include thermal expansion and surface condition. Separate supplier nominal data from measured properties.

**Assembly:** Use qualified fixtures and calibrated tools. Record temperature, setup and measurement revision.

**Inspection:** Retain uncertainty and tool-validity records. Treat overlapping limits as unresolved review.

**Maintenance:** Recalibrate and inspect fixtures after damage or relocation. Preserve repeatability studies and drift history.

**Verification:** Datum repeatability and measurement-system study. Independent uncertainty-aware conformity review.

**Open evidence and decisions:** Released limits and uncertainty coverage. Fixture clamp capacity and load verification.

Basis: [BIPM: Uncertainty-aware conformity decisions; explicit decision-rule selection](https://www.bipm.org/en/doi/10.59161/jcgm106-2012), [Siemens: Measurement context, temperature and calibration traceability](https://references.siemens.com/en/reference/32785?id=32785), [NIST: Diagnostic spread/capability statistics and their stability/distribution/sample assumptions](https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc16.htm).

<a id="materials"></a>

## Material qualification and supplier equivalence

Responsible role: materials engineer. Applied to 356 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-007, STD-CTRL-008, STD-CTRL-011, STD-CTRL-012. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Select materials against strength, fatigue, fire, exposure and repair needs. Evaluate substitutions at the installed assembly level.

**Materials:** Maintain grade, heat/lot, shelf-life, certificate and supplier revision. Require measured properties and representative test coupons.

**Assembly:** Control storage, mixing and contamination. Quarantine expired or unapproved substitutes.

**Inspection:** Check certificate-to-lot identity and incoming condition. Preserve rejected batches and deviations.

**Maintenance:** Publish repair compatibility and replacement routes. Control cleaning chemicals and ageing inspections.

**Verification:** Supplier equivalence matrix and representative material tests. Installed build-up fire and ageing test plan.

**Open evidence and decisions:** Released grades and supplier certificates. Hazard categories and acceptance values.

Basis: [ISO: ISO 22163:2023 railway quality-management scope](https://www.iso.org/standard/79427.html), [BSI: BS EN 45545-2:2020+A1:2023](https://knowledge.bsigroup.com/products/railway-applications-fire-protection-on-railway-vehicles-requirements-for-fire-behaviour-of-materials-and-components-2), [Sika: Rail bonding and coating applications](https://industry.sika.com/en/home/transportation/rail.html).

<a id="manufacturing"></a>

## Qualified manufacture, travelers and quality learning

Responsible role: production/quality lead. Applied to 356 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-011, STD-CTRL-012, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Design for repeatable fixtures and accessible inspections. Separate planning cycle times from observed qualified production.

**Materials:** Control input lot and special-process consumables. Bind process windows to material system and revision.

**Assembly:** Use issued procedures, competent staff and sequenced holds. Capture tool traces and approved rework in portable travelers.

**Inspection:** Prevent open NCRs or missing holds from passing review. Use capability statistics only with suitable stability and measurement evidence.

**Maintenance:** Maintain tooling and process equipment. Feed recurring defects into corrective action and instruction revisions.

**Verification:** First-article traveler audit and process qualification. Traceable repeated-build inspection and capability study.

**Open evidence and decisions:** Approved process windows and product coverage. Released drawings, competence and real production records.

Basis: [Alstom: Repeatable special processes, equipment monitoring, competence and lean production](https://www.alstom.com/sites/alstom.com/files/2025/04/24/Alstom_Whitepaper_SmartManufacturing_EN.pdf), [Alstom: Digital work instructions and per-joint smart torque records](https://www.alstom.com/press-releases-news/2024/4/different-and-smart-approach-maintaining-trains), [ISO: ISO 3834-2:2021 fusion-welding quality scope](https://www.iso.org/standard/81651.html), [NIST: Diagnostic spread/capability statistics and their stability/distribution/sample assumptions](https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc16.htm).

<a id="environment"></a>

## Lifecycle energy, carbon, repair and circularity

Responsible role: environment/lifecycle lead. Applied to 356 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-001, STD-CTRL-015, STD-CTRL-016. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Compare alternatives against the same duty, lifespan and system boundary. Prioritise replaceable modules and disassembly access.

**Materials:** Request supplier EPD and recycled-content evidence. Account for adhesives, batteries and mixed-material separation.

**Assembly:** Measure actual waste and process energy. Record material recovery and hazardous waste routes.

**Inspection:** Review functional unit, geography and uncertainty. Do not transfer vendor savings to OSR forecasts.

**Maintenance:** Track replacements and energy against duty. Assess repair before replacement and retain safe disposal records.

**Verification:** Independently reviewed lifecycle inventory. Baseline-versus-alternative duty-cycle comparison.

**Open evidence and decisions:** Supplier environmental data and adopted LCA methods. Local recycling and disposal capability.

Basis: [ISO: ISO 14040:2006](https://www.iso.org/standard/37456.html), [Alstom: Energy, recyclability and lifecycle-aware material choices](https://www.alstom.com/company/sustainability/environment), [ISO: ISO 55001:2024](https://www.iso.org/standard/83054.html).

<a id="cybersecurity"></a>

## Secure software, networks and maintenance access

Responsible role: cybersecurity/software lead. Applied to 356 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-005, STD-CTRL-006, STD-CTRL-016. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Separate safety control from enterprise and passenger networks. Define trust boundaries, least privilege and recoverable update paths.

**Materials:** Track firmware, software bill of materials and component support life. Secure key provisioning and credential handling.

**Assembly:** Verify software identity and approved configuration. Restrict remote access and retain signed update/audit records.

**Inspection:** Test segmentation, loss of communications and rollback. Review vulnerabilities with safety and availability impacts.

**Maintenance:** Maintain offline recovery and revocable access. Approve patches against the safety configuration.

**Verification:** Threat model and controlled penetration/robustness tests. Restore-from-backup and update rollback demonstration.

**Open evidence and decisions:** Applicable railway cyber standards and acceptance authority. Validated security/safety interaction and actual control implementation.

Basis: [NIST: SP 800-82 Rev. 3: operational technology security](https://csrc.nist.gov/pubs/sp/800/82/r3/final), [IEC: IEC 62278-1:2025](https://webstore.iec.ch/en/publication/68933).

<a id="carbody"></a>

## Carbody load paths, lifting and equipment mounts

Responsible role: structural/mechanical engineer. Applied to 22 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-008, STD-CTRL-011, STD-CTRL-012, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Resolve fatigue, crash, lifting, towing and equipment retention load paths. Include installed mass, CG and interface loads.

**Materials:** Specify traceable structural grades and corrosion isolation. Qualify weld and fastener systems for the actual material.

**Assembly:** Build from common datums with controlled distortion. Inspect inaccessible welds before closure.

**Inspection:** Survey mounting interfaces and weld disposition. Weigh completed assemblies and reconcile the mass ledger.

**Maintenance:** Provide inspection and replaceable bracket access. Publish lifting and rescue instructions with load limits.

**Verification:** Independent structural/fatigue and recovery load assessment. First-article dimensional, NDT and weighed mass/CG records.

**Open evidence and decisions:** Released load cases and resistance factors. Qualified crashworthiness, fatigue and recovery evidence.

Basis: [ERA: LOC&PAS TSI and current application guidance](https://www.era.europa.eu/domains/technical-specifications-interoperability/rolling-stock-locomotives-and-passengers-tsi_en), [ISO: ISO 3834-2:2021 fusion-welding quality scope](https://www.iso.org/standard/81651.html), [IEC: IEC 61373:2010](https://webstore.iec.ch/en/publication/5395).

<a id="composites"></a>

## Composite shells, liners and bonded inserts

Responsible role: composites/process engineer. Applied to 22 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-008, STD-CTRL-011, STD-CTRL-012, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Separate cosmetic skins from structural load assumptions. Design removable modules and retained edges.

**Materials:** Freeze resin, fibre, core, adhesive and full coating build-up. Qualify fire, moisture, UV and cleaning compatibility.

**Assembly:** Control ply orientation, cure, vacuum, insert position and bond preparation. Retain batch/coupon genealogy and cure traces.

**Inspection:** Inspect thickness, voids, cure and insert retention using qualified methods. Test representative coated and bonded coupons.

**Maintenance:** Define approved patch, removal and water-ingress repairs. Inspect retention after impact or repair.

**Verification:** Representative laminate/insert mechanical and ageing tests. Installed fire build-up and repeated removal tests.

**Open evidence and decisions:** Released laminate schedules and cure windows. Repair qualification and allowable defects.

Basis: [Sika: Rail bonding and coating applications](https://industry.sika.com/en/home/transportation/rail.html), [BSI: BS EN 45545-2:2020+A1:2023](https://knowledge.bsigroup.com/products/railway-applications-fire-protection-on-railway-vehicles-requirements-for-fire-behaviour-of-materials-and-components-2), [Alstom: Repeatable special processes, equipment monitoring, competence and lean production](https://www.alstom.com/sites/alstom.com/files/2025/04/24/Alstom_Whitepaper_SmartManufacturing_EN.pdf).

<a id="coatings"></a>

## Coatings, graphics, seals and weathering

Responsible role: surface/materials engineer. Applied to 20 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-008, STD-CTRL-011, STD-CTRL-012, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Design drainage and isolate dissimilar metals. Keep experimental radiative coatings behind qualification gates.

**Materials:** Freeze surface preparation, primer, coating, film and seal compatibility. Include fire and repair build-up evidence.

**Assembly:** Record ambient/dew-point conditions and cure dependencies. Maintain clean preparation and protected handling.

**Inspection:** Measure preparation, coverage, film thickness and adhesion by issued methods. Inspect edges, penetrations and trapped water.

**Maintenance:** Define cleaning and touch-up systems. Inspect water ingress, seal ageing and coating breakdown.

**Verification:** Representative corrosion/weathering and adhesion assessment. Water-ingress and repair compatibility tests.

**Open evidence and decisions:** Exposure category and coating system. Radiative-coating durability and actual energy benefit.

Basis: [ISO: ISO 12944-2:2017](https://www.iso.org/standard/64834.html), [Sika: Rail bonding and coating applications](https://industry.sika.com/en/home/transportation/rail.html), [Siemens: Resource scheduling with coating/drying and quality dependencies](https://resources.sw.siemens.com/de-DE/case-study-increase-efficiency-and-productivity-with-digital-scheduling/).

<a id="fasteners"></a>

## Fasteners, captive service rails and retained fixtures

Responsible role: joint/assembly engineer. Applied to 19 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-008, STD-CTRL-011, STD-CTRL-012, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Reduce part variety using qualified interface families. Check preload, fatigue, slip and secondary retention.

**Materials:** Specify grade, coating and galvanic isolation. Control locking elements and single-use parts.

**Assembly:** Use per-joint tool traces and qualified tightening method. Approve retorque and replacement before rework.

**Inspection:** Inspect joint access, engagement and witness identity. Torque alone shall not be treated as measured preload.

**Maintenance:** Publish reusable versus replace-on-removal rules. Inspect service rails and anti-lift retainers after replacement.

**Verification:** Joint preload/retention qualification and repeated-service trial. Configuration-bound calibrated tightening record audit.

**Open evidence and decisions:** Released torque/angle or tension limits. Joint-specific friction, fatigue and service reuse evidence.

Basis: [Alstom: Digital work instructions and per-joint smart torque records](https://www.alstom.com/press-releases-news/2024/4/different-and-smart-approach-maintaining-trains), [NASA: Systems engineering handbook: interfaces and verification](https://www.nasa.gov/reference/system-engineering-handbook-appendix/).

<a id="bogie-frame"></a>

## Bogie frames, guards and torque reaction

Responsible role: bogie structural engineer. Applied to 9 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-008, STD-CTRL-011, STD-CTRL-012, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Include wheelset, brake, motor and suspension interface loads. Check guard retention, clearance and common fatigue details.

**Materials:** Specify structural grades and weld-quality classes by consequence. Avoid unqualified mass substitutions.

**Assembly:** Use released fixture and weld sequence. Inspect alignment before installing running equipment.

**Inspection:** Perform qualified weld NDT and datum surveys. Check accessible guard and reaction-link retainers.

**Maintenance:** Define frame inspection and repair exclusions. Maintain fatigue-critical weld and mount histories.

**Verification:** Independent fatigue/load assessment and frame test plan. First-article NDT and running-equipment alignment records.

**Open evidence and decisions:** Actual suspension/motor/brake loads. Frame fatigue qualification and approved repair limits.

Basis: [ERA: LOC&PAS TSI and current application guidance](https://www.era.europa.eu/domains/technical-specifications-interoperability/rolling-stock-locomotives-and-passengers-tsi_en), [ISO: ISO 3834-2:2021 fusion-welding quality scope](https://www.iso.org/standard/81651.html), [IEC: IEC 61373:2010](https://webstore.iec.ch/en/publication/5395).

<a id="wheelsets"></a>

## Wheelsets, rail profiles and running contact

Responsible role: vehicle/track dynamics engineer. Applied to 7 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-008, STD-CTRL-012, STD-CTRL-013, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Select wheel and rail profiles together with gauge and turnouts. Use models within their validated contact and loading domain.

**Materials:** Freeze axle, wheel, disc and profile specifications. Retain heat and wheelset serial genealogy.

**Assembly:** Control wheel press fits, back-to-back and disc attachment. Avoid bearing and axle contamination.

**Inspection:** Measure profiles, dimensions and qualified axle/wheel NDT. Reject unsupported contact footprints in numerical evidence.

**Maintenance:** Set measured wear, reprofile and defect limits. Preserve mileage, thermal events and wheelset change records.

**Verification:** Actual-profile running-dynamics and braking assessment. Qualified wheelset fit, NDT and dimensional tests.

**Open evidence and decisions:** Released profiles and running-safety criteria. Full six-car passage remains outside the current model contact domain.

Basis: [ERA: LOC&PAS TSI and current application guidance](https://www.era.europa.eu/domains/technical-specifications-interoperability/rolling-stock-locomotives-and-passengers-tsi_en), [FTA: Report 0215: track inspection and maintenance](https://www.transit.dot.gov/research-innovation/research-report-and-findings-review-standards-track-inspection-and-maintenance).

<a id="axleboxes"></a>

## Axleboxes, bearings, lubrication and sensing

Responsible role: bearing/running-gear engineer. Applied to 8 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-008, STD-CTRL-012, STD-CTRL-013, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Design bearing fits, sealing and sensor placement for actual duty. Separate diagnostic monitoring from safety decisions.

**Materials:** Freeze bearing, lubricant, seal and sensor revisions. Control cleanliness and storage.

**Assembly:** Use qualified press/heating tools and fit procedures. Record serials and avoid transmitting assembly loads through rollers.

**Inspection:** Measure fits and inspect sealing/temperature-sensor function. Retain installation and lubricant genealogy.

**Maintenance:** Set intervals from supplier duty and observed evidence. Investigate temperature/vibration alarms and lubricant contamination.

**Verification:** Bearing application and thermal/life assessment. Installation fit and sensor fault/health tests.

**Open evidence and decisions:** Released fits, loads and lubrication data. Validated alarm thresholds and response policy.

Basis: [SKF: Evolution of railway axlebox technology](https://evolution.skf.com/en/the-evolution-of-railway-axlebox-technology/), [Hitachi Rail: HMAX for signalling](https://www.hitachirail.com/products-and-solutions/digital-asset-management/hmax-for-signalling/).

<a id="suspension"></a>

## Primary/secondary suspension and body connection

Responsible role: suspension/dynamics engineer. Applied to 8 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-008, STD-CTRL-012, STD-CTRL-013, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Model full loaded/empty travel and emergency support. Check ride, roll, clearance and retention together.

**Materials:** Freeze spring, air-spring, damper and elastomer specifications. Include temperature, ageing and leak behaviour.

**Assembly:** Use surveyed pads and released shim/height procedures. Verify link orientation and retained fasteners.

**Inspection:** Measure installed height, travel and air leakage. Record component identity and characteristic curves.

**Maintenance:** Inspect leaks, ageing, wear and damper condition. Keep approved replacement pairing and height resets.

**Verification:** Measured force-displacement/damping curves. Loaded/empty dynamics and deflated-suspension tests.

**Open evidence and decisions:** Supplier curves and approved ride criteria. Bump-stop, emergency spring and degraded-mode qualification.

Basis: [Continental: Railway secondary suspension](https://www.continental-industry.com/global/en/products-solutions/airsprings-suspension/railway/secondary-suspension), [ERA: LOC&PAS TSI and current application guidance](https://www.era.europa.eu/domains/technical-specifications-interoperability/rolling-stock-locomotives-and-passengers-tsi_en).

<a id="braking"></a>

## Service, emergency and parking braking with adhesion

Responsible role: brake/safety engineer. Applied to 11 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-007, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Prove friction braking when regeneration or charging is unavailable. Include low adhesion, load, gradient and degraded channels.

**Materials:** Freeze pads, discs, actuators and WSP sensors. Consider thermal capacity and contamination.

**Assembly:** Verify brake clearances, hose/harness routing and polarity. Preserve independently checked safety joints.

**Inspection:** Test parking hold, brake demand, release and fault handling. Retain synchronized speed/pressure/deceleration traces.

**Maintenance:** Maintain wear, thermal-damage and actuator inspections. Trend failures without extending intervals automatically.

**Verification:** Approved loaded/empty stopping and low-adhesion test campaign. Emergency, parking, WSP fault and regen-loss tests.

**Open evidence and decisions:** Accepted stopping envelopes and failure allocations. Qualified physical brake tests and signalling interface.

Basis: [Knorr-Bremse: Adhesion and wheel-slide protection](https://rail.knorr-bremse.com/en/us/portfolio/products-and-systems/braking-systems/adhesion/), [IEC: IEC 62290-1:2025](https://webstore.iec.ch/en/publication/83773).

<a id="traction"></a>

## Motors, gearboxes, couplings and thermal duty

Responsible role: traction engineer. Applied to 12 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-007, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Size propulsion for route, gradient, load and degraded operation. Compare measured efficiency maps rather than nominal vendor gains.

**Materials:** Freeze winding/insulation, gear, lubricant and coupling specifications. Include contamination and thermal ageing.

**Assembly:** Align motor/gearbox interfaces and reaction links. Record lubrication and calibrated critical joints.

**Inspection:** Measure alignment, insulation and rotation direction. Test loaded thermal behaviour and protective trips.

**Maintenance:** Provide replaceable drive modules and safe isolation. Track wear, temperature and lubricant condition.

**Verification:** Duty-cycle traction/thermal and efficiency-map assessment. Alignment, overspeed/protection and degraded-drive tests.

**Open evidence and decisions:** Actual supplier maps and continuous/peak envelopes. Validated energy and cooling performance.

Basis: [CRRC: Primary account of lifecycle automation, redundancy, running-gear monitoring and efficient traction](https://www.crrcgc.cc/en/2026-04/29/article_2026042916024714810.html), [ERA: LOC&PAS TSI and current application guidance](https://www.era.europa.eu/domains/technical-specifications-interoperability/rolling-stock-locomotives-and-passengers-tsi_en).

<a id="batteries"></a>

## Traction batteries, enclosures and safe removal

Responsible role: battery/electrical safety engineer. Applied to 13 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-007, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Treat chemistry changes as controlled redesign. Analyse pack containment, propagation, ventilation and emergency isolation.

**Materials:** Freeze cell/module/BMS and enclosure build-up. Track cell lots, transport and storage conditions.

**Assembly:** Use protected handling, interlocked trays and keyed connections. Bind pack serials and test history to configuration.

**Inspection:** Check insulation, bonding, BMS sensing and shutdown. Inspect pack retention and cooling/vent routes.

**Maintenance:** Define health limits, isolation, safe removal and quarantine. Retain abuse, thermal and repair history.

**Verification:** Qualified pack electrical/mechanical/thermal and fault test plan. Removal, isolation and emergency-response demonstration.

**Open evidence and decisions:** Released chemistry and cell-to-pack qualification. LTO reference geometry does not release an LFP substitution.

Basis: [IEC: IEC 62928:2017](https://webstore.iec.ch/en/publication/31101), [IEC: IEC 61373:2010](https://webstore.iec.ch/en/publication/5395), [BSI: BS EN 45545-2:2020+A1:2023](https://knowledge.bsigroup.com/products/railway-applications-fire-protection-on-railway-vehicles-requirements-for-fire-behaviour-of-materials-and-components-2).

<a id="hv-distribution"></a>

## HV/LV power distribution, bonding and harnesses

Responsible role: electrical integration engineer. Applied to 19 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-007, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Coordinate protection, grounding, creepage and stored-energy discharge. Segregate HV, safety, data and passenger circuits.

**Materials:** Specify cable, connector, fuse, contactor and insulation systems. Include flame, abrasion and environment evidence.

**Assembly:** Control crimps, terminal forces, bend radii and bonding. Use keyed circuits and verified routing.

**Inspection:** Perform continuity, polarity, insulation and protection tests. Record each circuit, tool and connector revision.

**Maintenance:** Provide safe lockout and replaceable harness sections. Inspect chafing, loosening, ingress and insulation condition.

**Verification:** Protection coordination and insulation assessment. Installed EMC, electrical tests and stuck-contactor fault tests.

**Open evidence and decisions:** Adopted voltage/altitude/pollution design basis. Qualified protection and installed-system EMC evidence.

Basis: [IEC: IEC 62497-1:2010 with AMD1:2013 review required](https://webstore.iec.ch/en/publication/7117), [IEC: IEC 62236-3-2:2018](https://webstore.iec.ch/en/publication/62682), [IEC: IEC 61373:2010](https://webstore.iec.ch/en/publication/5395).

<a id="cooling"></a>

## Cooling, fluids, pneumatic auxiliaries and drains

Responsible role: thermal/fluid engineer. Applied to 16 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-007, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Separate hazardous fluids and electrical zones. Size cooling and pneumatic support for climate and failed equipment.

**Materials:** Freeze hose, coolant, lubricant, seal and pressure ratings. Check chemical compatibility and cleanliness.

**Assembly:** Control routing, clamping, bleeding and contamination. Keep leak checks before inaccessible closure.

**Inspection:** Measure flow, pressure, leakage and protective response. Verify drain paths and isolated maintenance points.

**Maintenance:** Maintain filters, dryers, drains and fluid sampling. Publish depressurisation and spill response.

**Verification:** Thermal/pressure duty and failure assessment. Leak, blocked-drain, pump-loss and compressor-loss tests.

**Open evidence and decisions:** Released flow/pressure/temperature windows. Supplier compatibility and degraded support capacity.

Basis: [ISO: ISO 19659-4:2026](https://www.iso.org/standard/85202.html), [Continental: Railway secondary suspension](https://www.continental-industry.com/global/en/products-solutions/airsprings-suspension/railway/secondary-suspension).

<a id="hvac"></a>

## HVAC, air distribution and passenger comfort

Responsible role: HVAC engineer. Applied to 10 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-007, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Specify route climate, solar, passenger, door-cycle and ventilation loads. Assess unit performance together with installed ducts.

**Materials:** Freeze refrigerant, insulation, filters and fire build-up. Check corrosion and condensate compatibility.

**Assembly:** Seal and support ducts without obstructing service access. Control refrigeration joints and condensate slope.

**Inspection:** Measure airflow, thermal comfort and noise at occupied positions. Check leakage, control response and drainage.

**Maintenance:** Provide replaceable filters and maintainable condensate systems. Track refrigerant leakage and actual energy demand.

**Verification:** Climate-chamber and installed saloon comfort tests. Ventilation, failed-unit, condensate and noise tests.

**Open evidence and decisions:** Project comfort values and fresh-air basis. Actual climate/load performance and cab applicability.

Basis: [ISO: ISO 19659-2:2020](https://www.iso.org/standard/70232.html), [ISO: ISO 19659-4:2026](https://www.iso.org/standard/85202.html), [ISO: ISO 3381:2021](https://www.iso.org/standard/77368.html).

<a id="doors"></a>

## Passenger doors, carriers and boarding interlocks

Responsible role: door/control engineer. Applied to 6 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-007, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Treat cassette, carrier, sensitive edge and control as one interface. Coordinate platform alignment, entrapment and emergency release.

**Materials:** Freeze seals, glazing, actuators and detection devices. Include fire, fatigue and weathering.

**Assembly:** Survey carrier datums, shims and connector keying. Preserve door clearance through interior trim installation.

**Inspection:** Check obstruction detection, locking and traction inhibit. Measure alignment, water ingress and emergency opening.

**Maintenance:** Retain cycle counts, seal and mechanism inspections. Prohibit bypasses outside approved degraded procedures.

**Verification:** Approved obstruction, emergency and repeated-cycle tests. Wrong-side, sensor failure and platform-door integration tests.

**Open evidence and decisions:** Door forces, clearances and safety allocation. Qualified physical cassette and interlock evidence.

Basis: [Knorr-Bremse / IFE: Train entrance systems](https://www.knorr-bremse.us/en/products/door-systems/entrance-systems/), [IEC: IEC 62290-1:2025](https://webstore.iec.ch/en/publication/83773).

<a id="glazing"></a>

## Glazing, retention, seals and replacement

Responsible role: glazing/joint engineer. Applied to 11 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-007, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Design load, impact, retention and safe replacement together. Keep drains and secondary retention accessible.

**Materials:** Freeze glass, heaters, seals, setting blocks and adhesive build-up. Evaluate installed fire and ageing compatibility.

**Assembly:** Control bond preparation, thickness and cure or dry-seal compression. Inspect setting blocks before closure.

**Inspection:** Measure opening/glass fit and retained edges. Verify water ingress and heating/isolation function.

**Maintenance:** Publish removal and cure/return-to-service instructions. Inspect chips, delamination and seal breakdown.

**Verification:** Retention/impact and environmental qualification. First replacement and water-ingress demonstration.

**Open evidence and decisions:** Approved glazing performance and opening geometry. Bonding qualification and replacement release times.

Basis: [Sika: Rail bonding and coating applications](https://industry.sika.com/en/home/transportation/rail.html), [ERA: LOC&PAS TSI and current application guidance](https://www.era.europa.eu/domains/technical-specifications-interoperability/rolling-stock-locomotives-and-passengers-tsi_en).

<a id="interiors"></a>

## Floors, seats, handrails and passenger fixtures

Responsible role: interior/accessibility engineer. Applied to 14 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-007, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Design slip, retention and unobstructed accessible circulation. Coordinate removable floors with underfloor hazards.

**Materials:** Qualify actual floor/adhesive/liner/seat build-ups. Require fire, cleaning and wear compatibility.

**Assembly:** Use common retained mounts and accessible captive fixings. Protect door and PRM clearance through fit-out.

**Inspection:** Inspect edges, ramps, floor bonds and fixture joints. Survey installed accessible spaces.

**Maintenance:** Publish cleaning, replacement and damage limits. Inspect retained hatches and handrails after service.

**Verification:** Installed fixture-load, slip/wear and fire tests. Accessible circulation and repeated hatch-removal trials.

**Open evidence and decisions:** Vehicle-specific access and load criteria. Installed fire build-up and fixture retention evidence.

Basis: [BSI: BS EN 45545-2:2020+A1:2023](https://knowledge.bsigroup.com/products/railway-applications-fire-protection-on-railway-vehicles-requirements-for-fire-behaviour-of-materials-and-components-2), [ISO: ISO 21542:2021](https://www.iso.org/standard/71860.html), [IEC: IEC 61373:2010](https://webstore.iec.ch/en/publication/5395).

<a id="gangways"></a>

## Couplers, articulation, gangways and flexible services

Responsible role: coupling/articulation engineer. Applied to 20 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-007, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Check curves, twist, collision, rescue and passenger bridge envelopes. Select one end-interface configuration per position.

**Materials:** Freeze bearings, pins, bellows, wear liners and service loops. Include ageing and fire compatibility.

**Assembly:** Survey common end datums and retained pins. Keep flexible HV/LV/fluid paths segregated through full movement.

**Inspection:** Measure movement clearance, retention and leak paths. Test coupling lock and service continuity.

**Maintenance:** Inspect fatigue, pin wear, bellows and service-loop abrasion. Bind replacements to selected end configuration.

**Verification:** Full-envelope articulation and rescue load tests. Repeated movement, gangway gap and service continuity tests.

**Open evidence and decisions:** Released motion/load envelope and coupling compatibility. Optional train-to-train configuration transfer qualification.

Basis: [ERA: LOC&PAS TSI and current application guidance](https://www.era.europa.eu/domains/technical-specifications-interoperability/rolling-stock-locomotives-and-passengers-tsi_en), [NASA: Systems engineering handbook: interfaces and verification](https://www.nasa.gov/reference/system-engineering-handbook-appendix/).

<a id="automation"></a>

## Train control, navigation and automated lifecycle

Responsible role: train-control/safety engineer. Applied to 18 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-007, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Allocate movement authority and interlocks independently of navigation. Define standby, depot, mainline, platform, rescue and wash modes.

**Materials:** Freeze control hardware, sensor and software revisions. Include shock, thermal, EMC and security evidence.

**Assembly:** Verify safety I/O identities, sensor datums and protected harnesses. Keep commissioning configuration under change control.

**Inspection:** Test brake/door/HV/comms interlocks and stale/lost inputs. Preserve critical lockout and bounded auxiliary recovery.

**Maintenance:** Use controlled diagnostics and approved manual/degraded controls. Review software changes and sensor calibration.

**Verification:** Independent safety architecture and integrated fault campaign. Approved physical lifecycle and movement-authority tests.

**Open evidence and decisions:** Real signalling architecture and safety integrity allocation. Offline Python contracts do not establish GoA4 qualification.

Basis: [IEC: IEC 62290-1:2025](https://webstore.iec.ch/en/publication/83773), [IEC: IEC 62278-1:2025](https://webstore.iec.ch/en/publication/68933), [CRRC: Primary account of lifecycle automation, redundancy, running-gear monitoring and efficient traction](https://www.crrcgc.cc/en/2026-04/29/article_2026042916024714810.html).

<a id="communications"></a>

## Train/wayside communications, timing and event records

Responsible role: communications/software engineer. Applied to 21 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-006, STD-CTRL-014, STD-CTRL-015. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Specify latency, time alignment, availability and data ownership. Distinguish diagnostics from safety communications.

**Materials:** Freeze antenna, network device and recorder revisions. Check EMC, storage endurance and environment.

**Assembly:** Verify cable segregation, connector identity and antenna placement. Provision least-privilege identities and synchronized clocks.

**Inspection:** Test coverage, handover, time skew, link loss and record retrieval. Retain traceable event identifiers and checksums.

**Maintenance:** Publish open diagnostic exports and offline access. Control retention, privacy, backup and unsupported firmware.

**Verification:** Route communications/EMC and failover trials. Timestamped event reconstruction and recovery test.

**Open evidence and decisions:** Qualified safety communication channels and time budgets. Crashworthy recorder and actual coverage evidence.

Basis: [NIST: SP 800-82 Rev. 3: operational technology security](https://csrc.nist.gov/pubs/sp/800/82/r3/final), [IEC: IEC 62290-1:2025](https://webstore.iec.ch/en/publication/83773), [Hitachi Rail: HMAX for signalling](https://www.hitachirail.com/products-and-solutions/digital-asset-management/hmax-for-signalling/).

<a id="passenger-systems"></a>

## Information, lighting, intercom and security equipment

Responsible role: passenger systems engineer. Applied to 14 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-006, STD-CTRL-014, STD-CTRL-015. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Coordinate visual/audio information, lighting and emergency calls. Keep emergency functions available under defined power failures.

**Materials:** Freeze luminaires, displays, speakers, cameras and mounts. Check fire and cleaning/ingress suitability.

**Assembly:** Use keyed feeders and common retained service mounts. Verify camera/speaker coverage without obstructing access.

**Inspection:** Test intelligibility, display accuracy, illuminance and emergency call routing. Inspect backup supply and independent lighting feeds.

**Maintenance:** Maintain lamps, optics, content and privacy controls. Check help points and emergency functions periodically.

**Verification:** Installed passenger-information/accessibility demonstration. Power-loss, audio, lighting and intercom failover tests.

**Open evidence and decisions:** Project lighting/intelligibility and privacy rules. Qualified emergency duration and accessibility evidence.

Basis: [ISO: ISO 21542:2021](https://www.iso.org/standard/71860.html), [IEC: IEC 62236-3-2:2018](https://webstore.iec.ch/en/publication/62682), [Knorr-Bremse / IFE: Train entrance systems](https://www.knorr-bremse.us/en/products/door-systems/entrance-systems/).

<a id="fire-response"></a>

## Fire detection, containment, evacuation and rescue

Responsible role: fire/life-safety engineer. Applied to 22 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-001, STD-CTRL-003, STD-CTRL-004, STD-CTRL-014, STD-CTRL-015. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Analyse battery, electrical, interior and station fire scenarios together. Define detection, isolation, evacuation and responder access.

**Materials:** Qualify installed build-ups and penetration seals. Choose suppression only after hazard-specific assessment.

**Assembly:** Protect detector/vent routes and fire barriers. Inspect concealed seals before closure.

**Inspection:** Test alarms, isolation, emergency lighting and communications. Record cause/effect and barrier installation evidence.

**Maintenance:** Maintain detectors, barriers, extinguishers and escape routes. Train operators/responders using current approved plans.

**Verification:** Project fire/evacuation strategy review. Controlled emergency exercises and hazard-specific detection/suppression tests.

**Open evidence and decisions:** Applicable fire codes and evacuation criteria. Physical fire propagation, containment and rescue evidence.

Basis: [BSI: BS EN 45545-2:2020+A1:2023](https://knowledge.bsigroup.com/products/railway-applications-fire-protection-on-railway-vehicles-requirements-for-fire-behaviour-of-materials-and-components-2), [FTA: Emergency preparedness planning guide (2003)](https://www.transit.dot.gov/oversight-policy-areas/public-transportation-system-security-and-emergency-preparedness-planning), [IEC: IEC 62928:2017](https://webstore.iec.ch/en/publication/31101).

<a id="survey"></a>

## Survey, alignment, gauge and route configuration

Responsible role: survey/track engineer. Applied to 18 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-009, STD-CTRL-010, STD-CTRL-012, STD-CTRL-013. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Use accepted coordinate/vertical datums and survey uncertainty. Reconcile alignment with vehicle swept and platform envelopes.

**Materials:** Control monument, instrument and rail-profile revisions. Preserve survey provenance and ground reference conditions.

**Assembly:** Set out from checked control networks. Verify coordinates and units before lifting or track installation.

**Inspection:** Independently check closure, gauge, level and clearance. Keep raw observations and adjusted results.

**Maintenance:** Monitor movement and renew damaged monuments. Update as-maintained alignment after repairs.

**Verification:** Independent survey adjustment and clearance audit. Loaded-envelope and track-geometry reconciliation.

**Open evidence and decisions:** Accepted survey control and route geometry. Project gauge/clearance limits and uncertainty.

Basis: [buildingSMART: IFC railway domain and open exchange](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcRailway.htm), [FTA: Report 0215: track inspection and maintenance](https://www.transit.dot.gov/research-innovation/research-report-and-findings-review-standards-track-inspection-and-maintenance).

<a id="ground"></a>

## Ground investigation, foundations and settlement

Responsible role: geotechnical/foundation engineer. Applied to 10 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-009, STD-CTRL-010, STD-CTRL-012, STD-CTRL-013. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Base foundations on site investigation and groundwater. Include settlement, scour, seismic and adjacent utilities.

**Materials:** Freeze concrete, reinforcement and ground-treatment systems. Control water/soil aggressivity assumptions.

**Assembly:** Issue excavation, support and pile/foundation procedures. Record ground deviations before concealment.

**Inspection:** Inspect founding level, reinforcement and concrete evidence. Retain pile/load and settlement records as applicable.

**Maintenance:** Provide settlement and drainage monitoring. Inspect scour and deterioration after extreme events.

**Verification:** Independent geotechnical/design review and site tests. Foundation capacity and settlement verification.

**Open evidence and decisions:** Site ground model and design criteria. Foundation, groundwater and temporary support release.

Basis: [FHWA: Bridge concrete technical resources](https://www.fhwa.dot.gov/bridge/concrete/), [FHWA: Bridge preservation resources](https://www.fhwa.dot.gov/bridge/preservation/).

<a id="precast"></a>

## Precast/prestressed beams, decks, piers and platform units

Responsible role: civil structural/production engineer. Applied to 26 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-009, STD-CTRL-011, STD-CTRL-012, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Design lifting, transport, erection and final load stages. Include railway fatigue, dynamics, durability and replaceability.

**Materials:** Freeze concrete mix, reinforcement, tendons, inserts and grout. Keep batch/heat/strand traceability.

**Assembly:** Inspect forms, reinforcement and ducts before casting. Record concrete, curing, strength release and stressing/grout procedures.

**Inspection:** Survey dimensions, inserts, cracks and tendon/grout evidence. Quarantine damaged units pending engineer disposition.

**Maintenance:** Provide inspection access and repair limits. Track cracks, leakage, corrosion and bearing-zone condition.

**Verification:** Independent staged structural and fatigue assessment. Qualified concrete/strength, stressing/grouting and lifting records.

**Open evidence and decisions:** Project resistance/durability criteria and reinforcement. Released mix, strength-at-handling and prestress procedures.

Basis: [FHWA: Bridge concrete technical resources](https://www.fhwa.dot.gov/bridge/concrete/), [ISO: ISO 3834-2:2021 fusion-welding quality scope](https://www.iso.org/standard/81651.html), [Alstom: Repeatable special processes, equipment monitoring, competence and lean production](https://www.alstom.com/sites/alstom.com/files/2025/04/24/Alstom_Whitepaper_SmartManufacturing_EN.pdf).

<a id="bearings"></a>

## Bridge bearings, joints, jacking and replaceability

Responsible role: bridge/interface engineer. Applied to 4 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-009, STD-CTRL-011, STD-CTRL-012, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Check translation, rotation, restraint and rail-structure interaction. Design safe bearing replacement and inspection access.

**Materials:** Freeze bearing, elastomer/sliding surface and grout systems. Check corrosion and seal compatibility.

**Assembly:** Survey seats and orientation with temperature context. Use released jacking, seating and grout sequence.

**Inspection:** Measure seat levels, movement and keeper clearances. Retain bearing serial and orientation evidence.

**Maintenance:** Inspect movement, debris, leaks and restraint condition. Use approved staged jacking for replacement.

**Verification:** Bearing/load/movement assessment. Seat survey and first replacement/jacking demonstration.

**Open evidence and decisions:** Released bridge movement/load envelope. Supplier bearing qualification and replacement procedure.

Basis: [FHWA: Bridge preservation resources](https://www.fhwa.dot.gov/bridge/preservation/), [NASA: Systems engineering handbook: interfaces and verification](https://www.nasa.gov/reference/system-engineering-handbook-appendix/).

<a id="erection"></a>

## Logistics, lifting, temporary works and site assembly

Responsible role: construction/temporary works engineer. Applied to 12 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-009, STD-CTRL-011, STD-CTRL-012, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Design transport routes, lifts and temporary stability stages. Schedule holds, strength release and weather constraints explicitly.

**Materials:** Freeze lifting accessories, anchor and grout systems. Inspect reusable lifting equipment condition.

**Assembly:** Use issued lift plans, competent crews and exclusion zones. Release temporary supports only after checked handover.

**Inspection:** Verify lifting capacity/configuration and incoming unit condition. Record surveys and critical hold completion.

**Maintenance:** Maintain cranes, slings, rigs and temporary works. Retain reusable fixture inspection histories.

**Verification:** Independent temporary-works and lift-plan review. Controlled first lift, erection survey and handover audit.

**Open evidence and decisions:** Site-specific lifting capacity and wind limits. Released temporary works and actual strength evidence.

Basis: [FHWA: Bridge concrete technical resources](https://www.fhwa.dot.gov/bridge/concrete/), [Siemens: Resource scheduling with coating/drying and quality dependencies](https://resources.sw.siemens.com/de-DE/case-study-increase-efficiency-and-productivity-with-digital-scheduling/), [ISO: ISO 22163:2023 railway quality-management scope](https://www.iso.org/standard/79427.html).

<a id="drainage"></a>

## Drainage, water management and climate resilience

Responsible role: drainage/environment engineer. Applied to 11 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-009, STD-CTRL-011, STD-CTRL-012, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Coordinate route, deck, platform, battery and canopy drainage. Design maintainable outfalls for site flood and debris scenarios.

**Materials:** Freeze pipe, seal, protection and ground-treatment compatibility. Include soil/water exposure.

**Assembly:** Survey falls and clean connections before closure. Protect drains during erection and finishing.

**Inspection:** Test flow, blockage access and leakage. Reconcile installed outlets with accepted outfall design.

**Maintenance:** Inspect before seasonal extremes and after floods. Remove debris and record erosion, scour and ingress.

**Verification:** Site hydrology/drainage and resilience assessment. Flow, blocked-drain and inspection-access demonstrations.

**Open evidence and decisions:** Site rainfall/flood climate and outfall permission. Extreme-weather operating and recovery criteria.

Basis: [FHWA: Bridge preservation resources](https://www.fhwa.dot.gov/bridge/preservation/), [ISO: ISO 12944-2:2017](https://www.iso.org/standard/64834.html).

<a id="track"></a>

## Rails, fastenings, slabs and wheel/rail interfaces

Responsible role: track/vehicle integration engineer. Applied to 14 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-009, STD-CTRL-011, STD-CTRL-012, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Select rail, pad, clip, insulator and support as one qualified system. Check gauge, rail stress, dynamic stiffness and vehicle profiles.

**Materials:** Freeze rail grade/profile, fasteners, pads and slab interfaces. Retain rail heat and fastening batch evidence.

**Assembly:** Use approved rail joining, stressing and fastening installation. Survey support geometry and electrical isolation.

**Inspection:** Measure gauge, alignment, joints and fastener condition. Check actual installed support stiffness where required.

**Maintenance:** Set inspected wear, geometry and defect limits. Control rail grinding, replacement and thermal interventions.

**Verification:** Vehicle-track dynamics and rail-structure interaction assessment. Track geometry, joining and fastening qualification.

**Open evidence and decisions:** Actual rail/wheel profiles and track stiffness. Approved wear/geometry limits and inspection intervals.

Basis: [Pandrol: Fastclip rail fastening system](https://www.pandrol.com/products/fastening-systems/fasteners/fastclip), [FTA: Report 0215: track inspection and maintenance](https://www.transit.dot.gov/research-innovation/research-report-and-findings-review-standards-track-inspection-and-maintenance), [ERA: LOC&PAS TSI and current application guidance](https://www.era.europa.eu/domains/technical-specifications-interoperability/rolling-stock-locomotives-and-passengers-tsi_en).

<a id="turnouts"></a>

## Turnouts, point machines, detection and track ends

Responsible role: turnout/signalling engineer. Applied to 13 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-009, STD-CTRL-011, STD-CTRL-012, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Qualify geometry, locking, detection and interlocking together. Include obstruction, run-through, manual operation and terminal overrun.

**Materials:** Freeze rail/frog, sleepers, actuator and detector systems. Check heater/protection environment and wear.

**Assembly:** Survey turnout datums and mechanically verify lock/detection. Control hand-wind isolation, cabling and heater installation.

**Inspection:** Test obstruction, wrong detection and loss of power. Measure switch/frog geometry and end-stop installation.

**Maintenance:** Inspect wear, lock, force and detector drift. Retain movement counts and approved manual intervention.

**Verification:** Integrated point machine/locking/interlocking fault tests. Turnout geometry, wheel passage and end-stop energy assessment.

**Open evidence and decisions:** Released point forces, detector logic and stopping envelope. Qualified turnout and terminal-overrun protection.

Basis: [voestalpine Railway Systems: Turnout systems and lifecycle integration](https://www.voestalpine.com/railway-systems/en/company/news/turnout-systems-intelligent-networked-and-future-proof.-system-thinking-for-rail-infrastructure-excellence./?year=2025), [FTA: Report 0215: track inspection and maintenance](https://www.transit.dot.gov/research-innovation/research-report-and-findings-review-standards-track-inspection-and-maintenance), [IEC: IEC 62290-1:2025](https://webstore.iec.ch/en/publication/83773).

<a id="signalling"></a>

## Wayside signalling, detection and movement authority

Responsible role: signalling safety engineer. Applied to 14 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-006, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Define safe authority, route locking and train detection independently of advisory telemetry. Include degraded and maintenance modes.

**Materials:** Freeze safety hardware/software and detection assumptions. Check vehicle EMC and axle/detection compatibility.

**Assembly:** Verify route-specific wiring and configured topology. Independently check safety-critical mappings.

**Inspection:** Test wrong route, loss of detection/comms and stale authority. Retain versioned route and event records.

**Maintenance:** Use controlled fault isolation and configuration restoration. Condition monitoring shall not override safe detection.

**Verification:** Independent signalling safety case review. Integrated route locking, train detection and authority fault tests.

**Open evidence and decisions:** Applicable complete signalling/safety standards. Actual safety architecture and physical train/wayside integration.

Basis: [IEC: IEC 62290-1:2025](https://webstore.iec.ch/en/publication/83773), [IEC: IEC 62278-1:2025](https://webstore.iec.ch/en/publication/68933), [ERA: LOC&PAS TSI and current application guidance](https://www.era.europa.eu/domains/technical-specifications-interoperability/rolling-stock-locomotives-and-passengers-tsi_en), [Hitachi Rail: HMAX for signalling](https://www.hitachirail.com/products-and-solutions/digital-asset-management/hmax-for-signalling/).

<a id="platforms"></a>

## Platforms, boarding gaps and platform doors

Responsible role: station/vehicle interface engineer. Applied to 22 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-003, STD-CTRL-009, STD-CTRL-014, STD-CTRL-015. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Assess boarding against loaded/empty vehicle and curve envelopes. Coordinate evacuation, crowding and platform-door synchronization.

**Materials:** Freeze coping, tactile, slip-resistant and door systems. Include outdoor exposure and fire compatibility.

**Assembly:** Survey edge datums against actual track and vehicle. Protect accessible gaps through closure and rework.

**Inspection:** Measure platform height/gap with uncertainty and all relevant vehicle states. Test synchronized and degraded door opening.

**Maintenance:** Inspect edge movement, tactile condition and door alignment. Publish approved closure and boarding-assistance procedures.

**Verification:** Integrated vehicle/platform envelope and access demonstration. Platform-door obstruction, wrong-side and power-loss tests.

**Open evidence and decisions:** Adopted access/boarding limits and crowd assumptions. Qualified platform-door and evacuation interface.

Basis: [ISO: ISO 21542:2021](https://www.iso.org/standard/71860.html), [Knorr-Bremse / IFE: Train entrance systems](https://www.knorr-bremse.us/en/products/door-systems/entrance-systems/), [IEC: IEC 62290-1:2025](https://webstore.iec.ch/en/publication/83773).

<a id="canopies"></a>

## Station steel, solar roofs and safe access

Responsible role: station structural/roof engineer. Applied to 10 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-009, STD-CTRL-011, STD-CTRL-012, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Check wind, seismic, uplift, rain and maintenance loads. Design replaceable panels and safe roof access.

**Materials:** Freeze steel, fasteners, sandwich panels and bond build-up. Include corrosion, fire and UV compatibility.

**Assembly:** Use temporary bracing and surveyed base plates. Control roof-panel attachment and drainage sequence.

**Inspection:** Inspect structural joints, anchors, bonds and water ingress. Verify roof-access and edge-protection interfaces.

**Maintenance:** Inspect corrosion, wind damage and seal/drain condition. Plan safe module replacement with electrical isolation.

**Verification:** Independent structure/uplift and panel retention assessment. First erection, water and access-system tests.

**Open evidence and decisions:** Site loads and structural resistance basis. Qualified roof panels, bonds and safe maintenance access.

Basis: [ISO: ISO 12944-2:2017](https://www.iso.org/standard/64834.html), [FHWA: Bridge concrete technical resources](https://www.fhwa.dot.gov/bridge/concrete/), [Sika: Rail bonding and coating applications](https://industry.sika.com/en/home/transportation/rail.html).

<a id="station-services"></a>

## Station LV services, UPS, cabinets and lighting

Responsible role: station electrical/MEP engineer. Applied to 9 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-007, STD-CTRL-009, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Coordinate emergency supplies, earthing and cabinet thermal loads. Define loss-of-power and fire cause/effect.

**Materials:** Freeze switchgear, cable, enclosure and UPS specifications. Include protection, fire and weathering evidence.

**Assembly:** Verify protection settings, cable identity and bonds. Keep service access and fire penetration seals.

**Inspection:** Test insulation, grounding, backup duration and emergency lighting. Check cabinet thermal/ingress behaviour.

**Maintenance:** Inspect batteries, protection devices, ingress and terminal condition. Preserve isolation and UPS change records.

**Verification:** Protection/thermal and backup supply assessment. Installed electrical and emergency power-loss tests.

**Open evidence and decisions:** Applicable installation codes and emergency duration. Approved protection settings and actual load evidence.

Basis: [IEC: IEC 62497-1:2010 with AMD1:2013 review required](https://webstore.iec.ch/en/publication/7117), [ISO: ISO 21542:2021](https://www.iso.org/standard/71860.html), [FTA: Emergency preparedness planning guide (2003)](https://www.transit.dot.gov/oversight-policy-areas/public-transportation-system-security-and-emergency-preparedness-planning).

<a id="station-passenger"></a>

## Station information, fares, CCTV and help points

Responsible role: passenger systems/operations engineer. Applied to 18 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-006, STD-CTRL-014, STD-CTRL-015. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Design accessible fares, intelligible information and emergency calls. Keep passenger networks separate from safety control.

**Materials:** Freeze equipment, mounts and weatherproofing. Plan supplier support and privacy constraints.

**Assembly:** Survey accessible lanes and protected plinth cable paths. Verify speaker/camera coverage and help-point routing.

**Inspection:** Test transactions, power-loss egress and information consistency. Check audio/visual and accessible user journeys.

**Maintenance:** Maintain content, cleaning, backups and access controls. Periodically test emergency calls and gate fail states.

**Verification:** Accessible end-to-end passenger and fare tests. Power/comms-loss and OCC help-point failover tests.

**Open evidence and decisions:** Local fare/privacy rules and accessibility values. Actual speech, security and egress performance.

Basis: [ISO: ISO 21542:2021](https://www.iso.org/standard/71860.html), [NIST: SP 800-82 Rev. 3: operational technology security](https://csrc.nist.gov/pubs/sp/800/82/r3/final), [FTA: Emergency preparedness planning guide (2003)](https://www.transit.dot.gov/oversight-policy-areas/public-transportation-system-security-and-emergency-preparedness-planning).

<a id="vertical-access"></a>

## Approaches, lifts, escalators, stairs and overbridges

Responsible role: access/vertical transport engineer. Applied to 9 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-003, STD-CTRL-009, STD-CTRL-014, STD-CTRL-015. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Provide accessible routes under lift outage and evacuation scenarios. Coordinate clear widths, fall protection and structural interfaces.

**Materials:** Freeze lift/escalator, surfacing, rail and structural systems. Include slip, corrosion and enclosure exposure.

**Assembly:** Verify shaft/anchor interfaces and competent supplier installation. Protect accessible approach gradients and drainage.

**Inspection:** Survey clearances and accessible routes. Test emergency stop, rescue, outage and backup arrangements.

**Maintenance:** Retain competent statutory service/inspection records. Keep rescue access and outage passenger assistance current.

**Verification:** Applicable lift/escalator and structural acceptance review. Accessible journey, rescue and evacuation demonstration.

**Open evidence and decisions:** National lift/escalator codes and rescue authority. Actual capacity, route geometry and outage accessibility.

Basis: [ISO: ISO 21542:2021](https://www.iso.org/standard/71860.html), [FTA: Emergency preparedness planning guide (2003)](https://www.transit.dot.gov/oversight-policy-areas/public-transportation-system-security-and-emergency-preparedness-planning).

<a id="charging"></a>

## Train/wayside charging and traction substations

Responsible role: traction power/charging engineer. Applied to 7 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-007, STD-CTRL-009, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Coordinate charger, battery, protection and mechanical alignment. Require isolation before exposed contact and movement.

**Materials:** Freeze connector, cable, protection and power conversion specifications. Include arc, temperature and ingress ratings.

**Assembly:** Survey wayside alignment and bonding. Verify polarity, interlock I/O and protection settings.

**Inspection:** Test misalignment, stuck contactor, link loss and thermal limits. Confirm charger disconnect/traction-inhibit logic.

**Maintenance:** Inspect contacts, cable damage and cooling. Keep isolation procedures and approved firmware compatibility.

**Verification:** Charger/battery compatibility and protection assessment. Integrated energized/isolated, fault and movement-interlock tests.

**Open evidence and decisions:** Applicable fixed-installation/charging standards. Released current/duty and physical interface qualification.

Basis: [IEC: IEC 62497-1:2010 with AMD1:2013 review required](https://webstore.iec.ch/en/publication/7117), [IEC: IEC 62928:2017](https://webstore.iec.ch/en/publication/31101), [IEC: IEC 62290-1:2025](https://webstore.iec.ch/en/publication/83773).

<a id="solar-storage"></a>

## PV, stationary storage and microgrid integration

Responsible role: energy/electrical engineer. Applied to 14 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-007, STD-CTRL-009, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Model generation, export, backup and battery operation with actual climate. Separate stationary storage from onboard battery qualification.

**Materials:** Freeze PV, inverter, connector and stationary ESS systems. Require electrical, fire and weathering evidence.

**Assembly:** Verify connector compatibility, string polarity and bonding. Coordinate roof retention, lightning and safe isolation.

**Inspection:** Test protection, islanding/export policy and insulation. Record string configuration and real energy metering.

**Maintenance:** Inspect connectors, roof ingress, storage health and protection. Define fire response and safe module disposal.

**Verification:** Applicable PV/ESS/grid-code and fire assessment. Installed polarity/protection, backup and metered-energy tests.

**Open evidence and decisions:** Project grid rules and stationary-storage standards. Qualified ESS fire response and actual yield/lifecycle data.

Basis: [ISO: ISO 14040:2006](https://www.iso.org/standard/37456.html), [IEC: IEC 62497-1:2010 with AMD1:2013 review required](https://webstore.iec.ch/en/publication/7117), [NIST: SP 800-82 Rev. 3: operational technology security](https://csrc.nist.gov/pubs/sp/800/82/r3/final).

<a id="depots"></a>

## Depot lifts, workshops, wash, lathe and isolation

Responsible role: depot/workshop engineer. Applied to 9 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-001, STD-CTRL-003, STD-CTRL-014, STD-CTRL-015, STD-CTRL-016. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Design safe stabling, bogie change and heavy maintenance access. Coordinate recovery, wash, battery quarantine and fire separation.

**Materials:** Freeze lifting, tooling, service-fluid and equipment specifications. Provide calibrated inspection tools and qualified replacement parts.

**Assembly:** Release lifting foundations, synchronized lifts and crane interfaces. Verify workshop isolation and segregated vehicle movements.

**Inspection:** Test lift/crane protection, clearance and isolation. Inspect wash effluent, traction power and service interfaces.

**Maintenance:** Maintain competent lifting-equipment and tooling inspections. Retain work orders and controlled return-to-service records.

**Verification:** Site/workshop hazard and lift capacity assessment. Controlled first bogie change, isolation and recovery demonstration.

**Open evidence and decisions:** Applicable machinery/lifting/environmental rules. Qualified equipment and actual workshop capacity.

Basis: [ISO: ISO 55001:2024](https://www.iso.org/standard/83054.html), [ERA: Entities in charge of maintenance](https://www.era.europa.eu/domains/trains/certification-entities-charge-maintenance_en), [FTA: Emergency preparedness planning guide (2003)](https://www.transit.dot.gov/oversight-policy-areas/public-transportation-system-security-and-emergency-preparedness-planning).

<a id="operations"></a>

## Service planning, degraded operation and incident response

Responsible role: operator/operations lead. Applied to 30 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-001, STD-CTRL-003, STD-CTRL-014, STD-CTRL-015, STD-CTRL-016. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Plan capacity, dwell, headway and recovery against real route constraints. Define dispatch, degraded, evacuation and rescue authority.

**Materials:** Provide controlled consumables, spares and emergency supplies. Track replacement availability and shelf life.

**Assembly:** Train competent staff and rehearse handovers. Restrict unapproved bypasses and temporary configurations.

**Inspection:** Monitor service failures, energy and passenger outcomes. Inspect emergency readiness and accessible support.

**Maintenance:** Feed incidents into hazard and instruction review. Validate changes to operating envelopes and staffing.

**Verification:** Timetable/headway and degraded-service validation. Controlled emergency drills and operator competence assessment.

**Open evidence and decisions:** Approved operating rules and regulator acceptance. Actual availability, demand and emergency-response evidence.

Basis: [FTA: Public Transportation Agency Safety Plans](https://www.transit.dot.gov/PTASP), [IEC: IEC 62290-1:2025](https://webstore.iec.ch/en/publication/83773), [FTA: Emergency preparedness planning guide (2003)](https://www.transit.dot.gov/oversight-policy-areas/public-transportation-system-security-and-emergency-preparedness-planning).

<a id="maintenance"></a>

## Maintenance, spares, condition monitoring and return to service

Responsible role: maintenance authority. Applied to 28 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-001, STD-CTRL-003, STD-CTRL-014, STD-CTRL-015, STD-CTRL-016. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Allocate maintainable units and failure detection requirements. Keep time/mileage/cycle intervals distinct from diagnostic advice.

**Materials:** Control spares equivalence, expiry and obsolete suppliers. Preserve serial/lot and material genealogy.

**Assembly:** Use issued repair tasks and independent safety checks. Bind work orders, tools, NCRs and configuration changes.

**Inspection:** Verify repaired function and close mandatory holds. Retain failures including no-fault-found events.

**Maintenance:** Extend intervals only through approved duty/condition evidence. Freeze as-maintained configuration before return to service.

**Verification:** Maintenance task/interval and spares review. Physical repair, inspection and return-to-service demonstration.

**Open evidence and decisions:** Approved supplier/project intervals and acceptance authority. Validated diagnostic thresholds and interval changes.

Basis: [ERA: Entities in charge of maintenance](https://www.era.europa.eu/domains/trains/certification-entities-charge-maintenance_en), [ISO: ISO 55001:2024](https://www.iso.org/standard/83054.html), [Hitachi Rail: HMAX for signalling](https://www.hitachirail.com/products-and-solutions/digital-asset-management/hmax-for-signalling/).

<a id="level-crossings"></a>

## Level crossings, public interfaces and intrusion

Responsible role: crossing/public safety engineer. Applied to 2 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-006, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Assess separation, sighting, accessible passage and road/rail risks. Coordinate detection, protection, intrusion and emergency access.

**Materials:** Freeze crossing surface, barrier, lighting and detection systems. Include outdoor, wear and vandalism exposure.

**Assembly:** Verify approach geometry and fail-state wiring. Keep pedestrian paths and drainage clear.

**Inspection:** Test obstruction, protection failure and road/rail timing. Inspect visibility and accessible route condition.

**Maintenance:** Maintain detectors, barriers, surfaces and public information. Review near misses and changed traffic patterns.

**Verification:** Independent crossing/public risk assessment. Controlled fail-state, intrusion and road/rail integration tests.

**Open evidence and decisions:** Local crossing authority and legal protection requirements. Qualified traffic/detection and accessible crossing evidence.

Basis: [IEC: IEC 62278-1:2025](https://webstore.iec.ch/en/publication/68933), [IEC: IEC 62290-1:2025](https://webstore.iec.ch/en/publication/83773), [FTA: Public Transportation Agency Safety Plans](https://www.transit.dot.gov/PTASP).

<a id="vehicle-track-system"></a>

## Integrated vehicle, track, bridge and station dynamics

Responsible role: integrated vehicle/civil engineer. Applied to 40 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-001, STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-013, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Use one mass/load/geometry configuration across disciplines. Cover loaded/empty, braking, rescue, both tracks and degradation.

**Materials:** Use measured stiffness, damping, masses and profiles. Retain supplier/physical provenance and uncertainty.

**Assembly:** Reconcile actual datums and installed support conditions. Record deviations before dynamic trials.

**Inspection:** Keep model-domain failures and incomplete passages visible. Check force, energy and numerical refinement independently.

**Maintenance:** Review track/vehicle changes together. Monitor settlements, wear and changed service loads.

**Verification:** Independent coupled dynamics and complete passage campaign. Physical profile, load, modal and running-response correlation.

**Open evidence and decisions:** Validated contact model and complete six-car passage. Accepted safety/ride criteria and measured correlation data.

Basis: [ERA: LOC&PAS TSI and current application guidance](https://www.era.europa.eu/domains/technical-specifications-interoperability/rolling-stock-locomotives-and-passengers-tsi_en), [NASA: Systems engineering handbook: interfaces and verification](https://www.nasa.gov/reference/system-engineering-handbook-appendix/), [FTA: Report 0215: track inspection and maintenance](https://www.transit.dot.gov/research-innovation/research-report-and-findings-review-standards-track-inspection-and-maintenance).

<a id="energy-system"></a>

## Integrated train, charger, route and energy supply

Responsible role: system energy engineer. Applied to 21 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-001, STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-013, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Balance duty-cycle traction, auxiliaries, regeneration and charging. Include low state of charge, failed chargers and reserve policy.

**Materials:** Use released chemistry, efficiency maps and climate ageing data. Control supply/storage lifecycle boundaries.

**Assembly:** Reconcile actual train and wayside configurations. Verify charger compatibility before energisation.

**Inspection:** Use calibrated synchronized meters and energy residuals. Retain unmet-demand and curtailed-regeneration scenarios.

**Maintenance:** Track battery health and actual energy per duty. Reassess timetables and supply when assets degrade.

**Verification:** Independent energy/thermal and contingency assessment. Metered full-duty and failed-charger validation.

**Open evidence and decisions:** Accepted reserve, range and energy criteria. Measured efficiency/ageing maps and actual grid/charging capacity.

Basis: [IEC: IEC 62928:2017](https://webstore.iec.ch/en/publication/31101), [ISO: ISO 14040:2006](https://www.iso.org/standard/37456.html), [CRRC: Primary account of lifecycle automation, redundancy, running-gear monitoring and efficient traction](https://www.crrcgc.cc/en/2026-04/29/article_2026042916024714810.html).

<a id="boarding-system"></a>

## Integrated accessible passenger journey and evacuation

Responsible role: accessibility/fire/operations lead. Applied to 29 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-001, STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-013, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Validate street-to-seat and safe-return journeys together. Include crowded, lift-outage, wrong-side and emergency conditions.

**Materials:** Choose tactile, slip, signage and fire systems for actual use. Retain compatibility of installed passenger fixtures.

**Assembly:** Reconcile platform, train, doors and access routes. Protect clearance after fit-out and maintenance.

**Inspection:** Test complete journeys with relevant user needs. Verify information, assistance and emergency access.

**Maintenance:** Provide controlled outage assistance and inspection tasks. Review incident feedback and changed demographics.

**Verification:** Independent accessible journey and evacuation review. Physical boarding, outage assistance and emergency exercises.

**Open evidence and decisions:** Adopted access and evacuation acceptance rules. Representative user validation and integrated physical evidence.

Basis: [ISO: ISO 21542:2021](https://www.iso.org/standard/71860.html), [FTA: Emergency preparedness planning guide (2003)](https://www.transit.dot.gov/oversight-policy-areas/public-transportation-system-security-and-emergency-preparedness-planning), [Knorr-Bremse / IFE: Train entrance systems](https://www.knorr-bremse.us/en/products/door-systems/entrance-systems/).

<a id="control-system"></a>

## Integrated safety control, power, doors and operations

Responsible role: system safety/control engineer. Applied to 44 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-001, STD-CTRL-002, STD-CTRL-003, STD-CTRL-004, STD-CTRL-013, STD-CTRL-014. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Define safe states for stale inputs, common causes and partial power loss. Keep diagnostics, navigation and maintenance requests subordinate to authority.

**Materials:** Freeze combined hardware/software and security baselines. Review failure/obsolescence of shared services.

**Assembly:** Verify complete interface topology and fail-state mapping. Independently check configured safety I/O.

**Inspection:** Test combined brake, door, charger, detection and communication faults. Retain failed and interrupted trials.

**Maintenance:** Control overrides and updates with independent review. Prove recovery without silent safety bypass.

**Verification:** Independent integrated safety/cyber/interface review. Approved physical multi-fault and degraded-mode campaign.

**Open evidence and decisions:** Actual safety architecture, communication contracts and integrity levels. Independent qualification and operating authority.

Basis: [IEC: IEC 62278-1:2025](https://webstore.iec.ch/en/publication/68933), [IEC: IEC 62290-1:2025](https://webstore.iec.ch/en/publication/83773), [NIST: SP 800-82 Rev. 3: operational technology security](https://csrc.nist.gov/pubs/sp/800/82/r3/final).

<a id="software-lifecycle"></a>

## Software requirements, deterministic behaviour and target validation

Responsible role: software assurance lead. Applied to 60 scoped definitions. Status: recommended; project adoption open.

Existing assurance objectives: STD-CTRL-002, STD-CTRL-005, STD-CTRL-006, STD-CTRL-013, STD-CTRL-014, STD-CTRL-016. Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.

**Design:** Derive bounded, deterministic behaviours from allocated hazards and interface contracts. Separate simulation/proof assumptions from actual target timing and I/O.

**Materials:** Pin source, dependencies, toolchains and reproducible artifact identities. Track firmware support, vulnerabilities and third-party licence obligations.

**Assembly:** Build reviewed artifacts with controlled deployment settings. Verify startup, watchdog, resource and hardware-interface configuration.

**Inspection:** Use independent review and requirement-derived unit/integration/formal checks. Retain failed, incomplete and unsupported-target checks.

**Maintenance:** Control updates, rollback and repair configuration. Reassess proof assumptions and target behaviour after dependency or interface changes.

**Verification:** Independent software requirement, tool and configuration review. Target-hardware timing, resource, HIL and fault-response validation.

**Open evidence and decisions:** Project safety/software integrity allocation and adopted clauses. Actual target I/O, timing, tool qualification and independent acceptance.

Basis: [IEC: IEC 62279:2015](https://webstore.iec.ch/en/publication/22781), [NIST: SP 800-82 Rev. 3: operational technology security](https://csrc.nist.gov/pubs/sp/800/82/r3/final), [NASA: Systems engineering handbook: interfaces and verification](https://www.nasa.gov/reference/system-engineering-handbook-appendix/).

## Source limitations and refresh

All references were reviewed on the date recorded below. ISO/IEC/EN entries are public-scope discovery, with complete adopted clause review open. Regulatory scope depends on project jurisdiction and system type. Manufacturer examples contribute methods; no proprietary design, guaranteed improvement or accepted supplier specification is redistributed.

Refresh policies are OSR research rules: regulatory sources 90 days, manufacturer examples 180 days, standard scopes 365 days, method references 730 days. Checks use an explicit assessment date; a source overdue for review stays visible in the audit.

- [CRRC: Primary account of lifecycle automation, redundancy, running-gear monitoring and efficient traction](https://www.crrcgc.cc/en/2026-04/29/article_2026042916024714810.html) (manufacturer-practice; reviewed 2026-10-11). Primary account of lifecycle automation, redundancy, running-gear monitoring and efficient traction Manufacturer claims; performance objectives require OSR duty-cycle baselines and independent evidence

- [Alstom: Repeatable special processes, equipment monitoring, competence and lean production](https://www.alstom.com/sites/alstom.com/files/2025/04/24/Alstom_Whitepaper_SmartManufacturing_EN.pdf) (manufacturer-practice; reviewed 2026-10-11). Repeatable special processes, equipment monitoring, competence and lean production Methods adapted as original OSR controls; no robot count or productivity claim transferred

- [Alstom: Digital work instructions and per-joint smart torque records](https://www.alstom.com/press-releases-news/2024/4/different-and-smart-approach-maintaining-trains) (manufacturer-practice; reviewed 2026-10-11). Digital work instructions and per-joint smart torque records OSR stores open tool-neutral records; no vendor cloud implementation copied

- [Siemens: Resource scheduling with coating/drying and quality dependencies](https://resources.sw.siemens.com/de-DE/case-study-increase-efficiency-and-productivity-with-digital-scheduling/) (manufacturer-practice; reviewed 2026-10-11). Resource scheduling with coating/drying and quality dependencies Actual durations and process windows require released material/process data

- [Siemens: Measurement context, temperature and calibration traceability](https://references.siemens.com/en/reference/32785?id=32785) (manufacturer-practice; reviewed 2026-10-11). Measurement context, temperature and calibration traceability No proprietary inspection software dependency

- [Alstom: Energy, recyclability and lifecycle-aware material choices](https://www.alstom.com/company/sustainability/environment) (manufacturer-practice; reviewed 2026-10-11). Energy, recyclability and lifecycle-aware material choices No environmental percentages adopted; supplier EPD and repair evidence remain required

- [NIST: Diagnostic spread/capability statistics and their stability/distribution/sample assumptions](https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc16.htm) (method; reviewed 2026-10-11). Diagnostic spread/capability statistics and their stability/distribution/sample assumptions No universal Cpk acceptance threshold or process qualification inferred

- [BIPM: Uncertainty-aware conformity decisions; explicit decision-rule selection](https://www.bipm.org/en/doi/10.59161/jcgm106-2012) (method; reviewed 2026-10-11). Uncertainty-aware conformity decisions; explicit decision-rule selection Conservative interval containment is an OSR internal rule, not a universal ISO acceptance rule

- [ISO: ISO 22163:2023 railway quality-management scope](https://www.iso.org/standard/79427.html) (standard-scope; reviewed 2026-10-11). ISO 22163:2023 railway quality-management scope Public scope reviewed; controlled clauses, amendments and conformity assessment remain open

- [ISO: ISO 3834-2:2021 fusion-welding quality scope](https://www.iso.org/standard/81651.html) (standard-scope; reviewed 2026-10-11). ISO 3834-2:2021 fusion-welding quality scope Public scope reviewed; material/process-specific qualification remains open

- [NASA: Systems engineering handbook: interfaces and verification](https://www.nasa.gov/reference/system-engineering-handbook-appendix/) (method; reviewed 2026-10-11). Integration and verification planning connect requirements, interfaces and evidence. A systems-engineering method reference; NASA requirements are not rail operating rules.

- [IEC: IEC 62278-1:2025](https://webstore.iec.ch/en/publication/68933) (standard-scope; reviewed 2026-10-11). Railway RAMS lifecycle management scope. Public scope only; project safety allocation and the applicable complete standard series require controlled review.

- [IEC: IEC 62290-1:2025](https://webstore.iec.ch/en/publication/83773) (standard-scope; reviewed 2026-10-11). Urban guided transport management and command/control concepts. No GoA4 certification, protocol specification or safety integrity level inferred from the public scope.

- [IEC: IEC 62928:2017](https://webstore.iec.ch/en/publication/31101) (standard-scope; reviewed 2026-10-11). Onboard lithium-ion traction battery design and test scope. Stationary storage and charging installations need their own applicable standards; no cell-to-pack approval inferred.

- [IEC: IEC 61373:2010](https://webstore.iec.ch/en/publication/5395) (standard-scope; reviewed 2026-10-11). Railway equipment shock and vibration test scope. Mounting category, test levels and clauses require project review; a CAD attachment is not qualification.

- [IEC: IEC 62497-1:2010 with AMD1:2013 review required](https://webstore.iec.ch/en/publication/7117) (standard-scope; reviewed 2026-10-11). Rail insulation coordination includes rolling stock, signalling and fixed installations. Adopted edition/amendment, altitude, pollution, voltage and clearances require controlled clause review.

- [IEC: IEC 62236-3-2:2018](https://webstore.iec.ch/en/publication/62682) (standard-scope; reviewed 2026-10-11). Rolling-stock apparatus electromagnetic compatibility scope. Apparatus evidence does not qualify the complete vehicle or wayside system; select other series parts as applicable.

- [ISO: ISO 55001:2024](https://www.iso.org/standard/83054.html) (standard-scope; reviewed 2026-10-11). Asset-management requirements address lifecycle decisions. A management-system reference, not a component maintenance interval or asset certification.

- [ISO: ISO 21542:2021](https://www.iso.org/standard/71860.html) (standard-scope; reviewed 2026-10-11). Accessibility and usability of buildings and their approaches. Vehicle and platform boarding limits and national accessibility rules require separate adoption.

- [ISO: ISO 19659-2:2020](https://www.iso.org/standard/70232.html) (standard-scope; reviewed 2026-10-11). Passenger-area thermal comfort and measurement scope. Does not cover driver-cab thermal comfort; climate, loads and acceptance values need project selection.

- [ISO: ISO 19659-4:2026](https://www.iso.org/standard/85202.html) (standard-scope; reviewed 2026-10-11). HVAC customer design inputs and unit test/inspection scope. Public scope reviewed; unit test evidence must be integrated with saloon/cab and installed duct performance.

- [ISO: ISO 3381:2021](https://www.iso.org/standard/77368.html) (standard-scope; reviewed 2026-10-11). Reproducible vehicle interior noise type-test methods. No universal noise limit or whole-journey exposure result inferred.

- [ISO: ISO 12944-2:2017](https://www.iso.org/standard/64834.html) (standard-scope; reviewed 2026-10-11). Steel protective-coating exposure classification. Classification alone does not select a coating; preparation, application, durability and inspection require additional applicable methods.

- [ISO: ISO 14040:2006](https://www.iso.org/standard/37456.html) (standard-scope; reviewed 2026-10-11). Lifecycle assessment goal, scope and interpretation framework. Review amendment and other applicable LCA/EPD methods; no carbon saving transferred from a vendor statement.

- [BSI: BS EN 45545-2:2020+A1:2023](https://knowledge.bsigroup.com/products/railway-applications-fire-protection-on-railway-vehicles-requirements-for-fire-behaviour-of-materials-and-components-2) (standard-scope; reviewed 2026-10-11). Rail vehicle material/component fire-behaviour scope. Hazard/category, requirement set and actual installed build-up require controlled review; no blanket fire rating.

- [NIST: SP 800-82 Rev. 3: operational technology security](https://csrc.nist.gov/pubs/sp/800/82/r3/final) (method; reviewed 2026-10-11). OT security must account for physical processes, availability and safety. Reference guidance; railway threat model and applicable IEC/rail-specific cyber requirements remain project decisions.

- [ERA: LOC&PAS TSI and current application guidance](https://www.era.europa.eu/domains/technical-specifications-interoperability/rolling-stock-locomotives-and-passengers-tsi_en) (regulatory-scope; reviewed 2026-10-11). Vehicle/subsystem interfaces and links to current guidance and amendments. EU interoperability applicability must be decided for each project; metro/tram scope is not assumed. No global legal adoption.

- [ERA: Entities in charge of maintenance](https://www.era.europa.eu/domains/trains/certification-entities-charge-maintenance_en) (regulatory-scope; reviewed 2026-10-11). Maintenance functions require responsibility and traceability in the ECM system. EU certification applicability is project-dependent; guidance version 10.0 (2025) listed at review.

- [FTA: Public Transportation Agency Safety Plans](https://www.transit.dot.gov/PTASP) (regulatory-scope; reviewed 2026-10-11). Agency safety plans incorporate safety-management processes. US funding/oversight applicability is limited; OSR adapts the management approach, not a global legal requirement.

- [FTA: Report 0215: track inspection and maintenance](https://www.transit.dot.gov/research-innovation/research-report-and-findings-review-standards-track-inspection-and-maintenance) (method; reviewed 2026-10-11). Review of US rail-transit inspection and maintenance practice. 2022 research portal reviewed; local defect limits, intervals and current rules require independent selection.

- [FTA: Emergency preparedness planning guide (2003)](https://www.transit.dot.gov/oversight-policy-areas/public-transportation-system-security-and-emergency-preparedness-planning) (method; reviewed 2026-10-11). Emergency response planning is a system lifecycle activity. Historical planning reference; current fire, evacuation and emergency-response requirements must govern each project.

- [FHWA: Bridge concrete technical resources](https://www.fhwa.dot.gov/bridge/concrete/) (method; reviewed 2026-10-11). Public precast/prestressed bridge construction and assessment resources. Road bridge methods need railway load, fatigue, vibration and jurisdiction transfer review; no curing duration adopted from the portal.

- [FHWA: Bridge preservation resources](https://www.fhwa.dot.gov/bridge/preservation/) (method; reviewed 2026-10-11). Preservation and service-life planning include assessment and maintenance. Road bridge reference; actual railway inspection criteria and access plans remain project-specific.

- [SKF: Evolution of railway axlebox technology](https://evolution.skf.com/en/the-evolution-of-railway-axlebox-technology/) (manufacturer-practice; reviewed 2026-10-11). Axlebox bearing architecture includes sealing, lubrication and integration. Supplier architecture reference; fits, loads, lubricants, life and intervals require released supplier data.

- [Continental: Railway secondary suspension](https://www.continental-industry.com/global/en/products-solutions/airsprings-suspension/railway/secondary-suspension) (manufacturer-practice; reviewed 2026-10-11). Air-spring solutions couple vehicle support and ride behaviour. No universal stiffness, emergency capacity or maintenance interval inferred.

- [Knorr-Bremse: Adhesion and wheel-slide protection](https://rail.knorr-bremse.com/en/us/portfolio/products-and-systems/braking-systems/adhesion/) (manufacturer-practice; reviewed 2026-10-11). Adhesion management and wheel-slide protection belong to integrated braking systems. No stopping-distance improvement or proprietary control algorithm adopted; qualify actual duty and degraded modes.

- [Knorr-Bremse / IFE: Train entrance systems](https://www.knorr-bremse.us/en/products/door-systems/entrance-systems/) (manufacturer-practice; reviewed 2026-10-11). Entrance equipment is supplied as integrated door systems. No closing force, speed, geometry or interoperability acceptance imported from marketing.

- [Sika: Rail bonding and coating applications](https://industry.sika.com/en/home/transportation/rail.html) (manufacturer-practice; reviewed 2026-10-11). Rail bonding requires application-specific design, production and material data; EN 17460 is identified. Supplier method context, not independent proof of product superiority or bonding certification; review EN 17460 separately.

- [Pandrol: Fastclip rail fastening system](https://www.pandrol.com/products/fastening-systems/fasteners/fastclip) (manufacturer-practice; reviewed 2026-10-11). Elastic fastening is a rail/pad/insulator/clip installation system. Specific vendor system is a candidate only; no generic clip force, spacing or approved interchangeability.

- [voestalpine Railway Systems: Turnout systems and lifecycle integration](https://www.voestalpine.com/railway-systems/en/company/news/turnout-systems-intelligent-networked-and-future-proof.-system-thinking-for-rail-infrastructure-excellence./?year=2025) (manufacturer-practice; reviewed 2026-10-11). Turnout geometry, actuation, signalling and lifecycle care are treated as one system. Vendor lifecycle approach; no actuator load or inspection interval adopted.

- [Hitachi Rail: HMAX for signalling](https://www.hitachirail.com/products-and-solutions/digital-asset-management/hmax-for-signalling/) (manufacturer-practice; reviewed 2026-10-11). Asset monitoring supports maintenance decisions for signalling. Advisory monitoring is not safety authority; no predictive accuracy, interval extension or vendor platform dependency adopted.

- [buildingSMART: IFC railway domain and open exchange](https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcRailway.htm) (method; reviewed 2026-10-11). IFC 4.3 provides railway spatial structures for open information exchange. Export must be checked for units, identity and semantics; an IFC file is not a construction release.

- [IEC: IEC 62279:2015](https://webstore.iec.ch/en/publication/22781) (standard-scope; reviewed 2026-10-11). Railway control/protection software development process scope. Full clauses, tool qualification and applicable edition transitions require project review. Source SIL/GoA target labels do not establish achieved integrity.

## Expansion boundaries

- **tunnels** (research-and-design-open): No detailed tunnel product catalogue in this inventory; fire/smoke control, lining, ventilation, waterproofing and evacuation require separate expansion.
- **overhead-third-rail** (research-and-design-open): The current charging architecture does not define a complete overhead/third-rail collection system; add power collection, return current and stray-current assurance if adopted.
- **kits-and-consumables** (decomposition-open): Every catalogued kit is mapped, but its fasteners, crimps, seals and fluids need a released piece-level BOM and scoped verification.
- **other-fleets** (variant-transfer-open): LM3 catalogue practices are candidates for other consist families; lengths, loads, interfaces and evidence require configuration-specific transfer review.
- **full-standard-clauses** (applicability-and-clause-review-open): Public scopes support discovery only; adopt controlled complete ISO/IEC/EN and local requirements with clause-level traceability before acceptance.
