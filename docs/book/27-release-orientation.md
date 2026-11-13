# The published v0.6.1 platform

The first packaged OpenSourceRail platform release gives a reader several ways
to explore the project. One can browse a city, inspect a proposed service,
follow an engineering candidate, examine a drawing, and ask how a design might
be made and maintained. The release is a working software and research
environment. Its output is most useful when a reader keeps the difference
between a calculated outline and an approved railway clearly in view.

## Three products in one project

The first product is the **design and delivery platform**. It brings city
geography, transport proposals, vehicle and civil designs, calculations,
quantities, costs and proposed delivery records into a traceable workflow. A
change to a station or train should be visible in the results it affects. The
platform is already useful for exploring and reviewing design-stage questions,
though not every intended handoff is complete.

The second product is a **railway and manufacturing system**. Its development
reference is a six-car, wheel-supported train on conventional rails supported
by concrete, with a strong preference for local manufacture and repair.
Vehicles, guideway, stations, propulsion, braking and workshops must form one
buildable candidate. The release includes drawings, inventories and numerical
studies; it does not contain a physically qualified train or construction
package.

The third product is **open train-control research**. Rust software explores
train protection, interlocking, station dispatch, supervision and fault
response. Its simulations and checks can reveal inconsistent commands or
unsafe state transitions. It has no live railway movement authority. The
business and equipment-observation integrations discussed later are also
software components; they do not turn the research system into an operating
railway.

## Start with what is available

The published city catalogue contains outlines for 266 cities and 1,565
lines. These are mapped planning cases with route and station information,
service assumptions, energy and cost scenarios and local-evidence records.
They provide breadth for comparison, not 266 surveyed construction designs.
The Workbench can display the geography, sources and calculated results and
can run a bounded Samawah study. That study is the clearest fresh example of
the v0.6.1 software journey.

The release also includes fourteen-scope cost and delivery drafts. A reader
can inspect what is included in a proposed railway estimate, where a price
comes from and which quantities remain provisional. Engineering galleries
offer rotatable and editable geometry for selected vehicle and civil examples.
These are useful views of design thinking, not approved production drawings.

Some capabilities are **previews**. Baghdad has a retained route, service and
cost comparison that can be read without recalculating the city. Candidate
research has source-pinned alternatives, but the current Workbench portfolio
selector is held. ERPNext, Frappe HR, FUXA and gateway adapters can prepare
reviewable drafts and examples, while actual purchasing and railway control
remain outside the release. Full native CAD and mechanics workflows vary by
model and tool availability.

## Why the visible holds matter

A calculated result is trustworthy only for the inputs and method that made
it. The older integrated engineering dossier has a broken source binding at
the published release. The Workbench therefore keeps global portfolio and
cost cards held instead of presenting them as current. The Samawah calculation
uses its own checked inputs and remains available. Likewise, the native
RustGIS project export from the published atlas is held because its GIS and
outline publications do not match; the read-only Baghdad atlas still works.

This is how an open platform should behave when evidence is incomplete: show
the useful work, name the limit and refuse to borrow a result from a different
source. Later development may close or change a hold, but the v0.6.1 release
remains a fixed record of what users could actually inspect and run. The next
chapters take a reader through that release, beginning with one ordinary
Workbench session.

## A modest adoption path

A city need not begin by choosing a train. It can start by agreeing on a
passenger problem, asking residents how they reach existing services and
using the atlas to compare several corridor ideas. The Samawah journey
shows how to turn one scenario into a traceable calculation. The cost
scopes identify which local prices, surveys and supplier conversations
would have the most value. Only after those questions are clearer should
the city ask whether a vehicle, propulsion family and civil arrangement
can meet the service at an acceptable whole-life cost. In that sequence,
the platform supports an informed public and engineering discussion
without implying that a proposal is ready for tender or passenger service.
