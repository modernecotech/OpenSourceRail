# Iterative physical design search

OpenSourceRail develops simple, locally repairable transport and compares complete service consequences. The [v0.6 wheel/LIM campaign](../../campaigns/v06-wheel-lim.toml) now uses this coordinator for generated bodies, station motors, brakes, civil loads and research-twin exports. [Executed generations](../../docs/design-engine/v06-optimisation/README.md) preserve failed and unknown cases, source/tool/dependency identities, failure-driven revisions and explicit next engineering tasks.

```bash
./osr design campaign create campaigns/v06-wheel-lim.toml
./osr design campaign run <campaign-id> [--max-jobs 1]
./osr design campaign compare <campaign-id>
./osr design campaign publish <campaign-id>
```

`wheel_families` owns physical composition; `wheel_evaluators` binds exact upstream evidence; `wheel_body`, `wheel_motor` and `wheel_brakes` generate/evaluate alternatives; `whole_system.evaluate_wheel` couples service and quantities through `wheel_system`; `wheel_twin` regenerates native known stock and delivery drafts. Numerical, design, evidence and system failures remain distinct. Same-model refinement cannot establish independent-domain qualification. Complete installed equipment, costs and physical release remain gated.

The retained carrier/beam campaign below is historical maglev research, with independent family/evaluator IDs. Its numerical results do not describe the wheel-supported v0.6 train.

The separate [practical launch comparison](../../docs/design-engine/practical-launch/README.md)
uses `python -m engineering.design_search.launch_options plan/compare/publish/verify`
for cheap force, travel, contact, storage and service bounds. It does not change
the retained P1–P7 campaign or materialize a revised vehicle from unknown hardware.

**Current propulsion priority:** [passive bogies and short wayside accelerators](../../docs/design-engine/station-accelerators/README.md),
using `python -m engineering.design_search.station_accelerators plan/compare/publish/verify`.
The [priority campaign](../../campaigns/station-accelerator-development.toml) excludes
onboard traction equipment and retains independent services, braking and external
recovery. Earlier [powered-bogie/store comparisons](../../docs/design-engine/propulsion-layout/README.md)
remain secondary reproducible research, not the active vehicle proposal.

The [end-to-end research twin](../../docs/design-engine/digital-twin/README.md)
uses `./osr-twin` to materialize the short-bank configuration across a complete
train/civil stock ledger, federated BOM, propulsion/braking requirements,
construction, controls and cost coverage. It regenerates semantic artifacts and
reopens actual IFC/CAD/STEP; strict engineering completion remains held.
The [current closure](../../docs/design-engine/engineering-closure/README.md) adds
`./osr-complete`, authenticated physical/source records, numerical operating-map
admission, equipment/structural/braking/site/cost evaluation and actual 20 m
field/circuit experiments. New winding candidates propagate through the full
stock/BOM/dead-load/delivery chain without rewriting retained publications.

## Coordinated candidate design

OpenSourceRail aims for simple fixed lines, affordable construction and repair,
local production and high passenger throughput. Passive steel-wheel bogies carry
the current train while fixed wayside motors provide propulsion. Former magnetic
support studies retain their historical configurations and results.
Passengers transfer between fixed lines. This package connects physical design
alternatives and deterministic engineering calculations without granting physical
acceptance.

One versioned candidate describes architecture, native stock, frames, materials,
interfaces and installed equipment. Its physical SHA256 excludes modelling
hypotheses and lineage. Each evaluation has a separate identity covering the
requirements, sources, model hypothesis, settings, mesh, scenario and observed
runtime. A selection has a third identity covering its purpose and declared
policy. Results also carry a complete payload digest, so edited metrics cannot
reuse an evaluation identity.

## Fine-mesh continuation record

