# OpenSourceRail design search

The design search coordinates candidate generation, engineering evaluation,
delivery records and whole-system comparison. The repository's development
default is defined in [`engineering/development-baseline.toml`](../development-baseline.toml).
Every run must preserve candidate, evaluation and selection identities and carry
one candidate bundle through dependent models.

## Coordinated railway workflow

Start with the coupled campaign and continue any pending work from its retained
frontier:

```bash
./osr design railway
./osr design railway plan
./osr design railway run --max-bundles 2 --native-jobs 1
./osr design railway publish
./osr design railway verify
```

The coordinated workflow joins geometry, installed mass, structural and
propulsion analysis, braking, civil quantities, manufacturing and provisional
economics. A changed upstream input invalidates dependent results. Failed,
incomplete and out-of-domain evaluations remain recorded with their reasons;
software capability and successful numerical replay do not establish physical
qualification.

## Design exploration

Use the function-first adaptive search to change materials, load paths, joints,
fitout, running gear, propulsion, service, civil works and manufacturing:

```bash
./osr design adaptive
./osr design generative
```

Adaptive candidates retain their requirements, ancestry, evaluator domains and
resource limits. The generative experiment preserves its typed physical graph,
stock, interfaces and assembly description. Each candidate must be propagated
through the same downstream inventory, engineering, delivery and cost models.
Search examples and solver construction bounds are not the full design space;
repeated local failure should lead to a new design family or an evidence task.

The breadth-first shape portfolio composes the existing frame, shell and rib
productions across 18 descriptor cells and three bounded geometry profiles:

```bash
./osr design portfolio plan
./osr design portfolio build
./osr design portfolio verify
```

It retains per-family Pareto alternatives using actual nominal stock mass,
manufacturing-occurrence count and provisional low/base/high Class C body-stock
factory-gate estimates. The production proxy uses two 8-hour shifts; the linked
scenario defines civil work at two 8-hour shifts and operations at two 8-hour,
two 9-hour and three 8-hour shifts, but this study generates no civil or
operating estimate. The study does not run structural analysis or select a railway. Curved shells,
cellular/implicit geometry, topology optimization and coupled vehicle/guideway
shape search remain explicit adapter work. See the [portfolio results](../../docs/design-engine/breadth-first-shape-portfolio/README.md).

## Bounded campaigns

Existing campaign definitions remain reproducible under their own contracts:

```bash
./osr design campaign create campaigns/v06-wheel-lim.toml
./osr design campaign run <campaign-id> [--max-jobs 1]
./osr design campaign compare <campaign-id>
./osr design campaign publish <campaign-id>
```

These bounded studies support comparison and method development. They do not
replace the coordinated workflow, expand its requirements, or grant automatic
admission of synthetic or software-generated evidence.

## Evidence and selection

Keep execution status, numerical validity, engineering screen, evidence
maturity, selection purpose and physical acceptance separate. A useful
calculation may fail its engineering screen; an assumption may support a
provisional design estimate without supporting a physical-performance claim.
Preserve Pareto alternatives and rank the next experiment separately from the
integrated-baseline candidate. Independently confirm any proposed selection.

See [the current coordinated experiment](../../docs/design-engine/coupled-railway/README.md),
[adaptive search definition](../../campaigns/adaptive-railway-design.toml),
[generative structural experiment](../../docs/design-engine/generative-structure/README.md),
and [development instructions](../../AGENTS.md).
