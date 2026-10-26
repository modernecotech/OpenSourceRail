# ERPNext business deployment

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. Six 17 m comfort cars carry 44 seats plus two wheelchair places/car and no planned standing; the 120-second target gives 8,280 passengers/hour/direction. Passive steel-wheel bogies run on conventional rails carried by precast concrete. Station LIMs act on passive onboard secondaries; there are no traction motors, traction batteries or suspension magnets onboard. Service batteries, independent brakes and the existing station-led GoA4 architecture remain. The reference design is research only; city numerical regeneration, economics and physical release remain open. Maglev documents below are retained historical research, not the selected v0.6 physical design.

[Project introduction](../../README.md) · [Engineering approach and current status](../../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

This [composition](compose.yaml) retains ERPNext, Frappe HR, the OSR integration
app, MariaDB, Redis, workers, scheduler, websocket server and nginx. It supports
business records and accountable review; it does not establish engineering or
physical acceptance.

The current [maglev design programme](../../engineering/ferrite_maglev/README.md)
has provisional quantities and process routes. The
[Baghdad manufacturing plan](../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/maglev/manufacturing.json)
is not a released or fully priced MBOM. Procurement and production need approved
materials, drawings, tolerances, process instructions, supplier configurations,
quotations, company/warehouse masters and authenticated acceptance evidence.
Planning rows must not become approved Items, submitted BOMs or Work Orders
through an automatic design refresh.

Private configuration and secrets remain under `var/erpnext/`. Existing databases
and persistent volumes are retained. The declared images and native app can be
reviewed independently through this directory; current primary design commands
do not provision a business site or import city assets.

The app retains draft planning, procurement, engineering identity, revision
review, workforce, qualification and maintenance functions. Native document
permissions and accountable review apply. Alarm clearance, stock movement,
repair completion and ERP case closure do not release a railway or manufactured
unit. Current city identities, drawing revisions, product definitions and signed
acceptance records must be configured before deployment-specific workflows run.

Native regression scripts under [tests](tests/) require a configured site and
private credentials. They were not executed as part of the offline code migration.
The current design runner never manufactures credentials, measurements, supplier
quotations, signatures or physical release evidence.
