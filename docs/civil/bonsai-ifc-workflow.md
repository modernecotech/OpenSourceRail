# Bonsai / IFC4.3 Civil Workflow

Status: implemented design-reference workflow  
Baseline: Bonsai 0.8.5, Blender 5.2, IfcOpenShell/IfcTester/BCF 0.8.5, IFC4.3

## Decision

Bonsai is better suited than FreeCAD alone for the federated civil BIM part of
OpenSourceRail: native IFC authoring, rail-domain object classification,
property and quantity inspection, drawing/coordination work, and construction
sequence review. It is not currently a better source for deterministic railway
alignment engineering. The OSR alignment engine and parametric civil catalogue
therefore remain authoritative; Bonsai receives a generated IFC4.3 model and
must not silently override its route or engineering rules.

| Information | Authority | Bonsai role |
|---|---|---|
| Horizontal/vertical alignment, transitions, cant and rule checks | OSR-ALN plus accepted survey/GIS inputs | Inspect the exported `IfcAlignment` reference and coordinate issues |
| Pier, girder, trackform, platform and canopy parameters | `design/component-catalogue/src/osr_mech/` | Federate, classify, inspect, annotate and develop deployment detail against stable IDs |
| Structural capacity, reinforcement, bearings, foundations and temporary works | Reviewed analysis decks and engineer-released drawings | Coordinate released results; never infer approval from visible geometry |
| IFC object hierarchy, property sets, quantities and 4D task links | Generated IFC checked by IfcOpenShell schema/EXPRESS validation and IDS | Native GUI authoring/review environment |
| Civil planning rates | Generated `lib/templates/civil-cost-model.toml` from CAD quantities and reviewed benchmark shares | Inspect the model hash, rate properties and quantity basis; do not treat them as a quote |
| Revision identity | City Studio content hash and Git revision | Carry revision and source hashes in IFC properties and the saved Blender scene |

This boundary reflects current upstream limitations: Bonsai's road/rail guide
describes its PI CSV alignment import as a temporary stop-gap, while the
IfcOpenShell alignment API is still under development and explicitly does not
select engineering design parameters.

## Generate and review

Check the installed stack:

```bash
tools/automation/bonsai-civil.sh --check
```

Generate deterministic IFC and JSON evidence without opening Blender:

```bash
tools/automation/bonsai-civil.sh --generate
```

Generate, import through Bonsai, save a native review scene, and render it:

```bash
tools/automation/bonsai-civil.sh --render
```

Render the normalized construction sequence as MP4 as well:

```bash
tools/automation/bonsai-civil.sh --animate
```

To bind the federation to a City Studio line, use the **Generate Bonsai civil
IFC4.3** job in the engineering hub. The adapter converts the selected line to
the local engineering frame and supplies that immutable reference axis to the
same exporter. The civil settings panel can store an accepted map conversion
per stable line ID; it is Git-visible, revision-hashed, shown in semantic
revision comparison, and passed only when that line is regenerated.

Ordinary jobs are written beneath `build/engineering/bonsai-civil/`. The same
generator publishes the named GitHub-review set beneath
[`engineering/models/bim/reference/`](../../engineering/models/bim/reference/README.md):

- `civil-coordination.ifc` — native IFC4.3 model;
- `civil-coordination.index.json` — object-aware browser index and authority boundary;
- `civil-construction-sequence.json` — tasks, dates, QA holds and product assignments;
- `civil-information-requirements.ids` — buildingSMART IDS 1.0 delivery requirements;
- `civil-information-requirements.report.json` — complete deterministic IDS audit evidence;
- `civil-coordination-issues.bcf` — BCF 3.0 package with object-linked release issues;
- `civil-coordination-issues.index.json` — browser-safe issue and IFC selection index;
- `civil-coordination.validation.json` — reopen, IDS, BCF-link, and exact artifact-hash checks.

The tracked screenshot is under [`docs/screenshots/civil/`](../screenshots/civil/).
Bonsai `.blend` scenes, animation frames and videos are reproducible review
outputs and remain under `build/` or tagged GitHub Release storage.

