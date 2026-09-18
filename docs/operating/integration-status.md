# Integrated operating software: completion and deployment inputs

This register covers the requested ERPNext/FUXA/OpenSourceRail software integration
and its reusable city workflows. The published [v0.4.0 baseline](../release-v0.4.md)
is immutable; the disposition enhancements below are recorded in
[Unreleased](../../CHANGELOG.md). Software acceptance uses simulation and temporary
ERP transactions. Physical deployment and independent acceptance have their own
evidence gates.

## Implemented software

| Task | Implementation and acceptance |
|---|---|
| ERP business backbone | Pinned ERPNext/Frappe HR deployment, native projects/tasks, procurement, stock, manufacturing, quality, assets, maintenance, finance and workforce components; [deployment](../../deployment/erpnext/README.md) and native component/procurement tests |
| Generic and city-specific configuration | Shared component/equipment templates, per-city project/company mappings, 266 validated profiles and reproducible task payload generation; [city platform](city-platform.md) and [readiness](readiness.md) |
| One connected UI | Workbench embeds authenticated ERP and FUXA and carries city/equipment context to OSR controls, engineering and lifecycle screens; [guide and screenshots](../workbench/README.md) |
| Engineering tools and digital twin | Reviewed execution mappings, FreeCAD/IFC/Bonsai/GIS evidence references, stable equipment identities, installed serial history and revision impact; [lifecycle guide](../lifecycle/README.md) |
| Rust and embedded supervision | Shared controller contracts, native simulation bridge, quality/timestamps, command request/result states and maintained historian; [embedded contract](../lifecycle/embedded-integration.md) |
| Alarm to maintenance and handback | Durable condition-event delivery, deduplicated Issues, reviewed Asset Repairs, native parts/actuals, and independent OSR inspection/handback; native lifecycle and controller acceptance |
| Engineering revision disposition | Permission-filtered BOM/order/material exposure, assigned immutable proposals, independent endorsement/rejection, stale review rejection and evidence download |
| All disposition outcome types | Registry-driven retention, cancellation, direct amendment, production stop, corrective work plus accepted inspection, performed inspection and reconciled movement trace; [exact checks and limits](../lifecycle/README.md#independent-native-outcome-verification) |
| Reproducible acceptance and recovery | Unit/browser tests plus disposable native stack workflow, including service outage/recovery; [CI definition](../../.github/workflows/integrated-stack.yml) |
| Documentation and publication | Root README, current deployment/workflow guides, changelog and generated reader book; published v0.4.0 remains the historical release baseline |

The outcome registry is in
[`outcome_contract.py`](../../deployment/erpnext/apps/osr_erpnext/osr_erpnext/outcome_contract.py).
It drives native document selectors in the ERP dialog. Native readers enforce
permissions; pure checks validate document relationships and measurements.
Verification records bind the evidence selection, observed data, reviewer and
exposure checksum. The same implementation uses each city's existing project,
company and engineering mapping; no city-specific verifier code is required.

## Complete example city

The [isolated Samawah scenario](../../deployment/example-city/README.md) adds a
retained end-to-end city lifecycle and settings matrix, with Mosul as a control.
It includes actual native ERP records and unmocked browser checks. Its report
separates full planning coverage, selected live equipment and physical acceptance
limits. The [push/PR/manual CI workflow](../../.github/workflows/example-city.yml) publishes
public reports and screenshots while keeping credentials private. The recorded
18 September 2026 local run passed 98 lifecycle/settings/recovery checks, including
ten real-service browser checks and a full stop/start. Its separate whole-city
contract sweep covered 573 equipment positions and 1,610 measurements. This records
local verification; candidate CI evidence must be checked separately by exact commit.

The additional `expand-check` passed 389 live/native/restoration assertions and a
separate 230-check schema matrix. Its [coverage register](../../deployment/example-city/coverage-register.md)
tracks 518 integration entries: 36 scenario, 64 varied, 135 partial and 283 without
qualifying evidence. Payment posting/cancellation is exercised transactionally;
other remaining workflows are listed explicitly. Passing examples do not establish
coverage of every function or variable combination.

`business-check` adds 24 native outcome/rollback checks for actual budget enforcement,
assignment, replenishment and training. `disposition-check` adds nine unmocked browser
checks using three native identities, including stale verification after a subsequent
native action. The release gate now requires this city workflow and validates its
commit-bound report hashes. See the [review follow-through](review-follow-through.md)
for cross-domain freshness, controller fixes, broader proof execution and open gates.

The implementation candidate `92b20ff32` passed general CI, integrated-stack and
complete-city CI. Its broader formal run passed 30 of 41 declared Kani harnesses;
11 timed out, so release packaging remains blocked. Local fresh-volume ERP restore
rehearsals checked database records, ledger entries, public/private files and
encrypted settings. Coordinated FUXA/gateway/OSR recovery and independent acceptance
remain open. The [review record](review-follow-through.md#integration-candidate-and-erp-recovery)
links the exact runs and explains the recovery scope.

## Acceptance commands

The CI workflow creates a disposable deployment and runs:

- `deployment/erpnext/tests/verify-components.py`, `verify-procurement.py` and
  `verify-lifecycle.py` inside the ERP backend. Transactional business fixtures
  roll back, including native cancellation, amendment, corrective Job Cards,
  inspections and manufactured batch trace.
- `deployment/workbench/tests/verify-dispositions.mjs` against real ERP Desk
  widgets with mocked business responses, exercising dynamic evidence fields and
  explicit preview/record. The native Python tests separately verify actual ERP
  records and permissions.
- FUXA, pilot, embedded, native Workbench and outage checks in the sequence
  specified by the integrated-stack workflow.
- `tools/automation/tests/test_outcome_contract.py` and
  `test_outcome_evidence.py` for invalid identities, scope, quantities, readings,
  missing evidence and unrelated source changes; lifecycle browser tests for
  current/stale status and city scoping.

Run these against a disposable or local simulation installation. Pilot/controller
tests record explicitly labelled simulation evidence; they are not physical
commissioning procedures. Site credentials remain in private local configuration.

## Inputs that remain open for deployment

| Required input or acceptance | Why software cannot close it |
|---|---|
| Legal companies, operating calendars, approved ERP masters and role assignments | Must be supplied and approved by each owner/operator |
| Surveyed alignment, released geometry, supplier configurations and engineering evidence | Generated reference geometry and analysis links do not replace received site/supplier data or design approval |
| Physical controller addresses, protocols, calibration and machine/quality inputs | Simulation bindings are not commissioned equipment bindings |
| Production identity/TLS/MFA, hosted backup operation and recovery acceptance | The localhost evaluation stack is not an operated shared production environment |
| Performed manufacturing inspections, accepted configuration and first articles | Native test readings demonstrate software behaviour; real production evidence must be received and independently accepted |
| Signed physical commands, HIL, operator validation and railway release | ERP completion and native outcome verification do not authorise railway service |

The broader [roadmap](../ROADMAP.md) retains operating-capacity/energy validation,
full CAD/solver change propagation and the physical release workstreams. Completion
of this software integration does not mark those separate workstreams complete.
