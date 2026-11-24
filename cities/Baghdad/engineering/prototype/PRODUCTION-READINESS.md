# Baghdad Airport production preparation and v0.8 decision

**Decision on 23 November 2026: hold v0.8.** The six packages below document earlier first-article preparation and the critical interfaces still to resolve. The representative car still has unlocated equipment, and several moving, load-bearing and electrical interfaces have only nominal dimensions or supplier-proposed limits. Those are release criteria for the production package. The last published software release is [v0.7.2](../../../../docs/releases/v0.7.2/README.md).

For new enquiries, use the [corrected 17.46 km horizontal Airport study](../simulation/ASSUMPTION-AUDIT.md). Export the price scopes for the feeder layout under review. The 30-minute paired6 comparison completes the booked working day in the modelled normal and degraded cases. Site selection, surveyed levels, protection approval and first-article fabrication remain open.

The earlier 12 km, 15-minute schematic retains its drawings, six six-car sets, 54 procurement and comparison lines, and ERPNext edition for reproduction. Its length fails the minimum distance through the mapped stops. Rebind drawings, quantities and prices to the corrected candidate before using them in a new enquiry.

## Tasks and assignments

Two lower-cost Sol workers prepared the vehicle/factory and infrastructure enquiries under an Astra manager. The coordinator integrated the drawings, procurement schedules and ERP edition. The owners in the final column identify the discipline needed for the next decision. A role assignment here records the work required; contact and appointment of external organisations rests with the buyer.

| Package | Completed for quotation | Open task and owner | Completion evidence for the production package |
|---|---|---|---|
| Representative car | Nominee plan and elevation, counted steel and liner takeoff, fitout and mass boundaries, door movement allowances and inspection sequence. [Car arrangement](vehicle-factory/INSTALLED-GA.md) | Vehicle integrator and equipment suppliers to locate and dimension the working fitout, service routes and removal envelopes; structural engineer to complete critical joints. | An installed assembly drawing and matching BOM, a bounded mass and load distribution, controlled interfaces and a reviewed join and inspection plan tied to that revision. |
| Powered bogie | Two frame instances share a jig drawing. Twelve opposed or primary pad locations, axle planes and 22 inspection rows support the proposed exchange and refit. [Body and bogie mating drawing](vehicle-factory/BODY-BOGIE.md). [Bogie and vehicle schedule](vehicle-factory/vehicle-quote.csv) | Running-gear designer and nominated equipment suppliers to specify wheelset, journal, bearing, drive and brake fits, loads, motion limits and withdrawal space. | Coordinated mount and suspension drawings with tolerances, full equipped removal sweep, replaceable parts and independently reviewed fit and load account. |
| Viaduct | A selected 10 m beam has a cage and strand schedule, preliminary bearing footprints, handling reactions, a pier and footing model, and a first-article inspection enquiry. [Beam and foundation schedule](infrastructure/VIADUCT.md) | Civil designer, precaster and lifting engineer to resolve end-zone reinforcement, strand transfer, inserts, bearing restraints, temporary stability and site actions for the applicable foundation family. | Controlled section, bearing and pick details with verified design limits, staged handling and inspection sign-off. Record where the foundation is applicable and the survey needed at each site. |
| Station | A 5 m bay, platform panels, drainage and maintenance access accompany the straight station. On an illustrative 150 m curve the straight-edge offset intersects the nominal body by 62 mm on the inside or 27 mm on the outside. [Platform clearance study](infrastructure/PLATFORM-SWEEP.md). [Station schedule](infrastructure/STATION.md) | Station and accessibility leads to resolve the installed door-to-edge envelope, accessible circulation and evacuation, drains, power isolation and rescue access against the proposed site. | Coordinated station layout and reviewed interface limits for loaded and worn conditions, maintenance access and the intended evacuation arrangements. |
| Power and control module | Candidate-specific single-lines, radial and paired circuits, equipment scopes, connector return and a station-visit bench plan include normal running and fault cases. [Power and controls schedule](infrastructure/ELECTRICAL-CONTROLS.md) | Utility, equipment suppliers and protection engineer to supply source limits, cabinet and connector data, protective-device coordination, heat duty, clearances and maintainable isolation. | Reviewed connector and terminal schedule, replaceable cabinet layout, isolation design and calculation for the specified normal and degraded service. Identify which tests use simulators and which require a representative device. |
| Local production and repair | Five draft pilot orders, quantified vehicle, civil and wayside workcells, QA, repair and ERPNext handoffs, separate supplier returns and overlap credits. [Machine quantities and product routes](FACTORY-SPECIFICATION.md). [Factory route and records](vehicle-factory/factory-routing.md) | Buyer, local workshops and quality lead to complete capacity/tooling returns, site masters, make/buy choices and controlled inspection and handback instructions. | Usable routing and serial-to-installation handoff for the nominated works, including who owns drawings, tools, inspection, nonconformances, repair and release. |

## Taking the factory issue to a workshop

For the earlier schematic, the [cost schedule](SHOP-COSTS.md) prices the 41 machine and service lines using the output and operating periods in the factory register. Use the [machine quotation procedure](PROCUREMENT-PLAN.md) to collect competing returns for the same units. The [CAM handoff](cam/CAM.md) provides DXF profiles, placements, saw patterns and a postprocessed practice exercise. The [yard procedure](infrastructure/YARD-CUTTING.md) converts the beam cage schedule to stock orders and traceable cut bundles. Buyers, operators and inspectors can work through a sample handover in the [offline class](training/index.html).

