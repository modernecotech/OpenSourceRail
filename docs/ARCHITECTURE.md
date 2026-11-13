# OpenSourceRail architecture

OpenSourceRail connects three products: a design and delivery platform, a
reference railway and manufacturing system, and open GoA4 control software. The
delivery lifecycle covers planning, design, procurement, manufacture,
construction, commissioning, operation, maintenance and renewal. Local design
authority, repairability and whole-life affordability are objectives that each
candidate must demonstrate.

## Selected v0.6 vehicle reference

[`development-baseline.toml`](../engineering/development-baseline.toml) selects
six 17 m comfort cars with 44 fixed seats and two wheelchair places per car, no
planned standing. Passive steel-wheel bogies run on conventional rails carried
by concrete. The vehicle retains a passive aluminium secondary interface; this
does not select an installed propulsion system. The reference vehicles have no
normal-service traction motors, traction batteries or permanent magnets.
Independent braking, service power, protection and rescue provisions remain
required.

The selector's `propulsion_design` policy requires candidate-specific selection
of architecture, installed powered length, acceleration, braking and headway.
Neither 900 m nor 100 m is a prescribed installation. The 72 km/h launch cap,
120-second headway and 35-second dwell form a named retained service control,
rather than selected operating requirements.

The selected candidate is a development reference. It has not been physically
qualified or released for manufacture or passenger operation. The 8,280
passengers/hour/direction figure is capacity arithmetic, not a demonstrated
service. A reference records the purpose of selection; an alternative records
a comparison role. An evaluated result names the calculation and evidence scope.
Prototype validation requires its own physical evidence and remains undemonstrated.

## Connected platform

The [planning workspace](workbench/planning/index.html) verifies current city
route and map-context sources, displays the available geographic layers, and
supports route, stop, service and OD editing. Run
`./osr plan compile edits.json --output build/my-plan` to create an immutable
proposal handoff bound to the selected candidate, then verify it with
`./osr plan verify build/my-plan`. The handoff carries proposals only; it
excludes vehicle, propulsion, fleet, civil quantity, cost, performance and
cashflow results. It grants no movement authority.

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
| Propulsion candidate | Mechanism-specific force, power, losses, thermal duty, interfaces and handoff; electrical and magnetic maps where applicable |
| Braking and journey | Same candidate mass and geometry, independent brakes, service energy, station power and protection |
| Rail and civil | Moving axle reactions, rails and fasteners, alignment, deflection, torsion, piers, foundations and erection |
| Delivery | Candidate-matched BOM, manufacturing processes, procurement, assembly, CAD/IFC and maintenance records |
| Economics | Equal passenger service, routes, reliability, design life, installed scope and price uncertainty |

The [held v0.6 reference dossier](design-engine/current/README.md) and its
[candidate twin exports](design-engine/current/exports/manifest.json) retain
their source identities. The [platform reader](../OpenSourceRail-Book.pdf)
summarises the published software and current v0.7 work without treating that
dossier as supported release evidence. The CLI and Workbench show source holds.
Candidate-specific city performance publication remains held until
propulsion, braking, route, civil and economic evidence supports it. Physical
qualification and independent review remain open.
