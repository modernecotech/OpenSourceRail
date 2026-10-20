# ERPNext business deployment

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
