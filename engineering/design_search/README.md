# Coordinated candidate design

OpenSourceRail aims for simple fixed lines, affordable construction and repair,
local production and high passenger throughput. Ferrite support and guidance
remain independently powered while fixed wayside motors propel the train.
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
Bubblewrap, with only its private output writable. The attempt receipt records
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
