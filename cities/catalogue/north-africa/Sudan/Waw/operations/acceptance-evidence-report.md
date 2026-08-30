# Waw Acceptance And Accreditation Evidence Basis

This report is the generated evidence basis for acceptance, trial-running
readiness, and accreditation review. It is not itself an approval or
certificate; it is the traceability index that shows which assets,
manufacturing packages, BOM/material refs, QA hold points, evidence
records, release authorities, and predecessor controls must be closed.

## Summary

| Item | Count / Status |
|---|---:|
| Assets in register | 97 |
| Manufacturing schedule rows | 360 |
| Manufacturing material/BOM rows | 5,391 |
| Manufacturing QA verification rows | 360 |
| Construction QA action rows | 339 |
| Maintenance handover schedule rows | 422 |
| Manufacturing rows with material refs | 360 / 360 |
| Manufacturing rows with verification refs | 360 / 360 |
| Manufacturing rows linked to QA actions | 360 / 360 |
| Unresolved external predecessors | 0 |

## Material / BOM Basis

| Source | Rows |
|---|---:|
| `project_kit` | 594 |
| `rolling_stock_bom` | 4,510 |
| `rolling_stock_cots_fitout` | 287 |

Rolling-stock rows link to the generated rolling-stock BOM and COTS
fit-out BOM. Infrastructure rows use controlled `project_kit:*` refs
until detailed civil/station/energy BOMs are added.

## QA Gate Coverage

| QA gate | Verification rows |
|---|---:|
| `qa-00-design-freeze` | 1 |
| `qa-10-carbody-structure` | 82 |
| `qa-11-bogie-wheelset` | 41 |
| `qa-12-traction-brake-battery` | 41 |
| `qa-13-passenger-systems` | 41 |
| `qa-15-first-article-trainset` | 41 |
| `qa-20-survey-geotech` | 6 |
| `qa-21-earthworks-drainage` | 6 |
| `qa-22-trackform-rail` | 32 |
| `qa-24-stations-depots-plant` | 20 |
| `qa-25-power-energy` | 19 |
| `qa-26-wayside-comms-safety` | 30 |

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
[certification release gap register](../../../../../../docs/certification/release-gap-register.md),
[control-electronics release checklist](../../../../../../control-electronics/release-checklist.md),
and
[rolling-stock v2 release checklist](../../../../../../docs/rolling-stock/light-metro-3car/v2-release-checklist.md).
The acceptance matrix should be treated as the evidence index that
collects those closures, not as the closure itself.

## Review Artifacts

- Operations bundle: [`waw-operations.json.gz`](waw-operations.json.gz)
- Evidence matrix CSV: [`waw-acceptance-evidence-matrix.csv`](waw-acceptance-evidence-matrix.csv)
- Manufacturing schedule CSV: [`waw-manufacturing-schedule.csv`](waw-manufacturing-schedule.csv)
- Manufacturing materials CSV: [`waw-manufacturing-materials.csv`](waw-manufacturing-materials.csv)
- Manufacturing verification CSV: [`waw-manufacturing-verification.csv`](waw-manufacturing-verification.csv)
- QA register CSV: [`waw-qa-register.csv`](waw-qa-register.csv)
- Maintenance schedule CSV: [`waw-maintenance-schedule.csv`](waw-maintenance-schedule.csv)

## Accreditation Use

The evidence matrix can be filtered by asset, package, QA gate, release
authority, or material source. During acceptance, each row should be
matched to completed Ops Core evidence, defects/NCR status, and the
release authority signoff before the related asset is accepted into
trial running or passenger operation.
