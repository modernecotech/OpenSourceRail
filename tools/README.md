# OpenSourceRail development tools

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. The reference vehicle has six 17 m comfort cars, each with 44 seats and two wheelchair places, no planned standing, and passive steel-wheel bogies on conventional rails carried by concrete. Its passive LIM interface is available for comparison; no installed propulsion architecture or powered length is selected. Acceleration, braking, speed and headway are candidate-specific design variables. The retained 120-second service control gives 8,280 nominal places/hour/direction. The reference vehicle has service batteries and independent brakes, without onboard traction motors, traction batteries or suspension magnets; alternatives must account for their complete system effects. Calculated, priced corridor and city outlines support comparison with explicit assumptions. Engineering verification, prototype validation and manufacturing or operating release remain separate gates.

[Project introduction](../README.md) · [Engineering findings](../docs/design-engine/v06-design-closure/README.md) · [v0.7 execution](../docs/design-engine/v07-execution/README.md)
<!-- osr-system-context:end -->

The [`./osr` launcher](../osr) is the supported entry point for the v0.6
reference and developing v0.7 engineering, planning, delivery and verification
workflows. Start with the [engineering guide](../engineering/station_rail/README.md),
[v0.6 design-closure ledger](../docs/design-engine/v06-design-closure/README.md)
and [v0.7 execution record](../docs/design-engine/v07-execution/README.md).

| Task | Command | Result |
|---|---|---|
| Inspect selected candidate and open gates | `./osr status` | Candidate identities, publication status and acceptance flags |
| Refresh current engineering records | `./osr build` | Source-bound calculations, dossier, exports and Workbench |
| Verify current records | `./osr verify` | Source and payload identity checks |
| Plan a coordinated candidate study | `./osr design railway plan` | Shared candidate, evaluator dependencies and bounded execution plan |
| Run bounded engineering work | `./osr design railway run --max-bundles 2 --native-jobs 1` | Restartable evaluations; pending and failed tasks remain recorded |
| Publish and verify a study | `./osr design railway publish` / `./osr design railway verify` | Candidate-bound study records and reproducibility checks |
| Index large campaign cases | `./osr design railway columnar index <contract-state> <private-index-dir>` | Bounded Rust Arrow/Parquet index; retained case evidence remains canonical |
| Refresh developer toolchains | `./install.sh --toolchains-only` | Verify latest Node LTS and uv stable releases, then refresh Rust stable without rebuilding design records |
| Edit and compile city proposals | `./osr plan serve` then `./osr plan compile edits.json --output build/my-plan` | Immutable route, stop, service and OD handoff bound to the selected candidate |
| Verify a planning handoff | `./osr plan verify build/my-plan` | Source and candidate identity verification |
| Inspect candidate delivery exports | `./osr twin export` | Current CAD/IFC, BOM, procurement, assembly and control export status |
| Draft selected-candidate factory work package | `./osr twin factory-draft compile build/my-plan --output build/factory-plan` | Modelled process hours, low/base/high cost and two-shift production plan; requires a verified planning handoff |
| Verify factory work package | `./osr twin factory-draft verify build/my-plan build/factory-plan` | Source and candidate identity verification; no procurement or manufacturing release |
| Open the engineering viewer | `./osr workbench` | Read-only current candidate and evidence views |

Planning handoffs contain proposals. They do not contain route-performance,
procurement, construction-schedule or full-city-cost results. Exported delivery
records are research drafts. Missing equipment, installed mass, physical drive
maps, site data, prices and acceptance evidence remain explicit; no command
grants manufacturing or movement authority.

Before a large campaign, use `./osr perf storage` to inspect the disk reserve
and `./osr design railway plan` to inspect the candidate and stage budget. The
[v0.7 runtime and toolchain review](../docs/plans/v0.7-runtime-toolchain-review.md)
identifies measured memory and disk costs and the next bounded experiments.

## Automation and dependencies

[`automation/default-design.py`](automation/default-design.py) defines the
current design refresh. Shared Python dependencies are pinned in
[`engineering/requirements.txt`](../engineering/requirements.txt). Run repository
commands through `./osr` so the declared project toolchain and environment are
used. `./osr` uses locally verified tool receipts and never resolves new releases
during a candidate evaluation. Background refresh scripts print proposed service configuration; they do
not install or activate a service.

## Current checks

CI runs current software, source-bound publication and browser checks from the
selected v0.6 configuration. Native solvers run only when their declared tools
and resources are available. Reports distinguish execution, numerical validity,
engineering screening and physical acceptance. A passed software check is not
physical validation or release.

## Rust design-search footprint

Run `bash tools/automation/check-rust-design-footprint.sh` to check the default
`osr-design-search` dependency graph, release executable and source package.
The default graph must contain no Arrow, Parquet, Polars, DataFusion or GeoArrow
crates. Columnar research tools may use explicit features or separate binaries;
they must not enlarge the default search executable. The check builds with two
Cargo jobs unless `CARGO_BUILD_JOBS` is set, and respects `CARGO_TARGET_DIR`.

The measured 2026-11-16 integrated baseline on current stable Rust 1.100.0
was a 957,760-byte release executable, a 39,512-byte compressed source crate,
and no default columnar dependencies.
CI caps the executable at 2 MiB and the source crate at 256 KiB. These are
regression budgets, not engineering acceptance limits. If a useful change needs
more room, record a fresh measured baseline and review the budget change with
the implementation. The workspace release profile retains overflow checks;
the footprint check does not strip debug symbols or alter optimisation settings.
