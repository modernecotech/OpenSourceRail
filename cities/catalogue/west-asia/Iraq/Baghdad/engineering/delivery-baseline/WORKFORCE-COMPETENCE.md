# Baghdad workload, recruitment and competence pilot

The prior **10,782 FTE / USD 115.993m/year** allowance is USD 896.50/person/month. The existing 21-role weighted split remains a budget allocation, not shift cover. This separate [establishment](workforce-establishment.csv) derives posts/task hours, 1520 productive hours per FTE after leave, training, sickness and travel/handovers, integer cover and editable grade pay with employer/overtime allowances.

| Function | Annual workload h | Concurrent posts | Reference FTE | Loaded annual IQD m |
| --- | --- | --- | --- | --- |
| occ-lead | 7,482 | 1 | 5 | 157.9 |
| dispatcher | 404,055 | 54 | 270 | 5,686.2 |
| remote-assist | 1,735,940 | 232 | 1175 | 24,745.5 |
| station-lead | 448,950 | 60 | 312 | 9,856.1 |
| platform-assistance | 4,489,500 | 600 | 2982 | 37,680.6 |
| customer-service | 1,122,375 | 150 | 765 | 9,666.5 |
| station-cleaning | 657,000 | 0 | 459 | 5,799.9 |
| workshop-lead | 224,640 | 54 | 162 | 5,117.6 |
| fleet-mechanical | 992,160 | 0 | 676 | 14,236.6 |
| fleet-electrical | 661,440 | 0 | 462 | 9,729.7 |
| fleet-finish-cleaning | 1,508,910 | 0 | 1025 | 12,951.9 |
| infrastructure-lead | 112,320 | 54 | 108 | 3,411.7 |
| civil-track | 276,456 | 0 | 210 | 4,422.6 |
| solar-storage | 317,400 | 0 | 232 | 4,885.9 |
| wayside-comms | 240,000 | 0 | 187 | 3,938.2 |
| city-director | 1,520 | 1 | 1 | 31.6 |
| chief-engineer | 1,520 | 1 | 1 | 31.6 |
| quality-safety | 75,897 | 0 | 50 | 1,579.5 |
| training | 106,680 | 0 | 71 | 1,495.3 |
| procurement-stores | 80,010 | 0 | 53 | 1,116.2 |
| finance-people | 53,340 | 0 | 36 | 758.2 |

Reference total is **9,242 operating FTE**, loaded payroll **USD 120.999m/year equivalent**. Quantities are explicit task-hour/post assumptions, **not measured local work or accepted Iraqi pay/rest terms**. Higher overtime, emergency cover, queues, simultaneous faults and actual maintenance could change them. The dedicated solar plant specialist workload is unpriced. Maintenance contracts and payroll must be reconciled to avoid adding contractor labour twice to existing envelopes. No revised OPEX is silently adopted.

Factory 743 direct staffed-shift positions are separate; their production payroll is already in train procurement. Construction crew counts remain unknown and separate, rather than scheduled task slots called people. Temporary commissioning has its own cash requirement.

[Recruitment cohorts](recruitment-cohorts.csv) work backwards from each conditional line opening through requisition, selection, joining, training, first/repeated assessment and supervised experience. Offers allow 15% pre-join attrition and 80% first-pass / 75% repeat-pass assumptions. Hiring alone provides zero authorised productive capacity. Paid pre-opening training plus trainer/assessor reference cash is IQD 110.093bn; additional three-month commissioning payroll is IQD 5.118bn. These are distinct pre-opening uses, with overlap against EPC still unverified; rigs, agency fees and local terms remain unquoted. No trained/appointed person is invented.

[Seven controlled curriculum drafts](training-curricula.json) cover induction, OCC, stations/accessibility, fleet, civil/energy, factory and supervisors/assessors. Each lists prerequisites, method revision, equipment, practical exercises, critical assessment criteria, assessor requirements and retraining triggers. [Arabic glossary](arabic-glossary.json) is a draft requiring native technical review; full Arabic lessons are pending. Attendance, practical competence and scoped task authorisation are separate records.

The [seven-day first-corridor OCC roster](pilot-roster.json) contains actual service-hour coverage requirements and **zero named workers**. Every slot is blocked pending appointments and task-specific authorisation. The executable [eligibility evaluator](../../../../../../../engineering/analysis/workforce_checks.py) checks worker record, assessed task/asset-family/location/method scope, validity, suspension, skill fade, availability, checked rest, access, permits, tools/materials, competent supervision and independent verification. Evaluate both at planning and task start; changed or expired evidence blocks eligibility. It creates no assignment or operational release.

Department owns outcomes/budget/risk; unit owns assets/backlog; crew owns executable access-window work; worker owns a scoped method/evidence; verifier owns independent acceptance/handback. [Native ERP mappings](native-workforce-map.json) retain Staffing Plan/recruitment/Employee/onboarding/training/shift records, manufacturing Work Order/Job Card and maintenance Asset Maintenance/Asset Repair, with Project/Task for programme evidence. Dashboards track accepted output, blocks, competence expiry, shortages, overdue hazards and forecast cost; attendance or Task closure never counts as physical acceptance. Deploy permissions/recovery/rest rules against actual records before enabling assignment.

[Frappe staffing documentation](https://docs.frappe.io/hr/staffing-plan) supports administrative records. [ORR competence guidance](https://www.orr.gov.uk/guide-rogs/7-managing-safety-critical-work) is a useful reference for assessment/monitoring/reassessment, not Iraqi legal approval. References checked 4 October 2026.
