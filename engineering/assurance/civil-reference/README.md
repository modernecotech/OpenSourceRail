# Civil reference demonstration A

**Status: awaiting site design, physical evidence and independent review. Release is blocked.**

The reference contains 4 beam assets with 20/25 m spans and 20 m of adjoining at-grade transition. It provides quantities, connection briefs, construction hold points, option comparisons and a connected civil FMEA. It is a review package for engineers and suppliers; it has no accepted construction drawings.

## Layout and quantities

| Asset | Family | Chainage (m) | Supports |
|---|---|---:|---|
| PI20-T1 | Pi20 | 0–20 | SUP-00, SUP-20 |
| PI20-T2 | Pi20 | 0–20 | SUP-00, SUP-20 |
| PI25-T1 | Pi25 | 20–45 | SUP-20, SUP-45 |
| PI25-T2 | Pi25 | 20–45 | SUP-20, SUP-45 |
| TRANS-01 | trackform-comparison-required | 45–65 | SUP-45, SUP-65 |
| TRANS-02 | trackform-comparison-required | 45–65 | SUP-45, SUP-65 |

4 bare beams contain **107.91 m³** of envelope concrete over **261.0 m²** of deck. Foundation, reinforcement, prestress and installed cost quantities remain unresolved. 3 elevated support lines are identified. The candidate arrangement has 16 bearing seats; capacities and fixity are unresolved.

## Mass and lifting

| Family | Bare mass (kg) | Margin under 75 t (kg) | Complete lift |
|---|---:|---:|---|
| Pi20 | 59,950.0 | 15,050.0 | blocked-incomplete-mass-or-lift |
| Pi25 | 74,937.5 | 62.5 | blocked-incomplete-mass-or-lift |

Net diaphragms, bulk-density reinforcement adjustment, prestress steel, anchorages, embedded lifting hardware, attachments, retained temporary works, slings, spreader and hook/block masses must be measured or substantiated. The overlapping CAD diaphragm zones cannot be summed as additional fabrication concrete. The actual crane/launcher chart, configuration, radius, dynamic allowance, utilisation, centre of gravity, ground support and lateral stability must be reviewed.

## Foundation and trackform comparison

Candidate foundations: bored-shaft, pile-group. None is selected. A measured comparison must cover axial/lateral resistance, total and differential settlement, groundwater, chemistry, liquefaction/scour where relevant, utilities and installation constraints. Calcium-based treatment needs reviewed chemistry compatibility. Reinforced-soil approaches need railway deformation, stability and scour justification.

Ballasted track, slipformed slab and precast panels remain explicit alternatives. Compare settlement, drainage, local material and maintenance capability, repair possessions and whole-life cost for the layout-defined transition before selection.

## Conventional girder comparator

Locally manufactured prestressed I-girders with a separate railway deck is retained for the 20/25 m span families. Supplier section, girder count, deck quantities and price are pending; no system is declared cheapest.

- moulds and prestress beds.
- reinforcement/end zones and transfer strength.
- girder/deck quantities and foundation reactions.
- transport and number/weight of lifts.
- temporary bracing and deck erection.
- railway deck and connection compatibility.
- bearings, jacking and replacement access.
- inspection and maintenance.
- installed time and cost.
- whole-life cost and uncertainty.

Use equivalent railway actions, geometry and service-life assumptions for both systems. Record initial capital, construction possessions, inspection, cleaning, bearing/track replacement, discount rate and uncertainty before calculating whole-life net present cost.

## Controlled connection briefs

Numerical loads, tolerances, resistance and movement limits are pending for every connection. Each requires an engineered drawing, first-article qualification and independent review.

### C-01 — Pier to foundation

Loads: axial, moment, shear, seismic cyclic demand.

Install: Survey starter bars/socket; trial fit; brace; grout/cure before loading.

Inspect: Survey alignment; reinforcement/coupler record; grout strength and fill evidence.

Repair/replacement: Engineer-designed local repair or replacement; retain access.

### C-02 — Cap to column

Loads: vertical reactions, torsion, transverse loads and seismic.

Install: Brace cap; verify interface; complete continuity/grout; strength hold point.

Inspect: Joint dimensions, engagement and void checks; as-built survey.

Repair/replacement: Accessible repair ports and approved temporary support.

