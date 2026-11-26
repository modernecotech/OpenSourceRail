# OpenSourceRail operating rules

Use this file for project-wide engineering, software, evidence and publication
rules. [Governance](GOVERNANCE.md) assigns decisions and release responsibilities.
[Contributing](CONTRIBUTING.md) explains issue and review practice.
[Design decisions](docs/DESIGN-DECISIONS.md) records current choices and why they can
change. The [standards register](docs/certification/README.md) records applicable
evidence and review ownership. Update values and decisions in their own sources.

## Project principles

- Optimise for safe, accessible, affordable whole-life transport and high normal
  passenger throughput. Preserve local manufacture, repairability, vendor choice
  and open engineering knowledge.
- Treat safety, passenger protection and applicable accessibility as obligations
  before comparing cost. Prefer simple, locally maintainable, elevated solutions
  and catenary-free supply where feasible. Apply location-specific requirements
  explicitly, such as zero tunnels for the Baghdad brief.
- Let the corridor, demand and evidence determine train, supply, civil and
  production choices. The v0.6 passive-wheel reference, synthetic corridor and
  Baghdad studies serve different purposes. Each has its own inputs, results
  and evidence. Keep comparative options and their original scope reproducible.

## Standard sequence for a change

1. **Define the decision.** Identify the user, candidate, intended use, affected
   interfaces and sourced requirement. For a correction, capture a reproducible
   example of the original problem before changing the model.
2. **Check the inputs.** Validate geometry, units, identities, scope and simple
   necessary bounds. Record missing survey data, estimates and open decisions at
   their source before running dependent calculations.
3. **Evaluate and propagate.** Change the authoritative input once. Rerun
   dependent outputs and compare credible alternatives on equal service and cost
   scope. Reuse results whose inputs and tools are unchanged.
4. **Review against the original problem.** Exercise the case that exposed it and
   a previously valid case. Retain failed or incomplete results and record their
   causes, affected outputs and evidence needed. Independently confirm a proposed
   engineering selection.
5. **Publish a coherent revision.** Update affected readers and regenerate linked
   records. Record the candidate and evaluation, commands, results, assumptions
   and limits. Verify the published revision against the reviewed changes.

## Requirements and assumptions

- In greenfield network redesign, treat the published routes as a comparison and
  a library of candidate alignments. Include a search that assembles services
  from an empty network. Allow any route, including an orbital, to be removed,
  shortened, replaced or rerouted. Carry forward documented destination access,
  safety, interchange, service and constructability requirements. An existing
  route or station ID needs a separately evidenced constraint to become mandatory.
- Record the source, date or revision, units, applicable candidate, range or
  tolerance, downstream use and evidence maturity for a decision-driving input.
  Keep requirements, project preferences, provisional estimates, supplier data
  and physical measurements distinguishable.
- Treat a trial value as a candidate input. Span, crane capacity, formation and
  headway are examples to reassess. For a lift, use the load chart at the working
  radius and configuration with the actual stock, rigging, clearance and ground
  basis. Record what evidence could change the decision.
- Keep digital calculation validity, functional feasibility, cost comparison,
  production readiness and physical acceptance visible in reports and tools.
  Rank eligible options on equal scope. Carry incomplete options forward for
  research or quotation with their governing limits and outstanding evidence.

## Configuration discipline

- Pass one explicit candidate bundle through geometry, mass, analysis, BOM, CAD,
  BIM, procurement, construction and controls. Reject mixed candidate identities.
- Separate the physical candidate identity, evaluation identity and selection
  identity. A different flux hypothesis is a different evaluation, not a new
  physical geometry. Preserve ancestry and the reasons for each revision.
- Count joints, fasteners, cooling, wiring, protection and maintenance envelopes.
  Unknown installed mass, price, thermal duty or origin remains unknown or bounded;
  it never becomes zero. Derived subtotals are not complete installed quantities.
- Preserve the project's wider front-door explanation when revising the vehicle:
  local design/manufacturing/repair capability, three connected products, delivery
  lifecycle, ERPNext/Frappe HR, FUXA/gateway, city planning, contributions and
  licensing. Keep current, retained and disconnected capabilities explicit, with
  exact historical links. A hardware revision must not turn the README into only
  a campaign log or silently discard the rest of the platform's purpose.
- Keep the front README's Hayder Aziz attribution, About the author section,
  research citations and contributor credit when reorganising the introduction.
- The repository development default is engineering/development-baseline.toml:
  six 17 m cars, 44 fixed seats plus two wheelchair places/car, no planned standing,
  two doors on one side. The 120-second/8,280 normal passengers/hour/direction
  case is a named reference control. The retained-stop network proposal uses a
  72 km/h launch cap.
  Version 0.6 uses passive wheel bogies on conventional rails carried by concrete.
  The reference vehicle retains its passive aluminium secondary interface; this
  does not select an installed propulsion system. Architecture, powered length,
  acceleration, braking and headway must be selected per candidate against demand,
  physical constraints and whole-life cost. Treat 900 m and 100 m powered
  lengths as hypotheses. The reference vehicle has no onboard traction motors, traction
  batteries or permanent magnets; independently sized service batteries, braking and rescue remain.
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

