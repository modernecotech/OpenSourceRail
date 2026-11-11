# First adoption path: current planning and engineering tools

OpenSourceRail has three connected products: design and delivery software, a reference railway and manufacturing system, and open GoA4 controls. The current v0.6 front end provides city-planning proposals, calculated city/design outlines, candidate engineering views and delivery records. ERPNext/Frappe HR and FUXA/gateway are separate configurable integrations. Calculated completion is distinct from approved construction and live railway operation.

The v0.6 software-release checklist is tracked separately from engineering
closure. Current readiness and its six source-bound software gates are in the
[software-release ledger](design-engine/v06-software-release/README.md).

## Who can use it

A public owner can edit geographic, route, stop, service and origin-destination proposals, then hand them to candidate-specific engineering review. A local builder can inspect candidate CAD/IFC, bill of materials, process, assembly and procurement drafts. An organisation can configure ERPNext/Frappe HR and FUXA/gateway workflows for its own project and equipment. Universities and reviewers can reproduce source-bound numerical methods and identify measurements needed for a prototype.

The current v0.6 [engineering Workbench](workbench/current/index.html) displays the selected candidate, source-bound engineering and cost summaries, readiness holds and links to its delivery records. The [coordinated experiment](design-engine/coupled-railway/README.md) carries one candidate identity through geometry, inventory, engineering analysis and delivery drafts.

The [planning workspace](workbench/planning/index.html) verifies current city map context and route sources, then supports route, stop, service and origin-destination proposals. Run `./osr plan compile edits.json --output build/my-plan` to create an immutable handoff bound to the selected v0.6 candidate; run `./osr plan verify build/my-plan` to verify its source files and identities. The handoff contains proposals only. It excludes vehicle, propulsion, fleet, civil quantity, cost, performance and cashflow results; those require candidate-specific evaluation. Planning revisions do not grant movement authority.

The [priced outline workspace](workbench/current/index.html) evaluates mapped networks, joined station complexes, straighter corridors and rounded-ring alternatives. It calculates service, fleet, manufacturing, civil quantities, project budgets and thirty-year cost scenarios with visible assumptions. Its [completion record](design-engine/outline-completion/README.md) distinguishes complete calculated outlines from physical engineering and release. Run the local Workbench with `./osr workbench`, choose a priced city and calculate a scenario. **Edit this outline and recalculate** opens the exact calculated routes and services in the planning workspace. Stop, geometry and headway edits then recalculate fleet, civil quantities and all cost scopes. A proposal that fails demand or access remains priced with its failed checks visible. The result includes a resource-leveled production/construction programme and disabled ERPNext/Frappe BOM, routing, workstation, work-order, project and staffing drafts. Real calendars, company/warehouse masters and reviewed imports require site configuration; nothing is submitted automatically.

## What is available and what needs configuration

| Area | Available scope | Deployment or engineering work still needed |
|---|---|---|
| Design research | Candidate definitions, source-bound calculations, failed/pending work, comparison and readiness holds | Trustworthy physical evaluators, complete installed equipment and independent confirmation |
| Manufacturing and delivery records | Candidate CAD/IFC, BOM, provisional process and assembly records, procurement drafts and calculated cost estimates | Exact drawings, joints, tooling, labour, suppliers, inspection, complete installed quantities and production release |
| ERPNext/Frappe HR | Current OSR app and deployment guide for projects, procurement, workforce, quality and maintenance | Legal entities, calendars, roles, warehouse/item masters, reviewed imports and operating procedures |
| FUXA/gateway | Integration components for observations, historian, alarms and review-linked lifecycle records | Actual equipment models, authenticated bindings, communications and commissioning |
| Candidate delivery exports | Candidate-bound CAD/IFC stock, engineering BOM, process and assembly records, and disabled ERPNext drafts | Complete installed geometry, serialised as-built evidence, priced project execution and independent acceptance |

The current repository includes [ERPNext/Frappe HR deployment](../deployment/erpnext/README.md), [FUXA/gateway deployment](../deployment/supervision/README.md), candidate-bound [CAD/IFC and delivery exports](design-engine/current/exports/manifest.json), and an [integration service](../services/integration/osr_integration/). These are configurable software components and research handoffs. No v0.6 site has been commissioned, no physical asset has been accepted, and the railway does not have operating release.

## A controlled adoption sequence

1. Select a workshop, depot or bounded planning/pilot scope and define its owners and review responsibilities.
2. Use current product/site identities; separate sample records and incomplete data from the proposed deployment.
3. Configure business masters, users, permissions, record retention and recovery through the [ERP deployment](../deployment/erpnext/README.md).
4. Review draft material, process, procurement, assembly and inspection records before creating real business transactions.
5. Configure the [supervision gateway](../deployment/supervision/README.md) with authenticated equipment bindings; keep simulation and physical inputs distinct.
6. Link measured inspections, serial installation, defects, repairs and independent handback to exact product revisions.
7. Keep railway control in simulation or separately authorised development until the physical plant and deployment safety case are accepted.

Business case closure, an alarm reset, a revision hash or a simulated inspection cannot accept hardware, release a railway or authorise movement. The current design runner does not automatically provision ERP sites, import city assets, submit purchasing or commission controllers.

[Project introduction](../README.md) · [Architecture](ARCHITECTURE.md) · [Current engineering](design-engine/current/README.md) · [Roadmap](ROADMAP.md).