The aluminium-frame candidate's normal-load C3D8I refinement is a numerical
follow-up within campaign `6ba19dff09e30606bb4d20ddd153deef033c86ab1d27adc8dab6ad842d68f99f`,
contract `de9f89acc80e0ec2f3ebb8b6c8f60e2446de9df06c66317c5cedc5b8625f8921`,
candidate `8db92b830fda54c81ec231c541f811b24f938f2471b559448d2ed2683754f78b`,
and bundle `1e8d1d7c394fc0bdbd47e34fb21d413ebc34a49576bad60b31b254bd635dfb68`.
The 0.2125 m predecessor completed as evaluation
`da022c36ff3125f5cab90c2f709a2c29e85381e690dbfa082b03deef52f7ad05`.
The 0.10625 m request kept that physical candidate, normal load, element family,
solver and supports fixed. Its first 5 GiB/150 s execution
(`46dac2f71ff6b42ae0715b4219e1789534b0014d8cbae0bdb786bb55112f3b75`,
evaluation `7347006f979dba45aa8958599a49c2ef68ac5a543dc7a5a20a4f6ed6034ddc4d`)
stopped with a Spooles allocation error during matrix factorization. It is a
retained resource failure, not a structural rejection.

A separate one-invocation 8 GiB/240 s resource revision completed in 89.42 s:
request `e8a5a9c6d836cb5f20425a46f04ecac21f107952bec25559e5650e69a865cd7e`,
evaluation `bd0566331853171bac52b8107e075cd4c997526735af7ede9bbcc3fc3ebca9ea`.
The completed run has force, moment and energy residuals of `1.44e-7`,
`4.98e-9` and `6.91e-8`; maximum lateral, longitudinal and vertical
displacements are 1.489 mm, 1.771 mm and 20.139 mm. Across 123,324 matched
physical nodes from 0.2125 m to 0.10625 m, the maximum component differences
relative to the fine-grid component maxima are 15.16% lateral, 6.79%
longitudinal and 3.53% vertical. The trend therefore remains unresolved.
The 150.06 MPa peak is an unqualified ideal-joint stress diagnostic only.

The existing completed solver packet can be sealed and checked without another
solver invocation:

```bash
./osr design railway refine-next-resource-reconcile \
  --parent-result build/coupled-railway/de9f89acc80e0ec2f3ebb8b6c8f60e2446de9df06c66317c5cedc5b8625f8921/result.json \
  --candidate-id 8db92b830fda54c81ec231c541f811b24f938f2471b559448d2ed2683754f78b
./osr design railway refine-next-resource-verify \
  --parent-result build/coupled-railway/de9f89acc80e0ec2f3ebb8b6c8f60e2446de9df06c66317c5cedc5b8625f8921/result.json \
  --candidate-id 8db92b830fda54c81ec231c541f811b24f938f2471b559448d2ed2683754f78b
```

These checks reproduce result metrics and stress from the saved `model.dat`,
compare its FRD mesh with the deterministic mesh definition, and retain the
matched-point comparison source. Numerical completion is not a body
qualification: allowable strength, joints, buckling, fatigue, clearance,
physical correlation and independent review remain open. Neither engineering
nor physical acceptance is granted.

## Run the first campaign

```bash
./osr design campaign create campaigns/carrier-beam.toml
./osr design campaign run <campaign-id> --max-jobs 2
./osr design campaign run <campaign-id>
./osr design campaign compare <campaign-id>
./osr design campaign tasks <campaign-id>
./osr design campaign publish <campaign-id>
./osr twin compile <candidate-id> --campaign <campaign-id> --purpose research --allow-incomplete
```

The first run deliberately pauses after two completed jobs; the second resumes
matching work. Omit `--max-jobs` for an uninterrupted run. State defaults to
`build/design-search`, separate from source checkouts. A source revision creates
a new campaign identity. Exact request matches can reuse cached results; tool
errors and interrupted attempts remain retryable evidence. Job limits and the
total campaign runtime budget are separate from agent conversation limits.

The declared campaign compares rigid existing hardpoints, four yaw carriers and
five yaw/slide carriers with different guidebeam sections and 20/25 m spans.
Failure-directed revisions remain within the declared stock/span bounds. It
retains the six-car Baghdad context, 120 normal passengers per car and a
14,400 passengers/hour/direction comparison floor: 180-second headway. Larger
formations or changed speed/spacing require a separate service comparison with
platform, charging, fleet, evacuation and civil consequences.

