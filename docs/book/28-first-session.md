# A reader's first session

The simplest route into OpenSourceRail is to open the published Workbench and
follow the Samawah example. The release package includes an installation guide
and a recorded clean-install demonstration. For this software journey, the
optional native CAD, mechanics, GIS and business services are unnecessary.
That separation helps a new reader understand the platform before assembling
a full engineering workstation.

## Orient yourself before changing a value

Begin with the city view. Choose Samawah and inspect the line and station map,
the displayed source information, demand assumptions, planned headway and
access notes. The map is a proposal over available geography. It does not
certify the walking route to a station, the land needed for a pier or the
accuracy of an unsurveyed alignment. A useful first question is therefore:
*which facts are local observations, and which are shared model assumptions?*

The Workbench separates source context from an evaluation. Source context
includes the geography and other information selected for the study. An
evaluation applies an explicit service request to that context and produces
a calculated answer. The same request should lead back to the same verified
answer; a changed request deserves its own result. The interface exposes
this relationship so a reader can compare the two cases without guessing
which map, train or cost basis was used.

## Read a result in layers

After the baseline Samawah request completes, start with the service summary.
Which lines are included? How many trains are implied? What energy and civil
quantities are counted? Then open the cost view. Its fourteen scopes include
more than the train or the concrete: construction, stations, power, labour,
maintenance, replacement and end-of-life work all have to be considered.
Low, base and high values describe model uncertainty and assumptions; they
are not three supplier offers.

Next inspect the detailed result and its delivery draft. The result should
show its inputs and its unresolved questions. The delivery draft translates
model quantities into proposed tasks and resource needs. It is useful for
asking whether a local workshop or construction sequence has been considered,
but it does not authorize procurement or fabrication. A business-system draft
is deliberately disabled until reviewed conversion and real transactions are
appropriate.

## Repeat, then change one thing

Repeat the identical request. The published demonstration confirms that the
Workbench reuses the sealed result rather than performing unnecessary work.
For the reader, the important point is consistency: the same inputs should
not quietly produce a different city price or vehicle candidate. Reuse also
matters on a computer with limited disk and memory, because a design team may
review the same scenario many times.

Then change the example peak demand from 4,000 to 9,000 passengers per hour
per direction. The Workbench creates a distinct evaluation and shows its
service and cost effects. This does not assert that Samawah has observed
either demand level. It demonstrates how an owner can ask, “What if our peak
demand is higher?” while keeping the previous case available for comparison.
The same discipline should apply to a future route or vehicle revision:
change the relevant input, recalculate its dependants and retain the parent.

## Take away the right result

The Workbench offers a summary, detailed result, source record, performance
record and delivery plan for the study. These help another person review the
calculation and repeat it under the same software. The exported package is
not an engineering approval or a surveyed city plan. A new user should leave
this first session knowing what was assumed, what changed, what was reused
and what field or supplier evidence is still missing. That is a stronger
outcome than merely finding an attractive total on a dashboard.

## Discuss the result with another person

A useful follow-up is to ask a planner and a vehicle engineer to describe
the same study in their own words. The planner might notice a weak station
catchment; the engineer might notice that a proposed frequency relies on
unverified stopping. Both can refer to the same source and evaluation
without mistaking their different questions for conflicting data. A cost
specialist can then identify the largest transferred rates. This shared
review exposes the most important uncertainty before anyone invests in a
more detailed model. It also shows why the Workbench presents links and
holds alongside the attractive numbers: the next decision depends on
understanding the conditions of the answer.
