# OpenSourceRail tools

<!-- osr-system-context:start -->
OpenSourceRail develops an open, locally buildable urban railway with fixed linear motors at stations and, where needed, located boosters. Trains coast between powered zones while onboard ferrite support, guidance and passenger services remain independently powered; passengers transfer between fixed lines at junctions. Simple vehicles, repeated civil works and repairable local production aim for high useful passenger throughput and affordable construction, operation and debt repayment. Current studies and digital workflows support development; an accepted physical railway has not been established.

[Project introduction](../README.md) · [Engineering approach and current status](../engineering/ferrite_maglev/README.md)
<!-- osr-system-context:end -->

Start with the [project launcher](../osr) and [current engineering workflow](../engineering/ferrite_maglev/README.md).

| Workflow | Command | Purpose |
|---|---|---|
| Rebuild current evidence | `./osr build` | Rebuild stale prerequisites and publish source-bound studies |
| Inspect current studies | `./osr design status` | Show architecture, requirements, responsibilities and open gates |
| Regenerate a city | `./osr city baghdad` | Compile formations, quantities, partial costs and manufacturing routes |
| Replay city charging | `./osr sim baghdad --cycles 2` | Test the compiled offline energy ledger |
| Open design UI | `./osr workbench` | Inspect city plans, native geometry and provisional cost scope |
| Verify | `./osr test` | Run current Rust, Python, publication and browser checks |
| Verify design alternatives | `bash tools/automation/test-maglev-research.sh` | Check research simulations, exact mass/source bindings and README context coverage |
| Refresh in background | `./osr design install` | Install the user-local source-change build timer |

[Automation scripts](automation/) provide the current pipeline. The generic
[movement-authority reference utility](reference-ma/README.md) remains a separate
development helper; it does not qualify control hardware or railway operation.
