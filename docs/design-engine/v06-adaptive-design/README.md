# Function-first adaptive design

The generator seeks a functioning railway under broad service, safety, accessibility, affordability and manufacturing requirements. Initial dimensions, material choices, support arrangements and provisional stiffness targets are hypotheses to investigate. A fixed list of four sill sizes or one global L/500 number is not a universal design space or acceptance rule.

The extensible registry currently declares **102 variables across 14 domains**. Examples are not exhaustive. New descriptors can participate in revision planning without changing its fixed strategy table. A descriptor does not conjure material data or a valid solver; unsupported changes create bounded generator/evaluator/data tasks. The selected v0.6 reference is preserved.

## What the engine changes

| Domain | Registered variables |
|---|---:|
| materials | 9 |
| body | 17 |
| joints | 7 |
| runninggear | 8 |
| propulsion | 14 |
| braking | 4 |
| fitout | 9 |
| services | 5 |
| operations | 10 |
| civil | 6 |
| station | 2 |
| manufacturing | 3 |
| maintenance | 2 |
| model | 6 |

This includes material grades, foam/honeycomb/corrugated cores, cell directions, layups, structural topology, load paths, member proportions, joints and inserts; bogie arrangement and support positions; propulsion topology/windings/fin/gap/inverters; brakes; doors/windows/benches/floors/roofs/HVAC; formation, capacity, speed, spacing, powered zones; civil, stations, manufacturing, maintenance and recovery. Each change declares its interfaces and downstream geometry, mass, loads, heat, controls, service and economic recalculations.

## Different findings require different actions

- A provisional target exceedance prompts criterion justification and diverse physical experiments; it does not reject an architecture.
- A supported functional/physical limit violation prompts a redesign of the mechanism, load path, component or railway arrangement.
- Numerical nonconvergence or a model-domain exceedance prompts model repair or development before interpreting physical performance. Raising the retained linear-steel field bound does not create a nonlinear motor.
- Missing material, interface or installed-equipment evidence prompts targeted measurements/data work.
- Two recorded unsuccessful local changes cause escalation toward untried load paths, material arrangements or system architecture.

[Requirement policy](requirement-policy.json) separates mandatory obligations, preferences, revisable assumptions and numerical domains. Quantitative hard limits require a justified interface/material/function basis. Changing a target alone does not change geometry or establish improvement. Historical results retain their original criteria and identities.

## Executed material-redistribution experiment

The new counted rectangular-tube adapter accepts continuous depth and wall thickness within its declared construction/model domain. Those domain bounds can be extended through explicit geometry and numerical validation; they are not project-wide requirements. The two experiments keep the upper sill datum, support locations, passenger/crowd loads and joint topology while redistributing material. No reference geometry or old solver receipt is edited.

| Section | Accounted tare/car | Change versus previous jointed body | Normal vertical displacement | Mesh trend |
|---|---:|---:|---:|---|
| 180x392.187x4.593mm-generated | 19.054 t | -281.236 kg | 29.529 mm | mesh-trend-confirmed |
| 180x600x4mm-generated | 19.146 t | -188.703 kg | 21.272 mm | mesh-trend-confirmed |

The previous finite-area body accounts for 19.335 t/car and predicts 28.018 mm normal displacement. Its former 25.6 mm comparison is advisory in the new policy, with integrated suitability unknown. Known-stock comparisons are not complete installed mass or a whole-railway optimum.

Normal coarse/fine and crowd cases use the same actual candidate stock and load inventory. The crowd case has one mesh and is not independently mesh-confirmed. Thin-wall buckling, local stress, weld/HAZ and joint fatigue, actual material/bond allowables, flexible modes, dynamic clearances, manufacturing and physical correlation remain necessary work. Less deflection does not close those obligations.

The changed mass propagates into wheel/axle reactions, rotational-mass-aware 1.5/2/3 km required-force/energy profiles and crowd-sized box/twin/U concrete comparisons. These are required forces and preliminary civil quantities; no available nonlinear LIM map, physical journey or installed cost is invented.

## Continue instead of stopping at a failed screen

The campaign saves immutable per-case native results and a pending work frontier. Subsequent run invocations resume unfinished cases and then advance to new definitions, rather than repeatedly selecting the same first two. Focused redistribution and deterministic continuous-domain sampling generate additional exact-stock section proposals; the declared solver domain can be extended with a new validated adapter. Publication uses a zero-new-job budget. A per-invocation job/time budget controls resource use; it does not conclude that no working design exists, discard unfinished work or grant acceptance. Exact physics can be reused under a revised advisory policy when stock, loads, model source, mesh and solver bytes match. Reuse carries an explicit new context without changing the native receipt.

A working solution is not mathematically guaranteed for every combination of requirements. If local revisions do not improve supported margins, the next work changes a family/architecture or establishes missing evaluation capability. The engine never manufactures success by weakening an evidenced safety limit or assigning zero to missing equipment.

```bash
./osr design adaptive plan
./osr design adaptive run --max-jobs 1
./osr design adaptive run
./osr design adaptive publish
./osr design adaptive verify
```

[Summary](summary.json) · [Registry](variables.json) · [Campaign and coupled calculations](campaign.json.gz) · [Next frontier](frontier.json.gz) · [Native evidence](native-index.json) · [Checkpoint/resume](execution-demonstration.json) · [Receipt](manifest.json)

Native input decks, definitions, logs and responses summaries are retained. Large nodal/stress fields remain local or regenerate from their indexed SHA-256 receipts, rather than adding them to ordinary Git history. Physical, requirement, evaluation and selection identities remain separate.
