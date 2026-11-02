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
shape search remain explicit adapter work for these body candidates. See the [portfolio results](../../docs/design-engine/breadth-first-shape-portfolio/README.md).

The separate civil competition explores six physical section families across
three profiles, sharing a 20 m span and 2 m deck envelope:

```bash
./osr design civil-portfolio plan
./osr design civil-portfolio build
./osr design civil-portfolio verify
```

It generates explicit polygon-prism geometry for boxes, ribbed U sections,
varying-depth boxes, folded plates, steel/concrete assemblies and stepped
load-following ribs. Stock quantities and surfaces feed candidate-specific
Class C process, tooling, delivery, scoped installed and lifecycle estimates.
The next-evaluator frontier preserves family diversity and records the required
load, material-domain, connection and manufacturing checks before costly solves.
Resistance, smooth organic discovery and native CAD remain pending; this
quantity study does not replace a selected civil component. Its conditional
mechanics follow-up is described below.

Optional [pymoo](https://pymoo.org/algorithms/moo/nsga2.html) and
[pyribs](https://docs.pyribs.org/en/stable/api/ribs.archives.CategoricalArchive.html)
adapters independently audit the finite evaluated pool. Install
`engineering/design_search/requirements-search.txt`, then run
`./osr design civil-portfolio audit-optimizers`. pymoo checks Pareto sorting;
pyribs retains separate objective champions within each descriptor cell.
These adapters do not yet emit evolutionary geometry candidates. See the
[civil comparison](../../docs/design-engine/civil-shape-portfolio/README.md).

The [civil mechanics follow-up](../../docs/design-engine/civil-shape-mechanics/README.md)
evaluates each section's actual stepped stiffness under the same selected train's
empty, normal and crowd-control axle loads. It propagates all three accounted
span-mass scenarios and compares steel-only with perfect-bond hybrid hypotheses.
Representative-pose responses and analytical all-pose model bounds remain
separate. Lifting demands can increase provisional erection cost; stiffness,
cost and mass retain alternatives in each family without granting qualification.

```bash
python3 -m engineering.design_search.civil_shape_mechanics build
python3 -m engineering.design_search.civil_shape_mechanics verify
```

These gross-elastic calculations do not resolve cracking, resistance, shear,
torsion, connections, actual crane capacity or unknown installed quantities.
Stage-two solver admission and physical acceptance remain pending.

Run `./osr workbench` and open Design Portfolio to browse the body, civil and
two web-topology portfolios. The body
quantity archive retains 18 of 54 candidates. The civil quantity archive retains
6 of 18, while the mechanics archive retains all 18; each archive filter keeps
its own objectives and scope. Civil details join the exact parent portfolio,
candidate and quantity evaluation, show partial beam progress, and leave stage
one incomplete. Body stock cost per car and scoped installed civil cost per
20 m span remain separate comparisons.

The [implicit cellular experiment](../../docs/design-engine/implicit-geometry-study/README.md)
creates a bounded three-dimensional gyroid-sheet occupancy and a binary VTK
export. Its 0.4 m sample uses an assumed material density and has 8,448
occupied cells, or 129.525 kg of sampled material; skin, connections, installed
mass and costs are not included. The voxel surface is not a manufacturing CAD
model, and the reported continuous-volume interval assumes exact arithmetic.
The saved sample is a detached component study, not a railway candidate.

```bash
python3 -m engineering.design_search.implicit_geometry_publication verify --expected-manifest-id 3fa44c54689ae832a4d450a45ba5da7fe0092bd87d54a3738d499a7087787117
python3 -m engineering.design_search.flanged_span_publication verify
```

The externally pinned implicit manifest identifies the original evidence; the
verifier resamples it and compares the VTK bytes while recording the replay
environment separately. It does not independently attest the original runtime
or qualify the shape for manufacture.

The topology baseline has an additional independent cost replay. Supply its
identity from a trusted reference, such as the reviewed publication commit:

```bash
python3 -m engineering.design_search.topology_baseline_integrity --expected-baseline-id 55755de037fa3708aab0ff579caea20585c92e3da740505c395784aed6fe7d29
```

This recomputes the canonical cost fields and compares them with the pinned
baseline; recorded and replay tool contexts remain separate. The lower-level
`validate_baseline` check alone checks internal consistency and does not provide
this independently anchored replay.

The [flanged-span system scenarios](../../docs/design-engine/flanged-system-cost-study/README.md)
use the same six-car vehicle, synthetic route and cost-rate assumptions for three
distinct span geometries. Rails and fasteners are counted once; reinforcement
and bracing have bounded fabrication and inspection allowances. Productive
crane hours include the paid time implied by utilization. Whole-life ranking
against the reference is held because the reference does not yet have matching
coating and bearing renewal events. Site, structural and equipment evidence
remain open.

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
