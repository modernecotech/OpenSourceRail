# Design Engine Review Follow-ups

The review of `7b0ba0a` found two acceptance gaps and an incomplete campaign
connection. Independent vehicle comparisons now verify each retained case
manifest, input, result, log and history before consuming metrics. Every case,
including the baseline, must declare unchanged physics sources and toolchain;
both identities must match across the campaign. Missing, changed, mixed or
unretained evidence keeps comparison unknown. These local integrity records do
not establish independent attestation or physical validation.

Vehicle confirmation now executes a baseline and separate time, deck, rail and
body-mode refinements for each of the four reference scenarios. The other
inputs remain fixed for each comparison. Plans precede execution, every case
uses the common evaluation and remaining wall budget, and progress retains
planned, executed and validated counts through cancellation or budget failure.
Dispatch reserves ten seconds for progress and attempt sealing, and stops
starting cases when that reserve is reached.
The comparison and physical-part views show these counts, passage coverage,
provenance issues and each axis's numerical state in English and Arabic.
Execution completion alone cannot pass refinement. The 5% relative screen is
provisional; contact validity, additional refinement levels, real body stiffness
and measured correlation remain open.

Impact selection now follows both native-part problems' dependency closures and
the native acceptance implementation/tests. Changes to generated geometry,
shared physical properties/schema or the acceptance runner select
`native-design`; unrelated commercial prose does not. The four-profile software
release requirement remains separate.

The [fresh verification record](refinement-verification.json) retains the
source-qualified 20-case diagnostic. Its native passages all exceeded their
allocated budgets, so no independent numerical convergence pass is claimed.

The physical-property review found that BOM correspondence accepted symmetric
inertia tensors with impossible principal moments. BOM validation now uses the
shared physical inertia validator, checking positive semidefiniteness and the
principal-moment triangle inequalities. Its tolerance scales with the tensor,
so small parts do not receive an absolute allowance that conceals invalid data.
Point, line and lamina limits remain valid. Export tests seal matching invalid
records and verify rejection before a review package is written.

BOM JSON and CSV now state SI property units, coordinate frame and the own-CG
inertia reference. Known CG/inertia requires an explicit proper rigid placement;
contradictory unit/frame declarations, scaled axes and reflections are rejected.
Unknown physical properties remain unknown. Standalone `evidence` validation
also restores exact bundled Baghdad prerequisites before repository health;
different existing input bytes are preserved and fail setup explicitly.

The review of `f72181b` identified two further recursive-policy defects. Known
mandatory failures now veto screening and verified recommendations regardless
of check category. This includes the actual roof hot/wet failure; passing
numerical checks cannot override it. Regression cases cover both `failed` and
`outside-domain` states during screening and confirmation, across numerical and
physical check groups.

The civil preset now requires executable geometry, mass/inertia and service
screening, followed by native refinement. Interfaces and degraded-service
qualification remain explicit unresolved checks. The fixed deck still fails
its actual service screen and cannot enter confirmation. Callback-transport
tests deliberately substitute a labelled service pass to exercise the eligible
route; they do not establish a feasible civil design or execute native solvers.

The required `native-design` acceptance profile executes the installed FreeCAD,
Gmsh and CalculiX tests. Missing tools, omitted or skipped mandatory cases,
incomplete native reports and changed artifact bytes fail acceptance. The
[local validation instructions](../local-validation.md) give reproduction and
receipt-verification commands. This feature profile does not close the separate
four-profile software release gate.

The earlier review of `63cfe3347` identified three defects in the shared
software. They are repaired:

| Finding | Implemented behaviour | Verification |
|---|---|---|
| Vehicle BOM silently empty | Review and CSV export read the validated installed register. Physical IDs, quantities, mass, definition hashes and unresolved allocations must reconcile with either `parts` or `instances`; malformed inventories fail. Study-only adapters explicitly report non-applicability. | Actual panel, civil, battery, HVAC and 192-instance whole-train compilers; corrupt/duplicate/missing inventory mutations; offline export correspondence |
| Evidence lost project/revision/baseline | Full canonical identity and explicit candidate/part/batch/physical-definition applicability are persisted and included in record revisions, idempotency and independent verification. Null scope is unknown, not a wildcard. Legacy records are retained, unscoped and ineligible. | Cross-project/revision/baseline/candidate/part/batch/definition rejection; independently verified actual quotation fixtures; missing installed inventory still prevents complete cost |
| Checked drafts could not drive optimisation | A source-backed proposal retains checked inputs and document bytes. An independent authenticated reviewer permits research use. A new configuration revision creates an immutable child request, recompiles the assembly and reruns checks/search. No parent or adopted baseline is edited. | Actual HTTP → reviewed sources → child worker → paired-seed optimisation; changed constraints reject child candidates; independent review, lost replies, source corruption, two-generation export and recovery |

