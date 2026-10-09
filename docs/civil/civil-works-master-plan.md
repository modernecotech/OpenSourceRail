# Civil works master plan

Revision basis: 8 October 2026. Detailed construction planning and method-development package; project drawings, temporary works, permits, prices and site acceptance remain required before execution.

This plan connects viaducts, stations, ground-supported railway, special crossings, depots, energy sites, utilities, drainage, access and reinstatement. Use **25 m average span** for strategic production and logistics sizing. Purchase and erect against the identified span schedule: shorter catalogue bays, station transitions and separately designed closures retain their own geometry. Do not replace that schedule with rounded kilometres multiplied by a standard beam count.

The [generated Baghdad civil works package](../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/civil-works/README.md) reconciles the current alignment, running-span register, station topology and depot scope. It provides line quantities, workfront and station registers, production/logistics sensitivities, package dependencies, inspection gates and source locks. Run [the civil planning compiler](../../tools/automation/civil-works-plan.py) after a controlled alignment or method revision; `--check` rejects stale outputs. Other cities can apply the methods after substituting their own identified assets and local evidence.

## Package structure and responsibilities

| Package | Accountable role | Controlled outputs and handover |
|---|---|---|
| CW-01 surveys, land and utilities | survey/consents lead | Survey control, corridor boundaries, utility trial-hole register, property/access permissions, verified site model |
| CW-02 enabling and temporary works | construction manager and temporary-works coordinator | Worksite/traffic layouts, haul roads, platforms, drainage, hoardings, design/check register, permits to load/use/dismantle |
| CW-03 foundations and ground treatment | geotechnical authority | Zone design, support schedule, tested method, actual installed lengths, verification and settlement records |
| CW-04 viaduct substructure | bridge construction lead | Columns, caps, abutments, bearing seats, dimensional/strength records and released support packets |
| CW-05 precast production and delivery | precast/logistics manager | Existing-facility audits, shop drawings, accepted serialized components, load/route plans and receiving records |
| CW-06 viaduct erection and completion | appointed lift planner and bridge lead | Configured plant, erection stages, temporary restraints, connections, waterproofing, barriers, drainage and structural handover |
| CW-07 station civil and access | station construction lead | Structure, platforms, shafts, stairs, concourse, roofs, street routes, equipment interfaces and public access acceptance |
| CW-08 at-grade track and approaches | track/earthworks lead | Released formation, treatment, retained approaches, slab/panel zones, crossings, track geometry and drainage |
| CW-09 special crossings and closures | special-structures authority | Site-specific bridge/closure design, access and erection study, water/road interfaces, independent check |
| CW-10 drainage and flood protection | drainage authority | Catchments, receiving outfalls, attenuation, cross drainage, scour/flood controls, clean/test records |
| CW-11 depot and stabling civil | depot design/construction lead | Surveyed yard, buildings, pits, pavements, tracks, charging foundations, workshop and fire/access interfaces |
| CW-12 energy and railway systems civil | systems interface manager | Ducts, foundations, equipment rooms, earthing interfaces, fire separation, pull/test and systems handover |
| CW-13 roads, public realm and reinstatement | urban works lead | Permanent traffic arrangements, accessible paths, road/utility restoration and local handback |
| CW-14 integrated acceptance | owner handover manager | Asset/as-built records, outstanding defect controls, independent acceptance and line-opening packet |

Roles are proposed responsibilities, not appointments. The owner appoints designers, principal delivery leadership, independent checking and local approving bodies before corresponding releases. A contractor programme cannot grant its own independent acceptance.

## Scope and 25 m average-span basis

After removing the 40 m ring spur, the retained Baghdad design has 478.9724 route-km: 183.4095 at grade, 264.6807 elevated and 30.8822 bridge/water-crossing. Running elevated intervals cover 217.9053 km; the remaining 46.7754 km of elevated station/transition scope requires station and interface design. These are distinct chainage scopes. Special bridge class is additional to the unresolved short closures in running elevated intervals.

The identified running layout contains 8,499 catalogue bays (7,749 Pi25 and 750 Pi20), 16,998 catalogue single-track beams and 376 separately designed spans. Its total 8,875 running spans average approximately 24.55 m. There are 9,424 proposed running support chainage records across 549 disconnected runs. The integrated line-based plan resolves the closed-ring start/end alias into one physical support packet; its candidate foundation count does not adopt a field quantity or cost saving. Support sharing, run boundaries and specials prevent deriving foundations simply as total bays plus one. Proposed chainage positions still need survey, utilities, ground and structural release.

For a **reference uninterrupted kilometre**, 25 m means 40 double-track bays and 80 single-track full-span beams. Count 41 support positions only for that isolated kilometre; adjoining sections share boundaries. Four-span structural-continuity units and simple-span link slabs require different bearing counts and stage designs. Neither a 25 m average nor a reference-kilometre count establishes a foundation, pile length or released beam order.

The station scope includes 186 stations, 238 physical platforms and 411 boarding faces. There are 136 elevated and 50 at-grade station layouts, with 314 each of lifts, shafts, stairs and escalators. Layout counts do not size platform foundations, fire stairs, concourse structures or accessible street routes. Each station gets an individual work package and interface review.

