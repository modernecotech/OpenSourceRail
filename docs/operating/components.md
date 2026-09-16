# Reusable operating components

Eight typed adapters connect city operating baselines to native ERPNext and
Frappe HR records. Their shared registry drives the API, validation, interactive
forms and repeatable configuration packages. Adding another city requires data,
not another implementation of the adapters.

## Use from ERPNext

Open a city Project and choose **OpenSourceRail → Operating components**. Select
a component, supply a stable instance key and its inputs, then **Preview**.
The review shows the native record and its effects. **Apply component** validates
again and opens the resulting native record. Warehouse choices are restricted
to the city's configured stores. Quality inspection references provide an item
line picker. Account and user lists use editable table controls.

| Component | Native result | Behaviour after apply |
|---|---|---|
| Stock replenishment | An Item Reorder row on an existing stock Item | Live configuration; native stock settings/scheduler govern automatic requests |
| Production order | Work Order populated from an active submitted BOM | Draft; native submission and Job Card/stock workflows follow |
| Incoming inspection | Quality Inspection using an approved parameter template and a project-linked receipt/invoice line | Draft; inspectors enter measurements and submit; native reference-link hooks still run |
| Asset servicing | Asset Maintenance, native log and assignment | Schedule and team-member assignment start on save; requires a submitted, commissioned city Asset |
| Training programme | Training Program | Scheduled programme; events, attendance, results and competence decisions are separate |
| Project budget | Budget with native account allocations and purchasing/expense controls | Draft; controls take effect after native submission |
| Facility service | Issue, optionally with a native SLA | Open issue; native business response rules apply |
| City task assignment | Assignment Rule, scoped to project and work category | Disabled initially; review users and enable in ERPNext |

An Item can have replenishment rules for several cities. Existing rules for a
warehouse are preserved; the adapter refuses to replace an unmanaged rule.
Native maintenance provides one schedule document per Asset; edit its native
child task table when extending an existing schedule. Native approvals, stock
transactions, invoice/payment processing and railway release remain in their
respective systems.

## Generic configuration and city overrides

- Shared defaults/instances: [components.json](../../deployment/erpnext/config/components.json).
- City overrides: `cities/catalogue/<region>/<country>/<city>/operations/erp-components.json`.
- Compiled packages: `build/erpnext/cities/<slug>/components.json`.
- Schemas/adapters: [component_catalogue.py](../../deployment/erpnext/apps/osr_erpnext/osr_erpnext/component_catalogue.py)
  and [components.py](../../deployment/erpnext/apps/osr_erpnext/osr_erpnext/components.py).

Defaults merge by component and input name. Lists such as budget account rows
replace the inherited list. Instances merge by `(component, key)`; a city can
override an inherited instance or set `enabled: false` to omit it. `${city}` and
`${project}` are literal substitutions; profiles contain no executable code.
Unknown inputs, duplicate instance keys, invalid numbers/dates and unsupported
components fail validation.

The shared profile creates a city operating induction programme, with distinct
Samawah and Mosul title overrides. Other components require verified native
master records and operator inputs. None of those identities, stock quantities,
approved BOMs, asset service intervals, budgets or personnel are invented.
All 266 merged profiles and their induction packages are compiled by the
[operating-readiness audit](readiness.md); that compile proves schema and package
integrity, not the existence of the native ERP masters needed to enable the
other seven adapter types.

```json
{
  "schema": "osr-components/1",
  "city": "samawah",
  "defaults": {"assignment": {"strategy": "Load Balancing"}},
  "instances": [
    {
      "component": "replenishment",
      "key": "depot-bearing-stock",
      "enabled": false,
      "inputs": {"level": 12, "quantity": 24}
    }
  ]
}
```

This example is deliberately incomplete and disabled. Supply a verified ERP
`item` and city `warehouse`, review quantities in its stock unit, then enable
it when ready to configure native replenishment. Do not put credentials or
employee personal records in tracked city files.

## Repeatable commands

```bash
./osr erp components catalogue
./osr erp components init-configs   # preserves existing overrides
./osr erp components validate
./osr readiness --check
./osr erp components prepare samawah --project PROJ-0001
./osr erp components preview build/erpnext/cities/samawah/components.json
./osr erp components apply build/erpnext/cities/samawah/components.json
./osr erp snapshot
```

A package is bound to an explicit ERP Project and city. Apply first previews all
its enabled instances, then creates their records in one database transaction.
A validation failure rolls back that transaction. Native external hooks or
integrations must be commissioned with their own delivery guarantees. The
package's effective defaults are saved on the Project so interactive forms use
the same city defaults. This configuration is separate from the immutable
engineering/task baseline and does not force its re-import.

## Identity, permissions and repeatability

Each native record carries its project, component ID, instance key and input
checksum. The database enforces a unique component identity. Identical calls
reuse records, preserving operator edits; changed inputs with the same key are
rejected. Review the native record or deliberately choose a new key. A new key
cannot bypass native uniqueness constraints, such as one maintenance schedule
per Asset or one reorder rule per Item/warehouse. Concurrent attempts can return
a duplicate error and safely retry; Item updates also acquire a row lock.

The preview fingerprint covers the component version, inputs, derived native
values and project baseline. Apply rebuilds and compares it. Preview does not
insert records or execute native document hooks. Apply uses native document
permissions and validation; it never uses `ignore_permissions` or submits a
financial/production document. Linked companies, city warehouses, receipt item
project, asset baseline membership, maintenance team and user access are checked.
Assignment conditions are constructed by code, not accepted as user expressions.

## Feedback and API

The existing five-minute twin refresh includes counts and states for all eight
components. It uses native parent permissions, including Item permissions for
reorder child rows. It does not expose staff lists or imply railway authority.
Only records managed by these components are counted in this section; the
existing purchasing/project feedback also covers other native business records.

- GET `osr_erpnext.components.catalogue?project=…`
- GET `osr_erpnext.components.inspection_lines?project=…&reference_type=…&reference=…`
- POST `osr_erpnext.components.preview`: `project`, `component`, `key`, `inputs`.
- POST `osr_erpnext.components.apply`: the same inputs plus preview `fingerprint`.

## Validation

Run `tools/automation/osr-python -m pytest -q tools/automation/tests/test_erpnext_components.py`
and `./osr erp components validate`. Native integration checks run against the
local evaluation site using temporary fixtures and transaction rollback. New
adapters need schema tests, native validation coverage and city-scope checks.

```bash
docker compose --env-file var/erpnext/local.env -f deployment/erpnext/compose.yaml \
  exec -T backend env/bin/python < deployment/erpnext/tests/verify-components.py
```

This local check expects the Samawah and Mosul evaluation baselines. It mutes
test emails, creates its own Items/BOM/receipt/Asset/team, exercises all eight
adapters and rolls back the transaction, including temporary user permissions.
