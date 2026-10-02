# Subsystem qualification and quantitative RAMS

The battery-cooling workflow connects the assurance graph to quantitative
screening, controlled rig measurements, manufacturing equivalence and signed
review decisions. Workbench's **Decision readiness** view shows requirements,
design verification, physical qualification, integration, independent review
and operating conditions separately.

The current package is a **reference programme with no selected physical rig,
supplier parameters or measured qualification results**. Numerical examples
are labelled assumptions. They cannot establish an operating restriction,
inspection interval, staffing commitment or accepted railway use.

## Controlled sources

| Source | Responsibility |
|---|---|
| [Qualification definition](../../lib/templates/subsystem-qualification.json) | RAMS allocation, hazards/interfaces, assessment agreement, rig, instruments, test criteria, production controls and reviews |
| [Quantitative inputs](../../engineering/assurance/battery-cooling/rams-inputs.json) | Parameter ranges, units, evidence basis, common causes, repair/inspection/logistics assumptions and alternatives |
| [RAMS models](../../engineering/analysis/rams.py) | Numerical models with bounded problem sizes and finite input validation |
| [Qualification compiler](../../tools/automation/subsystem_qualification.py) | Measurement checks, model correlation, manufacturing findings, signed-review verification and export |
| [Generated readiness](../../engineering/assurance/battery-cooling/qualification-report.md) | Results and unresolved decisions; [JSON](../../engineering/assurance/battery-cooling/qualification-report.json) also feeds standards reports and passports |

The definition allocates reliability, availability, maintainability and safety
targets from the reference railway boundary to the cooling loop and its flow
and power interfaces. Targets remain null until responsible engineers allocate
and review them. Operator, independent assessor and agreed assessment reference
are explicit prerequisites.

Each allocation declares an allowlisted `metric`, exact `result_path`, `unit`,
`comparison` (`<=` or `>=`), target, review state and applicable
`operating_conditions`. Conditions must match the linked result; mission
probability also binds `mission_h`. The input study declares its condition
envelope in `operating_conditions`. The current metric links cover pump failure
rate, stationary function availability, pump mean repair time and physical
thermal time to limit. These metrics retain their particular scope and do not
constitute a quantified battery-fire risk or railway service-availability claim.

`allocation_results` reports `met`, `not-met` or `undetermined`, with result
bounds, numerical outcome and reasons. The required `all-bounds` treatment
returns `met` only if the entire supported range satisfies the target, `not-met`
if the entire range fails, and `undetermined` if it overlaps. Unsupported input
evidence, unknown dependencies, unvalidated physical predictions, missing
targets or mismatched units/conditions cannot establish `met`. Every result
other than `met` remains an acceptance blocker, even after target review.

## Quantitative methods

| Question | Method | Practical limits |
|---|---|---|
| Time after cooling loss | Analytic lumped heat balance, `C dT/dt = Q - UA(T-Ta)`, with corner sensitivity and temperature trajectories | Constant heat/conductance/ambient; no hydraulic, hotspot, spatial, phase-change or runaway model. Non-crossing cases stay explicit. |
| Failure combinations | Exact Boolean state enumeration and minimal cut sets | Shared/repeated events count once. Unknown software/process events retain uncertainty, with no invented hardware rates. Maximum 16 primitive events. |
| Repairable availability | Same Boolean structure with stationary down fraction `lambda*MTTR/(1+lambda*MTTR)` | Independent exponential failure/repair processes and explicit common causes. Queue competition, wear-out and logistics are outside this availability screen. |
| Latent exposure | Exact time-average undetected probability under periodic proof tests; invert against an exposure budget | Constant hardware rate, perfect detection/restoration and uniform demand timing. Actual coverage, repair exposure and demand need evidence. |
| One braking channel unavailable | Constant effective deceleration and reaction delay against available stopping distance | Grade, adhesion, brake development, target timing and operational authority must support actual restrictions. |
| Spares and repair capacity | M/M/c mean queue wait and Poisson replenishment pipeline | Concurrent crews are not roster headcount. Shift cover, skills, correlated failures and stockout-driven downtime need additional modelling. This does not prove service availability. |
| Design versus cost | Declared failure-rate and residual-cooling alternatives | Cost/performance inputs are illustrative study units. Overlapping uncertainty does not select a supplier or release a design. |

