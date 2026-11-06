# Demand-led railway outlines

The Workbench can now finish a **provisional outline study** from a passenger-service brief. Headway, speed, acceleration and dwell are design variables. The 120-second development reference remains a named comparison, rather than a universal operating requirement.

Open the local Workbench with `./osr workbench`, enter the route, stations, peak directional demand, occupancy and journey limit, then generate and compare outlines. Inspect an outline to see its assumptions and next engineering tasks, or download its complete cost ledger and evidence record. No business-system transaction or hardware selection occurs.

## What the current implementation completes

1. Creates a requirements identity from the demand and service brief.
2. Adds a demand-derived headway to the supplied service hypotheses.
3. Screens conditional journeys, capacity, fleet, auxiliary charging, launch reset and terminal resource bounds. Rejected and deferred cases remain in the study.
4. Recalculates rolling stock, civil quantities, stations, launch power, factory/tooling, construction, depot, operating labour, energy, maintenance and renewals across all 14 cost scopes.
5. Retains the lowest central whole-life estimate for each of three launch concepts: cable/capstan, common-drive rollers and compact LIM. Every priced case remains in the compact cost index.
6. Assigns outline maturity using explicit geometry envelopes, bounded mass, calculated costs, provisional production routes and assumptions.
7. Exports an immutable study with requirements, source identities, assumptions, manufacturing/resource quantities and subsequent verification tasks.

The current formation is six 17 m cars with 276 normal places and no planned standing. Other formations, running gear, arbitrary organic geometry and propulsion architectures still need their own adapters and complete system consequences. Example parameter lists and the bounded 128-screen invocation budget do not define the complete permissible design space.

The [transport-goal policy](../../../engineering/outline/transport-goal.toml) keeps the approach space open. Onboard or distributed propulsion, shorter/articulated vehicles, different running gear, guideways, surface/elevated/mixed alignments and other public-transport comparators may be proposed. New names do not fail a technology whitelist: `engineering.outline.approaches.propose` accepts defined ideas for research and creates their explicit model/input tasks. Missing adapters mean **not yet assessed**, rather than physically infeasible. Comparisons must share passenger-service and geographic-access requirements and cover complete installed and whole-life consequences; reference quantities and evidence do not transfer automatically. “Best” applies only within the declared evaluated scope.

Inspect this non-exhaustive catalogue with `.venv/bin/python -m engineering.outline approaches` or the Workbench's open-approach link. These are proposal-intake capabilities; the current numerical cost calculator still evaluates its three declared station-launch methods around the six-car reference and 20 m box-beam module. The policy links the existing requirement, design-variable, architecture, capability-admission and revision-task frameworks; their wider research remains available without rewriting earlier bounded campaigns.

## A completed planning example

The [reproducible inputs](inputs.json) declare 30 route-km, 12 uniformly spaced stations including terminals, 4,000 peak passengers/hour/direction, 85% occupancy, a 45-minute journey limit, a maximum 300-second headway and an **assumed**, unmeasured 99% service availability. The line is level and fully elevated. Production and construction use two shifts; operating hours can be 18 in two shifts or 24 in three shifts.

The current publication screened 72 service cases and produced 48 complete cost cases, with 0 native solver jobs. Source-bound summaries are in [summary.json](summary.json); source and artifact bindings are in [manifest.json](manifest.json). Runtime measurements belong to private execution records and are not universal throughput claims.

| Retained launch concept | Headway | Speed cap | Acceleration | Fleet including reserves | Central installed cost | Central cost / route-km |
| --- | --- | --- | --- | --- | --- | --- |
| Cable / capstan | 200 s | 72 km/h | 0.8 m/s² | 32 trains | US$450.8m | US$15.03m |
| Common-drive rollers | 200 s | 72 km/h | 0.8 m/s² | 32 trains | US$458.8m | US$15.29m |
| Compact LIM | 200 s | 72 km/h | 0.8 m/s² | 32 trains | US$494.7m | US$16.49m |

These are **Class C engineering estimates** using the [project-volume purchasing and manufacturing policy](../supply-economics/README.md). The cable outline takes approximately 41.93 minutes one way. Installed low/base/high costs are US$144.7m / US$450.8m / US$1,945.4m; central 30-year NPV is US$996.3m. These are sensitivity cases, not confidence limits or supplier offers.

The original generic-rate benchmark remains US$738.0m / US$24.6m per route-km with 52 trains and a 120-second headway for 8,280 nominal places/hour/direction. The updated supply comparison reprices that same service. This demand example has different requirements; compare pricing scenarios at equal service, and service choices under the same pricing basis. The Workbench retains all three selectable pricing bases.

## Progressive acceptance

An **accepted outline** is a successful design-stage result for comparison and further detailing. It can use explicit bounded assumptions, internally calculated prices and provisional manufacturing routes. A missing supplier quote or prototype test does not by itself reject the outline.

Execution status, numerical validity, outline acceptance, analytical screening, detailed engineering, prototype validation, manufacturing release and operating release remain separate. A supported physical contradiction requires revision. An unsupported model result or missing later-stage evidence creates an evidence task. Unknown mass or cost never becomes zero.

The current launch packages calculate required force and equipment capacity. They do not establish available thrust, coupling integrity, repeated thermal duty, independent stopping, safe separation, conflict-free turnback, complete installed mass/CG, structural/fire performance or physical accessibility acceptance. Mass bounds vary the residual accounts; service and cost comparisons use the stated nominal mass. Independent qualification remains governed by the existing evidence workflow.

## Reference intelligence and reverse engineering

Three linked libraries hold functional patterns, physical solutions and production methods. Each record retains source bytes or hashes, units, uncertainty, rights declarations, interfaces, assumptions and remaining evidence work. Unknown permitted use can be stored for review but cannot become implementation-reusable evidence.

The owned-source pilot actually exercises three offline ERP draft behavior fixtures: disabled draft generation, active-item refusal and mixed-candidate refusal. It also records a source-inspected Rust protocol pattern and reconstructs a bounded, owned 12-triangle plate fixture after manifold, orientation and volume checks. These are software/geometry checks, not observations of railway hardware.

The optional [REA](https://github.com/morluto/rea) adapter prepares bounded authorized inspection tasks and imports normalized observations. **REA is not installed or executed by this workflow.** Complete source uses ordinary source analysis; upstream permission claims require a separate operator declaration before reuse. Physical reconstruction recipes distinguish [Open3D](https://www.open3d.org/docs/latest/), [nickpagz/stl2step](https://github.com/nickpagz/stl2step) and other similarly named tools. Plans do not execute arbitrary commands, and the limited plate reconstruction does not claim general organic CAD recovery.

## Reproduce and verify

From the repository root:

```sh
.venv/bin/python -m engineering.outline run \
  --brief docs/design-engine/demand-outline/inputs.json \
  --output build/my-demand-outline
.venv/bin/python -m engineering.outline verify --output build/my-demand-outline
```

Use a fresh output directory. Verification replays the calculation and compares canonical outputs. Full reproducible runs remain outside Git; the repository retains compact inputs, summaries and hashes. Numerical or hardware approval is never inferred from an outline manifest.