Before a production order, the nominated workshop must identify the machine and post revision, return delivered prices and capacity, record first-off inspection, and obtain release of the specific interfaces it will build. The instructor records a learner’s practical observation separately from the software exercise. The $347.50 classroom example covers 14 learners in short role exercises. The separate $8,060 shop trial covers seven learners in two four-hour sessions, two first-off shifts and staffed inspection. Budget the scope the operator intends to deliver and credit shared time.

## Integration tasks from the November review

| Work package | Repository evidence and remaining decision |
|---|---|
| Configuration and service | The Airport diagram includes passenger, positioning and terminal movements. The citywide case has fourteen connected main routes with deferred access explicitly identified. At 30-minute intervals the Airport case offers 1,400 places per hour per direction, half the 15-minute offer. On the same 30-site procurement basis, buying five sets gives a $1,113.08m construction estimate and $12.25m central annual operating estimate, compared with $1,124.32m and $13.09m for six sets. Compare both with the Yellow urban survey candidate before choosing an opening. The operator owns demand counts, the transfer survey and timetable adoption. [Opening options](../../OPERATING-ALTERNATIVES.md) · [Citywide service](../../CITYWIDE-SERVICE.md) |
| Controls | The candidate-specific station replay exercises the boarding hold, door locks, effort handover and faults. The bench procedure covers stale signals, wrong-side doors, brake loss, emergency evacuation and blackout restart. A controls lab must provide time-synchronised physical results and independently approved limits. [Station bench](../controls/STATION-BENCH.md) |
| Electric supply | The priced radial system clears the revised hot-case floor by about 0.57 V. The combined adverse case fails. A six-site paired circuit clears that case with a site out, and falls below the floor under concurrent path-pair and site loss. Check the proposed degraded service, grid connection, protection and safe evacuation against utility and equipment returns. [Power and degraded cases](../commissioning/COMMISSIONING.md) |
| Engineering and BOM | The candidate connects stock geometry, moving loads, opening quantities and draft manufacturing orders. The six first-article packages above identify the outstanding installed interfaces. The hybrid-body comparison retains its own engineering assumptions and needs its own installed offer. [Engineering twin and material comparison](README.md) |
| Costs and construction | The buyer can substitute a matching offer, compare local value and examine phased public cash including renewals. Statutory treatment, site works and funding await the buyer and authorities. The pilot ERP comparison uses test suppliers. [Commercial scope and cash](commercial-guide.md) · [Estimate and ERP workflow](PROCUREMENT-PLAN.md) |
| Workbench and performance | A user can edit a city, review a candidate in the Workbench and open the Airport twin offline. The selected checks and compact install avoid a full-catalogue rebuild. The architecture comparison must keep a different city, train or supply model separately identified. [Planning guide](../../../../docs/workbench/planning/README.md) |
| Release verification | Reproduce the technical packet, buyer estimate, car arrangement and integrated issue with the commands below. Check the same revision in a clean installation. The v0.8 decision depends on the six production outputs above. |

## Wider work and its owner

| Further decision | Existing work | Next owner and evidence |
|---|---|---|
| Which corridor should receive the first public investment? | The Airport and Yellow service scenarios compare capacity, service and costs. Yellow has a different survey and feeder scope. | The planning authority needs origin–destination counts, peak loads, journey distances and road-delay observations for a like-for-like passenger-kilometre, subsidy and avoided-congestion comparison. The buyer and lender need actual financing and allocation terms. |
| Where should a physical demonstration run? | A 2 km civil module and the Airport first-article enquiries provide separate planning quantities. | The owner selects a site and demonstration objective. The civil and systems leads then price its actual ground conditions, access, erection, power, controls, trial vehicles and witnesses. Use the [reference module](../../../../docs/reference-v07/civil/README.md) only within its stated scope. |
| How should another city compare supply systems? | New-city outlines use elevated civil works and prefer catenary-free supply. The planning guide links explicitly identified conventional comparisons. | A city seeking a site-specific overhead alternative needs its own train collector, overhead clearances, route, electrical sizing and cost. The 30 km overhead reference has separate site and service assumptions. [City workflow and available comparisons](../../../../docs/workbench/planning/README.md) |
| Which remaining builds are worth optimising? | Current Airport checks reproduce a compact source installation. Historical results keep their source-bound versions. | The release maintainer should profile a repeated city or engineering change, record the recalculated dependencies, elapsed time and peak storage, and target the observed bottleneck. Keep retention or Git-history changes separate from issuing a prototype enquiry. |

## Reproduce and use the enquiry

Run from the repository root with the project Python environment. Generate an enquiry for the corrected candidate and retain the original signed returns against its lot scopes. Use `--layout radial30` with a separate output path to price that comparison. Review the normal and degraded service results for each layout before comparing prices.

```sh
./osr design railway audit --check
./osr design railway audit --packet build/baghdad-airport-paired6-enquiries.zip --layout paired6
```

For historical reproduction, extract the earlier first-article archive and open **START.html**. Its ERPNext edition, drawings and shop exercises remain available for that schematic.

```sh
./osr design railway prototype --check
./osr design railway sourcing --check
python3 cities/Baghdad/engineering/prototype/vehicle-factory/installed_ga.py --check
./osr design railway sourcing --issue build/baghdad-airport-12km-reference.zip
```

The issue manifest identifies every member, the physical candidate, the drawing evaluation and the buyer estimate. The working-file checksums support revision control. A changed fit, circuit, drawing or estimate requires the affected schedules and pack to be reviewed and reissued.

## After production preparation

The engineering owner reviews the critical interfaces before authorising fabrication of a safety-critical article. First-article inspection, calibrated weighing, loaded and hot tests, installation and site commissioning then produce evidence against that exact release. Passenger service also requires the authority's decision, trained staff and an accepted operating system. Neither a price submission nor a software test supplies those approvals.
