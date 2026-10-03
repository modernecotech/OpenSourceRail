# Baghdad detailed engineering and Iraqi manufacturing plan

Baghdad uses a **six-car, 111 m metro family**. The next design stage retains ballastless slab track and expands the civil, mechanical, electronics and software packages into controlled interfaces, parts and manufacturing operations. The [component register](engineering/detail/README.md), [parts CSV](engineering/detail/parts.csv) and [source-bound JSON](engineering/detail/register.json) contain the calculated city quantities and open supplier positions. These are engineering references; production drawings, surveys, qualified suppliers and operational approvals remain required.

The current city allocation is 831 trainsets, 4,986 cars, 182 stations and 158 energy sites. The two-bogie-per-car reference gives 9,972 bogies and 19,944 wheelsets. Wheelsets are children of complete bogies, not extra purchases. Doors, cooling loops, fixtures, harnesses and equipment repeats are reference allocations that must pass the six-car family review. The detailed three-car LM3 manufacturing package is useful process evidence; it is not a released Baghdad production package and cannot be doubled to obtain qualified six-car interfaces.

## Reference architecture and drawing package

The mechanical load path is wheelset to suspension/axlebox to bogie frame to secondary suspension/pivot to car underframe to coupler and body structure. Cladding attaches to the structural frame through controlled service rails and retention features; FRP panels do not replace the primary crash structure. Keep longitudinal crash loads, recovery loads, passenger fixture loads and equipment retention as separate calculation cases with a common drawing revision.

The electrical path is protected charging contact to traction battery/HV junction to inverters/motors and protected auxiliary DC/DC branches. Battery, inverter and motor cooling circuits require a coordinated heat balance. The nominal traction bus is 675 V and normal maximum 740 V; “800 V class” describes a component class, not the normal bus voltage. Coordination must include abnormal/transient limits, insulation monitoring, HV interlocks, precharge, discharge, isolation and emergency disconnect.

| Controlled drawing | Required content | Reference data available | Release owner / remaining evidence |
|---|---|---|---|
| BG-M-001 Trainset arrangement | Six-car positions, couplers, gangways, swept and evacuation envelopes | 111 m train envelope; six cars; five intercar interfaces; two ends | Rolling-stock authority: exact end/coupler lengths, curve sweep and tolerance stack |
| BG-M-002 Car structure | Underframe/side/roof members, joints, datums, lift/recovery points | 18.5 m average module allocation; geometry is not a cut list | Structures: stress/fatigue/crash, weld map, material thicknesses, distortion and NDT |
| BG-M-003 Bogie interface | Pivots, spring/air attachments, wheel profile, brake/motor clearances | One powered and one trailer bogie per car reference | Supplier + dynamics authority: axle loads, suspension rates, hunting, curves and brake duty |
| BG-M-004 Battery and HV bay | Racks, crash retention, isolation, vent paths and removable pack access | 225 kWh gross allocation per car; 1,350 gross / 1,080 usable per train | HV/battery authority: actual pack mass/dimensions, fault current, thermal propagation and retention |
| BG-M-005 Cooling and HVAC | Chiller/radiator/pump, hoses, expansion/bleed, ducts and condensate | Hot-desert 50 °C design ambient | Thermal authority: traction/aux duty, degraded operation, dust and heat rejection |
| BG-M-006 Door/glazing | Openings, leaves, locks, seals, glazing retention and maintenance access | Two double-leaf openings per side/car reference | Body + accessibility authority: family-specific layout, loading, escape and obstruction |
| BG-M-007 Harness and connector | Wire/terminal IDs, cavity views, cut lengths, routing, clamps and separation | HV/LV/data service zones; reference host counts | Electrical authority: current/voltage drop, insulation, EMC, connector and supplier pin freeze |
| BG-M-008 Interior/accessibility | Seats, rails, ramps/steps, lighting, fire barriers and service panels | 720 nominal passengers, 120 seats, 960 crush per train | Interior authority: fixture loads, fire/smoke, accessibility and passenger evacuation |
| BG-C-001 ST6 and slipform section | Concrete geometry, cage, inserts, rail seats, drainage and transitions | Six-metre panel geometry and 20 seats | Track/civil authority: reinforcement, support stiffness, shrinkage, fasteners and actual geotechnical zones |
| BG-C-002 Viaduct and bridge interfaces | Pi20/Pi25, foundations, bearings, joints, CWR and walkway interfaces | Standard 20/25 m spans; bridge-specific exceptions | Structures: permanent/variable/thermal/seismic/braking, fatigue, scour and foundation release |
| BG-E-001 End electronics cabinet | Rails, protection, output chain, harness, thermal and enclosure | Corrected T-OBS capacity and exposed Pico bench pins | Electronics authority: actual vendor BOM, schematic, HAL, EMC and injected faults |