## Model content

The current reference federation contains 185 stable assets and 19 reusable
component types organised below an
`IfcRailway` and four `IfcRailwayPart` containers: track, substructure,
above-track systems, and lineside/clearance. Civil objects use IFC4.3 types
including `IfcRail`, `IfcBeam`, `IfcBearing`, `IfcColumn`, `IfcSlab`, `IfcRoof`, and an
`IfcAlignment`. The selected line's control-point polyline is represented by
native `IfcAlignmentHorizontal` `LINE` segments, `IfcAlignmentVertical`
`CONSTANTGRADIENT` segments, an `IfcGradientCurve`, and stationing referents.
This improves civil-tool interoperability without inventing curve radii,
transitions, or cant that the planning input does not contain. Each asset carries:

- stable OSR asset ID and class;
- canonical source and source hash;
- revision ID and lifecycle status;
- inspectable coordination dimensions and source net volume;
- explicit detail mode when a complex assembly is represented by its review envelope.

One hundred and thirty-eight occurrences are linked to an `IfcTypeProduct` derived from their
exact asset class and source-geometry recipe. Types carry stable `OSR-TYPE-…`
identity and `OSR_Type`; occurrence placement and geometry remain
authoritative. The 47 virtual clearance, foundation, and jacking interfaces
remain untyped because IFC4.3 has no `IfcVirtualElementType`.

Each of the nine source pier compounds is split without overlapping geometry
into one column, one `IfcBeam/PIERCAP`, four `IfcBearing/ELASTOMERIC` products,
four bearing-replacement jacking interfaces, and one foundation interface.
The bearings retain their measured 0.6 × 0.5 × 0.1 m source envelopes and
explicitly unresolved supplier/load/movement schedules. Foundation and jacking
zones use `IfcVirtualElement`: the source intentionally withholds the actual
foundation type and depth, so exporting `IfcFooting` or `IfcDeepFoundation`
would assert engineering that does not exist.

Face contact in the checked envelopes also generates 27
`IfcRelConnectsWithRealizingElements` relationships: 24 beam-end connections
realized by two bearings each and three station-deck connections realized by
four bearings each. All 36 bearings participate in the resulting 60
realizations. The relationships record physical topology only; connection
geometry, stiffness, loads, movement capacity, supplier selection, and release
remain deliberately unset.

Three native `IfcMaterial` family declarations cover 46 occurrences through
five type associations: running-rail steel, prestressed beam concrete, and
precast platform-unit concrete. `OSR_MaterialStatus` identifies the source
authority and explicitly records that grade, design, supplier certification,
and release remain unresolved. Mixed or interface-only assemblies receive no
material association until their constituent specification is authoritative.

The 32 straight running-rail occurrences use one native
`IfcMaterialProfileSet` and cardinal-point-5 `IfcMaterialProfileSetUsage`.
Their bodies are `IfcExtrudedAreaSolid` geometry driven by the same simplified
60E1 polygon as the CAD source, replacing coordination box meshes. The indexed
section area and extrusion volume are checked against the source solid. This
remains a straight-line review polygon; procurement still requires the full
mill profile, fillets, tolerances, released steel grade, and certificates.

### Native OSR asset classification

One internal `IfcClassification` contains 15 lightweight references using the
existing OSR asset codes. One hundred and thirty-eight occurrences inherit
their reference from 19 reusable types; the 47 untyped virtual interfaces
receive their class directly. All 185 assets therefore remain natively queryable without
duplicating type-level relationships. This classification supports OSR
automation only. Its metadata and City Studio inspector explicitly state that
country/client mappings remain unnominated and require an approved deployment
crosswalk.

The five source layouts are also native `IfcGroup` coordination groups, with
all 185 assets assigned exactly once. Their properties state that they are
separated review layouts—not surveyed spatial zones or functional engineering
systems—so Bonsai and City Studio can filter them without asserting false
`IfcSpatialZone` semantics or confusing review geography with system function.

