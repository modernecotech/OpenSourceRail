# Machine-Readable Inputs

The `lib/` tree holds the data that drives generated city designs,
simulator examples, and reusable planning assumptions. These files are
intended to be edited, reviewed, and versioned alongside the code.

## Contents

| Folder | Purpose |
|---|---|
| [`templates/`](templates/) | Shared TOML assumptions for rolling stock, stations, track geometry, signalling, demand, costs, finance, climate, and regulatory context |
| [`city-batches/`](city-batches/) | Batch lists for generated city catalogues, including the world sample and calibration set |
| [`recipes/`](recipes/) | End-to-end recipe inputs that combine templates into deployment designs |
| [`examples/`](examples/) | Small hand-authored simulator/design examples |
| [`fault-injection-scenarios/`](fault-injection-scenarios/) | Scenario files for degraded-mode and safety-path demonstrations |

The generated outputs from these inputs live under
[`designs/`](../designs/), and the design synthesis crate is
[`crates/osr-design`](../crates/osr-design/).

Civil cost inputs are split deliberately: edit
[`templates/civil-cost-calibration.toml`](templates/civil-cost-calibration.toml)
and the parametric civil geometry, then run
`python3 scripts/generate-civil-cost-model.py`. The generated
[`templates/civil-cost-model.toml`](templates/civil-cost-model.toml) is the
contract used by city synthesis, finance, IFC provenance and documentation.
