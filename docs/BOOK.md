# OpenSourceRail: open engineering platform

**Reader edition: 13 November 2026.** The published software release is
[v0.6.1](releases/v0.6.1/README.md). v0.7 is in development; its
[execution record](design-engine/v07-execution/README.md) separates completed
software and numerical work from unresolved engineering and physical evidence.

OpenSourceRail develops an affordable, accessible urban railway and the open
tools needed to plan, design, make, operate, maintain and renew it. Local design
knowledge, manufacture and repair are central to the project. The platform
connects city planning, railway engineering and manufacturing/lifecycle work;
the three products must share explicit candidate and source identities.

## What is available

| Area | Supported scope | Boundary |
|---|---|---|
| Published software | v0.6.1 planning, research, Workbench and delivery tools; the clean-install Samawah journey is recorded. | Software publication does not approve hardware or train operation. |
| City comparison | Calculated outlines for 266 city networks and a candidate-bound Samawah station-edit comparison. | Route, demand, land, ground, access and prices can remain provisional. |
| Engineering research | Counted vehicle and civil concepts, SolidCraft/FieldCraft studies, independent controls and source-bound candidate packets. | A calculated or converged model is not a qualified installation. |
| Business and maintenance | ERPNext/Frappe HR and FUXA/gateway adapters, draft records and a bounded assembly custody contract. | Native full-module transactions, live control and purchasing authority remain separate. |

Use the [capability register](capabilities/README.md) for specific entry points
and maturity. The [v0.6.1 known limitations](releases/v0.6.1/known-limitations.md)
define the published release boundary. The stale integrated engineering dossier
and portfolio selector are held; this reader does not draw conclusions from
them.

## Development reference and research alternatives

The development reference uses six 17 m cars with passive wheel bogies on
conventional rails carried by concrete. Each car has 44 fixed seats and two
wheelchair places, with no planned standing and two doors on one side. The
passive aluminium secondary is a comparison interface. Installed propulsion,
powered length, acceleration, braking and operating headway are selected per
candidate. The former maglev configuration and the 120-second service case are
retained research controls, not the selected physical railway.

Research candidates may change traction, running gear, formation, station
spacing or civil form. Each change must carry its mass, power, heat, protection,
service, manufacture, construction and whole-life cost effects. Mandatory
safety, accessibility and passenger protection stay as requirements. The
[architecture](ARCHITECTURE.md) explains how candidate, evaluation and selection
identities prevent results from being mixed.

## One corridor through v0.7

The [v0.7 roadmap](ROADMAP.md) uses one Samawah corridor revision as the
integration case. Two source station markers are about 79.977 m apart against
a 120 m platform assumption. The reviewed midpoint edit changes raw markers
from 26 to 25; the published comparison already groups them into 25 operational
stops, so its fleet stays at 81. The project envelope identifies which service,
quantity, cost and dossier results change and which unaffected results are
reused. These are planning calculations, not a surveyed alignment.

Current v0.7 evidence also includes a headless native GIS two-edit cycle for
Samawah and Baghdad, bounded civil and force/braking controls, and a measured
opt-in Rust delivery scheduler. The measured complete delivery-CLI median fell
from 12.49 to 10.79 seconds across three paired Samawah trials with a prebuilt
binary. That is a 13.64% reduction for this compiler path; it is not a
whole-city or engineering-solver speedup. The [agent delivery plan](plans/v0.7-agent-delivery-plan.md)
keeps further Rust work tied to measured bottlenecks and exact output parity.

## The door module and the next physical interfaces

The candidate-bound one-opening handoff counts 74 part types and 694 pieces:
97 locally fabricated, 568 bought to standard and 29 bought to qualification.
Its 597 purchased pieces span 35 types. The software custody contract checks
receipt-backed, individually serialized purchased children with serial, batch,
incoming QA and parent consumption. A sealed, reviewed synthetic one-child
pack exercises that contract. The complete module has not passed a native
ERPNext receipt, assembly, replacement and handback journey.

The opening layout still lacks controlled header/body, rail/carriage,
belt/pulley, drive and sensor mating datums. Installed transforms, approved
inspection limits, clearance and removal paths, complete installed mass and
physical acceptance remain open. A 2 m display proxy does not establish fit
for the 2.9 m guide stock. The [handoff and evidence record](design-engine/v07-execution/README.md)
identifies each unresolved interface; no missing quantity or limit is zero.

Civil work likewise needs a represented rail/support/load domain, bearings,
foundations, erection stability and a crane chart at the actual lift radius.
Propulsion and braking need installed force, current and repeated thermal-duty
evidence. Independent physical tests and reviews remain necessary before any
manufacturing, movement or operating release.

## Use and reproduce the software

Start with the [published installation instructions](releases/v0.6.1/README.md)
and their checksum-verified downloads. The [Workbench](workbench/current/index.html)
shows supported journeys and visible holds. The repository exposes bounded
research commands:

```bash
./osr design railway plan
./osr design railway run --max-bundles 2 --native-jobs 1
./osr design railway verify
./osr book --check
```

Native CAD, FEM and GIS jobs need compatible tools, declared resource budgets
and exact input identities. Keep a host disk reserve and retain failed or
interrupted run evidence. Current v0.7 work uses SolidCraft, FieldCraft and
RustGIS in their demonstrated domains; optional independent solvers remain
useful for verification. A tool substitution creates a new evaluation, not a
new physical design by itself.

## Source, review and history

The [project README](../README.md) remains the public entry point. This PDF
also includes that entry point, the capability register, release scope and
limitations, and roadmap as source-attributed chapters. The v0.7 execution
record remains linked and source-bound to this edition.
The [platform guide](platform-guide.md) retains deeper v0.6 reference and
research background under its stated evidence limits.
The [documentation index](INDEX.md) lists further maintained guides. The
[v0.7 execution ledger](../campaigns/v07-execution.json) records task status,
candidate boundaries and evidence. The current book PDF has its own source
receipt; its summaries do not supersede the sealed engineering packets.

The published v0.6.1 release and historical v0.6.0, v0.5 and v0.4 records keep
their original identities. Earlier maglev and source-bound research remain
retrievable through the [historical manifest](archives/pre-comfort-default/manifest.json).
Their results apply only to their declared candidates and methods. Preserve
useful failures, open assumptions and original hashes when revising the design.

Software is licensed under Apache 2.0, open physical designs under CERN-OHL-S
v2, and documentation under CC-BY-SA 4.0, subject to path-specific notices in
the [license guide](../LICENSE.md).