Use train longitudinal datum X, track centre Y and surveyed rail datum Z for integration. Each supplier drawing must state its own mating datum and tolerance contribution. The track reference gauge is 1,435 mm between the running faces; rail-head width and inclination are needed to convert this into rail-centre/baseplate coordinates. Existing simplified CAD rail-line positions must not be used as drilling coordinates. A platform step/gap or bogie pivot offset copied from LM3 is an unresolved six-car interface until reviewed.

## Mechanical manufacturing and missing kit content

Local work can cover steel structure fabrication, service rails, FRP moulding/trim, interiors, mounts, battery enclosures, harness manufacture, pipework and final integration. Initially import complete qualified bogies, motor/inverter packages, cells/qualified packs, safety glazing, doors and electronics where local process and product qualification is absent. A later local-content decision needs supplier drawings/licences, process capability, acceptance tests and economics; local fabrication is not evidence that a safety-critical design is accepted.

| Work package | Make/buy and production route | Child content that must be explicit | Verification / hold point |
|---|---|---|---|
| Car frame | Iraqi cut/form/machine/fixture/weld | Plates/sections, brackets, joint preparation, isolation, drains and finish | Released datum/fixture, WPS, weld/NDT, dimensional and load inspection |
| FRP skin | Iraqi mould/layup/cure/trim/fit | Resin/fibre/core, inserts, retention clips, edge seals and fire-compatible finish | Laminate/fire/smoke, cure coupon, insert pullout and panel retention |
| Bogie | Complete supplier package first | Wheels/axles, bearings, suspension, dampers, brakes, grounding and guards | Family axle-load/dynamics/brake qualification and complete serial records |
| Battery/HV | Import qualified core; locally integrate after approval | Rack, fuses, contactors, precharge, disconnect, HVIL, BMS, sensors, vent/containment and service lift | Supplier duty, propagation, isolation, fault-current and retention tests |
| Thermal | Local formed tube/hose/brackets with sourced pumps/chillers | Fluid, filters, manifolds, isolation valves, drains, bleed/expansion and leak detection | Pressure/cleanliness, heat balance at hot ambient and failure response |
| Brake | Supplier-controlled complete design | Compressor, dryer, reservoir, valve blocks, parking brake, hoses and sensors | Pressure/leak, stop distance, adhesion/degraded modes and rescue |
| Doors/glass | Qualified sourced units with local frame/fitting | Lock/detection/obstruction, emergency release, drainage, seals, adhesive and retainers | Opening alignment, force/leak/retention and interlock to safety host |
| Wiring | Iraqi formboard/cut/crimp/test | Cable, contacts, mating halves, seals, glands, shielding, clamps and labels | Calibrated crimp/pull, cavity checks, continuity and insulation |
| Final vehicle | Local installation and configuration | Torque evidence, fluids, firmware, mass/CG, identification and handover records | Weighed family vehicle, static brake/door tests, route acceptance and traceability |

The existing small-component standard, factory release, tooling, inspection and mass-closure modules remain useful. Their product IDs and drawing seeds must be cross-referenced to a Baghdad family-specific EBOM/MBOM before ERP Work Orders are released. No exact bolt torque, weld size, laminate layup or heat-exchanger area is invented here. Those values must close the applicable load, thermal or supplier calculation.

## Slab track decision

Choose **ballastless slab track as the reference permanent way**. Use continuous slipforming for long, open, machine-accessible at-grade sections; use Iraqi-made **OSR-ST6 single-track precast panels** in constrained streets, utility/transition zones, short possessions, station/depot interfaces and replaceable sections. On standard elevated Pi20/Pi25 structures, use direct-fixation plinths above the structural flange with a thin alignment layer only where needed. Floating track is a location-specific vibration treatment, not a blanket addition.