### C-03 — Girder bearings and restraints

Loads: vertical uplift, braking, lateral, thermal, seismic and derailment.

Install: Survey seats; set orientation and movement datum; place beam; engage restraints.

Inspect: Seat levels, bearing rotation/contact, travel, fixity and restraint witness.

Repair/replacement: Isolate traffic; use reviewed jacking seats; replace bearing and resurvey.

### C-04 — Walkway and containment attachments

Loads: egress crowd, containment impact and fatigue.

Install: Cast inserts; gauge fit; install panels and barriers with movement allowance.

Inspect: Anchor engagement/proof evidence, gaps, containment continuity and access.

Repair/replacement: Remove replaceable panels and bolts from protected work area.

### C-05 — Track plinth and fastener anchors

Loads: vertical axle, lateral, braking, fatigue and rail interaction.

Install: Survey rail seats; qualify anchor/grout system; fit and gauge fasteners.

Inspect: Gauge, level, pull-out qualification, torque and electrical insulation.

Repair/replacement: Exchange fasteners or local plinth repair with track possession.

### C-06 — Drainage and utility crossings

Loads: water pressure, utility weight, thermal movement and accidental loads.

Install: Set falls and movement loops; separate utilities; seal joints; commission drainage.

Inspect: Survey falls; leak/flow and blockage-access checks; utility clearance.

Repair/replacement: Accessible clean-outs and replaceable flexible connections.

### C-07 — Jacking and bearing replacement

Loads: jacking reactions, temporary redistribution, lateral stability.

Install: Approve possession/supports; install synchronised monitored jacks at designed seats.

Inspect: Jack calibration, seat capacity, lift limits and stable temporary load path.

Repair/replacement: Replace bearing; controlled lowering; movement datum and track survey.

## Construction sequence and hold points

| Stage | Activity | Hold point |
|---|---|---|
| ST-01 | Freeze layout, railway loads and surveyed ground/drainage basis | Independent reviewed design and safe working constraints |
| ST-02 | Compare foundations and ground treatment; install/test supports ahead of erection | Measured load tests, settlement and chemistry compatibility; released temporary works |
| ST-03 | Fabricate beams and connection mock-ups | Reviewed reinforcement/prestress, transfer strength, mass and lifting hardware records |
| ST-04 | Survey bearing seats and install bearings/restraints | Seat levels, orientation, capacities and movement datum accepted |
| ST-05 | Transport and lift first beam; brace before releasing rigging | Reviewed actual lift configuration, stability and equipment support; witness first article |
| ST-06 | Erect paired beam and finish connections, walkway and containment | Connection strength/fill, engagement, survey and temporary support release |
| ST-07 | Construct approach/trackform, catchment and drainage interfaces | Settlement/drainage/scour criteria and blockage access checks |
| ST-08 | Commission, inspect and establish maintenance access | Geometry, drainage scenarios, jacking/replacement rehearsal; independent and authority acceptance |

## Calculations and drainage demonstration

[Native model/result files](calculations/) preserve the reproducible elastic calculation and drainage replay. The beam comparison uses E = 30 GPa, bulk-envelope self-weight, an illustrative 20 kN/m additional service load and endpoint supports. OpenSees uses the Pi-section area/inertia; CalculiX uses an equal-area/inertia rectangular surrogate. Prestress, reinforcement, torsion, fatigue, derailment, seismic response, actual lift support positions and rail interaction are unresolved.

The elastic hand check is 5wL⁴/(384EI). This checks software and units; its deflections are not accepted railway limits.

| Span / stage | Hand deflection (mm) | OpenSees (mm) | CalculiX (mm) |
|---|---:|---:|---:|
| 20 m / construction | 14.280 | 14.280 | 14.363 |
| 20 m / service | 23.993 | 23.993 | 24.132 |
| 25 m / construction | 34.864 | 34.864 | 34.980 |
| 25 m / service | 58.576 | 58.576 | 58.772 |

The synthetic drainage system uses a 1 ha catchment, a 50 m conduit and a storm independent of any site. The blockage sensitivity reduces the 0.5 m conduit to 0.1 m; the backwater sensitivity fixes tailwater at 1.5 m. Reviewed project blockage/debris and flood boundaries may require different cases.

