# Multi-agent generative engineering campaign

## Federated engineering twins

`./osr design twin` joins the controlled 63-package inventory, source-qualified
component specifications, existing physical-study model, and executable
mechanical, civil, software and factory alternatives. Specialist AI agents
developed the lanes and then rotated into independent criticism. The retained
runner executes deterministic engineering adapters; it does not invoke an LLM
or browse for new ideas at runtime.

```sh
./osr design twin plan
./osr design twin run --output build/design-twin/new-campaign --concurrency 3
./osr design twin verify --output build/design-twin/new-campaign --replay
```

The [Baghdad development record](../../docs/design-engine/baghdad-engineering-twin-2026-10-17.md)
links the component/variant browser, complete retained model packets and open
detail/evidence requests. Parts and variants have distinct revision-bound
identities. Mechanical changes trigger explicit gross-added-mass civil
sensitivities with bounded failure-directed repair; removed structure and omitted
accessories receive no invented mass credit. The original reference model stays
configuration-distinct.

Numerical caches are reset at campaign start. Input and executable-source bytes
are captured before execution and checked afterwards; code changes require a new
Python process. Output hashes and the exact member set are verified. `--replay`
recomputes the same packet in the recorded Python/NumPy environment;
`--historical` checks retained byte integrity without current applicability.

Observation replay is read-only and binds asset, configuration, units, scenario,
model endpoint time and observation provenance. It rejects incompatible or
out-of-order records and retains residuals. Matching synthetic or unverified
field records never confer physical validation. Use `./osr design twin observe
--help` for the intake command. Actual supplier internal BOMs, unresolved part
dimensions/tolerances, site data, material/process qualification, physical
calibration and issued manufacturing information remain explicit open work.

The [architecture feedback](../../docs/design-engine/architecture-feedback-2026-10-17.md)
propagates actual LM3 source axle identities plus proposed gap/member changes,
keeps the six-car mass sensitivities separate, and investigates whole-module
platforms and British equipment limits. All acceptance gates remain open.

```sh
./osr design campaign architecture --output build/architecture-feedback/my-run --native
./osr design campaign verify-architecture --output build/architecture-feedback/my-run
./osr design campaign publish-architecture --output build/architecture-feedback/my-run \
  --destination docs/design-engine/my-architecture-review
./osr design campaign verify-architecture-snapshot \
  --destination docs/design-engine/my-architecture-review
```

Use fresh output directories. `verify-architecture --historical` and
`verify-architecture-snapshot --historical` check retained integrity using frozen
case records, without asserting applicability to current source inputs.

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

## Unified review and immutable evidence

The [campaign review](../../docs/design-engine/campaign-review/index.html)
filters configuration-specific screening results, detailed unknowns and next
actions, and compares two records without inventing unknown mass or cost.
Generate it with `tools/automation/campaign-review.py --architecture <packet>`.
The [consolidation record](../../docs/design-engine/review-consolidation-2026-10-17.md)
explains historical applicability and acceptance limits.

Published JSON may now be an immutable-store reference. Use
`engineering.generative_design.evidence_store.read_json(path)` or
`read_bytes(path)` to read it, rather than decoding the reference file directly.
`verify_projection(folder)` verifies the exact original member set and hashes.
`materialized(folder)` is a context manager yielding a temporary reconstruction
of the original packet; legacy snapshot verifiers use it automatically. The
original seals are preserved byte for byte. `source_closure(path)` includes only
reachable objects, so adding unrelated evidence does not stale an older source
binding. Publication deduplicates repeated JSON subtrees in the shared store;
CAD and review assets remain available at their ordinary paths.

Run `tools/automation/migrate-design-evidence.py verify` to check the three
migrated historical packets. `prune` reports unreferenced objects without
deleting them; the explicit `prune --delete-unreferenced` maintenance command
removes only objects outside every projection and pinned original source map.
Run integrity checks before and after maintenance. Never edit stored objects or
replace historical seals to make current-source checks pass.

`./osr validate run --profile factory-native` now requires a fresh architecture
campaign in addition to the original factory examples and common adapters.
`python -m engineering.generative_design.native_acceptance run --output <newdir>`
executes and independently checks the two mandatory current architecture
models; `verify --output <dir>` rechecks its receipt. Failures remain in the
output directory and fail the profile. This establishes numerical/native
correspondence for the declared geometry, with engineering and manufacturing
release explicitly false.

## Feedback-directed detailed design team

The [detailed scenario](../../docs/design-engine/multi-agent-detail-scenario-2026-10-17.md)
adds `design_scenario.plan()` with exact component/artifact/inspection allocation,
`mechanical_detail` and `civil_detail` adapters, and `design_iteration` orchestration.
Run `./osr design campaign iterate --output <fresh-dir> --native --budget 256`.
The default executes existing preliminary studies for every package;
`--no-baseline` limits execution to the new detailed adapters. The standalone
`tools/automation/design-iteration.py` CLI exposes the same functions.

Every attempt is checkpointed and retains parent/repair reasons. Failed checks
generate bounded changes, with full geometry/self-weight/demand recomputation.
Mechanical gross mass feeds separately identified civil sensitivity contexts;
net replacement mass remains unknown. `--resume <prior-dir>` continues retained
frontiers only for unchanged sources and contexts. Budget is a total per context,
not an additional evaluation count. Changes require new controlled campaigns.

`verify-iteration --require-native` replays the numerical feedback sequence,
checks exact source/component/evidence joins and independently derives required
native context membership. `factory-native` now also executes this detailed
campaign and verifies all required assembly exports; old receipts are incomplete.
Historical integrity cannot satisfy fresh native acceptance. Local survivors
remain research proposals until all package and integrated acceptance gates close.


## Hierarchical experiments and recovery

The [hierarchical pilot](../../docs/design-engine/hierarchical-development-2026-10-17.md) uses common-store jobs, bounded isolated worktrees and independent fixtures to evaluate proposals and reject adverse parent effects. `tools/automation/hierarchical-design.py` plans, runs, verifies and publishes these experiments. `hierarchical-design` is a required local validation profile for affected sources.

Detailed runs default to `--mode repair`; `--mode optimization` continues past the first known-check pass and retains sourced conditional Pareto alternatives. Resume accepts an interrupted `execution-state.json` without a final receipt, preserving completed attempts and the frontier in a fresh output directory. Original mode/source/context/environment bindings remain mandatory. Historical evidence is checked against Git-index/tree publication membership as well as its immutable seals.
