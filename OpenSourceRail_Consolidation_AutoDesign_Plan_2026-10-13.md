# OpenSourceRail: repository consolidation, auto-design and verification plan

Review date: 13 October 2026. Reviewed revision: **ace7e0b4ddb2754fb9ddd89860534cefb7a71c27**.

Repository: [modernecotech/OpenSourceRail](https://github.com/modernecotech/OpenSourceRail/tree/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27).

## Decision

Preserve the project's breadth and independent railway-control boundaries. Consolidate shared contracts, orchestration, evidence, navigation and documentation. Extend the existing engineering solvers through a common auto-design workflow rather than create another disconnected search application.

The repository is a substantial research, planning and integration platform. Its next improvement should be a coherent product that a planner, engineer, workshop or operator can navigate and reproduce. A numerical result, artifact checksum, successful application transaction and engineering acceptance remain different facts.

This is a repository-wide architectural and functional review, with representative code inspection and verification. It covers all top-level functional domains, current Actions results, frontend sources and retained screenshots. It is not a line-by-line audit of 35,347 files, a fresh execution of every native solver or an independent physical/design acceptance. The city checkout used for local checks contains Baghdad, Samawah and Mosul; catalogue-wide conclusions use tracked inventory, canonical generators and published CI, not a claimed rerun of all 266 cities. No repository implementation or operational records were changed during this review.

## 1. Current state and evidence

### Repository shape

| Measure | Count at reviewed revision | Implication |
|---|---:|---|
| Tracked files | 35,347 | Separate source, review snapshots and bulk evidence in navigation and tooling. |
| Files beneath cities | 31,416 | Approximately 89% of tracked paths; optimise catalogue regeneration and artifact handling before blaming software modularity. |
| Rust workspace crates | 60 | Preserve useful domain and control boundaries; consolidate repeated helpers and deployment metadata. |
| Python files | 839 | Includes tests and generation; establish clear packages and dependency profiles. |
| Top-level Python automation scripts | 192 | Keep existing launchers compatible while moving substantive logic into reusable modules. |
| Markdown files | 6,211 | Much is generated/local evidence; a searchable inventory is not a reading journey. |
| Workbench navigation entries | 25 | Progressive disclosure and task grouping are preferable to removing functions. |
| GitHub workflow files | 14 | Share job definitions and dependency selection; preserve independent acceptance scopes. |
| Root README lines | 219 | Already substantially consolidated; improve its journeys and freshness, not add another long front page. |

Large source modules include buildable_trainset.py (5,884 lines), civil_bonsai_ifc.py (5,558), City Studio project.rs (4,924), network_readme.py (3,998), simulator sim.rs (3,190), City Studio app.js (2,607) and Operations Portal app.js (1,804). Size alone is not a defect. Their mixed responsibilities make targeted extraction worthwhile.

### Verification performed

| Evidence | Result and interpretation |
|---|---|
| Initial selected mechanical, engineering, panel and integration suites | 145 passed; one test could not execute because OpenSeesPy was initially absent. |
| Selected operations, field intake, Workbench, dependency, recovery and identity suites | 86 passed. Native ERP intake tests include controlled doubles; this is not a fresh deployed ERP acceptance. |
| Focused design-consistency and panel-response rerun | 26 passed; these overlap the initial suite and are not added again to the unique total. |
| Frontend Node unit suite | 14 passed. |
| Composite-panel publication reproduction | Passed; 2,592 conditional variants reproduced. |
| Published best-practice design twin | Passed against the current compiler. |
| Additional native-dependent checks | Interrupted by the runtime's OpenSees/MPI network-interface initialisation, even after installing the specified OpenSeesPy package. This is an environment limitation, not evidence of a repository regression. |
| Rust and full frontend execution locally | Not rerun: local Cargo/native browser build environment was unavailable. Current commit-specific Actions logs were inspected instead. |

Thus **231 distinct selected Python tests and 14 JavaScript unit tests passed**. Do not interpret this as the entire repository test suite passing.

At the reviewed commit, eight of nine reported Actions workflows completed successfully: civil exploration, integrated stack, example city, factory programme, best-practice design twin, research coverage, engineering integration and Kani. The main CI workflow failed in two jobs. Its Rust format/lint/tests and bounded TACS jobs passed. Its browser suite reported 42 passes and one failure; its Python/generated job stopped before the later broad suites.

Actions evidence: [main CI](https://github.com/modernecotech/OpenSourceRail/actions/runs/38358685892), [civil](https://github.com/modernecotech/OpenSourceRail/actions/runs/38358686002), [integrated stack](https://github.com/modernecotech/OpenSourceRail/actions/runs/38358685821), [example city](https://github.com/modernecotech/OpenSourceRail/actions/runs/38358685845).

### Resolved since the previous review

- The published design-twin source manifest now includes the composite module; its reproduction check passes.
- The reference civil input hash was reconciled; local validation reaches native environment initialisation rather than rejecting the previous stale load-trace hash.
- Legacy frame FEA now uses explicit hollow study geometry and matching BOX sections. The proposed wall values still need engineering selection.
- Core grades couple density, stiffness, strength, conductivity and temperature properties instead of changing density alone.
- Support changes create additional rails, brackets, attachments and mass.
- Manufacturing, analysis and IFC correspondence demonstrators have been added for a panel, roof, bogie interface and viaduct bay.
- The latest plate model maps ply/region properties, trimmed openings, discrete attachments and hollow rail bending. It checks all single-clip-loss locations and combined pressure/fault holdouts.

These are implemented improvements. Do not describe them as still missing.

### Important retained adverse results

The flat side-bay baseline has about 59.57 kg of defined mass and 4.97 mm nominal global deflection against a provisional 5 mm limit. Its worst single-clip-loss deflection is about 16.50 mm, and the 3.5 kPa combined clip-loss case reaches about 28.87 mm. The tight-support arrangement increases defined mass to about 83.51 kg and clips from 12 to 48, while passing those particular elastic deflection screens. Neither arrangement is qualified for strength, fatigue, fire or physical service. Defined mass excludes unresolved seal/secondary retention and final connection details.

The curved roof's 85°C study condition exceeds the selected foam grades' 70°C continuous-temperature datum. The current civil-stage and construction-front studies retain blocked results, including a transport payload exceedance. Auto-design must expose these outcomes, not hide them behind a green nominal result.

## 2. Prioritised findings

| ID | Priority | Finding | Recommended action |
|---|---|---|---|
| F01 | P0 | Main CI rejects installed-cost-and-service-finance.json. Local recomputation differs only in connected_construction_source_revision: retained 6d28e81b… versus current 558112ec…. | Rebuild the affected finance/evidence closure transactionally. Preserve exact provenance comparison; do not introduce numeric tolerances for hashes. |
| F02 | P0 | The engineering-change browser test mocks ERP origin 8180 while the current example catalogue declares 8284. The UI intentionally suppresses links for a different origin. | Build the matching-origin fixture from the recorded catalogue; test mismatched origin separately. Preserve run-specific document identity filters. |
| F03 | P1 | Several exploration workflows own parallel candidate, run, manifest, verification and report conventions. | Introduce common orchestration and contracts with domain adapters; preserve their physics and historical schemas. |
| F04 | P1 | Changes can leave downstream publications stale despite individual source updates. | One dependency graph, immutable runs and atomic publication of the complete dependent artifact closure. |
| F05 | P1 | The Workbench shell and embedded applications present overlapping navigation, city selectors and concepts. | Six task areas with persistent shared context; nested ERP/FUXA menus remain accessible inside the appropriate task. |
| F06 | P1 | City, revision, baseline, run, environment, asset, part and native document identities appear in several contracts. | Define a shared identity envelope and explicit crosswalks; navigation context must remain distinct from authentication and approval. |
| F07 | P1 | Large mixed-responsibility generators and servers increase review and regression risk. | Extract by responsibility behind existing APIs; use golden outputs, contract tests and staged migration rather than a mass rewrite. |
| F08 | P1 | Thousands of generated paths compete with editable source and current guidance. | Capability/source index, current-versus-historical labels and role-based journeys; retain useful CAD/IFC review evidence. |
| F09 | P1 | General Python CI stops at a generated-artifact failure before running broad independent suites. | Separate cheap source/unit jobs, artifact coherence, domain integration and native evidence jobs, then require their combined result. |
| F10 | P1 | Current mixed panel search flips curved/flat geometry and also changes panel height from 3.45 m to 2.35 m. | Define separate functional problem classes. A future material change must not allow side and roof functions to compete merely on absolute mass. |
| F11 | P1 | The detailed panel-response model is not yet the uniform automatic confirmation stage for the earlier strip-based search. | Add a common shortlist/refinement adapter, ranking comparison and explicit model-domain rejection. |
| F12 | P1 | Production geometry, supplier joints, full kit inventories and calibrated full-train modal/contact models remain incomplete. | Close critical physical chains first; the new demonstrators are not whole-train equivalence. |
| F13 | P1 | Civil resistance, prestress histories, full reinforcement, calibrated soil and structural erection stages remain incomplete. | Integrate staged/global-to-local checks and measured inputs; retain component benchmarks separately. |
| F14 | P1 | Quoted installed/lifecycle costs, repair time and controlled carbon are missing from some searches. | Keep unknowns explicit; qualify cost records by scope, place, date, currency and uncertainty. |
| F15 | P2 | Browser acceptance is predominantly Chromium at a large desktop viewport, with default service workers blocked. Dedicated offline tests exist separately. | Add focused responsive, keyboard, Arabic/RTL, browser-engine and service-worker-enabled acceptance lanes. |
| F16 | P2 | ERP business execution, SQLite railway assurance and gateway field/telemetry records can look like interchangeable work-management systems. | Publish record ownership and handoff rules. Share the user's work queue while retaining separate evidence and handback authority. |
| F17 | P2 | Installation/runtime assumptions and dependency ranges vary between general, engineering and research workflows. | Named minimal toolchain profiles, lock/receipt generation and native preflight diagnostics. |
| F18 | P2 | Some current mathematical code is compressed into dense statements, while large modules mix calculation and presentation. | Consistent formatting, units/types, derivation notes and small independently tested kernels. |

Priority definitions: P0 blocks a trustworthy current baseline; P1 enables coherent functionality; P2 improves usability, maintainability and scale. These are review priorities, not safety classifications.

## 3. What to consolidate, and what to preserve

### Ownership model

| Concern | Proposed authoritative owner | Other systems' role |
|---|---|---|
| Physical design, variants and material/process specifications | Versioned engineering definitions and controlled supplier evidence | FreeCAD manufacturing representation; Bonsai civil coordination; solver reductions |
| City alignment, demand, service scenario and deployment assumptions | Existing canonical city/workspace definitions and accepted deployment inputs | GIS, simulator, cost and delivery projections |
| Business work, purchasing, stock, manufacturing, HR and accounting | Native ERPNext/Frappe records | Workbench projections and reviewed OSR-linked handoffs |
| Railway inspections, NCRs and independent handback evidence | Existing OSR assurance workflow and appointed deployment authority | ERP task completion can be referenced, not substituted for railway handback |
| Telemetry, alarms and scoped supervisory requests | Existing integration gateway and controller ownership | FUXA and Workbench views |
| Design experiments and numerical evidence | Common immutable experiment/run service | All discipline tools and reports read the same run identity |
| Acceptance | Named, scope-qualified independent decisions | Search, hashes, simulations and UI role selectors cannot grant it |

Keep Rust control crates independent where they represent separate hazards or hosts. Keep observation-only supervision separate from movement authority. Keep native ERP/FUXA authentication and record ownership until a deliberate, independently tested identity integration exists. Keep physical, simulation and training environments visibly separate.

### Incremental architecture

Create a thin shared design-engine package, not new implementations of the solvers. Existing civil_exploration, design_consistency, panel_response, design-options, changes and twin_design become registered adapters. Their model code can remain in its current domain until duplication has actually been demonstrated.

Shared services should provide:

1. Typed identity, SI quantity/unit, applicability, evidence and material contracts.
2. Versioned problem definitions, variable bounds and mandatory constraints.
3. Candidate compilation, dependency hashing and lineage.
4. Bounded jobs, checkpoint/resume, cancellation and structured failure records.
5. Artifact storage, verification, retrieval and atomic publication.
6. Comparison, refinement and review/export APIs.
7. A common Workbench presentation and command-line dispatcher.

Useful existing seams: osr_mech engineering_definition and section_contract; design_consistency contracts; civil_exploration workflow/storage; Workbench context contract and job manager; integration identity/store; existing desktop bridge and ERP engineering-change workflow.

Extend the existing ./osr command. Proposed commands include design problems, design run, design compare, design refine, design verify and design export, plus check --scope and doctor --profile. These are proposed interfaces, not currently implemented commands. Legacy scripts delegate to the new dispatch path during migration.

Avoid a new universal database for every subsystem. A lightweight indexed experiment store plus immutable artifact directories can sit alongside native ERP, gateway history and existing assurance storage. Cross-system relationships use explicit IDs and revisions.

### Repository and publication simplification

- Keep a capability ledger linking every current function to its owner, CLI, UI route, contract, tests, example and status.
- Keep canonical city snapshots and small public review artifacts in Git, following the existing artifact policy. Large solver fields and repeated reports can use versioned release/artifact storage with checksums and durable retrieval.
- Measure duplicate content and regeneration time before deleting files. A compact pointer without an obtainable payload is a functionality loss.
- Generate docs, Workbench routes, dependency scopes and command help from controlled metadata where useful; do not generate readable engineering explanations from an opaque inventory alone.
- Preserve older artifacts as historical evidence without treating their schemas as active implementation alternatives.
- Format and type critical calculation boundaries; extract small modules for CAD, quantities, physics, evidence and presentation from the identified monoliths.

## 4. UI and documentation target

### Six primary Workbench areas

| Area | Functions consolidated beneath it |
|---|---|
| Plan | City Studio, GIS, demand, routes, service/fleet/staff planning, candidate city comparisons |
| Design | Parts, subsystems, assemblies, auto-design, CAD/BIM exchange, interfaces and engineering changes |
| Deliver | Procurement, manufacturing, construction schedule, labour, costs/cashflow and business execution |
| Operate | OCC/training replay, FUXA supervision, current observations, alarms and incidents |
| Maintain | Assets, condition, defects, work packs, offline field capture, repairs and renewal |
| Assure | Requirements, hazards, tests, provenance, decision readiness, inspections and acceptance gates |

The current 25 entries become secondary navigation and role-specific shortcuts. This is an information-architecture target, not removal of 19 functions.

Always retain a compact context strip: city/project, configuration revision, environment, selected asset/part and active run. Show the approved baseline distinctly. Display longer hashes, source lists and review details in an inspector. Changing city or revision must keep the current context-invalidation behaviour.

Replace multiple parallel status pages with one consistent evidence panel. Its states should distinguish draft, running, numerically verified, physically correlated, independently accepted, failed, stale, unknown and not run. Avoid one ambiguous passed flag. Every failure should show the failed condition, affected scope, units, governing load case and the next resolvable action.

An asset/part detail page should link its CAD/IFC, assemblies, material/process record, supplier revision, BOM, drawings, loads, interfaces, inspections, FMEA and historical changes. Do not populate absent information with plausible-looking defaults.

A common job centre should show queue, phase, progress, elapsed/resource budget, cancellation, resume eligibility, warnings, logs and outputs. It should make an unavailable native solver visible before launching the job. Preserve failed attempts and incomplete runs.

Use shared HTML/CSS/ES-module components and design tokens for OSR-owned pages; extend osr-gui-shared for Rust canvas interfaces. ERP and FUXA remain native applications with appropriate links and framing. A wholesale frontend-framework rewrite is not needed to achieve this.

Accessibility targets include keyboard paths, visible/unobscured focus, semantic labels, scalable text, meaningful non-colour status, accessible tables, reduced motion and touch targets. Add Arabic translation and RTL/layout support for the Iraq deployment, while keeping engineering identifiers and units unambiguous. Automated checks supplement keyboard and representative-user review. WCAG 2.2 is the proposed web target; conformance is not claimed here.

The existing README has already been shortened. Keep it as the front door. Add a minimal role/task getting-started path, a clear capability/status directory, an editable-source map and named tutorials using the same example. Mark historical reviews and generated local summaries consistently. Generate the reader book from those paths, and measure whether readers can find the input, command, result and remaining gate for a task.

## 5. Auto-design specification

### Ethos translated into engineering inputs

Auto-design should minimise complete installed and lifecycle cost, foreign-currency dependence, production/installation effort and disruption, while maintaining service, durability, maintainability, local ownership and verified engineering performance.

Each problem states its functional contract: envelope, capacity, load cases, duty cycle, interfaces, service life, climate, site/route, manufacturing processes, materials, supplier evidence, inspection and replacement access. Side panels, roofs, structural members and infrastructure packages are different problem classes. Fix the required function before allowing shape changes.

Typically choose two to four primary optimisation objectives for a campaign. Report other outcomes and apply necessary constraints; putting every possible goal into one many-objective search can obscure useful tradeoffs. Objectives may include whole-life cost, installed mass, production/erection time and disruption. Imported spend, maximum lift, energy duty, replacement time and verified carbon can be objectives or constraints depending on the owner-defined charter. An unavailable quotation or environmental dataset is unknown, never zero.

Local manufacturing inputs include stock sizes, workshop equipment, mould reuse, crane/transport availability, operator skills, energy/cure needs, achievable tolerances, QA capability, rejects, spares and supply risk. These constraints should select realistic processes, not simply favour minimum material volume.

### Levels of design

| Level | Variables and generated consequences | Verification |
|---|---|---|
| Part | Section walls, shapes, layups, cores, ribs, openings, insert/bolt patterns, process choices | Material/geometry quantities, local strength/buckling/contact, manufacturing limits, inspections |
| Subsystem | Rail/support arrangement, battery mounting/cooling, HVAC installation, bogie interfaces, bearings, pier/cap/pile package | Load paths, interfaces, tolerances, service access, thermal/electrical/mechanical response |
| Assembly | Underframe/body/roof, articulated train, full viaduct bay, station assembly | Mass/CG/inertia closure, modes, dynamic loads, clashes, failure cases and assembly sequence |
| Deployment | Route/site, construction front, fleet/service, charging, depot and maintenance configuration | Delivered service, finite-resource schedule, complete costs, disruption and operational resilience |

Optimise hierarchically but re-evaluate the integrated design. A lighter part that adds brackets, lifting equipment, qualification cost or maintenance burden can make the assembly worse. Preserve loads and boundary conditions from the complete system when refining local parts.

### Candidate lifecycle

Define problem → compile physical candidate → reject invalid geometry/processes → run fast screen → record conditional tradeoffs → refine a diverse shortlist → verify ranking and convergence → test holdout/fault/uncertainty cases → correlate prototype evidence → prepare an independent review package.

The compiler must regenerate hardware, joints, quantities and tests for every accepted variable change. Candidate IDs identify definition/material/process changes; evaluation IDs additionally identify load cases, solver versions, meshes, tolerances and evidence. Cache only those complete identities. A solver failure, outside-domain result and physically infeasible candidate have separate statuses.

Keep numerical search, physical qualification and baseline promotion distinct. The software may prepare a recommendation or draft ERP change; it must not silently overwrite the adopted design, production BOM or release state.

### Tool responsibilities

| Tool | Role and limits |
|---|---|
| FreeCAD | Native manufacturing solids, datums, assemblies, drawings and tooling; deterministic generation and reopen checks. An editable model alone is not evidence of strength. |
| Bonsai/IfcOpenShell | Civil/site coordination, physical/analytical model identities, quantities, reinforcement/tendon objects, schedules, IDS and BCF. Solving needs an explicit analysis adapter. |
| Gmsh/CalculiX | Mesh generation and mechanical shell/solid/connection analyses; independent benchmarks and domain limits required. |
| OpenSeesPy | Existing global civil and foundation models; extend staged/cyclic response with calibrated laws. |
| Existing shared vehicle solver | Train–track–viaduct coupling, equipment mounts and controllers; complete modal/contact/service validation remains required. |
| pymoo | Existing mixed-variable multi-objective search; common budgets, constrained ranking and reproducible comparisons. |
| Code_Aster / IFC2CA | Follow-on prestressed/nonlinear/time-dependent concrete analysis; add a bounded validated adapter before claiming support. |
| MBDyn | Optional independent flexible multibody benchmark, not an automatic rail-contact replacement. |
| BESO / CalculiX | Later topology exploration in bounded brackets/carriers/stiffeners; reconstruct manufacturable CAD and verify again. |

Do not begin with unconstrained AI-generated topology. The immediate gains lie in reusable parametric shapes, assembly arrangements, material/process choices and measured model refinement. Natural-language assistance may create a reviewable draft problem specification; structured validation governs execution.

### Physics extensions that remain necessary

- Panels: hot/wet properties, curved roof shells, unilateral contact/gaps, potting/insert pull-out, peel/debonding, secondary retention, fatigue, impact, water/UV/sand ageing, complete-stack fire and thermal margin beneath roof PV.
- Vehicle: complete critical kit decomposition, manufactured joint definitions, weld fatigue, actual structural/modal basis, supplier suspension curves, approved wheel/rail profiles, roughness, flange/multiple-patch domain, full duty and degraded service.
- Civil: reinforcement/tendon/anchorage detailing, transfer and losses, creep/shrinkage/cracking, shear/torsion, cyclic/seismic resistance, calibrated soil/pile-group/settlement behaviour and site water/flood/scour applicability.
- Construction: transport and lifting stability, temporary supports, launcher loads, stressing/continuity sequence, dimensional tolerances, release strength and bearing replacement/jacking.
- Commercial: bounded, scope-complete local prices, installation/QA/rework, rights/licensing, spares, support and realistic resource productivity.

## 6. Work packages

Every package below has an owner role, dependencies, a concrete output and testable completion. Appoint people and capacity before assigning dates. P0/P1/P2 are priorities. Packages are proposed work, not completed repository changes.

### Consolidation and reproducibility: C01–C10

| ID | Priority / owner | Dependencies | Deliverable | Acceptance tests and completion |
|---|---|---|---|---|
| C01 | P0 / release engineer + finance modeller | None | Reconciled industrialisation finance publication and manifest closure | Current exact source revision reproduces; semantic financial diff is reviewed; an upstream source change invalidates only its declared dependants; main generated-artifact job passes. |
| C02 | P0 / frontend test engineer | None | Catalogue-driven ERP-origin fixture and distinct mismatch regression | Matching origin exposes project/BOM/work-order searches bound to the recorded run; a wrong origin exposes no unrelated links; reused IDs and other cities remain isolated; all 43 current browser cases pass. |
| C03 | P1 / architecture maintainer + domain owners | C01, C02 | Capability ledger for all current CLI/UI workflows, crates, services and studies | Every active function has owner/source/entry/contract/test/example/status; before/after ledger comparison proves no unexplained feature loss. |
| C04 | P1 / contract architect | C03 | Shared identity, SI quantity, evidence and applicability envelope with versioned crosswalks | Units, nonfinite values, duplicates, missing scope and incompatible revisions are rejected; old examples translate without altered decisions or numerical meaning. |
| C05 | P1 / build-and-evidence engineer | C04 | Dependency graph, transactional generation/publication and immutable run store | Crash cannot publish a partial closure; changed material/solver/geometry invalidates dependent results; an unrelated documentation edit does not invalidate physics; stale cache/resume is rejected. |
| C06 | P1 / Python/CLI maintainer | C03 | Reusable Python packages, minimal toolchain profiles, launcher delegation and doctor command | Clean setup can run the selected quick profile; native requirements are reported explicitly; old commands retain output/exit semantics during migration; dependency receipts reproduce. |
| C07 | P2 / module maintainers | C03, C04 | Staged extraction of geometry, calculations, evidence, API and rendering from the largest modules | Golden fixtures and interface contracts remain equivalent; benchmarks protect key paths; imports obey domain boundaries; review-sized migrations are independently tested. |
| C08 | P2 / data/publication maintainer | C05 | Catalogue artifact index, incremental regeneration and durable bulk-evidence retrieval | All city cores remain available; selected-city build leaves others unchanged; published links resolve; offline reference packages work; byte identity, retention and licensing survive migration. |
| C09 | P1 / documentation lead + practitioner reviewers | C03 | Role/task tutorials, current/history/source labels and generated command/capability directory | A planner, engineer and maintainer each find editable input, command, output and unresolved gate using one named example; documentation links and generated index reproduce. |
| C10 | P1 / ERP + assurance + integration owners | C04 | Record-ownership/handoff matrix and shared user work-queue projection | ERP completion cannot grant railway handback; duplicate/offline/lost-reply events preserve one execution; business revisions and assurance decisions retain separate audit histories. |

### User interface: U01–U06

| ID | Priority / owner | Dependencies | Deliverable | Acceptance tests and completion |
|---|---|---|---|---|
| U01 | P1 / product designer + frontend lead | C03, C04 | Six task areas with secondary routes and persistent context | All 25 existing entries are reachable; city/revision switches clear invalid baseline/run/asset state; role shortcuts grant no authority; direct links still work. |
| U02 | P2 / frontend maintainer | U01 | Shared design tokens, status/evidence/table/form components and split JS modules | Loading, unavailable, empty, failed, stale and unknown states are distinguishable; no lost drafts; embedded tool layout, theme and status semantics remain coherent. |
| U03 | P1 / full-stack engineer | C05, U01 | Common job centre and asset/part detail inspector | Progress/cancel/resume and results survive reload; unavailable tools fail preflight; one selected part resolves all its available CAD/BIM/BOM/QA evidence without crossing city or environment. |
| U04 | P2 / accessibility/localisation lead | U02 | Keyboard/mobile/zoom/Arabic-RTL improvements | Manual keyboard journeys and automated checks pass; 200% zoom/reflow and representative touch layouts work; Arabic and mixed-unit content render correctly; offline field capture remains durable. |
| U05 | P1 / design product lead + frontend engineer | A01, A02, U03 | Auto-design flow: define, vary, run, compare, refine, review/export | Users see variable bounds, units, fixed function, budgets, failed/unknown gates and governing cases; conditional search results cannot be mistaken for accepted designs. |
| U06 | P2 / CAD/BIM integration engineer | C04, U03 | Consistent FreeCAD/Bonsai selection and reviewed-edit exchange | Stable IDs survive native save/reopen and exchange; changed desktop geometry requires a visible definition diff and invalidation; no browser-to-shell arbitrary command path. |

### Auto-design: A01–A13

| ID | Priority / owner | Dependencies | Deliverable | Acceptance tests and completion |
|---|---|---|---|---|
| A01 | P1 / systems engineer + product owner | C03, C04 | Versioned problem charter and ethos-based objective/constraint policy | Fixed functional requirement, environment, scope and mandatory gates are explicit; unknown price/carbon is not zero; side/roof/vehicle/civil functions cannot be compared without declared equivalence. |
| A02 | P1 / design-engine maintainer | A01, C05 | Adapter registry over existing civil, panel, consistency, city-option and engineering-change tools | One typed job/result API covers each adapter; domain limits are declared and enforced; legacy studies remain reproducible; unavailable solvers cannot report native passes. |
| A03 | P1 / parametric CAD + contract engineers | A01, A02 | Coherent variant compiler and installed-assembly crosswalk | A variable change updates geometry, material regions, joints, mass/CG/inertia, BOM, support arrangement and inspections exactly once; dependent solver inputs share the candidate identity. |
| A04 | P1 / materials/process engineer | A01, C04 | Controlled material and local-process database | Grade density/stiffness/strength/temperature and ageing are coupled; batch/supplier/test source is preserved; unsupported interpolation and process substitutions fail; nominal/synthetic/measured states remain distinct. |
| A05 | P1 / manufacturing + joint-design engineers | A03, A04 | DFM/DFA, connection, tolerance, assembly and service-access rules | Thickness/radius/stock/process limits, fastener tools, removable-part paths, tolerance stacks and mould/fixture counts affect validity and quantities; no free support or joint optimisation. |
| A06 | P1 / composite/FE analyst | A02–A05, T02 | End-to-end clipped side/roof part pilot with automatic detailed confirmation | Search finalists run the mapped plate/rail model; all single-clip failures and holdouts are retained; curved roofs use an applicable shell adapter; mass includes final retention/seals; measured tests remain open until supplied. |
| A07 | P1 / electrical/thermal/mechanical leads | A02–A05, T02 | Battery mounting/cooling and roof-HVAC/PV subsystem optimisation | Equipment counts, electrical compatibility, thermal duty, failed-module performance, fire interfaces, mass and supports change coherently; subsystem improvements do not hide vehicle energy or maintenance penalties. |
| A08 | P1 / vehicle dynamics + structural leads | A03–A07, T02, T03 | Underframe/body/bogie/articulation assembly optimisation | Actual/modal mass is conserved; FE modes and mounting loads reconcile; complete prescribed cases run with temporal/spatial refinement; failed contact/model domains remain visible; joint-fatigue/physical gates cannot be waived by search. |
| A09 | P1 / bridge/prestress engineer | A02–A05, T02 | Deck/pier/bearing package optimisation with staged/global-to-local checks | Reinforcement, tendons, anchorage and stage supports affect quantities and analysis; transfer, losses, crack/service/ultimate demands, lifting and bearing replacement are individually assessed. |
| A10 | P1 / geotechnical + route/station engineers | A09, A04 | Site-qualified foundation, junction and station variants | Survey/CRS/ground/water/utility data are source-qualified; soil/group/settlement/cyclic models declare calibration; route clearances and station access remain constraints; research defaults do not establish site resistance. |
| A11 | P1 / optimisation/numerical engineer | A02, T02, T06 | Multi-fidelity constrained search, sensitivities, uncertainty and optional surrogate | Equal-budget seeded baselines, diversity, cache accounting and mesh/time confirmation reproduce; detailed ranking is checked; held-out/fault cases are independent; surrogate extrapolation is rejected and finalists are solved directly. |
| A12 | P1 / cost + production/logistics planners | A03–A05, A09 | Complete installed/lifecycle/localisation and finite-resource objective adapters | Quotes carry place/date/currency/scope; tooling, QA/rejects, transport, cranes, crews, procurement and replacement are included; capacity and closure windows affect schedules; no global financial adoption occurs silently. |
| A13 | P1 / configuration + assurance + ERP leads | A06–A12, C10 | Review-ready drawing/BOM/RFQ/test/ERP change package | Approved scope identifies every candidate/result/deviation; old evidence is retained; test reviewer and design authority are distinct; a recommendation can prepare a draft but cannot overwrite the baseline or production release. |

### Testing and assurance: T01–T07

| ID | Priority / owner | Dependencies | Deliverable | Acceptance tests and completion |
|---|---|---|---|---|
| T01 | P1 / test infrastructure engineer | C03, C06 | Shared test tiers, environment preflight, locked profiles and impact-based CI | Source/unit, contracts, solver, browser, stack, soak/formal and physical tests have distinct scope; missing native prerequisites are explicit; independent tests still run after one artifact check fails; complete periodic jobs protect the selector. |
| T02 | P1 / numerical verification lead | C04, A02 | Independent mechanics/thermal/electrical/soil and solver benchmark library | Reaction/moment balance, work/energy, mass, rigid modes, analytical limits and mesh/time refinement are checked; native geometry and fallback geometry never share an ambiguous pass. |
| T03 | P1 / property-test engineer + domain leads | C04, A03 | Property/metamorphic, fuzz and schema-evolution tests | Permutation preserves assembly totals; density affects mass; support additions add material; rotation transforms inertia; state/revision/units mutations reject safely; parser and lineage cycles are bounded. |
| T04 | P1 / frontend acceptance engineer | U01–U05 | Behavioural browser/context/accessibility/offline matrix | Matching/mismatched origins, reused IDs, stale hashes, role/mode/city changes, denied writes, mobile/RTL and offline conflict recovery work; use isolated fixtures and user-visible assertions rather than longer sleeps. |
| T05 | P1 / integration/SRE engineer | C05, C10, A02 | Restart/outage/lost-reply/resource and restoration campaigns | Cancelled jobs leave durable attempts; duplicate ERP events are idempotent; restore uses clean resources; corrupted evidence and expired/revoked credentials fail; CPU/memory/evaluation/time budgets are enforced. |
| T06 | P1 / optimisation QA lead | A01, A02 | Algorithm and adversarial objective-regression suite | Establish the benchmark harness before A11, then extend it with that implementation. Known optima/fronts and equal-budget random controls reproduce; no fake zero cost, weakened constraint, changed function, free hardware or search-only rank wins; diverse holdout failures remain in reports. |
| T07 | P1 / assurance + prototype/HIL leads | C04, A06–A10 | Part→subsystem→assembly verification matrix, prototype and HIL correlation, exact formal-scope register | Measured/test/calibration validity and uncertainty are controlled; independent data establish correlation; unresolved formal obligations remain open despite selected CI success; failures invalidate only scoped acceptance. |

## 7. Execution sequence and migration controls

### First two weeks

Complete C01 and C02. Establish C03's capability ledger and baseline command/output inventory. Design C04/C05 contracts around existing implemented seams. Agree ownership boundaries in C10. Prototype U01 with current routes. Separate the current main CI's independent checks so one stale publication does not obscure all source-test outcomes.

### First 90 days: useful software milestone

Target one common design problem/job/result lifecycle, a task-grouped Workbench, one shared evidence/part inspector and one end-to-end clipped-panel pilot (A06). Adopt the test tiers and adversarial optimisation regressions. Demonstrate that all current workflows remain reachable and that a change produces a complete reviewed closure. This is a proposed scope target, not an assured schedule; staffing and native-tool capacity must be allocated.

### Subsequent engineering waves

1. Battery/HVAC and bogie-interface subsystems, manufacturing/connection detail and economics.
2. Actual full-vehicle modal/contact/service integration and full viaduct/foundation/staging families.
3. Broader route/station and construction-front optimisation, calibration and prototype/HIL evidence.
4. Optional surrogate, topology, Code_Aster or MBDyn integrations only after the base adapters and benchmarks are useful.

Physical and supplier milestones depend on actual material records, site investigations, quotations and prototype access. They should have appointed owners and evidence dates rather than software-generated completion claims.

### Migration rules

- Every capability is mapped before moving or removing an entry point.
- Capture reference fixtures and exact hashes before a refactor. Preserve the original manifest serializer for historical evidence; a shared future serializer needs an explicit schema/version transition.
- Reuse physics code behind adapter contracts before attempting model mergers.
- Run old and new paths on the same inputs; compare outputs, errors, bounds, authority and performance.
- Move one workflow at a time. Deprecate only after parity, documentation and operator feedback.
- Preserve existing accepted/historical evidence and the ability to verify it without treating old inputs as current.
- A rollback returns routing/configuration, not a destructive rewrite of engineering or ERP history.

## 8. Testing framework and completion metrics

| Tier | Required evidence | Appropriate trigger |
|---|---|---|
| 0: static/source | Formatting, types, schemas, dependency/ownership graph, documentation and licence checks | Every change |
| 1: fast unit/contracts | Pure calculations, negative scope/unit/value tests, UI state and adapters | Every change, scoped but with a complete periodic run |
| 2: mathematical/model | Analytical limits, patch/energy/equilibrium tests, native solver crosschecks and domain rejection | Changed model/adapter; scheduled reference replay |
| 3: candidate/assembly | CAD↔analysis quantities and IDs, modal/interface transfer, construction stages, scenario/fault/holdouts | Design/material/load/process changes |
| 4: application/stack | Browser tasks, ERP/FUXA/gateway integration, offline execution, restart and restoration | Relevant boundaries; regular clean-stack replay |
| 5: endurance/formal | Long duty/soak, scale budgets, declared formal properties and remaining proof scope | Scheduled and release candidates |
| 6: physical/acceptance | Coupons, joints, manufactured articles, modal/ride/load tests, HIL, calibration and independent decisions | Controlled prototype/deployment programme |

Reduce duplicated fixtures and expensive identical executions, not independent evidence. Run artifact coherence as a dedicated gate rather than ahead of all source tests. Use separate numerical-reproduction tolerances for named observables; provenance, units, decisions and scope remain exact. Reject a candidate for engineering infeasibility separately from unavailable tools, solver failure and exceeded budgets.

Candidate-dependent tests must be generated from an independently defined verification matrix. If the same generator creates both implementation and expected result, also retain analytical/native/physical comparisons that can find a shared error.

Acceptance metrics for consolidation:

- 100% of existing active capabilities mapped, with no unexplained loss.
- Six primary navigation areas; all existing secondary routes and deep links retained or deliberately migrated.
- One identity envelope, experiment/job/result contract and artifact pipeline for new common-engine runs.
- Critical cross-system mappings tested for city, environment, revision, serial, project and permissions.
- No partial current publication after forced interruption.
- Reproducible clean minimal development setup and explicit native profile requirements.
- Measured onboarding task completion and time-to-first-success improve from an observed baseline.
- CI and regeneration time measured before/after, with protected physics and acceptance scopes.

Acceptance metrics for auto-design:

- At least one part, subsystem and complete assembly workflow can generate and compare physical alternatives.
- Every finalist identifies all mandatory passed/failed/unknown/not-run checks.
- Geometry, mass, CG/inertia, supports, joints, BOM and relevant test inputs reconcile.
- Search improvement is reported against equal-budget baselines across multiple seeds, not a selected best run.
- Detailed model and holdout/fault checks can overturn screening rankings; overturned candidates remain inspectable.
- Commercial, material and physical unknowns never become zero objectives or release passes.
- Review/export preserves revision, scope, sources, licence and unresolved work.

## 9. Sources and review anchors

All repository links below are pinned to the reviewed revision.

- [Workspace and crate membership](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/Cargo.toml).
- [Workbench module registry](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/docs/workbench/modules.json).
- [Main CI](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/.github/workflows/ci.yml) and [frontend configuration](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/playwright.config.mjs).
- [Failing browser fixture](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/tests/frontend/engineering-change.spec.mjs), [origin-bound UI](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/engineering/changes/app.js) and [example catalogue](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/engineering/changes/catalogue.json).
- [Industrialisation generator](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/tools/automation/industrialisation-study.py).
- [Design consistency](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/engineering/design_consistency/README.md), [contracts](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/engineering/design_consistency/contracts.py) and [mixed search](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/engineering/design_consistency/search.py).
- [Panel response](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/engineering/panel_response/README.md) and [retained comparison](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/engineering/panel_response/examples/summary.json).
- [Civil exploration](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/engineering/civil_exploration/README.md), [city design options](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/engineering/design-options/README.md), [operations management](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/engineering/operations/README.md) and [artifact policy](https://github.com/modernecotech/OpenSourceRail/blob/ace7e0b4ddb2754fb9ddd89860534cefb7a71c27/docs/repository-artifact-policy.md).
- [Playwright best practices](https://playwright.dev/docs/best-practices): isolated tests, user-visible behaviour and resilient assertions.
- [W3C WCAG 2.2 guidance](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/): focus, input and accessibility targets.
- [pymoo mixed-variable documentation](https://pymoo.org/customization/mixed.html): categorical/integer/continuous/binary search; use the repository's validated version before upgrading.
- [IfcOpenShell IFC2CA](https://docs.ifcopenshell.org/ifc2ca.html): explicit IFC structural analytical models to Code_Aster; this conversion is a follow-on adapter, not an existing automatic qualification route.

Prepared work packages: **36** — 10 consolidation, 6 UI, 13 auto-design and 7 testing/assurance packages. The first reviewable delivery should fix reproducibility and make one complete engineering workflow easier to use; subsequent work expands that coherent pattern across the broad platform.
