# Whole-railway architecture research

OpenSourceRail seeks simple, locally repairable transport at low whole-life cost. This umbrella campaign keeps v0.6 as the selected research reference and challenges its propulsion, speed, formation, powered-track and guideway hypotheses under separately identified configurations. Safety, passenger protection and accessibility remain mandatory holds until supported.

The campaign executes **509 analytical cases**, **174 distinct physical definitions** and **2 generations**. It generates definitions first, checks necessary demand/geometry/recovery bounds, retains explicit failed cases and prepares specialist/native tasks. **No complete architecture is qualified; zero physical station-to-station journeys are claimed.**

| Family | Research arrangement | Cases | Demand target reached* | Off-zone stall* | Numerical/horizon hold |
|---|---|---:|---:|---:|---:|
| P1 | Current station LIM | 20 | 20 | 0 | 0 |
| P2 | Lower-speed station LIM | 38 | 29 | 9 | 0 |
| P3 | Sparse wayside boosters | 119 | 113 | 3 | 3 |
| P4 | Creep/recovery drive | 110 | 92 | 18 | 0 |
| P5 | Distributed wayside propulsion | 56 | 56 | 0 | 0 |
| P6 | Onboard wheel traction | 110 | 110 | 0 | 0 |
| P7 | Alternative passive secondary | 56 | 47 | 9 | 0 |

*These are analytical required-force trajectories at inherited v0.6 comparison mass, not journeys driven by an available motor/brake map. Extra recovery/traction equipment remains unweighed. Invalid calculations and interrupted horizons do not generate physical rankings or geometry revisions.

## What changes and what stays mandatory

The bounded space varies 4/6/8 cars; 1.5/2/3 km station spacing; 43.2/57.6/72 km/h caps; finite station launch/receiving geometry; explicit booster/distributed sections; recovery-driven axles; battery/conductor wheel-traction supply; and box/twin/U guideway sections. The former station-only/no-onboard-traction hypothesis can change inside a research configuration. The selected v0.6 default, seating policy and city geography are preserved.

A synthetic 6 km directional ring keeps route extent explicit. Changing station density changes access service and requires a separate city/demand comparison. Formation/headway is recalculated for 8,280 offered passengers/hour/direction; protected headway remains unknown. Fleet and energy quantities are conditional on required trajectories, not validated operational performance.

Physical, requirement, evaluation, source/tool and selection identities remain separate. The same hardware can appear under different speed requirements. Stator quantity uses the geometric union of installed intervals expanded for the full train/fin envelope, including periodic overlap. Geometric overlap is never multiplied by centred thrust to invent an entry/exit force.

## Foundation checks before full-body and motor ranking

The joint work retains the two-point mechanism and unconverged point-transfer controls. Corrected finite-area fixtures check all six work-conjugate force/moment directions, energy, reciprocity and modes under genuine three-dimensional refinement. Independent review found and corrected a misplaced force reference and duplicate near-identical mesh cuts; previous source-bound failures remain available. Actual joint preload, slip, bearing, fatigue, temperature and measured correlation stay open.

The resulting whole-body alternative counts 40 backing inserts, 240 finite-area bond regions and 160 complete bolt stacks, with floor-lap notches and no positive-volume overlap against retained stock. Its known-stock increase is 113.008 kg/car. The 0.3 m to 0.2 m mesh check changes vertical displacement by 1.43%, lateral by 0.98% and longitudinal by 0.41%. Normal vertical deflection is **28.018 mm**, failing the **25.6 mm** screen despite the confirmed mesh trend. The coarser crowd case is 41.115 mm and is not independently mesh-confirmed. Ideal rigid-section transfer and perfect bonds remain upper-bound hypotheses; local bearing, slip, fatigue, strength, modes and physical joint correlation remain open.

The first finer body solve exhausted its 3 GiB address-space budget. A separately recorded 5 GiB resource revision completed the same physical case without changing geometry, loads or pass limits. Both executions are retained. Numerical confirmation does not make this body structurally acceptable.

