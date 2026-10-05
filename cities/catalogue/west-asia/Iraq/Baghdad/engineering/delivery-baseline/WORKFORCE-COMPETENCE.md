# Baghdad workload, recruitment and competence pilot

<!-- OSR CURRENT SCOPE CONTEXT -->
> **Original catalogue or earlier scope reference.** The figures and policies below retain their original assumptions; they are not the latest Baghdad staffing, depot, procurement or funding basis. See the [current Baghdad recalculation](../programme-recalculation/README.md) and [current city summary](../../README.md). National/portfolio totals have not been repriced with that conditional Baghdad option.
<!-- END OSR CURRENT SCOPE CONTEXT -->

The prior **3,460 FTE / USD 38.552m/year** allowance is USD 928.52/person/month. The existing 21-role weighted split remains a budget allocation, not shift cover. This separate [establishment](workforce-establishment.csv) derives posts/task hours, 1520 productive hours per FTE after leave, training, sickness and travel/handovers, integer cover and editable grade pay with employer/overtime allowances.

| Function | Annual workload h | Concurrent posts | Reference FTE | Loaded annual IQD m |
| --- | --- | --- | --- | --- |
| occ-lead | 7,482 | 1 | 5 | 157.9 |
| dispatcher | 67,342 | 9 | 45 | 947.7 |
| remote-assist | 658,460 | 88 | 437 | 9,203.2 |
| station-lead | 142,168 | 19 | 101 | 3,190.6 |
| platform-assistance | 1,391,745 | 186 | 920 | 11,625.1 |
| customer-service | 351,678 | 47 | 234 | 2,956.8 |
| station-cleaning | 203,670 | 0 | 139 | 1,756.4 |
| workshop-lead | 37,440 | 9 | 27 | 852.9 |
| fleet-mechanical | 370,560 | 0 | 249 | 5,243.9 |
| fleet-electrical | 247,040 | 0 | 166 | 3,496.0 |
| fleet-finish-cleaning | 563,560 | 0 | 376 | 4,751.1 |
| infrastructure-lead | 18,720 | 9 | 18 | 568.6 |
| civil-track | 153,284 | 0 | 106 | 2,232.4 |
| solar-storage | 98,400 | 0 | 69 | 1,453.1 |
| wayside-comms | 74,400 | 0 | 55 | 1,158.3 |
| city-director | 1,520 | 1 | 1 | 31.6 |
| chief-engineer | 1,520 | 1 | 1 | 31.6 |
| quality-safety | 34,600 | 0 | 23 | 726.6 |
| training | 38,320 | 0 | 26 | 547.6 |
| procurement-stores | 28,740 | 0 | 19 | 400.1 |
| finance-people | 19,160 | 0 | 13 | 273.8 |

Reference total is **3,030 operating FTE**, loaded payroll **USD 39.696m/year equivalent**. Quantities are explicit task-hour/post assumptions, **not measured local work or accepted Iraqi pay/rest terms**. Higher overtime, emergency cover, queues, simultaneous faults and actual maintenance could change them. The dedicated solar plant specialist workload is unpriced. Maintenance contracts and payroll must be reconciled to avoid adding contractor labour twice to existing envelopes. No revised OPEX is silently adopted.

Factory 1,112 direct staffed-shift positions are separate; their production payroll is already in train procurement. Construction crew counts remain unknown and separate, rather than scheduled task slots called people. Temporary commissioning has its own cash requirement.

[Recruitment cohorts](recruitment-cohorts.csv) work backwards from each conditional line opening through requisition, selection, joining, training, first/repeated assessment and supervised experience. Offers allow 15% pre-join attrition and 80% first-pass / 75% repeat-pass assumptions. Hiring alone provides zero authorised productive capacity. Paid pre-opening training plus trainer/assessor reference cash is IQD 35.268bn; additional three-month commissioning payroll is IQD 0.853bn. These are distinct pre-opening uses, with overlap against EPC still unverified; rigs, agency fees and local terms remain unquoted. No trained/appointed person is invented.

[Seven controlled curriculum drafts](training-curricula.json) cover induction, OCC, stations/accessibility, fleet, civil/energy, factory and supervisors/assessors. Each lists prerequisites, method revision, equipment, practical exercises, critical assessment criteria, assessor requirements and retraining triggers. [Arabic glossary](arabic-glossary.json) is a draft requiring native technical review; full Arabic lessons are pending. Attendance, practical competence and scoped task authorisation are separate records.

The [seven-day first-corridor OCC roster](pilot-roster.json) contains actual service-hour coverage requirements and **zero named workers**. Every slot is blocked pending appointments and task-specific authorisation. The executable [eligibility evaluator](../../../../../../../engineering/analysis/workforce_checks.py) checks worker record, assessed task/asset-family/location/method scope, validity, suspension, skill fade, availability, checked rest, access, permits, tools/materials, competent supervision and independent verification. Evaluate both at planning and task start; changed or expired evidence blocks eligibility. It creates no assignment or operational release.

Department owns outcomes/budget/risk; unit owns assets/backlog; crew owns executable access-window work; worker owns a scoped method/evidence; verifier owns independent acceptance/handback. [Native ERP mappings](native-workforce-map.json) retain Staffing Plan/recruitment/Employee/onboarding/training/shift records, manufacturing Work Order/Job Card and maintenance Asset Maintenance/Asset Repair, with Project/Task for programme evidence. Dashboards track accepted output, blocks, competence expiry, shortages, overdue hazards and forecast cost; attendance or Task closure never counts as physical acceptance. Deploy permissions/recovery/rest rules against actual records before enabling assignment.

[Frappe staffing documentation](https://docs.frappe.io/hr/staffing-plan) supports administrative records. [ORR competence guidance](https://www.orr.gov.uk/guide-rogs/7-managing-safety-critical-work) is a useful reference for assessment/monitoring/reassessment, not Iraqi legal approval. References checked 4 October 2026.
