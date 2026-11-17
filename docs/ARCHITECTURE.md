# OpenSourceRail architecture

OpenSourceRail connects three products: a design and delivery platform, a
reference railway and manufacturing system, and open GoA4 control software. The
delivery lifecycle covers planning, design, procurement, manufacture,
construction, commissioning, operation, maintenance and renewal. Local design
authority, repairability and whole-life affordability are objectives that each
candidate must demonstrate.

The [v0.7 engineering decision register](ENGINEERING-STATUS.md) tracks the
selected reference and separate prototype research. The [cost baseline](COST-BASELINE.md)
and [finite release gate](RELEASE-v0.7.md) govern current public claims.

The [v0.7 concept configuration](reference-v07/README.md) combines a powered-wheel
vehicle, joint-free 10 m span, twelve-station synthetic 30 km service,
fourteen-scope budget and construction programme under one planning ID. Its
**US$1.0235bn** capital and **43-month** programme are concept estimates. The
separate [Baghdad concept](../cities/Baghdad/PROPOSAL.md) uses a 700-place child
train and its own capital and schedule.

The [joined prototype quotation basis](reference-v07/integration/README.md)
controls the car, guideway, station and power interfaces for one configuration.
Its [manufacturing handoff](reference-v07/manufacturing/README.md) gives a
candidate-linked BOM, shop route, QA points and ERPNext import draft. These
support supplier quotation and prototype planning; fabrication and operation
still require approved drawings and measured tests.

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

## v0.7 prototype architecture under test

The [equal-service decision screen](design-engine/v07-architecture-decision/README.md)
advances a **separate powered-wheel research child** for prototype quotation
and measurement. Its proposed six-car layout has 24 motorised axles and
protected 1.5 kV DC roof collection from rigid overhead supply. The
[electrical demand](design-engine/v07-powered-bogie/README.md) and
[mechanical car layout](design-engine/v07-powered-vehicle/README.md) retain
their own component identities. A [source-bound prototype research bundle](design-engine/v07-prototype-bundle/README.md)
joins them under a new physical candidate and propagates their upper equipment
mass into service demand, a provisional quote BOM and nominal IFC interfaces.
Its selection identity authorises the **next quotation and test**, not an
installed drive or civil selection. This prototype direction does not revise
the v0.6 passive-wheel reference.

The bounded 30 km comparison shows station-only launch stalling on the tested
1% and 2% uphill sensitivities, and one 250 m booster stalling on 2%. Powered
wheels reach those demand cases, but available motor output, wet adhesion,
independent braking, overhead clearance, installed mass and price remain
unproved. A station-charged battery or battery–supercapacitor system would
require megawatt-scale charging within the 35 s dwell hypothesis; it is
retained as a separately costed alternative, not assumed to be a small store.
The proposed overhead-fed car retires the passive LIM fin and station primary
only within its research child. The [joint-free 10 m span screen](design-engine/v07-simple-span/README.md)
is a distinct civil alternative to the jointed 20 m beam, with a powered crowd
load but no surveyed ground or supplier installed price. The [priced v0.7
concept](reference-v07/README.md) establishes a planning budget and method.
Supplier equipment, physical tests and a surveyed alignment determine the
installed design.

## Connected platform

The [planning workspace](workbench/planning/index.html) verifies current city
route and map-context sources, displays the available geographic layers, and
supports route, stop, service and OD editing. Run
`./osr plan compile edits.json --output build/my-plan` to create an immutable
proposal handoff bound to the selected candidate, then verify it with
`./osr plan verify build/my-plan`. The handoff carries proposals only; it
excludes vehicle, propulsion, fleet, civil quantity, cost, performance and
cashflow results. It grants no movement authority.

The editable Workbench source is `engineering/development_baseline/web/`.
`docs/workbench/current/` is the generated public copy: the station publisher
copies its core assets and the city-atlas publisher copies its map assets with a
source-checked receipt. Matching files in the two directories are expected
publication outputs, not two independent implementations.

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

The integrated v0.6 reference dossier is held at a source-binding mismatch;
its local packet may be unavailable. The [v0.6 design-closure ledger](design-engine/v06-design-closure/README.md)
records open findings. Candidate twin exports retain their own source identities
when materialized and verified. The [platform reader](../OpenSourceRail-Book.pdf)
summarises the published software and current v0.7 work without treating that
dossier as supported release evidence. The CLI and Workbench show source holds.
Candidate-specific city performance publication remains held until
propulsion, braking, route, civil and economic evidence supports it. Physical
qualification and independent review remain open.
