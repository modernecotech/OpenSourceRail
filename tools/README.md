# OpenSourceRail tools

<!-- osr-system-context:start -->
OpenSourceRail develops simple, affordable, locally maintainable urban transport. The development default is six 17 m comfort cars, each with 44 seats plus two wheelchair places and no planned standing; the 120-second service target gives 8,280 normal passengers/hour/direction. All permanent magnets and suspension controls remain onboard; concrete beams carry passive steel facings, while station windings provide launch and receiving power. Lightweight assemblies, repeated civil works and repairable local production support the low-cost ethos. Stable physical operation and manufacturing release remain open.

[Project introduction](../README.md) · [Engineering approach and current status](../docs/design-engine/current/README.md)
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
