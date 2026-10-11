# Engineering integration review — 11 October 2026

The [23-item integration programme](../../engineering/integration_programme/data/programme.json)
records the remaining review work, implemented capabilities and external evidence
requirements. Implementation, numerical verification, physical correlation and
independent acceptance are separate states. This work does not close production,
site deployment, hardware qualification or railway conformity gates.

## Reproducibility and native assembly

The publication check preserves exact configuration, source and retained-artifact
hashes. Recomputed solver observables have narrowly named numerical reproduction
tolerances; engineering limits and acceptance flags remain exact. Baghdad's
connected-build package was regenerated. The dependency scanner reports stale
current packages separately from retained historical records.

The expanded train contains **414 instances, 413 joints and 545 interfaces**.
Conductor/insulation sections, connectors, coolant pipes/clamps and door seals
are original study designs. Their masses are extracted once from residual
allocations. The assembled mass is **201,240.10827341524 kg**. These additions do
not complete the inventory: **1,157 of 1,367 allocation slots remain unresolved**,
and the 210 mapped slots include partial kits. The
[native twin](../../engineering/models/digital-twins/best-practice/index.html)
retains occupied-solid, assembly-constraint, inertia, drawing and STEP checks.

## Open examples and represented physics

[OSRD's physical model](https://osrd.fr/en/docs/explanation/running_time_calculation/physical_modeling/)
informs force balances and effort/resistance handling. Its retained fictional
commuter example is pinned to an exact upstream commit, Git blob and byte hash.
The schema's per-kilogram Davis coefficients are converted once. Conditional
curves, supply mode and train-tail speed-limit clearance remain explicit. The
390,000 kg, 110 m example and its 1.5/25 kV supply modes are **not adopted as OSR
ratings**. Its LGPL-3.0-only data notices and licence texts are retained.

[CONTACT](https://github.com/eve70a/CONTACT) contributes nominal Manchester
benchmark files: 399 wheel and 495 rail points, retained with Apache-2.0 notices,
source hashes and transformation metadata. Raw ingestion does not establish the
axis/side/datum transform, approved project profiles, flange or multiple-contact
support. The external CONTACT solver has not been executed here. The
[research register](../../engineering/integration_programme/data/research.json)
also distinguishes researched RCM-DX interoperability from an implemented adapter.

Yaw rolling-reference kinematics were corrected without weakening contact-domain
guards. Complete six-car reference and expanded-twin passages were executed.
Separate reference time refinement and spatial refinement reach the registered
5% numerical screen at the finest retained levels. This is one configuration's
numerical comparison, not an accepted operating envelope or an ISO ride rating.
All 22 baseline cases were attempted: 17 completed, two exceeded the old
duration budget, two left the contact domain, and the two-train run exceeded its
wall budget. Fresh 414-instance rescue and maintenance passages both completed
39.18 seconds; its fresh two-train run also completed the passage. These
configuration-specific records do not merge into an accepted common envelope.
The [contact investigation](../civil/full-train-contact-domain.md) retains the
older failures and explains the corrected scope. The
[published evidence manifest](../../engineering/integration_programme/evidence/manifest.json)
binds compact review results to actual execution receipts; large histories remain
in the ignored local build evidence. Historical source scopes are labelled.

The spatial solver can now separate battery equipment mass from the carbody,
solve finite six-direction retention joints from the actual mounting-hole
coordinates, and insert work-conjugate carbody beam modes into the same sparse
mechanical solve. Native Rust BMS, traction, brake and thermal controllers exchange
states with six separate battery plants. Converged wheel speeds determine drive
work, friction heat and electrical/thermal evolution; each auxiliary load is
counted once. One-second experiments include a pump/fire protection fault and
separate timestep comparisons. Coarse failed comparisons are retained. The final 3,200-to-6,400-step comparison
passes the 5% research screen (contact force 3.683%, wheel unloading 0.7845%);
spatial, operating-envelope and physical qualification remain open.
These experiments use prescribed transport with bounded perturbations, assumed
maps, equivalent cells and reduced beam modes. They do not transfer measured
shell/bogie modes or qualify a complete service passage with native control.

The native hollow carbody shell, its four door portals and modal output remain an
independent proposed structural study. Complete bogie structure, local production
joints, nonlinear civil resistance and physical modal/force correlation remain
open. The civil audit accounts for all 38 displayed instances and explicitly
reports unreconciled sections/masses/datums and undisplayed pier/foundation domains.
An association with a beam/spring is not geometric or material equivalence.

The search compiles battery topology through the shared variant/design compiler
and screens complete passages. Each method/seed has an equal time quota, cache
use is reported, and finalist time is reserved. Temporal and spatial refinement
are separate; refined results are checked against adopted limits. Unknown limits,
resistance or complete installed costs exclude qualified feasible Pareto claims.

## Native software lifecycle

Coincident City Studio markers have separate ordinary click targets and leaders;
canonical surveyed coordinates and intentional dragging are preserved. Native
example lifecycle, browser selection, restart and disposition checks were rerun.
The ERP business suite executes 35 checks covering reviewed resource/crew release,
assignment strategies, attendance/payroll, procurement commitment budgets, asset
opening/depreciation journals and SLA holiday calendars. Fixture transactions are
rolled back and private fixture files removed. Payroll examples are not adopted
jurisdictional policy or employee payments.

Submitted fleet lifecycle changes now use the existing role guard, with only the
lifecycle custom field editable after submission. Cost fields remain protected.
All isolated ERP application services were rebuilt/recreated with the new code.
The actual production ERP deployment was not changed.

A fresh coordinated checkpoint preserves runtime temporary mounts and immutable
image IDs. Its isolated rehearsal verified ten volume inventories, signing
identity, ERP/encryption state, queue lost-reply reconciliation and HTTP services,
then removed its own restore resources. Source writers resumed. This is a
same-host fresh-volume rehearsal; separately hosted cutover, resumed destination
controllers/jobs and adopted RPO/RTO remain open. Public reports contain results;
private checkpoint credentials, state and archives are not published.

## Remaining acceptance and release boundaries

All nine previously open Kani obligations were attempted with complete checks,
900-second timeouts and 6 GiB memory limits. Eight memory failures and one timeout
establish no proof. Alternative backend errors are retained. The TLA+ to Rust
consensus refinement argument remains unresolved. Passing a bounded CI subset
does not close these obligations.

No supplier test records, calibrated prototype observations, selected controller
hardware records or approved wheel/rail profiles were available. Accordingly,
physical serial/measurement ingress, calibration validity, independent condition
revisions and analysis invalidation are implemented, while physical correlation
and release remain open. The 15 Baghdad deployment gates, real process windows,
material grades, first articles, full civil resistance, actual targets, quotations,
manufacturing rights and support commitments still require their actual records.

[OSR-INT-001](../standards/OSR-INT-001.md) is the original open internal integration
standard. ISO and industry references inform methods; configuration-specific
clause adoption and authority acceptance are not inferred. Station vehicle-fire
HL1 claims were removed, and IEC 60439/61439 assembly applicability was corrected.

The retained local lifecycle began on a working tree under development. It is
representative software evidence, not clean-commit release acceptance. The
existing `example-city` CI workflow reruns the lifecycle on the pushed clean
candidate and separately records release evidence. Its result must be checked;
local passing reports are not relabelled as that release run.
