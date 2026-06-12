# Samawah Acceptance And Accreditation Evidence Basis

This report is the generated evidence basis for acceptance, trial-running
readiness, and accreditation review. It is not itself an approval or
certificate; it is the traceability index that shows which assets,
manufacturing packages, BOM/material refs, QA hold points, evidence
records, release authorities, and predecessor controls must be closed.

## Summary

| Item | Count / Status |
|---|---:|
| Assets in register | 316 |
| Manufacturing schedule rows | 937 |
| Manufacturing material/BOM rows | 13,084 |
| Manufacturing QA verification rows | 937 |
| Construction QA action rows | 954 |
| Maintenance handover schedule rows | 1,086 |
| Manufacturing rows with material refs | 937 / 937 |
| Manufacturing rows with verification refs | 937 / 937 |
| Manufacturing rows linked to QA actions | 937 / 937 |
| Unresolved external predecessors | 0 |

## Material / BOM Basis

| Source | Rows |
|---|---:|
| `project_kit` | 2,236 |
| `rolling_stock_bom` | 10,176 |
| `rolling_stock_cots_fitout` | 672 |

Rolling-stock rows link to the generated rolling-stock BOM and COTS
fit-out BOM. Infrastructure rows use controlled `project_kit:*` refs
until detailed civil/station/energy BOMs are added.

## QA Gate Coverage

| QA gate | Verification rows |
|---|---:|
| `qa-00-design-freeze` | 1 |
| `qa-10-carbody-structure` | 96 |
| `qa-11-bogie-wheelset` | 96 |
| `qa-12-traction-brake-battery` | 96 |
| `qa-13-passenger-systems` | 96 |
| `qa-15-first-article-trainset` | 96 |
| `qa-20-survey-geotech` | 28 |
| `qa-21-earthworks-drainage` | 28 |
| `qa-22-trackform-rail` | 144 |
| `qa-24-stations-depots-plant` | 74 |
| `qa-25-power-energy` | 64 |
| `qa-26-wayside-comms-safety` | 118 |

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

## Review Artifacts

- Operations bundle: [`docs/operations-portal/data/samawah-operations.json`](../../docs/operations-portal/data/samawah-operations.json)
- Evidence matrix CSV: [`docs/operations-portal/data/samawah-acceptance-evidence-matrix.csv`](../../docs/operations-portal/data/samawah-acceptance-evidence-matrix.csv)
- Manufacturing schedule CSV: [`docs/operations-portal/data/samawah-manufacturing-schedule.csv`](data/samawah-manufacturing-schedule.csv)
- Manufacturing materials CSV: [`docs/operations-portal/data/samawah-manufacturing-materials.csv`](data/samawah-manufacturing-materials.csv)
- Manufacturing verification CSV: [`docs/operations-portal/data/samawah-manufacturing-verification.csv`](data/samawah-manufacturing-verification.csv)
- QA register CSV: [`docs/operations-portal/data/samawah-qa-register.csv`](data/samawah-qa-register.csv)
- Maintenance schedule CSV: [`docs/operations-portal/data/samawah-maintenance-schedule.csv`](data/samawah-maintenance-schedule.csv)

## Accreditation Use

The evidence matrix can be filtered by asset, package, QA gate, release
authority, or material source. During acceptance, each row should be
matched to completed Ops Core evidence, defects/NCR status, and the
release authority signoff before the related asset is accepted into
trial running or passenger operation.
