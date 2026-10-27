# OpenSourceRail engineering work

Develop affordable whole-life transport and high normal passenger throughput,
using simple station-powered wheel-supported vehicles as the v0.6 reference.
Preserve local manufacture, repairability and open design knowledge. Explicit
research configurations may challenge propulsion distribution, onboard traction,
formation, bogies, speed, station spacing and civil sections. Mandatory safety,
passenger protection and accessibility are never financial trade-offs. Research
alternatives do not silently change the selected reference or inherit its results.

## Configuration discipline

- Pass one explicit candidate bundle through geometry, mass, analysis, BOM, CAD,
  BIM, procurement, construction and controls. Reject mixed candidate identities.
- Separate the physical candidate identity, evaluation identity and selection
  identity. A different flux hypothesis is a different evaluation, not a new
  physical geometry. Preserve ancestry and the reasons for each revision.
- Count joints, fasteners, cooling, wiring, protection and maintenance envelopes.
  Unknown installed mass, price, thermal duty or origin remains unknown or bounded;
  it never becomes zero. Derived subtotals are not complete installed quantities.
- The repository development default is engineering/development-baseline.toml:
  six 17 m cars, 44 fixed seats plus two wheelchair places/car, no planned standing,
  two doors on one side and a 120-second target (8,280 normal passengers/hour/
  direction). The retained-stop network proposal uses a 72 km/h launch cap.
  Version 0.6 uses passive wheel bogies on conventional rails carried by concrete.
  Station double-sided linear-induction motors act on passive onboard aluminium
  secondaries. Onboard traction motors, traction batteries and permanent magnets
  are absent; independently sized service batteries, braking and rescue remain.
  The former PM-assisted maglev is retained historical research. Development
  selection is not physical acceptance.
- The umbrella research campaign is campaigns/whole-railway-architecture-search.toml.
  It separates mandatory requirements, project preferences and revisable design
  hypotheses. An onboard recovery or wheel-traction comparison is permitted only
  under a new research configuration with its mass, energy, running gear,
  protection, recovery, manufacturing and whole-system consequences explicit.
  Capability declarations, test plans and software tests never become measured
  physical evidence or automatic native-evaluator admission.
- Preserve the former 120-person/14,400 capacity comparison and 160-person crowd
  structural control as explicitly named alternatives; seating policy does not
  remove applicable crowd, evacuation or accidental-load verification. Different
  formations require their complete platform, civil, fleet and service effects.

## Coordinated work

- Use specialist agents for bounded engineering questions and evaluator work;
  use deterministic numerical workers for parameter samples. Each assignment
  identifies its candidate, requirements, allowed variables, fixed interfaces,
  required artifacts, trial/runtime/resource budgets and completion conditions.
- Use isolated Git worktrees for source development. Use private candidate/run
  directories for numerical work; do not create a checkout for every sample.
- Keep source edits and numerical execution separate. Workers return immutable
  input/output/log packages; the coordinator alone integrates and publishes.
- Resolve cheap definition and necessary-bound failures before expensive solves.
  Preserve failed, nonconverged, interrupted and out-of-domain executions.
- Independently confirm a proposed selection. Keep next-experiment ranking
  separate from integrated-baseline ranking and retain Pareto alternatives.
- Custom agent instructions inherit parent permissions. A read-only instruction
  is not an OS sandbox. Report actual verifier isolation and integrity checks;
  never claim enforcement that the execution environment does not provide.

## Evidence and completion

- Track execution, numerical validity, engineering screen, evidence maturity,
  selection purpose and physical acceptance separately. A completed calculation
  can fail its engineering screen without losing its useful digital evidence.
- Couple mass, force, current, heat, cooling, deformation and clearances with explicit
  residuals and budgets. Numerical convergence alone does not establish feasibility.
- Use engineering/design_search/requirement_policy.py to distinguish supported
  obligations from advisory targets, revisable hypotheses and model domains.
  A provisional L/500 comparison is not a universal body rejection rule. Derive
  quantitative functional limits from actual interfaces, loads and evidence.
- Use campaigns/adaptive-railway-design.toml and `./osr design adaptive` for
  ongoing function-first design. Earlier bounded wheel/LIM campaigns retain
  their original parameter/screening contracts for historical reproduction;
  do not let those contracts define the complete current search space.
- Extend design_variables.py across materials, cores, load paths, joints, fitout,
  running gear, propulsion, service, civil and manufacturing as needed. Example
  values and current solver construction bounds are not the complete design
  space. Repeated unsuccessful local changes should trigger a new family or
  evaluator/measurement task. Preserve pending work across invocation budgets;
  never claim a working solution by weakening an evidenced obligation.
- Use `./osr design generative` for the composable structural-grammar experiment.
  Preserve its physical graph, stock, typed interfaces, assembly and same-candidate
  propagation. Pin-graph mechanisms diagnose only the declared axial load path;
  they do not invalidate a bonded shell or rigid frame without its own evaluator.
  Gross untrimmed stock, declared manufacturing groups and CAD volume agreement
  are not complete installed mass, manufacturability or body qualification.
- Start coordinated work with `./osr design railway` and
  campaigns/coupled-railway-design.toml. Keep standalone architecture/adaptive/
  generative experiments reproducible. A physical revision must propagate through
  one canonical bundle to inventory, interfaces, propulsion, braking, civil and
  manufacturing/economics; new upstream evidence invalidates dependent caches.
  Native reuse requires the exact source, tool, candidate, load, mesh and resource
  request. Numerical budget revisions do not change engineering obligations.
  Continue unresolved refinement or unsupported-model work in the frontier;
  balanced forces/energy and CAD/IFC volume agreement do not qualify a body.
- Preserve historical source-bound archives. Regenerate affected current packets
  with their generators after changing implementation inputs; record a hold when
  dependencies or physical measurements are unavailable. Do not edit receipts to
  conceal stale sources or turn synthetic evidence into physical qualification.
- Physical requirements stay open until the existing qualification workflow has
  appropriate authenticated measurements, approved limits and independent review.
- Run meaningful regression and integration checks for the changed behavior.
  Document exact commands, bounded campaign results, limitations and artifact IDs.
- Preserve unrelated user edits, including local editor settings. Commit and
  update main only within the user's authorized scope; never force-push around a
  conflicting update or publish an automatically accepted physical design.

Current engineering: `docs/design-engine/current/README.md`; current adapters:
`engineering/development_baseline/`. Historical evidence is pinned by
`docs/archives/pre-comfort-default/manifest.json`; regenerate historical methods
only in an isolated checkout. Candidate campaigns:
`engineering/design_search/`. Project role files follow the
[official Codex agent schema](https://learn.chatgpt.com/docs/agent-configuration/subagents).
