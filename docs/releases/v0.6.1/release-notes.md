# v0.6.1 — Open Engineering Platform

v0.6.1 is the first packaged Open Engineering Platform release in the v0.6 series.

## Included

OpenSourceRail connects city planning and service design, railway engineering, and manufacturing/delivery and maintenance tools. The platform is built around affordable whole-life transport, local design and manufacture, repairability and open design knowledge.

- **City planning catalogue:** mapped outlines for **266 cities and 1,565 lines**, with route and station information, service assumptions, energy and cost scenarios, funding context and local-evidence records. Original, straighter and ring-layout proposals provide starting points for comparison. See the [city catalogue](https://github.com/modernecotech/OpenSourceRail/blob/v0.6.1/cities/catalogue/README.md).

- **Editable Workbench journeys:** load a city network, inspect and change planning/service inputs, calculate fleet, energy assumptions and costs, follow job status, and export results and delivery drafts. Samawah includes fresh, unchanged-cache and changed-demand demonstrations; Baghdad provides a retained route/service/cost comparison.

- **Design generation and comparison:** coordinated railway candidate bundles, architecture searches, adaptive design and generative structural experiments. The outline catalogue covers **112 railway bundles, 54 vehicle bodies and 18 civil spans**. Physical candidate, evaluation and selection identities keep alternative configurations and their evidence traceable. See the [design workflow](https://github.com/modernecotech/OpenSourceRail/blob/v0.6.1/docs/design-engine/coupled-railway/README.md).

- **Reference railway and alternative research:** definitions for the six-car, 17 m comfort-car reference with passive wheel bogies, conventional rails and concrete support, alongside separately identified propulsion, braking, station-energy-recovery and powered-wheel research configurations. The [capability register](https://github.com/modernecotech/OpenSourceRail/blob/v0.6.1/docs/capabilities/README.md) connects the reference, reconciled pilot and no-store comparisons.

- **Service and whole-life economics:** journey, headway, capacity, fleet and energy calculations connected to **fourteen cost scopes**, with low/base/high scenarios. Cost and delivery models cover vehicle and civil quantities, factories and tooling, procurement, construction, staffing, energy, maintenance, renewal, reliability and disposal. Assumptions, sources and uncertainty travel with the results.

- **CAD, BIM and engineering models:** source-linked vehicle, bogie, seating, door, coupling, launch-shuttle and guideway studies; rotatable STL/GLB views and editable STEP/FreeCAD assets. Optional native-tool workflows and recorded comparisons include SolidCraft, FieldCraft, FreeCAD and CalculiX. Browse the [3D engineering gallery](https://github.com/modernecotech/OpenSourceRail/blob/v0.6.1/docs/engineering-models/README.md).

- **Manufacturing and delivery definitions:** vehicle parts catalogues, materials and quantities, BOMs, fabrication and assembly routes, tooling concepts, inspection characteristics, procurement records, construction and repair planning. Candidate-linked exports connect geometry and engineering revisions with process-hour and cost estimates. See the [platform guide](https://github.com/modernecotech/OpenSourceRail/blob/v0.6.1/docs/platform-guide.md).

- **Business and workforce integration:** optional [ERPNext and Frappe HR](https://github.com/modernecotech/OpenSourceRail/blob/v0.6.1/deployment/erpnext/README.md) deployment recipes and adapters for project, purchasing, stock, workforce, manufacturing, quality, serialized equipment and maintenance workflows, with reviewable draft handoffs and disposable integration scenarios.

- **Control, supervision and equipment observation:** GoA4 control research in Rust, including train protection, interlocking, doors, train control and station SCADA contracts. Optional [FUXA and gateway](https://github.com/modernecotech/OpenSourceRail/blob/v0.6.1/deployment/supervision/README.md) integrations provide observations, trends, alarms and maintenance/lifecycle handoffs. Deterministic simulations and refusal checks accompany the software.

- **Reproducibility and efficient processing:** verified result reuse, selected-city source collection, indexed city-cache hints, incremental integrity checks, bounded streaming archives and optional Rust canonical encoding. Worker/resource limits, disk admission, performance measurement, storage inventory and conservative cleanup commands support local execution.

- **Documentation and release evidence:** the platform/adoption guides, illustrated reader, engineering galleries, source manifests, retained research archives, contribution and licensing guidance, plus the versioned installation guide, software test evidence, complete Samawah demonstration exports and download checksums attached to this release.

## Installation

Use the attached **INSTALL-v0.6.1.md** to install the versioned source and run the Workbench. Verify downloads with **SHA256SUMS**.

Frozen source: `5cfe89488a64549b37d4a7fd3ea9e3d3a8923aea`

## Verification

- [Python release lane](https://github.com/modernecotech/OpenSourceRail/actions/runs/43176691666): 228 tests passed.
- [Rust control contracts](https://github.com/modernecotech/OpenSourceRail/actions/runs/43176691677): passed.
- [Workbench/Samawah](https://github.com/modernecotech/OpenSourceRail/actions/runs/43176691729): frontend checks and two complete journeys passed.

The software evidence ZIP contains the recorded checks and documentation inputs. The journey ZIP contains the complete demonstration exports.

See the [feature maturity table](https://github.com/modernecotech/OpenSourceRail/blob/v0.6.1/docs/releases/v0.6.1/feature-maturity.md) and [known limitations](https://github.com/modernecotech/OpenSourceRail/blob/v0.6.1/docs/releases/v0.6.1/known-limitations.md) for supported workflows and current holds.