- backwater: routing continuity error 0%; 6 hydraulic limit exceedances in the illustrative screen.
- blocked-drain: routing continuity error 0%; 1 hydraulic limit exceedances in the illustrative screen.
- normal: routing continuity error 0%; 0 hydraulic limit exceedances in the illustrative screen.

Adequate continuity does not establish adequate drainage. Flooding volume, surcharge duration, peak head, conduit depth and outfall flow are checked using engine statistics across every routing step. Culvert debris, outfall consent, erosion/scour, flood pathways and cleaning access need site design. Consider ANUGA when 2D surface overflow changes the risk.

## Connected civil FMEA

| ID / stage | Failure chain | Controls and evidence |
|---|---|---|
| CF-01 / service | blocked drain → saturated formation → foundation movement → bearing displacement → track geometry deterioration → operating restriction | Accessible drains; redundant route where justified; geometry monitoring and intervention. Evidence: Blockage/backwater replay, cleaning trial, settlement model and geometry intervention review. **Open**. |
| CF-02 / construction | eccentric lifting → girder roll or lateral instability → dropped member or collapse | Reviewed sling geometry, centre of gravity, temporary bracing and exclusion zone. Evidence: Weighed member, lift chart/radius, stability calculation and witnessed first lift. **Open**. |
| CF-03 / construction | wrong orientation or level → restraint or loss of bearing contact → unexpected forces or support loss | Surveyed seats and movement/fixity datum; witness installation. Evidence: Bearing schedule, seat survey and installation inspection. **Open**. |
| CF-04 / construction | voids or incomplete engagement → connection resistance loss → progressive cracking or collapse | Qualified grouting procedure, mock-up, fill witness and strength hold. Evidence: Batch/strength records, void/engagement inspection and connection qualification. **Open**. |
| CF-05 / construction | early prestress transfer → anchorage/end-zone cracking → loss of prestress or handling failure | No transfer or handling before reviewed measured strength. Evidence: Specimen maturity/strength, transfer procedure and end-zone inspection. **Open**. |
| CF-06 / construction | weak support or excessive ground pressure → support settlement/overturning → equipment and member collapse | Ground investigation, outrigger/launcher foundation and temporary works review. Evidence: Support loadcase, bearing/settlement calculations, survey and trial load. **Open**. |
| CF-07 / service | outfall erosion or transition stiffness change → differential movement → track geometry deterioration → operating restriction or derailment hazard | Scour protection, graded stiffness and drainage access. Evidence: Flood/scour assessment, transition settlement model and inspection trigger. **Open**. |

The shared schema allocates the coupled drainage chain to these planned assets and responsibilities:

| Failure / asset | Owner | Calculation or observation | Required response |
|---|---|---|---|
| CF-01 / DRAIN-01 | Drainage maintainer | engineering/assurance/civil-reference/calculations/drainage-sanity.json | Clean/inspect drain and invoke reviewed adverse-rain response |
| CF-01-BEARING / BEARING-20 | Bridge maintainer/structural engineer | bearing inspection and rail-structure movement calculation required | Inspect bearing travel/fixity and review jacking/repair plan |
| CF-01-FOUNDATION / FOUND-20 | Structural/geotechnical engineers | site support survey and geotechnical movement calculation required | Survey support position; impose reviewed movement intervention |
| CF-01-OPERATION / CIVIL-SYSTEM | Operator/control centre | controlled operator decision and effectiveness check required | Apply restriction or stop service pending engineering handback |
| CF-01-SATURATION / FORMATION-45 | Geotechnical engineer | site groundwater/formation observation and coupled settlement calculation required | Inspect groundwater and formation; reassess settlement model |
| CF-01-TRACK / TRACK-20 | Track engineer | track geometry observation and adopted railway limit calculation required | Measure geometry; compare approved limits; request restriction |

The physical hierarchy connects parts to subassemblies, the reference bay and the civil system. Foundation–bearing–track interfaces and the saturation common cause are explicit. Planned member occurrences link concrete mix revision, constituent batches, curing, transfer/lifting strength, test records and nonconformances to the member. The planned drainage inspection links its work order, model reassessment, effectiveness check and engineering handback to the same failure chain. These templates contain no manufactured members, measured strengths or completed maintenance.