The common engine exposes fifteen controlled problems. New civil alternatives
keep a 100 m, five-span, two-track reference function while varying existing deck,
pier, material and foundation families. New vehicle alternatives retain the
six-car reference function and compile actual battery/HVAC/equipment arrangements
and declared joint hypotheses. Mass changes cannot be hidden by adjusting residual
allowances. Unknown allowance positions and complete installed mass remain unknown.
The 32-series battery choice is rejected when it violates the actual bogie envelope.

Optional paired factorial studies execute two levels of two to six declared
variables. Every compiler/screen evaluation consumes the common worker budget.
Reports retain all attempted or missing corners, engineering failures, paired
contrasts and unknown costs/carbon. This is finite scenario exploration; no
probability distribution, calibrated uncertainty or global optimum is inferred.

Source-qualified foundation inputs now drive a conditional elastic pile-group
model: actual pile positions, cap offsets, coupled six-axis response, settlement,
lateral displacement, rotations, reactions and equilibrium. Explicit group and
cyclic factors are sensitivities. Independent axial/toe, Timoshenko cantilever,
group symmetry and overturning benchmarks check its numerical scope. Project
soil calibration and nonlinear p-y/t-z/q-z resistance remain unresolved. The
[FHWA GEC 9 reference](https://www.fhwa.dot.gov/engineering/geotech/pubs/hif18031.pdf)
is supporting literature, not a project ground record.

Guided SI/source fields, field validation, installed-part/joint/failure inspection,
reviewed-input controls and operation-specific setup are available in English and
Arabic. Raw JSON remains an optional expert view. CAD export checks CAD setup;
screening does not require a native confirmation solver. New frontend code is
formatted using the pinned local formatter. Automated browser journeys do not
replace human accessibility or translation review.

Process ownership now handles unavailable `/proc` safely. A live process with
unverifiable ownership is retained as unknown; another worker cannot steal its
job or signal it. Definitively dead or reused processes remain recoverable.
The Workbench city-job manager uses the same ownership checks.

The flexible vehicle matrix assembly uses compact active columns while retaining
the same equations. Dense-equivalence checks cover straight/curved systems,
equipment/preload and two/six modes. An actual 100-step comparison returned every
field exactly equal, with measured wall time reduced from 16.555 to 10.927 seconds
on this machine. This measurement is not a general performance guarantee. Common
vehicle confirmation now allocates each case from the remaining declared job
budget instead of silently imposing a 45-second limit.

[Fresh common-engine executions](review-model-verification.json) and the
[full-duration dynamics executions](dynamics-verification.json) retain actual source,
input, toolchain and output hashes. Earlier [model executions](model-verification.json)
remain historical with their original bytes; they have not been relabelled current.
[Local verification](verification.md) records the checks and release limitations.

Further engineering development remains required:

| Area | Remaining implementation or evidence |
|---|---|
| Side and roof panels | Complete seal/secondary-retention/locking/contact-land inventories; insert pull-out, bearing, bond failure, fatigue and complete thermal/fire stack; applicable measured correlation. Existing failed pressure/attachment-loss cases remain failures. |
| Vehicle dynamics | Execute and pass the worker-connected independent time/deck/rail/modal campaign with valid contact for every scenario and further levels as required; derive reduced models from actual body/underframe geometry and obtain measured joints/fatigue correlation. A completed passage alone closes none of these. |
| Civil structures | Cracking/nonlinear resistance, shear/torsion, reinforcement/anchorage, bearing laws and buildable erection/replacement details. The retained gross-elastic 23.97 mm service deflection still exceeds the provisional 20 mm limit. |
| Foundations/sites | Calibrated ground inputs, nonlinear/group/cyclic resistance and independent project validation; no site release from source syntax or input completeness. |
| Electrical/thermal installation | Installed converters, protection, harnesses, cooling circuits, mounts and complete mass; route-duty/usable-energy/thermal correlation. Public potential parts supply no free installed credit. |
| Lifecycle/calibration | Exact-revision measurement/inspection/calibration intake is available. Automatic parameter updates, as-built serial reconciliation and independent holdout execution remain domain work; uploading a calibration document cannot update a solver. |
| Economic ranking | Applicable quotations can contribute only to their exact scoped assessment. Full installed quantities, lifecycle scope, production, disruption, imports and carbon still require sourced inputs and connected models. |
| Acceptance | Named reviewers, measured coupon/joint/assembly/HIL tests, supplier commitments, site records and human accessibility review remain unavailable. |

All computation remains local. GitHub Actions stays disabled. A software release
requires passing `ci`, `kani`, `integrated-stack` and `example-city` receipts bound
to the same clean candidate commit. The deployment profiles refuse existing
services, ports and volumes; their guard is preserved to protect operational data.
