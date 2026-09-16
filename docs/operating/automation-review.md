# ERPNext integration and automation review

Reusable adapters for the eight recommended areas are now implemented. See
[Operating components](components.md) for their dynamic forms, city profiles,
preview/apply API and activation behaviour. The master-data requirements below
still apply when commissioning each component.

Reviewed against the installed ERPNext **15.121.2**, Frappe **15.120.1** and
Frappe HR **15.64.0**. All 62 native document types checked across the ten
areas below exist in this installation. Current upstream documentation can
also describe newer versions; this implementation uses the installed v15
schemas and native validation.

## Implemented in this increment

1. **Procurement requirement → draft Material Request.** Open an imported
   procurement Task and choose **OpenSourceRail → Material request**. Search by
   requirement ID, description or railway asset; select a real ERP Item, enter
   the verified quantity in its stock unit, a required date and a city warehouse.
   The native request retains the source requirement, project and cost centre.
   Repeating the same mapping returns the existing request and preserves edits.
   Different inputs for an already converted requirement require review of that
   request. Requests remain unsubmitted; no supplier orders or emails are sent.
2. **Purchasing lifecycle feedback.** The twin counts native Material Requests,
   Purchase Orders, Purchase Receipts and Purchase Invoices linked through either
   document headers or item lines. A document appears once per project even if
   several lines match. Parent-document permissions and company scope apply.
   Work Orders and project Budgets also appear. These are document counts,
   not ledger amounts or quantities combined across incompatible units.
3. **Automatic work-readiness checks.** Every snapshot counts overdue, undated
   and unassigned unfinished Tasks. Completed/cancelled work is excluded;
   missing dates are not classified as late. Counts overlap. The existing
   five-minute feedback timer refreshes these checks without assigning staff
   or sending notifications. ERP uses its configured site date for lateness.
4. **Condition Issue → reviewed Asset Repair.** An Issue linked to a commissioned
   Asset now previews the native repair, parts and city-store availability,
   technician assignment and expected downtime. Apply is repeat-safe and creates
   only a draft; native submission owns part consumption and actual repair data.
   Feedback returns repair/part/assignment/evidence state while always marking
   railway handback as external and still required.

These additions work for every applied city baseline without changing its
engineering/configuration checksum. Native operator transactions sit alongside
that immutable baseline. The generic/company/city warehouse configuration is
reused; no separate per-city implementation is needed.

## Further integration opportunities

These are implementation recommendations based on the available native
functions, rather than claims that all integrations are already enabled.

| Area / native components | OpenSourceRail input and useful automation | City/operator data needed | Recommended order |
|---|---|---|---|
| Purchasing: Material Request, RFQ, Supplier Quotation, Purchase Order, Receipt, Invoice, Supplier Scorecard | Convert verified BOM requirements into requests; follow the native quotation/order/receipt process; compare promised and actual delivery against required-by dates | Approved Item/UOM mapping, verified quantities, delivery dates, supplier qualification and purchasing authorities | **Now:** draft conversion and lifecycle counts installed; bulk mappings and delivery-risk checks next |
| Inventory: Item Reorder, Warehouse, Stock Entry, Serial No, Batch | Maintain depot spare levels; use native automatic reordering; associate serialised parts and batches with receipt/installation evidence | City stores, stock opening balances, replenishment levels and quantities, traceability policy | Next, after the Item catalogue |
| Manufacturing: BOM, Operation, Workstation, Production Plan, Work Order, Job Card, Subcontracting Order | Convert approved production recipes into Work Orders and Job Cards; feed material consumption and actual production time back to the twin | Verified multi-level BOMs, output Items, operations, workstations, capacities and calendars | Next, one representative assembly first |
| Quality: Quality Inspection Template/Inspection, Quality Procedure, Goal, Review, Action | Require incoming/in-process inspections on native stock/production documents; carry batch/serial and rejected-material references into OSR evidence | Test methods, tolerances, sampling, qualified inspectors and real receipt/job-card references | Next, with procurement and production |
| Assets: Asset, Maintenance Team, Maintenance, Maintenance Log, Repair, Movement | Map commissioned assets; generate native scheduled maintenance logs; convert condition Issues into reviewed Repairs with part/assignment feedback; track repair costs/movements | Real asset identities, commissioning dates, approved intervals, service teams and accounting treatment | **Now:** calendar servicing and condition-repair transition installed; movement/repair-pool commissioning next |
| Finance: Budget, Cost Center, Timesheet, Expense Claim, Payment Entry, Bank Transaction | Apply native project/account budget controls; collect labour costs and expenses; reconcile commitments and actuals | Fiscal year, account mappings, approved budgets, currency, costing rates and access controls | Now: project Budget visibility; budget commissioning next |
| People: Staffing Plan, Job Requisition, Job Opening, Onboarding, Training Program/Event/Result, Employee Skill Map, Shift Type/Assignment | Derive role-demand and training proposals from task roles; use native recruitment, onboarding and training workflows; compare available skills to work demand | Actual establishment, named employees, competent assessors, training outcomes and agreed calendars | Next: training/role templates; staff assignment after validation |
| Service: Issue, SLA, Warranty Claim, Maintenance Schedule/Visit | Track facility defects, supplier warranty cases and contracted service response; link tickets to city/project/asset references | Service providers, contract terms, priority rules, response hours and authorised communication channels | After assets and supplier contracts |
| Contracts/revenue: Contract, Quotation, Sales Order, Sales Invoice | Track EPC/service milestones, customer claims and contractual billing | Signed contract structure, customers, tax/accounting setup and milestone acceptance | Later, per operating business model |
| Workflow: Workflow, Assignment Rule, Notification, Auto Repeat, Webhook | Route business approvals, distribute work by city/department, repeat eligible business documents, publish authenticated integration events | Named approvers/users, segregation rules, escalation policy, approved recipients and event consumers | Configure after the responsible teams are known |

