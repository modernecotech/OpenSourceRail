# ERPNext and Frappe HR integration

<!-- osr-system-context:start -->
OpenSourceRail develops affordable rail that local companies can build, maintain and improve. The published digital release joins a costed vehicle, civil works, controls, production plan and Workbench journey; Baghdad has separate elevated city planning alternatives. The earlier v0.6 passive-wheel, station-launch design remains research, not the installed drive selection for the v0.7 reference or Baghdad. Each candidate retains its own geometry, mass, service, power, cost and evidence. Safety and accessibility remain requirements. Digital results do not grant fabrication or passenger-operation approval.

[Project introduction](../../README.md) · [Engineering approach and current status](../../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

The [composition](compose.yaml) includes ERPNext, Frappe HR, the OpenSourceRail
integration app, MariaDB, Redis, workers, scheduler, websocket server and nginx.
It supports accountable business workflows; it does not establish engineering
or physical acceptance.

The retained v0.6 design workflow generates candidate-bound engineering BOMs,
stock and process records, assembly dependencies, procurement tasks and
disabled ERPNext Item/BOM drafts. Review the
[candidate delivery index](../../docs/design-engine/coupled-railway/delivery-index.json)
and [current engineering exports](../../docs/design-engine/current/exports/manifest.json).
The [v0.7 selected production handoff](../../docs/reference-v07/digital/production/README.md)
has its own 52-row BOM and 23-step routing; it is a digital planning package.
Drafts must not become approved Items, submitted BOMs, purchase orders or Work
Orders through an automatic design refresh.

Procurement and production require approved materials, controlled drawings,
tolerances, process instructions, supplier configurations and quotations,
company and warehouse masters, and authenticated acceptance evidence. Cost and
production scenarios include two 8-hour production shifts; civil construction
uses two 8-hour shifts. Operating-cost scenarios model two shifts for 16/18-hour
service and a third shift for a 24-hour case. These are planning assumptions,
not an approved local roster or operating plan.

Private configuration and secrets belong under `var/erpnext/`. Existing
databases and persistent volumes are retained. The repository does not
provision a configured business site, city assets or company-specific master
data. Native regression scripts under [`tests/`](tests/) require a configured
site and private credentials.

The integration app supports draft planning, procurement, candidate identity,
revision review, workforce, qualification and maintenance records. Native
permissions and accountable review apply. Alarm clearance, stock movement,
repair completion and ERP case closure do not release a railway or manufactured
unit. The design runner never creates credentials, measurements, supplier
quotations, signatures or physical release evidence.

## Airport supplier quotations

Sign in to `/airport-sourcing` on a site with the OSR app installed. A buyer chooses the project, estimate edition and lot. Each invited supplier uses their own linked ERPNext account to enter quantity, price, exceptions and after-sales terms. The portal compares their native Supplier Quotations.

The opening Project carries its central planning allowance. The private estimate holds the full quantities, extended amounts and price sources. To inspect the unit rates in Desk, open **Item Price** and filter by one of the project's three **OSR estimate** buying lists. A scenario with a different quantity uses that scenario's quantity to derive its unit rate. Rounding follows the site's Item Price precision. Supplier offer prices stay on the individual quotation. [Price register and introduction](../../cities/Baghdad/engineering/prototype/PROCUREMENT-PLAN.md) · [ERPNext Item Price](https://docs.frappe.io/erpnext/item-price) · [ERPNext Request for Quotation](https://docs.frappe.io/erpnext/request-for-quotation)
