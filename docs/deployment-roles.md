# Deployment Roles

OpenSourceRail separates open reference artifacts from the organizations
that carry legal, financial, and safety responsibility for a real
railway. A deployment should name each role before any safety-critical
trial begins.

## Role Map

| Role | Carries | Typical evidence or decision |
|---|---|---|
| Owner / public sponsor | Budget, public objectives, asset ownership, residual public risk | Business case, funding approvals, land access, public-service obligations |
| Operator | Operating rules, competence, service delivery, degraded-mode response | Rulebook acceptance, staffing plan, training records, trial-running reports |
| Entity in charge of maintenance | Maintenance system, asset condition, spares, inspection records | Maintenance plan, work-order closeout, defect/NCR history, handback signatures |
| Prime integrator | System integration, interface control, technical delivery, safety-case assembly | Interface control documents, configuration baseline, integration tests, evidence index |
| Independent safety assessor | Independent review of safety argument and evidence | Assessment report, action log, residual-risk findings |
| Regulator / national safety authority | Legal approval for trial running and revenue operation | Authorization, conditions, operating certificate, accepted residual-risk decision |
| Insurer / liability underwriter | Insurability, claims framework, liability exclusions | Insurance terms, risk survey, required mitigations |
| EPC / civil contractor | Survey, civil works, structures, stations, depots, trackform, construction QA | Survey package, method statements, ITPs, as-built records, handover certificates |
| Rolling-stock production plant | Local manufacture, tooling, fixtures, first article, production QA | BOM, routings, weld/NDT records, first-article inspection, configuration records |
| Hardware integrator | COTS/SBC or custom-board build, wiring, enclosures, bench tests, commissioning | SKU freeze, harness maps, power/thermal margins, self-test logs |
| Energy and utility partner | PV, BESS, chargers, grid/PPA, protection settings, energy operations | Grid study, interconnect approval, charger thermal study, tariff/PPA |
| Financing entity | Debt, grant, guarantee, disbursement conditions | Term sheet, covenants, eligibility evidence, procurement conditions |

## OSR Project Boundary

OpenSourceRail can provide:

- reference architecture and RFCs;
- simulator and generated city designs;
- operations portal, asset registers, QA, maintenance, manufacturing,
  and evidence templates;
- safety-case scaffolds, tests, formal models, and release-gap registers;
- hardware and rolling-stock reference packages.

OpenSourceRail does not provide:

- statutory operating approval;
- product liability cover;
- sovereign guarantees or project finance;
- independent safety assessment;
- construction warranties;
- operator competence certification.

Those duties belong to the deployment roles above.

## Minimum Role Closure For A Pilot

A non-safety digital pilot can start with only an owner/operator sponsor
and an implementation team. A closed-track or depot movement pilot needs
more:

| Gate | Roles that must be named |
|---|---|
| Digital-only shadow mode | Owner/operator, implementation lead, data owner |
| Depot or closed-track movement | Owner/operator, prime integrator, entity in charge of maintenance, safety reviewer, insurer or risk owner |
| Public trial running | Owner/operator, prime integrator, independent safety assessor, regulator, insurer, civil/EPC, maintainer |
| Revenue operation | All roles in the role map, with accepted safety case and operating authorization |

## Relationship To Other Docs

- Unified city/deployment pipeline:
  [`deployment-model.md`](deployment-model.md)
- First adoptable product:
  [`first-adoptable-product.md`](first-adoptable-product.md)
- Certification gaps:
  [`certification/release-gap-register.md`](certification/release-gap-register.md)
- Acceptance evidence basis:
  [`operations-portal/acceptance-evidence-report.md`](operations-portal/acceptance-evidence-report.md)