Slab track is selected for the design package because it supports controlled alignment, modular installation and local concrete work. Lifecycle value must be tested against settlement risk, access, repairability, construction traffic, drainage and noise. It is not inherently cheaper on weak or uninvestigated ground. Keep ballasted/special transition arrangements available as engineered exceptions where life-cycle, geotechnical or depot requirements justify them.

| ST6 single-track reference | Value / quantity |
|---|---|
| Dimensions | 6,000 × 2,900 mm; 250 mm base; two 380 × 160 mm plinths |
| Double track | Two independently manufactured rows on 3,500 mm centres |
| Concrete, base and plinths | 5.0796 m³ per panel; excludes service-trough envelope, bedding and steel |
| Bare concrete planning mass | 12.699 t at 2,500 kg/m³; steel, inserts and lifting rig add weight |
| Reinforcement allowance | 761.94 kg at 150 kg/m³; not a released bar schedule |
| Rail seats | 20 per panel; 10 per rail, at X = 300 + 600 × i mm, i = 0…9 |
| Repeated-module seat pitch | 600 mm including the panel joint; maximum reference spacing remains 650 mm |
| Complete seat child allocation | One pad/baseplate kit, two clips, two lateral insulators, two anchor assemblies and one adjustment kit; supplier pattern to freeze |
| Bedding illustration | 30 mm over 17.4 m² = 0.522 m³; actual support/grout design required |
| Lifting illustration | Four engineered anchors; supplier load sharing, strength, angle and rigging required |

The previous CAD placed the first baseplate centre at the concrete edge, extending its 260 mm footprint beyond the panel. The corrected layout centres seats inside the module and keeps uniform pitch across repeated joints. Continuous-run planning quantities still use the existing 650 mm basis; precast method zones need their own 20-seat-per-panel schedule. Do not apply a single rounded per-km seat allowance as a fabrication order for every six-metre panel.

A complete track seat needs the matched rail, baseplate, resilient pad/layer, clips, insulators, anchors, shim/adjustment and tested fastening system. The legacy sleeper/clip CAD remains a ballasted alternative; it is not the default slab-track MBOM. Source proprietary/safety-critical elastic parts and qualified anchors initially; manufacture concrete/cages, ducts/covers, moulds, jigs and appropriate metalwork locally. Local clip or pad manufacture requires licensing/material/process/fatigue and insulation qualification, not just matching the rendered shape.

Pandrol's published direct-fixation system provides an example of adjustable, resilient fastening for slab structures with system-specific performance and testing. This supports the architecture; it does not select Pandrol, approve an equivalent, transfer the vendor stiffness/adjustment values to OSR or establish Iraq pricing. [Pandrol technical sheet](https://www.pandrol.com/wp-content/uploads/2019/04/V13939_Pandrol-Bonded_DFF_ADH_Technical_Sheet_v3.pdf).

## Iraqi slab manufacturing line

Add a dedicated slab line alongside the shared Baghdad plant or a route-adjacent civil yard after a haulage/capacity comparison. Do not consume the same Pi-beam moulds, crane shifts or curing spaces twice in the production programme. A mould row must record mould ID, cycle, available shifts, crane allocation, rejected pieces and actual release strength. The previous 24-hour mould-cycle target remains a trial target; use the existing 48-hour planning basis until hot-weather trials substantiate an alternative.

1. Release panel/cage/insert drawings, supplier fastener pattern, concrete mix/exposure class and prototype inspection plan.
2. Qualify Iraqi cement, aggregate, water and admixtures for the site sulfate/chloride exposure. Check shrinkage, creep and curing rather than assuming a higher concrete grade solves durability.
3. Build surveyed reusable steel moulds, cage/weld jigs and insert/rail-seat gauges. Fit engineered lifting sockets, bonding/drain sleeves and unique panel identity.
4. Inspect cage cover, insert positions, cleanliness and mould dimensions before casting. Record supplier/batch and mixing conditions.
5. Place/vibrate the approved mix or use qualified self-compacting concrete. Protect from heat/wind, control moisture and record maturity against strength tests.
6. Release lifting only at the calculated strength. Survey rail-seat datums, flatness, geometry and cracks; record repair/rejection decisions against panel serials.
7. Transport with designed support points and route clearance; inspect after transport. Install on accepted formation/bed, grout under the released procedure and survey rail alignment.
8. Install the matched fastening system, complete CWR welding/stress management, verify gauge/cant/height and inspect bonding/insulation/drainage. Record the as-installed rail/fastener/panel configuration.
9. Perform proof loading/ride/geometry and monitored settlement trials before series deployment. Retain replaceability and maintenance-access demonstrations.