## Programme logic and working calendar

Use the [programme and workface controls](civil-programme-and-controls.md) with [viaduct](viaduct-construction-method.md), [station](station-construction-method.md), [other civil works](other-civil-works-methods.md), [logistics](construction-logistics-plan.md), and [inspection/handover](civil-inspection-and-handover.md) methods.

Start with two candidate erection fronts per line and an eighteen-machine study pool, subject to independently feasible released fronts. Expanded inventories queue later fronts behind the previous assignment of each physical machine, including transport/recommissioning gates. Foundation and substructure crews work ahead; precast stock is accepted before dispatch. Station structures and specials are parallel critical-path packages with explicit crossing/relocation interfaces. When radial fronts finish, evaluate additional ring fronts before moving machines to another city. Extra launchers help only when access, foundations, accepted stock, deliveries, crews and temporary works support them.

The resource envelope uses a proposed six-day erection week, an eight-hour shift and explicit holiday/maintenance/weather deductions. Production curing uses elapsed time, not an erection working-day counter. Illustrative rates of 0.5, 1.0 and 1.5 accepted bays per launcher-working-day test capacity; none is a measured production commitment. The minimum quantity/rate duration is a lower bound. Full dates require site-specific quantities, calendars, finite resources, release dates and the complete network of predecessors. The existing 811–1,195-day running-bay comparisons remain conditional comparators, not railway-opening dates.

## Existing industry, procurement and commercial plan

Iraq has many existing precast facilities and production expertise. Begin with factory capability and spare-slot audits, adaptable beds/moulds, prestressing/handling equipment, concrete and reinforcement supply, and regional delivery routes. Use the [potential vendor register](../../engineering/industrialisation/vendor-candidates.json) for screening; a listing gives no compatible product, spare capacity or agreement. A dedicated new civil factory is an option only after comparing existing contracted capacity, upgrades, site and transport costs.

Issue configuration-specific packages for Pi20/Pi25, caps/columns, panels/walkways, bearings/expansion joints, lifting equipment, heavy haulage, station modules, drainage, track support and systems foundations. Separate design/IP support, tooling, qualification/first article, repeat supply, freight/permits, installation, commissioning, spares, maintenance and taxes. Require supplier drawings and declared complete mass, CG, lifting/support positions, release strengths, tolerances and traceability. Record rejected items, NCR rework and replacement capacity in delivery planning.

## Cost, payment and opening interfaces

Build the estimate from named packages and measured quantities. Record foundations by actual type/count/length, columns by height, caps by selected type, beams by span ID, station structures by engineered take-off, and earthworks/ground treatment by surveyed volume/area. Include temporary works, access/traffic, factory tooling, spoil disposal, hauling/escorts, storage/handling, crane or launcher mobilisation, testing, utility diversions, special crossings, flood works, systems civil interfaces, overheads, escalation, risk and contingency.

The retained route-km rates and USD 9m launcher purchase allowance are comparator scopes; they are not a complete installed quotation. Credit embedded erection or plant allowances only after reconciling invoice scope. Milestone payments follow accepted releases/deliveries/installation and contractual certification, with retention and final handback separate. Unknown prices remain unknown; no sum of known rows becomes the full adopted CAPEX.

For each line, opening requires accepted running structures, stations, specials/transitions, track, energy, depot/stabling, fleet, testing and approvals. Construction handover includes safe access for following trades; opening additionally needs integrated railway and operating acceptance. The [coupled programme study](../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/coupled-programme/README.md) retains these gates and conditional finance months. No date, revenue or saving is adopted from a running-span finish alone.

## Review and release plan

Review the first representative complete bay, station access/structure package, at-grade treatment/track zone, and depot/energy foundation package before repetition. Check design interfaces, sequencing, working platforms, ground/temporary loads, manufacturing and logistics capacity, tolerance stack-up, traffic/access, rescue arrangements and full installed costs. Feed measured first-cycle durations, rejected quantities and disruption back into the finite-resource programme.

The generated review register distinguishes repository quantity consistency from site approval. It currently flags unresolved survey/structural releases, no qualified supplier or delivery-route capacity, missing station/special take-offs, inconsistent illustrative buffer sizes, and incomplete depot/stabling provision. Close each through a dated configuration-bound record; do not turn an authoring review into independent construction acceptance.

## Reference practice

International guidance supports method development; Iraqi authorities and the project design basis determine adoption. [FHWA prefabricated bridge elements](https://www.fhwa.dot.gov/bridge/prefab/) describes off-site fabrication, transport and site assembly. [FHWA accelerated bridge construction](https://www.fhwa.dot.gov/bridge/abc/index.cfm) treats planning, geotechnical and structural placement choices together. [HSE temporary works guidance](https://www.hse.gov.uk/construction/safetytopics/temporary-works.htm) describes coordination, designs and checking. [HSE lifting-operation planning](https://www.hse.gov.uk/work-equipment-machinery/planning-organising-lifting-operations.htm) supports competent planning and supervision. These references do not supply Baghdad geometry, capacities, acceptance values or permits.
