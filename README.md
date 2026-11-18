# OpenSourceRail

OpenSourceRail develops affordable urban rail and the open tools to plan, design,
build, operate and renew it. The aim is a railway that local companies can
manufacture, inspect and repair, with design knowledge and supplier choice kept
in-country. Safety, accessible travel and passenger protection are requirements
for every design.

**Current published release: [v0.7.1](docs/RELEASE-v0.7.md).** It contains a
costed **digital** railway reference and separate city planning applications.
It does not authorize construction or passenger operation. The [architecture
guide](docs/ARCHITECTURE.md#which-design-is-current) identifies each design;
the [engineering status](docs/ENGINEERING-STATUS.md) and [cost baseline](docs/COST-BASELINE.md)
give the current assumptions and results.

## The current designs

| Design | Purpose | 2026 US-dollar installed estimate |
|---|---|---:|
| [Synthetic 30 km reference](docs/reference-v07/README.md) | One six-car, 276-place powered-wheel train, 12 stations, 10 m precast spans and overhead power; a joined design, cost and production example | **$1.025bn** |
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

The earlier [v0.6 passive-wheel, station-launch reference](engineering/development-baseline.toml)
is retained for research. Its six 17 m comfort cars have 44 fixed seats and two
wheelchair places per car, no planned standing, passive steel-wheel bogies and
no onboard traction motors or traction battery. Station launch, limited
boosters and small onboard drives remain separate design options; their
whole-system mass, energy, braking, civil and cost consequences must be
calculated for each route. The [v0.6 findings](docs/design-engine/v06-design-closure/README.md)
and [v0.7 execution record](docs/design-engine/v07-execution/README.md) preserve
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

## Explore and use the work

1. Start with a [city](cities/catalogue/README.md), the [Baghdad proposal](cities/Baghdad/PROPOSAL.md)
   or the [planning workspace](docs/workbench/planning/index.html).
2. Compare complete railway choices in the [Workbench](docs/workbench/current/index.html)
   and read the [fourteen-scope cost basis](docs/COST-BASELINE.md).
3. Inspect the [vehicle, civil and production package](docs/reference-v07/README.md),
   [control electronics](control-electronics/README.md) and [engineering model gallery](docs/engineering-gallery.md).
4. Connect a reviewed design to [ERPNext/Frappe HR](deployment/erpnext/README.md)
   and [FUXA](deployment/supervision/README.md) for delivery and operations planning.

For the bounded digital software journey:

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

The [source-bound engineering packet](docs/design-engine/current/README.md)
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
