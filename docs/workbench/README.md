# OSR Workbench

The Workbench presents City Studio, simulation, OCC replay and Ops Core under
one origin while preserving their authority boundaries. Shared URL context
links the city, immutable revision, approved baseline, simulation run and
selected asset.

Install and launch it through the root [one-command setup](../../README.md#one-command-linux-setup).

Open <http://127.0.0.1:8090/>. Planning and training modes cannot emit live OCC
commands; live mode does not expose design or simulation modules. Actor and
role fields provide navigation context, not authentication. The versioned
contract is [`context-contract.schema.json`](context-contract.schema.json).
Simulator and OCC replays expose deterministic onboard, infrastructure, and
depot-data evidence for the same run; this is software-in-loop, not hardware.
