# OpenSourceRail development tools

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. Six 17 m comfort cars carry 44 seats plus two wheelchair places/car and no planned standing; the 120-second target gives 8,280 passengers/hour/direction. Passive steel-wheel bogies run on conventional rails carried by precast concrete. Station LIMs act on passive onboard secondaries; there are no traction motors, traction batteries or suspension magnets onboard. Service batteries, independent brakes and the existing station-led GoA4 architecture remain. The reference design is research only; city numerical regeneration, economics and physical release remain open.

[Project introduction](../README.md) · [Engineering approach and current status](../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

The [`./osr` launcher](../osr) is the supported entry point for current v0.6
engineering, planning, delivery and verification workflows. Start with the
[engineering guide](../engineering/station_rail/README.md) and
[current dossier](../docs/design-engine/current/README.md).

| Task | Command | Result |
|---|---|---|
| Inspect selected candidate and open gates | `./osr status` | Candidate identities, publication status and acceptance flags |
| Refresh current engineering records | `./osr build` | Source-bound calculations, dossier, exports and Workbench |
| Verify current records | `./osr verify` | Source and payload identity checks |
| Plan a coordinated candidate study | `./osr design railway plan` | Shared candidate, evaluator dependencies and bounded execution plan |
| Run bounded engineering work | `./osr design railway run --max-bundles 2 --native-jobs 1` | Restartable evaluations; pending and failed tasks remain recorded |
| Publish and verify a study | `./osr design railway publish` / `./osr design railway verify` | Candidate-bound study records and reproducibility checks |
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

## Automation and dependencies

[`automation/default-design.py`](automation/default-design.py) defines the
current design refresh. Shared Python dependencies are pinned in
[`engineering/requirements.txt`](../engineering/requirements.txt). Run repository
commands through `./osr` so the declared project toolchain and environment are
used. Background refresh scripts print proposed service configuration; they do
not install or activate a service.

## Current checks

CI runs current software, source-bound publication and browser checks from the
selected v0.6 configuration. Native solvers run only when their declared tools
and resources are available. Reports distinguish execution, numerical validity,
engineering screening and physical acceptance. A passed software check is not
physical validation or release.