The line requires batching/aggregate handling, controlled curing, slab moulds, cage jigs, insert fixtures, maturity/strength testing, survey gear, lifting frames, certified rigging and loading/storage space. Iraqi labour can fabricate cages/moulds and operate casting, survey, installation and maintenance; specialist training, qualified lifting/welding and independent inspection need funded work packages. No construction-job count or local-content percentage is asserted without a priced resource and origin schedule.

A quantity example for **one kilometre of double track wholly assigned to ST6** is 334 full panels = 2 × ceil(1,000/6), 6,680 seats and 1,696.5864 m³ of base/plinth concrete. These cover 1,002 m per track with end trimming/interface treatment unresolved. It is an example, not Baghdad's method allocation. If the surveyed constrained length is L on each of the two tracks, use 2 × ceil(L/6) and separately schedule short end pieces; do not infer L from all at-grade kilometres.

## Civil interfaces that need completion

| Interface | Required design information | Acceptance and cost implication |
|---|---|---|
| Formation/slab | Ground zones, groundwater, modulus, settlement, sulfate exposure, utility trenches | Settlement and transition design; preparation/ground improvement measured by zone |
| Drainage/flood | Catchments, design storm, outlet levels, maintenance access, debris and scour | Cable routes separated from wet channels; outfalls/attenuation/pumps counted where required |
| Viaduct/slab/CWR | Thermal range, neutral rail temperature, braking, deck movement and restraint | Rail–structure interaction analysis; no automatic expansion device at every deck gap |
| Bearings/continuity | Unit lengths, pier stiffness, seismic/thermal restraints, replacement/lift access | Supplier bearing envelope and certified reactions; quantity schedule by actual support |
| River/highway bridges | Survey/navigation, scour, traffic/diversion, foundations and special spans | Separate bridge design; standard Pi spans do not release major crossings |
| Elevated evacuation | Walkway/barrier loads, clear width, station access and rescue route | Outer 1 m cassette reference checked against obstruction and fire/evacuation rules |
| Station boarding | Six-car swept envelope, floor height, tolerance and accessibility | Surveyed step/gap and dwell/evacuation capacity; LM3 offsets cannot be copied blindly |
| Depot/stabling | 831-train circulation and storage, workshop equipment, wash/drainage/recovery | Existing USD8m depot allowance needs detailed scope and pricing; workshop bays are not parking |
| Plant/logistics | Crane charts, rig loads, haul route, curing, power/water/waste and laydown | 12.699 t concrete panel is not the certified shipping/lift weight; steel/rigging included |

Keep the existing construction-method and foundation catalogs. Their “actual length and cost required” gates prevent generic deep-pile lengths from being adopted as surveyed Baghdad foundations. Release each geotechnical zone and map it to the alignment segments before recalculating quantities and installed costs.

## Onboard electronics corrections

The revised [T-OBS bench design](../../../../../control-electronics/t-obs/diy-assembly/README.md) and [integration JSON](../../../../../control-electronics/reference-integration.json) close erroneous interface assumptions and add missing power, watchdog, relay-feedback, harness and external-controller blocks. They do not release a production board or pretend that a driver exists because its crate appears in the workspace.