The nonlinear magnetic fixture uses a pinned generic reversible 49-point numerical reference, not selected rail steel. A nonzero airgap force is checked independently against a scalar circuit and fixed-current coenergy derivative. Real finite-primary entry/centred/exit linear controls show why overlap needs spatial evaluation. Selected-grade nonlinear moving LIM, finite-height current paths, core losses, inverter control and repeated thermal duty remain separate holds. The old linear-material screen is not relaxed.

See [native evidence index](native-index.json) and [historical producer bytes](historical-source-index.json). Inputs, logs and textual responses are retained; bulky fields are indexed for regeneration. A numerical method pass does not pass M1 physical correlation or qualify the train.

## Cost, construction and assembly

[Civil/construction comparison](civil-construction.json.gz) evaluates 27 crowd-load section/span/formation contexts and preserves moving-load, prestress, deflection and erection quantities. Piers, actual foundations, bearings, lateral/seismic loads, containment, survey, crane radius and priced construction remain incomplete. No beam is selected by concrete quantity alone. Shared-bogie counts expose higher axle-load and new body/articulation requirements without pretending gross bogie-account removal is an installed saving.

Each architecture exposes powered motor/conductor metres, stations, conditional fleet/car/drive counts, platform length and a symbolic installed-cost expression. Unknown equipment, labour, energy tariffs, renewals and recovery disruption remain unknown; no zero-cost winner or complete CAPEX/OPEX comparison is produced.

[Installed assembly contract](assembly-contract.json) requires doors, glazing, benches, HVAC ducts/drains, solar sealing, wiring, bogies and every joint to have geometry, mass, interfaces, installation/removal and QA records. Primary structural joints and removable service-panel clips remain separate roles. New architectures cannot inherit the reference CAD/ERP records as complete assembled products.

## Staged working-system milestones

[Prototype programme](prototype-program.json) defines M1 measured component/joint/brake correlation, M2 repeated passive-carriage launch/coast/stop/fault tests, and M3 full-sized station-to-station pilot/recovery. It requires instrument calibration, raw measurements, uncertainty, specimen identity and independent review. Proposed tests and simulation do not count as completed measurements. No physical milestone is marked complete.

[Campaign cases/results](campaign.json.gz) · [Summary](summary.json) · [Capability registry](capabilities.json) · [Next bounded tasks](next-tasks.json.gz) · [Execution journal](journal.json) · [Interrupted-run receipt](interruption.json) · [Publication receipt](manifest.json)

```bash
./osr design architecture run --max-cases 1  # new-job budget; exit3 if interrupted
./osr design architecture run              # exact-source resume
./osr design architecture publish
./osr design architecture verify
```

Cached jobs bind exact candidate, requirements, numerical settings and source epoch. A source change creates a new contract. Native evaluation requires the capability registry to admit a matching, independently benchmarked model in its declared domain. Unsupported material/topology combinations create implementation or measurement tasks instead of inheriting unrelated results.

## Example architecture trade-offs

Six cars over a 2 km leg within the same 6 km comparison ring, at inherited normal comparison mass. These are representative parameter choices, not optimised or physically validated winners. P2 uses a lower speed requirement; new equipment mass and actual available traction remain unknown.

| Family | Supply / driven axles | Required trip time | Required peak force/car | Linear motor metres/ring | Conductor metres/ring | Conditional purchased cars |
|---|---|---:|---:|---:|---:|---:|
| P1 | auxiliary-only / 0 | 147.4 s | 11.10 kN | 2839.5 | 0 | 36 |
| P2 | auxiliary-only / 0 | 176.5 s | 8.40 kN | 2839.5 | 0 | 42 |
| P3 | auxiliary-only / 0 | 159.3 s | 11.00 kN | 3129.0 | 0 | 36 |
| P4 | separate-recovery-store / 2 | 147.4 s | 11.10 kN | 2839.5 | 0 | 36 |
| P5 | auxiliary-only / 0 | 176.2 s | 10.97 kN | 3418.5 | 0 | 42 |
| P6 | battery / 24 | 141.7 s | 11.10 kN | 0.0 | 0 | 36 |
| P7 | auxiliary-only / 0 | 147.4 s | 11.10 kN | 2839.5 | 0 | 36 |

[Exact cases and requirements](equal_context_comparison.json). Removing linear motor track does not remove battery, conductor, converter, charging, braking, maintenance or recovery costs. The installed price and mass coverage are incomplete for every family.