Six native `IfcSystem`-family records provide the separate functional view:
track and running way, guideway structure, station interfaces, rolling-stock
reference, clearance assurance, and unreleased civil interfaces. IFC4.3 specializations are used where the
source supports them: track is `IfcBuiltSystem/RAILWAYTRACK`, guideway is
`IfcBuiltSystem/LOADBEARING`, and the station interface is
`IfcBuiltSystem/USERDEFINED`; clearance and rolling-stock references remain
generic `IfcSystem`. Foundation and jacking interfaces use a generic system
because virtual elements cannot be members of an `IfcBuiltSystem`. The 15
authoritative OSR asset classes map without overlap, so all 185 occurrences
have exactly one membership.

Four `IfcRelReferencedInSpatialStructure` relationships provide seven explicit
links from the systems to the track, substructure, above-track, or lineside
`IfcRailwayPart` they cover. The station system legitimately spans two parts.
These are non-hierarchical spatial-service references, not containment. The
systems remain design-reference groupings—not surveyed zones, commissioned
operational systems, or safety releases—and track number, usage,
electrification, and other unavailable operational properties stay unset.

The two representative LM3 trainsets use native `IfcVehicle/ROLLINGSTOCK`
occurrences and one reusable `IfcVehicleType/ROLLINGSTOCK`, replacing the former
generic building proxies. Each vehicle carries the standard
`Qto_VehicleBaseQuantities` Length, Width, and Height measured directly from
the deterministic geometry. Capacity, mass, availability, serial identity,
manufacturer, and operational release are intentionally not inferred.

Four `IfcPresentationLayerAssignment` records assign each asset's
`IfcShapeRepresentation` to track, substructure, above-track, or lineside.
They provide native visibility filters for Bonsai and layer-oriented CAD/BIM
tools. They deliberately carry no engineering meaning beyond simple geometry
grouping; object identity and semantics remain in IFC objects, types,
classification, and coordination groups.

The nine deterministic integration gates are native project-level
`IfcObjective` constraints with hard `DESIGNINTENT` semantics, source path,
fixed evaluation time, current observation, and PASS/FAIL state. Six checks
also carry native nested `IfcMetric` records with `EQUALTO` length benchmarks;
their observed and target values come from structured integration data, not
parsed prose. The other three gates remain explicitly qualitative because their
sources provide no defensible numeric benchmark.

All custom properties now use the standards-compliant `OSR_` prefix; the IFC
`Pset_` prefix is reserved for property sets defined by buildingSMART. Sixteen
native `IfcPropertySetTemplate` dictionaries declare 99 property and quantity
field types across occurrence, type, material, profile, and quantity data.
Applicable templates link 483 `IfcPropertySet`/`IfcElementQuantity` definitions
via `IfcRelDefinesByTemplate`; material and profile resources cannot use that
relationship, so their four definitions match the declared material/profile
templates by name and template type. All 16 templates are declared in the IFC
project context and indexed for City Studio inspection.

Fifteen native `IfcDocumentInformation`/`IfcDocumentReference` records expose
the actual repository sources used by the federation. Complete SHA-256
revisions and repository-relative locations cover the component generators,
integration source, exporter, alignment contract, cost contract, and this
release-boundary workflow. `IfcRelAssociatesDocument` links all 185 occurrences
and their reusable types to the applicable source modules. These are source
records, not issued drawings or a substitute for a deployment CDE.

Dimensions, source volume, and representation count are native
`IfcElementQuantity` values in `OSR_CoordinationEnvelopeQuantities`, with the
calculation method declared on the quantity set. The four discipline containers
also declare the IFC4.3-required `VERTICAL` railway-part usage. The exporter
runs IfcOpenShell schema and EXPRESS rules after writing and rejects any issue;
the result is retained in `civil-coordination.validation.json`.

The default model deliberately remains on the named local engineering grid.
When accepted survey/GIS control exists, use City Studio's per-line **IFC
survey control** form or add this optional block to the civil alignment input:

