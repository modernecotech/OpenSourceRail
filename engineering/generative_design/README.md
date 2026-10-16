# Multi-agent generative engineering campaign

The [queued-systems continuation](../../docs/design-engine/queued-systems-results-2026-10-16.md)
executes 63 package-specific preliminary studies, records actual production/inspection
requirements and propagates provisional six-car feedback into civil/factory demands.
It retains source-changing mechanical proposals separately from source-compatible
choices. Full discipline qualification and manufacturing release remain open.

```sh
./osr design campaign queue --output build/queued-design/my-run --native
./osr design campaign verify-queue --output build/queued-design/my-run
./osr design campaign publish-queue --output build/queued-design/my-run \
  --destination docs/design-engine/my-queued-review
./osr design campaign verify-queue-snapshot \
  --destination docs/design-engine/my-queued-review
```

Queue commands require fresh execution/publication directories. Verification binds
actual drawing JSON, referenced artifact bytes, CAD inputs, evaluator sources,
toolchain and the inherited snapshot. `--historical` checks integrity without
current source applicability. Publication retains CSV/SVG/JSON/HTML/FCStd;
native STEP and execution logs remain in the sealed local run. Inherited civil
evaluations require unchanged numerical dependencies; the new six-car response
study is calculated during each queue run. A failed attempt remains on disk.

This campaign allocates every inventoried civil, vehicle and factory item to an
agent work package, executes bounded variations, and retains the open
manufacturing/design gates. Read the
[scenario](../../docs/design-engine/multi-agent-design-scenario-2026-10-16.md) and
[scope manifest](data/system-scope.json). The actual team used civil and mechanical
design workers plus a scope worker; that worker then reviewed the proposals and
integration code independently of their authors. The local runner executes
controlled engineering evaluators, rather than creating simulated AI approvals.

```sh
./osr design campaign plan
./osr design campaign run --output build/generative-design/my-campaign \
  --civil-budget 2048 --mechanical-budget 4096 --native --common native
./osr design campaign verify --output build/generative-design/my-campaign
./osr design campaign publish --output build/generative-design/my-campaign \
  --destination docs/design-engine/my-campaign
./osr design campaign verify-snapshot --destination docs/design-engine/my-campaign
```

All execution/publication directories must be fresh. Runtime outputs remain
under ignored `build/`; compact published evidence belongs in `docs/design-engine/`.
`verify --historical` and `verify-snapshot --historical` check retained integrity
without claiming current source applicability. Full common native artifacts
remain in their sealed parent stores and are checked by campaign verification;
the portable review explicitly retains a compact projection.

The scope audit reads actual source collection IDs and hashes. It requires
coverage of 120 vehicle products, 26 assemblies, 50 station products, 19 civil
types, all 31 factory release packages, 62 production-data products, 12 mechanical
interfaces and 14 equipment cases. It also checks dependencies and exact unique
ledger IDs. Inventory assignment does not establish engineering coverage.

The civil lane varies paired Pi20/Pi25 section depth, stem width, strand count,
strand distribution and lift stations. Failed checks drive bounded neighbouring
proposals. It retains transfer, three-car service and handling fibre demands,
geometry/cover/grip screens, mass and prestressing force. Six-car loading,
accepted compression limits, reinforcement/end zones and actual mould/lift
qualification stay unknown. The continuous moving-moment method is inherited
from the [beam study](../../docs/design-engine/factory-beam-demands-2026-10-16.md);
fibre stresses remain sampled. Candidate selection is local research screening.

The mechanical lane repairs locator fit, bolt/bore and rail access, stock size,
plate stiffness and machine-envelope failures. Its continuous assessor also
supports independent analytical tests; generated search proposals are restricted
to the declared finite choices. An exhausted feedback frontier does not imply
exhaustive coverage of every Cartesian combination. Actual material resistance,
loads, fastener preload, retention, machine sweep and measured process capability
remain open. The equipment basis prioritises the Worcester-made
[Mazak CV5](https://www.mazak.com/uk-en/products/cv5/); origin and configuration
of an offered machine require supplier evidence. No supplier is contacted.

The bed coupling propagates each selected beam's changed prestressing force to
two return rails. It varies 16/20/25 mm walls and three hypothetical ground-spring
values using the existing elastic eigenvalue solver. These gross axial
sensitivities do not qualify the new head pattern, staged eccentric loads,
splices, local connections, foundations or a measured stiffness.

`--native` exports selected physical primitives through installed FreeCAD and
reopens FCStd and STEP, checking identity, volumes and bounds. The tooling
steel subset is checked for interference. Concrete and strand-envelope overlap
is intentional and gives no interference acceptance or reinforcement detail.
The original nine factory examples and earlier snapshots remain unchanged.

`--common native` executes the existing recursive CAD → Gmsh → CalculiX loop
for all six declared alternatives in each of `mechanical-cleat` and
`civil-steel-beam`. Their loads, supports, numerical limits and material assumptions
remain fixed synthetic functions. Other mapped common problems receive at most
four one-coordinate screening alternatives, or their sole fixed reference.
They do not inherit native verification from the two small part families.

`--common screen` runs those bounded screens without recursive native work;
`--common none` limits execution to the new lanes and coupling. The optional
`--common-store` and repeated `--import-job` arguments reuse terminal sealed
jobs only when city/project/environment/revision, controlled charter, current
source hashes and actual toolchain match. Every failed and unknown check stays
in its candidate. Missing objectives remain unknown.

The closure ledger and work queue retain every package and its prerequisites.
Unsupported systems need a validated discipline adapter and controlled inputs
before further automated design. Representative search passes cannot issue
manufacturing drawings, prove process capability or close an entire system.
New accepted input/model revisions require new campaigns and review of affected
descendants. The current partial evaluators deliberately produce no manufacturing
or physical release.
