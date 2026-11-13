# The Workbench project journey

The intended v0.7 Workbench journey begins with a place, not a solver.
A user chooses Samawah, sees its proposed lines and stations, opens the
close-marker question, and compares a before and after case. From there,
the project should lead naturally to the train, civil works, costs and
delivery records that would be affected by the decision. The interface
has to make both the answers and their missing inputs understandable.

## What a reader can do now

The development Workbench offers the Samawah station-merge comparison.
It calculates the two cases under the same explicit service and cost
policies, shows the raw and operational station counts, fleet and
whole-life differences, and makes the two dossiers and revised delivery
draft available. A source-bound door panel gives the reader another
view into the physical project: part definitions, proposed assembly
groups and open inspection and removal questions. These are connected
software views, not a complete physical build package.

An identical city request can be retrieved from a verified result without
rerunning the same calculation. If the user changes a substantive input,
the result must have its own evaluation and updated dependants. The
Workbench should show an unchanged result explicitly. A zero difference
in fleet, for example, tells the reader that the chosen station edit
did not move the model across a fleet threshold. It should not vanish
from the report simply because it is not dramatic.

## Guide the reader through decisions

A good project view starts with a question: What changed, why, and for
whom? It then gives a plain-language result before the detailed tables.
In Samawah, the raw marker count falls by one, but the operating stop
count and trainsets stay the same. The model's capital total falls a
little while whole-life cost rises. A reader can open the cost scopes
to see the energy and access contributions, then return to the city
map to consider whether the proposed station position helps people.

The next layer explains evidence. The route is a planning outline; the
walking path is not surveyed; the propulsion and braking evidence does
not yet support an actual operating timetable. The Workbench should
present those limits beside the figures that depend on them. A result
that cannot be supported should be held visibly, with the reason and
the next evidence needed, rather than replaced by an attractive global
number from another revision.

## Move from the corridor to an asset

The v0.7 target is to open the exact vehicle and choose its representative
door operator from the same project. The reader should see its fitted
geometry, material and make-or-buy route, controlled inspection criteria,
production and removal sequence, and maintenance record. A changed door
that alters installed mass or clearance should trigger the appropriate
vehicle and service reviews. A station location change should not
regenerate an unchanged door. Both kinds of edit should produce a
new comprehensible dossier.

This complete journey remains development work. The existing Samawah
browser comparison and door evidence panel are demonstrated software
steps. A native GIS round trip has been exercised through automated
native-tool editing, and the
full door lifecycle and installed railway integration remain open.
The Workbench will be most valuable when a new reader can follow these
boundaries without needing to interpret a collection of specialist files.

## A useful set of screens

The city overview can present the map and passenger question first. A
comparison screen can then place the parent and edited station side by
side, with a concise account of why the change was made. A service screen
can show offered trains, journey time, fleet and energy. The cost screen
can group factory, installed and whole-life figures without hiding the
assumptions underneath. The engineering screen can show the vehicle,
door and civil option alongside their outstanding fit and test findings.

The last screen should be a readable dossier: what was selected, what
changed, what evidence was used and what remains unresolved. Different
readers may stop at different depths, but the deeper record should
always be available. A planner should not need to interpret a mesh
file to see that a bearing is unverified. An engineer should be able
to find that bearing question and its exact model when ready to work
on it. This layered presentation is the Workbench's central promise.