| Issue identified | Corrected design treatment |
|---|---|
| HDR-60-24 treated as 24 V to 5/12 V | It is AC/high-voltage DC input to 24 V output; use appropriately protected DC/DC branches onboard |
| USB isolator used as SPI / Pico device-to-device link | Use directionally correct SPI isolation with one controller and one peripheral |
| TPS3701 called dual heartbeat watchdog | Voltage detector only; separate channel heartbeat watchdogs and hardware inhibition |
| Pico GP30–39, ADC at GP14–17, native CAN/RMII | Exposed Pico pins and supported functions only; custom chip pinout separately frozen; external CAN/Ethernet controllers |
| ATECC608B driven through SPI | Selected breakout uses I2C; provisioning and exact variant confirmed |
| Digital ultrasonic echo sampled through ADS1115 | Timed digital capture with voltage-level conversion; raw piezo requires an AFE/driver design |
| Radar said to ship M12 / USB-C | AWR1843BOOST EVM uses vendor J3 CAN, micro USB and 5 V barrel; add qualified adapter/harness |
| HAP claimed Gigabit/12 V PoE | Select HAP TX 100BASE-TX; vendor 9–18 V power separately; T1 interface differs |
| Ultrasonic face hidden behind radome | Separate acoustic apertures and tested radar/optical windows |
| Under-20-W host and 1-A input protection | 71.5 W simultaneous output sizing envelope; 79.44 W at 90% efficiency; 99.31 W with 25% margin; 100 W reference capacity |
| Two relays asserted “always safe” | Require end-to-end polarity, feedback, welded-contact/driver faults and common-cause analysis |

Capacity is not measured average power. Do not inflate train OPEX from a 100 W converter nameplate or retain a 40 W allowance as if it covers the updated candidate assembly. Production sensor and firmware selection must provide a measured duty cycle for the auxiliary energy/thermal model. Exact wire gauge, fuse, supply voltage range, bus topology, PCB layout, heat spreader and relay remain design-owned.