[Machine-readable report](report.json) contains the typed graph and drain-change trace. It uses the existing connected-assurance traversal, including both old and new relationships. The civil assembly is validated through the same configuration, ownership, effect, mitigation, evidence and decision schema as the component example. A drain change reaches formation, foundation, bearing and track failures, required operator response and blocked civil gates. All physical and independent evidence remains missing.

## Unresolved site inputs

- Adopted railway standards and code editions.
- Survey/alignment, curvature, skew and rail movement datum.
- Railway service, derailment, fatigue, wind and seismic actions.
- Boreholes, groundwater, axial/lateral soil response and settlement.
- Sulfate/chloride exposure where present and treatment compatibility trials.
- Liquefaction, flood levels, scour and surface flood pathways where relevant.
- Supplier reinforcement/prestress, end zones, transfer/handling strengths and mould/bed limits.
- Measured net detail masses, centre of gravity, transport axle loads and route clearances.
- Lifting chart/configuration/radius, rigging, temporary stability and support-ground capacity.
- Accepted rainfall/storm ensemble, catchments, culvert sizing and outfall consent/tailwater.
- Connection tolerances, loads, movement and inspection acceptance values.
- Supplier-installed cost/time, service life, maintenance capability and discount basis.
- Independent check, physical first article evidence and signed authority release.

## Public references and reuse rights

No external drawing or code was copied into this package. Record drawing-specific rights before incorporation; software licences do not grant rights to unrelated drawings.

| Reference | Intended use | Rights/access status |
|---|---|---|
| [FHWA-PBES](https://www.fhwa.dot.gov/bridge/prefab/if09010/) | Prefabrication, connections, tolerances and erection practice; highway examples need railway adaptation | Reference only; individual drawing/third-party reuse rights not established; page reviewed |
| [WSDOT-DRAWINGS](https://wsdot.wa.gov/engineering-standards/design-topics/superstructure-design-bridges-structures) | Conventional bridge detail benchmark | Reference only; drawing reuse permission pending; 403 on review; obtain controlled drawing set |
| [PGSUPER](https://github.com/WSDOT/PGSuper/blob/master/License.txt) | Conventional prestressed girder comparison; agency/highway assumptions need railway adaptation | Alternate Route Open Source License 1.1; no code incorporated; license reviewed; application not executed |
| [RDSO](https://rdso.indianrailways.gov.in/view_section.jsp?id=0%2C2%2C466%2C603&lang=0) | Railway bridge arrangement and detail references | Reference only; drawing access and reuse permission pending; portal unavailable on review; obtain applicable set |
| [XC](https://github.com/xcfem/xc) | Candidate additional structural check after validating one model | No code incorporated; check pinned license before adoption; repository reference only; not integrated |
| [SWMM](https://github.com/USEPA/Stormwater-Management-Model) | Drainage network simulation | Existing tool integration; no external drawing incorporated; repository/API reviewed; existing solver executed |
| [ANUGA](https://github.com/GeoscienceAustralia/anuga_core) | Optional 2D surface flood assessment when overflow pathways matter | No code incorporated; check pinned license before adoption; repository reviewed; not required or executed |
| [FHWA-GROUND](https://www.fhwa.dot.gov/engineering/geotech/pubs/nhi16072.pdf) | Investigate soil chemistry before calcium-based ground treatment | Reference only; no extracts or drawings copied; primary reference supplied; site testing required |
| [FHWA-GRS](https://www.fhwa.dot.gov/publications/research/infrastructure/structures/11026/004.cfm) | Candidate reinforced-soil approaches; railway deformation, stability and scour review required | Reference only; no drawings copied; primary reference supplied; not a selected design |

## Reproduction

From the repository root:

```bash
.venv/bin/python tools/automation/civil_reference.py --run-solvers
.venv/bin/python tools/automation/civil_reference.py --check
.venv/bin/python tools/automation/civil_reference.py --verify-native-replay
```

OpenSeesPy, PySWMM and native `ccx` are needed for replay. The default compiler and `--check` validate recorded files and provenance without running native solvers. The release gates require a separately reviewed, design-hash-bound asset register, per-asset numerical outputs and accepted limits. This concept register is deliberately pending and cannot satisfy them.
