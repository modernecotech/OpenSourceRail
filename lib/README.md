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
[`cities/catalogue/`](../cities/catalogue/), and the design synthesis crate is
[`crates/osr-design`](../crates/osr-design/).

The shared [`templates/field-evidence.toml`](templates/field-evidence.toml)
drives the pre-mobilisation survey/site brief for any city. Generated briefs
remain unaccepted until the named project authorities approve the requirements
and field deliveries. [`templates/survey-control-processing.toml`](templates/survey-control-processing.toml)
defines the corresponding GNSS receipt roles and provisional RTKLIB screen;
neither automated processing nor a quality code is survey acceptance.
[`templates/ground-model-processing.toml`](templates/ground-model-processing.toml)
then defines the QGIS/ODM/CloudCompare derivative, checkpoint, master-
GeoPackage and authority gates without duplicating raw field data in Git.
[`templates/surveyed-alignment-processing.toml`](templates/surveyed-alignment-processing.toml)
adds the subsequent per-line OSR-ALN, LandXML round-trip, platform/yard/turnout
interface and multi-discipline acceptance contract.
[`templates/route-station-fit-processing.toml`](templates/route-station-fit-processing.toml)
then defines the utility, land, flood, access, integration, road, construction-
logistics, possession, issue-closure and coordinated route-fit contract.
[`templates/drainage-ground-design-processing.toml`](templates/drainage-ground-design-processing.toml)
defines the subsequent SWMM replay, hydrology, geotechnical zoning, foundation/
ground-treatment schedule, conditional OpenGeoSys and authority gate.

Civil cost inputs are split deliberately: edit
[`templates/civil-cost-calibration.toml`](templates/civil-cost-calibration.toml)
and the parametric civil geometry, then run
`python3 tools/automation/generate-civil-cost-model.py`. The generated
[`templates/civil-cost-model.toml`](templates/civil-cost-model.toml) is the
contract used by city synthesis, finance, IFC provenance and documentation.
