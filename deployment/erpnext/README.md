# ERPNext and Frappe HR integration

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. Six 17 m comfort cars carry 44 seats plus two wheelchair places/car and no planned standing; the 120-second target gives 8,280 passengers/hour/direction. Passive steel-wheel bogies run on conventional rails carried by precast concrete. Station LIMs act on passive onboard secondaries; there are no traction motors, traction batteries or suspension magnets onboard. Service batteries, independent brakes and the existing station-led GoA4 architecture remain. The reference design is research only; city numerical regeneration, economics and physical release remain open.

[Project introduction](../../README.md) · [Engineering approach and current status](../../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

The [composition](compose.yaml) includes ERPNext, Frappe HR, the OpenSourceRail
integration app, MariaDB, Redis, workers, scheduler, websocket server and nginx.
It supports accountable business workflows; it does not establish engineering
or physical acceptance.

The current v0.6 design workflow generates candidate-bound engineering BOMs,
stock and process records, assembly dependencies, procurement tasks and
disabled ERPNext Item/BOM drafts. Review the
[candidate delivery index](../../docs/design-engine/coupled-railway/delivery-index.json)
and [current engineering exports](../../docs/design-engine/current/exports/manifest.json).
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
