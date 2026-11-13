# A Samawah Workbench journey

Samawah is the published release's most complete fresh software example.
The Workbench loads a mapped city outline, accepts a bounded service request,
calculates a result, reuses an unchanged result and produces a separate
answer when demand changes. This lets a reader observe the platform's
central promise: a design question, its assumptions and its answer remain
connected.

## The first calculation

Begin with the displayed city and line assumptions. The source record tells
the Workbench which network and local information to use. The service
request records values such as demand and headway. Before submitting it,
note the station and access assumptions. A railway map may show a plausible
line while leaving the actual platform, walking route or land rights open;
the comparison is still useful if those unknowns remain visible.

Submit the baseline request and follow its status until the result is ready.
The summary reports service and fleet, energy assumptions, civil quantity
classes and the full cost account. A low, base and high estimate shows how
rates and model assumptions affect the total. A reader should resist the
temptation to call the base figure “the price.” It is a conditional estimate
for this source, train and service, with local prices and site quantities
still to be improved.

## The unchanged request

Run the same request a second time. The release demonstration shows verified
reuse of the sealed calculation. The same result is not a claim that the
railway has been physically tested twice. It is a check that the software
recognizes identical inputs and avoids a needless recalculation. For a
small city edit this is good engineering practice: a repeated screen view
should not regenerate a structural model, nor should a changed rate silently
reuse an obsolete cost.

The visible result record helps distinguish source, evaluation and selection.
The **source** is what the model used. The **evaluation** is the calculation
under a particular request. A **selection** is a decision to use a candidate
for a stated purpose. The first two can be checked by software; neither is
permission to build or operate the line. These distinctions may seem abstract
until two similar maps produce different prices. Then they explain whether
the difference came from geography, demand or a design choice.

## The changed-demand request

In the published demonstration, the reader changes peak demand from 4,000
to 9,000 passengers per hour per direction. The Workbench gives the revised
request its own evaluation. The two figures are scenario values, not a
measurement of Samawah's peak. Their value lies in showing how a service
and cost model responds to a passenger question. The higher case may alter
fleet and operating requirements even though the drawn line remains the
same. The old result is retained, so the comparison remains inspectable.

This is a different exercise from the v0.7 station-merge comparison described
later in the book. Demand changes the requested service. The station merge
changes a planning feature while keeping the route and selected reference
explicit. Both must preserve their own inputs and must not borrow costs
from a different vehicle candidate.

## Open the exported records

The release journey offers a short summary, detailed result, source record,
performance record and delivery draft. The summary is for orientation;
the detailed result allows questions about specific scope and assumptions.
The performance record shows whether the answer was calculated or reused.
The delivery draft turns model quantities into proposed work and review
tasks, without authorizing a purchase or a production order. The disabled
business draft illustrates a possible later handoff while preserving the
human approval boundary.

One can use this journey to teach a project team how to review a model:
state the passenger question, identify the source, inspect all the costs,
repeat an unchanged request, change one assumption, and explain the resulting
differences. It is a demonstration of traceable software behaviour. The
actual Samawah corridor still needs demand evidence, surveyed access and
alignment, site structures, physical train data, supplier prices and
independent engineering review.

## Carry one question into the field

A sensible next action is to select one station or street crossing whose
real geometry could alter the model's result. A field team can measure
walking routes, available frontage, platform approaches and utilities,
then return with a documented alternative. The Workbench can compare the
new proposal with the earlier one under the same service and candidate.
The important measure of progress is whether the decision becomes clearer:
perhaps one position has better accessible access, or perhaps a cheaper
structure creates a longer walk. The software helps keep those effects
together; the field visit supplies knowledge the software cannot invent.
