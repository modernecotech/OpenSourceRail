# Civil construction logistics plan

The [master plan](civil-works-master-plan.md) uses 25 m average spans for logistics sizing and identified spans for orders. The [generated logistics envelope](../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/civil-works/resource-and-logistics.json) distinguishes assumptions, required capacity, available evidence and adopted capacity. No surveyed delivery route or contracted supplier capacity is currently entered.

## Factory and regional-yard network

Audit existing Iraqi precast facilities and production expertise before selecting expansion or a new factory. For each plant record bed usable length/width, mould positions, prestressing capacity, mix/curing control, cage production, handling/stacking capacity, available shifts, current commitments, inspection staff, power/water, raw-material suppliers, environmental permits and delivery access. Assess Pi20/Pi25, column/cap shells, walkways and ST6 separately; a suitable panel factory is not automatically a prestressed-beam supplier.

Select regional yards by permitted land, road/bridge access, geotechnical bearing/drainage, safe handling, flood risk, distance and delivery restrictions. Separate raw materials, cages/moulds, curing, accepted stock, quarantine, dispatch lanes and returnable gear. Layout access for the longest vehicle, fire/rescue and crane replacement. Design dunnage, restraint and storage stacking; the actual layout determines gross area and maximum stock. A count of beams cannot establish a yard area without supports, spacing and handling aisles.

## Capacity equations and scenario boundaries

| Requirement | Equation and qualification |
|---|---|
| Erection supply | `active launchers × accepted bays/launcher-working-day × 2 beams/bay` |
| Production positions | `ceil(accepted daily beam demand × mould cycle hours / production hours per day / first-pass yield)`; a position casts one complete beam per cycle |
| Weekly balance | `erection working days/week × daily demand`; compare with actual factory/haulage working days, cure time and outages |
| Fresh concrete | Beam-specific accepted count × released cast volume, adjusted for production rejects; foundation/station/other concrete is additional |
| Beam movements | One complete beam per proposed load; verify transporter configuration, axle/bridge capacity, load/support restraint and route permissions |
| Round-trip vehicle cycle | Loading + outward journey + unloading + return + delays/driver breaks; reserve loading/unloading equipment concurrently |
| Trailer requirement | `ceil(required trips/day / executable trips/vehicle/day)`; derive trips from the route's permitted window and complete cycle, then add independently justified resilience |
| Beam buffer | `2 × 10–15 released bays × active fronts`, limited by remaining continuous run, storage capacity and accepted handling/access |
| Ready support buffer | All unique supports for the next 10–15 bays, each released for the planned machine/beam load; endpoint sharing is explicit |

The generated six-day scenarios use illustrative 48-hour production cycles, 24 production-calendar hours/day, 90% first-pass yield, a 12-hour haulage window and an eight-hour complete route cycle (including a declared allowance for return and delays). These are sizing assumptions, not supplier or route evidence. A 12-hour window is not permission for a driver to work without statutory rest. Verified driver/crew calendars further constrain executable trips.

Daily rates also need a compatible erection cycle. The [programme controls](civil-programme-and-controls.md) deduct productivity, handover and maintenance from the proposed single shift; the existing eight-hour serial reference cycle does not support the higher one-shift targets. Resource rows show the cycle that would be required and retain achieved rate as unknown.

At eighteen active launchers and one accepted bay per launcher-working-day, the requirement is 36 accepted beams and 450 equivalent route-metres per erection day. Using the Pi25 complete-member study, beam cargo alone is about 3,078 t/day; trailer tare, rigging and all other materials are additional. Production at 90% yield needs 40 gross beams/day and 80 one-beam mould positions under the illustrative 48-hour/24-hour basis. These are capacity requirements to compare with available audited beds, not a proposal for eighty new moulds or a commitment to supply.

The 10–15-bay buffer requires 360–540 accepted beams across eighteen sufficiently long fronts. Existing conditional route examples use twelve beams per front, equivalent to only six double-track bays. The generated review flags that mismatch. Reconcile buffer policy, site/yard storage and front lengths before assigning a build rate; do not silently claim that six bays meets a ten-bay requirement.

