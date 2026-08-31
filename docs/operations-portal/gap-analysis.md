# OSR Operations Portal Gap Analysis

**Reviewed:** 2026-08-31

This note compares the current OSR Operations Portal against adjacent
commercial and open-source systems:

- Rail/EAM/APM: [IBM Maximo](https://www.ibm.com/products/maximo),
  [HxGN EAM](https://docs.hexagonppm.com/r/en-US/EAM-System-Overview/12.3/1261935),
  [Siemens Railigent X](https://www.mobility.siemens.com/global/en/portfolio/digital-solutions-software/digital-services/railigent-x.html),
  [Bentley AssetWise Rail Condition Analytics](https://www.bentley.com/software/assetwise-rail-condition-analytics/)
- Construction QA / common data environment:
  [Procore Quality & Safety](https://www.procore.com/quality-safety),
  [Autodesk Construction Cloud quality management](https://construction.autodesk.com/workflows/construction-quality-management/),
  [Oracle Aconex](https://www.oracle.com/construction-engineering/aconex/)
- Open-source / lighter CMMS comparators:
  [openMAINT](https://www.openmaint.org/en/home),
  [Odoo Maintenance](https://www.odoo.com/app/maintenance),
  [ERPNext Maintenance Schedule](https://docs.frappe.io/erpnext/maintenance-schedule)
- Standards posture:
  [ISO 55001 asset-management system](https://www.iso.org/standard/55089.html),
  [ISO 19650 BIM/information management](https://www.bsigroup.com/en-GB/products-and-services/standards/iso-19650-building-information-modelling-bim/)

## Current OSR Position

The portal is a strong **planning and generated-register tool**:

- Deterministically expands a city design into asset ids.
- Generates spreadsheet-friendly asset, manufacturing, QA, and maintenance
  CSVs.
- Gives each trainset, station, track section, switch, energy site,
  waypoint/W-SBC, signalling node, depot, and production-plant tool a
  stable row.
- Renders manufacturing packages, QA gates, and maintenance intervals in
  one browser UI.
- Keeps the design-to-operations link explicit and reproducible.

It is now a lightweight owner-operator execution tool, but it is not a
full CMMS/EAM, construction-management platform, or manufacturing MES.

## Missing Capabilities

| Priority | Gap | Why it matters | Comparator signal |
|---|---|---|---|
| P0 | Work-order lifecycle depth | OSR has authenticated city-scoped RBAC, assignable work orders, status transitions, holds, rejection/rework, independent handback, SQLite persistence and server-enforced closeout. Routed queues and deployment-configurable authority matrices remain open. | HxGN EAM work requests become approved work orders, can be dispatched, scheduled, rescheduled, and status-managed. |
| P0 | Inspection forms/checklists | The portal has pass/watch/fail evidence, readings, authenticated inspector identity, managed photo/file upload, automatic NCR creation and server content attestations. Template-specific typed checksheets and offline capture remain open. | Procore/Autodesk emphasize mobile inspection checklists, field observations, photos, signatures, and issues for nonconforming items. |
| P0 | NCR/CAPA workflow | Failed inspection evidence creates an NCR and blocks work; open NCRs block closeout. Root-cause taxonomy, corrective/preventive actions, retest, waiver/deviation authority and effectiveness review remain missing. | Construction QA tools center observations, corrective actions, and issue resolution. |
| P0 | Document control / CDE | Managed content-addressed evidence, append-only document revisions, supersession links and sealed audit records are implemented. RFI/submittal transmittals, organisation ownership and full ISO 19650 CDE workflows remain open. | Oracle Aconex sells complete project records, process workflows, document ownership, and audit trail as core features. |
| P0 | Roles and permissions | Password-authenticated users, city scopes, RBAC, CSRF protection and identity-based segregation of inspection/approval duties are enforced server-side. HMAC server attestations are not qualified signatures; SSO/MFA, organisation federation and jurisdiction-specific legal-signature policy remain deployment work. | Aconex/Procore/Maximo all rely on accountable users, permissions, and auditable actions. |
| P1 | Calendar and crew scheduling | Manufacturing now has project-day windows and staff-task roles, while maintenance still uses textual next-due basis. There is no actual opening date, crew assignment roster, depot capacity, possession window, or workload balancing. | HxGN EAM includes daily scheduling, labor/parts availability, labor utilization, routing, and workload balancing. |
| P1 | Meter/telemetry ingestion | The schedule has km/condition triggers, but no live service-km, BMS, wheel, vibration, charger, W-SBC, or SCADA feed. | Maximo and Railigent emphasize condition data, sensor data, predictive maintenance, and health states. |
| P1 | Defect and failure history | There are no defect codes, failure modes, root causes, MTBF/MTTR, bad-actor assets, or reliability trends. | Odoo computes maintenance statistics such as MTBF/MTTR; Maximo and AssetWise emphasize reliability/performance analytics. |
| P1 | Spares, inventory, tools, warranty | Tasks list owners but do not reserve parts/tools, track stock, manage warranty claims, or roll costs against assets. | HxGN EAM work orders include labor, materials, tools, permits, safety docs, and warranty/claims tracking. |
| P1 | Linear asset analytics | Track sections are simple inter-station rows, not true linear-referencing assets with chainage, measurements, geometry defects, renewal prioritization, or state-of-good-repair scoring. | Bentley AssetWise Rail Condition Analytics focuses on rail condition data, linear analytics, predictive renewal decisions, and SGR. |
| P1 | GIS/BIM/digital twin linkage | Assets have lat/lon or chainage text, but no map view, BIM object ids, as-built model references, or ISO 19650-style information requirements. | ISO 19650 expects secure lifecycle information management for built assets; openMAINT mentions GIS and BIM. |
| P2 | Mobile/offline field app | The browser supports work-order and inspection entry with local fallback, but is not an offline-first technician app with sync conflict policy, QR scans, managed photos or device identity. | Procore, Odoo, ERPNext, and CMMS tools all lean on field/mobile execution. |
| P2 | Regulator/opening evidence package | QA evidence exists as planned rows, not a packaged safety-case/submittal bundle with signoff status and dependencies. | Aconex/Autodesk tie documents, RFIs, issues, assets, commissioning, and handover. |
| P2 | Cost and lifecycle management | There is no asset lifecycle-cost rollup, replacement forecast, depreciation, renewal budget, or capex/opex optimization. | ISO 55001 focuses on balancing performance, risk, and expenditure across the asset lifecycle. |

## Suggested Build Order

1. **Production identity integration.** Add OIDC/SSO, MFA, organisation
   boundaries, routed approval queues and deployment-defined authority policy
   above the implemented local authenticated RBAC baseline.
2. **Inspection/checksheet templates.** Expand manufacturing,
   maintenance, and QA rows
   into fillable forms with typed fields, pass/fail, numeric readings,
   photo/evidence slots, signature, and generated NCR on failure.
3. **Opening-date scheduler.** Convert `next_due_basis` into actual due
   dates from a city opening date, plus km-based placeholder counters.
4. **Defect/NCR/CAPA depth.** Add defect severity, root cause,
   corrective action, responsible party, due date, retest, and waiver.
5. **Telemetry bridge.** Feed `osr-cbm-backend`, energy-site telemetry,
   and simulation outputs into the same asset ids.
6. **Inventory/tools module.** Add parts, tools, calibration records,
   stock min/max, reservations, and warranty/claim fields.
7. **Linear/GIS view.** Add map/chainage view for track sections,
   switches, structures, stations, and energy sites.
8. **CDE workflow depth.** Add RFI, submittal and transmittal workflows around
   the implemented managed-file, document-revision and immutable-audit core.

## Product Decision

The portal should stay intentionally lightweight and open. Its current small
transactional core is:

```text
asset register + work orders + inspection evidence + independent handback + NCR + audit log
```

This is a deployable workshop/pilot reference with a materially stronger trust
boundary, not a complete enterprise EAM or hosted security service. A real
deployment must add TLS, secret management, monitored backups, SSO/MFA where
required, data-retention policy and an independent security review. The simplified implementation is captured
in [`ops-core.md`](ops-core.md) and exposed through the portal's
**Ops Core** tab.
