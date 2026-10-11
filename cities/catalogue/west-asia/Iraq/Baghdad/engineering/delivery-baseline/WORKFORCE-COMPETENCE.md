# Baghdad workload, recruitment and competence pilot

<!-- OSR CURRENT SCOPE CONTEXT -->
> **Original catalogue or earlier scope reference.** The figures and policies below retain their original assumptions; they are not the latest Baghdad staffing, depot, procurement or funding basis. See the [current Baghdad recalculation](../programme-recalculation/README.md) and [current city summary](../../README.md). National/portfolio totals have not been repriced with that conditional Baghdad option.
<!-- END OSR CURRENT SCOPE CONTEXT -->

The prior **4,624 FTE / USD 50.801m/year** allowance is USD 915.53/person/month. The existing 21-role weighted split remains a budget allocation, not shift cover. This separate [establishment](workforce-establishment.csv) derives posts/task hours, 1520 productive hours per FTE after leave, training, sickness and travel/handovers, integer cover and editable grade pay with employer/overtime allowances.

| Function | Annual workload h | Concurrent posts | Reference FTE | Loaded annual IQD m |
| --- | --- | --- | --- | --- |
| occ-lead | 7,482 | 1 | 5 | 157.9 |
| dispatcher | 127,202 | 17 | 85 | 1,790.1 |
| remote-assist | 808,110 | 108 | 537 | 11,309.2 |
| station-lead | 194,545 | 26 | 137 | 4,327.8 |
| platform-assistance | 1,878,108 | 251 | 1244 | 15,719.2 |
| customer-service | 471,398 | 63 | 320 | 4,043.5 |
| station-cleaning | 274,845 | 0 | 191 | 2,413.5 |
| workshop-lead | 70,720 | 17 | 51 | 1,611.1 |
| fleet-mechanical | 459,840 | 0 | 308 | 6,486.5 |
| fleet-electrical | 306,560 | 0 | 209 | 4,401.5 |
| fleet-finish-cleaning | 699,340 | 0 | 471 | 5,951.6 |
| infrastructure-lead | 35,360 | 17 | 34 | 1,074.1 |
| civil-track | 172,642 | 0 | 122 | 2,569.3 |
| solar-storage | 135,000 | 0 | 96 | 2,021.8 |
| wayside-comms | 100,400 | 0 | 76 | 1,600.6 |
| city-director | 1,520 | 1 | 1 | 31.6 |
| chief-engineer | 1,520 | 1 | 1 | 31.6 |
| quality-safety | 40,740 | 0 | 27 | 852.9 |
| training | 48,360 | 0 | 32 | 673.9 |
| procurement-stores | 36,270 | 0 | 24 | 505.4 |
| finance-people | 24,180 | 0 | 16 | 337.0 |

Reference total is **3,987 operating FTE**, loaded payroll **USD 52.239m/year equivalent**. Quantities are explicit task-hour/post assumptions, **not measured local work or accepted Iraqi pay/rest terms**. Higher overtime, emergency cover, queues, simultaneous faults and actual maintenance could change them. The dedicated solar plant specialist workload is unpriced. Maintenance contracts and payroll must be reconciled to avoid adding contractor labour twice to existing envelopes. No revised OPEX is silently adopted.

Factory 1,094 direct staffed-shift positions are separate; their production payroll is already in train procurement. Construction crew counts remain unknown and separate, rather than scheduled task slots called people. Temporary commissioning has its own cash requirement.

[Recruitment cohorts](recruitment-cohorts.csv) work backwards from each conditional line opening through requisition, selection, joining, training, first/repeated assessment and supervised experience. Offers allow 15% pre-join attrition and 80% first-pass / 75% repeat-pass assumptions. Hiring alone provides zero authorised productive capacity. Paid pre-opening training plus trainer/assessor reference cash is IQD 46.985bn; additional three-month commissioning payroll is IQD 1.611bn. These are distinct pre-opening uses, with overlap against EPC still unverified; rigs, agency fees and local terms remain unquoted. No trained/appointed person is invented.

[Seven controlled curriculum drafts](training-curricula.json) cover induction, OCC, stations/accessibility, fleet, civil/energy, factory and supervisors/assessors. Each lists prerequisites, method revision, equipment, practical exercises, critical assessment criteria, assessor requirements and retraining triggers. [Arabic glossary](arabic-glossary.json) is a draft requiring native technical review; full Arabic lessons are pending. Attendance, practical competence and scoped task authorisation are separate records.

The [seven-day first-corridor OCC roster](pilot-roster.json) contains actual service-hour coverage requirements and **zero named workers**. Every slot is blocked pending appointments and task-specific authorisation. The executable [eligibility evaluator](../../../../../../../engineering/analysis/workforce_checks.py) checks worker record, assessed task/asset-family/location/method scope, validity, suspension, skill fade, availability, checked rest, access, permits, tools/materials, competent supervision and independent verification. Evaluate both at planning and task start; changed or expired evidence blocks eligibility. It creates no assignment or operational release.

Department owns outcomes/budget/risk; unit owns assets/backlog; crew owns executable access-window work; worker owns a scoped method/evidence; verifier owns independent acceptance/handback. [Native ERP mappings](native-workforce-map.json) retain Staffing Plan/recruitment/Employee/onboarding/training/shift records, manufacturing Work Order/Job Card and maintenance Asset Maintenance/Asset Repair, with Project/Task for programme evidence. Dashboards track accepted output, blocks, competence expiry, shortages, overdue hazards and forecast cost; attendance or Task closure never counts as physical acceptance. Deploy permissions/recovery/rest rules against actual records before enabling assignment.

[Frappe staffing documentation](https://docs.frappe.io/hr/staffing-plan) supports administrative records. [ORR competence guidance](https://www.orr.gov.uk/guide-rogs/7-managing-safety-critical-work) is a useful reference for assessment/monitoring/reassessment, not Iraqi legal approval. References checked 4 October 2026.
