# Technical documentation

<!-- osr-system-context:start -->
OpenSourceRail connects locally maintainable railway hardware, design and delivery tools, and train and wayside software. The published v0.7.2 Baghdad opening study includes a service plan, traction assessment and supplier dossier. Current development joins revised route, vehicle, power, civil and purchasing assumptions for v0.8 production preparation; first-article measurements and independent review remain open. The v0.6 passive-wheel vehicle is a separate research selector. Safety and accessibility remain mandatory, and digital results do not grant fabrication or passenger-operation approval.

[Project introduction](../README.md) · [Current platform and evidence](BOOK.md)
<!-- osr-system-context:end -->

The [development vehicle](../engineering/development-baseline.toml) retains passive wheel bogies and an aluminium secondary. Each railway study specifies its propulsion system. The [current engineering packet](design-engine/current/README.md) describes the selected vehicle and its open physical requirements. The [historical archive](archives/README.md) and dated research packets preserve earlier evaluations; their results do not transfer to a different candidate.

## Choose a railway

| For this decision | Start here | What you get |
|---|---|---|
| Evaluate OpenSourceRail for a prospective operator | [Operator guide](operator-review/README.md) and [illustrated briefing](operator-review/OpenSourceRail-Operator-Brief.pdf) | A meeting agenda and an offline kit for inspecting station and train models, operating screens, money and staffing. |
| Price a reference railway on a common basis | [30 km reference](reference-v07/README.md) and [capital, operations and renewals](reference-v07/cost/README.md) | A synthetic twelve-station corridor with a powered train, overhead supply, beam quantities, fleet and production schedule. |
| Review a Baghdad investment proposal | [City guide](../cities/Baghdad/README.md), [corridor geography](../cities/Baghdad/maps/README.md) and [buyer comparison](../cities/Baghdad/BUYER-COMPARISON.md) | Two independent elevated networks, mapped locations and gaps, funding cases and a way to compare supplier prices and verified Iraqi value added. |
| Develop a proposal for another city | [City catalogue](../cities/catalogue/README.md) and [planning workspace](workbench/planning/README.md) | City-specific planning records and the inputs needed to define an opening service, sites and infrastructure. |

## Follow one asset from design to service

Take a bogie as an example. The designer locates its wheel and brake interfaces on the car. The buyer asks suppliers to identify the geometry, included parts, exclusions and replacement access. The factory links the build and inspection records to the serial fitted to the car. In service, the maintainer needs that serial, the workshop procedure, the replacement part and a release record before the train returns to traffic.

| Handover | Records to use |
|---|---|
| Designer to buyer | [Train and station models](operator-review/twins/README.md), [core interface schedule](reference-v07/integration/interfaces.csv) and [Baghdad frame quotation](../cities/Baghdad/engineering/mechanical/vehicle/README.md) |
| Buyer to manufacturer | [Bills of materials and assembly routes](reference-v07/manufacturing/README.md), [selected production quantities](reference-v07/digital/production/README.md) and [works layouts](operator-review/delivery/README.md) |
| Manufacturer to operator | [Control electronics](../control-electronics/README.md), [boarding and brake trials](../cities/Baghdad/engineering/controls/README.md) and [staff training and assessment](operator-review/delivery/README.md) |
| Operator to maintainer | [Control-room and serial-history examples](operator-review/screens/README.md), [ERPNext and Frappe HR setup](../deployment/erpnext/README.md) and [supervision and gateway setup](../deployment/supervision/README.md) |

The demonstrations include proposed designs, simulated equipment and an earlier business-system pilot. Check the railway, design revision and evidence described on each screen before attaching records to a purchase order or installed asset.

## Find the engineering basis

The [architecture](ARCHITECTURE.md) identifies the vehicle and power supply for each railway. The [engineering status](ENGINEERING-STATUS.md) records open checks. The [cost baseline](COST-BASELINE.md) and [delivery roadmap](ROADMAP.md) connect those choices to quantities, budgets and the next trials. For the commands behind the local Workbench, use the [engineering guide](../engineering/development_baseline/README.md).

The [v0.7.2 release record](releases/v0.7.2/README.md) describes the released Baghdad Airport timetable, traction study and supplier dossier. The [Airport prototype review](../cities/Baghdad/engineering/prototype/README.md) retains a later frame revision on the earlier 12 km schematic. The [current Airport audit](../cities/Baghdad/engineering/simulation/AUDIT-RESULTS.md) covers the revised 17.46 km study and its paired-supply budgetary enquiry. The [v0.7 release ledger](RELEASE-v0.7.md) records the digital reference and its release checks. The [v0.6.1 software release](releases/v0.6.1/README.md) and [research archive](archives/) preserve earlier work, including the passive station-powered reference. Use the [illustrated book](../OpenSourceRail-Book.pdf) for a longer introduction and the [documentation index](INDEX.md) to locate an individual guide.
