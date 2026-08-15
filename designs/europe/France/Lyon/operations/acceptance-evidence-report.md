# Lyon Acceptance And Accreditation Evidence Basis

This report is the generated evidence basis for acceptance, trial-running
readiness, and accreditation review. It is not itself an approval or
certificate; it is the traceability index that shows which assets,
manufacturing packages, BOM/material refs, QA hold points, evidence
records, release authorities, and predecessor controls must be closed.

## Summary

| Item | Count / Status |
|---|---:|
| Assets in register | 824 |
| Manufacturing schedule rows | 3,093 |
| Manufacturing material/BOM rows | 45,895 |
| Manufacturing QA verification rows | 3,093 |
| Construction QA action rows | 2,868 |
| Maintenance handover schedule rows | 3,712 |
| Manufacturing rows with material refs | 3,093 / 3,093 |
| Manufacturing rows with verification refs | 3,093 / 3,093 |
| Manufacturing rows linked to QA actions | 3,093 / 3,093 |
| Unresolved external predecessors | 0 |

## Material / BOM Basis

| Source | Rows |
|---|---:|
| `project_kit` | 5,296 |
| `rolling_stock_bom` | 38,170 |
| `rolling_stock_cots_fitout` | 2,429 |

Rolling-stock rows link to the generated rolling-stock BOM and COTS
fit-out BOM. Infrastructure rows use controlled `project_kit:*` refs
until detailed civil/station/energy BOMs are added.

## QA Gate Coverage

| QA gate | Verification rows |
|---|---:|
| `qa-00-design-freeze` | 1 |
| `qa-10-carbody-structure` | 694 |
| `qa-11-bogie-wheelset` | 347 |
| `qa-12-traction-brake-battery` | 347 |
| `qa-13-passenger-systems` | 347 |
| `qa-15-first-article-trainset` | 347 |
| `qa-20-survey-geotech` | 79 |
| `qa-21-earthworks-drainage` | 79 |
| `qa-22-trackform-rail` | 205 |
| `qa-24-stations-depots-plant` | 172 |
| `qa-25-power-energy` | 147 |
| `qa-26-wayside-comms-safety` | 328 |

## Acceptance Control Logic

- Every manufacturing package has a controlled material/BOM row set.
- Every manufacturing package has a QA verification row.
- Every verification row links to a generated QA action by `qa_uid`.
- Resolved predecessor ids are generated for schedule blocking.
- The portal blocks successor manufacturing work until predecessor
  work orders are closed with pass evidence.
- The portal blocks manufacturing closeout until the selected work
  order has pass evidence.
- Failed evidence creates a defect/NCR and puts the work order on hold.
- SQLite-backed Ops Core stores work orders, inspections, defects/NCR,
  and audit records for handover.

## Remaining External Release Gates

This generated evidence basis organizes acceptance work, but it does
not close release gates that require independent review, field data,
hardware bring-up, supplier freeze, first-article tests, or authority
acceptance. The open gates remain:

| Gate family | Still required before accreditation / revenue release |
|---|---|
| Independent safety assessment and residual risk | Named ISA/assessor review, action log, residual-risk acceptance, and deployment-specific ALARP/tolerability decision. |
| Formal safety integration | Consensus refinement proof from TLA+ to implementation behavior, plus signed safety-log integration tests for forged, replayed, stale, and unknown-issuer entries. |
| Pilot hardware evidence | Exact COTS BOM freeze, wiring/harness maps, enclosure/mounting, power/thermal margins, SD image checksums, self-test logs, bench/safety evidence, and commissioning records for T-ECU/S, T-ECU/A, T-OBS, W-SBC, and S-SBC. |
| Rolling-stock production release | Supplier envelope freeze, EN structural/FEA reports, weld/WPS/NDT packages, manufacturing drawings, flat patterns/NC output, harness routing, weight/balance, first-car build hold point, and first-article inspection. |
| Field validation | Obstacle/intrusion sensor calibration and representative hot-weather, dust/soiling, night, and rain datasets with false-positive/false-negative analysis. |
| Charging and site energy | Site-specific solar yield, grid interconnect, charger thermal study, protection settings, utility approval, and train charging interface tests. |
| Operations validation | Operator workshops, translated/deployment rulebook where needed, competence records, emergency exercises, maintenance access trials, and trial-running records. |

Those items are tracked in the
[certification release gap register](../../../../../docs/certification/release-gap-register.md),
[hardware release checklist](../../../../../hardware/release-checklist.md),
and
[rolling-stock v2 release checklist](../../../../../docs/rolling-stock/light-metro-3car/v2-release-checklist.md).
The acceptance matrix should be treated as the evidence index that
collects those closures, not as the closure itself.

## Review Artifacts

- Operations bundle: [`lyon-operations.json.gz`](lyon-operations.json.gz)
- Evidence matrix CSV: [`lyon-acceptance-evidence-matrix.csv`](lyon-acceptance-evidence-matrix.csv)
- Manufacturing schedule CSV: [`lyon-manufacturing-schedule.csv`](lyon-manufacturing-schedule.csv)
- Manufacturing materials CSV: [`lyon-manufacturing-materials.csv`](lyon-manufacturing-materials.csv)
- Manufacturing verification CSV: [`lyon-manufacturing-verification.csv`](lyon-manufacturing-verification.csv)
- QA register CSV: [`lyon-qa-register.csv`](lyon-qa-register.csv)
- Maintenance schedule CSV: [`lyon-maintenance-schedule.csv`](lyon-maintenance-schedule.csv)

## Accreditation Use

The evidence matrix can be filtered by asset, package, QA gate, release
authority, or material source. During acceptance, each row should be
matched to completed Ops Core evidence, defects/NCR status, and the
release authority signoff before the related asset is accepted into
trial running or passenger operation.