The exponential/HPP assumption follows the
[NIST reliability handbook](https://www.itl.nist.gov/div898/handbook/apr/section3/apr311.htm).
Boolean cut-set reasoning follows the
[NASA fault-tree handbook](https://s3vi.ndc.nasa.gov/ssri-kb/static/resources/Fault%20Tree%20Handbook_NASA.pdf).
These methodological references are not railway conformity decisions. The
thermal, braking and queue screens are tested against analytic cases.

Every interval has `low`, `high`, `unit`, `basis` and `evidence_ids`. Basis is
`unknown`, `illustrative-assumption`, `supplier-data` or `measured`. Unknown
inputs have null bounds. Supplier/measured parameters require controlled,
hashed evidence with review references and validity dates in `input_evidence`.
Corner ranges are sensitivity envelopes, not confidence intervals or validated
physical bounds. Without a declared primitive-independence assumption,
probability and availability quantification remain unresolved.

## Controlled rig programme

Freeze selected pump, connection, circuit, sensors, controller and representative
thermal load with supplier identities and serials. Bind the as-built rig to
the engineering configuration fingerprint. Record the expected serials in
`rig.specimen_serials`; every run must observe those same specimens. Define duty, ambient, flow,
pressure and instrument calibration before execution. Fault injection,
containment, independent shutdown and protection arrangements require competent
review and a recorded hold point.

| Test | Observations |
|---|---|
| Normal duty | Temperature and flow at allocated operating points |
| Pump seizure/circulation loss | Flow loss, detection delay, physical isolation and thermal response |
| Leak/pressure loss | Pressure, leakage response, detection and protection |
| Pump fault plus flow reading stuck high | Remaining diagnostics/protection versus the actual fault |
| Charging, high ambient and fouling | Representative duty and isolation within the approved envelope |
| Shared auxiliary loss | Circulation, primary diagnostics and independent protection/integration response |

Each test has a controlled procedure revision, requirement/scenario links,
acceptance limits, duration, repetitions and model-error tolerance. Values are
intentionally unresolved in the reference programme. Review must establish
that the rig, duty and sampling represent the claim.

Raw measurements use UTF-8 CSV with fixed units/channels:

```text
time_s,temperature_c,ambient_c,flow_l_min,pressure_kpa,fault_active,detected,isolation,derate
```

Times strictly increase; values are finite; digital channels are 0/1.
`fault_onset_s` records commanded onset. Fault scenarios require pre-onset normal
operation: inactive fault, diagnostics and protection, reviewed minimum flow
and baseline duration. `preconditions.digital_state`, `min_flow_l_min` and
`minimum_duration_s` declare that starting state. `response_sequence` declares
the required ordered rising transitions after observed fault onset, normally
diagnosis followed by isolation. A signal already asserted before the fault,
missing baseline, absent transition, reversed order or transitions recorded in
the same sample cannot demonstrate that sequence. Such records retain failed
validation and null delays; an already-isolated rig does not prove fault response.

Every test includes a reviewed `maximum_sample_gap_s` limit. Actual sample gaps
must meet it, and the declared resolution cannot exceed the tightest response
timing criterion. Normal-operation tests cannot include an injected fault or
asserted protection. `response_validation` preserves transition times and
findings; reported delays are observed upper bounds from commanded onset,
without sub-sample interpolation. Sampling and baseline criteria remain null
until competent review determines the resolution and operating state needed.
`isolation` must mean a physical energy-isolation observation, rather than a
controller request.

Each `measurement_runs` entry includes run/test ID, CSV path/hash, configuration
fingerprint, rig and all observed component serials, physical/synthetic origin,
operator, timezone-aware timestamp, procedure revision, fault onset,
channel-to-instrument provenance and signal semantics. Calibration records
include instrument ID, certificate path/hash, `valid_from`, `valid_until` and
temperature uncertainty. `performed_at` is acquisition start; CSV times are
elapsed seconds from it. Calibration must cover the entire acquisition interval,
including the last sample. Date-only certificate bounds include the full UTC
day; explicit timestamps require a timezone. Later expiry does not invalidate
a measurement that was valid at acquisition. Missing starts, future calibration,
expiry during acquisition and changed certificate bytes remain blockers.

`calibration_events` separately records retrospective instrument findings with
ID, `instrument_id`, `discovered_at`, `affected_from`, `affected_until` and
reference. Events match the certificate's `instrument_id` (or its record ID) and
invalidate overlapping runs. `calibration_impact` lists the affected runs;
non-overlapping runs retain their original calibration result. New valid
measurements are needed to replace affected evidence; deleting a finding is not
a revalidation process. Mismatched configuration, missing
physical identity and unresolved/failed criteria stay blocked. Synthetic
fixtures exercise the software and cannot qualify a physical assembly.

## Close the prediction and measurement loop

1. Agree requirement-derived criteria and the assessment approach.
2. Freeze rig configuration, procedure, model parameters and valid envelope.
3. Predict normal/fault temperatures and retain source/input hashes.
4. Capture raw physical temperatures, flows and protection signals.
5. Record maximum model discrepancy, including measurement uncertainty.
6. Investigate differences and revise the design/model under change control.
7. Repeat affected tests against the revised frozen configuration.
8. Validate on separate held-out runs and obtain independent review.

Per-test `thermal_inputs` can define different duty/fault envelopes; otherwise
the compiler uses `physical_thermal`. Those physical parameters are initially
unknown. The compiler compares supplied parameters and does not fit them to
validation data. Calibration and validation run IDs must be disjoint, with
held-out coverage of every declared normal/fault case.

## Production and operational assurance

Critical characteristics allocate torque, flow, pressure and diagnostic latency
to operations and inspection hold points. Production batches bind supplier
batches, serials, process revision, configuration fingerprint, per-serial
results and original inspection evidence. The same checks apply to assemblies
2, 20 and 200. Unmeasured values, different processes/configurations and
synthetic records remain findings.

NCRs retain affected serials, disposition, independent review and requalification
status. Replacement rules bind compatible revisions to supplier evidence and
maintenance instructions; design changes reopen compatibility. Operational
records retain asset serial, failure mode, corrective action, effectiveness and
engineering handback. Administrative closure does not establish handback.

The records use existing manifest and ERP identities. This milestone imports
and checks dossier data and exports a review package; it does not create ERPNext
production orders or approve supplier dispositions.

## Scoped readiness and signed decisions

Workbench recompiles current inputs through a read-only endpoint. It shows
configuration, accepted use, changes, six decision areas, uncertainty,
measurement gaps and manufacturing findings. Reference evidence is explicitly
separate from a city's acceptance. A real package for another city/environment
is withheld from that view.

Existing Ed25519-signed reviews can be verified against an operator-controlled
policy passed through `--review-policy`, or the server's
`OSR_QUALIFICATION_REVIEW_POLICY`. The envelope schema is
`osr-subsystem-review/1`, with reviewer, authorized role, disposition,
reference, validity date, exact evidence/configuration fingerprints and
accepted use where appropriate. The policy enables reviewers, authorizes roles
and pins public-key hashes. Signers must differ from the package owner, executing
identities and exclusion authors.

The qualification subject's assurance scope is derived from its contained
components and dependencies, then followed through the graph to propagated
failure analyses, requirements, evidence, applicability obligations and
dependent gates. `assurance_scope.additional_record_ids` can widen this scope.
Every relevant graph blocker feeds the corresponding readiness area and
prevents subsystem acceptance. The report retains the complete record list,
graph fingerprint and individually identified findings.

An exclusion is a review proposal, not a way to silently remove a finding.
`assurance_scope.exclusions` must identify the exact finding ID, record ID and
current graph fingerprint, with rationale, accountable owner, author, distinct
reviewer and review reference. Both authenticated assessor and design-authority
envelopes must explicitly list the finding in `approved_exclusion_ids`; the
assessor identity and reference must match the exclusion's accountable review.
Missing approvals or changed baselines leave the blocker open. A scoped exclusion
does not accept the graph's railway gate or establish a wider operating release.

Integration records use `kind` values `hil`, `vehicle`, `infrastructure` and
`operations`. Each area requires its own configuration-bound evidence; a passing
HIL record alone leaves the other areas unresolved.

Source, measurement, criteria, configuration and process changes invalidate the
signed scope. Assessor and design-authority decisions are both required.
Review pointers are excluded from the signed evidence fingerprint so adding
the signature does not change its own subject. Every readiness area must also
have current evidence before supplied subsystem acceptance can be displayed.
Vehicle/railway authorization remains separate and `release_ready` stays false.
No trusted reviewer policy or acceptance signatures are supplied by default.

## Reproduce and export

```bash
python3 tools/automation/subsystem_qualification.py
python3 tools/automation/subsystem_qualification.py --check
python3 tools/automation/subsystem_qualification.py --stdout
python3 tools/automation/subsystem_qualification.py --plan path/to/definition.json --stdout
python3 tools/automation/subsystem_qualification.py --export build/qualification/cooling-dossier.zip
python3 tools/automation/digital-assurance.py
python3 tools/automation/component_assurance.py
```

The export contains the effective definition, readable results and original
checksummed input/evidence bytes. It checks for changes during export.

To close the physical milestone, supply the selected supplier/rig definition,
agreed targets/criteria, calibration certificates, normal/fault measurements,
production inspections, held-out validation and independently reviewed results.
The current software makes those missing inputs explicit and provides the
executable assessment process.
