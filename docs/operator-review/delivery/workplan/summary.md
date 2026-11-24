# Costed workforce and shift workplan

Scope **first · Unattended GoA4**

Plan `33f5c5695e8a1b5f63aab594b0121855c04de9c62e4cd98911966ee5ba8b01cd` · 55 work rows · 90% capacity in the availability test.

Amounts are planning estimates in US dollars. Each account has its own purchase, construction, training or operating period. Where a contract already includes labour, use the account to test or replace the allowance.

| Phase and account | Required hours¹ | Paid hours¹ | Available hours¹ | Uncovered hours¹ · base → stress | Low | Base | High | Unpriced rows |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Initial operator training · Commissioning · one initial GoA4 operating intake | 284,960.0 | 284,960.0 | Open | Open → Open | $1,180,094.40 | $1,291,923.20 | $1,516,880.00 | 0 |
| Operating year · Operating payroll · annual equivalent | 2,622,560.0 | 3,174,080.0 | 2,622,560.0 | 0.0 → 262,256.0 | $11,209,411.19 | $12,270,689.61 | $14,410,135.99 | 0 |
| Precast production · Elevated civil · precast production crew allowance | 533,520.0 | 673,920.0 | 561,556.8 | 0.0 → 28,118.9 | $4,337,049.60 | $4,751,884.80 | $5,577,436.80 | 0 |
| Site erection · Elevated civil · site erection crew allowance | 237,120.0 | 299,520.0 | 249,580.8 | 0.0 → 12,497.3 | $1,913,558.40 | $2,096,265.60 | $2,460,556.80 | 0 |
| Vehicle final assembly · Fleet purchase · factory support posts | 288,000.0 | 299,520.0 | 288,000.0 | 0.0 → 28,800.0 | $1,567,238.40 | $1,716,998.40 | $2,015,020.80 | 0 |
| Vehicle final assembly · Fleet purchase · staffed assembly window | 1,452,000.0 | 2,620,800.0 | 1,713,600.0 | 0.0 → 0.0 | $17,190,950.40 | $18,832,320.00 | $22,109,068.80 | 0 |

¹ Known subtotals. Unresolved hours are blank in the detailed rows and counted in the JSON report. Capacity in one shift or trade cannot cover a shortage in another. The availability test reduces productive capacity with payroll held fixed.

Repeated day patterns in local time. Fixed 06:00 public start is a planning assumption. Annual wages include relief from the source role pool. Civil crews are budgeted over the full reservation window, with effective availability from the source plan.

Programme labour, intake and operating-year payroll have separate periods. These are allowances inside the fleet, civil, commissioning and operating accounts. Match contract exclusions and labour credits before substituting them.

No named staff, awarded shifts or authorisation. Peak role/shift coverage is a workload screen. Onboard scenarios distribute annual duty using the departure profile where available.

## Work awaiting quantities, quotations or deployment evidence

| Phase | Work or evidence | Accountable role | Estimate basis or next input |
|---|---|---|---|
| Operating year | Timetabled relief, peak coverage, staff breaks, accessibility and rescue | Operating and safety directors | Price actual duty diagrams, mobilisation and specialist response separately; annual pools only. |
| Initial operator training | Classroom capacity, mentors, assessors, bilingual courses and operator competence | HR and assessment leads | Price facilities, independent assessments, simulators, travel and backfill; intake labour only is priced. |
| Programme definition | Survey, access, design review, utility diversion, permits and programme management | Owner and designer | Use matched surveys and engineering tenders. Dates and staff quantities await the issue scope. Scope comparator from the selected infrastructure estimate, in US$m at its published basis. Design assurance 474.55, land/utilities/disruption 296.40. |
| Site construction | Foundations, stations, trackwork, traction electrical, controls and depot construction | Civil and systems contractors | Use candidate-specific work breakdown and priced bills. Crew rows cover beam production and erection. Same-candidate scope comparators include elevated civil 1,331.24, stations/access 832.00, track/walkways 237.12, traction supply 316.92, signalling/comms 177.84 and depots/control 260.00 US$m. |
| Precast production | Transport, stock imbalance, rejected batches, contractor supervision and night watch | Yard and logistics leads | Separate labour after mapping operated crane and haul contracts to the crew allowance. |
| Site erection | Possessions, closures, relief, lifting design and subcontract staff | Installation planner | Return actual front bookings and split labour from hire; do not add the allowance to an operated crane quote. |
| Vehicle final assembly | Component factories, supplier lead time, specialised shops, rework and integrated qualification | Vehicle supply and quality leads | Use measured times and matched fleet or supplier lots; the staffing allowance covers final assembly and support. |
| Commissioning | System tests, transition, trials and independent review | Operator and integrator | Set trial dates and approval work. Use supervisory payroll for the actual trial period. The testing/commissioning envelope is 148.30 US$m. |

Use `workforce.csv` for each shift, role, requirement, cost and allowance. `workforce.parquet` carries the same rows in typed columns for subsequent queries. `plan.json` and `run-receipt.json` identify the input and recorded output bytes.
