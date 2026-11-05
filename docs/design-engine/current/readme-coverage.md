# Current README entrypoints

OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. The reference vehicle has six 17 m comfort cars, each with 44 seats and two wheelchair places, no planned standing, and passive steel-wheel bogies on conventional rails carried by concrete. Its passive LIM interface is available for comparison; no installed propulsion architecture or powered length is selected. Acceleration, braking, speed and headway are candidate-specific design variables. The retained 120-second service control gives 8,280 nominal places/hour/direction. The reference vehicle has service batteries and independent brakes, without onboard traction motors, traction batteries or suspension magnets; alternatives must account for their complete system effects. Calculated, priced corridor and city outlines support comparison with explicit assumptions. Engineering verification, prototype validation and manufacturing or operating release remain separate gates.

[Project introduction](../../../README.md) · [System approach](../../../engineering/README.md) · [Current design and engineering gates](README.md)

The **10 maintained v0.6 entrypoints** carry the current project, engineering, deployment and tool context.

| README class | Documents |
|---|---:|
| manual-current-entrypoint | 10 |

Regenerate and check with:

```bash
tools/automation/osr-python -m engineering.readme_context --write
tools/automation/osr-python -m engineering.readme_context --check
```

The write command owns the maintained manual introduction blocks; it does not rewrite generated engineering evidence. Local document titles, technical scopes, licences and all content outside an owned block remain with their existing authors.

| README | Class | Current system context | Existing route |
|---|---|---|---|
| [LICENSES/README.md](../../../LICENSES/README.md) | manual-current-entrypoint | [System approach](../../../engineering/README.md) | [project](../../../README.md) |
| [control-electronics/README.md](../../../control-electronics/README.md) | manual-current-entrypoint | [System approach](../../../engineering/README.md) | [project](../../../README.md) |
| [crates/README.md](../../../crates/README.md) | manual-current-entrypoint | [System approach](../../../engineering/README.md) | [project](../../../README.md) |
| [deployment/README.md](../../../deployment/README.md) | manual-current-entrypoint | [System approach](../../../engineering/README.md) | [project](../../../README.md) |
| [deployment/erpnext/README.md](../../../deployment/erpnext/README.md) | manual-current-entrypoint | [System approach](../../../engineering/README.md) | [project](../../../README.md) |
| [deployment/supervision/README.md](../../../deployment/supervision/README.md) | manual-current-entrypoint | [System approach](../../../engineering/README.md) | [project](../../../README.md) |
| [docs/README.md](../../README.md) | manual-current-entrypoint | [System approach](../../../engineering/README.md) | [project](../../../README.md) |
| [engineering/README.md](../../../engineering/README.md) | manual-current-entrypoint | [System approach](../../../engineering/README.md) | Current system introduction |
| [tools/README.md](../../../tools/README.md) | manual-current-entrypoint | [System approach](../../../engineering/README.md) | [project](../../../README.md) |
| [tools/reference-ma/README.md](../../../tools/reference-ma/README.md) | manual-current-entrypoint | [System approach](../../../engineering/README.md) | [project](../../../README.md) |