## What runs

| Module | Responsibility |
|---|---|
| `contracts.py`, `registry.py` | Physical/context records, typed results, append-only identities and exact cache |
| `families.py` | Counted carrier stock, selected beam/span and bounded revisions |
| `evaluators/` | Definition checks, actual structural/magnetic calculations and explicit coupling hold |
| `geometry.py` | Proper rigid transforms, oriented stock checks and conservative sampled sweeps |
| `coupling.py` | Budgeted fixed-point state/residual iteration with explicit validity failures |
| `campaign.py`, `worker.py` | Dependency dispatch, private runs, resource limits, restart and provenance |
| `verification.py` | Independent stock arithmetic and source checks; no domain-physics confirmation |
| `selection.py` | Separate Pareto rankings for next experiments and integrated baselines |
| `twin.py` | Candidate-bound actual native CAD/STEP, BOM, assembly, IFC and draft delivery records |
| `publication.py` | Portable comparison Workbench, complete retained evidence and integrity check |

The current adapters call the native stock/structure chain and nonlinear magnetic
plant. They do not select using the earlier ideal-force adaptive evaluator.
Cheap definition failures remain visible; independent domain screens can still
run to diagnose which architecture needs revision. Execution, numerical validity,
engineering screen, evidence maturity, selection purpose and physical acceptance
are distinct fields. A completed job may correctly report a failed screen.

Unknown bearings, slides, protection and equipment masses never become zero.
Known stock gives a subtotal; complete mass, CG and inertia remain null when the
installation is incomplete or unlocated. Strict twin compilation refuses these
gaps by default. Explicit `--allow-incomplete` compiles a research package with
those gaps listed. Native CAD contains one module coupon, one selected beam/span
and per-car counted carrier stock in review poses. It does not depict a complete
installed train. Assembly instructions identify unresolved retention, handling
and removal details rather than claim a proven collision-free installation.

The current coupled adapter retains a hold because calibrated temperature,
cooling, deformation and magnetic-gap maps are missing. The generic coupling
solver can converge a supplied component model, but that does not establish a
converged physical train. Arithmetic/source confirmation cannot satisfy the
integrated policy's independent domain requirement. A no-survivor result is a
valid completed campaign.

## Agents and numerical workers

[Project instructions](../../AGENTS.md) and eight role files in `.codex/agents/`
assign systems, magnetics, electrical, mechanical, civil, twin, service and
verification work. Agent tasks carry candidate/requirement identities, allowed
variables, interfaces, evaluators, artifacts and budgets. Ordinary numerical
workers execute parameter samples; agents develop and interpret evaluators.
Source changes use isolated worktrees. Only the coordinator publishes.

Role instructions inherit parent permissions. Where available, the campaign
runs its verifier using a read-only filesystem and isolated network through
Bubblewrap, with its private output and temporary scratch writable. The attempt receipt records
actual isolation. Source and result checks still run if isolation is unavailable;
the receipt does not mislabel that fallback as an enforced sandbox.

## Verification and remaining engineering

```bash
tools/automation/osr-python -m pytest -q engineering/design_search/tests
tools/automation/osr-python -m pytest -q engineering/analysis/tests/test_ferrite_maglev_candidate_structures.py
```

Meaningful regressions cover local prestress stress envelopes, lead times before
first consumption, selected-span quantities, rigid transforms, unknown stock,
identity mixing, result tampering, resume, worker errors and selection policy.
Native integration tests reopen actual FCStd/STEP and parse actual IFC/IDS/BCF.

Next engineering work is independently correlated spatial fields on identical
geometry, complete joint/cooling/protection stock and repair paths, measured
material properties, current/thermal maps, coupled deformation/gap closure and
then full formation/route/fault confirmation. No supplier price, material test,
ground investigation or acceptance is invented by this software. The held
[qualification programme](../../docs/design-engine/ferrite-maglev/qualification/README.md)
continues to control physical dispositions.