```json
{
  "georeferencing": {
    "crs_name": "EPSG:9306",
    "eastings": 198765.4,
    "northings": 431234.5,
    "orthogonal_height": 18.25,
    "x_axis_abscissa": 0.999847695,
    "x_axis_ordinate": -0.017452406,
    "scale": 0.99995,
    "source": "Accepted survey control revision S-04"
  }
}
```

Use the actual project CRS and survey transform; the example values are only a
shape example. With the block present, the IFC contains `IfcProjectedCRS` and
`IfcMapConversion`. Without it, the index and project properties explicitly
record `project-crs-unresolved` rather than inventing map coordinates. For a 3D
model, use a compound CRS that identifies the vertical datum as required by
IFC4.3.

The IFC project also carries `OSR_CostModel`: the generated contract hash,
maturity and current class rates. Its JSON index includes the full per-route-km
quantity basis. Editing a reviewed parametric dimension and regenerating first
updates the quantity model and cost contract, then emits both into IFC and city
CAPEX. Direct Bonsai edits remain coordination changes until promoted back into
the authoritative parametric source.

The same generated contract is also represented by one native USD
`IfcCostSchedule` with `SCHEDULEOFRATES` semantics and three `IfcCostItem`
alternatives: at-grade, elevated, and bridge. Each `IfcCostValue` uses a
1,000-project-metre unit basis. The items intentionally have no cost quantities
or product assignments, so consumers cannot mistake mutually exclusive
planning rates for a selected scope, multiplied project total, bill, tender,
or quotation. The cost-contract document is hash-locked to both the project
and this schedule.

Eighteen track, station, and viaduct tasks are embedded in an
`IfcWorkSchedule`. Five tasks now carry stage-specific outputs: track completion,
station structural assembly, foundation/pier/cap completion, bearing/beam
erection, and viaduct trackform/egress finishing. Native
`IfcRelAssignsToProduct` relationships distinguish 134 physical construction
outputs from 45 virtual foundation/jacking review interfaces by relationship
name and description. Virtual interfaces therefore participate in their QA
gate without appearing as constructed products in the 4D animation.
Predecessors, planning durations, hold points, and evidence remain in the
companion sequence index.

![Bonsai support-end review of twin OSR-Pi25 decks and the reduced common cap](../screenshots/civil/bonsai-pi25-support-detail.png)

The support-end render is generated by the same command. It shows the
coordination relationship between the two narrow track decks, bearing lines,
7 m common cap and independent outer walkway/containment cassettes; it does not
represent released reinforcement, prestress or connection detailing.

## IDS delivery gate and BCF review loop

The exporter writes an IDS 1.0 contract and immediately reopens it with
IfcTester against the written IFC. Twenty specifications cover all 185 assets,
the 19-type catalogue, the source-backed material subset, alignment authority,
the native rail-profile assignments, OSR asset classification, native document
register, five coordination groups, six functional systems, four presentation
layers, 36 native bearings and their connectivity records, nine virtual foundation interfaces, two native vehicles
and their standard base quantities, nine interface constraints, six native
metrics, typed property dictionaries, the planning schedule of rates, and
project provenance. The current reference exchange passes all 3,340
entity-level checks. The audit is deterministic: entity
evidence is sorted before hashing, so a repeat build produces byte-identical
IFC, IDS, audit, BCF, indexes, sequence, and validation files.

Passing IDS means that the information delivery is complete for this declared
coordination purpose. It does not mean the design is structurally or legally
released. The generated BCF 3.0 package therefore carries three open issues
with viewpoints and selected IFC GUIDs:

1. replace the planning axis with accepted survey and alignment geometry;
2. release the elevated station deck structural design;
3. complete the viaduct span, bearing, pier, foundation, and reinforcement work.

City Studio exposes the requirement report and issue index alongside the IFC.
Bonsai can open the native BCF package for discipline coordination and issue
closure against the same stable objects.

