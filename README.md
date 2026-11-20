# OpenSourceRail

OpenSourceRail develops affordable urban rail and the open tools to plan, design,
build, operate and renew it. The aim is a railway that local companies can
manufacture, inspect and repair, with design knowledge and supplier choice kept
in-country. Safety, accessible travel and passenger protection are requirements
for every design.

**Current published release: [v0.7.1](docs/RELEASE-v0.7.md).** It contains a
costed **digital** railway reference and separate city planning applications.
Subsequent work on `main` includes the Baghdad train diagrams, station boarding replay, workforce budgets and supplier quotation comparison.
Neither version authorizes construction or passenger operation. The [architecture
guide](docs/ARCHITECTURE.md#which-design-is-current) identifies each design;
the [engineering status](docs/ENGINEERING-STATUS.md) and [cost baseline](docs/COST-BASELINE.md)
give the current assumptions and results.

## Present the railway

For a meeting with a prospective operator, [open the 14-page illustrated briefing](docs/operator-review/OpenSourceRail-Operator-Brief.pdf). For a hands-on session, [download the offline workshop kit](https://raw.githubusercontent.com/modernecotech/OpenSourceRail/main/docs/operator-review/OpenSourceRail-Operator-Kit.zip), extract the entire ZIP and open **START.html** in a browser. The kit includes the train and station models, Baghdad timetable card, control-room replay, workforce planner, funding calculator and downloadable supplier enquiries. Start with one diagrammed train, inspect its turnback, then compare unattended and staffed duties against the operating budget. [Core timetable](docs/reference-v07/integration/TIMETABLE.md) · [Baghdad train diagrams](cities/Baghdad/SERVICE-DIAGRAMS.md) · [Airport opening quantities and price](cities/Baghdad/AIRPORT-OPENING.md) · [Core and Baghdad supplier enquiries](docs/operator-review/README.md#taking-drawings-to-a-supplier) · [First-network quotation quantities](cities/Baghdad/BUYER-COMPARISON.md#first-network-quantities-for-a-pricing-round)

![Baghdad station and train in the interactive design viewer](docs/operator-review/twins/baghdad-station.png)

| Question for the meeting | What to open and do |
|---|---|
| Can a passenger board here, and can we maintain the equipment? | Select the Baghdad platform edge, door or bogie in the twin. Follow the component to its drawing and ask for loaded clearances, tool space and a witnessed replacement. [Twin and IFC guide](docs/operator-review/twins/README.md) |
| What will the control room see when equipment stops reporting? | Step through a section trip, a stale reading and restoration. Compare the timestamp with the alarm state, then follow a separate depot example through its serial history. [Operations and maintenance screens](docs/operator-review/screens/README.md) |
| How much public funding will the service need? | Choose a railway and borrowing term, then enter paid journeys and net receipts. Inspect the annual debt, operations and renewal rows. [Funding guide and worked example](docs/operator-review/finance/README.md) |
| Can local firms deliver the fleet and keep it running? | Walk the vehicle works and precast yard drawings. Compare line capacity with the order, allow for relief on each shift and cost the training cohorts. [Factory, employment and training plan](docs/operator-review/delivery/README.md) |

The [operator guide](docs/operator-review/README.md) gives a 30-minute agenda. The [delivery workplan](docs/operator-review/WORKPLAN.md) assigns route surveys, first-article trials, supplier quotations and funding decisions to the teams that would carry them out.

## The current designs

| Design | Purpose | 2026 US-dollar installed estimate |
|---|---|---:|
| [Synthetic 30 km reference](docs/reference-v07/README.md) | 51 six-car powered-wheel trains with 276 places each, 12 stations, 10 m precast spans and overhead power; a joined design, cost and production example | **$1.025bn** |
| [Baghdad seven-corridor concept](cities/Baghdad/README.md) | Independent 148.2 km, 64-station, all-elevated plan with 700-place trains and protected trackside power | **$7.866bn** |
| [Baghdad citywide concept](cities/Baghdad/PROPOSAL.md) | Independent 605.652 km, 280-station, all-elevated plan; 50.099 km is reserved guideway without an assigned passenger path | **$31.018bn** |

The Baghdad alternatives have **zero tunnels and no overhead wires** in their
selected planning configuration. They are independent choices, not stages to
add together. Their fleet, operating and construction figures use declared
planning allowances; the [Baghdad maps, full proposal and calculation](cities/Baghdad/README.md)
show what has and has not been located or scheduled. The synthetic reference
uses a different train, power supply, service and cost basis.

![Schematic Baghdad citywide railway corridors over the city map](cities/Baghdad/maps/Baghdad-606km.png)

*The citywide map shows planning corridors over the city background. Its lines
are not surveyed construction alignments.*

The [v0.6 passive-wheel, station-launch design](engineering/development-baseline.toml)
remains the repository development baseline and a separate research candidate.
Its six 17 m comfort cars have 44 fixed seats and two
wheelchair places per car, no planned standing, passive steel-wheel bogies and
no onboard traction motors or traction battery. Station launch, limited
boosters and small onboard drives remain separate design options; their
whole-system mass, energy, braking, civil and cost consequences must be
calculated for each route. The [v0.6 findings](docs/design-engine/v06-design-closure/README.md)
and [current engineering record](docs/design-engine/current/README.md) preserve
the research without changing the selected Baghdad or 30 km candidates.

## What OpenSourceRail provides

| Connected product | What it does now |
|---|---|
| [Design and delivery platform](docs/capabilities/README.md) | City maps and briefs, option comparison, engineering calculations, CAD/IFC, cost and schedule outputs, and candidate-linked records |
| [Reference railway and manufacturing system](docs/reference-v07/README.md) | Digital vehicle, station, civil, power and production packages with bills of materials, assembly routes and inspection plans |
| [Open control software](crates/README.md) | Train protection, door and brake logic, wayside control and supervision interfaces under development and simulation; see the [equipment schedule](control-electronics/README.md) |

The [engineering Workbench](docs/workbench/current/index.html) connects a route
edit to affected service, energy, quantities and cost outputs. Its editable
source is in `engineering/development_baseline/web/`; the public Workbench is
generated from that source. A candidate carries its own identity through the
geometry, mass, analysis, bill of materials, procurement and controls records.
An unknown component, price, origin or measured performance is never counted
as zero.

**Delivery lifecycle:** city brief → design and comparison → procurement →
local production → construction → commissioning → operation → maintenance and
renewal. [ERPNext and Frappe HR](deployment/erpnext/README.md) cover draft
purchasing, inventory, production, quality, workforce, payroll and maintenance
records. [FUXA and the gateway](deployment/supervision/README.md) provide
equipment observation, alarms and history; they do not grant train movement
authority. The [platform guide](docs/platform-guide.md) explains these
interfaces and their current deployment state.

## Design, build and operate the railway

| Who | Where to start | What to decide |
|---|---|---|
| City planner or transport authority | [City plans](cities/catalogue/README.md) and [Baghdad proposal](cities/Baghdad/PROPOSAL.md) | Which journeys to serve, where passengers can board and transfer, and how the city would fund construction and service. |
| Railway designer or manufacturer | [Reference train and viaduct](docs/reference-v07/README.md), [bogie and body frames](cities/Baghdad/engineering/mechanical/vehicle/README.md), [station and track sections](cities/Baghdad/engineering/mechanical/civil/README.md) | Which parts a local workshop can make, how they fit together, how to replace them and what to check on the first article. |
| Procurement or construction team | [Cost and delivery schedule](cities/Baghdad/COST-AND-DELIVERY.md) and [vendor comparison](cities/Baghdad/BUYER-COMPARISON.md) | Compare installation and renewal prices, delivery obligations and the work suppliers will undertake in Iraq. |
| Operator or maintainer | [Train and station control equipment](control-electronics/README.md), [boarding and brake sequence](cities/Baghdad/engineering/controls/README.md) and [supervision guide](deployment/supervision/README.md) | Inspect equipment, understand door and brake interlocks, and identify what crews must demonstrate before commissioning. |

Open the [Workbench](docs/workbench/current/index.html) to explore the effect of a route or station change on the train service, quantities and cost. To use the tools locally, run these commands from the repository root.

```sh
./install.sh
./osr status
./osr readiness
./osr workbench
./osr reference v07
```

The [v0.7 release guide](docs/RELEASE-v0.7.md) lists the exact selected checks.
`./osr build` and `./osr test` cover broader research scopes; read
[setup](tools/README.md) before running native CAD, FEM or large campaigns.
The [illustrated book](OpenSourceRail-Book.pdf) is a reader's overview.

## Design history and evidence

[v0.4 conventional rail](https://github.com/modernecotech/OpenSourceRail/tree/v0.4.0),
[v0.5 maglev](https://github.com/modernecotech/OpenSourceRail/tree/v0.5.1) and
the [v0.6.1 software release](docs/releases/v0.6.1/README.md) remain available
as historical designs and releases.

The [current source-bound engineering packet](docs/design-engine/current/README.md)
and [research gallery](docs/engineering-gallery.md)
retain CAD, FEM and simulation evidence with their own candidate identities.
A digital calculation or assembly view is evidence for its stated model; it is
not a physical test or an approved production drawing.

The [roadmap](docs/ROADMAP.md), [adoption path](docs/first-adoptable-product.md)
and [documentation index](docs/INDEX.md) provide deeper detail. The three
products, local production goal and open design knowledge remain the project
scope as individual railway configurations evolve.

## Contribute

Contribute route and demand data, local supplier capability, fabrication and
repair methods, engineering checks, controls, accessible design or clear
documentation through [CONTRIBUTING](CONTRIBUTING.md) and
[GOVERNANCE](GOVERNANCE.md). [AGENTS.md](AGENTS.md) states the engineering and
candidate rules. **Hayder Aziz** initiated the project; his [research
background](docs/platform-guide.md#about-the-author) explains the design
knowledge and open manufacturing approach.

Software uses **Apache 2.0**, physical designs use **CERN-OHL-S v2**, and
documentation uses **CC-BY-SA 4.0**, subject to file-specific and upstream
notices. See [LICENSE.md](LICENSE.md) and [LICENSES](LICENSES/README.md).
