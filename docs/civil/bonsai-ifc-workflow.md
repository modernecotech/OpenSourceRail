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
| Pier, girder, trackform, platform and canopy parameters | `mechanical-py/src/osr_mech/` | Federate, classify, inspect, annotate and develop deployment detail against stable IDs |
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
scripts/bonsai-civil.sh --check
```

Generate deterministic IFC and JSON evidence without opening Blender:

```bash
scripts/bonsai-civil.sh --generate
```

Generate, import through Bonsai, save a native review scene, and render it:

```bash
scripts/bonsai-civil.sh --render
```

Render the normalized construction sequence as MP4 as well:

```bash
scripts/bonsai-civil.sh --animate
```

To bind the federation to a City Studio line, use the **Generate Bonsai civil
IFC4.3** job in the engineering hub. The adapter converts the selected line to
the local engineering frame and supplies that immutable reference axis to the
same exporter. The civil settings panel can store an accepted map conversion
per stable line ID; it is Git-visible, revision-hashed, shown in semantic
revision comparison, and passed only when that line is regenerated.

Outputs are written beneath `build/engineering/bonsai-civil/`:

- `civil-coordination.ifc` — native IFC4.3 model;
- `civil-coordination.index.json` — object-aware browser index and authority boundary;
- `civil-construction-sequence.json` — tasks, dates, QA holds and product assignments;
- `civil-information-requirements.ids` — buildingSMART IDS 1.0 delivery requirements;
- `civil-information-requirements.report.json` — complete deterministic IDS audit evidence;
- `civil-coordination-issues.bcf` — BCF 3.0 package with object-linked release issues;
- `civil-coordination-issues.index.json` — browser-safe issue and IFC selection index;
- `civil-coordination.validation.json` — reopen, IDS, BCF-link, and exact artifact-hash checks;
- `civil-coordination.blend` — Bonsai scene retaining IFC links and the animation timeline;
- `civil-coordination.png` and optional MP4 — reproducible visual review artifacts.

## Model content

The current reference federation contains 95 stable assets and 17 reusable
component types organised below an
`IfcRailway` and four `IfcRailwayPart` containers: track, substructure,
above-track systems, and lineside/clearance. Civil objects use IFC4.3 types
including `IfcRail`, `IfcBeam`, `IfcColumn`, `IfcSlab`, `IfcRoof`, and an
`IfcAlignment` reference. Each object carries:

- stable OSR asset ID and class;
- canonical source and source hash;
- revision ID and lifecycle status;
- inspectable coordination dimensions and source net volume;
- explicit detail mode when a complex assembly is represented by its review envelope.

Ninety-three occurrences are linked to an `IfcTypeProduct` derived from their
exact asset class and source-geometry recipe. Types carry stable `OSR-TYPE-…`
identity and `Pset_OSR_Type`; occurrence placement and geometry remain
authoritative. The two clearance envelopes remain untyped because IFC4.3 has
no `IfcVirtualElementType`.

Three native `IfcMaterial` family declarations cover 46 occurrences through
five type associations: running-rail steel, prestressed beam concrete, and
precast platform-unit concrete. `Pset_OSR_MaterialStatus` identifies the source
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

One internal `IfcClassification` contains 11 lightweight references using the
existing OSR asset codes. Ninety-three occurrences inherit their reference
from 17 reusable types; the two untyped clearance envelopes receive the same
class directly. All 95 assets therefore remain natively queryable without
duplicating type-level relationships. This classification supports OSR
automation only. Its metadata and City Studio inspector explicitly state that
country/client mappings remain unnominated and require an approved deployment
crosswalk.

The five source layouts are also native `IfcGroup` coordination groups, with
all 95 assets assigned exactly once. Their properties state that they are
separated review layouts—not surveyed spatial zones or functional engineering
systems—so Bonsai and City Studio can filter them without asserting false
`IfcSpatialZone` or `IfcSystem` semantics.

Fifteen native `IfcDocumentInformation`/`IfcDocumentReference` records expose
the actual repository sources used by the federation. Complete SHA-256
revisions and repository-relative locations cover the component generators,
integration source, exporter, alignment contract, cost contract, and this
release-boundary workflow. `IfcRelAssociatesDocument` links all 95 occurrences
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

The IFC project also carries `Pset_OSR_CostModel`: the generated contract hash,
maturity and current class rates. Its JSON index includes the full per-route-km
quantity basis. Editing a reviewed parametric dimension and regenerating first
updates the quantity model and cost contract, then emits both into IFC and city
CAPEX. Direct Bonsai edits remain coordination changes until promoted back into
the authoritative parametric source.

Eighteen track, station, and viaduct tasks—including foundation-zone release
before Pi-beam production and erection—are embedded in an
`IfcWorkSchedule`. Final installation tasks are linked to their output products
for Bonsai 4D visualization; predecessors, planning durations, QA holds, and
required evidence remain in the companion sequence index.

![Bonsai support-end review of twin OSR-Pi25 decks and the reduced common cap](../screenshots/civil/bonsai-pi25-support-detail.png)

The support-end render is generated by the same command. It shows the
coordination relationship between the two narrow track decks, bearing lines,
7 m common cap and independent outer walkway/containment cassettes; it does not
represent released reinforcement, prestress or connection detailing.

## IDS delivery gate and BCF review loop

The exporter writes an IDS 1.0 contract and immediately reopens it with
IfcTester against the written IFC. Nine specifications cover all 95 assets,
the 17-type catalogue, the source-backed material subset, alignment authority,
the native rail-profile assignments, OSR asset classification, native document
register, five coordination groups, and project provenance. The current
reference exchange passes all 1,347
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
toggle civil disciplines or any of the five native coordination groups, and
scrub or play the 18-task 4D sequence while showing the current QA hold and
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

## Gap review and economical next steps

| IFC capability | Decision |
|---|---|
| Native quantity take-off | Implemented now; it replaces quantity-shaped generic properties and enables later parametric IFC costing. |
| CRS/map conversion | Implemented now as validated opt-in input; unresolved projects remain visibly local rather than receiving a guessed EPSG code. |
| Full horizontal/vertical/cant alignment segments and linear placement | Defer until the accepted OSR-ALN design supplies segment parameters. LandXML, railML, stakeout CSV, and the current IFC reference curve already preserve a usable handoff; the upstream IfcOpenShell alignment API remains under development. |
| Native `IfcCostSchedule` | Defer until approved element-level rates exist. The generated CAD-indexed cost contract already propagates to city CAPEX, finance, IFC metadata, and Git revisions; attaching route-km benchmark rates to reference component samples would imply false 5D precision. Native quantities now provide the correct foundation for it later. |
| Reusable object types | Implemented for 93 safely typable occurrences using exact source recipes. Type geometry maps are deliberately omitted so occurrence geometry remains authoritative. |
| Material families | Implemented for the 46 occurrences whose source explicitly declares a safe single-material family. Every declaration is visibly grade/design unresolved. |
| Native rail profile | Implemented for all 32 straight 60E1 rail occurrences using a shared material profile set, occurrence usages, and matching extruded solids. |
| Mixed materials, other profiles, reinforcement, bearings, and foundations | Do not flatten mixed assemblies or populate generic placeholders. Add constituent/profile data when released specifications and deployment engineering are available. |
| Native OSR asset classification | Implemented with one internal system, 11 lightweight references, type inheritance for 93 occurrences, and direct references for two untyped envelopes. |
| Country/client classification mapping | Defer Uniclass, OmniClass, national, or client codes until the deployment nominates an edition and approves a crosswalk; no global mapping is guessed. |
| Native coordination groups | Implemented with five deterministic `IfcGroup` records and exactly one group membership per asset. They preserve source review layouts without claiming surveyed space or system function. |
| Surveyed spatial zones and functional systems | Add `IfcSpatialZone` or `IfcSystem` only when accepted spatial boundaries or an engineering system definition exists; the current separated review layout is insufficient evidence. |
| Native source-document register | Implemented with 15 hash-locked repository sources and direct project/type/occurrence associations. |
| Issued drawings and CDE document control | Defer sheets, issue/transmittal states, and CDE URLs until a deployment selects its naming, approval, and common-data-environment convention. |

## Upstream references

- [Bonsai introduction and native IFC workflow](https://docs.bonsaibim.org/quickstart/introduction_to_bim.html)
- [Bonsai road and rail alignment guide](https://docs.bonsaibim.org/guides/alignment.html)
- [IfcOpenShell alignment API and current design limitations](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/alignment/index.html)
- [IfcOpenShell georeferencing API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/georeference/index.html)
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
- [IfcOpenShell group API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/group/index.html)
- [IFC4.3 document information](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcDocumentInformation.htm)
- [IFC4.3 document associations](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRelAssociatesDocument.htm)
- [IfcOpenShell document API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/document/index.html)
- [IfcOpenShell schema validation](https://docs.ifcopenshell.org/ifcopenshell-python/validation.html)
- [IfcOpenShell parametric cost-quantity links](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/cost/assign_cost_item_quantity/index.html)
- [IfcTester IDS API](https://docs.ifcopenshell.org/autoapi/ifctester/ids/index.html)
- [IfcOpenShell BCF 3 topic API](https://docs.ifcopenshell.org/autoapi/bcf/v3/topic/index.html)
- [buildingSMART IFC4.3 rail domain](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/ifcraildomain/content.html)