### Boundaries that matter

- A manufacturing planning task is not automatically a valid production BOM or
  Work Order. Scope descriptions and quantity-basis strings need verified units
  and executable recipes before they become stock transactions.
- OSR maintenance triggers include calendar, mileage and condition logic. Native
  calendar maintenance and the condition-Issue-to-Repair transition are installed.
  Mileage/cycle thresholds and deployment-specific approved maintenance rules
  remain to be commissioned with trustworthy meter/reset data.
- ERP inspection acceptance, training completion and asset status do not grant
  railway competence, signalling authority, safety-case acceptance or handback.
- The city CAPEX estimate is a planning reference, not an approved ERP Budget.
  Budget controls need account/fiscal-year/currency mapping and operator approval.
- Native Issues can cover business/facility service. Train dispatch and railway
  incident authority remain in OSR. Frappe Helpdesk, CRM and Learning are separate
  apps, not assumed to be installed by this integration.
- Payroll, bank payments, email delivery and external webhooks need real operator
  configuration. This review does not activate them.

## Reproducible commissioning sequence

For each city, apply its operating baseline, then maintain the following reviewed
mapping set alongside its deployment records: Items/UOMs and quantities; stores
and reorder policy; production BOMs/workstations; commissioned assets and service
intervals; roles/training requirements; fiscal/account/budget mapping; business
approval rules. Reuse shared templates and override only the city-specific data.
Keep credentials and employee personal data out of tracked city profiles.

The first practical sequence is **items and procurement → stock and incoming
quality → production → commissioned asset maintenance → workforce and finance
controls**. Each stage should use native ERP documents and return its execution
state through the existing city/revision-linked twin.

## API and operational behaviour

- GET `osr_erpnext.procurement.candidates`: parameters `task`, optional `search`
  and `offset`; returns at most 50 matching source requirements.
- POST `osr_erpnext.procurement.create_material_request`: parameters `task`,
  `requirement_id`, `item_code`, `quantity`, `schedule_date`, `warehouse`.
  Requires Task read, Project write, Material Request create and master-data
  read access. Warehouse must belong to that city's configured company/stores.
  Quantity is explicit, finite and positive; required date cannot be in the past.
- GET `osr_erpnext.city_runtime.city_status`: adds `readiness` and extends
  `business_documents`. Existing snapshot fields remain compatible.
- POST `osr_erpnext.integration.preview_repair`: parameters `issue`, `proposal`;
  validates the linked city Asset, technician, Items/warehouses, optional serial/
  batch bundles and availability without writing.
- POST `osr_erpnext.integration.apply_repair`: adds the preview fingerprint and
  creates or returns the repeat-safe draft Asset Repair and native assignment.
  It does not submit, close the Issue or authorise handback.

A request identity is unique per project, procurement task and source requirement.
The database unique constraint prevents concurrent duplicates; a competing call
can receive a duplicate error and safely retry. Cancellation/amendment remains
an explicit native workflow. Repeating a conversion returns the existing record
and its document status; it does not silently recreate a cancelled request.

## Verification

Run the pure rule tests:

```bash
tools/automation/osr-python -m pytest -q tools/automation/tests/test_erpnext_automation.py
```

On the local evaluation site
with Samawah and Mosul applied, run the native transaction check:

```bash
docker compose --env-file var/erpnext/local.env -f deployment/erpnext/compose.yaml \
  exec -T backend env/bin/python < deployment/erpnext/tests/verify-procurement.py
```

It creates a temporary Item and draft request inside a rolled-back transaction,
checks line-linked twin counts, preserved edits, conflicting inputs, wrong-city
warehouses and denied guest access. It does not submit or commit its fixtures.

## Upstream references

- [Material Requests](https://docs.frappe.io/erpnext/material-request) and
  [automatic stock replenishment](https://docs.frappe.io/erpnext/auto-creation-of-material-request).
- [Work Orders](https://docs.frappe.io/erpnext/work-order),
  [Quality Inspection](https://docs.frappe.io/erpnext/quality-inspection) and
  [Asset Maintenance](https://docs.frappe.io/erpnext/asset-maintenance).
- [Budgets](https://docs.frappe.io/erpnext/budget),
  [Training Programs](https://docs.frappe.io/hr/training-program) and
  [Job Requisitions](https://docs.frappe.io/hr/job-requisition).
- [Issues and SLAs](https://docs.frappe.io/erpnext/issue) and
  [Assignment Rules](https://docs.frappe.io/erpnext/assignment-rule).
