# Technical documentation

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. Six 17 m comfort cars carry 44 seats plus two wheelchair places/car and no planned standing; the 120-second target gives 8,280 passengers/hour/direction. Passive steel-wheel bogies run on conventional rails carried by precast concrete. Station LIMs act on passive onboard secondaries; there are no traction motors, traction batteries or suspension magnets onboard. Service batteries, independent brakes and the existing station-led GoA4 architecture remain. The reference design is research only; city numerical regeneration, economics and physical release remain open.

[Project introduction](../README.md) · [Engineering approach and current status](design-engine/current/README.md)
<!-- osr-system-context:end -->

Start with the [project README](../README.md), [architecture](ARCHITECTURE.md),
[current engineering report](design-engine/current/README.md) and
[roadmap](ROADMAP.md).

The [project overview](open-source-rail-overview.md) and
[first adoption path](first-adoptable-product.md) explain the delivery,
manufacturing, business, supervision and control platform. Current integration
guides cover [ERPNext/Frappe HR](../deployment/erpnext/README.md),
[FUXA and the gateway](../deployment/supervision/README.md), and the
[candidate-bound planning workspace](workbench/planning/index.html).

The [current engineering Workbench](workbench/current/index.html) presents the
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

The [reader PDF](../OpenSourceRail-Book.pdf) combines the current design
documentation, geometry review and city directory. Source Markdown and
source-bound receipts remain authoritative. Engineering, manufacturing and
physical acceptance gates remain open where evidence is incomplete.
