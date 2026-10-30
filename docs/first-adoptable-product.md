# First adoption path: the design and delivery platform

OpenSourceRail has three connected products: the owner/builder/operator delivery platform, reference railway hardware and manufacturing system, and open GoA4 controls. Controlled planning, training, workshop/depot records and evidence management can be useful before a new train or guideway is physically qualified.

## Who can use it

A public owner can organise requirements, candidate revisions, supplier enquiries and acceptance work. A local builder can inspect material, stock, assembly, tooling and QA needs. An operator can configure asset, defect and maintenance workflows. Universities and reviewers can reproduce numerical methods and identify the measurements needed for a prototype.

The current v0.6 [engineering Workbench](workbench/current/index.html) and [coordinated experiment](design-engine/coupled-railway/README.md) expose candidate-bound geometry, simulation, inventories and delivery drafts. The [editable planning workspace](workbench/planning/index.html) retains local city, stop, service and OD editing over historical planning packets. Exported edits can be compiled and verified with `./osr plan compile` and `./osr plan verify`; the resulting immutable handoff is bound to the selected v0.6 candidate. Its map and starting service values remain historical proposals, and the handoff does not provide v0.6 route performance, movement authority or proof of route suitability.

## What is available and what needs configuration

| Area | Available scope | Deployment or engineering work still needed |
|---|---|---|
| Design research | Reproducible candidate definitions, source-bound calculations, failed/pending work and comparison | Trustworthy physical evaluators, complete installed equipment and independent confirmation |
| Manufacturing planning | Stock/process records, EBOM/MBOM coverage, assembly dependencies, procurement and QA tasks | Exact drawings, joints, tooling, labour, suppliers, inspection and production release |
| ERPNext/Frappe HR | Retained OSR app and business deployment for projects, procurement, workforce, quality and maintenance | Legal entities, calendars, roles, warehouse/item masters, reviewed imports and operating procedures |
| FUXA/gateway | Retained observation, historian, alarm and review-linked lifecycle functions | Actual equipment models, authenticated bindings, communications and commissioning |
| Physical twin | Candidate-bound CAD/IFC stock and disabled ERPNext research drafts | Complete installed geometry, serialised as-built evidence, priced project execution and independent acceptance |

The [earlier Baghdad digital pilot](design-engine/ferrite-maglev/pilot-delivery/README.md) and [native ERPNext/FUXA/Workbench exercise](design-engine/ferrite-maglev/pilot-lifecycle/README.md) retain maglev-era simulation evidence for receiving, inspection, rework, installation, condition monitoring, maintenance and simulated handback. They are not commissioned v0.6 deployments. The [capability migration register](design-engine/ferrite-maglev/capability-migration/README.md) records the disposition of earlier v0.4 features.

## A controlled adoption sequence

1. Select a workshop, depot or bounded planning/pilot scope and define its owners and review responsibilities.
2. Use current product/site identities; separate historical examples and incomplete data from the proposed deployment.
3. Configure business masters, users, permissions, record retention and recovery through the [ERP deployment](../deployment/erpnext/README.md).
4. Review draft material, process, procurement, assembly and inspection records before creating real business transactions.
5. Configure the [supervision gateway](../deployment/supervision/README.md) with authenticated equipment bindings; keep simulation and physical inputs distinct.
6. Link measured inspections, serial installation, defects, repairs and independent handback to exact product revisions.
7. Keep railway control in simulation or separately authorised development until the physical plant and deployment safety case are accepted.

Business case closure, an alarm reset, a revision hash or a simulated inspection cannot accept hardware, release a railway or authorise movement. The current design runner does not automatically provision ERP sites, import city assets, submit purchasing or commission controllers.

[Project introduction](../README.md) · [Architecture](ARCHITECTURE.md) · [Current engineering](design-engine/current/README.md) · [Roadmap](ROADMAP.md).
