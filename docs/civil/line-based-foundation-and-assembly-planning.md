# Line-based foundation and viaduct assembly planning

The [integrated Baghdad package](../../engineering/network-planning/baghdad/README.md) is the line-specific implementation of the [civil master plan](civil-works-master-plan.md). Its nine construction plans, support register, bay register, directed launcher fronts, junction packages and stage library share actual line/span/component identities. The [offline viewer](../../engineering/network-planning/baghdad/network-foundation-viewer.html) lets reviewers select a line, zoom to individual supports and inspect the coordinate, adjacent spans, desktop investigation reference and unresolved design values.

## One physical support, one foundation packet

Every unique running support has one `FND:<support-id>` record, a proposed route-interpolated position, line chainage and the adjoining bay IDs. Adjacent bays reference that packet; they do not create two footings at the same support. Geographic positions remain planning datums requiring survey control, utilities and property/access release. Coincident positions on different lines enter a common junction/site review; a shared foundation is never assumed merely from XY coincidence.

Station/concourse/shaft, approach, water bridge, depot/pit and energy-site foundations are separate design scopes in [the other-structure register](../../engineering/network-planning/baghdad/other-structure-foundation-scopes.json). Their counts and geometry remain unknown where no structural/site design exists. Reconcile station/running support ownership before adding quantities; do not price both as independent foundations for the same load path.

## Ground investigation and design brief

The support packet links its nearest same-line desktop-soil sample by chainage, including the offset and investigation flags. Those mapped topsoil properties do not establish deep stratigraphy, bearing capacity, groundwater, settlement or pile length. Use them to organise field investigation, not to select a footing.

| Design task | Required support/zone evidence |
|---|---|
| Survey and existing assets | Surveyed support/track coordinates and elevations, utilities/trial holes, property, adjacent buildings and traffic/access |
| Ground and groundwater | Borehole/CPT/test-pit programme, verified stratigraphy, groundwater and laboratory classification/strength/compressibility/durability; zone limits and uncertainty |
| Load transfer | Selected beam/continuity scheme, columns/caps/bearings, full train and lateral/dynamic actions, launcher/delivery/asymmetric stages, wind/seismic/collision/flood/scour |
| Foundation options | Shallow footing where verified competent ground permits; bored shaft for suitable constrained/vibration conditions; driven bent where installation is acceptable; pile group for selected lateral/scour/ground cases |
| Geometry and verification | Actual element count/size/depth, socket/cap/column details, settlement/rotation limits, installation and proof/integrity/load testing, independent checking |
| Construction interface | Working platform/excavation/dewatering/slurry/spoil method, reinforcement/connection, concrete/curing, tolerance/inspection and support-ready release |

The register reports an **unqualified simple-span beam-deadload screen** from complete-member study masses: two single-track beams per bay, half of each at each end. It excludes cap/column, train, continuity redistribution, construction combinations and lateral/environmental actions. It is not an adopted foundation axial load or allowable bearing pressure; complete design axial/lateral/moment values remain unknown. Special-member mass also remains unknown.

Prepare a foundation design and installation method for each verified ground/load zone. Trial and test representative foundations before repetition, with a reviewed extension to unlike zones. Select concrete, reinforcement, corrosion/durability and test criteria through the project design basis. Actual lengths, drilling/driving logs, concrete volumes, specimens/maturity, integrity/load tests, dimensions and NCRs become installed records. No universal six-metre pile or generic foundation-concrete allowance is used.

## Directed workfront plan

Two initial launcher fronts per line are inherited from the running-bay sensitivity. Positive fronts install toward increasing chainage; negative fronts begin at the high-chainage end and install backward. The existing scheduler interprets direction internally; the new exports make the execution and dispatch order explicit. All identified catalogue spans are assigned to one front and one sequence position. Special spans retain a separately engineered package and create no ordinary Pi25 order.

For each front, release actual access/assembly space, working platforms, configured machinery, delivery route, competent rested crew and the first consecutive ready supports. Maintain 10–15 accepted bays of support and beam readiness only where continuous run and storage capacity permit. Factory slots, inspection, accepted stock, trailers, receiving plant and installation appointments follow the directed SKU/component order. Shared equipment/crews cannot be reserved to two fronts simultaneously.

Disconnected intervals, stations and specials require a checked passage or dismantle/transport/reassembly/recommission method. The predecessor is the previous executed bay, not simply the preceding ascending row in a database. Foundations used by adjoining bays share the same stage packet. Released radial launchers can transfer to additional ring fronts only after access, foundations, supply, crews and recommissioning are evaluated together.

## Assembly-stage dependencies

| Stage | Entry and exit |
|---|---|
| F0–F3 foundation | Survey/utility/ground/load design → trial and temporary-platform release → actual selected installation → accepted tests/dimensions/NCR closure |
| P0–B0 support | Column/cap and connection/temporary restraint → surveyed bearing seats and actual next-stage loading release |
| M0–M3 manufacturing | Frozen shop/handling configuration → mould/cage/prestress/cast/curing → separate strength gates and inspection → accepted serialized member |
| H0–H1 delivery | Actual vehicle/route/load restraint and appointment → receiving/damage survey, designed storage and reservation |
| E0 preparation | Both support B0 packets, both beam H1 records, predecessor/relocation and relevant junction J2 release |
| E1 first beam | Configured controlled lift, seating, balance and required lateral/torsional restraint |
| E2 paired bay | Second controlled lift, securing, surveyed geometry and bearing contact |
| E3 connections | Selected connection/joint/strength, bearing movement and NCR acceptance; no shared bearing reduction without structural continuity |
| E4 advance | Accepted current-stage path, checked advance/delivery loads, next supports, weather and protected access |
| E5 following trades | Walkway/barrier, waterproofing/drainage, track interface, permitted loads/access and signed handover |

The [stage library](../../engineering/network-planning/baghdad/assembly-stage-library.json) stores these reusable chains; the [bay register](../../engineering/network-planning/baghdad/span-assembly-register.csv.gz) binds them to actual component and parent IDs. Junction-affected member orders remain on design hold until level/clearance/support/stage releases close. Installation is never inferred from an accepted factory beam or a completed documentary task.

## Inspection and complete opening

Apply the [site ITP and handover plan](civil-inspection-and-handover.md). Record source configuration, personnel/equipment authority, measured results, test criteria and signatures before closing each hold. After transport damage, abnormal loading, changed temporary works, utilities or adverse weather, inspect and re-release affected stages.

Complete line opening requires stations, specials/transitions, track, energy, depot/stabling, commissioned fleet, integrated testing and approvals in addition to running-bay completion. The plan does not adopt an opening date, field foundation quantity, installed quote or paid-passenger uplift from illustrative capacity or coverage.