City Studio also pairs the object index with the hash-verified construction
sequence. Its interactive review controls rotate the projected federation,
toggle any of the four native presentation layers, five coordination groups,
or six functional systems, and scrub or play the 18-task 4D sequence while
showing the current QA hold, physical-output count, virtual-review count, and
visible-asset count. These projected envelopes
support rapid coordination and BCF selection; native tessellated geometry and
authoritative IFC editing remain in Bonsai.

City Studio stores a review decision in the project's committed
`coordination/issues.toml`. It never rewrites a prior BCF artifact. Closing or
resolving a topic requires both resolution evidence and a reviewer; the next
civil job reads the new content-addressed revision and emits a fresh BCF with
the same deterministic topic/viewpoint identities and updated status,
assignee, resolution, and reviewer.

The IFC object inspector can also create a new coordination topic against a
selected stable asset. Custom issues use a deterministic content-derived ID;
their asset IDs must resolve in the regenerated federation. The exporter then
creates deterministic BCF topic/viewpoint UUIDs and a selected-component
viewpoint. Unknown assets fail the civil job instead of producing a dangling
coordination reference.

## Engineering release boundary

The generated model is deliberately labelled **design-reference / not for
construction**. Its nine current gates check interface geometry such as
rail/platform datums, clearance gaps, pier bearing top to girder soffit, and
station/viaduct track-support continuity. It does not release geotechnical
parameters, reinforcement, prestress, bearing schedules, seismic restraints,
drainage capacity, construction loads, or local-code compliance. Those remain
deployment analyses and competent-engineer decisions linked back into IFC only
after review.

Each gate remains governed by the `IfcProject`, while its single
`IfcRelAssociatesConstraint` also identifies the evidence it evaluates. Across
the nine objectives this produces 91 asset, six review-group, one functional-
system, and nine project links. City Studio exposes those IDs directly. This
scope is traceability, not a claim that the qualitative checks replace
structural analysis or approval.

The registered, SHA-256-locked civil-integration `IfcDocumentReference` is
also attached to all nine objectives and their six metrics by one
`IfcExternalReferenceRelationship`. This is the IFC4.3 resource-level link
intended for constraints, which do not inherit from `IfcRoot`; it is provenance
only and does not represent approval, issue, or engineering release.

## Capability closure and external decisions

All IFC/Bonsai work supported by the current repository inputs is implemented.
The generated index reports `source-supported-ifc-work-complete` with zero
implementable open tasks. Nine external-decision records identify the named
authority, evidence, blocked capability, and safe current state for work that
cannot be completed truthfully from repository data alone.

