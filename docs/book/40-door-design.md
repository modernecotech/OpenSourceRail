# The door operator as a complete module

A passenger door is a fitting test of whether a railway design is truly
connected. It must suit the body opening and the station platform, move
through an unobstructed path, protect passengers, receive power and
signals, survive repeated use, and be removable by a maintainer. The
v0.7 programme chose one door operator as a representative module because
it joins these mechanical, electrical, production and service questions
in a form that can be reviewed end to end.

## Begin with the counted proposal

One opening has 74 defined part types and 694 individual pieces in the
current proposal. Among them, 97 pieces are proposed for local fabrication,
568 for standard purchase and 29 for purchase subject to qualification.
Across the six-car train there are twelve openings. The inventory includes
the header, guide, carriage, belt, pulleys, drive, leaves, sensors, seals,
wiring and their connections. It is much more informative than a simple
door animation, but counting is only the first step of installation.

The stock-and-allowance subtotal for one opening is about fifty kilograms.
That number is not an installed mass. Mounts, actual bought equipment,
hardware choices, protective enclosures and the way parts are attached
can change it. The body structure around the opening must carry the
operator and passenger loads. Its motion must remain clear under body
deflection, manufacturing tolerance and wear.

## Draw the mating relationships

A buildable drawing set needs controlled datums: how the header attaches
to the body, where the guide lies, how the carriage runs, how the belt
and pulley align, where the motor and reducer sit, and how the leaf meets
its stop and seals. Sensors need positions that work in the real motion
envelope. Inspection limits must distinguish an acceptable assembled
door from one that merely looks plausible in a model.

The current installation study reveals a specific problem. Eleven operator
types still occupy a generic centre region of the header rather than
resolved installed positions. A two-metre removal envelope does not
represent the full 2.9-metre guide stock. These are useful findings: they
tell the team what must be redesigned or measured before anyone describes
the operator as fitted. Copying the generic coordinates into a drawing
would hide, not solve, the conflict.

## Make, inspect, replace

A local workshop needs material and process definitions, cutting and
machining instructions, assembly order, tooling, tolerances and QA checks.
Purchased components need their own supplier and incoming-inspection
records. An assembled door needs a serial identity so its exact children,
tests and later repairs can be traced. Replacement requires a safe
isolation procedure, a path for removing the largest component and a
way to verify the fitted replacement against the vehicle revision.

The project already has a source-bound door panel and a typed software
route for counted assemblies. These expose part counts, proposed groups,
missing inspection definitions and custody requirements. A native
ERPNext journey has exercised a simpler synthetic workpiece, and software
contracts cover some made and bought child records. The full 694-piece
door has not yet passed that actual native lifecycle. Nor has the physical
operator completed a mated installation, qualification test or passenger
service approval.

The module will be complete for the v0.7 software journey when a user can
open the corridor's exact vehicle, examine the controlled operator, follow
its bill of materials and inspection record, and see how it is removed and
replaced. Physical qualification requires the next, independent step:
manufactured parts, measurements, endurance and safety testing under
approved limits.

## A passenger-facing design review

The operator can also be reviewed from the platform and cabin. Leaf speed,
closing force, obstruction detection, visible and audible warnings,
emergency release, seal condition and the platform gap affect how safe
and confident people feel when boarding. A wheelchair user needs a
predictable clear width and enough time to pass; a person with luggage
or a child may meet the closing path differently. These behaviours
need tests with the actual door and control arrangement, not only a
static section drawing.

Maintainers have their own passenger-facing problem: a faulty door can
remove a car from service or delay a whole line. Fast diagnosis and a
replaceable operator could improve availability, but only if the unit
can be isolated and extracted in the real vehicle. The unresolved full
guide removal is therefore an operating and cost issue as well as a
CAD issue. This is why v0.7 follows one module through the complete
system before scaling the method to every component.
