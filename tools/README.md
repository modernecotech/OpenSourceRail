# OpenSourceRail tools

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. Six 17 m comfort cars carry 44 seats plus two wheelchair places/car and no planned standing; the 120-second target gives 8,280 passengers/hour/direction. Passive steel-wheel bogies run on conventional rails carried by precast concrete. Station LIMs act on passive onboard secondaries; there are no traction motors, traction batteries or suspension magnets onboard. Service batteries, independent brakes and the existing station-led GoA4 architecture remain. The reference design is research only; city numerical regeneration, economics and physical release remain open. Maglev documents below are retained historical research, not the selected v0.6 physical design.

[Project introduction](../README.md) · [Engineering approach and current status](../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

Start with the [project launcher](../osr) and [current engineering workflow](../engineering/station_rail/README.md).

| Workflow | Command | Purpose |
|---|---|---|
| Rebuild current evidence | `./osr build` | Rebuild stale prerequisites and publish source-bound studies |
| Inspect current studies | `./osr design status` | Show architecture, requirements, responsibilities and open gates |
| Inspect city readiness | `./osr city baghdad` | Report retained geography and the v0.6 performance-evaluation hold |
| Inspect the journey hold | `./osr sim baghdad` | Report missing current physical inputs; never replay old results as v0.6 |
| Plan coordinated research | `./osr design railway plan` | Show the shared candidate, evaluator dependencies and execution budgets |
| Run bounded research | `./osr design railway run --max-bundles 2 --native-jobs 1` | Resume engineering/manufacturing evaluation and pending tasks |
| Verify coordinated evidence | `./osr design railway verify` | Check exact candidate, source, native and publication identities |
| Open design UI | `./osr workbench` | Inspect city plans, native geometry and provisional cost scope |
| Verify | `./osr test` | Run current Rust, Python, publication and browser checks |
| Reproduce historical alternatives | `bash tools/automation/test-maglev-research.sh` in the pinned historical checkout | Retain the original magnetic method, source and publication contracts |
| Refresh in background | `./osr design install` | Install the user-local source-change build timer |

[Automation scripts](automation/) provide the current pipeline. The generic
[movement-authority reference utility](reference-ma/README.md) remains a separate
development helper; it does not qualify control hardware or railway operation.
