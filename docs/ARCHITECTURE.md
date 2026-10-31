# OpenSourceRail architecture

OpenSourceRail connects three products: a design and delivery platform, a
reference railway and manufacturing system, and open GoA4 control software. The
delivery lifecycle covers planning, design, procurement, manufacture,
construction, commissioning, operation, maintenance and renewal. Local design
authority, repairability and whole-life affordability are objectives that each
candidate must demonstrate.

## Selected v0.6 research candidate

[`development-baseline.toml`](../engineering/development-baseline.toml) selects
six 17 m comfort cars with 44 fixed seats and two wheelchair places per car, no
planned standing, and a 120-second service target. Passive steel-wheel bogies
run on conventional rails carried by concrete. Double-sided station linear
induction motors act on passive onboard aluminium secondaries. The vehicles
have no normal-service traction motors, traction batteries or suspension
magnets. Independent braking, service power, protection and rescue provisions
remain required.

The selected candidate is a development reference. It has not been physically
qualified or released for manufacture or passenger operation. The 8,280
passengers/hour/direction figure is capacity arithmetic, not a demonstrated
service.

## Connected platform

The [planning workspace](workbench/planning/index.html) verifies current city
route and map-context sources, displays the available geographic layers, and
supports route, stop, service and OD editing. `./osr plan compile` creates an
immutable proposal handoff bound to the selected candidate, and `./osr plan
verify` checks its identities and sources. The handoff carries proposals only;
it does not calculate current route performance, procurement quantities,
construction schedules or complete city costs. It grants no movement
authority.

The coordinator carries one candidate bundle through geometry, mass, analysis,
BOM, CAD/IFC, procurement, assembly, construction and controls. The current
[engineering exports](design-engine/current/exports/manifest.json) and
[coupled delivery index](design-engine/coupled-railway/delivery-index.json)
provide candidate-linked research records. They do not imply complete installed
equipment, qualified manufacturing instructions or approved business records.

[ERPNext and Frappe HR](../deployment/erpnext/README.md) provide draft business,
workforce, procurement, production, QA and maintenance workflows.
[FUXA and the gateway](../deployment/supervision/README.md) support observation,
alarm, history and review records. Company and site masters, permissions,
authenticated device bindings and reviewed imports are deployment inputs.
Neither integration supplies movement authority or accepts engineering evidence
automatically.

## Identity and evidence boundaries

The physical candidate identity describes the vehicle, support and propulsion
configuration. Evaluation identity binds models, sources and scenarios.
Selection identity records which candidate is used for a stated purpose. A
different model hypothesis is a different evaluation; a physical revision gets
a new candidate identity. Mixed identities fail closed, and downstream results
must be regenerated when upstream evidence changes.

Unknown installed mass, force, heat, cost, origin or qualification remains
unknown or bounded. Calculated assumptions can complete a research scenario but
cannot establish a physical result. Software execution, numerical validity,
engineering screening, evidence maturity, selection purpose and physical
acceptance remain separate records.

## Coupled engineering domains

| Domain | Required coupling |
|---|---|
| Vehicle | Complete fitout, bogies, service supply, thermal equipment, load paths, mass and inertia |
| Station propulsion | Force/current/frequency/gap/temperature, normal force, losses, cooling and section handoff |
| Braking and journey | Same candidate mass and geometry, independent brakes, service energy, station power and protection |
| Rail and civil | Moving axle reactions, rails and fasteners, alignment, deflection, torsion, piers, foundations and erection |
| Delivery | Candidate-matched BOM, manufacturing processes, procurement, assembly, CAD/IFC and maintenance records |
| Economics | Equal passenger service, routes, reliability, design life, installed scope and price uncertainty |

The [current dossier](design-engine/current/README.md), CLI, Workbench,
[candidate twin exports](design-engine/current/exports/manifest.json) and
[project reader](../OpenSourceRail-Book.pdf) expose the current development
selection. City performance publication remains held until candidate-specific
propulsion, braking, route, civil and economic evidence supports it. Physical
qualification and independent review remain open.