## Railway and delivery interfaces

| Area | What to check and carry forward |
|---|---|
| Route and passenger service | Check ordered stops against mapped distances and identify survey and grade gaps. Verify a connected route, dwell, headways, junctions, turnbacks, depot moves and fleet reserve. Label observed demand, inferred demand and allowances. Price reserved guideway and unproven services explicitly. |
| Vehicle, power and controls | Carry installed mass, unequal axle loads, clearance, normal and degraded stopping, traction duty, heat, auxiliary energy, protection and recovery into the corresponding simulations. Test loss of or stale feedback and the door, brake and traction handover. Keep simulation, supervision, business approval and movement authority distinct. |
| Civil works and construction | Size each span and support family for its own load cases, ground, bearings, access and maintenance. Check temporary works, loaded transport, erection and traffic or night windows as well as passenger loading. Derive yard size and throughput from mould occupancy, release, buffer, handling, staffing and access. Price special bays, starter works, closure and fallback separately when they differ. |
| CAD, CAM and factory | Match controlled drawings, installed or bounded mass, quantities, BOM, workholding, process route and inspection to the same revision. Reconcile material, tooling, machine capacity, labour, yield and rework. Establish the actual machine, controller, post, tooling and collision checks before releasing a production job. Keep training jobs and ERP drafts identifiable. |
| Offers, lifecycle costs and cash | Ask suppliers for matched quantities, inclusions, currency and price date, lead times, exclusions, origin and maintenance. Replace an allowance once and identify labour, plant or tooling already priced elsewhere. Distinguish illustrative low/base/high ranges from calibrated probabilities. Propagate scope changes through installed cost, operations, renewals and phased cash. Declare any inherited schedules or allowances. |
| Evidence and handover | Use the standards crosswalk and project-specific acceptance criteria to link requirements, hazards, models, tests, supplier evidence, decisions and responsible reviewers. Maintain part and asset identity from quotation through as-built records, inspection, repair and return to service. |

## Repository workflow and readers

- Work in the existing OpenSourceRail repository on `main`. Keep city designs in
  their city folders and shared railway designs in the project’s engineering
  folders. Use the existing ignored build directory for temporary outputs.
- Check the intended changes, preserve unrelated local edits, integrate with
  GitHub `main` and verify the published commit. Incorporate concurrent changes
  before pushing. Keep one working checkout and one delivery branch.
- Write for the people planning routes, building trains and stations, purchasing
  equipment, running the service and maintaining it. Lead with the design,
  quantities, costs, operating consequences and work still needed. Keep solver
  settings, commands and run records in the supporting engineering material.
- Keep source data, generated results and historical archives distinct. Keep the
  README, Workbench and release notes aligned with the current source. Point to
  exact archived revisions for retained studies. Name the historical case when
  reusing its chart, price or result.
- Use existing modules, commands and dependency-aware publication paths where
  they satisfy the work. Bound new calculations and storage, preserve useful logs
  and leave unrelated city catalogues and historical packets outside routine rebuilds.

## Coordinated work

- Use specialist agents for bounded engineering questions and evaluator work;
  use deterministic numerical workers for parameter samples. Each assignment
  identifies its candidate, requirements, allowed variables, fixed interfaces,
  required artifacts, trial/runtime/resource budgets and completion conditions.
- Admit projected writes for tool installation and
  publication through the shared Git-common-dir disk reservation before they
  start. Monitor the target filesystem during long jobs and stop at the 20 GiB
  free-space floor; a one-time `df` check is insufficient.
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

## Verification and release

- Run the affected unit, integration and generator checks. For a changed current
  source-bound publication, run `./osr build` and verify the resulting packet.
  Check changed Markdown, links and the rendered reader where applicable.
  `./osr book --check` checks the book. Use `./osr test` for the broader current
  software, engineering and browser checks when verifying a release.
- State the exact scope tested and the unresolved work. A digital platform release,
  a budgetary enquiry, a controlled fabrication package and permission to operate
  each require their own evidence. Use the existing release workflow and
  [roadmap](docs/ROADMAP.md) for milestones. Confirm the published commit and
  the affected assets after an authorised push.

Current engineering: `docs/design-engine/current/README.md`; current adapters:
`engineering/development_baseline/`. Historical evidence is pinned by
`docs/archives/pre-comfort-default/manifest.json`; use the pinned archives for historical reproduction. Candidate campaigns:
`engineering/design_search/`. Project role files follow the
[official Codex agent schema](https://learn.chatgpt.com/docs/agent-configuration/subagents).