| IFC capability | Decision |
|---|---|
| Native quantity take-off | Implemented now; it replaces quantity-shaped generic properties and enables later parametric IFC costing. |
| CRS/map conversion | Implemented now as validated opt-in input; unresolved projects remain visibly local rather than receiving a guessed EPSG code. |
| Alignment layouts and linear placement | Native horizontal `LINE` and vertical `CONSTANTGRADIENT` planning segments, gradient-curve geometry, and stationing are implemented from the selected line polyline. Design radii, transition spirals, vertical curves, cant, and product linear placement remain deferred until an accepted OSR-ALN design supplies those parameters; LandXML, railML, and stakeout CSV remain the detailed handoff. |
| Native `IfcCostSchedule` | Implemented as a USD `SCHEDULEOFRATES` with three generated route-kilometre alternatives and a 1,000 m unit basis. It has no product assignments, cost quantities, or project total; element-level estimating remains deferred until approved rates and selected scope exist. |
| Reusable object types | Implemented for 138 safely typable occurrences using exact source recipes. Type geometry maps are deliberately omitted so occurrence geometry remains authoritative. |
| Material families | Implemented for the 46 occurrences whose source explicitly declares a safe single-material family. Every declaration is visibly grade/design unresolved. |
| Native rail profile | Implemented for all 32 straight 60E1 rail occurrences using a shared material profile set, occurrence usages, and matching extruded solids. |
| Native rolling-stock vehicles | Implemented for both representative trainsets with one reusable `IfcVehicleType/ROLLINGSTOCK` and standard measured Length, Width, and Height quantities. Operational, manufacturer, capacity, mass, and availability fields remain unset until authoritative inputs exist. |
| Bearings and foundation interfaces | The 36 source bearings are native typed `IfcBearing/ELASTOMERIC` assets with measured envelopes and explicit supplier/load/movement release gates. Nine foundation and 36 jacking envelopes remain `IfcVirtualElement`; promote them only after geotechnical and supplier design. |
| Bearing connectivity | Implemented with 27 native `IfcRelConnectsWithRealizingElements` relationships and 60 bearing realizations derived from exact source-envelope face contact. No analytical condition or supplier performance is inferred. |
| Mixed materials, other profiles, and reinforcement | Do not flatten mixed assemblies or populate generic placeholders. Add constituent/profile and reinforcement data when released specifications and deployment engineering are available. |
| Native OSR asset classification | Implemented with one internal system, 15 lightweight references, type inheritance for 138 occurrences, and direct references for 47 untyped virtual interfaces. |
| Country/client classification mapping | Defer Uniclass, OmniClass, national, or client codes until the deployment nominates an edition and approves a crosswalk; no global mapping is guessed. |
| Native coordination groups | Implemented with five deterministic `IfcGroup` records and exactly one group membership per asset. They preserve source review layouts without claiming surveyed space or system function. |
| Native functional systems | Implemented with six deterministic `IfcSystem`-family records and exactly one membership per asset, derived from the complete 15-class OSR asset classification. Three use supported `IfcBuiltSystem` subtypes, and seven non-hierarchical references connect all systems to the railway parts they cover. Virtual civil interfaces remain in a generic system. |
| Surveyed spatial zones | Add `IfcSpatialZone` only when accepted boundaries and survey control exist; the current separated review layout is insufficient evidence. |
| Native presentation layers | Implemented with four stable layers and exactly one `IfcShapeRepresentation` assignment per asset for simple visibility control. Object semantics remain elsewhere. |
| Native interface constraints | Implemented with nine hard `IfcObjective` records and 107 scoped project/asset/group/system evidence links. Six checks have native nested `IfcMetric/EQUALTO` length benchmarks; three remain explicitly qualitative. |
| Stage-specific 4D product semantics | Implemented across five output tasks: 134 physical assets animate at their actual completion stage, while 45 virtual foundation/jacking interfaces are separately related as review gates and never treated as constructed output. |
| Native OSR property dictionaries | Implemented with 16 project-declared templates, 99 typed fields, 483 direct definition links, and four name/type-matched material/profile definitions. Custom sets use `OSR_`, never the reserved `Pset_` prefix. |
| Native source-document register | Implemented with 15 hash-locked repository sources, direct project/cost/type/occurrence associations, and one resource-level relationship linking the civil source to all nine objectives and six metrics. |
| External engineering decision register | Implemented with nine indexed decisions. Survey, geotechnical, structural, bearing, material, classification, commercial, rolling-stock, and CDE promotion remains blocked until the named authority supplies the listed evidence. |
| Issued drawings and CDE document control | Defer sheets, issue/transmittal states, and CDE URLs until a deployment selects its naming, approval, and common-data-environment convention. |

## Upstream references

