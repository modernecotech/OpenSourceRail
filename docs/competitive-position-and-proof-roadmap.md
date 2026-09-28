# Competitive Position And Proof Roadmap

**Baseline reviewed:** repository `main` after the 2026-09-28 lifecycle release

**Decision use:** product positioning and evidence planning—not tender evaluation, supplier prequalification or a claim of equivalent railway acceptance

## Position In One Sentence

OpenSourceRail is presently strongest as an open, owner-controlled railway
planning, engineering, delivery and asset-information platform. Its reference
vehicles, infrastructure and GoA4 control system remain development programmes
and must not be sold as equivalent to commissioned commercial railways.

That distinction produces three separate products with separate claims:

| Product | Evidence now | Honest use now | Evidence still needed |
|---|---|---|---|
| Planning, design and delivery platform | City Studio, source-locked GIS, native/SUMO simulation, FreeCAD/IFC, quantities, asset identities, schedules, procurement and cashflow | Corridor screening, reference design, option comparison and delivery coordination | Surveyed corridor validation, independent numerical benchmarks, issued design deliverables and customer deployment evidence |
| Owner/operator and maintenance platform | ERPNext/Frappe HR, Ops Core, governed asset/work/inspection/maintenance records, observation-only FUXA integration and recovery exercises | Existing workshop, depot or pilot-corridor implementation with no railway command | Operator master data, production identity/TLS/MFA, commissioned equipment adapters, measured adoption outcomes and service support |
| Physical railway and GoA4 control | LM3 and reusable civil reference designs, deterministic evaluators, formal checks and staged pilot boundaries | Supplier engagement, prototype definition, shadow/HIL research and evidence planning | Supplier-frozen configurations, released production drawings, first articles, physical/HIL/field tests, independent assessment and national/operator authorization |

The 265-city developing-country portfolio demonstrates repeatable model
generation. It is not 265 deployments, orders or approved railway projects.

## What Competes With Each Product

No single reviewed alternative maps to the entire repository. The useful
comparison is by job to be done.