Primary specifications checked 3 October 2026: [Mean Well](https://www.meanwell.com/Upload/PDF/HDR-60/HDR-60-SPEC.PDF), [TI voltage detector](https://www.ti.com/product/TPS3701), [TI radar](https://www.ti.com/lit/ug/spruim4b/spruim4b.pdf), [Livox](https://www.livoxtech.com/hap/specs), [Raspberry Pi carrier](https://www.raspberrypi.com/documentation/computers/compute-module.html), [Pico 2](https://datasheets.raspberrypi.com/pico/pico-2-datasheet.pdf), [Microchip secure element](https://www.microchip.com/en-us/product/ATECC608B). Candidate lifecycle/price and rail suitability are not implied by a working datasheet link.

## Software and hardware integration work

The component register verifies all 60 Rust workspace packages against `deployment/components.toml`. Existing control, diagnostics, AFC, CBM, station, supervision and identity software is retained. RFC0033 TACS runtime/resource control remains a process reference; it is not installed Baghdad protection equipment. A logical redundant process cannot substitute for independent power, I/O, sensing and qualified timing.

| Work package | Required binding / acceptance |
|---|---|
| Device HAL | Board-revision ADC/timer/PIO, external CAN/Ethernet, GPIO defaults, watchdog and relay feedback; mock tests plus actual bench traces |
| Sensor ingress | Vendor framing, calibration, timestamps/sequence/CRC, data age, malformed frames, packet loss and common sensor faults |
| Protection output | Complete boot/reset/timeout/permission truth table and hardware watchdog inhibition; braking and traction supplier interfaces |
| Runtime deployment | Qualified host composition, task/WCET budgets, fault containment, resource authority, committed resource state and degraded recovery |
| Clock/network | Actual timestamp accuracy, redundant routes/switches, PTP loss, CAN termination, bandwidth and shared-path failure analysis |
| Target images | Reproducible signed build, configuration/board hash, driver versions, SBOM, secure boot/update/rollback and release evidence |
| Operations integration | Event provenance, CBM/Issue triage, maintenance states, trusted operator decisions and reporting; ERP/FUXA remain outside the safety authority |
| Ticketing/revenue | Actual validators/payment/acquirer contracts, offline/replay/refund behaviour, Arabic UX, tariff versions and daily settlement reconciliation |
| Cybersecurity/service | Key provisioning/revocation, account/role access, logs/storage limits, patch ownership and restore drills |

The image cookbook explicitly records that production SD images are absent. Leave that fact visible. Add real driver/board work against each package and evidence gate; do not create empty drivers or announce “complete onboard firmware” from successful host-library tests. Hardware-in-loop must test a full protected output path using representative I/O and faults.

## ERP recheck and detail handover

The city component compiler, city configuration validator and supervision asset validator pass for all **266 cities**; supervision covers **249,114 equipment records**. This proves reusable planning/asset contracts. Baghdad's enabled reusable profile currently contains the induction training programme; it does not automatically create production, purchasing, quality or maintenance documents.

The local ERP MariaDB service was repeatedly failing on 3 October 2026 because it could not create temporary InnoDB files under `/tmp`. The compose definition now gives the database a writable, bounded 512 MiB temporary filesystem with mode 1777. The database was recreated against its existing persistent volume; it became healthy and the ERP ping API returned HTTP 200. No city assets, Work Orders, stock movements or loan records were fabricated during this repair. Health does not replace backup/restore or load testing.

| ERP handover | Existing capability | Inputs needed to activate the detailed package |
|---|---|---|
| Engineering parts / Item / BOM | Native Items, nested BOMs and version exposure/disposition | Exact family part/revision, UOM, make/buy, supplier alternatives, child content and approved production BOM |
| Production | Draft Work Orders and native execution/Job Cards | Approved BOM, city source/WIP/FG warehouses, workstations, routing, actual hours, dated capacity and operator permissions |
| Procurement / stock | Project material requests, purchasing, receipts, replenishment | Landed freight/duty/tax, lead time, MOQ, safety stock, serial/batch and warehouse availability; no invented stock |
| Quality | Draft native Quality Inspections and evidence references | Released characteristics, sampling and limits, gauges/calibration, inspector, receipt line and retained actual results |
| Maintenance / CBM | Asset Maintenance, Issue-driven repair preview and controlled draft repair | Commissioned serial asset, approved interval/team/date, spares and handback acceptance |
| Training | Reusable programme and native events | Competence criteria, assessor, actual attendance and role authorisation |
| Finance | Native currency/accounting and project budgets; proposal cashflow remains a separate planning model | Iraqi legal company, fiscal year, IQD chart/accounts, USD-import clearing, actual bank/loan/bond terms, treasury schedule and approvals |
| Lifecycle | Version/evidence/disposition and physical identity templates | Real HTTPS resolver, physical serial binding and verified evidence before printable deployment labels |

Use the 69 engineering rows as **reference requirements** first. They are not automatically posted as live ERP Items or added to existing priced city materials; complete assemblies and their child content need a nested MBOM to avoid double counting. The generic ERP manufacturing/quality/maintenance contracts should remain disabled until actual approved inputs exist.

For Baghdad finance, keep the previously selected government share 25%, imported component cash/Chinese-credit split 50/50 and all other cash/debt/bonds in IQD. Confirm company currency IQD, actual FX conversion dates and USD exposures when live treasury accounting is configured. Imported procurement is not automatically all Chinese-origin credit-eligible; rails, fastening hardware, safety electronics and tooling need actual origin/loan-eligibility schedules. Foreign climate money is not IQD financing unless an on-lender or a priced hedge provides that currency structure.

## Cost and release reconciliation

This detail stage does **not** add a second plant, national financing, a new capital total or fictional savings. Existing civil and vehicle allowances already contain planning permanent-way and equipment scope; the added breakdowns clarify what a complete package must contain. Unknown detailed unit costs remain null/open, not zero or a claim that all omissions are covered. The depot, civil manufacturing line, full control-electronics integration, spares, qualification and measured auxiliary duty need RFQs and scope reconciliation before the current financing model becomes a tender-grade model.

For each priced assembly, mark child lines as included, separately payable or excluded; bind quantities, installed rates and origin to one revision. Compare the detail subtotal with its current allowance, update CAPEX/import split/EPC only for an accepted scope delta, then regenerate the Baghdad cashflow, tranche and debt sweep outputs together. A prototype/localisation plan must not be treated as an agreed Chinese loan, grant or bond subscription.

Release sequence: surveyed alignment/ground/utility zones to family and track interface freeze to priced complete BOM/MBOM to local manufacturing trials to hardware/software integration and fault tests to independent review to approved construction/production documents to field acceptance. This makes missing components actionable without marking them as manufactured or qualified.