- [Bonsai introduction and native IFC workflow](https://docs.bonsaibim.org/quickstart/introduction_to_bim.html)
- [Bonsai road and rail alignment guide](https://docs.bonsaibim.org/guides/alignment.html)
- [IfcOpenShell alignment API and current design limitations](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/alignment/index.html)
- [IFC4.3 `IfcAlignmentHorizontal`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentHorizontal.htm)
- [IFC4.3 `IfcAlignmentVertical`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcAlignmentVertical.htm)
- [IFC4.3 `IfcReferent`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcReferent.htm)
- [IfcOpenShell georeferencing API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/georeference/index.html)
- [IFC4.3 `IfcCostSchedule`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcCostSchedule.htm)
- [IFC4.3 `IfcCostValue`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcCostValue.htm)
- [IfcOpenShell cost API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/cost/index.html)
- [IFC4.3 `IfcProjectedCRS`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcProjectedCRS.htm)
- [IFC4.3 `IfcMapConversion`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcMapConversion.htm)
- [IFC4.3 railway-part organisation and usage](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRailwayPartTypeEnum.htm)
- [IFC4.3 native quantity sets](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Definition/Quantity_Sets/content.html)
- [IFC4.3 object typing](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Definition/Object_Typing/content.html)
- [IfcOpenShell type assignment](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/type/assign_type/index.html)
- [IFC4.3 material sets](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Association/Material_Association/Material_Set/content.html)
- [IfcOpenShell material assignment](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/material/assign_material/index.html)
- [IFC4.3 material profile usage](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcMaterialProfileSetUsage.htm)
- [IfcOpenShell arbitrary profiles](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/profile/add_arbitrary_profile/index.html)
- [IFC4.3 classification systems](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcClassification.htm)
- [IfcOpenShell classification API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/classification/index.html)
- [IFC4.3 `IfcGroup`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcGroup.htm)
- [IFC4.3 `IfcSpatialZone`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcSpatialZone.htm)
- [IFC4.3 `IfcSystem`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcSystem.htm)
- [IFC4.3 `IfcVehicle`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcVehicle.htm)
- [IFC4.3 vehicle types](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcVehicleTypeEnum.htm)
- [IFC4.3 vehicle base quantities](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/Qto_VehicleBaseQuantities.htm)
- [IFC4.3 `IfcBearing`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcBearing.htm)
- [IFC4.3 bearing types](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcBearingTypeEnum.htm)
- [IFC4.3 element connectivity](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRelConnectsElements.htm)
- [IFC4.3 connections with realizing elements](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRelConnectsWithRealizingElements.htm)
- [IFC4.3 `IfcFooting` and shallow/deep-foundation boundary](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcFooting.htm)
- [IFC4.3 `IfcBuiltSystem`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcBuiltSystem.htm)
- [IFC4.3 built-system types](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcBuiltSystemTypeEnum.htm)
- [IFC4.3 spatial service connectivity](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Connectivity/Spatial_Service_Connectivity/content.html)
- [IfcOpenShell group API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/group/index.html)
- [IfcOpenShell system API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/system/index.html)
- [IFC4.3 `IfcPresentationLayerAssignment`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcPresentationLayerAssignment.htm)
- [IfcOpenShell layer API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/layer/index.html)
- [IFC4.3 constraint resource](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/ifcconstraintresource/content.html)
- [IFC4.3 `IfcObjective`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcObjective.htm)
- [IFC4.3 `IfcMetric`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcMetric.htm)
- [IFC4.3 `IfcRelAssociatesConstraint`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRelAssociatesConstraint.htm)
- [IFC4.3 `IfcExternalReferenceRelationship`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcExternalReferenceRelationship.htm)
- [IFC4.3 `IfcDocumentReference`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcDocumentReference.htm)
- [IfcOpenShell constraint API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/constraint/index.html)
- [IFC4.3 custom property-set naming](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcPropertySet.htm)
- [IFC4.3 property-set templates](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcPropertySetTemplate.htm)
- [IfcOpenShell property-template API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/pset_template/index.html)
- [IFC4.3 document information](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcDocumentInformation.htm)
- [IFC4.3 document associations](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRelAssociatesDocument.htm)
- [IfcOpenShell document API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/document/index.html)
- [IfcOpenShell schema validation](https://docs.ifcopenshell.org/ifcopenshell-python/validation.html)
- [IfcOpenShell parametric cost-quantity links](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/cost/assign_cost_item_quantity/index.html)
- [IfcTester IDS API](https://docs.ifcopenshell.org/autoapi/ifctester/ids/index.html)
- [IfcOpenShell BCF 3 topic API](https://docs.ifcopenshell.org/autoapi/bcf/v3/topic/index.html)
- [buildingSMART IFC4.3 rail domain](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/ifcraildomain/content.html)