| Benchmark | Strong benchmark for | OpenSourceRail distinction to prove | Do not claim |
|---|---|---|---|
| [OSRD](https://osrd.fr/en/) | Open railway infrastructure, timetable, capacity and train simulation | Engineering revision, product, procurement, construction and maintenance consequences carried beyond planning | That breadth implies equivalent railway-planning depth or institutional maturity; OSRD publishes an active [roadmap](https://osrd.fr/en/about/roadmap/) |
| [Eclipse SUMO](https://eclipse.dev/sumo/) | Microscopic multimodal traffic, pedestrian/public-transport and network interaction | A common city revision connected to rail engineering and delivery packages | That OSR native results are independently validated until matched inputs and tolerances are published |
| Netzgrafik-Editor | Regular-interval timetable editing and connections | Downstream asset, financial and construction effects | That a broad platform replaces every specialist timetable tool |
| EULYNX / railML / RCM-DX | Signalling interfaces and railway data exchange | Owner-held integration and lifecycle records | That interface standards or partial simulators are turnkey signalling products |
| [Bentley OpenRail Designer](https://www.bentley.com/en/products/openrail-designer/) and connected commercial tooling | Specialist alignment, cant, turnout, corridor, documentation and multidisciplinary CDE workflows | Inspectable source, adaptable workflow and owner-held configuration | That commercial products are uniformly closed, obsolete or non-interoperable |
| [IBM Maximo](https://www.ibm.com/products/maximo/travel-transportation) and specialist EAM/APM systems | Deployed asset, work, inspection, inventory and reliability management | A railway-specific, locally adaptable implementation connected to public engineering definitions | Equivalent supportability, scale or operating history before a real deployment measures it |
| Commercial train/CBTC/turnkey suppliers | Accepted product configurations, system integration, commissioning and lifecycle support | A different ownership, localisation and supplier-replacement proposition | Equivalent safety, availability, delivery price or passenger service before physical evidence and like-for-like offers exist |

The practical open-source competitor is also a competent integrator assembling
QGIS, FreeCAD/Bonsai, ERPNext and FUXA directly. OpenSourceRail earns its place
only when its common identities, revisions, quantities, interfaces, evidence
and repeatable deployment workflow measurably reduce reconciliation work and
errors.

## Claims Register

| Claim | Current status | Evidence required before strengthening it |
|---|---|---|
| The repository joins planning through maintenance | Demonstrated in reproducible software and generated evidence | Retain exact-commit integration and recovery results |
| The owner can retain inspectable source and records | Supported by repository licences and architecture | Deployment contracts must preserve data export, configuration, tooling and step-in rights |
| The owner/operator stack is adoptable before train control | Credible product proposition | One real workshop/depot deployment with baseline, user, integrity, recovery, support and outcome measurements |
| The railway is cheaper than commercial alternatives | Unproven; mechanisms and editable sensitivities exist | Same corridor, scope, capacity, civil mix, risk, acceptance, warranty, spares, renewals and financing; independent or tendered prices |
| The LM3 can be locally manufactured | Development objective with controlled work packages | Supplier-backed BOM, production drawings, closed mass/axle loads, qualified processes, first articles and repeated conformity |
| GoA4 is ready for passenger operation | False | Frozen safety architecture, production hardware/transports, HIL and field evidence, independent assessment and authorization |
| An industrial partner or manufacturer supports OSR | Unverified until contracted | Exact legal entity, authority, named resources, equipment responsibility, warranty and contribution evidence |

The cost model must keep factory-gate repeat-unit targets separate from
non-recurring engineering, factory/tooling, supplier qualification,
homologation, commissioning, warranty, spares, renewals and finance. Import
content measures foreign-exchange exposure; it does not by itself determine
external borrowing.

## Four Proof Programmes

### 1. Prove The Owner/Operator Product

Deploy the [first adoptable product](first-adoptable-product.md) in an existing
workshop, depot or bounded pilot environment. Measure:

- asset and work-record completeness before and after migration;
- elapsed time and reconciliation errors from defect to inspected handback;
- evidence retrieval, backup and clean-volume recovery;
- inventory, calibration, competence and authorization exceptions;
- implementation/support hours and operator-owned exit/export results;
- user review time, error rates and overrides where AI-assisted drafts are used.

The comparison baseline is the operator's actual prior process or a stated
configured alternative—not an invented manual-work estimate.

### 2. Publish Rigorous Corridor Comparisons

Maintain multiple potential examples rather than treating one city as the
permanent reference. Samawah and Mosul are useful repository-backed starting
points; any of the catalogue cities—or a customer-supplied corridor—may enter
the candidate portfolio. For each selected study, obtain the relevant owner's
agreement, freeze its own input package and compare OSR native simulation with
SUMO or another independent railway tool for:

| Evidence family | Minimum publication |
|---|---|
| Geometry and service | Source/CRS/revision, line lengths, gradients, curves, station/turnback layout, dwell and timetable |
| Demand and capacity | OD source/calibration, boarding rules, sectional loads, platform/turnback constraints and crowding |
| Motion and energy | Train mass/configuration, resistance, traction/braking, auxiliaries, charging losses and full-day state of charge |
| Reliability | Delay distributions, charger/train/station outages, degraded headways, recovery rules and stranded-service outcomes |
| Civil and cost | Survey/topography basis, at-grade/elevated/bridge quantities, station scope, supplier quotes and excluded risk |
| Comparison | Versioned tools, identical inputs where possible, explained model differences, tolerance and adjudication owner |

A candidate pass means results agree within predeclared tolerances or each difference is
explained and accepted for its decision use. It is not a railway approval.
Comparisons remain separate evidence records so a strong result in one city
cannot conceal a weak or inapplicable result in another.

### 3. Make The Owner Platform Supplier-Neutral

Prove that a deployment can buy accepted trains, signalling or maintenance
equipment from another supplier while retaining OSR asset, project,
configuration and evidence workflows. Required demonstrations are:

- stable owner asset/product identities mapped to supplier identities;
- import/export and revision reconciliation in documented open formats;
- a supplier adapter that cannot cross the observation-only authority boundary;
- owner-held work, defect, inspection and handback history after adapter removal;
- documented exit, archive, backup and alternative-supplier qualification paths.

### 4. Close Physical Evidence, Not Catalogue Volume

Prioritise supplier-frozen configurations, released drawings, mass/CG/axle-load
closure, manufacturing qualifications, first articles, calibrated test results,
production hardware and independent field evidence. Adding another generated
city does not close any of those gates.

## Evidence-Led Release Sequence

| Stage | Product decision | Exit evidence |
|---|---|---|
| C0 — Position | Decide which of the three products is being offered | Named customer problem, bounded scope and accurate maturity statement |
| C1 — Benchmark | Establish a fair alternative and baseline | Common requirements, input package, comparison method and accepted tolerances |
| C2 — Demonstrate | Run the product in a controlled customer environment | Exact configuration, observed outcomes, failures, recovery and user acceptance |
| C3 — Contract | Allocate delivery, data, support and liability | Legal counterparties, acceptance, warranty, IP/data, change, exit and support terms |
| C4 — Replicate | Reuse only what evidence supports | Audited cost, schedule, reliability, capability and lessons from the applicable reference projects |

Commercial or partnership work follows the separate
[joint-development framework](commercial/joint-development-framework.md) and
its fail-closed [readiness record](commercial/partnership-readiness.md).

## Primary Sources Used For The Framework

- [OSRD product and governance](https://osrd.fr/en/) and [published roadmap](https://osrd.fr/en/about/roadmap/)
- [Eclipse SUMO product](https://eclipse.dev/sumo/) and [railway simulation documentation](https://eclipse.dev/sumo/docs/Simulation/Railways.html)
- [Bentley OpenRail Designer](https://www.bentley.com/en/products/openrail-designer/)
- [IBM Maximo for travel and transportation](https://www.ibm.com/products/maximo/travel-transportation)
- [WIPO technology-transfer and joint-venture guidance](https://www.wipo.int/en/web/technology-transfer/agreements)

Product pages describe their publishers' capabilities and are not independent
comparative evaluations. A procurement must verify the applicable version,
configuration, licence, support, references and offered terms directly.