## Route survey and transport release

Create one route record per supplier–yard–front movement, with GIS path and direction, surveyed dimensions, gradients/crossfall, bends/swept path, weak bridge/culvert/pavement limits, overhead utilities, temporary widening, load permits, closures/escorts, delivery windows and alternates. Record the actual vehicle, axle spacing/load distribution, gross mass, loaded height/width/length, ground clearance, cargo CG, support/restraint design and braking/grade constraints. Gross tonnage alone cannot assess a bridge or pavement.

Load using inspected equipment and released beam/support points; verify member ID, mass, release strength, dimensions, restraints and travel documentation. Inspect after loading and at receipt. Use wheel/ground restraints and segregated receiving zones; place on designed storage supports or supply directly to the released erection position. Missing route, equipment or access evidence blocks dispatch even when a beam is accepted.

Release lift, transport and storage separately. The current Pi25 manufactured study is 85.51 t, versus 89.51 t suspended with illustrative gear. Transport gross mass also includes trailer/tractor and carried accessories. Neither the bare 75 t product target nor nominal equipment tonnage clears those loads. The [handling envelope](viaduct-transport-and-erection-envelope.md) and supplier actual configuration govern release.

## Booking, stock and material flow

Allocate each beam to span and track, factory slot, inspection gate, route, receiving yard/front, delivery appointment and installed record. Dispatch in erection sequence, including Pi20 and special interfaces; maintain location/condition and reservations in ERP. Reserve trailers, loading/unloading cranes, competent workers and route/closure slots before commitment. Keep rejected/awaiting-test stock separate from accepted available stock.

Coordinate concrete trucks, reinforcement/cage deliveries, spoil, station modules, lifts/escalators, rail/panels, fuel and systems equipment in the same access calendar. Check opposing flows and shared loading gates. Keep deliveries off pedestrian/emergency routes and avoid unplanned roadside queuing. Provide supplier/driver check-in, receiving inspection, safe standby, washout/spill and emergency procedures.

Record daily opening stock, accepted production, rejects/rework, loaded/dispatched, in transit, received, installed and closing stock by SKU/location. Balance mass and count; no item can be simultaneously available at the factory and workfront. Front saturation or a stopped crane/launcher pauses dispatch. Test loss of a supplier, road closure, trailer breakdown, rejected load, weather stop, buffer overflow and extended curing, with identified safe storage and controlled resequencing.

## Material quantities, spoil and environment

Develop take-offs for concrete/rebar/prestress, foundations, station modules, track/panels/rails, bearings/joints, drainage/ducts, fill/ground treatment and road reinstatement. Convert them to delivery lots by approved vehicle/material constraints. The generated beam-only concrete quantity excludes other civil scope; do not present it as total project concrete or infer rebar from a generic kg/m³ study as a purchased schedule.

Plan permitted quarries/batching, water quality, standby concrete supply, curing/shade/temperature measures, pumping reach and rejected concrete disposal. Reuse suitable excavated material only after tests; measure outgoing spoil and transport conditions. Record disposal receipts, dust/noise/vibration controls, wheel cleaning, runoff/spill containment and packaging/returnable-rack recovery.

## Launcher and station-module movements

Provide discrete transport/assembly/commissioning packages for each launcher transfer. Check dismantled component weights, unloading platforms, escorts/access, assembly crane and tested foundations/deck supports. Reserve transfer crew and equipment; assess additional ring fronts against remaining critical-path demand. The launcher is unavailable to both old and new fronts during transfer and recommissioning.

Station modules have their own load/route/installation packages and often share access with running beams. Reserve roof/platform/shaft lifts, maintain following-trade and emergency routes, and deliver access equipment before closing necessary apertures. Under-deck storage or commercial use requires fire, flooding, impact and inspection-access review; it is not automatically free logistics space.
