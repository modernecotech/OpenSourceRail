# OSR Workbench

The Workbench presents City Studio, simulation, OCC replay and Ops Core under
one origin while preserving their authority boundaries. Shared URL context
links the city, immutable revision, approved baseline, simulation run and
selected asset.

The **Generate a city digital twin** bar lists all 266 tracked catalogue
cities. One button creates that city's asset register, family-scoped assembly
plan, finite-resource critical path, budget work packages, supplier/order-by
plan, monthly local/imported cash requirements, QA and maintenance records,
then opens the result in Operations. Generation is an allowlisted background
job: the browser cannot supply a command or filesystem path. Output under
`build/workbench/project-twins/` is disposable; reviewed compact baselines stay
with each city under `engineering/project-twin/summary.json`.

![Workbench any-city digital-twin generator](../screenshots/workbench/city-twin-generator.png)

Install and launch it through the root [one-command setup](../../README.md#one-command-linux-setup).

Open <http://127.0.0.1:8090/>. Planning and training modes cannot emit live OCC
commands; live mode does not expose design or simulation modules. Actor and
role fields provide navigation context, not authentication. The versioned
contract is [`context-contract.schema.json`](context-contract.schema.json).
Simulator and OCC replays expose deterministic onboard, infrastructure, and
depot-data evidence for the same run; this is software-in-loop, not hardware.
