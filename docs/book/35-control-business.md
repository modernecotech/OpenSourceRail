# Business, supervision and controls

A railway is built and kept in service by organizations, not only by
calculations. Parts must be ordered, inspected, assembled, fitted,
maintained and replaced. Staff need training and work records. Equipment
needs observation and fault response. The published platform connects
these concerns to engineering candidates, while keeping drafts and
simulation clearly separate from live transactions or train commands.

## From design intent to a business record

The ERPNext and Frappe HR integrations are optional building blocks for
project, purchasing, stock, workforce, manufacturing, quality and
maintenance workflows. A candidate-linked bill of materials can inform
a draft, but a real purchasing item needs a reviewed specification,
supplier and source. An incoming part needs a quantity, origin and
inspection result. An installed serialized component needs a position,
revision and maintenance history. Those records are valuable because
they let an owner know what is actually on the railway and why it was
accepted.

The v0.6.1 package provides deployment recipes, adapters and reviewable
examples. It does not create approved purchase orders or qualify a
manufacturing process. A generated draft is a prompt for the responsible
team to check the engineering definition and business meaning before
conversion. This protects local capability: a workshop can develop and
record its own processes without concealing the origin of specialist
items it buys.

## Observe equipment without confusing observation and authority

FUXA and gateway integrations explore how station and workshop equipment
could report status, trends, alarms and maintenance events. A temperature
trend might prompt inspection of a drive cabinet. A recurring door fault
might lead to a design change or different spare-part policy. The
observation record should identify the actual asset and its installed
candidate so that a maintainer does not apply the wrong instruction.

These integrations are examples until devices, networks, permissions and
procedures are commissioned for a real site. A displayed alarm is not a
train-protection decision. The Workbench is a design and review interface,
not a live operations desk. A railway's movement authority must come
from a separately engineered and approved safety system.

## Open control software as research

The control work examines station-led dispatch, automatic train
protection, interlocking, doors, train supervision and fault response.
Rust is used for deterministic contracts and simulations of state changes.
The value of this software is that unsafe or inconsistent conditions can
be described, tested and reviewed in the open. A refusal case may be more
important than a smooth normal journey: the system should stop a
contradictory movement, an occupied route or an invalid door state.

The software still needs real sensors, actuators, communications, braking
characteristics, operating rules and independent safety assessment before
any live use. A perfect test with an ideal brake curve cannot prove an
actual wet-rail stop. Station-powered propulsion and onboard brakes must
be studied together, but the onboard protective stop must remain
independent of a receiving station drive.

## Keep the lifecycle connected

Imagine a door operator whose sensor fails repeatedly. A useful platform
should connect the service event to the exact installed module, its
supplier or production lot, its drawing and inspection history, and the
vehicle candidate. Engineers can then decide whether the problem is
installation, maintenance, environment or design. An approved revision
could flow into procurement and future train builds without erasing the
history of the original part.

This complete loop is a project objective. The release establishes
parts of its data and integration route, not a finished live lifecycle.
The practical benefit of describing it now is that vehicle designers can
include serial identification, accessible inspection and replacement
from the first controlled drawing rather than trying to add them after
production.

## Give the workforce a place in the design

Local capability requires people who can assemble, test, diagnose and
repair the system over decades. Training records, safe work instructions,
shift arrangements and tooling matter as much as the drawing of a
component. Frappe HR can be part of a configured workforce process, but
the platform cannot infer that a city has qualified staff or enough
technicians from a modelled labour-hour total. A deployment team has to
identify skills, local institutions, supervision and the actual work
calendar.

This also changes the design choice. A specialized imported module may
have a low first price but require an expensive distant repair channel.
A locally serviceable module may cost more to make initially while
reducing downtime and dependence on one supplier. The lifecycle record
should make those consequences visible to the city and the workshop.
