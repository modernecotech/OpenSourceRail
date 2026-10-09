# Civil programme and workface controls

This is the scheduling and execution interface for the [civil master plan](civil-works-master-plan.md). The [generated package graph](../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/civil-works/package-dependencies.json) includes all fourteen civil packages per line and links the complete-line opening requirements for every current line. It supplies logic and quantities; dates stay unknown where surveyed scope, measured rates, contract calendars or release dates are missing.

## Work-breakdown and asset records

Use programme → city → line/zone → continuous run, station, special, depot or energy site → work package → approved Task → serialized installed asset. Keep running span/support IDs, station/platform/access IDs and special/utility/drainage/yard references stable. Model station and transition scope explicitly rather than duplicating it in running bays. Bill quantities and costs by this hierarchy; link drawing/method/design revisions and suppliers.

Each Task carries location and IDs, method revision, design/temporary-works reference, predecessor release, measured quantity, required role quantities, reserved equipment/materials/crew, allowed shift/calendar, estimated/measured duration, hold points, completion evidence and independent acceptance requirements. Method authoring status cannot issue a construction permit. Use current native ERP eligibility and future reservations before assignment; revalidate at start and after a relevant change.

## Programme stages

1. Mobilisation/design: appoint roles; land/survey/utility/ground investigations; approve worksite/temporary-works strategy and procurement scopes; qualify representative methods and trial products.
2. Enabling: create access, drainage and working platforms; divert/protect services; obtain road/water/land permissions and construction power/water.
3. Parallel production: qualify factories/first articles; construct verified foundations and substructure ahead; build station and special packages; book delivery and erection paths.
4. Running erection: draw from accepted stock and support buffers; complete two-beam bays with checked restraints and stage handover; track delivery/rejection and resource hours.
5. Interfaces and finishing: station approaches/special closures, continuity/joints, walkways/drainage/waterproofing, track support/rail, station enclosure/access, depot/energy civil and public realm.
6. Handover/testing: inspect complete assets, clear NCRs/restrictions, issue as-builts and systems access, complete integrated railway commissioning and independent/local approvals.

Foundations, columns/caps, beam supply and erection operate as linked crews and queues. Use a location/time chart to preserve the tested safe lead/lag and buffer, then a finite-resource CPM for stations, specials, utilities and handovers. Do not take the maximum of optimistic independent rates as the accepted programme.

## Calendars and staffing

The proposed erection calendar is six days/week with an eight-hour shift before approved leave, holiday, heat/weather, maintenance and traffic-window deductions. No night work is credited without approval, supervision, lighting and relief. Factory curing and delivery operate on their own elapsed-time and permitted-shift calendars; a weekend erection stop can increase accepted stock and overflow a yard if production continues.

For the explicit single-shift capacity screen, 80% productive time less 0.5 h handover and 0.5 h maintenance leaves **5.4 productive hours/day**. The existing connected reference has two 2 h placements, two 1 h securing operations and 2 h advance: an **8 h serial bay cycle**, with two shifts in its original scenario. At one bay per day, a single-shift cycle would need to fit 5.4 h; at 1.5 bays, 3.6 h. Those targets therefore require measured method improvements or additional authorised shift hours. The generated review records this mismatch; it does not transfer the original two-shift rate into the one-shift calendar.

Calculate role-hours from actual task cycles and simultaneous fronts. Reserve qualified survey, foundation, pier/cap, launcher operator, two riggers where the method requires them, lift supervisor, independent inspection and handover resources. Add production/logistics, station trades and specialist installation crews by their own workloads. Protect supervisor/inspector independence, rest, breaks, leave, training, sickness and handover. A nominal role present does not satisfy required quantities or concurrency.

Recruit backwards from first-article/readiness dates through lead time, induction, training batches, supervised practice and practical equipment/task assessments. Supplier commissioning/technical support and equipment-authorised operators are separate dependencies. Training completion cannot substitute for work authorisation. The [workload/recruitment model](../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/coupled-programme/workload-and-recruitment.json) leaves missing measurements and funded appointments open.

## Running-front control and reassignment

Before the weekly plan, verify design/support/utility release horizons, accepted beam SKU stock, production slots, delivery appointments, equipment condition, crew competence and permissible work hours. Plan only tasks that can satisfy those constraints; show withheld packages and limiting resource. Review daily queue/buffer levels, cycle components, weather/traffic losses, NCRs and plant maintenance.

Treat each of the 548 disconnected Baghdad running intervals as a separate access/launcher-boundary review. Survey support spacing and actual relocation routes. Reuse a launcher sequentially only after dismantling or checked passage, transport, new-front readiness, reassembly/inspection and commissioning. Assess radial-to-ring redistribution with all resources and full-line milestones, then evaluate transfer to the next city. Record equipment exclusivity during every movement.

## Cost and cash programme

Time-phase accepted quotation scopes against fabrication, factory acceptance, dispatch/arrival, installed milestones, tests and handover. Separate advance payments/security, retention, provisional items, recurring plant costs and final account. Finance ties to the same WBS and quantities; cash need may precede installation by months. Link delay/rejection/route changes to storage, demurrage, standby, interest and replacement, preserving unknown values rather than setting them to zero.

Use existing finance as a comparator until complete quantities/prices, scope credit and accepted dates are supplied. A higher launcher rate does not establish an installed-rate saving. Systems/fleet/testing/approval milestones remain separate from civil handover, and paid passenger revenue starts only through the accepted opening/service scenario.

## Inspection, change and reporting

No next-stage release passes an open hold point or unresolved NCR affecting safety, load path or concealed work. Retain drawing/method/configuration hashes, observations, measured results, equipment/worker authority, reviewer identity/date and sign-off scope. Reinspect after transport damage, abnormal load, weather event, utility change or failed test. Quarantine changed/rejected items and reopen affected tasks/handovers.

Publish weekly planned/completed quantities by package, accepted stock, unique released supports, active fronts, installed span/beam IDs, station milestone state, labour/plant hours, rejects/rework, closures/disruption, forecast dependencies, costs/cash and decisions. Separate physical progress, documentary readiness, conditional forecast and accepted opening. Keep a reviewable change record showing input quantities, resource assumptions and conclusions that changed.

## Complete opening

CW-14 civil handover requires CW-03/04/06/07/08/09/10/11/12/13 completion as applicable and controlled enabling/production records. Link it to running structures, stations, specials/transitions, track, energy and depot/stabling opening packages. Fleet, integrated testing and approvals are additional gates; the railway opens only after all are accepted for the same line/configuration. Missing package dates or costs keep complete opening date and cash unknown.
