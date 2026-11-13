# Technical documentation

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. The reference vehicle has six 17 m comfort cars, each with 44 seats and two wheelchair places, no planned standing, and passive steel-wheel bogies on conventional rails carried by concrete. Its passive LIM interface is available for comparison; no installed propulsion architecture or powered length is selected. Acceleration, braking, speed and headway are candidate-specific design variables. The retained 120-second service control gives 8,280 nominal places/hour/direction. The reference vehicle has service batteries and independent brakes, without onboard traction motors, traction batteries or suspension magnets; alternatives must account for their complete system effects. Calculated, priced corridor and city outlines support comparison with explicit assumptions. Engineering verification, prototype validation and manufacturing or operating release remain separate gates.

[Project introduction](../README.md) · [Current platform and evidence](BOOK.md)
<!-- osr-system-context:end -->

Start with the [project README](../README.md), [current platform book](BOOK.md),
[published v0.6.1 scope](releases/v0.6.1/README.md),
[v0.7 execution record](design-engine/v07-execution/README.md) and
[roadmap](ROADMAP.md). The [integrated v0.6 reference dossier](design-engine/current/README.md)
is retained with a source-binding hold; it is not the current supported
release result.

The [planning guide](workbench/planning/README.md) explains proposal editing
and the candidate-bound v0.6 handoff; open the [planning workspace](workbench/planning/index.html)
to edit current city route, stop, service and OD proposals.

The [retained v0.6 reference overview](open-source-rail-overview.md) and
[first adoption path](first-adoptable-product.md) describe the current planning,
engineering, delivery and integration workflows. Current integration guides
cover [ERPNext/Frappe HR](../deployment/erpnext/README.md),
[FUXA and the gateway](../deployment/supervision/README.md), and the
[candidate-bound planning workspace](workbench/planning/index.html).

The [engineering Workbench](workbench/current/index.html) presents the
selected v0.6 vehicle and its evidence holds. The [coordinated railway campaign](design-engine/coupled-railway/README.md)
propagates one candidate through inventory, propulsion, braking, civil and
manufacturing evaluations. Use the [engineering implementation guide](../engineering/development_baseline/README.md),
[tools guide](../tools/README.md), and [city geography catalogue](design-engine/current/cities.json)
to reproduce current workflows and inspect geographic inputs.

The [sourcing dossier](design-engine/sourcing/README.md) describes material,
catalogue, price and construction evidence. The [sourcing implementation](../engineering/sourcing/README.md)
covers candidate-bound records, adapters, replay packets and business-system
drafts. The [model-based cost and delivery plan](design-engine/model-based-cost-and-delivery.md)
describes provisional cost completion and its evidence boundaries.

The [reader PDF](../OpenSourceRail-Book.pdf) combines the maintained
[book source](BOOK.md), project entry point, capability register, published
v0.6.1 scope and limitations, and roadmap. Its receipt also binds the v0.7 execution record
binds those sources. It does not import the held integrated dossier as
engineering proof.
Source-bound engineering packets remain authoritative for their own claims.
